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

use ethos_core::error::EthosError;
use ethos_core::model::{Chunk, Document};

use crate::{read_document, write_output, Failure, RagChunkArgs};

pub(crate) fn rag_chunk(args: RagChunkArgs) -> Result<(), Failure> {
    let doc = read_document(&args.input)?;
    let out = rag_chunk_output_bytes(&doc)?;
    write_output(args.out, &out)
}

fn rag_chunk_output_bytes(doc: &Document) -> Result<Vec<u8>, Failure> {
    let mut out = Vec::with_capacity(4096);
    for chunk in &doc.payload.chunks {
        let line = ethos_core::c14n::c14n_bytes(&rag_chunk_record(doc, chunk)?)
            .map_err(|e| EthosError::internal(e.message))?;
        out.extend_from_slice(&line);
        out.push(b'\n');
    }
    Ok(out)
}

fn rag_chunk_record(doc: &Document, chunk: &Chunk) -> Result<serde_json::Value, Failure> {
    let warning_code = |id: &str| -> Option<&'static str> {
        doc.payload
            .security_warnings
            .iter()
            .chain(doc.payload.parser_warnings.iter())
            .find(|w| w.id == id)
            .map(|w| w.code.as_str())
    };

    let mut record = serde_json::Map::new();
    record.insert(
        "schema_version".into(),
        serde_json::Value::String(doc.schema_version.clone()),
    );
    record.insert(
        "document_fingerprint".into(),
        serde_json::Value::String(doc.fingerprint.clone()),
    );
    record.insert(
        "source_fingerprint".into(),
        serde_json::Value::String(doc.source.fingerprint.clone()),
    );
    record.insert(
        "config_sha256".into(),
        serde_json::Value::String(doc.config_sha256.clone()),
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
    let warnings: Vec<serde_json::Value> = chunk
        .warning_refs
        .iter()
        .filter_map(|id| warning_code(id))
        .map(|c| serde_json::Value::String(c.to_string()))
        .collect();
    record.insert("warnings".into(), serde_json::Value::Array(warnings));
    Ok(serde_json::Value::Object(record))
}
