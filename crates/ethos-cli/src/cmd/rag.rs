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

struct RagChunkRefs<'a> {
    page_ids: BTreeSet<&'a str>,
    element_ids: BTreeSet<&'a str>,
    warning_codes: BTreeMap<&'a str, &'a str>,
    schema_version: &'a str,
    document_fingerprint: &'a str,
    source_fingerprint: &'a str,
    config_sha256: &'a str,
}

impl<'a> RagChunkRefs<'a> {
    fn new(doc: &'a Document) -> Self {
        Self {
            page_ids: doc
                .payload
                .pages
                .iter()
                .map(|page| page.id.as_str())
                .collect(),
            element_ids: doc
                .payload
                .elements
                .iter()
                .map(|element| element.id.as_str())
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
    for id in &chunk.element_refs {
        if !refs.element_ids.contains(id.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} references unknown element_ref {}",
                chunk.id, id
            )));
        }
    }
    for id in &chunk.page_refs {
        if !refs.page_ids.contains(id.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} references unknown page_ref {}",
                chunk.id, id
            )));
        }
    }
    for (idx, bbox) in chunk.bboxes.iter().enumerate() {
        if !refs.page_ids.contains(bbox.page.as_str()) {
            return Err(Failure::Usage(format!(
                "chunk {} bboxes[{}] references unknown page_ref {}",
                chunk.id, idx, bbox.page
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
