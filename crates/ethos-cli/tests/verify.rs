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

fn document_example() -> PathBuf {
    repo_root().join("schemas/examples/document.example.json")
}

fn odl_example() -> PathBuf {
    repo_root().join("examples/verify/opendataloader.json")
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
    let root = repo_root();
    let cases: [(&str, Vec<String>, PathBuf); 4] = [
        (
            "native-grounded",
            vec![
                "verify".to_string(),
                root.join("schemas/examples/document.example.json")
                    .display()
                    .to_string(),
                "--citations".to_string(),
                root.join("examples/verify/native_grounded_citations.json")
                    .display()
                    .to_string(),
            ],
            root.join("examples/verify/goldens/native_grounded_report.json"),
        ),
        (
            "opendataloader-grounded",
            vec![
                "verify".to_string(),
                root.join("examples/verify/opendataloader.json")
                    .display()
                    .to_string(),
                "--grounding".to_string(),
                "opendataloader-json".to_string(),
                "--citations".to_string(),
                root.join("examples/verify/opendataloader_grounded_citations.json")
                    .display()
                    .to_string(),
            ],
            root.join("examples/verify/goldens/opendataloader_grounded_report.json"),
        ),
        (
            "native-stale",
            vec![
                "verify".to_string(),
                root.join("schemas/examples/document.example.json")
                    .display()
                    .to_string(),
                "--citations".to_string(),
                root.join("examples/verify/native_stale_citations.json")
                    .display()
                    .to_string(),
            ],
            root.join("examples/verify/goldens/native_stale_report.json"),
        ),
        (
            "opendataloader-capability-limited",
            vec![
                "verify".to_string(),
                root.join("examples/verify/opendataloader_no_tables.json")
                    .display()
                    .to_string(),
                "--grounding".to_string(),
                "opendataloader-json".to_string(),
                "--citations".to_string(),
                root.join("examples/verify/opendataloader_table_cell_citations.json")
                    .display()
                    .to_string(),
            ],
            root.join("examples/verify/goldens/opendataloader_capability_limited_report.json"),
        ),
    ];

    for (name, args, expected_path) in cases {
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
    assert!(report["capability_limits"]
        .as_array()
        .unwrap()
        .iter()
        .any(|limit| limit == "missing_tables"));
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
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["all_evidence_grounded"], true);
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
            "verification config claim_kinds must not include other",
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
    assert_eq!(report["all_evidence_grounded"], false);
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
