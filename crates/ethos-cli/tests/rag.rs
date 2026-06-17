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

fn append_next_page(doc: &mut Value) -> String {
    let pages = doc["payload"]["pages"]
        .as_array_mut()
        .expect("fixture pages are an array");
    let first_page = pages.first().expect("fixture has at least one page");
    let first_id = first_page["id"]
        .as_str()
        .expect("fixture page id is a string");
    let next_id = format!(
        "p{:04}",
        first_id[1..]
            .parse::<u32>()
            .expect("fixture page id has numeric suffix")
            + 1
    );
    let mut page = first_page.clone();
    page["id"] = serde_json::json!(next_id);
    page["index"] = serde_json::json!(pages.len() + 1);
    pages.push(page);
    next_id
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
fn rag_chunk_rejects_empty_chunk_element_refs() {
    let document = document_with_mutated_chunk("empty-chunk-element-refs-document", |doc| {
        doc["payload"]["chunks"][0]["element_refs"] = serde_json::json!([]);
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("chunk c000001 must include at least one element_ref"));
}

#[test]
fn rag_chunk_rejects_empty_chunk_page_refs() {
    let document = document_with_mutated_chunk("empty-chunk-page-refs-document", |doc| {
        doc["payload"]["chunks"][0]["page_refs"] = serde_json::json!([]);
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("chunk c000001 must include at least one page_ref"));
}

#[test]
fn rag_chunk_rejects_empty_chunk_bboxes() {
    let document = document_with_mutated_chunk("empty-chunk-bboxes-document", |doc| {
        doc["payload"]["chunks"][0]["bboxes"] = serde_json::json!([]);
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("chunk c000001 must include at least one bbox"));
}

#[test]
fn rag_chunk_rejects_chunk_bbox_page_not_listed_in_page_refs() {
    let mut expected_page_id = String::new();
    let document = document_with_mutated_chunk("chunk-bbox-page-not-listed-document", |doc| {
        expected_page_id = append_next_page(doc);
        doc["payload"]["chunks"][0]["bboxes"][0]["page"] =
            serde_json::json!(expected_page_id.clone());
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(&format!(
        "chunk c000001 bboxes[0] page {expected_page_id} is not listed in page_refs"
    )));
}

#[test]
fn rag_chunk_rejects_chunk_element_page_not_listed_in_page_refs() {
    let mut expected_element_id = String::new();
    let mut expected_page_id = String::new();
    let document = document_with_mutated_chunk("chunk-element-page-not-listed-document", |doc| {
        expected_element_id = doc["payload"]["chunks"][0]["element_refs"][0]
            .as_str()
            .expect("fixture chunk element_ref is a string")
            .to_string();
        expected_page_id = append_next_page(doc);
        doc["payload"]["elements"][0]["page"] = serde_json::json!(expected_page_id.clone());
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(&format!(
        "chunk c000001 element_ref {expected_element_id} page {expected_page_id} is not listed in page_refs"
    )));
}

#[test]
fn rag_chunk_rejects_unbacked_chunk_page_ref() {
    let mut expected_page_id = String::new();
    let document = document_with_mutated_chunk("unbacked-chunk-page-ref-document", |doc| {
        expected_page_id = append_next_page(doc);
        doc["payload"]["chunks"][0]["page_refs"]
            .as_array_mut()
            .expect("fixture chunk page_refs are an array")
            .push(serde_json::json!(expected_page_id.clone()));
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(&format!(
        "chunk c000001 page_ref {expected_page_id} is not backed by element_refs or bboxes"
    )));
}

#[test]
fn rag_chunk_rejects_zero_area_chunk_bbox() {
    let document = document_with_mutated_chunk("zero-area-chunk-bbox-document", |doc| {
        let x0 = doc["payload"]["chunks"][0]["bboxes"][0]["bbox"][0]
            .as_i64()
            .expect("fixture bbox x0 is an integer");
        doc["payload"]["chunks"][0]["bboxes"][0]["bbox"][2] = serde_json::json!(x0);
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("chunk c000001 bboxes[0] has zero area")
    );
}

#[test]
fn rag_chunk_rejects_out_of_bounds_chunk_bbox() {
    let mut expected_page_id = String::new();
    let document = document_with_mutated_chunk("out-of-bounds-chunk-bbox-document", |doc| {
        expected_page_id = doc["payload"]["chunks"][0]["bboxes"][0]["page"]
            .as_str()
            .expect("fixture bbox page is a string")
            .to_string();
        let page_width = doc["payload"]["pages"][0]["width"]
            .as_i64()
            .expect("fixture page width is an integer");
        doc["payload"]["chunks"][0]["bboxes"][0]["bbox"][2] = serde_json::json!(page_width + 1);
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(&format!(
        "chunk c000001 bboxes[0] exceeds page {expected_page_id} bounds"
    )));
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

#[test]
fn rag_chunk_rejects_default_excluded_chunk_warning_refs() {
    for code in [
        "hidden_text_detected",
        "off_page_text_detected",
        "low_contrast_text_detected",
    ] {
        let document = document_with_mutated_chunk(
            &format!("default-excluded-{code}-chunk-document"),
            |doc| {
                doc["payload"]["security_warnings"][0]["code"] = serde_json::json!(code);
                doc["payload"]["chunks"][0]["warning_refs"] = serde_json::json!(["w0001"]);
            },
        );
        let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

        assert_eq!(output.status.code(), Some(2));
        assert_eq!(output.stdout, b"");
        assert!(String::from_utf8_lossy(&output.stderr).contains(&format!(
            "chunk c000001 references default-excluded warning_ref w0001 ({code})"
        )));
    }
}

#[test]
fn rag_chunk_allows_non_exclusion_security_warning_ref() {
    let document = document_with_mutated_chunk("non-exclusion-security-warning-document", |doc| {
        doc["payload"]["security_warnings"][0]["code"] = serde_json::json!("annotations_present");
        doc["payload"]["chunks"][0]["warning_refs"] = serde_json::json!(["w0001"]);
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert!(
        output.status.success(),
        "ethos rag chunk failed\nstatus: {:?}\nstderr:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(output.stderr, b"");
    assert!(
        String::from_utf8_lossy(&output.stdout).contains(r#""warnings":["annotations_present"]"#)
    );
}

#[test]
fn rag_chunk_rejects_default_excluded_element_warning_ref() {
    let mut expected_element_id = String::new();
    let document =
        document_with_mutated_chunk("default-excluded-element-warning-document", |doc| {
            expected_element_id = doc["payload"]["chunks"][0]["element_refs"][0]
                .as_str()
                .expect("fixture chunk element_ref is a string")
                .to_string();
            doc["payload"]["elements"][0]["warning_refs"] = serde_json::json!(["w0001"]);
        });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(&format!(
        "chunk c000001 element_ref {expected_element_id} carries default-excluded warning_ref w0001 (hidden_text_detected)"
    )));
}

#[test]
fn rag_chunk_rejects_default_excluded_warning_attached_to_cited_element() {
    let mut expected_element_id = String::new();
    let document = document_with_mutated_chunk(
        "default-excluded-attached-element-warning-document",
        |doc| {
            expected_element_id = doc["payload"]["chunks"][0]["element_refs"][0]
                .as_str()
                .expect("fixture chunk element_ref is a string")
                .to_string();
            doc["payload"]["security_warnings"][0]["element_ref"] =
                serde_json::json!(expected_element_id.clone());
        },
    );
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(&format!(
        "chunk c000001 element_ref {expected_element_id} carries default-excluded warning_ref w0001 (hidden_text_detected)"
    )));
}

#[test]
fn rag_chunk_rejects_default_excluded_span_warning_reached_by_cited_element() {
    let mut expected_element_id = String::new();
    let mut expected_span_id = String::new();
    let document = document_with_mutated_chunk("default-excluded-span-warning-document", |doc| {
        expected_element_id = doc["payload"]["chunks"][0]["element_refs"][0]
            .as_str()
            .expect("fixture chunk element_ref is a string")
            .to_string();
        expected_span_id = doc["payload"]["security_warnings"][0]["span_ref"]
            .as_str()
            .expect("fixture security warning span_ref is a string")
            .to_string();
        doc["payload"]["elements"][0]["span_refs"]
            .as_array_mut()
            .expect("fixture element span_refs are an array")
            .push(serde_json::json!(expected_span_id.clone()));
    });
    let output = run_ethos(&["rag", "chunk", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(&format!(
        "chunk c000001 element_ref {expected_element_id} includes span_ref {expected_span_id} with default-excluded warning_ref w0001 (hidden_text_detected)"
    )));
}
