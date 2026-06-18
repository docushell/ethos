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

use std::collections::{BTreeMap, BTreeSet};

use ethos_core::codes::WarningCode;
use ethos_core::error::EthosError;
use ethos_core::model::{Chunk, Document};

use crate::{read_document, write_output, Failure, RagChunkArgs};

pub(crate) fn rag_chunk(args: RagChunkArgs) -> Result<(), Failure> {
    let doc = read_document(&args.input)?;
    let out = rag_chunk_output_bytes(&doc)?;
    write_output(args.out, &out)
}

fn rag_chunk_output_bytes(doc: &Document) -> Result<Vec<u8>, Failure> {
    let refs = RagChunkRefs::new(doc);
    let mut out = Vec::with_capacity(4096);
    for chunk in &doc.payload.chunks {
        validate_chunk_refs(chunk, &refs)?;
        let line = ethos_core::c14n::c14n_bytes(&rag_chunk_record(chunk, &refs)?)
            .map_err(|e| EthosError::internal(e.message))?;
        out.extend_from_slice(&line);
        out.push(b'\n');
    }
    Ok(out)
}

#[derive(Clone, Copy)]
struct PageBounds {
    width: i64,
    height: i64,
}

struct RagChunkRefs<'a> {
    page_bounds: BTreeMap<&'a str, PageBounds>,
    element_pages: BTreeMap<&'a str, &'a str>,
    element_span_refs: BTreeMap<&'a str, &'a [String]>,
    element_warning_refs: BTreeMap<&'a str, &'a [String]>,
    excluded_element_warnings: BTreeMap<&'a str, (&'a str, WarningCode)>,
    excluded_span_warnings: BTreeMap<&'a str, (&'a str, WarningCode)>,
    warning_codes: BTreeMap<&'a str, WarningCode>,
    schema_version: &'a str,
    document_fingerprint: &'a str,
    source_fingerprint: &'a str,
    config_sha256: &'a str,
}

impl<'a> RagChunkRefs<'a> {
    fn new(doc: &'a Document) -> Self {
        let mut excluded_element_warnings = BTreeMap::new();
        let mut excluded_span_warnings = BTreeMap::new();
        let mut warning_codes = BTreeMap::new();
        for warning in doc
            .payload
            .security_warnings
            .iter()
            .chain(doc.payload.parser_warnings.iter())
        {
            warning_codes.insert(warning.id.as_str(), warning.code);
            if warning.code.excludes_from_default_chunks() {
                if let Some(element_ref) = warning.element_ref.as_deref() {
                    excluded_element_warnings
                        .insert(element_ref, (warning.id.as_str(), warning.code));
                }
                if let Some(span_ref) = warning.span_ref.as_deref() {
                    excluded_span_warnings.insert(span_ref, (warning.id.as_str(), warning.code));
                }
            }
        }

        Self {
            page_bounds: doc
                .payload
                .pages
                .iter()
                .map(|page| {
                    (
                        page.id.as_str(),
                        PageBounds {
                            width: page.width,
                            height: page.height,
                        },
                    )
                })
                .collect(),
            element_pages: doc
                .payload
                .elements
                .iter()
                .map(|element| (element.id.as_str(), element.page.as_str()))
                .collect(),
            element_span_refs: doc
                .payload
                .elements
                .iter()
                .map(|element| (element.id.as_str(), element.span_refs.as_slice()))
                .collect(),
            element_warning_refs: doc
                .payload
                .elements
                .iter()
                .map(|element| (element.id.as_str(), element.warning_refs.as_slice()))
                .collect(),
            excluded_element_warnings,
            excluded_span_warnings,
            warning_codes,
            schema_version: doc.schema_version.as_str(),
            document_fingerprint: doc.fingerprint.as_str(),
            source_fingerprint: doc.source.fingerprint.as_str(),
            config_sha256: doc.config_sha256.as_str(),
        }
    }
}

fn validate_chunk_refs(chunk: &Chunk, refs: &RagChunkRefs<'_>) -> Result<(), Failure> {
    validate_chunk_required_refs(chunk)?;
    let page_refs = validate_chunk_page_refs(chunk, refs)?;
    let mut backed_pages = BTreeSet::new();
    validate_chunk_element_refs(chunk, refs, &page_refs, &mut backed_pages)?;
    validate_chunk_bboxes(chunk, refs, &page_refs, &mut backed_pages)?;
    validate_backed_page_refs(chunk, &page_refs, &backed_pages)?;
    validate_chunk_warning_refs(chunk, refs)
}

fn validate_chunk_required_refs(chunk: &Chunk) -> Result<(), Failure> {
    if chunk.element_refs.is_empty() {
        return Err(Failure::Usage(format!(
            "chunk {} must include at least one element_ref",
            chunk.id
        )));
    }
    if chunk.page_refs.is_empty() {
        return Err(Failure::Usage(format!(
            "chunk {} must include at least one page_ref",
            chunk.id
        )));
    }
    if chunk.bboxes.is_empty() {
        return Err(Failure::Usage(format!(
            "chunk {} must include at least one bbox",
            chunk.id
        )));
    }
    Ok(())
}

fn validate_chunk_page_refs<'a>(
    chunk: &'a Chunk,
    refs: &RagChunkRefs<'a>,
) -> Result<BTreeSet<&'a str>, Failure> {
    let mut page_refs = BTreeSet::new();
    for id in &chunk.page_refs {
        if !refs.page_bounds.contains_key(id.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} references unknown page_ref {}",
                chunk.id, id
            )));
        }
        if !page_refs.insert(id.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} has duplicate page_ref {}",
                chunk.id, id
            )));
        }
    }
    Ok(page_refs)
}

fn validate_chunk_element_refs<'a>(
    chunk: &'a Chunk,
    refs: &RagChunkRefs<'a>,
    page_refs: &BTreeSet<&'a str>,
    backed_pages: &mut BTreeSet<&'a str>,
) -> Result<(), Failure> {
    let mut element_refs = BTreeSet::new();
    for id in &chunk.element_refs {
        let Some(page) = refs.element_pages.get(id.as_str()) else {
            return Err(Failure::Usage(format!(
                "chunk {} references unknown element_ref {}",
                chunk.id, id
            )));
        };
        if !page_refs.contains(page) {
            return Err(Failure::Usage(format!(
                "chunk {} element_ref {} page {} is not listed in page_refs",
                chunk.id, id, page
            )));
        }
        if !element_refs.insert(id.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} has duplicate element_ref {}",
                chunk.id, id
            )));
        }
        validate_element_default_chunk_warnings(chunk, id, refs)?;
        backed_pages.insert(*page);
    }
    Ok(())
}

fn validate_chunk_bboxes<'a>(
    chunk: &'a Chunk,
    refs: &RagChunkRefs<'a>,
    page_refs: &BTreeSet<&'a str>,
    backed_pages: &mut BTreeSet<&'a str>,
) -> Result<(), Failure> {
    let mut bboxes = BTreeSet::new();
    for (idx, bbox) in chunk.bboxes.iter().enumerate() {
        let Some(page_bounds) = refs.page_bounds.get(bbox.page.as_str()) else {
            return Err(Failure::Usage(format!(
                "chunk {} bboxes[{}] references unknown page_ref {}",
                chunk.id, idx, bbox.page
            )));
        };
        if !page_refs.contains(bbox.page.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} bboxes[{}] page {} is not listed in page_refs",
                chunk.id, idx, bbox.page
            )));
        }
        let [x0, y0, x1, y1] = bbox.bbox.to_array();
        if x0 >= x1 || y0 >= y1 {
            return Err(Failure::Usage(format!(
                "chunk {} bboxes[{}] has zero area",
                chunk.id, idx
            )));
        }
        if x0 < 0 || y0 < 0 || x1 > page_bounds.width || y1 > page_bounds.height {
            return Err(Failure::Usage(format!(
                "chunk {} bboxes[{}] exceeds page {} bounds",
                chunk.id, idx, bbox.page
            )));
        }
        if !bboxes.insert((bbox.page.as_str(), bbox.bbox.to_array())) {
            return Err(Failure::Usage(format!(
                "chunk {} bboxes[{}] duplicates an earlier bbox on page {}",
                chunk.id, idx, bbox.page
            )));
        }
        backed_pages.insert(bbox.page.as_str());
    }
    Ok(())
}

fn validate_backed_page_refs(
    chunk: &Chunk,
    page_refs: &BTreeSet<&str>,
    backed_pages: &BTreeSet<&str>,
) -> Result<(), Failure> {
    for id in page_refs {
        if !backed_pages.contains(id) {
            return Err(Failure::Usage(format!(
                "chunk {} page_ref {} is not backed by element_refs or bboxes",
                chunk.id, id
            )));
        }
    }
    Ok(())
}

fn validate_chunk_warning_refs(chunk: &Chunk, refs: &RagChunkRefs<'_>) -> Result<(), Failure> {
    for id in &chunk.warning_refs {
        let Some(code) = refs.warning_codes.get(id.as_str()) else {
            return Err(Failure::Usage(format!(
                "chunk {} references unknown warning_ref {}",
                chunk.id, id
            )));
        };
        if code.excludes_from_default_chunks() {
            return Err(Failure::Usage(format!(
                "chunk {} references default-excluded warning_ref {} ({})",
                chunk.id,
                id,
                code.as_str()
            )));
        }
    }
    Ok(())
}

fn validate_element_default_chunk_warnings(
    chunk: &Chunk,
    element_ref: &str,
    refs: &RagChunkRefs<'_>,
) -> Result<(), Failure> {
    for warning_ref in refs
        .element_warning_refs
        .get(element_ref)
        .into_iter()
        .flat_map(|warning_refs| warning_refs.iter())
    {
        let Some(code) = refs.warning_codes.get(warning_ref.as_str()) else {
            return Err(Failure::Usage(format!(
                "chunk {} element_ref {} references unknown warning_ref {}",
                chunk.id, element_ref, warning_ref
            )));
        };
        if code.excludes_from_default_chunks() {
            return Err(Failure::Usage(format!(
                "chunk {} element_ref {} carries default-excluded warning_ref {} ({})",
                chunk.id,
                element_ref,
                warning_ref,
                code.as_str()
            )));
        }
    }
    if let Some((warning_ref, code)) = refs.excluded_element_warnings.get(element_ref) {
        return Err(Failure::Usage(format!(
            "chunk {} element_ref {} carries default-excluded warning_ref {} ({})",
            chunk.id,
            element_ref,
            warning_ref,
            code.as_str()
        )));
    }
    for span_ref in refs
        .element_span_refs
        .get(element_ref)
        .into_iter()
        .flat_map(|span_refs| span_refs.iter())
    {
        if let Some((warning_ref, code)) = refs.excluded_span_warnings.get(span_ref.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} element_ref {} includes span_ref {} with default-excluded warning_ref {} ({})",
                chunk.id,
                element_ref,
                span_ref,
                warning_ref,
                code.as_str()
            )));
        }
    }
    Ok(())
}

fn rag_chunk_record(chunk: &Chunk, refs: &RagChunkRefs<'_>) -> Result<serde_json::Value, Failure> {
    let mut record = serde_json::Map::new();
    record.insert(
        "schema_version".into(),
        serde_json::Value::String(refs.schema_version.to_string()),
    );
    record.insert(
        "document_fingerprint".into(),
        serde_json::Value::String(refs.document_fingerprint.to_string()),
    );
    record.insert(
        "source_fingerprint".into(),
        serde_json::Value::String(refs.source_fingerprint.to_string()),
    );
    record.insert(
        "config_sha256".into(),
        serde_json::Value::String(refs.config_sha256.to_string()),
    );
    record.insert("id".into(), serde_json::Value::String(chunk.id.clone()));
    record.insert("text".into(), serde_json::Value::String(chunk.text.clone()));
    record.insert(
        "element_refs".into(),
        serde_json::Value::Array(
            chunk
                .element_refs
                .iter()
                .cloned()
                .map(serde_json::Value::String)
                .collect(),
        ),
    );
    record.insert(
        "page_refs".into(),
        serde_json::Value::Array(
            chunk
                .page_refs
                .iter()
                .cloned()
                .map(serde_json::Value::String)
                .collect(),
        ),
    );
    record.insert(
        "bboxes".into(),
        serde_json::to_value(&chunk.bboxes).map_err(|e| EthosError::internal(e.to_string()))?,
    );
    record.insert(
        "token_estimate".into(),
        serde_json::to_value(&chunk.token_estimate)
            .map_err(|e| EthosError::internal(e.to_string()))?,
    );
    let mut warnings = Vec::with_capacity(chunk.warning_refs.len());
    for id in &chunk.warning_refs {
        let code = refs
            .warning_codes
            .get(id.as_str())
            .expect("chunk warning_refs validated before record serialization");
        warnings.push(serde_json::Value::String(code.as_str().to_string()));
    }
    record.insert("warnings".into(), serde_json::Value::Array(warnings));
    Ok(serde_json::Value::Object(record))
}
