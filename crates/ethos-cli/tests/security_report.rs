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

fn run_ethos(args: &[&str]) -> Output {
    Command::new(ethos_bin())
        .args(args)
        .output()
        .expect("ethos command runs")
}

fn temp_path(name: &str, extension: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock after unix epoch")
        .as_nanos();
    std::env::temp_dir().join(format!("ethos-{name}-{nanos}.{extension}"))
}

fn json_file(path: impl AsRef<Path>) -> Value {
    let bytes = std::fs::read(path).expect("JSON fixture is readable");
    serde_json::from_slice(&bytes).expect("JSON fixture parses")
}

fn temp_json(name: &str, json: &str) -> PathBuf {
    let path = temp_path(name, "json");
    std::fs::write(&path, json).expect("temp JSON is writable");
    path
}

fn document_with_mutated_warning(name: &str, mutate: impl FnOnce(&mut Value)) -> PathBuf {
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
fn security_report_derives_text_backed_warning_from_document() {
    let output = run_ethos(&["security", "report", document_example().to_str().unwrap()]);

    assert!(
        output.status.success(),
        "ethos security report failed\nstatus: {:?}\nstderr:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(output.stderr, b"");

    let report: Value = serde_json::from_slice(&output.stdout).expect("report JSON parses");
    assert_eq!(report["schema_version"], "1.0.0");
    assert_eq!(
        report["document_fingerprint"],
        "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3"
    );
    assert_eq!(report["summary"]["hidden_text_detected"], 1);
    assert_eq!(report["findings"].as_array().unwrap().len(), 1);
    assert_eq!(report["findings"][0]["id"], "f0001");
    assert_eq!(report["findings"][0]["code"], "hidden_text_detected");
    assert_eq!(
        report["findings"][0]["message"],
        "hidden text detected: excluded from default chunks"
    );
    assert_eq!(report["findings"][0]["page"], "p0001");
    assert_eq!(report["findings"][0]["span_ref"], "s000003");
    assert_eq!(
        report["findings"][0]["bbox"],
        serde_json::json!([100, 79100, 6000, 79200])
    );
    assert_eq!(
        report["findings"][0]["text_preview"],
        "internal-draft-do-not-cite"
    );
    assert_eq!(report["findings"][0]["excluded_from_default_chunks"], true);
    for key in ["annotations", "actions", "attachments", "scripts", "links"] {
        assert_eq!(report["inventories"][key], serde_json::json!([]));
    }
}

#[test]
fn security_report_out_writes_same_bytes_as_stdout() {
    let stdout_output = run_ethos(&["security", "report", document_example().to_str().unwrap()]);
    assert!(
        stdout_output.status.success(),
        "ethos security report failed\nstatus: {:?}\nstderr:\n{}",
        stdout_output.status.code(),
        String::from_utf8_lossy(&stdout_output.stderr)
    );

    let out = temp_path("security-report-out", "json");
    let output = run_ethos(&[
        "security",
        "report",
        document_example().to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
    ]);

    assert!(
        output.status.success(),
        "ethos security report --out failed\nstatus: {:?}\nstderr:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(output.stdout, b"");
    assert_eq!(output.stderr, b"");
    assert_eq!(
        std::fs::read(&out).expect("--out report is readable"),
        stdout_output.stdout
    );
    let _ = std::fs::remove_file(out);
}

#[test]
fn security_report_output_is_byte_identical_across_runs() {
    let first = run_ethos(&["security", "report", document_example().to_str().unwrap()]);
    let second = run_ethos(&["security", "report", document_example().to_str().unwrap()]);

    assert!(
        first.status.success(),
        "first ethos security report failed\nstatus: {:?}\nstderr:\n{}",
        first.status.code(),
        String::from_utf8_lossy(&first.stderr)
    );
    assert!(
        second.status.success(),
        "second ethos security report failed\nstatus: {:?}\nstderr:\n{}",
        second.status.code(),
        String::from_utf8_lossy(&second.stderr)
    );
    assert_eq!(first.stderr, b"");
    assert_eq!(second.stderr, b"");
    assert_eq!(first.stdout, second.stdout);
}

#[test]
fn security_report_rejects_inventory_backed_warning_without_inventory_source() {
    for code in [
        "annotations_present",
        "external_links_present",
        "unsupported_annotation",
    ] {
        let document = document_with_mutated_warning("inventory-backed-security-warning", |doc| {
            doc["payload"]["security_warnings"][0]["code"] = serde_json::json!(code);
            doc["payload"]["security_warnings"][0]["message"] =
                serde_json::json!("inventory-backed warning present");
            doc["payload"]["security_warnings"][0]
                .as_object_mut()
                .unwrap()
                .remove("span_ref");
        });

        let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

        assert_eq!(output.status.code(), Some(2), "{code}");
        assert_eq!(output.stdout, b"", "{code}");
        assert!(
            String::from_utf8_lossy(&output.stderr).contains(&format!(
                "security report warning w0001 ({code}) requires inventory data not available in canonical document"
            )),
            "{code}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn security_report_ignores_reportable_parser_warnings() {
    let document = document_with_mutated_warning("reportable-parser-warning", |doc| {
        doc["payload"]["parser_warnings"][0]["code"] = serde_json::json!("hidden_text_detected");
        doc["payload"]["parser_warnings"][0]["message"] =
            serde_json::json!("parser warning must stay outside security report");
        doc["payload"]["parser_warnings"][0]["span_ref"] = serde_json::json!("s000002");
        doc["payload"]["parser_warnings"][0]
            .as_object_mut()
            .unwrap()
            .remove("element_ref");
    });

    let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

    assert!(
        output.status.success(),
        "ethos security report failed\nstatus: {:?}\nstderr:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    let report: Value = serde_json::from_slice(&output.stdout).expect("report JSON parses");
    assert_eq!(report["summary"]["hidden_text_detected"], 1);
    assert_eq!(report["findings"].as_array().unwrap().len(), 1);
}

#[test]
fn security_report_rejects_non_security_code_in_security_warnings() {
    let document = document_with_mutated_warning("non-security-code-in-security-warning", |doc| {
        doc["payload"]["security_warnings"][0]["code"] =
            serde_json::json!("low_confidence_reading_order");
        doc["payload"]["security_warnings"][0]["message"] =
            serde_json::json!("parser warning code in security warnings");
        doc["payload"]["security_warnings"][0]
            .as_object_mut()
            .unwrap()
            .remove("span_ref");
    });

    let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(
        "security report warning w0001 (low_confidence_reading_order) is not a security warning code"
    ));
}

#[test]
fn security_report_rejects_text_warning_without_span_ref() {
    let document = document_with_mutated_warning("text-warning-without-span-ref", |doc| {
        doc["payload"]["security_warnings"][0]
            .as_object_mut()
            .unwrap()
            .remove("span_ref");
    });

    let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("security report warning w0001 (hidden_text_detected) requires span_ref"));
}

#[test]
fn security_report_rejects_text_warning_without_page() {
    let document = document_with_mutated_warning("text-warning-without-page", |doc| {
        doc["payload"]["security_warnings"][0]
            .as_object_mut()
            .unwrap()
            .remove("page");
    });

    let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("security report warning w0001 (hidden_text_detected) requires page"));
}

#[test]
fn security_report_rejects_image_only_warning_without_page() {
    let document = document_with_mutated_warning("image-only-warning-without-page", |doc| {
        doc["payload"]["security_warnings"][0]["code"] = serde_json::json!("image_only_page");
        doc["payload"]["security_warnings"][0]["message"] = serde_json::json!("image-only page");
        doc["payload"]["security_warnings"][0]
            .as_object_mut()
            .unwrap()
            .remove("span_ref");
        doc["payload"]["security_warnings"][0]
            .as_object_mut()
            .unwrap()
            .remove("page");
    });

    let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("security report warning w0001 (image_only_page) requires page"));
}

#[test]
fn security_report_derives_image_only_page_warning() {
    let document = document_with_mutated_warning("image-only-warning", |doc| {
        doc["payload"]["security_warnings"][0]["code"] = serde_json::json!("image_only_page");
        doc["payload"]["security_warnings"][0]["message"] = serde_json::json!("image-only page");
        doc["payload"]["security_warnings"][0]
            .as_object_mut()
            .unwrap()
            .remove("span_ref");
    });

    let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

    assert!(
        output.status.success(),
        "ethos security report failed\nstatus: {:?}\nstderr:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(output.stderr, b"");
    let report: Value = serde_json::from_slice(&output.stdout).expect("report JSON parses");
    assert_eq!(report["summary"]["image_only_page"], 1);
    assert_eq!(report["findings"].as_array().unwrap().len(), 1);
    assert_eq!(report["findings"][0]["code"], "image_only_page");
    assert_eq!(report["findings"][0]["page"], "p0001");
    assert!(report["findings"][0].get("bbox").is_none());
    assert!(report["findings"][0].get("span_ref").is_none());
    assert_eq!(report["findings"][0]["excluded_from_default_chunks"], false);
}

#[test]
fn security_report_rejects_unknown_span_ref() {
    let document = document_with_mutated_warning("security-warning-unknown-span-ref", |doc| {
        doc["payload"]["security_warnings"][0]["span_ref"] = serde_json::json!("s999999");
    });

    let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("security report warning w0001 references unknown span_ref s999999"));
}

#[test]
fn security_report_rejects_span_not_owned_by_element_ref() {
    let document = document_with_mutated_warning("security-warning-span-element-mismatch", |doc| {
        doc["payload"]["security_warnings"][0]["element_ref"] = serde_json::json!("e000001");
    });

    let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(
        "security report warning w0001 span_ref s000003 is not owned by element_ref e000001"
    ));
}

#[test]
fn security_report_rejects_invalid_text_warning_span_bbox() {
    for (name, bbox, expected) in [
        (
            "zero-width",
            serde_json::json!([100, 79100, 100, 79200]),
            "security report warning w0001 span_ref s000003 bbox has zero area",
        ),
        (
            "zero-height",
            serde_json::json!([100, 79100, 6000, 79100]),
            "security report warning w0001 span_ref s000003 bbox has zero area",
        ),
        (
            "negative-x",
            serde_json::json!([-1, 79100, 6000, 79200]),
            "security report warning w0001 span_ref s000003 bbox exceeds page p0001 bounds",
        ),
        (
            "negative-y",
            serde_json::json!([100, -1, 6000, 79200]),
            "security report warning w0001 span_ref s000003 bbox exceeds page p0001 bounds",
        ),
        (
            "x-exceeds-page",
            serde_json::json!([100, 79100, 61201, 79200]),
            "security report warning w0001 span_ref s000003 bbox exceeds page p0001 bounds",
        ),
        (
            "y-exceeds-page",
            serde_json::json!([100, 79100, 6000, 79201]),
            "security report warning w0001 span_ref s000003 bbox exceeds page p0001 bounds",
        ),
    ] {
        let document = document_with_mutated_warning(
            &format!("security-warning-invalid-span-bbox-{name}"),
            |doc| {
                doc["payload"]["spans"][2]["bbox"] = bbox;
            },
        );

        let output = run_ethos(&["security", "report", document.to_str().unwrap()]);

        assert_eq!(output.status.code(), Some(2), "{name}");
        assert_eq!(output.stdout, b"", "{name}");
        assert!(
            String::from_utf8_lossy(&output.stderr).contains(expected),
            "{name}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}
