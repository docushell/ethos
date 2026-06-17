/*
 * Copyright 2026 The Ethos maintainers
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

use std::collections::{HashMap, HashSet};

use ethos_core::config::ParseConfig;
use ethos_core::error::EthosError;
use ethos_core::fingerprint::{source_fingerprint, FingerprintManifest};
use ethos_core::ids::warning_id;
use ethos_core::model::{
    CoordinateSystem, Document, Element, ParserInfo, Payload, ProfileRef, Region, SourceInfo, Span,
    Warning,
};
use ethos_core::traits::{BackendManifest, Extraction, LayoutEngine as _};

pub(crate) fn assemble_document(
    source_bytes: &[u8],
    config: &ParseConfig,
    extraction: Extraction,
    backend_manifest: BackendManifest,
    include_diagnostics: bool,
) -> Result<Document, EthosError> {
    let payload = assemble_payload(extraction)?;
    let hashes = compute_document_hashes(source_bytes, config, &payload)?;
    let diagnostics = diagnostics_payload(include_diagnostics, backend_manifest);

    Ok(Document {
        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
        parser: ParserInfo {
            name: "ethos".to_string(),
            version: env!("CARGO_PKG_VERSION").to_string(),
        },
        profile: ProfileRef {
            id: ethos_core::PROFILE_ID.to_string(),
            sha256: hashes.profile_sha256,
        },
        source: SourceInfo {
            fingerprint: hashes.source_fingerprint,
            bytes: source_bytes.len() as u64,
        },
        config_sha256: hashes.config_sha256,
        payload_sha256: hashes.payload_sha256,
        fingerprint: hashes.fingerprint,
        payload,
        diagnostics,
    })
}

fn assemble_payload(extraction: Extraction) -> Result<Payload, EthosError> {
    let layout = ethos_layout::BasicLayoutEngine.layout(&extraction)?;
    let mut spans = extraction.spans;
    assign_span_offsets(&layout.elements, &mut spans)?;
    let mut elements = layout.elements;
    let mut regions = extraction.regions;
    let (security_warnings, parser_warnings) = finalize_warnings(
        &mut spans,
        &mut regions,
        &mut elements,
        extraction.warnings,
        layout.warnings,
    )?;
    let tables = table_candidates(&extraction.pages, &spans)?;

    Ok(Payload {
        coordinate_system: CoordinateSystem {
            origin: "top-left".to_string(),
            unit: "quantum".to_string(),
            quantum_per_point: ethos_pdf::QUANTUM_PER_POINT,
        },
        pages: extraction.pages,
        elements,
        spans,
        tables,
        chunks: Vec::new(),
        regions,
        security_warnings,
        parser_warnings,
    })
}

fn table_candidates(
    pages: &[ethos_core::model::Page],
    spans: &[Span],
) -> Result<Vec<ethos_core::model::Table>, EthosError> {
    let mut tables = Vec::new();
    let mut next_table_ordinal = 1u32;

    for page in pages {
        let page_tables = ethos_tables::detect_regular_grid_candidates(
            &page.id,
            spans,
            next_table_ordinal,
            &ethos_tables::TableCandidateConfig::default(),
        )?;
        next_table_ordinal += page_tables.len() as u32;
        tables.extend(page_tables);
    }

    Ok(tables)
}

struct DocumentHashes {
    config_sha256: String,
    payload_sha256: String,
    profile_sha256: String,
    source_fingerprint: String,
    fingerprint: String,
}

fn compute_document_hashes(
    source_bytes: &[u8],
    config: &ParseConfig,
    payload: &Payload,
) -> Result<DocumentHashes, EthosError> {
    let payload_sha256 = Document::compute_payload_sha256_for_payload(payload)?;
    let profile_sha256 = profile_sha256()?;
    let source_fingerprint = source_fingerprint(source_bytes);
    let config_sha256 = config.config_sha256()?;
    let manifest = FingerprintManifest {
        config_sha256: config_sha256.clone(),
        payload_sha256: payload_sha256.clone(),
        profile_id: ethos_core::PROFILE_ID.to_string(),
        profile_sha256: profile_sha256.clone(),
        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
        source_fingerprint: source_fingerprint.clone(),
    };
    let fingerprint = manifest
        .document_fingerprint()
        .map_err(|e| EthosError::internal(e.message))?;

    Ok(DocumentHashes {
        config_sha256,
        payload_sha256,
        profile_sha256,
        source_fingerprint,
        fingerprint,
    })
}

fn diagnostics_payload(
    include_diagnostics: bool,
    backend_manifest: BackendManifest,
) -> Option<serde_json::Value> {
    include_diagnostics.then(|| {
        serde_json::json!({
            "backend": backend_manifest,
            "surface": "ethos-cli",
        })
    })
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
enum WarningOrigin {
    Extraction,
    Layout,
}

struct PendingWarning {
    origin: WarningOrigin,
    source_index: usize,
    original_id: String,
    warning: Warning,
}

pub(crate) fn finalize_warnings(
    spans: &mut [Span],
    regions: &mut [Region],
    elements: &mut [Element],
    extraction_warnings: Vec<Warning>,
    layout_warnings: Vec<Warning>,
) -> Result<(Vec<Warning>, Vec<Warning>), EthosError> {
    let mut pending = Vec::with_capacity(extraction_warnings.len() + layout_warnings.len());
    for (source_index, warning) in extraction_warnings.into_iter().enumerate() {
        pending.push(PendingWarning {
            origin: WarningOrigin::Extraction,
            source_index,
            original_id: warning.id.clone(),
            warning,
        });
    }
    for (source_index, warning) in layout_warnings.into_iter().enumerate() {
        pending.push(PendingWarning {
            origin: WarningOrigin::Layout,
            source_index,
            original_id: warning.id.clone(),
            warning,
        });
    }

    pending.sort_by(|a, b| {
        warning_order(&a.warning, &b.warning)
            .then_with(|| a.origin.cmp(&b.origin))
            .then_with(|| a.source_index.cmp(&b.source_index))
    });

    let mut extraction_ids = HashMap::new();
    let mut layout_ids = HashMap::new();
    let mut security_warnings = Vec::new();
    let mut parser_warnings = Vec::new();

    for (index, pending_warning) in pending.into_iter().enumerate() {
        let ordinal =
            u32::try_from(index + 1).map_err(|_| EthosError::internal("warning id overflow"))?;
        let final_id = warning_id(ordinal)?;
        match pending_warning.origin {
            WarningOrigin::Extraction => {
                extraction_ids.insert(pending_warning.original_id, final_id.clone());
            }
            WarningOrigin::Layout => {
                layout_ids.insert(pending_warning.original_id, final_id.clone());
            }
        }

        let mut warning = pending_warning.warning;
        warning.id = final_id;
        if warning.code.is_security() {
            security_warnings.push(warning);
        } else {
            parser_warnings.push(warning);
        }
    }

    for span in spans {
        rewrite_warning_refs(&mut span.warning_refs, &extraction_ids, &layout_ids);
    }
    for region in regions {
        rewrite_warning_refs(&mut region.warning_refs, &extraction_ids, &layout_ids);
    }
    for element in elements {
        rewrite_warning_refs(&mut element.warning_refs, &layout_ids, &extraction_ids);
    }

    Ok((security_warnings, parser_warnings))
}

fn warning_order(a: &Warning, b: &Warning) -> std::cmp::Ordering {
    a.code
        .as_str()
        .cmp(b.code.as_str())
        .then_with(|| a.page.cmp(&b.page))
        .then_with(|| a.element_ref.cmp(&b.element_ref))
        .then_with(|| a.span_ref.cmp(&b.span_ref))
        .then_with(|| a.region_ref.cmp(&b.region_ref))
        .then_with(|| a.message.cmp(&b.message))
}

fn rewrite_warning_refs(
    warning_refs: &mut [String],
    primary_ids: &HashMap<String, String>,
    secondary_ids: &HashMap<String, String>,
) {
    for warning_ref in warning_refs {
        if let Some(final_id) = primary_ids
            .get(warning_ref)
            .or_else(|| secondary_ids.get(warning_ref))
        {
            *warning_ref = final_id.clone();
        }
    }
}

fn assign_span_offsets(elements: &[Element], spans: &mut [Span]) -> Result<(), EthosError> {
    for span in spans.iter_mut() {
        span.char_start = None;
        span.char_end = None;
    }

    let span_indices: HashMap<String, usize> = spans
        .iter()
        .enumerate()
        .map(|(idx, span)| (span.id.clone(), idx))
        .collect();
    let mut assigned = HashSet::new();

    for element in elements {
        let Some(text) = element.text.as_deref() else {
            continue;
        };
        if element.span_refs.is_empty() {
            continue;
        }

        let mut char_cursor = 0u32;
        for (pos, span_id) in element.span_refs.iter().enumerate() {
            if !assigned.insert(span_id.clone()) {
                return Err(EthosError::internal(
                    "span is assigned to multiple elements",
                ));
            }
            if pos > 0 {
                char_cursor = char_cursor
                    .checked_add(1)
                    .ok_or_else(|| EthosError::internal("span offset overflow"))?;
            }

            let idx = *span_indices
                .get(span_id)
                .ok_or_else(|| EthosError::internal("element references an unknown span"))?;
            let span_text_chars = spans[idx].text.chars().count();
            let span_text_chars = u32::try_from(span_text_chars)
                .map_err(|_| EthosError::internal("span text length overflow"))?;
            spans[idx].char_start = Some(char_cursor);
            char_cursor = char_cursor
                .checked_add(span_text_chars)
                .ok_or_else(|| EthosError::internal("span offset overflow"))?;
            spans[idx].char_end = Some(char_cursor);
        }

        let text_chars = u32::try_from(text.chars().count())
            .map_err(|_| EthosError::internal("element text length overflow"))?;
        if char_cursor != text_chars {
            return Err(EthosError::internal("layout text/span offsets disagree"));
        }
    }

    Ok(())
}

fn profile_sha256() -> Result<String, EthosError> {
    let raw = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../profiles/ethos-deterministic-v1.json"
    ));
    let value: serde_json::Value =
        serde_json::from_str(raw).map_err(|e| EthosError::internal(e.to_string()))?;
    ethos_core::c14n::sha256_hex(&value).map_err(|e| EthosError::internal(e.message))
}
