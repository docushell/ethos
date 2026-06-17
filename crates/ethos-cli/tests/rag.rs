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

use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::{SystemTime, UNIX_EPOCH};

use ethos_core::model::Document;
use serde_json::Value;

fn ethos_bin() -> &'static str {
    env!("CARGO_BIN_EXE_ethos")
}

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn document_example() -> PathBuf {
    repo_root().join("schemas/examples/document.example.json")
}

fn chunks_example() -> PathBuf {
    repo_root().join("schemas/examples/chunks.example.jsonl")
}

fn run_ethos(args: &[&str]) -> Output {
    Command::new(ethos_bin())
        .args(args)
        .output()
        .expect("ethos command runs")
}

fn json_file(path: impl AsRef<Path>) -> Value {
    let bytes = std::fs::read(path).expect("JSON fixture is readable");
    serde_json::from_slice(&bytes).expect("JSON fixture parses")
}

fn temp_json(name: &str, json: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock after unix epoch")
        .as_nanos();
    let path = std::env::temp_dir().join(format!("ethos-{name}-{nanos}.json"));
    std::fs::write(&path, json).expect("temp JSON is writable");
    path
}

fn document_with_mutated_chunk(name: &str, mutate: impl FnOnce(&mut Value)) -> PathBuf {
    let mut doc = json_file(document_example());
    mutate(&mut doc);

    let mut doc: Document = serde_json::from_value(doc).expect("document parses");
    doc.payload_sha256 = doc.compute_payload_sha256().expect("payload hash computes");
    doc.fingerprint = doc.compute_fingerprint().expect("fingerprint computes");
    temp_json(
        name,
        &serde_json::to_string(&doc).expect("document serializes"),
    )
}

#[test]
fn rag_chunk_matches_schema_example_jsonl() {
    let output = run_ethos(&["rag", "chunk", document_example().to_str().unwrap()]);

    assert!(
        output.status.success(),
        "ethos rag chunk failed\nstatus: {:?}\nstderr:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(output.stderr, b"");

    let expected = std::fs::read(chunks_example()).expect("chunks example is readable");
    assert_eq!(output.stdout, expected);
}

#[test]
fn rag_chunk_output_is_byte_identical_across_runs() {
    let first = run_ethos(&["rag", "chunk", document_example().to_str().unwrap()]);
    let second = run_ethos(&["rag", "chunk", document_example().to_str().unwrap()]);

    assert!(
        first.status.success(),
        "first ethos rag chunk failed\nstatus: {:?}\nstderr:\n{}",
        first.status.code(),
        String::from_utf8_lossy(&first.stderr)
    );
    assert!(
        second.status.success(),
        "second ethos rag chunk failed\nstatus: {:?}\nstderr:\n{}",
        second.status.code(),
        String::from_utf8_lossy(&second.stderr)
    );
    assert_eq!(first.stderr, b"");
    assert_eq!(second.stderr, b"");
    assert_eq!(first.stdout, second.stdout);
}

#[test]
fn rag_chunk_rejects_unknown_chunk_element_ref() {
    let document = document_with_mutated_chunk("stale-chunk-element-ref-document", |doc| {
        doc["payload"]["chunks"][0]["element_refs"][0] = serde_json::json!("e999999");
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("chunk c000001 references unknown element_ref e999999"));
}

#[test]
fn rag_chunk_rejects_unknown_chunk_page_ref() {
    let document = document_with_mutated_chunk("stale-chunk-page-ref-document", |doc| {
        doc["payload"]["chunks"][0]["page_refs"][0] = serde_json::json!("p9999");
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("chunk c000001 references unknown page_ref p9999"));
}

#[test]
fn rag_chunk_rejects_unknown_chunk_bbox_page_ref() {
    let document = document_with_mutated_chunk("stale-chunk-bbox-page-ref-document", |doc| {
        doc["payload"]["chunks"][0]["bboxes"][0]["page"] = serde_json::json!("p9999");
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("chunk c000001 bboxes[0] references unknown page_ref p9999"));
}

#[test]
fn rag_chunk_rejects_unknown_chunk_warning_ref() {
    let document = document_with_mutated_chunk("stale-chunk-warning-ref-document", |doc| {
        doc["payload"]["chunks"][0]["warning_refs"] = serde_json::json!(["w999999"]);
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("chunk c000001 references unknown warning_ref w999999"));
}
