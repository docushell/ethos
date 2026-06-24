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

fn opendataloader_example() -> PathBuf {
    repo_root().join("examples/verify/opendataloader.json")
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

fn temp_json(name: &str, value: Value) -> PathBuf {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock after unix epoch")
        .as_nanos();
    let path = std::env::temp_dir().join(format!("ethos-evidence-anchor-{name}-{nanos}.json"));
    std::fs::write(
        &path,
        serde_json::to_string(&value).expect("temp JSON serializes"),
    )
    .expect("temp JSON is writable");
    path
}

fn request(evidence_refs: Value) -> PathBuf {
    temp_json(
        "request",
        serde_json::json!({
            "artifact_type": "ethos.evidence_anchor_request.v1",
            "schema_version": "1.0.0",
            "evidence_refs": evidence_refs
        }),
    )
}

fn request_with_fingerprint(source_fingerprint: &str, evidence_refs: Value) -> PathBuf {
    temp_json(
        "request",
        serde_json::json!({
            "artifact_type": "ethos.evidence_anchor_request.v1",
            "schema_version": "1.0.0",
            "source_fingerprint": source_fingerprint,
            "evidence_refs": evidence_refs
        }),
    )
}

#[test]
fn help_lists_evidence_anchor() {
    let output = run_ethos(&["--help"]);
    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("evidence"), "{stdout}");

    let output = run_ethos(&["evidence", "--help"]);
    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("anchor"), "{stdout}");
}

#[test]
fn missing_evidence_refs_exits_usage() {
    let output = run_ethos(&["evidence", "anchor", document_example().to_str().unwrap()]);
    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
}

#[test]
fn empty_refs_succeeds_with_empty_anchors() {
    let request = request(serde_json::json!([]));
    let report = parse_success(&[
        "evidence",
        "anchor",
        document_example().to_str().unwrap(),
        "--evidence-refs",
        request.to_str().unwrap(),
    ]);
    assert_eq!(report["artifact_type"], "ethos.evidence_anchor_report.v1");
    assert_eq!(report["anchors"], serde_json::json!([]));
    assert_eq!(report["grounding"]["parser"]["adapter"], Value::Null);
}

#[test]
fn native_page_text_bbox_and_table_cell_bind() {
    let request = request_with_fingerprint(
        "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3",
        serde_json::json!([
            {
                "evidence_id": "ev_page",
                "evidence_kind": "page",
                "required_anchor_level": "page",
                "locator": { "page_index": 1 }
            },
            {
                "evidence_id": "ev_text",
                "evidence_kind": "text",
                "required_anchor_level": "text",
                "locator": { "page_index": 1 },
                "expected_text": "Revenue grew to $12.4M in Q3 2025, driven by enterprise expansion.",
                "expected_text_sha256": "sha256:49f675142f930e31d75679b14e23f7c639cb9903029eacb3235c709c14fe4be5",
                "text_normalization_profile": "ethos_collapse_whitespace_v1"
            },
            {
                "evidence_id": "ev_text_bbox",
                "evidence_kind": "text_region",
                "required_anchor_level": "text_bbox",
                "locator": {
                    "page_index": 1,
                    "bbox": [7200, 10100, 54000, 11500],
                    "coordinate_profile": "ethos_quantized_top_left_v1"
                },
                "expected_text": "Revenue grew to $12.4M in Q3 2025"
            },
            {
                "evidence_id": "ev_cell",
                "evidence_kind": "table_cell",
                "required_anchor_level": "table_cell",
                "locator": {
                    "table_id": "t0001",
                    "cell": { "row": 1, "col": 1 }
                },
                "expected_text": "$12.4M"
            }
        ]),
    );
    let report = parse_success(&[
        "evidence",
        "anchor",
        document_example().to_str().unwrap(),
        "--evidence-refs",
        request.to_str().unwrap(),
    ]);
    let anchors = report["anchors"].as_array().unwrap();
    assert_eq!(anchors.len(), 4);
    for anchor in anchors {
        assert_eq!(anchor["anchor_status"], "bound");
    }
    assert_eq!(anchors[0]["achieved_anchor_level"], "page");
    assert_eq!(anchors[1]["achieved_anchor_level"], "text");
    assert_eq!(anchors[2]["achieved_anchor_level"], "text_bbox");
    assert_eq!(anchors[3]["achieved_anchor_level"], "table_cell");
}

#[test]
fn non_bound_outcomes_still_exit_zero() {
    let request = request_with_fingerprint(
        "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        serde_json::json!([
            {
                "evidence_id": "ev_stale",
                "evidence_kind": "text",
                "required_anchor_level": "text",
                "locator": { "page_index": 1 },
                "expected_text": "Revenue"
            },
            {
                "evidence_id": "ev_region",
                "evidence_kind": "region",
                "required_anchor_level": "bbox",
                "locator": {
                    "page_index": 1,
                    "bbox": [1, 2, 3, 4],
                    "coordinate_profile": "ethos_quantized_top_left_v1"
                }
            }
        ]),
    );
    let report = parse_success(&[
        "evidence",
        "anchor",
        document_example().to_str().unwrap(),
        "--evidence-refs",
        request.to_str().unwrap(),
    ]);
    assert_eq!(report["anchors"][0]["anchor_status"], "stale_fingerprint");
    assert_eq!(report["anchors"][0]["checks"]["page"], "not_checked");
    assert_eq!(
        report["anchors"][1]["anchor_status"],
        "unsupported_evidence_kind"
    );
}

#[test]
fn opendataloader_text_binds_and_bbox_is_capability_limited() {
    let request = request(serde_json::json!([
        {
            "evidence_id": "odl_text",
            "evidence_kind": "text",
            "required_anchor_level": "text",
            "locator": { "page_index": 1 },
            "expected_text": "Revenue grew to $12.4M in Q3 2025."
        },
        {
            "evidence_id": "odl_bbox",
            "evidence_kind": "text_region",
            "required_anchor_level": "text_bbox",
            "locator": {
                "page_index": 1,
                "bbox": [72, 101, 540, 115],
                "coordinate_profile": "ethos_quantized_top_left_v1"
            },
            "expected_text": "Revenue grew to $12.4M in Q3 2025."
        },
        {
            "evidence_id": "odl_cell",
            "evidence_kind": "table_cell",
            "required_anchor_level": "table_cell",
            "locator": {
                "table_id": "odl-t1",
                "cell": { "row": 1, "col": 1 }
            },
            "expected_text": "$12.4M"
        }
    ]));
    let report = parse_success(&[
        "evidence",
        "anchor",
        opendataloader_example().to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--evidence-refs",
        request.to_str().unwrap(),
    ]);
    assert_eq!(report["anchors"][0]["anchor_status"], "bound");
    assert_eq!(report["anchors"][1]["anchor_status"], "capability_limited");
    assert_eq!(report["anchors"][1]["achieved_anchor_level"], "text");
    assert_eq!(report["anchors"][2]["anchor_status"], "bound");
}

#[test]
fn usage_errors_are_exit_two() {
    let cases = [
        request(serde_json::json!([
            {
                "evidence_id": "ev",
                "evidence_kind": "text",
                "required_anchor_level": "text",
                "locator": { "page_index": 1 }
            }
        ])),
        request(serde_json::json!([
            {
                "evidence_id": "ev",
                "evidence_kind": "text_region",
                "required_anchor_level": "bbox",
                "locator": { "page_index": 1 }
            }
        ])),
        request(serde_json::json!([
            {
                "evidence_id": "ev",
                "evidence_kind": "text",
                "required_anchor_level": "text",
                "locator": { "page_index": 1 },
                "expected_text": "   "
            }
        ])),
        request(serde_json::json!([
            {
                "evidence_id": "ev",
                "evidence_kind": "page",
                "required_anchor_level": "page",
                "locator": { "page_index": 0 }
            }
        ])),
        request(serde_json::json!([
            {
                "evidence_id": "ev",
                "evidence_kind": "text_region",
                "required_anchor_level": "text_bbox",
                "locator": { "page_index": 1, "bbox": [1, 2, 3, 4] },
                "expected_text": "x"
            }
        ])),
        request(serde_json::json!([
            {
                "evidence_id": "ev",
                "evidence_kind": "page",
                "required_anchor_level": "page",
                "locator": { "page_index": 1, "page_id": "p0001" }
            }
        ])),
        request(serde_json::json!([
            {
                "evidence_id": "ev",
                "evidence_kind": "page",
                "required_anchor_level": "text_bbox",
                "locator": { "page_index": 1 }
            }
        ])),
    ];
    for request in cases {
        let output = run_ethos(&[
            "evidence",
            "anchor",
            document_example().to_str().unwrap(),
            "--evidence-refs",
            request.to_str().unwrap(),
        ]);
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty());
    }
}

#[test]
fn table_cell_expected_text_uses_exact_normalized_match() {
    let request = request(serde_json::json!([
        {
            "evidence_id": "ev_cell",
            "evidence_kind": "table_cell",
            "required_anchor_level": "table_cell",
            "locator": {
                "table_id": "t0001",
                "cell": { "row": 1, "col": 1 }
            },
            "expected_text": "12.4"
        }
    ]));
    let report = parse_success(&[
        "evidence",
        "anchor",
        document_example().to_str().unwrap(),
        "--evidence-refs",
        request.to_str().unwrap(),
    ]);
    assert_eq!(report["anchors"][0]["anchor_status"], "mismatch");
    assert_eq!(report["anchors"][0]["checks"]["table_cell"], "mismatch");
}

#[test]
fn text_mismatch_takes_precedence_over_bbox_capability_limit() {
    let request = request(serde_json::json!([
        {
            "evidence_id": "odl_mismatch_limited",
            "evidence_kind": "text_region",
            "required_anchor_level": "text_bbox",
            "locator": {
                "page_index": 1,
                "bbox": [72, 101, 540, 115],
                "coordinate_profile": "ethos_quantized_top_left_v1"
            },
            "expected_text": "not present in the source"
        }
    ]));
    let report = parse_success(&[
        "evidence",
        "anchor",
        opendataloader_example().to_str().unwrap(),
        "--grounding",
        "opendataloader-json",
        "--evidence-refs",
        request.to_str().unwrap(),
    ]);
    assert_eq!(report["anchors"][0]["checks"]["text"], "mismatch");
    assert_eq!(report["anchors"][0]["checks"]["bbox"], "capability_limited");
    assert_eq!(report["anchors"][0]["anchor_status"], "mismatch");
}

#[test]
fn unknown_grounding_and_source_shape_exit_two() {
    let request = request(serde_json::json!([]));
    let output = run_ethos(&[
        "evidence",
        "anchor",
        document_example().to_str().unwrap(),
        "--grounding",
        "unknown",
        "--evidence-refs",
        request.to_str().unwrap(),
    ]);
    assert_eq!(output.status.code(), Some(2));

    let bad_source = temp_json("bad-source", serde_json::json!({"not": "a source"}));
    let output = run_ethos(&[
        "evidence",
        "anchor",
        bad_source.to_str().unwrap(),
        "--evidence-refs",
        request.to_str().unwrap(),
    ]);
    assert_eq!(output.status.code(), Some(2));
}

#[test]
fn repeated_input_is_byte_identical() {
    let request = request(serde_json::json!([
        {
            "evidence_id": "ev_text",
            "evidence_kind": "text",
            "required_anchor_level": "text",
            "locator": { "page_index": 1 },
            "expected_text": "Revenue grew to $12.4M in Q3 2025"
        }
    ]));
    let document = document_example();
    let args = [
        "evidence",
        "anchor",
        document.to_str().unwrap(),
        "--evidence-refs",
        request.to_str().unwrap(),
    ];
    let first = run_ethos(&args);
    let second = run_ethos(&args);
    assert!(first.status.success());
    assert!(second.status.success());
    assert_eq!(first.stdout, second.stdout);
}
