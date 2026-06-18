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

use ethos_core::fingerprint::source_fingerprint;
use ethos_core::model::Document;
use serde_json::Value;

fn ethos_bin() -> &'static str {
    env!("CARGO_BIN_EXE_ethos")
}

fn repo_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn run_ethos(args: &[&str]) -> Output {
    Command::new(ethos_bin())
        .args(args)
        .output()
        .expect("ethos command runs")
}

fn parse_success(args: &[&str]) -> Value {
    let output = run_ethos(args);
    assert!(
        output.status.success(),
        "ethos failed\nstatus: {:?}\nstderr:\n{}\nstdout:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    assert_eq!(output.stderr, b"");
    serde_json::from_slice(&output.stdout).expect("stdout is JSON")
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

fn temp_output(name: &str) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock after unix epoch")
        .as_nanos();
    std::env::temp_dir().join(format!("ethos-{name}-{nanos}.json"))
}

fn json_file(path: impl AsRef<Path>) -> Value {
    let bytes = std::fs::read(path).expect("JSON fixture is readable");
    serde_json::from_slice(&bytes).expect("JSON fixture parses")
}

fn temp_split_quote_document() -> (PathBuf, String) {
    let mut doc = json_file(document_example());
    doc["payload"]["elements"] = serde_json::json!([
        {
            "id": "split-a",
            "type": "text_block",
            "page": "p0001",
            "bbox": [100, 100, 400, 200],
            "text": "The alpha trust loop verifies "
        },
        {
            "id": "split-b",
            "type": "text_block",
            "page": "p0001",
            "bbox": [400, 100, 700, 200],
            "text": "grounded evidence"
        }
    ]);
    doc["payload"]["spans"] = serde_json::json!([]);
    doc["payload"]["tables"] = serde_json::json!([]);
    doc["payload"]["chunks"] = serde_json::json!([]);
    doc["payload"]["regions"] = serde_json::json!([]);
    doc["payload"]["security_warnings"] = serde_json::json!([]);
    doc["payload"]["parser_warnings"] = serde_json::json!([]);

    let mut doc: Document = serde_json::from_value(doc).expect("split quote document parses");
    doc.payload_sha256 = doc
        .compute_payload_sha256()
        .expect("split quote payload hash computes");
    doc.fingerprint = doc
        .compute_fingerprint()
        .expect("split quote document fingerprint computes");
    let fingerprint = doc.fingerprint.clone();
    let path = temp_json(
        "split-quote-native-document",
        &serde_json::to_string(&doc).expect("split quote document serializes"),
    );
    (path, fingerprint)
}

fn pdfium_configured() -> bool {
    std::env::var_os("ETHOS_PDFIUM_LIBRARY_PATH")
        .map(PathBuf::from)
        .is_some_and(|path| path.is_file())
}

fn document_example() -> PathBuf {
    repo_root().join("schemas/examples/document.example.json")
}

fn table_regular_grid_fixture() -> PathBuf {
    repo_root().join("fixtures/synthetic/table-regular-grid/document.pdf")
}

fn odl_example() -> PathBuf {
    repo_root().join("examples/verify/opendataloader.json")
}

fn verify_alpha_report_cases() -> Vec<(String, Vec<String>, PathBuf)> {
    let root = repo_root();
    let inventory = json_file(root.join("examples/verify/cases.json"));
    let report_cases = inventory["report_cases"]
        .as_array()
        .expect("verify-alpha report_cases is an array");

    report_cases
        .iter()
        .map(|case| {
            let name = case["name"]
                .as_str()
                .expect("verify-alpha case name is a string")
                .to_string();
            let mut args = vec![
                "verify".to_string(),
                root.join(
                    case["input"]
                        .as_str()
                        .expect("verify-alpha case input is a string"),
                )
                .display()
                .to_string(),
            ];
            if let Some(grounding) = case.get("grounding").and_then(Value::as_str) {
                args.push("--grounding".to_string());
                args.push(grounding.to_string());
            }
            args.push("--citations".to_string());
            args.push(
                root.join(
                    case["citations"]
                        .as_str()
                        .expect("verify-alpha case citations is a string"),
                )
                .display()
                .to_string(),
            );
            let expected = root.join(
                case["golden"]
                    .as_str()
                    .expect("verify-alpha case golden is a string"),
            );
            (name, args, expected)
        })
        .collect()
}

#[test]
fn verify_alpha_schema_report_example_matches_cli_output() {
    let root = repo_root();
    let report = parse_success(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("schemas/examples/citations.example.json")
            .to_str()
            .unwrap(),
    ]);
    let expected = json_file(root.join("schemas/examples/verification-report.example.json"));

    assert_eq!(report, expected);
}

#[test]
fn verify_alpha_demo_reports_match_goldens() {
    for (name, args, expected_path) in verify_alpha_report_cases() {
        let args = args.iter().map(String::as_str).collect::<Vec<_>>();
        let actual = parse_success(&args);
        let expected = json_file(expected_path);
        assert_eq!(actual, expected, "golden drift for {name}");
    }
}

#[test]
fn real_opendataloader_fixture_verifies_against_golden() {
    let root = repo_root();
    let report = parse_success(&[
        "verify",
        root.join("fixtures/foreign/opendataloader/real/opendataloader-output.json")
            .to_str()
            .unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        root.join("fixtures/foreign/opendataloader/real/citations.json")
            .to_str()
            .unwrap(),
    ]);
    let expected = json_file(
        root.join("fixtures/foreign/opendataloader/real/expected.verification_report.json"),
    );

    assert_eq!(report, expected);
    assert_eq!(report["all_evidence_grounded"], true);
    assert_eq!(report["grounding"]["parser"]["name"], "opendataloader-pdf");
    assert_eq!(report["grounding"]["parser"]["version"], "unknown");
    assert_eq!(
        report["grounding"]["parser"]["adapter"],
        "opendataloader-json"
    );
    assert_eq!(report["checks"].as_array().unwrap().len(), 3);
}

#[test]
fn real_opendataloader_ungrounded_fixture_verifies_against_golden() {
    let root = repo_root();
    let grounding = root.join("fixtures/foreign/opendataloader/real/opendataloader-output.json");
    let citations = root.join("fixtures/foreign/opendataloader/real/ungrounded_citations.json");
    let report = parse_success(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);
    let expected =
        json_file(root.join(
            "fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json",
        ));

    assert_eq!(report, expected);
    assert_eq!(report["all_evidence_grounded"], false);
    assert_eq!(report["checks"][0]["status"], "mismatch");
    assert_eq!(report["checks"][0]["match_method"], "normalized_text");
    assert_eq!(report["checks"][0]["reason"], "text_mismatch");

    let gated = run_ethos(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
        "--fail-on-ungrounded",
    ]);
    assert_eq!(gated.status.code(), Some(1));
    assert_eq!(gated.stderr, b"");
    let gated_report: Value = serde_json::from_slice(&gated.stdout).expect("stdout is JSON");
    assert_eq!(gated_report, expected);
}

#[test]
fn fail_on_ungrounded_exits_zero_when_all_evidence_is_grounded() {
    let root = repo_root();
    let output = run_ethos(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_grounded_citations.json")
            .to_str()
            .unwrap(),
        "--fail-on-ungrounded",
    ]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(output.stderr, b"");
    let report: Value = serde_json::from_slice(&output.stdout).expect("stdout is JSON");
    assert_eq!(report["all_evidence_grounded"], true);
}

#[test]
fn fail_on_ungrounded_exits_one_after_writing_stale_report() {
    let root = repo_root();
    let out = temp_output("stale-fail-on-ungrounded");
    let output = run_ethos(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_stale_citations.json")
            .to_str()
            .unwrap(),
        "--out",
        out.to_str().unwrap(),
        "--fail-on-ungrounded",
    ]);

    assert_eq!(output.status.code(), Some(1));
    assert_eq!(output.stdout, b"");
    assert_eq!(output.stderr, b"");
    let report = json_file(out);
    assert_eq!(report["fingerprint_stale"], true);
    assert_eq!(report["all_evidence_grounded"], false);
    assert_eq!(report["checks"][0]["status"], "stale");
    assert_eq!(report["checks"][0]["reason"], "stale_fingerprint");
}

#[test]
fn fail_on_ungrounded_exits_one_with_stdout_report_for_capability_blocked_source() {
    let root = repo_root();
    let output = run_ethos(&[
        "verify",
        root.join("examples/verify/opendataloader_no_tables.json")
            .to_str()
            .unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        root.join("examples/verify/opendataloader_table_cell_citations.json")
            .to_str()
            .unwrap(),
        "--fail-on-ungrounded",
    ]);

    assert_eq!(output.status.code(), Some(1));
    assert_eq!(output.stderr, b"");
    let report: Value = serde_json::from_slice(&output.stdout).expect("stdout is JSON");
    assert_eq!(report["all_evidence_grounded"], false);
    assert_eq!(report["checks"][0]["status"], "capability_blocked");
    assert_eq!(report["checks"][0]["reason"], "missing_table_capability");
    assert!(report["capability_limits"]
        .as_array()
        .unwrap()
        .iter()
        .any(|limit| limit == "missing_tables"));
}

#[test]
fn summary_format_reports_reason_before_fail_on_ungrounded_exit() {
    let root = repo_root();
    let output = run_ethos(&[
        "verify",
        root.join("examples/verify/opendataloader_no_tables.json")
            .to_str()
            .unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        root.join("examples/verify/opendataloader_table_cell_citations.json")
            .to_str()
            .unwrap(),
        "--format",
        "summary",
        "--fail-on-ungrounded",
    ]);

    assert_eq!(output.status.code(), Some(1));
    assert_eq!(output.stderr, b"");
    assert!(
        serde_json::from_slice::<Value>(&output.stdout).is_err(),
        "summary output must not be JSON"
    );
    let summary = String::from_utf8(output.stdout).expect("summary output is UTF-8");
    assert!(summary.contains("ethos verify summary\n"));
    assert!(summary.contains(
        "verification_config_sha256: 4bb224166a04a25fed2dd3ecdb9638ddcc5b398658532b73f1c0547e4983d0b0\n"
    ));
    assert!(summary.contains("all_evidence_grounded: false\n"));
    assert!(summary.contains(
        "grounding_capabilities: spans=false,char_offsets=false,tables=false,fingerprint=false,coordinate_origin=unknown,crop_support=false\n"
    ));
    assert!(summary.contains("checks_capability_blocked: 1\n"));
    assert!(summary.contains("capability_limits: missing_fingerprint,missing_spans,missing_char_offsets,missing_tables,unknown_coordinate_origin\n"));
    assert!(summary.contains("- v0001 status=capability_blocked reason=missing_table_capability kind=table_cell locator=table_id:odl-t1;cell:1,1 match_method=none\n"));
    assert!(summary
        .contains("  diagnostic: table_cell lookup requires a source with table capability\n"));
}

#[test]
fn summary_format_reports_no_non_grounded_checks_for_grounded_input() {
    let root = repo_root();
    let output = run_ethos(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_grounded_citations.json")
            .to_str()
            .unwrap(),
        "--format",
        "summary",
    ]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(output.stderr, b"");
    let summary = String::from_utf8(output.stdout).expect("summary output is UTF-8");
    assert!(summary.contains(
        "verification_config_sha256: 4bb224166a04a25fed2dd3ecdb9638ddcc5b398658532b73f1c0547e4983d0b0\n"
    ));
    assert!(summary.contains("all_evidence_grounded: true\n"));
    assert!(summary.contains(
        "grounding_capabilities: spans=true,char_offsets=true,tables=true,fingerprint=true,coordinate_origin=top-left,crop_support=false\n"
    ));
    assert!(summary.contains("checks_grounded: 3\n"));
    assert!(summary.contains("capability_limits: none\n"));
    assert!(summary.contains("warnings: none\n"));
    assert!(summary.contains("non_grounded_checks:\n- none\n"));
    assert!(!summary.contains("  diagnostic:"));
}

#[test]
fn native_verify_crop_dir_writes_deterministic_crop_descriptors() {
    let root = repo_root();
    let out = temp_output("native-crop-report");
    let crop_dir = tempfile::tempdir().expect("temp crop dir");
    let output = run_ethos(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_grounded_citations.json")
            .to_str()
            .unwrap(),
        "--crop-dir",
        crop_dir.path().to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(output.stdout, b"");
    assert_eq!(output.stderr, b"");

    let report = json_file(&out);
    assert_eq!(report["grounding"]["capabilities"]["crop_support"], true);
    assert_eq!(report["capability_limits"], serde_json::json!([]));

    let first_evidence = &report["checks"][0]["evidence"];
    let crop_ref = first_evidence["crop_ref"].as_str().unwrap();
    assert!(crop_ref.starts_with("crop-"));
    assert!(crop_ref.ends_with(".json"));

    let descriptor_path = crop_dir.path().join(crop_ref);
    let descriptor = json_file(&descriptor_path);
    let expected_descriptor = json_file(root.join("schemas/examples/crop-descriptor.example.json"));
    assert_eq!(descriptor, expected_descriptor);
    assert_eq!(descriptor["artifact_type"], "ethos.crop_descriptor.v1");
    assert_eq!(descriptor["schema_version"], "1.0.0");
    assert_eq!(descriptor["rendering_status"], "descriptor_only");
    assert_eq!(descriptor["crop_ref"], crop_ref);
    assert_eq!(
        descriptor["document_fingerprint"],
        report["document_fingerprint"]
    );
    assert_eq!(descriptor["page"], first_evidence["page"]);
    assert_eq!(descriptor["bbox"], first_evidence["bbox"]);
    assert_eq!(descriptor["check_ids"], serde_json::json!(["v0001"]));
    assert_eq!(descriptor["text_sha256"].as_str().unwrap().len(), 64);

    let crop_files = std::fs::read_dir(crop_dir.path())
        .unwrap()
        .map(|entry| entry.unwrap().path())
        .filter(|path| path.extension().and_then(|ext| ext.to_str()) == Some("json"))
        .count();
    assert_eq!(crop_files, 3);
    assert!(std::fs::read(&descriptor_path).unwrap().ends_with(b"\n"));
}

#[test]
fn crop_dir_is_native_ethos_only_for_alpha() {
    let root = repo_root();
    let crop_dir = tempfile::tempdir().expect("temp crop dir");
    let output = run_ethos(&[
        "verify",
        root.join("fixtures/foreign/opendataloader/real/opendataloader-output.json")
            .to_str()
            .unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        root.join("fixtures/foreign/opendataloader/real/citations.json")
            .to_str()
            .unwrap(),
        "--crop-dir",
        crop_dir.path().to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("--crop-dir is currently supported only for native Ethos document grounding"));
}

#[test]
fn crop_source_pdf_requires_crop_dir() {
    let root = repo_root();
    let output = run_ethos(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_grounded_citations.json")
            .to_str()
            .unwrap(),
        "--crop-source-pdf",
        root.join("fixtures/synthetic/simple-text/document.pdf")
            .to_str()
            .unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("--crop-source-pdf requires --crop-dir")
    );
}

#[test]
fn crop_source_pdf_rejects_source_fingerprint_mismatch() {
    let root = repo_root();
    let crop_dir = tempfile::tempdir().expect("temp crop dir");
    let output = run_ethos(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_grounded_citations.json")
            .to_str()
            .unwrap(),
        "--crop-dir",
        crop_dir.path().to_str().unwrap(),
        "--crop-source-pdf",
        root.join("fixtures/synthetic/simple-text/document.pdf")
            .to_str()
            .unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("crop source PDF fingerprint does not match document source fingerprint"));
    assert_eq!(std::fs::read_dir(crop_dir.path()).unwrap().count(), 0);
}

#[test]
fn crop_source_pdf_writes_rendered_crop_artifacts_when_pdfium_is_configured() {
    if !pdfium_configured() {
        return;
    }

    let root = repo_root();
    let source_pdf = root.join("fixtures/synthetic/simple-text/document.pdf");
    let doc_path = temp_output("simple-text-doc");
    let parse = run_ethos(&[
        "doc",
        "parse",
        source_pdf.to_str().unwrap(),
        "--out",
        doc_path.to_str().unwrap(),
    ]);
    assert_eq!(parse.status.code(), Some(0));
    assert_eq!(parse.stdout, b"");
    assert_eq!(parse.stderr, b"");

    let doc = json_file(&doc_path);
    let citations = serde_json::json!({
        "document_fingerprint": doc["fingerprint"],
        "claims": [
            {
                "kind": "quote",
                "text": "Hello",
                "citation": {
                    "element_id": "e000001"
                }
            }
        ]
    });
    let citations = temp_json(
        "simple-text-citation",
        &serde_json::to_string(&citations).expect("citations serialize"),
    );
    let out = temp_output("simple-text-rendered-crop-report");
    let crop_dir = tempfile::tempdir().expect("temp crop dir");

    let output = run_ethos(&[
        "verify",
        doc_path.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
        "--crop-dir",
        crop_dir.path().to_str().unwrap(),
        "--crop-source-pdf",
        source_pdf.to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(output.stdout, b"");
    assert_eq!(output.stderr, b"");

    let report = json_file(&out);
    assert_eq!(report["all_evidence_grounded"], true);
    let crop_ref = report["checks"][0]["evidence"]["crop_ref"]
        .as_str()
        .unwrap();
    let descriptor = json_file(crop_dir.path().join(crop_ref));
    assert_eq!(descriptor["rendering_status"], "rendered");
    assert_eq!(descriptor["rendered_format"], "png");
    let source_bytes = std::fs::read(&source_pdf).expect("source PDF fixture is readable");
    assert_eq!(
        descriptor["source_pdf_fingerprint"],
        source_fingerprint(&source_bytes)
    );
    assert_eq!(
        descriptor["document_fingerprint"],
        report["document_fingerprint"]
    );
    assert_eq!(descriptor["check_ids"], serde_json::json!(["v0001"]));
    assert!(descriptor["rendered_width_px"].as_u64().unwrap() > 0);
    assert!(descriptor["rendered_height_px"].as_u64().unwrap() > 0);

    let rendered_ref = descriptor["rendered_ref"].as_str().unwrap();
    assert!(rendered_ref.starts_with("crop-"));
    assert!(rendered_ref.ends_with(".png"));
    let png = std::fs::read(crop_dir.path().join(rendered_ref)).unwrap();
    assert!(png.starts_with(b"\x89PNG\r\n\x1a\n"));
    assert_eq!(
        descriptor["rendered_sha256"],
        ethos_core::c14n::sha256_hex_bytes(&png)
    );
    assert_eq!(std::fs::read_dir(crop_dir.path()).unwrap().count(), 2);
}

#[test]
fn fail_on_ungrounded_keeps_invalid_input_on_usage_exit_code() {
    let root = repo_root();
    let citations = temp_json("empty-citations", "[]");
    let output = run_ethos(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        citations.to_str().unwrap(),
        "--fail-on-ungrounded",
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("citations file must contain at least one claim"));
}

#[test]
fn verify_citations_contract_is_not_a_cli_alias() {
    for subcommand in ["verify-citations", "verify_citations"] {
        let output = run_ethos(&[subcommand]);

        assert_eq!(output.status.code(), Some(2), "case {subcommand}");
        assert_eq!(output.stdout, b"", "case {subcommand}");
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(
            stderr.contains("unrecognized subcommand") && stderr.contains(subcommand),
            "case {subcommand} stderr:\n{stderr}"
        );
    }
}

#[test]
fn malformed_native_document_is_usage_error() {
    let root = repo_root();
    let doc = temp_json("malformed-native-document", "{}");
    let output = run_ethos(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        root.join("examples/verify/native_citations.json")
            .to_str()
            .unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("input is not a canonical ethos document"));
    assert!(stderr.contains("missing field `schema_version`"));
}

#[test]
fn wrong_hash_native_document_keeps_integrity_signal() {
    let mut doc = json_file(document_example());
    doc["fingerprint"] = Value::String(format!("sha256:{}", "0".repeat(64)));
    let doc = temp_json(
        "wrong-hash-native-document",
        &serde_json::to_string(&doc).unwrap(),
    );
    let output = run_ethos(&["fingerprint", doc.to_str().unwrap()]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("input document failed integrity check"));
    assert!(stderr.contains("fingerprint mismatch"));
}

#[test]
fn native_ethos_verify_produces_non_empty_checks() {
    let doc = document_example();
    let root = repo_root();
    let citations = root.join("examples/verify/native_citations.json");
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["grounding"]["parser"]["name"], "ethos");
    assert_eq!(report["fingerprint_stale"], false);
    assert_eq!(report["checks"].as_array().unwrap().len(), 3);
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(
        report["checks"][0]["match_method"],
        "normalized_text_contains"
    );
    assert_eq!(report["checks"][1]["status"], "grounded");
    assert_eq!(report["checks"][1]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][2]["status"], "mismatch");
    assert_eq!(report["checks"][2]["reason"], "text_mismatch");
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn native_verify_grounds_split_quote_across_adjacent_elements() {
    let (doc, fingerprint) = temp_split_quote_document();
    let citations = serde_json::json!({
        "document_fingerprint": fingerprint,
        "claims": [
            {
                "kind": "quote",
                "text": "The alpha trust loop verifies grounded evidence",
                "citation": {
                    "element_id": "split-b"
                }
            }
        ]
    });
    let citations = temp_json(
        "split-quote-citations",
        &serde_json::to_string(&citations).unwrap(),
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["all_evidence_grounded"], true);
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(
        report["checks"][0]["match_method"],
        "normalized_text_contains"
    );
    assert_eq!(
        report["checks"][0]["evidence"]["text"],
        "The alpha trust loop verifies grounded evidence"
    );
    assert_eq!(
        report["checks"][0]["evidence"]["bbox"],
        serde_json::json!([100, 100, 700, 200])
    );
}

#[test]
fn opendataloader_verify_adapter_produces_capability_aware_report() {
    let grounding = odl_example();
    let root = repo_root();
    let citations = root.join("examples/verify/answer_citations.json");
    let report = parse_success(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(
        report["grounding"]["parser"]["adapter"],
        "opendataloader-json"
    );
    assert_eq!(
        report["grounding"]["capabilities"]["coordinate_origin"],
        "unknown"
    );
    assert_eq!(
        report["warnings"],
        serde_json::json!(["capability_limited"])
    );
    assert_eq!(
        report["capability_limits"],
        serde_json::json!([
            "missing_fingerprint",
            "missing_spans",
            "missing_char_offsets",
            "unknown_coordinate_origin"
        ])
    );
    assert_eq!(report["checks"].as_array().unwrap().len(), 3);
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(
        report["checks"][0]["match_method"],
        "normalized_text_contains"
    );
    assert_eq!(report["checks"][1]["status"], "grounded");
    assert_eq!(report["checks"][1]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][1]["evidence"]["text"], "$12.4M");
    assert_eq!(report["checks"][2]["status"], "mismatch");
    assert_eq!(report["checks"][2]["reason"], "text_mismatch");
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn opendataloader_adapter_errors_are_usage_errors() {
    let grounding = temp_json(
        "bad-odl-grounding",
        r#"{
          "tool": {
            "name": "opendataloader-pdf",
            "version": "0.0.0-synthetic"
          },
          "pages": [
            {
              "number": 1,
              "width": 612.0,
              "height": 792.0
            }
          ],
          "elements": [
            {
              "id": "bad-ref",
              "page": 2,
              "bbox": [72.0, 101.0, 540.0, 115.0],
              "type": "Paragraph",
              "text": "Revenue grew to $12.4M in Q3 2025."
            }
          ]
        }"#,
    );
    let citations = repo_root().join("examples/verify/answer_citations.json");
    let output = run_ethos(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("opendataloader-json adapter: element.page references unknown page"));
}

#[test]
fn stale_fingerprint_is_report_level_failure() {
    let doc = document_example();
    let citations = temp_json(
        "stale-citations",
        r#"{
          "document_fingerprint": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
          "claims": [
            {
              "kind": "presence",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["fingerprint_stale"], true);
    assert_eq!(report["checks"][0]["status"], "stale");
    assert_eq!(report["checks"][0]["reason"], "stale_fingerprint");
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn malformed_citation_fingerprint_is_usage_error() {
    let doc = document_example();
    let cases = [
        (
            "fingerprint-missing-prefix",
            "b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
        ),
        (
            "fingerprint-uppercase",
            "sha256:579DBF857DB19649463CD6716A6F7C5F43C44DD9A5E798E47F25760F0FFAAE02",
        ),
        (
            "fingerprint-short",
            "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae0",
        ),
        (
            "fingerprint-nonhex",
            "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae0z",
        ),
    ];

    for (name, fingerprint) in cases {
        let citations = temp_json(
            name,
            &format!(
                r#"{{
                  "document_fingerprint": "{fingerprint}",
                  "claims": [
                    {{
                      "kind": "presence",
                      "citation": {{
                        "element_id": "e000002"
                      }}
                    }}
                  ]
                }}"#
            ),
        );
        let output = run_ethos(&[
            "verify",
            doc.to_str().unwrap(),
            "--citations",
            citations.to_str().unwrap(),
        ]);

        assert_eq!(output.status.code(), Some(2), "case {name}");
        assert!(output.stdout.is_empty(), "case {name}");
        assert!(
            String::from_utf8_lossy(&output.stderr)
                .contains("citations document_fingerprint must be sha256:<64 lowercase hex chars>"),
            "case {name} stderr:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn invalid_citation_shape_is_usage_error() {
    let doc = document_example();
    let citations = temp_json(
        "invalid-citations",
        r#"{
          "claims": [
            {
              "kind": "presence",
              "citation": {}
            }
          ]
        }"#,
    );
    let output = run_ethos(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("claim 1 citation must contain at least one locator"));
}

#[test]
fn incomplete_table_cell_locator_is_usage_error() {
    let doc = document_example();
    let cases = [
        (
            "table-id-without-cell",
            r#"{
              "claims": [
                {
                  "kind": "table_cell",
                  "text": "$12.4M",
                  "citation": {
                    "table_id": "t0001"
                  }
                }
              ]
            }"#,
            "claim 1 citation table_id and cell must be provided together",
        ),
        (
            "cell-without-table-id",
            r#"{
              "claims": [
                {
                  "kind": "table_cell",
                  "text": "$12.4M",
                  "citation": {
                    "cell": {
                      "row": 1,
                      "col": 1
                    }
                  }
                }
              ]
            }"#,
            "claim 1 citation table_id and cell must be provided together",
        ),
        (
            "table-cell-kind-without-table-cell-locator",
            r#"{
              "claims": [
                {
                  "kind": "table_cell",
                  "text": "$12.4M",
                  "citation": {
                    "element_id": "e000002"
                  }
                }
              ]
            }"#,
            "claim 1 table_cell citation must include table_id and cell",
        ),
    ];

    for (name, json, expected) in cases {
        let citations = temp_json(name, json);
        let output = run_ethos(&[
            "verify",
            doc.to_str().unwrap(),
            "--citations",
            citations.to_str().unwrap(),
        ]);

        assert_eq!(output.status.code(), Some(2), "case {name}");
        assert!(output.stdout.is_empty(), "case {name}");
        assert!(
            String::from_utf8_lossy(&output.stderr).contains(expected),
            "case {name} stderr:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn unusable_bbox_locator_is_usage_error() {
    let doc = document_example();
    let cases = [
        (
            "bbox-without-page",
            r#"{
              "claims": [
                {
                  "kind": "presence",
                  "citation": {
                    "bbox": [7300, 10200, 8000, 11000]
                  }
                }
              ]
            }"#,
            "claim 1 citation bbox requires page unless another target locator is present",
        ),
        (
            "zero-width-bbox",
            r#"{
              "claims": [
                {
                  "kind": "presence",
                  "citation": {
                    "page": "p0001",
                    "bbox": [7300, 10200, 7300, 11000]
                  }
                }
              ]
            }"#,
            "claim 1 citation bbox must have positive area",
        ),
    ];

    for (name, json, expected) in cases {
        let citations = temp_json(name, json);
        let output = run_ethos(&[
            "verify",
            doc.to_str().unwrap(),
            "--citations",
            citations.to_str().unwrap(),
        ]);

        assert_eq!(output.status.code(), Some(2), "case {name}");
        assert!(output.stdout.is_empty(), "case {name}");
        assert!(
            String::from_utf8_lossy(&output.stderr).contains(expected),
            "case {name} stderr:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn unknown_citation_fields_are_usage_errors() {
    let doc = document_example();
    let cases = [
        (
            "unknown-citation-envelope-field",
            r#"{
              "claims": [
                {
                  "kind": "presence",
                  "citation": {
                    "element_id": "e000002"
                  }
                }
              ],
              "confidence": 0.99
            }"#,
        ),
        (
            "unknown-claim-field",
            r#"{
              "claims": [
                {
                  "kind": "presence",
                  "citation": {
                    "element_id": "e000002"
                  },
                  "confidence": 0.99
                }
              ]
            }"#,
        ),
        (
            "unknown-citation-field",
            r#"{
              "claims": [
                {
                  "kind": "presence",
                  "citation": {
                    "element_id": "e000002",
                    "confidence": 0.99
                  }
                }
              ]
            }"#,
        ),
        (
            "unknown-cell-field",
            r#"{
              "claims": [
                {
                  "kind": "table_cell",
                  "text": "$12.4M",
                  "citation": {
                    "table_id": "t0001",
                    "cell": {
                      "row": 1,
                      "col": 1,
                      "confidence": 0.99
                    }
                  }
                }
              ]
            }"#,
        ),
    ];

    for (name, json) in cases {
        let citations = temp_json(name, json);
        let output = run_ethos(&[
            "verify",
            doc.to_str().unwrap(),
            "--citations",
            citations.to_str().unwrap(),
        ]);

        assert_eq!(output.status.code(), Some(2), "case {name}");
        assert!(output.stdout.is_empty(), "case {name}");
        assert!(
            String::from_utf8_lossy(&output.stderr)
                .contains("citations file does not match the alpha citation input shape"),
            "case {name} stderr:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn bare_array_citation_input_works() {
    let doc = document_example();
    let citations = temp_json(
        "bare-array-citations",
        r#"[
          {
            "kind": "presence",
            "citation": {
              "element_id": "e000002"
            }
          }
        ]"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"].as_array().unwrap().len(), 1);
    assert_eq!(report["checks"][0]["status"], "stale");
    assert_eq!(
        report["checks"][0]["reason"],
        "missing_citation_fingerprint"
    );
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn envelope_without_fingerprint_blocks_when_source_has_fingerprint() {
    let doc = document_example();
    let citations = temp_json(
        "no-fingerprint-envelope-citations",
        r#"{
          "claims": [
            {
              "kind": "presence",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"].as_array().unwrap().len(), 1);
    assert_eq!(report["checks"][0]["status"], "stale");
    assert_eq!(
        report["checks"][0]["reason"],
        "missing_citation_fingerprint"
    );
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn unknown_config_fields_are_usage_errors() {
    let doc = document_example();
    let citations = temp_json(
        "presence-citations",
        r#"{
          "claims": [
            {
              "kind": "presence",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let cases = [
        (
            "unknown-config-top-level-field",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "unknown-field",
              "claim_kinds": ["quote", "presence"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 256
              },
              "evidence": {
                "include_text": true,
                "include_crops": false
              },
              "fuzzy": true
            }"#,
        ),
        (
            "unknown-config-matching-field",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "unknown-field",
              "claim_kinds": ["quote", "presence"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50,
                "fuzzy": true
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 256
              },
              "evidence": {
                "include_text": true,
                "include_crops": false
              }
            }"#,
        ),
        (
            "unknown-config-staleness-field",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "unknown-field",
              "claim_kinds": ["quote", "presence"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50
              },
              "staleness": {
                "require_fingerprint_match": true,
                "mode": "strict"
              },
              "limits": {
                "max_checks": 256
              },
              "evidence": {
                "include_text": true,
                "include_crops": false
              }
            }"#,
        ),
        (
            "unknown-config-limits-field",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "unknown-field",
              "claim_kinds": ["quote", "presence"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 256,
                "max_parse_ms": 1000
              },
              "evidence": {
                "include_text": true,
                "include_crops": false
              }
            }"#,
        ),
        (
            "unknown-config-evidence-field",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "unknown-field",
              "claim_kinds": ["quote", "presence"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 256
              },
              "evidence": {
                "include_text": true,
                "include_crops": false,
                "crop_format": "png"
              }
            }"#,
        ),
    ];

    for (name, json) in cases {
        let config = temp_json(name, json);
        let output = run_ethos(&[
            "verify",
            doc.to_str().unwrap(),
            "--citations",
            citations.to_str().unwrap(),
            "--config",
            config.to_str().unwrap(),
        ]);

        assert_eq!(output.status.code(), Some(2), "case {name}");
        assert!(output.stdout.is_empty(), "case {name}");
        assert!(
            String::from_utf8_lossy(&output.stderr)
                .contains("verification config does not match the schema"),
            "case {name} stderr:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn invalid_config_constraints_are_usage_errors() {
    let doc = document_example();
    let citations = temp_json(
        "presence-citations",
        r#"{
          "claims": [
            {
              "kind": "presence",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );

    let cases = [
        (
            "duplicate-claim-kind-config",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "duplicate-kind",
              "claim_kinds": ["quote", "quote"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 256
              }
            }"#,
            "verification config claim_kinds must be unique",
        ),
        (
            "other-claim-kind-config",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "other-kind",
              "claim_kinds": ["other"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 256
              }
            }"#,
            "verification config claim_kinds must include only quote, value, presence, and table_cell",
        ),
        (
            "region-claim-kind-config",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "region-kind",
              "claim_kinds": ["region"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 256
              }
            }"#,
            "verification config claim_kinds must include only quote, value, presence, and table_cell",
        ),
        (
            "negative-bbox-tolerance-config",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "negative-tolerance",
              "claim_kinds": ["quote"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": -1
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 256
              }
            }"#,
            "verification config bbox_containment_tolerance_q must be non-negative",
        ),
        (
            "zero-max-checks-config",
            r#"{
              "schema_version": "1.0.0",
              "config_version": "zero-max-checks",
              "claim_kinds": ["quote"],
              "matching": {
                "text_normalization": "collapse_whitespace",
                "case_sensitive": true,
                "bbox_containment_tolerance_q": 50
              },
              "staleness": {
                "require_fingerprint_match": true
              },
              "limits": {
                "max_checks": 0
              }
            }"#,
            "verification config max_checks must be at least 1",
        ),
    ];

    for (name, config_json, expected) in cases {
        let config = temp_json(name, config_json);
        let output = run_ethos(&[
            "verify",
            doc.to_str().unwrap(),
            "--citations",
            citations.to_str().unwrap(),
            "--config",
            config.to_str().unwrap(),
        ]);

        assert_eq!(output.status.code(), Some(2), "case {name}");
        assert!(output.stdout.is_empty(), "case {name}");
        assert!(
            String::from_utf8_lossy(&output.stderr).contains(expected),
            "case {name} stderr:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn max_checks_overflow_is_usage_error() {
    let doc = document_example();
    let config = temp_json(
        "max-checks-one-config",
        r#"{
          "schema_version": "1.0.0",
          "config_version": "max-checks-one",
          "claim_kinds": ["quote", "presence"],
          "matching": {
            "text_normalization": "collapse_whitespace",
            "case_sensitive": true,
            "bbox_containment_tolerance_q": 50
          },
          "staleness": {
            "require_fingerprint_match": true
          },
          "limits": {
            "max_checks": 1
          },
          "evidence": {
            "include_text": true,
            "include_crops": false
          }
        }"#,
    );
    let citations = repo_root().join("examples/verify/native_citations.json");
    let output = run_ethos(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
        "--config",
        config.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert!(String::from_utf8_lossy(&output.stderr).contains("citations file exceeds max_checks"));
}

#[test]
fn value_claim_verifies_against_native_ethos_text() {
    let doc = document_example();
    let citations = temp_json(
        "value-citations",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "value",
              "text": "Revenue grew to $12.4M in Q3 2025, driven by enterprise expansion.",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][0]["match_method"], "normalized_text");
    assert_eq!(report["unsupported_claim_kinds"], serde_json::json!([]));
    assert_eq!(report["all_evidence_grounded"], true);
}

#[test]
fn value_substrings_do_not_ground_against_native_ethos_text() {
    let doc = document_example();
    let citations = temp_json(
        "value-substring-citations",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "value",
              "text": "1",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "mismatch");
    assert_eq!(report["checks"][0]["match_method"], "normalized_text");
    assert_eq!(report["checks"][0]["reason"], "text_mismatch");
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn table_cell_claim_verifies_against_native_ethos_table() {
    let doc = document_example();
    let citations = temp_json(
        "table-cell-citations",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "table_cell",
              "text": "$12.4M",
              "citation": {
                "table_id": "t0001",
                "cell": {
                  "row": 1,
                  "col": 1
                }
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][0]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][0]["evidence"]["text"], "$12.4M");
    assert_eq!(report["all_evidence_grounded"], true);
}

#[test]
fn parsed_table_candidate_fixture_verifies_table_cell_citations() {
    if !pdfium_configured() {
        eprintln!("skipping table candidate verify fixture test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = table_regular_grid_fixture();
    let parsed = parse_success(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);
    assert_eq!(parsed["payload"]["tables"].as_array().unwrap().len(), 1);
    assert_eq!(parsed["payload"]["tables"][0]["id"], "t0001");
    assert_eq!(
        parsed["payload"]["tables"][0]["cells"]
            .as_array()
            .unwrap()
            .len(),
        6
    );
    let fingerprint = parsed["fingerprint"]
        .as_str()
        .expect("parsed fixture document has a fingerprint");
    let doc = temp_json(
        "table-candidate-fixture-document",
        &serde_json::to_string(&parsed).expect("parsed fixture serializes"),
    );
    let citations = serde_json::json!({
        "document_fingerprint": fingerprint,
        "claims": [
            {
                "kind": "table_cell",
                "text": "10",
                "citation": {
                    "table_id": "t0001",
                    "cell": {
                        "row": 1,
                        "col": 1
                    }
                }
            },
            {
                "kind": "table_cell",
                "text": "99",
                "citation": {
                    "table_id": "t0001",
                    "cell": {
                        "row": 1,
                        "col": 1
                    }
                }
            },
            {
                "kind": "table_cell",
                "text": "12",
                "citation": {
                    "table_id": "t0001",
                    "cell": {
                        "row": 9,
                        "col": 9
                    }
                }
            }
        ]
    });
    let citations = temp_json(
        "table-candidate-fixture-citations",
        &serde_json::to_string(&citations).expect("citations serialize"),
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["grounding"]["parser"]["name"], "ethos");
    assert_eq!(report["fingerprint_stale"], false);
    assert_eq!(report["checks"].as_array().unwrap().len(), 3);
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][0]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][0]["evidence"]["page"], "p0001");
    assert_eq!(report["checks"][0]["evidence"]["text"], "10");
    assert_eq!(
        report["checks"][0]["evidence"]["bbox"],
        serde_json::json!([18131, 8737, 19277, 9613])
    );
    assert_eq!(report["checks"][1]["status"], "mismatch");
    assert_eq!(report["checks"][1]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][1]["reason"], "text_mismatch");
    assert_eq!(report["checks"][2]["status"], "not_found");
    assert_eq!(report["checks"][2]["reason"], "table_cell_not_found");
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn parsed_table_candidate_fixture_writes_table_cell_crop_artifacts() {
    if !pdfium_configured() {
        eprintln!(
            "skipping table candidate crop fixture test: ETHOS_PDFIUM_LIBRARY_PATH is not configured"
        );
        return;
    }

    let source_pdf = table_regular_grid_fixture();
    let parsed = parse_success(&[
        "doc",
        "parse",
        source_pdf.to_str().unwrap(),
        "--format",
        "json",
    ]);
    let fingerprint = parsed["fingerprint"]
        .as_str()
        .expect("parsed fixture document has a fingerprint");
    let doc = temp_json(
        "table-candidate-crop-fixture-document",
        &serde_json::to_string(&parsed).expect("parsed fixture serializes"),
    );
    let citations = serde_json::json!({
        "document_fingerprint": fingerprint,
        "claims": [
            {
                "kind": "table_cell",
                "text": "10",
                "citation": {
                    "table_id": "t0001",
                    "cell": {
                        "row": 1,
                        "col": 1
                    }
                }
            }
        ]
    });
    let citations = temp_json(
        "table-candidate-crop-fixture-citations",
        &serde_json::to_string(&citations).expect("citations serialize"),
    );
    let out = temp_output("table-candidate-crop-fixture-report");
    let crop_dir = tempfile::tempdir().expect("temp crop dir");

    let output = run_ethos(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
        "--crop-dir",
        crop_dir.path().to_str().unwrap(),
        "--crop-source-pdf",
        source_pdf.to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(output.stdout, b"");
    assert_eq!(output.stderr, b"");

    let report = json_file(&out);
    assert_eq!(report["all_evidence_grounded"], true);
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][0]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][0]["evidence"]["page"], "p0001");
    assert_eq!(report["checks"][0]["evidence"]["text"], "10");
    assert_eq!(
        report["checks"][0]["evidence"]["bbox"],
        serde_json::json!([18131, 8737, 19277, 9613])
    );

    let crop_ref = report["checks"][0]["evidence"]["crop_ref"]
        .as_str()
        .unwrap();
    let descriptor = json_file(crop_dir.path().join(crop_ref));
    assert_eq!(descriptor["rendering_status"], "rendered");
    assert_eq!(descriptor["rendered_format"], "png");
    let source_bytes = std::fs::read(&source_pdf).expect("source PDF fixture is readable");
    assert_eq!(
        descriptor["source_pdf_fingerprint"],
        source_fingerprint(&source_bytes)
    );
    assert_eq!(
        descriptor["document_fingerprint"],
        report["document_fingerprint"]
    );
    assert_eq!(descriptor["check_ids"], serde_json::json!(["v0001"]));
    assert!(descriptor["rendered_width_px"].as_u64().unwrap() > 0);
    assert!(descriptor["rendered_height_px"].as_u64().unwrap() > 0);

    let rendered_ref = descriptor["rendered_ref"].as_str().unwrap();
    assert!(rendered_ref.starts_with("crop-"));
    assert!(rendered_ref.ends_with(".png"));
    let png = std::fs::read(crop_dir.path().join(rendered_ref)).unwrap();
    assert!(png.starts_with(b"\x89PNG\r\n\x1a\n"));
    assert_eq!(
        descriptor["rendered_sha256"],
        ethos_core::c14n::sha256_hex_bytes(&png)
    );
    assert_eq!(std::fs::read_dir(crop_dir.path()).unwrap().count(), 2);
}

#[test]
fn table_cell_mismatch_and_missing_cell_fail_gate() {
    let doc = document_example();
    let citations = temp_json(
        "table-cell-negative-citations",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "table_cell",
              "text": "$99M",
              "citation": {
                "table_id": "t0001",
                "cell": {
                  "row": 1,
                  "col": 1
                }
              }
            },
            {
              "kind": "table_cell",
              "text": "$12.4M",
              "citation": {
                "table_id": "t0001",
                "cell": {
                  "row": 9,
                  "col": 9
                }
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "mismatch");
    assert_eq!(report["checks"][0]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][0]["reason"], "text_mismatch");
    assert_eq!(report["checks"][1]["status"], "not_found");
    assert_eq!(report["checks"][1]["reason"], "table_cell_not_found");
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn quote_without_text_is_usage_error() {
    let doc = document_example();
    let citations = temp_json(
        "quote-without-text",
        r#"{
          "claims": [
            {
              "kind": "quote",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let output = run_ethos(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("text must be non-empty for quote, value, and table_cell"));
}

#[test]
fn value_without_text_is_usage_error() {
    let doc = document_example();
    let citations = temp_json(
        "value-without-text",
        r#"{
          "claims": [
            {
              "kind": "value",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let output = run_ethos(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("text must be non-empty for quote, value, and table_cell"));
}

#[test]
fn table_cell_is_capability_blocked_when_tables_are_missing() {
    let grounding = temp_json(
        "odl-no-tables",
        r#"{
          "tool": {
            "name": "opendataloader-pdf",
            "version": "0.0.0-synthetic"
          },
          "pages": [
            {
              "number": 1,
              "width": 612.0,
              "height": 792.0
            }
          ],
          "elements": [
            {
              "id": "odl-e2",
              "page": 1,
              "bbox": [72.0, 101.0, 540.0, 115.0],
              "type": "Paragraph",
              "text": "Revenue grew to $12.4M in Q3 2025."
            }
          ]
        }"#,
    );
    let citations = temp_json(
        "table-cell-no-tables",
        r#"{
          "claims": [
            {
              "kind": "table_cell",
              "text": "$12.4M",
              "citation": {
                "table_id": "t0001",
                "cell": {
                  "row": 1,
                  "col": 1
                }
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "capability_blocked");
    assert_eq!(report["checks"][0]["reason"], "missing_table_capability");
    assert_eq!(report["grounding"]["capabilities"]["tables"], false);
    assert_eq!(
        report["capability_limits"],
        serde_json::json!([
            "missing_fingerprint",
            "missing_spans",
            "missing_char_offsets",
            "missing_tables",
            "unknown_coordinate_origin"
        ])
    );
    assert_eq!(
        report["checks"][0]["warnings"],
        serde_json::json!(["capability_limited"])
    );
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn empty_tables_are_not_found_when_table_capability_is_declared() {
    let grounding = temp_json(
        "odl-empty-tables",
        r#"{
          "tool": {
            "name": "opendataloader-pdf",
            "version": "0.0.0-synthetic"
          },
          "pages": [
            {
              "number": 1,
              "width": 612.0,
              "height": 792.0
            }
          ],
          "elements": [],
          "tables": []
        }"#,
    );
    let citations = temp_json(
        "table-cell-empty-tables",
        r#"{
          "claims": [
            {
              "kind": "table_cell",
              "text": "$12.4M",
              "citation": {
                "table_id": "t0001",
                "cell": {
                  "row": 1,
                  "col": 1
                }
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["grounding"]["capabilities"]["tables"], true);
    assert_eq!(
        report["capability_limits"],
        serde_json::json!([
            "missing_fingerprint",
            "missing_spans",
            "missing_char_offsets",
            "unknown_coordinate_origin"
        ])
    );
    assert_eq!(report["checks"][0]["status"], "not_found");
    assert_eq!(report["checks"][0]["reason"], "table_not_found");
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn real_opendataloader_style_table_cell_claim_grounds() {
    let grounding = temp_json(
        "real-odl-style-table",
        r#"{
          "file name": "table.pdf",
          "number of pages": 1,
          "kids": [
            {
              "type": "table",
              "id": 13,
              "page number": 1,
              "bounding box": [10, 10, 240, 80],
              "rows": [
                {
                  "cells": [
                    {
                      "type": "table_cell",
                      "page number": 1,
                      "bounding box": [20, 20, 110, 50],
                      "content": "Metric"
                    },
                    {
                      "type": "table_cell",
                      "page number": 1,
                      "bounding box": [120, 20, 230, 50],
                      "content": "$12.4M"
                    }
                  ]
                }
              ]
            }
          ]
        }"#,
    );
    let citations = temp_json(
        "real-odl-style-table-cell-citations",
        r#"{
          "claims": [
            {
              "kind": "table_cell",
              "text": "$12.4M",
              "citation": {
                "table_id": "odl-13",
                "cell": {
                  "row": 1,
                  "col": 2
                }
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["grounding"]["capabilities"]["tables"], true);
    assert_eq!(
        report["capability_limits"],
        serde_json::json!([
            "missing_fingerprint",
            "missing_spans",
            "missing_char_offsets",
            "unknown_coordinate_origin"
        ])
    );
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][0]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][0]["evidence"]["page"], "page-1");
    assert_eq!(report["checks"][0]["evidence"]["text"], "$12.4M");
    assert_eq!(
        report["checks"][0]["evidence"]["bbox"],
        serde_json::json!([12000, 2000, 23000, 5000])
    );
    assert_eq!(report["all_evidence_grounded"], true);
}

#[test]
fn real_opendataloader_text_and_child_alias_claim_grounds() {
    let grounding = temp_json(
        "real-odl-style-aliases",
        r#"{
          "file name": "aliases.pdf",
          "number of pages": 1,
          "kids": [
            {
              "type": "section",
              "id": "parent",
              "page number": 1,
              "bounding box": [10, 10, 240, 80],
              "text": "Parent text",
              "children": [
                {
                  "type": "paragraph",
                  "id": "alias-child",
                  "page number": 1,
                  "bounding box": [20, 20, 230, 50],
                  "text": "Child alias grounds"
                }
              ]
            }
          ]
        }"#,
    );
    let citations = temp_json(
        "real-odl-style-alias-citations",
        r#"{
          "claims": [
            {
              "kind": "quote",
              "text": "Child alias grounds",
              "citation": {
                "element_id": "odl-alias-child"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(
        report["checks"][0]["match_method"],
        "normalized_text_contains"
    );
    assert_eq!(report["checks"][0]["evidence"]["page"], "page-1");
    assert_eq!(
        report["checks"][0]["evidence"]["text"],
        "Child alias grounds"
    );
    assert_eq!(
        report["checks"][0]["evidence"]["bbox"],
        serde_json::json!([2000, 2000, 23000, 5000])
    );
    assert_eq!(
        report["capability_limits"],
        serde_json::json!([
            "missing_fingerprint",
            "missing_spans",
            "missing_char_offsets",
            "missing_tables",
            "unknown_coordinate_origin"
        ])
    );
    assert_eq!(report["all_evidence_grounded"], true);
}

#[test]
fn foreign_source_without_fingerprint_blocks_fingerprint_pinned_citations() {
    let grounding = odl_example();
    let citations = temp_json(
        "odl-fingerprint-pinned-citations",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "presence",
              "citation": {
                "element_id": "odl-e2"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["fingerprint_stale"], false);
    assert_eq!(
        report["capability_limits"],
        serde_json::json!([
            "missing_fingerprint",
            "missing_spans",
            "missing_char_offsets",
            "unknown_coordinate_origin"
        ])
    );
    assert_eq!(report["checks"][0]["status"], "capability_blocked");
    assert_eq!(report["checks"][0]["reason"], "missing_source_fingerprint");
    assert_eq!(
        report["checks"][0]["warnings"],
        serde_json::json!(["capability_limited"])
    );
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn config_excluded_value_claim_is_unsupported() {
    let doc = document_example();
    let config = temp_json(
        "quote-presence-only-config",
        r#"{
          "schema_version": "1.0.0",
          "config_version": "quote-presence-only",
          "claim_kinds": ["quote", "presence"],
          "matching": {
            "text_normalization": "collapse_whitespace",
            "case_sensitive": true,
            "bbox_containment_tolerance_q": 50
          },
          "staleness": {
            "require_fingerprint_match": true
          },
          "limits": {
            "max_checks": 256
          },
          "evidence": {
            "include_text": true,
            "include_crops": false
          }
        }"#,
    );
    let citations = temp_json(
        "excluded-value",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "value",
              "text": "$12.4M",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
        "--config",
        config.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "unsupported_claim_kind");
    assert_eq!(report["checks"][0]["reason"], "unsupported_claim_kind");
    assert_eq!(report["checks"][0]["match_method"], "none");
    assert_eq!(report["checks"][0]["semantic_unverified"], false);
    assert!(report["checks"][0].get("evidence").is_none());
    assert_eq!(
        report["unsupported_claim_kinds"],
        serde_json::json!(["value"])
    );
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn page_only_presence_works() {
    let doc = document_example();
    let citations = temp_json(
        "page-only-presence",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "presence",
              "citation": {
                "page": "p0001"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][0]["match_method"], "presence_only");
    assert_eq!(
        report["checks"][0]["evidence"]["bbox"],
        serde_json::json!([0, 0, 61200, 79200])
    );
}

#[test]
fn bbox_presence_works_when_coordinate_origin_is_known() {
    let doc = document_example();
    let citations = temp_json(
        "bbox-known-origin",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "presence",
              "citation": {
                "page": "p0001",
                "bbox": [7300, 10200, 8000, 11000]
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(
        report["checks"][0]["evidence"]["text"],
        "Revenue grew to $12.4M in Q3 2025, driven by enterprise expansion."
    );
}

#[test]
fn bbox_presence_is_capability_blocked_when_coordinate_origin_is_unknown() {
    let grounding = odl_example();
    let citations = temp_json(
        "bbox-unknown-origin",
        r#"{
          "claims": [
            {
              "kind": "presence",
              "citation": {
                "page": "page-1",
                "bbox": [7300, 10200, 8000, 11000]
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        grounding.to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--citations",
        citations.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "capability_blocked");
    assert_eq!(report["checks"][0]["reason"], "unknown_coordinate_origin");
    assert_eq!(
        report["capability_limits"],
        serde_json::json!([
            "missing_fingerprint",
            "missing_spans",
            "missing_char_offsets",
            "unknown_coordinate_origin"
        ])
    );
    assert_eq!(
        report["checks"][0]["warnings"],
        serde_json::json!(["capability_limited"])
    );
    assert_eq!(report["all_evidence_grounded"], false);
}

#[test]
fn case_insensitive_config_allows_literal_case_difference() {
    let doc = document_example();
    let config = temp_json(
        "case-insensitive-config",
        r#"{
          "schema_version": "1.0.0",
          "config_version": "case-insensitive",
          "claim_kinds": ["quote", "presence"],
          "matching": {
            "text_normalization": "collapse_whitespace",
            "case_sensitive": false,
            "bbox_containment_tolerance_q": 50
          },
          "staleness": {
            "require_fingerprint_match": true
          },
          "limits": {
            "max_checks": 256
          },
          "evidence": {
            "include_text": true,
            "include_crops": false
          }
        }"#,
    );
    let citations = temp_json(
        "case-insensitive-citations",
        r#"{
          "document_fingerprint": "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
          "claims": [
            {
              "kind": "quote",
              "text": "revenue grew to $12.4m in q3 2025",
              "citation": {
                "element_id": "e000002"
              }
            }
          ]
        }"#,
    );
    let report = parse_success(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
        "--config",
        config.to_str().unwrap(),
    ]);

    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(
        report["checks"][0]["match_method"],
        "normalized_text_contains"
    );
    assert_eq!(report["all_evidence_grounded"], true);
}
