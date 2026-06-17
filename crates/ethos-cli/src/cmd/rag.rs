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
    warning_codes: BTreeMap<&'a str, &'a str>,
    schema_version: &'a str,
    document_fingerprint: &'a str,
    source_fingerprint: &'a str,
    config_sha256: &'a str,
}

impl<'a> RagChunkRefs<'a> {
    fn new(doc: &'a Document) -> Self {
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
            warning_codes: doc
                .payload
                .security_warnings
                .iter()
                .chain(doc.payload.parser_warnings.iter())
                .map(|warning| (warning.id.as_str(), warning.code.as_str()))
                .collect(),
            schema_version: doc.schema_version.as_str(),
            document_fingerprint: doc.fingerprint.as_str(),
            source_fingerprint: doc.source.fingerprint.as_str(),
            config_sha256: doc.config_sha256.as_str(),
        }
    }
}

fn validate_chunk_refs(chunk: &Chunk, refs: &RagChunkRefs<'_>) -> Result<(), Failure> {
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

    let mut page_refs = BTreeSet::new();
    for id in &chunk.page_refs {
        if !refs.page_bounds.contains_key(id.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} references unknown page_ref {}",
                chunk.id, id
            )));
        }
        page_refs.insert(id.as_str());
    }

    let mut backed_pages = BTreeSet::new();
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
        backed_pages.insert(*page);
    }
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
        backed_pages.insert(bbox.page.as_str());
    }
    for id in page_refs {
        if !backed_pages.contains(id) {
            return Err(Failure::Usage(format!(
                "chunk {} page_ref {} is not backed by element_refs or bboxes",
                chunk.id, id
            )));
        }
    }
    for id in &chunk.warning_refs {
        if !refs.warning_codes.contains_key(id.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} references unknown warning_ref {}",
                chunk.id, id
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
        warnings.push(serde_json::Value::String(code.to_string()));
    }
    record.insert("warnings".into(), serde_json::Value::Array(warnings));
    Ok(serde_json::Value::Object(record))
}
