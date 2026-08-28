// Copyright 2026 The Ethos maintainers
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//! Evidence anchoring — the second engine in this crate, and a leaf of it.
//!
//! # Why this is its own file
//!
//! `lib.rs` held both engines and had grown past five thousand lines. The two do
//! different jobs: **verification** answers *does this claim hold against this
//! source*, while **anchoring** answers the narrower *can this evidence reference
//! be resolved to a place in this source, and does what is there still match what
//! the reference says it is*. They share the source index and the text utilities
//! and nothing else.
//!
//! The split was chosen along the dependency edge rather than by line count. This
//! module calls into the shared index/text region of `lib.rs` — `SourceIndex`,
//! `target_from_element`, `contains_bbox`, `normalize_quote`, `context_echo` and a
//! handful of others — and **nothing in `lib.rs` calls back into anything defined
//! here**. That one-way edge is what makes the move mechanical: no item changed,
//! no signature moved, and every name this file needs is imported from its parent
//! rather than reached for through a cycle.
//!
//! # What has NOT changed
//!
//! Every public item keeps its path: `lib.rs` re-exports this module's surface, so
//! `ethos_verify::anchor_evidence` and the rest resolve exactly where callers
//! already expect them. The CLI, the integration tests and any external consumer
//! see an identical API.

use ethos_core::evidence_anchor::{
    AnchorChecks, AnchorLevel, AnchorStatus, BboxCheck, CoordinateProfile, EvidenceAnchor,
    EvidenceAnchorGrounding, EvidenceAnchorReport, EvidenceAnchorReportOptions,
    EvidenceAnchorRequest, EvidenceKind, EvidenceRef, FingerprintCheck, PageCheck, TableCellCheck,
    TextCheck, TextNormalizationProfile, EVIDENCE_ANCHOR_REPORT_ARTIFACT_TYPE,
    HARDENED_EVIDENCE_ANCHOR_SCHEMA_VERSION,
};
use ethos_core::grounding::{CoordinateOrigin, GroundingSource};
use ethos_core::verify_types::{CapabilityLimit, ClaimKind, VerificationConfig};
use sha2::{Digest, Sha256};

use crate::{
    bbox_area, check_provenance, contains_bbox, context_echo, normalize_quote, table_cell_covers,
    target_from_cell, target_from_element, target_from_span, FoundTarget, SourceIndex,
};

/// Validation or source-shape error for evidence anchoring.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EvidenceAnchorError {
    message: String,
}

impl EvidenceAnchorError {
    fn new(message: impl Into<String>) -> Self {
        EvidenceAnchorError {
            message: message.into(),
        }
    }
}

impl std::fmt::Display for EvidenceAnchorError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.message)
    }
}

impl std::error::Error for EvidenceAnchorError {}

/// Validate and resolve evidence refs over one grounding source.
pub fn anchor_evidence(
    source: &dyn GroundingSource,
    request: EvidenceAnchorRequest,
) -> Result<EvidenceAnchorReport, EvidenceAnchorError> {
    validate_anchor_request(&request)?;
    let index = SourceIndex::new(source);
    let fingerprint_check = fingerprint_check(request.source_fingerprint.as_deref(), source);
    let source_fingerprint = source.fingerprint();
    let grounding = EvidenceAnchorGrounding {
        parser: source.parser(),
        capabilities: source.capabilities(),
    };
    let anchors = request
        .evidence_refs
        .iter()
        .map(|evidence_ref| {
            anchor_one(
                source,
                &index,
                fingerprint_check,
                evidence_ref,
                request.report_options,
            )
        })
        .collect();
    Ok(EvidenceAnchorReport {
        artifact_type: EVIDENCE_ANCHOR_REPORT_ARTIFACT_TYPE.to_string(),
        schema_version: if request.report_options.is_some() {
            HARDENED_EVIDENCE_ANCHOR_SCHEMA_VERSION.to_string()
        } else {
            ethos_core::SCHEMA_VERSION.to_string()
        },
        source_fingerprint,
        grounding,
        anchors,
    })
}

fn validate_anchor_request(request: &EvidenceAnchorRequest) -> Result<(), EvidenceAnchorError> {
    if request.artifact_type != ethos_core::evidence_anchor::EVIDENCE_ANCHOR_REQUEST_ARTIFACT_TYPE {
        return Err(EvidenceAnchorError::new(
            "evidence anchor request artifact_type is not supported",
        ));
    }
    let options_enabled = request.report_options.is_some();
    let expected_schema_version = if options_enabled {
        HARDENED_EVIDENCE_ANCHOR_SCHEMA_VERSION
    } else {
        ethos_core::SCHEMA_VERSION
    };
    if request.schema_version != expected_schema_version {
        return Err(EvidenceAnchorError::new(
            "evidence anchor request schema_version is not supported",
        ));
    }
    if request.report_options.is_some_and(|options| {
        options.include_context_echo && !(1..=4096).contains(&options.context_window_chars)
    }) {
        return Err(EvidenceAnchorError::new(
            "context_window_chars must be between 1 and 4096 when context echo is enabled",
        ));
    }
    let mut ids = std::collections::BTreeSet::new();
    for evidence_ref in &request.evidence_refs {
        if !ids.insert(evidence_ref.evidence_id.as_str()) {
            return Err(EvidenceAnchorError::new(format!(
                "duplicate evidence_id '{}'",
                evidence_ref.evidence_id
            )));
        }
        validate_evidence_ref(evidence_ref)?;
    }
    Ok(())
}

fn validate_evidence_ref(evidence_ref: &EvidenceRef) -> Result<(), EvidenceAnchorError> {
    validate_locator(evidence_ref)?;
    validate_expected_text(evidence_ref)?;
    validate_kind_level_compat(evidence_ref)?;
    validate_required_anchor_inputs(evidence_ref)?;
    validate_required_page_locator(evidence_ref)?;
    Ok(())
}

fn validate_locator(evidence_ref: &EvidenceRef) -> Result<(), EvidenceAnchorError> {
    let locator = &evidence_ref.locator;
    if locator.page_index == Some(0) {
        return Err(EvidenceAnchorError::new("page_index must be 1-based"));
    }
    if locator.page_index.is_some() && locator.page_id.is_some() {
        return Err(EvidenceAnchorError::new(
            "use exactly one of page_index or page_id",
        ));
    }
    if locator.bbox.is_some()
        && locator.coordinate_profile != Some(CoordinateProfile::EthosQuantizedTopLeftV1)
    {
        return Err(EvidenceAnchorError::new(
            "bbox requires coordinate_profile ethos_quantized_top_left_v1",
        ));
    }
    Ok(())
}

fn validate_expected_text(evidence_ref: &EvidenceRef) -> Result<(), EvidenceAnchorError> {
    // A declared normalization profile is checked WHENEVER it is set, not only
    // when a hash accompanies it.
    //
    // The anchor path normalizes through `normalize_expected_text` — collapse
    // whitespace — and nothing else. Until now the profile field was read at
    // exactly one place, inside the `expected_text_sha256` branch below, so a
    // caller could declare a profile on its own and have it silently ignored
    // while collapse-whitespace was applied regardless. Today that is harmless
    // because the enum has one variant and it names the behaviour that runs; it
    // stops being harmless the moment a second variant exists, and the verify
    // side already has one this enum has no twin for
    // (`TextNormalization::UnicodeCompatV1`). A field that states something the
    // engine does not do is the shape of an artifact that lies, and it is
    // cheaper to close now than to discover through a wrong verdict later.
    //
    // The match is exhaustive on purpose: a new variant added to
    // `TextNormalizationProfile` fails to compile here rather than inheriting
    // collapse-whitespace semantics by default, which is the decision this
    // repository wants a human to make deliberately.
    if let Some(profile) = evidence_ref.text_normalization_profile {
        match profile {
            TextNormalizationProfile::EthosCollapseWhitespaceV1 => {}
        }
    }
    if let Some(expected_text) = evidence_ref.expected_text.as_deref() {
        if normalize_expected_text(expected_text).is_empty() {
            return Err(EvidenceAnchorError::new(
                "expected_text must not be empty after normalization",
            ));
        }
    }
    if evidence_ref.expected_text_sha256.is_some() {
        let Some(expected_text) = evidence_ref.expected_text.as_deref() else {
            return Err(EvidenceAnchorError::new(
                "expected_text_sha256 requires expected_text",
            ));
        };
        if evidence_ref.text_normalization_profile
            != Some(TextNormalizationProfile::EthosCollapseWhitespaceV1)
        {
            return Err(EvidenceAnchorError::new(
                "expected_text_sha256 requires text_normalization_profile ethos_collapse_whitespace_v1",
            ));
        }
        let expected_hash = format!(
            "sha256:{}",
            sha256_hex(normalize_expected_text(expected_text).as_bytes())
        );
        if evidence_ref.expected_text_sha256.as_deref() != Some(expected_hash.as_str()) {
            return Err(EvidenceAnchorError::new(
                "expected_text_sha256 does not match normalized expected_text",
            ));
        }
    }
    Ok(())
}

fn validate_kind_level_compat(evidence_ref: &EvidenceRef) -> Result<(), EvidenceAnchorError> {
    match evidence_ref.evidence_kind {
        EvidenceKind::Page if evidence_ref.required_anchor_level != AnchorLevel::Page => {
            return Err(EvidenceAnchorError::new(
                "page evidence supports only required_anchor_level page",
            ));
        }
        EvidenceKind::Text if evidence_ref.required_anchor_level != AnchorLevel::Text => {
            return Err(EvidenceAnchorError::new(
                "text evidence supports only required_anchor_level text",
            ));
        }
        EvidenceKind::TextRegion
            if !matches!(
                evidence_ref.required_anchor_level,
                AnchorLevel::Text | AnchorLevel::Bbox | AnchorLevel::TextBbox
            ) =>
        {
            return Err(EvidenceAnchorError::new(
                "text_region evidence supports only text, bbox, or text_bbox anchor levels",
            ));
        }
        EvidenceKind::TableCell if evidence_ref.required_anchor_level != AnchorLevel::TableCell => {
            return Err(EvidenceAnchorError::new(
                "table_cell evidence supports only required_anchor_level table_cell",
            ));
        }
        EvidenceKind::TableCell
            if evidence_ref.locator.table_id.is_none() || evidence_ref.locator.cell.is_none() =>
        {
            return Err(EvidenceAnchorError::new(
                "table_cell evidence requires table_id and cell",
            ));
        }
        EvidenceKind::Region | EvidenceKind::Other => {}
        _ => {}
    }
    Ok(())
}

fn validate_required_anchor_inputs(evidence_ref: &EvidenceRef) -> Result<(), EvidenceAnchorError> {
    if anchor_requires_text(evidence_ref) && evidence_ref.expected_text.is_none() {
        return Err(EvidenceAnchorError::new(
            "required_anchor_level text or text_bbox requires expected_text",
        ));
    }
    if requires_bbox(evidence_ref) && evidence_ref.locator.bbox.is_none() {
        return Err(EvidenceAnchorError::new(
            "required_anchor_level bbox or text_bbox requires locator.bbox",
        ));
    }
    Ok(())
}

fn validate_required_page_locator(evidence_ref: &EvidenceRef) -> Result<(), EvidenceAnchorError> {
    if page_locator_required(evidence_ref)
        && evidence_ref.locator.page_index.is_none()
        && evidence_ref.locator.page_id.is_none()
    {
        return Err(EvidenceAnchorError::new(
            "page_index or page_id is required for this evidence ref",
        ));
    }
    Ok(())
}

fn page_locator_required(evidence_ref: &EvidenceRef) -> bool {
    matches!(evidence_ref.evidence_kind, EvidenceKind::Page)
        || evidence_ref.locator.bbox.is_some()
        || (evidence_ref.locator.element_id.is_none()
            && evidence_ref.locator.span_id.is_none()
            && evidence_ref.locator.table_id.is_none())
}

fn fingerprint_check(
    request_fingerprint: Option<&str>,
    source: &dyn GroundingSource,
) -> FingerprintCheck {
    match (request_fingerprint, source.fingerprint()) {
        (None, _) => FingerprintCheck::NotChecked,
        (Some(_), None) => FingerprintCheck::CapabilityLimited,
        (Some(expected), Some(actual)) if expected == actual => FingerprintCheck::Matched,
        (Some(_), Some(_)) => FingerprintCheck::Stale,
    }
}

fn anchor_one(
    source: &dyn GroundingSource,
    index: &SourceIndex,
    fingerprint: FingerprintCheck,
    evidence_ref: &EvidenceRef,
    report_options: Option<EvidenceAnchorReportOptions>,
) -> EvidenceAnchor {
    let mut checks = AnchorChecks {
        fingerprint,
        ..AnchorChecks::default()
    };
    let mut capability_limits = Vec::new();

    if matches!(
        evidence_ref.evidence_kind,
        EvidenceKind::Region | EvidenceKind::Other
    ) {
        return anchor_result(
            evidence_ref,
            AnchorStatus::UnsupportedEvidenceKind,
            AnchorLevel::None,
            checks,
            capability_limits,
        );
    }
    if fingerprint == FingerprintCheck::Stale {
        return anchor_result(
            evidence_ref,
            AnchorStatus::StaleFingerprint,
            AnchorLevel::None,
            checks,
            capability_limits,
        );
    }
    if fingerprint == FingerprintCheck::CapabilityLimited {
        capability_limits.push(CapabilityLimit::MissingFingerprint);
    }

    let page = resolve_page(index, evidence_ref);
    checks.page = page.check;
    let mut achieved_page = page.check == PageCheck::Found;
    let mut text_ok = false;
    let mut bbox_ok = false;
    let mut table_ok = false;

    match evidence_ref.evidence_kind {
        EvidenceKind::Page => {}
        EvidenceKind::Text | EvidenceKind::TextRegion => {
            if anchor_requires_text(evidence_ref) {
                let text = resolve_text(index, evidence_ref, page.page_id.as_deref());
                checks.text = text.check;
                text_ok = text.check == TextCheck::Matched;
                if text.check == TextCheck::CapabilityLimited {
                    capability_limits.push(CapabilityLimit::MissingSpans);
                }
            }
            if requires_bbox(evidence_ref) {
                let bbox = resolve_bbox(index, evidence_ref, page.page_id.as_deref());
                checks.bbox = bbox;
                bbox_ok = bbox == BboxCheck::Valid;
                if bbox == BboxCheck::CapabilityLimited {
                    capability_limits.push(CapabilityLimit::UnknownCoordinateOrigin);
                }
            }
        }
        EvidenceKind::TableCell => {
            let table = resolve_anchor_table_cell(index, evidence_ref);
            checks.table_cell = table.check;
            table_ok = table.check == TableCellCheck::Matched;
            achieved_page = table.page_found;
            if table.check == TableCellCheck::CapabilityLimited {
                capability_limits.push(CapabilityLimit::MissingTables);
            }
        }
        EvidenceKind::Region | EvidenceKind::Other => {}
    }

    capability_limits.sort_by_key(|limit| capability_limit_order(*limit));
    capability_limits.dedup();
    let achieved_anchor_level =
        achieved_anchor_level(evidence_ref, achieved_page, text_ok, bbox_ok, table_ok);
    let anchor_status = anchor_status(evidence_ref, &checks, &capability_limits);
    let mut result = anchor_result(
        evidence_ref,
        anchor_status,
        achieved_anchor_level,
        checks,
        capability_limits,
    );
    if anchor_status == AnchorStatus::Bound {
        if let Some(options) = report_options.filter(|options| options.enabled()) {
            if let Some(target) =
                resolve_anchor_target(index, evidence_ref, page.page_id.as_deref())
            {
                result.resolved_element_ids = target.element_ids.clone();
                if options.include_provenance {
                    result.provenance = Some(check_provenance(source, &target));
                }
                if options.include_context_echo {
                    let config = VerificationConfig::default_v1();
                    result.context_echo = context_echo(
                        ClaimKind::Quote,
                        evidence_ref.expected_text.as_deref(),
                        &target,
                        &config,
                        options.context_window_chars,
                    );
                }
            }
        }
    }
    result
}

fn anchor_result(
    evidence_ref: &EvidenceRef,
    anchor_status: AnchorStatus,
    achieved_anchor_level: AnchorLevel,
    checks: AnchorChecks,
    capability_limits: Vec<CapabilityLimit>,
) -> EvidenceAnchor {
    EvidenceAnchor {
        evidence_id: evidence_ref.evidence_id.clone(),
        evidence_kind: evidence_ref.evidence_kind,
        anchor_status,
        required_anchor_level: evidence_ref.required_anchor_level,
        achieved_anchor_level,
        checks,
        capability_limits,
        resolved_element_ids: Vec::new(),
        provenance: None,
        context_echo: None,
    }
}

struct PageResolution {
    check: PageCheck,
    page_id: Option<String>,
}

fn resolve_page(index: &SourceIndex, evidence_ref: &EvidenceRef) -> PageResolution {
    if let Some(page_id) = evidence_ref.locator.page_id.as_deref() {
        return if index.pages.iter().any(|page| page.id == page_id) {
            PageResolution {
                check: PageCheck::Found,
                page_id: Some(page_id.to_string()),
            }
        } else {
            PageResolution {
                check: PageCheck::NotFound,
                page_id: None,
            }
        };
    }
    if let Some(page_index) = evidence_ref.locator.page_index {
        return index
            .pages
            .iter()
            .find(|page| page.index == page_index)
            .map(|page| PageResolution {
                check: PageCheck::Found,
                page_id: Some(page.id.clone()),
            })
            .unwrap_or(PageResolution {
                check: PageCheck::NotFound,
                page_id: None,
            });
    }
    PageResolution {
        check: PageCheck::NotChecked,
        page_id: None,
    }
}

struct TextResolution {
    check: TextCheck,
}

fn resolve_text(
    index: &SourceIndex,
    evidence_ref: &EvidenceRef,
    page_id: Option<&str>,
) -> TextResolution {
    let Some(expected_text) = evidence_ref.expected_text.as_deref() else {
        return TextResolution {
            check: TextCheck::NotFound,
        };
    };
    if let Some(span_id) = evidence_ref.locator.span_id.as_deref() {
        if !index.capabilities.spans {
            return TextResolution {
                check: TextCheck::CapabilityLimited,
            };
        }
        return match index.span(span_id) {
            Some(span) => TextResolution {
                check: text_check(expected_text, &span.text),
            },
            None => TextResolution {
                check: TextCheck::NotFound,
            },
        };
    }
    if let Some(element_id) = evidence_ref.locator.element_id.as_deref() {
        return index
            .element_by_id
            .get(element_id)
            .and_then(|position| index.elements.get(*position))
            .and_then(|element| element.text.as_deref())
            .map(|actual| TextResolution {
                check: text_check(expected_text, actual),
            })
            .unwrap_or(TextResolution {
                check: TextCheck::NotFound,
            });
    }
    let Some(page_id) = page_id else {
        return TextResolution {
            check: TextCheck::NotFound,
        };
    };
    if index
        .elements
        .iter()
        .filter(|element| element.page == page_id)
        .filter_map(|element| element.text.as_deref())
        .any(|actual| text_check(expected_text, actual) == TextCheck::Matched)
    {
        return TextResolution {
            check: TextCheck::Matched,
        };
    }
    if index
        .spans
        .iter()
        .filter(|span| span.page == page_id)
        .any(|span| text_check(expected_text, &span.text) == TextCheck::Matched)
    {
        return TextResolution {
            check: TextCheck::Matched,
        };
    }
    TextResolution {
        check: if index.elements.iter().any(|element| element.page == page_id)
            || index.spans.iter().any(|span| span.page == page_id)
        {
            TextCheck::Mismatch
        } else {
            TextCheck::NotFound
        },
    }
}

fn resolve_anchor_target(
    index: &SourceIndex,
    evidence_ref: &EvidenceRef,
    page_id: Option<&str>,
) -> Option<FoundTarget> {
    if let Some(span_id) = evidence_ref.locator.span_id.as_deref() {
        return index.span(span_id).map(target_from_span);
    }
    if let Some(element_id) = evidence_ref.locator.element_id.as_deref() {
        return index
            .element_by_id
            .get(element_id)
            .and_then(|position| {
                index
                    .elements
                    .get(*position)
                    .map(|element| (*position, element))
            })
            .map(|(position, element)| target_from_element(element, Some(position)));
    }
    if let (Some(table_id), Some(cell_ref)) = (
        evidence_ref.locator.table_id.as_deref(),
        evidence_ref.locator.cell,
    ) {
        return index.table(table_id).and_then(|table| {
            table
                .cells
                .iter()
                .find(|cell| table_cell_covers(cell, cell_ref.row, cell_ref.col))
                .map(|cell| target_from_cell(&table.page, cell))
        });
    }
    if let (Some(page_id), Some(bbox)) = (page_id, evidence_ref.locator.bbox) {
        let tolerance = VerificationConfig::default_v1()
            .matching
            .bbox_containment_tolerance_q
            .unwrap_or(0);
        return index
            .elements
            .iter()
            .enumerate()
            .filter(|(_, element)| {
                element.page == page_id
                    && element
                        .bbox
                        .is_some_and(|geom| contains_bbox(geom, bbox, tolerance))
            })
            .min_by_key(|(position, element)| {
                (element.bbox.map_or(u128::MAX, bbox_area), *position)
            })
            .map(|(position, element)| target_from_element(element, Some(position)));
    }
    let expected = evidence_ref.expected_text.as_deref()?;
    let page_id = page_id?;
    if let Some((position, element)) = index.elements.iter().enumerate().find(|(_, element)| {
        element.page == page_id
            && element
                .text
                .as_deref()
                .is_some_and(|actual| text_check(expected, actual) == TextCheck::Matched)
    }) {
        return Some(target_from_element(element, Some(position)));
    }
    index
        .spans
        .iter()
        .find(|span| span.page == page_id && text_check(expected, &span.text) == TextCheck::Matched)
        .map(target_from_span)
}

fn resolve_bbox(
    index: &SourceIndex,
    evidence_ref: &EvidenceRef,
    page_id: Option<&str>,
) -> BboxCheck {
    let Some(bbox) = evidence_ref.locator.bbox else {
        return BboxCheck::NotChecked;
    };
    if index.capabilities.coordinate_origin != CoordinateOrigin::TopLeft {
        return BboxCheck::CapabilityLimited;
    }
    let Some(page_id) = page_id else {
        return BboxCheck::NotFound;
    };
    let tolerance = VerificationConfig::default_v1()
        .matching
        .bbox_containment_tolerance_q
        .unwrap_or(0);
    if index.elements.iter().any(|element| {
        element.page == page_id
            && element
                .bbox
                .is_some_and(|geom| contains_bbox(geom, bbox, tolerance))
    }) || index.spans.iter().any(|span| {
        span.page == page_id
            && span
                .bbox
                .is_some_and(|geom| contains_bbox(geom, bbox, tolerance))
    }) || index.tables.iter().any(|table| {
        table.page == page_id
            && table
                .bbox
                .is_some_and(|geom| contains_bbox(geom, bbox, tolerance))
    }) {
        BboxCheck::Valid
    } else {
        BboxCheck::NotFound
    }
}

struct TableResolution {
    check: TableCellCheck,
    page_found: bool,
}

fn resolve_anchor_table_cell(index: &SourceIndex, evidence_ref: &EvidenceRef) -> TableResolution {
    if !index.capabilities.tables {
        return TableResolution {
            check: TableCellCheck::CapabilityLimited,
            page_found: false,
        };
    }
    let Some(table_id) = evidence_ref.locator.table_id.as_deref() else {
        return TableResolution {
            check: TableCellCheck::NotFound,
            page_found: false,
        };
    };
    let Some(cell_ref) = evidence_ref.locator.cell else {
        return TableResolution {
            check: TableCellCheck::NotFound,
            page_found: false,
        };
    };
    let Some(table) = index.table(table_id) else {
        return TableResolution {
            check: TableCellCheck::NotFound,
            page_found: false,
        };
    };
    let page_found = index.pages.iter().any(|page| page.id == table.page);
    let Some(cell) = table
        .cells
        .iter()
        .find(|cell| table_cell_covers(cell, cell_ref.row, cell_ref.col))
    else {
        return TableResolution {
            check: TableCellCheck::NotFound,
            page_found,
        };
    };
    let check = match evidence_ref.expected_text.as_deref() {
        Some(expected) => {
            if table_cell_text_matches(expected, &cell.text) {
                TableCellCheck::Matched
            } else {
                TableCellCheck::Mismatch
            }
        }
        None => TableCellCheck::Matched,
    };
    TableResolution { check, page_found }
}

fn anchor_requires_text(evidence_ref: &EvidenceRef) -> bool {
    matches!(
        evidence_ref.required_anchor_level,
        AnchorLevel::Text | AnchorLevel::TextBbox
    )
}

fn requires_bbox(evidence_ref: &EvidenceRef) -> bool {
    matches!(
        evidence_ref.required_anchor_level,
        AnchorLevel::Bbox | AnchorLevel::TextBbox
    )
}

fn text_check(expected: &str, actual: &str) -> TextCheck {
    if normalize_expected_text(actual).contains(&normalize_expected_text(expected)) {
        TextCheck::Matched
    } else {
        TextCheck::Mismatch
    }
}

fn table_cell_text_matches(expected: &str, actual: &str) -> bool {
    normalize_expected_text(actual) == normalize_expected_text(expected)
}

fn normalize_expected_text(input: &str) -> String {
    normalize_quote(input)
}

fn capability_limit_order(limit: CapabilityLimit) -> u8 {
    match limit {
        CapabilityLimit::MissingSpans => 0,
        CapabilityLimit::MissingCharOffsets => 1,
        CapabilityLimit::MissingTables => 2,
        CapabilityLimit::MissingFingerprint => 3,
        CapabilityLimit::UnknownCoordinateOrigin => 4,
        CapabilityLimit::MissingCropSupport => 5,
        CapabilityLimit::MissingStructure => 6,
    }
}

fn sha256_hex(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    format!("{:x}", hasher.finalize())
}

fn achieved_anchor_level(
    evidence_ref: &EvidenceRef,
    page_ok: bool,
    text_ok: bool,
    bbox_ok: bool,
    table_ok: bool,
) -> AnchorLevel {
    match evidence_ref.evidence_kind {
        EvidenceKind::Page if page_ok => AnchorLevel::Page,
        EvidenceKind::Text if text_ok => AnchorLevel::Text,
        EvidenceKind::TextRegion if text_ok && bbox_ok => AnchorLevel::TextBbox,
        EvidenceKind::TextRegion if text_ok => AnchorLevel::Text,
        EvidenceKind::TextRegion if bbox_ok => AnchorLevel::Bbox,
        EvidenceKind::TableCell if table_ok => AnchorLevel::TableCell,
        _ => AnchorLevel::None,
    }
}

fn anchor_status(
    evidence_ref: &EvidenceRef,
    checks: &AnchorChecks,
    capability_limits: &[CapabilityLimit],
) -> AnchorStatus {
    if checks.page == PageCheck::NotFound
        || checks.text == TextCheck::NotFound
        || checks.bbox == BboxCheck::NotFound
        || checks.table_cell == TableCellCheck::NotFound
    {
        return AnchorStatus::NotFound;
    }
    if checks.text == TextCheck::Mismatch
        || checks.bbox == BboxCheck::Invalid
        || checks.table_cell == TableCellCheck::Mismatch
    {
        return AnchorStatus::Mismatch;
    }
    if checks.fingerprint == FingerprintCheck::CapabilityLimited
        || checks.text == TextCheck::CapabilityLimited
        || checks.bbox == BboxCheck::CapabilityLimited
        || checks.table_cell == TableCellCheck::CapabilityLimited
        || !capability_limits.is_empty()
    {
        return AnchorStatus::CapabilityLimited;
    }
    let bound = match evidence_ref.required_anchor_level {
        AnchorLevel::Page => checks.page == PageCheck::Found,
        AnchorLevel::Text => checks.text == TextCheck::Matched,
        AnchorLevel::Bbox => checks.bbox == BboxCheck::Valid,
        AnchorLevel::TextBbox => {
            checks.text == TextCheck::Matched && checks.bbox == BboxCheck::Valid
        }
        AnchorLevel::TableCell => checks.table_cell == TableCellCheck::Matched,
        AnchorLevel::None => false,
    };
    if bound {
        AnchorStatus::Bound
    } else {
        AnchorStatus::NotFound
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::adjacent_text_pair_target;
    use crate::tests::TestSource;
    use ethos_core::evidence_anchor::EvidenceLocator;
    use ethos_core::grounding::{
        Capabilities, GroundingElement, GroundingSpan, GroundingTable, PageGeometry, ParserIdentity,
    };

    // ---- geometry-free text anchoring -------------------------------------------------
    //
    // An `element_id` + `expected_text` ref with no page locator and no bbox binds at
    // `AnchorLevel::Text` and reports no capability limit. `docs/v0-6-0-release.md` §10.1
    // established this by source audit; these tests make it an enforced invariant.
    //
    // Why it is guarded: geometry is mandatory in `ethos.grounding.v1` and its validator,
    // not in this algorithm. That gap is what would let a flow document — DOCX, where
    // pagination does not exist in the file and any bbox would have to be invented — ever
    // be verified honestly. A refactor that made a page locator or a bbox mandatory here
    // would close that path silently, and nothing else in the suite would notice.
    //
    // Multi-format support is deliberately out of scope (`docs/proof-statement-v1.md` §7).
    // These tests keep the door open; they do not open it.

    fn geometry_free_text_ref() -> EvidenceRef {
        EvidenceRef {
            evidence_id: "ev-1".into(),
            evidence_kind: EvidenceKind::Text,
            required_anchor_level: AnchorLevel::Text,
            locator: EvidenceLocator {
                page_index: None,
                page_id: None,
                element_id: Some("e000002".into()),
                span_id: None,
                bbox: None,
                ..Default::default()
            },
            expected_text: Some("Revenue grew to $12.4M".into()),
            expected_text_sha256: None,
            text_normalization_profile: None,
        }
    }

    #[test]
    fn geometry_free_text_ref_needs_no_page_locator() {
        // Guards the `element_id` disjunct in `page_locator_required`. If this flips true,
        // `validate_required_page_locator` rejects the ref before anchoring even starts.
        assert!(!page_locator_required(&geometry_free_text_ref()));
    }

    #[test]
    fn geometry_free_text_ref_needs_no_bbox() {
        // `AnchorLevel::Text` must stay outside `requires_bbox`, otherwise
        // `validate_required_anchor_inputs` rejects a ref that carries no bbox.
        assert!(!requires_bbox(&geometry_free_text_ref()));
    }

    #[test]
    fn absent_page_locator_resolves_to_not_checked_never_not_found() {
        // The distinction that carries the whole path. `NotChecked` means "no page was
        // asked about"; `NotFound` means "a page was asked about and is missing" and
        // would fail the anchor. A source with no pages at all must still yield
        // `NotChecked`, since `pages` has no `minItems` in the artifact schema.
        let source = TestSource::default();
        let index = SourceIndex::new(&source);
        let resolution = resolve_page(&index, &geometry_free_text_ref());
        assert_eq!(resolution.check, PageCheck::NotChecked);
        assert_eq!(resolution.page_id, None);
    }

    /// A source whose elements declare no geometry. Not reachable through
    /// `ethos.grounding.v1`, which still requires `bbox` on the wire — this exercises the
    /// Rust-level `None` that WP-0 task 0.2 made expressible.
    struct GeometryFree(TestSource);
    impl GroundingSource for GeometryFree {
        fn parser(&self) -> ParserIdentity {
            self.0.parser()
        }
        fn capabilities(&self) -> Capabilities {
            self.0.capabilities()
        }
        fn fingerprint(&self) -> Option<String> {
            self.0.fingerprint()
        }
        fn pages(&self) -> Vec<PageGeometry> {
            self.0.pages()
        }
        fn elements(&self) -> Vec<GroundingElement> {
            self.0
                .elements()
                .into_iter()
                .map(|element| GroundingElement {
                    bbox: None,
                    ..element
                })
                .collect()
        }
        fn spans(&self) -> Vec<GroundingSpan> {
            Vec::new()
        }
        fn tables(&self) -> Vec<GroundingTable> {
            Vec::new()
        }
    }

    #[test]
    fn absent_element_geometry_never_satisfies_a_bbox_query() {
        // Fail closed. An element that declares no box contains nothing, so a bbox
        // locator over a geometry-free source resolves to NotFound rather than matching
        // on the text alone. The failure this guards against is treating `None` as a
        // wildcard, which would make every bbox query succeed against every element.
        let source = GeometryFree(TestSource::default());
        let index = SourceIndex::new(&source);
        let mut evidence_ref = geometry_free_text_ref();
        evidence_ref.required_anchor_level = AnchorLevel::Bbox;
        evidence_ref.locator.page_id = Some("p0001".into());
        evidence_ref.locator.bbox = Some([7200, 10100, 54000, 11500]);

        assert_eq!(
            resolve_bbox(&index, &evidence_ref, Some("p0001")),
            BboxCheck::NotFound
        );
    }

    #[test]
    fn adjacent_quote_join_refuses_elements_without_geometry() {
        // The adjacency join reads two boxes to decide they touch. With no boxes there is
        // nothing to compare, so the join must decline rather than fall back to reading
        // order — the same posture the join already takes for CoordinateOrigin::Unknown.
        let source = GeometryFree(TestSource::default());
        let config = VerificationConfig::default_v1();
        let elements = source.elements();

        assert!(
            adjacent_text_pair_target(&elements[0], &elements[1], "anything", &config).is_none(),
            "a pair with no declared geometry must not be joined"
        );
    }

    #[test]
    fn geometry_free_text_ref_binds_with_no_capability_limit() {
        // End to end: the four steps above compose into `Bound`. The bbox axis must read
        // `NotChecked` rather than `CapabilityLimited` — the ref never asked for geometry,
        // so nothing was downgraded and the caller is owed no warning.
        let source = TestSource::default();
        let report = anchor_evidence(
            &source,
            EvidenceAnchorRequest {
                artifact_type: ethos_core::evidence_anchor::EVIDENCE_ANCHOR_REQUEST_ARTIFACT_TYPE
                    .to_string(),
                schema_version: ethos_core::SCHEMA_VERSION.to_string(),
                source_fingerprint: None,
                evidence_refs: vec![geometry_free_text_ref()],
                report_options: None,
            },
        )
        .expect("a geometry-free text ref is a valid request");

        let anchor = &report.anchors[0];
        assert_eq!(anchor.anchor_status, AnchorStatus::Bound);
        assert_eq!(anchor.achieved_anchor_level, AnchorLevel::Text);
        assert_eq!(anchor.checks.page, PageCheck::NotChecked);
        assert_eq!(anchor.checks.bbox, BboxCheck::NotChecked);
        assert_eq!(anchor.checks.text, TextCheck::Matched);
        assert!(
            anchor.capability_limits.is_empty(),
            "a ref that asked for no geometry was not downgraded: {:?}",
            anchor.capability_limits
        );
    }
}
