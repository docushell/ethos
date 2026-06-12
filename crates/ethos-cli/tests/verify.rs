use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::{SystemTime, UNIX_EPOCH};

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

fn document_example() -> PathBuf {
    repo_root().join("schemas/examples/document.example.json")
}

fn odl_example() -> PathBuf {
    repo_root().join("examples/verify/opendataloader.json")
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
    assert_eq!(report["checks"][0]["match_method"], "normalized_text");
    assert_eq!(report["checks"][1]["status"], "grounded");
    assert_eq!(report["checks"][1]["match_method"], "table_cell_lookup");
    assert_eq!(report["checks"][2]["status"], "mismatch");
    assert_eq!(report["all_evidence_grounded"], false);
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
    assert_eq!(report["checks"].as_array().unwrap().len(), 2);
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][1]["status"], "mismatch");
    assert_eq!(report["all_evidence_grounded"], false);
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
    assert_eq!(report["all_evidence_grounded"], false);
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
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["all_evidence_grounded"], true);
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
          "document_fingerprint": "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae02",
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
    ]);

    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][0]["match_method"], "normalized_text");
    assert_eq!(report["unsupported_claim_kinds"], serde_json::json!([]));
    assert_eq!(report["all_evidence_grounded"], true);
}

#[test]
fn table_cell_claim_verifies_against_native_ethos_table() {
    let doc = document_example();
    let citations = temp_json(
        "table-cell-citations",
        r#"{
          "document_fingerprint": "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae02",
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
fn table_cell_mismatch_and_missing_cell_fail_gate() {
    let doc = document_example();
    let citations = temp_json(
        "table-cell-negative-citations",
        r#"{
          "document_fingerprint": "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae02",
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
    assert_eq!(report["checks"][1]["status"], "not_found");
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
    let grounding = odl_example();
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
          "document_fingerprint": "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae02",
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
          "document_fingerprint": "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae02",
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
          "document_fingerprint": "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae02",
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
          "document_fingerprint": "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae02",
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
    assert_eq!(report["all_evidence_grounded"], true);
}
