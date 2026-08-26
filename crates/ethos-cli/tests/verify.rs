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

use ethos_core::crop_element::{
    crop_element_request_ref, CropElementRendering, CropElementRequest,
};
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

/// `ethos verify` emits an in-toto Statement (`docs/proof-statement-v1.md`). The report
/// these assertions care about is its predicate; the wrapper is asserted separately in
/// `verify_emits_a_proof_statement`.
fn verify_report(args: &[&str]) -> Value {
    parse_success(args)["predicate"].clone()
}

/// `ethos crop_element` emits an in-toto Statement; the descriptor is its predicate.
fn parse_crop_element_success(args: &[&str]) -> Value {
    let output = run_ethos(args);
    assert!(
        output.status.success(),
        "ethos failed\nstatus: {:?}\nstderr:\n{}\nstdout:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stderr),
        "warning: crop_element is source-only pre-alpha and unsupported\n"
    );
    serde_json::from_slice::<Value>(&output.stdout).expect("stdout is JSON")["predicate"].clone()
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

fn citation_ndjson(citations: &[&Path]) -> String {
    let mut output = citations
        .iter()
        .map(|path| serde_json::to_string(&json_file(path)).expect("citation fixture serializes"))
        .collect::<Vec<_>>()
        .join("\n");
    output.push('\n');
    output
}

fn crop_element_request(
    document: &Value,
    element_id: &str,
    rendering: CropElementRendering,
) -> Value {
    let mut request = CropElementRequest {
        artifact_type: "ethos.crop_element_request.v1".to_string(),
        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
        request_ref: String::new(),
        document_fingerprint: document["fingerprint"]
            .as_str()
            .expect("document fingerprint is a string")
            .to_string(),
        element_id: element_id.to_string(),
        rendering,
        source_pdf_fingerprint: (rendering == CropElementRendering::Rendered).then(|| {
            document["source"]["fingerprint"]
                .as_str()
                .expect("source fingerprint is a string")
                .to_string()
        }),
    };
    request.request_ref = crop_element_request_ref(&request).unwrap();
    serde_json::to_value(request).unwrap()
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

/// True when `ETHOS_PDFIUM_LIBRARY_PATH` points at a PDFium that Ethos itself accepts.
///
/// Asking `ethos doctor` keeps the harness from disagreeing with the product. On a host with no
/// pinned PDFium profile — macOS x64, for example — a correctly downloaded library is still
/// refused, and these tests must skip rather than fail.
fn pdfium_configured() -> bool {
    static USABLE: std::sync::OnceLock<bool> = std::sync::OnceLock::new();
    *USABLE.get_or_init(|| {
        let Some(path) = std::env::var_os("ETHOS_PDFIUM_LIBRARY_PATH").map(PathBuf::from) else {
            return false;
        };
        if !path.is_file() {
            return false;
        }
        let usable = Command::new(ethos_bin())
            .args(["doctor", "--require-pdfium"])
            .output()
            .is_ok_and(|output| output.status.success());
        if !usable {
            eprintln!(
                "skipping PDFium-backed tests: ETHOS_PDFIUM_LIBRARY_PATH is set, but Ethos does \
                 not accept this library on this host. Run `ethos doctor --require-pdfium` for \
                 the reason. Hosts without a pinned PDFium profile (for example macOS x64) are \
                 expected to skip."
            );
        }
        usable
    })
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
    let report = verify_report(&[
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
fn hardened_schema_report_example_matches_cli_output() {
    let root = repo_root();
    let report = verify_report(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("schemas/examples/citations.example.json")
            .to_str()
            .unwrap(),
        "--config",
        root.join("schemas/examples/verification-config.hardened.example.json")
            .to_str()
            .unwrap(),
    ]);
    let expected =
        json_file(root.join("schemas/examples/verification-report.hardened.example.json"));

    assert_eq!(report, expected);
}

/// Payload equivalence, and the reason the goldens did not move when verify output became
/// an in-toto Statement.
///
/// The goldens are still the pre-0.6 report shape. Asserting the emitted *predicate*
/// against them proves the wrapper is a pure re-wrap: every byte the verifier produces is
/// unchanged, only nested. Regenerating the goldens instead would have destroyed exactly
/// the evidence needed to show that, at the one moment it mattered.
///
/// A semantic change now fails here, where a wrapper change fails in
/// `verify_emits_a_proof_statement`. Keeping those separate is the point.
#[test]
fn verify_alpha_demo_report_predicates_match_goldens() {
    for (name, args, expected_path) in verify_alpha_report_cases() {
        let args = args.iter().map(String::as_str).collect::<Vec<_>>();
        let actual = parse_success(&args);
        let expected = json_file(expected_path);
        assert_eq!(actual["predicate"], expected, "golden drift for {name}");
    }
}

/// Every verdict-emitting command wraps its output, and each names its own predicate type.
///
/// One test over all of them because the failure mode is a command that quietly keeps its
/// own serialisation — the drift only shows when two producers disagree, which is exactly
/// when nobody is looking. `ethos doc parse` and `ethos rag chunk` are absent on purpose:
/// representations are not verdicts and stay bare (`docs/proof-statement-v1.md` §1.5).
#[test]
fn every_verdict_command_emits_its_own_predicate_type() {
    let root = repo_root();
    let doc = root.join("schemas/examples/document.example.json");
    let cases: [(&str, Vec<String>); 4] = [
        (
            "grounding",
            vec![
                "verify".into(),
                doc.display().to_string(),
                "--citations".into(),
                root.join("examples/verify/native_grounded_citations.json")
                    .display()
                    .to_string(),
            ],
        ),
        (
            "grounding-validation",
            vec![
                "grounding".into(),
                "check".into(),
                root.join("schemas/examples/grounding-source.example.json")
                    .display()
                    .to_string(),
            ],
        ),
        (
            "security",
            vec![
                "security".into(),
                "report".into(),
                doc.display().to_string(),
            ],
        ),
        (
            "crop",
            vec![
                "crop_element".into(),
                doc.display().to_string(),
                "--request".into(),
                root.join("schemas/examples/crop-element-request.example.json")
                    .display()
                    .to_string(),
            ],
        ),
    ];

    for (predicate, args) in cases {
        let args: Vec<&str> = args.iter().map(String::as_str).collect();
        let output = run_ethos(&args);
        let statement: Value =
            serde_json::from_slice(&output.stdout).unwrap_or_else(|_| panic!("{predicate}: JSON"));

        assert_eq!(
            statement["_type"], "https://in-toto.io/Statement/v1",
            "{predicate}"
        );
        assert_eq!(
            statement["predicateType"],
            format!("https://docushell.com/ethos/{predicate}/v1"),
            "{predicate}"
        );
        assert!(
            statement["predicate"].is_object(),
            "{predicate}: verdict must sit under .predicate"
        );
        let subject = statement["subject"]
            .as_array()
            .unwrap_or_else(|| panic!("{predicate}: subject"));
        assert_eq!(subject.len(), 1, "{predicate}");
        assert!(
            subject[0]["digest"]["sha256"].is_string(),
            "{predicate}: subject needs a digest"
        );
    }
}

/// `evidence_tier` states how precisely each check bound its evidence.
///
/// One report exercising three tiers at once, because the value of the field is that a
/// consumer reads it instead of deriving it from `match_method` plus the citation — and a
/// derivation that only ever sees one tier is a derivation nobody has tested.
#[test]
fn each_check_states_how_precisely_it_bound_evidence() {
    let root = repo_root();
    let report = verify_report(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_grounded_citations.json")
            .to_str()
            .unwrap(),
    ]);
    let tiers: Vec<&str> = report["checks"]
        .as_array()
        .expect("checks is an array")
        .iter()
        .map(|check| {
            check["evidence_tier"]
                .as_str()
                .expect("a grounded check states its tier")
        })
        .collect();

    // element-scoped quote, table cell, page-scoped presence — in citation order
    assert_eq!(tiers, ["element_scoped", "table_cell", "page_scoped"]);
}

/// A check that resolved nothing must not claim a precision it never achieved.
#[test]
fn unresolved_checks_state_no_tier() {
    let root = repo_root();
    let report = verify_report(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_ungrounded_citations.json")
            .to_str()
            .unwrap(),
    ]);
    for check in report["checks"].as_array().expect("checks is an array") {
        if check["status"] == "not_found" {
            assert!(
                check["evidence_tier"].is_null(),
                "a check that found nothing claimed a tier: {check}"
            );
        }
    }
}

/// The attestation block names what produced the verdict.
///
/// A version bump that forgot to flow through would silently produce reports attesting the
/// wrong verifier, so the version is checked against the crate's own metadata rather than
/// a hardcoded string.
#[test]
fn report_attests_the_verifier_config_and_claims() {
    let root = repo_root();
    let report = verify_report(&[
        "verify",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/native_grounded_citations.json")
            .to_str()
            .unwrap(),
    ]);
    let attestation = &report["attestation"];

    assert_eq!(attestation["verifier"]["name"], "ethos-verify");
    assert_eq!(
        attestation["verifier"]["version"],
        env!("CARGO_PKG_VERSION"),
        "verifier version desynced from the crate version"
    );
    assert_eq!(attestation["config_version"], "default-v1");
    assert!(
        attestation["claims_sha256"]
            .as_str()
            .is_some_and(|h| h.len() == 64 && h.chars().all(|c| c.is_ascii_hexdigit())),
        "{attestation:?}"
    );
}

/// `claims_sha256` binds the report to the exact claims, and to nothing else.
///
/// Two properties in one test because they are the same property from both sides: the hash
/// is over the parsed claims array, so an envelope and a bare array carrying identical
/// claims agree, while different claims disagree. Hashing raw file bytes would fail the
/// first; hashing the envelope would too.
#[test]
fn claims_hash_covers_the_claims_and_not_their_packaging() {
    let root = repo_root();
    let doc = root.join("schemas/examples/document.example.json");
    let hash_for = |citations: &str| {
        verify_report(&[
            "verify",
            doc.to_str().unwrap(),
            "--citations",
            root.join(citations).to_str().unwrap(),
        ])["attestation"]["claims_sha256"]
            .as_str()
            .expect("claims_sha256 is a string")
            .to_string()
    };

    let grounded = hash_for("examples/verify/native_grounded_citations.json");
    let ungrounded = hash_for("examples/verify/native_ungrounded_citations.json");
    assert_ne!(
        grounded, ungrounded,
        "different claims must not share a claims_sha256"
    );
}

/// The wrapper itself: shape, spelling, and the subject rule from
/// `docs/proof-statement-v1.md` §1.4.
#[test]
fn verify_emits_a_proof_statement() {
    let root = repo_root();
    let input = root.join("schemas/examples/document.example.json");
    let statement = parse_success(&[
        "verify",
        input.to_str().unwrap(),
        "--citations",
        root.join("examples/verify/native_grounded_citations.json")
            .to_str()
            .unwrap(),
    ]);

    assert_eq!(statement["_type"], "https://in-toto.io/Statement/v1");
    assert_eq!(
        statement["predicateType"],
        "https://docushell.com/ethos/grounding/v1"
    );

    // subject[0] is the representation Ethos read, digested by the bytes of the input file
    // so a consumer holding that file can compute the same value. subject[1] is absent:
    // the only source binding available is producer-declared, and an in-toto subject is
    // matched by digest, so recording a declaration would invite a consumer to conclude
    // Ethos verified against bytes it never saw.
    let subject = statement["subject"]
        .as_array()
        .expect("subject is an array");
    assert_eq!(subject.len(), 1, "{subject:?}");
    assert_eq!(subject[0]["name"], "document.example.json");
    let expected_digest = {
        use sha2::{Digest, Sha256};
        let bytes = std::fs::read(&input).expect("input is readable");
        format!("{:x}", Sha256::digest(&bytes))
    };
    assert_eq!(subject[0]["digest"]["sha256"], expected_digest);
    assert!(
        subject[0]["digest"]["sha256"]
            .as_str()
            .is_some_and(|d| !d.starts_with("sha256:")),
        "in-toto carries the algorithm in the map key; the value must not repeat it"
    );
}

#[test]
fn verify_batch_lines_byte_equal_corresponding_single_verify_reports() {
    let root = repo_root();
    let document = document_example();
    let grounded = root.join("examples/verify/native_grounded_citations.json");
    let ungrounded = root.join("examples/verify/native_ungrounded_citations.json");
    let citations_ndjson = temp_json(
        "verify-batch-single-report-equivalence",
        &citation_ndjson(&[&grounded, &ungrounded]),
    );

    let batch = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        citations_ndjson.to_str().unwrap(),
    ]);
    assert_eq!(batch.status.code(), Some(0));
    assert_eq!(batch.stderr, b"");

    let expected = [grounded, ungrounded]
        .iter()
        .map(|citations| {
            let output = run_ethos(&[
                "verify",
                document.to_str().unwrap(),
                "--citations",
                citations.to_str().unwrap(),
            ]);
            assert_eq!(output.status.code(), Some(0));
            output.stdout[..output.stdout.len() - 1].to_vec()
        })
        .collect::<Vec<_>>();
    assert_eq!(
        batch
            .stdout
            .split(|byte| *byte == b'\n')
            .filter(|line| !line.is_empty())
            .collect::<Vec<_>>(),
        expected.iter().map(Vec::as_slice).collect::<Vec<_>>()
    );
}

#[test]
fn verify_batch_preserves_request_order_and_is_byte_identical_on_repeat() {
    let root = repo_root();
    let document = document_example();
    let grounded = root.join("examples/verify/native_grounded_citations.json");
    let ungrounded = root.join("examples/verify/native_ungrounded_citations.json");
    let citations_ndjson = temp_json(
        "verify-batch-ordering",
        &citation_ndjson(&[&ungrounded, &grounded]),
    );
    let first = temp_output("verify-batch-first");
    let second = temp_output("verify-batch-second");

    for output_path in [&first, &second] {
        let output = run_ethos(&[
            "verify-batch",
            document.to_str().unwrap(),
            "--citations-ndjson",
            citations_ndjson.to_str().unwrap(),
            "--out",
            output_path.to_str().unwrap(),
        ]);
        assert_eq!(output.status.code(), Some(0));
        assert_eq!(output.stdout, b"");
        assert_eq!(output.stderr, b"");
    }

    let first_bytes = std::fs::read(&first).expect("first batch output is readable");
    assert_eq!(
        first_bytes,
        std::fs::read(&second).expect("second batch output is readable")
    );
    let reports = first_bytes
        .split(|byte| *byte == b'\n')
        .filter(|line| !line.is_empty())
        .map(|line| {
            serde_json::from_slice::<Value>(line).expect("NDJSON line is JSON")["predicate"].clone()
        })
        .collect::<Vec<_>>();
    assert_eq!(reports.len(), 2);
    assert_eq!(reports[0]["all_evidence_grounded"], false);
    assert_eq!(reports[1]["all_evidence_grounded"], true);
}

#[test]
fn verify_batch_merged_byte_equals_single_verify_over_concatenated_claims() {
    let root = repo_root();
    let document = document_example();
    let grounded = root.join("examples/verify/native_grounded_citations.json");
    let ungrounded = root.join("examples/verify/native_ungrounded_citations.json");
    let citations_ndjson = temp_json(
        "verify-batch-merged",
        &citation_ndjson(&[&grounded, &ungrounded]),
    );

    // The oracle is plain `verify` over the hand-concatenated envelope: --merged is
    // that concatenation, so the two outputs must agree byte for byte — attestation,
    // check ids, and framing included.
    let grounded_value = json_file(&grounded);
    let ungrounded_value = json_file(&ungrounded);
    assert_eq!(
        grounded_value["document_fingerprint"], ungrounded_value["document_fingerprint"],
        "fixtures must cite one document for this test to merge"
    );
    let mut merged = grounded_value.clone();
    merged["claims"]
        .as_array_mut()
        .expect("claims is an array")
        .extend(
            ungrounded_value["claims"]
                .as_array()
                .expect("claims is an array")
                .iter()
                .cloned(),
        );
    let merged_citations = temp_json(
        "verify-batch-merged-oracle",
        &serde_json::to_string(&merged).expect("merged envelope serializes"),
    );

    let single = run_ethos(&[
        "verify",
        document.to_str().unwrap(),
        "--citations",
        merged_citations.to_str().unwrap(),
    ]);
    assert_eq!(single.status.code(), Some(0));

    let batch = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        citations_ndjson.to_str().unwrap(),
        "--merged",
    ]);
    assert_eq!(batch.status.code(), Some(0));
    assert_eq!(batch.stderr, b"");
    assert_eq!(batch.stdout, single.stdout);

    // One report, one gate: an ungrounded claim anywhere in the batch fails the
    // merged report under --fail-on-ungrounded.
    let failing = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        citations_ndjson.to_str().unwrap(),
        "--merged",
        "--fail-on-ungrounded",
    ]);
    assert_eq!(failing.status.code(), Some(1));
}

#[test]
fn verify_accepts_the_unicode_compat_v1_normalization_profile() {
    let root = repo_root();
    let document = document_example();
    let grounded = root.join("examples/verify/native_grounded_citations.json");
    let mut config = json_file(root.join("schemas/examples/verification-config.example.json"));
    config["matching"]["text_normalization"] = Value::String("unicode_compat_v1".to_string());
    let config_path = temp_json(
        "verify-unicode-compat-config",
        &serde_json::to_string(&config).expect("config serializes"),
    );

    let report = verify_report(&[
        "verify",
        document.to_str().unwrap(),
        "--citations",
        grounded.to_str().unwrap(),
        "--config",
        config_path.to_str().unwrap(),
    ]);
    assert_eq!(report["all_evidence_grounded"], true);
    assert_eq!(report["checks"][0]["status"], "grounded");
}

#[test]
fn verify_batch_merged_enforces_max_checks_over_the_merged_total() {
    let root = repo_root();
    let document = document_example();
    let grounded = root.join("examples/verify/native_grounded_citations.json");
    let ungrounded = root.join("examples/verify/native_ungrounded_citations.json");
    let citations_ndjson = temp_json(
        "verify-batch-merged-max-checks",
        &citation_ndjson(&[&grounded, &ungrounded]),
    );
    // A config whose max_checks admits each request alone but not their sum: the
    // merged report attests this config, so the merged total must satisfy it exactly
    // as one `verify` run over the concatenated claims would.
    let mut config = json_file(root.join("schemas/examples/verification-config.example.json"));
    let per_request_max = [&grounded, &ungrounded]
        .iter()
        .map(|path| json_file(path)["claims"].as_array().expect("claims").len())
        .max()
        .expect("two requests");
    config["limits"]["max_checks"] = Value::from(per_request_max);
    let config_path = temp_json(
        "verify-batch-merged-max-checks-config",
        &serde_json::to_string(&config).expect("config serializes"),
    );

    let per_request = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        citations_ndjson.to_str().unwrap(),
        "--config",
        config_path.to_str().unwrap(),
    ]);
    assert_eq!(per_request.status.code(), Some(0), "each line fits alone");

    let merged = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        citations_ndjson.to_str().unwrap(),
        "--config",
        config_path.to_str().unwrap(),
        "--merged",
    ]);
    assert_eq!(merged.status.code(), Some(2));
    assert_eq!(merged.stdout, b"");
    assert!(
        String::from_utf8_lossy(&merged.stderr).contains("max_checks"),
        "stderr names the limit: {}",
        String::from_utf8_lossy(&merged.stderr)
    );
}

#[test]
fn verify_batch_merged_refuses_mixed_pinned_and_unpinned_requests() {
    let root = repo_root();
    let document = document_example();
    let grounded = root.join("examples/verify/native_grounded_citations.json");
    let pinned = json_file(&grounded);
    let bare_claims = pinned["claims"].clone();
    let ndjson = format!(
        "{}\n{}\n",
        serde_json::to_string(&bare_claims).expect("bare claims serialize"),
        serde_json::to_string(&pinned).expect("pinned citation serializes"),
    );
    let citations_ndjson = temp_json("verify-batch-merged-unpinned", &ndjson);

    let output = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        citations_ndjson.to_str().unwrap(),
        "--merged",
    ]);
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        stderr.contains("line 1") && stderr.contains("document_fingerprint"),
        "stderr names the unpinned line: {stderr}"
    );
}

#[test]
fn verify_batch_merged_refuses_disagreeing_fingerprints_and_writes_nothing() {
    let root = repo_root();
    let document = document_example();
    let grounded = root.join("examples/verify/native_grounded_citations.json");
    let mut restamped = json_file(&grounded);
    restamped["document_fingerprint"] = Value::String(
        "sha256:0000000000000000000000000000000000000000000000000000000000000000".to_string(),
    );
    let ndjson = format!(
        "{}\n{}\n",
        serde_json::to_string(&json_file(&grounded)).expect("citation fixture serializes"),
        serde_json::to_string(&restamped).expect("restamped citation serializes"),
    );
    let citations_ndjson = temp_json("verify-batch-merged-mixed", &ndjson);
    let out = temp_output("verify-batch-merged-mixed-out");

    let output = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        citations_ndjson.to_str().unwrap(),
        "--merged",
        "--out",
        out.to_str().unwrap(),
    ]);
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("document_fingerprint"),
        "stderr names the disagreement: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(
        !out.exists(),
        "a refused merge must not write a partial report"
    );
}

#[test]
fn verify_batch_fail_on_ungrounded_exits_one_after_output_and_invalid_input_writes_nothing() {
    let root = repo_root();
    let document = document_example();
    let ungrounded = root.join("examples/verify/native_ungrounded_citations.json");
    let valid_ndjson = temp_json(
        "verify-batch-fail-on-ungrounded",
        &citation_ndjson(&[&ungrounded]),
    );
    let report_output = temp_output("verify-batch-ungrounded-output");
    let ungrounded_output = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        valid_ndjson.to_str().unwrap(),
        "--fail-on-ungrounded",
        "--out",
        report_output.to_str().unwrap(),
    ]);
    assert_eq!(ungrounded_output.status.code(), Some(1));
    assert_eq!(ungrounded_output.stdout, b"");
    assert!(std::fs::read(&report_output)
        .expect("ungrounded report is written")
        .ends_with(b"\n"));

    let invalid_ndjson = temp_json(
        "verify-batch-invalid-input",
        &format!("{}not-json\n", citation_ndjson(&[&ungrounded])),
    );
    let invalid_output = temp_output("verify-batch-invalid-output");
    let invalid = run_ethos(&[
        "verify-batch",
        document.to_str().unwrap(),
        "--citations-ndjson",
        invalid_ndjson.to_str().unwrap(),
        "--out",
        invalid_output.to_str().unwrap(),
    ]);
    assert_eq!(invalid.status.code(), Some(2));
    assert_eq!(invalid.stdout, b"");
    assert!(
        !invalid_output.exists(),
        "invalid batch must not create output"
    );
}

#[test]
fn verify_batch_enforces_request_count_and_blank_line_boundaries() {
    let root = repo_root();
    let document = document_example();
    let grounded = root.join("examples/verify/native_grounded_citations.json");
    let line = serde_json::to_string(&json_file(&grounded)).unwrap();
    for count in [32, 1024] {
        let input = temp_json(
            &format!("verify-batch-{count}"),
            &(line.clone() + "\n").repeat(count),
        );
        let output = run_ethos(&[
            "verify-batch",
            document.to_str().unwrap(),
            "--citations-ndjson",
            input.to_str().unwrap(),
        ]);
        assert_eq!(
            output.status.code(),
            Some(0),
            "count={count}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(
            output
                .stdout
                .split(|byte| *byte == b'\n')
                .filter(|line| !line.is_empty())
                .count(),
            count
        );
    }
    for (name, contents) in [
        ("empty", String::new()),
        ("interior-blank", format!("{line}\n\n{line}\n")),
        ("oversized", (line.clone() + "\n").repeat(1025)),
    ] {
        let input = temp_json(&format!("verify-batch-{name}"), &contents);
        let output_path = temp_output(&format!("verify-batch-{name}-output"));
        let output = run_ethos(&[
            "verify-batch",
            document.to_str().unwrap(),
            "--citations-ndjson",
            input.to_str().unwrap(),
            "--out",
            output_path.to_str().unwrap(),
        ]);
        assert_eq!(output.status.code(), Some(2), "{name}");
        assert!(!output_path.exists(), "{name} must be atomic");
    }
}

#[test]
fn verify_batch_supports_foreign_grounding_and_explicit_config() {
    let root = repo_root();
    let cases = [
        (
            root.join("fixtures/foreign/opendataloader/real/opendataloader-output.json"),
            root.join("fixtures/foreign/opendataloader/real/citations.json"),
            Some("opendataloader-json"),
            None,
        ),
        (
            document_example(),
            root.join("examples/verify/native_grounded_citations.json"),
            None,
            Some(root.join("schemas/examples/verification-config.hardened.example.json")),
        ),
    ];
    for (source, citations, grounding, config) in cases {
        let input = temp_json(
            "verify-batch-adapter-config",
            &citation_ndjson(&[&citations]),
        );
        let mut batch_args = vec![
            "verify-batch",
            source.to_str().unwrap(),
            "--citations-ndjson",
            input.to_str().unwrap(),
        ];
        let mut single_args = vec![
            "verify",
            source.to_str().unwrap(),
            "--citations",
            citations.to_str().unwrap(),
        ];
        if let Some(value) = grounding {
            batch_args.extend(["--grounding", value]);
            single_args.extend(["--grounding", value]);
        }
        if let Some(path) = config.as_ref() {
            batch_args.extend(["--config", path.to_str().unwrap()]);
            single_args.extend(["--config", path.to_str().unwrap()]);
        }
        let batch = run_ethos(&batch_args);
        let single = run_ethos(&single_args);
        assert_eq!(
            batch.status.code(),
            Some(0),
            "{}",
            String::from_utf8_lossy(&batch.stderr)
        );
        assert_eq!(batch.stdout, single.stdout);
    }
}

#[test]
fn verify_batch_rejects_crop_config_atomically() {
    let root = repo_root();
    let mut config = json_file(root.join("schemas/examples/verification-config.example.json"));
    config["evidence"]["include_crops"] = serde_json::json!(true);
    let config_path = temp_json(
        "verify-batch-crop-config",
        &serde_json::to_string(&config).unwrap(),
    );
    let citations = root.join("examples/verify/native_grounded_citations.json");
    let input = temp_json("verify-batch-crop-input", &citation_ndjson(&[&citations]));
    let output_path = temp_output("verify-batch-crop-output");
    let output = run_ethos(&[
        "verify-batch",
        document_example().to_str().unwrap(),
        "--citations-ndjson",
        input.to_str().unwrap(),
        "--config",
        config_path.to_str().unwrap(),
        "--out",
        output_path.to_str().unwrap(),
    ]);
    assert_eq!(output.status.code(), Some(2));
    assert!(!output_path.exists());
    assert!(String::from_utf8_lossy(&output.stderr).contains("does not support crop evidence"));
}

#[test]
fn real_opendataloader_fixture_verifies_against_golden() {
    let root = repo_root();
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let gated_report: Value = serde_json::from_slice::<Value>(&gated.stdout)
        .expect("stdout is JSON")["predicate"]
        .clone();
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
    let report: Value = serde_json::from_slice::<Value>(&output.stdout).expect("stdout is JSON")
        ["predicate"]
        .clone();
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
    let report = json_file(out)["predicate"].clone();
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
    let report: Value = serde_json::from_slice::<Value>(&output.stdout).expect("stdout is JSON")
        ["predicate"]
        .clone();
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

    let report = json_file(&out)["predicate"].clone();
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
fn crop_element_cli_writes_descriptor() {
    let root = repo_root();
    let descriptor = parse_crop_element_success(&[
        "crop_element",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--request",
        root.join("schemas/examples/crop-element-request.example.json")
            .to_str()
            .unwrap(),
    ]);
    let expected = json_file(root.join("schemas/examples/crop-descriptor.example.json"));

    assert_eq!(descriptor, expected);

    let out = temp_output("crop-element-descriptor");
    let output = run_ethos(&[
        "crop_element",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--request",
        root.join("schemas/examples/crop-element-request.example.json")
            .to_str()
            .unwrap(),
        "--out",
        out.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(output.stdout, b"");
    assert_eq!(
        String::from_utf8_lossy(&output.stderr),
        "warning: crop_element is source-only pre-alpha and unsupported\n"
    );
    assert_eq!(json_file(out)["predicate"], expected);
}

#[test]
fn crop_element_cli_fails_closed_on_invalid_check_id() {
    let root = repo_root();
    let output = run_ethos(&[
        "crop_element",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--request",
        root.join("schemas/examples/crop-element-request.example.json")
            .to_str()
            .unwrap(),
        "--check-id",
        "v1",
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr).contains(
        "crop_element request failed: descriptor must bind exactly one logical check id"
    ));
}

#[test]
fn crop_element_cli_rendered_request_requires_source_pdf_and_crop_dir() {
    let root = repo_root();
    let document = json_file(root.join("schemas/examples/document.example.json"));
    let request = crop_element_request(&document, "e000002", CropElementRendering::Rendered);
    let request = temp_json(
        "crop-element-rendered-request",
        &serde_json::to_string(&request).unwrap(),
    );

    let missing_source = run_ethos(&[
        "crop_element",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--request",
        request.to_str().unwrap(),
    ]);

    assert_eq!(missing_source.status.code(), Some(2));
    assert_eq!(missing_source.stdout, b"");
    assert!(String::from_utf8_lossy(&missing_source.stderr)
        .contains("rendered crop_element request requires --crop-source-pdf"));

    let source_pdf = temp_json("crop-element-fake-source", "%PDF-1.7\n");
    let missing_dir = run_ethos(&[
        "crop_element",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--request",
        request.to_str().unwrap(),
        "--crop-source-pdf",
        source_pdf.to_str().unwrap(),
    ]);

    assert_eq!(missing_dir.status.code(), Some(2));
    assert_eq!(missing_dir.stdout, b"");
    assert!(String::from_utf8_lossy(&missing_dir.stderr)
        .contains("rendered crop_element request requires --crop-dir"));
}

#[test]
fn crop_element_cli_rendered_source_pdf_must_match_document_source() {
    let root = repo_root();
    let document = json_file(root.join("schemas/examples/document.example.json"));
    let request = crop_element_request(&document, "e000002", CropElementRendering::Rendered);
    let request = temp_json(
        "crop-element-rendered-mismatch-request",
        &serde_json::to_string(&request).unwrap(),
    );
    let source_pdf = temp_json("crop-element-mismatch-source", "%PDF-1.7\n");
    let crop_dir = tempfile::tempdir().expect("temp crop dir");

    let output = run_ethos(&[
        "crop_element",
        root.join("schemas/examples/document.example.json")
            .to_str()
            .unwrap(),
        "--request",
        request.to_str().unwrap(),
        "--crop-source-pdf",
        source_pdf.to_str().unwrap(),
        "--crop-dir",
        crop_dir.path().to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(2));
    assert_eq!(output.stdout, b"");
    assert!(String::from_utf8_lossy(&output.stderr)
        .contains("crop source PDF fingerprint does not match document source fingerprint"));
    assert_eq!(std::fs::read_dir(crop_dir.path()).unwrap().count(), 0);
}

#[test]
fn crop_element_cli_writes_rendered_artifacts_when_pdfium_is_configured() {
    if !pdfium_configured() {
        return;
    }

    let root = repo_root();
    let source_pdf = root.join("fixtures/synthetic/simple-text/document.pdf");
    let doc_path = temp_output("crop-element-simple-text-doc");
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

    let document = json_file(&doc_path);
    let request = crop_element_request(&document, "e000001", CropElementRendering::Rendered);
    let request = temp_json(
        "crop-element-simple-text-rendered-request",
        &serde_json::to_string(&request).unwrap(),
    );
    let out = temp_output("crop-element-simple-text-rendered-descriptor");
    let crop_dir = tempfile::tempdir().expect("temp crop dir");

    let output = run_ethos(&[
        "crop_element",
        doc_path.to_str().unwrap(),
        "--request",
        request.to_str().unwrap(),
        "--crop-source-pdf",
        source_pdf.to_str().unwrap(),
        "--crop-dir",
        crop_dir.path().to_str().unwrap(),
        "--out",
        out.to_str().unwrap(),
    ]);

    assert_eq!(output.status.code(), Some(0));
    assert_eq!(output.stdout, b"");
    assert_eq!(
        String::from_utf8_lossy(&output.stderr),
        "warning: crop_element is source-only pre-alpha and unsupported\n"
    );

    let descriptor = json_file(&out);
    assert_eq!(descriptor["rendering_status"], "rendered");
    assert_eq!(descriptor["rendered_format"], "png");
    let source_bytes = std::fs::read(&source_pdf).expect("source PDF fixture is readable");
    assert_eq!(
        descriptor["source_pdf_fingerprint"],
        source_fingerprint(&source_bytes)
    );
    assert_eq!(descriptor["document_fingerprint"], document["fingerprint"]);
    assert_eq!(descriptor["check_ids"], serde_json::json!(["v0001"]));
    assert!(descriptor["rendered_width_px"].as_u64().unwrap() > 0);
    assert!(descriptor["rendered_height_px"].as_u64().unwrap() > 0);

    let crop_ref = descriptor["crop_ref"].as_str().unwrap();
    assert_eq!(json_file(crop_dir.path().join(crop_ref)), descriptor);

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

    let report = json_file(&out)["predicate"].clone();
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
    let report = verify_report(&[
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
    let report = verify_report(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);

    // The join still grounds the literal text, but since the semantic_unverified
    // producer landed, a match that exists only as a geometry-inferred assembly of
    // two elements carries the bit — and the bit fails the gate closed, which is
    // its documented contract. The check is the evidence trail; the gate says the
    // report as a whole no longer certifies on it.
    assert_eq!(report["all_evidence_grounded"], false);
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(report["checks"][0]["semantic_unverified"], true);
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
    let report = verify_report(&[
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
    // The fabricated quote is refuted, not merely unadjudicated. The adapter declares an
    // unknown coordinate origin, but no reading-order neighbour of `odl-e2` joins with it to
    // produce "Operating margin was 99%", so no adjacency ruling could ground the claim and
    // the determinate negative stands. An unknown origin only blocks a check when geometry
    // is what the outcome turns on; `split_quote_requires_known_coordinates_for_adjacent_join`
    // in `ethos-verify` covers that case.
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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

    let report = json_file(&out)["predicate"].clone();
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
                  "row": 0,
                  "col": 1
                }
              }
            }
          ]
        }"#,
    );
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
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
    let report = verify_report(&[
        "verify",
        doc.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
        "--config",
        config.to_str().unwrap(),
    ]);
    let expected_config_hash =
        ethos_core::c14n::sha256_hex(&json_file(&config)).expect("config hash computes");

    assert_eq!(
        report["verification_config_sha256"].as_str().unwrap(),
        expected_config_hash
    );
    assert_eq!(report["checks"][0]["status"], "grounded");
    assert_eq!(
        report["checks"][0]["match_method"],
        "normalized_text_contains"
    );
    assert_eq!(report["all_evidence_grounded"], true);
}

#[test]
fn report_html_renders_supported_report_deterministically_and_escapes_content() {
    let root = repo_root();
    let mut report = json_file(root.join("schemas/examples/verification-report.example.json"));
    report["grounding"]["parser"]["name"] = serde_json::json!("parser<script>&\"'");
    report["checks"][0]["claim"]["text"] = serde_json::json!("claim<script>&\"'");
    let input = temp_json("html-report", &serde_json::to_string(&report).unwrap());
    let first = temp_output("html-report-first");
    let second = temp_output("html-report-second");
    for output in [&first, &second] {
        let result = run_ethos(&[
            "report",
            "html",
            input.to_str().unwrap(),
            "--out",
            output.to_str().unwrap(),
        ]);
        assert!(
            result.status.success(),
            "{}",
            String::from_utf8_lossy(&result.stderr)
        );
        assert!(result.stdout.is_empty());
    }
    let html = std::fs::read(&first).unwrap();
    assert_eq!(html, std::fs::read(&second).unwrap());
    let text = String::from_utf8(html).unwrap();
    assert!(text.starts_with("<!doctype html>"));
    assert!(text.contains("Ethos verifies citation grounding, not semantic truth"));
    assert!(text.contains("parser&lt;script&gt;&amp;&quot;&#39;"));
    assert!(text.contains("claim&lt;script&gt;&amp;&quot;&#39;"));
    assert!(text.contains("Status: <strong>grounded</strong>"));
    assert!(text.contains("match method: normalized_text_contains"));
    assert!(text.contains("Grounding capabilities"));
    assert!(text.contains("Capability limits"));
    assert!(text.contains("Proof limitations"));
    assert!(text.contains("Report warnings"));
    assert!(!text.contains("<script"));
    assert!(!text.contains("http://"));
    assert!(!text.contains("https://"));
    assert!(!text.contains("<link"));
    assert!(!text.contains("<img"));
}

#[test]
fn report_html_rejects_unsupported_schema_and_unsafe_crop_root_without_output() {
    let root = repo_root();
    let mut report = json_file(root.join("schemas/examples/verification-report.example.json"));
    report["schema_version"] = serde_json::json!("9.9.9");
    let input = temp_json(
        "unsupported-html-report",
        &serde_json::to_string(&report).unwrap(),
    );
    let output = temp_output("unsupported-html-output");
    let result = run_ethos(&[
        "report",
        "html",
        input.to_str().unwrap(),
        "--out",
        output.to_str().unwrap(),
    ]);
    assert_eq!(result.status.code(), Some(2));
    assert!(!output.exists());
    let valid = root.join("schemas/examples/verification-report.example.json");
    for root in [
        "/crops",
        "../crops",
        "crops//x",
        "crops\\x",
        "https://x",
        "crops?x",
        "crops#x",
        "javascript:alert(1)",
        "data:text/html,x",
        "crops/%2f",
        "./crops",
        "crops/",
        ".",
    ] {
        let output = temp_output("unsafe-crop-root");
        let result = run_ethos(&[
            "report",
            "html",
            valid.to_str().unwrap(),
            "--out",
            output.to_str().unwrap(),
            "--crop-root",
            root,
        ]);
        assert_eq!(result.status.code(), Some(2), "{root}");
        assert!(!output.exists());
    }

    let mut crop_report = json_file(valid);
    crop_report["checks"][0]["evidence"]["crop_ref"] = serde_json::json!("crop-01.png");
    let crop_input = temp_json(
        "safe-html-crop-input",
        &serde_json::to_string(&crop_report).unwrap(),
    );
    let cropless_output = temp_output("cropless-html-crop-output");
    let result = run_ethos(&[
        "report",
        "html",
        crop_input.to_str().unwrap(),
        "--out",
        cropless_output.to_str().unwrap(),
    ]);
    assert!(result.status.success());
    let cropless_html = String::from_utf8(std::fs::read(cropless_output).unwrap()).unwrap();
    assert!(cropless_html.contains("Crop unavailable in this standalone report"));
    assert!(!cropless_html.contains("href="));
    let crop_output = temp_output("safe-html-crop-output");
    let result = run_ethos(&[
        "report",
        "html",
        crop_input.to_str().unwrap(),
        "--crop-root",
        "crops",
        "--out",
        crop_output.to_str().unwrap(),
    ]);
    assert!(result.status.success());
    let crop_html = String::from_utf8(std::fs::read(crop_output).unwrap()).unwrap();
    assert!(crop_html.contains("href=\"crops/crop-01.png\""));
}

#[test]
fn report_html_renders_hardened_and_non_grounded_diagnostics() {
    let root = repo_root();
    for (fixture, expected) in [
        (
            "schemas/examples/verification-report.hardened.example.json",
            "Dispersion",
        ),
        (
            "schemas/examples/verification-report-negative.example.json",
            "Reason: stale_fingerprint",
        ),
    ] {
        let output = temp_output("html-report-variant");
        let result = run_ethos(&[
            "report",
            "html",
            root.join(fixture).to_str().unwrap(),
            "--out",
            output.to_str().unwrap(),
        ]);
        assert!(
            result.status.success(),
            "{fixture}: {}",
            String::from_utf8_lossy(&result.stderr)
        );
        let html = String::from_utf8(std::fs::read(output).unwrap()).unwrap();
        if expected == "Dispersion" {
            assert!(html.contains("Dispersion"));
            assert!(html.contains("grounded_checks"));
            assert!(html.contains("grounded"));
        } else {
            assert!(html.contains(expected), "{html}");
            assert!(html.contains("Status: <strong>stale</strong>"));
        }
    }
}

#[test]
fn grounding_json_check_is_deterministic_and_fail_closed() {
    let root = repo_root();
    let grounding = root.join("schemas/examples/grounding-source.example.json");
    let first = run_ethos(&["grounding", "check", grounding.to_str().unwrap()]);
    let second = run_ethos(&["grounding", "check", grounding.to_str().unwrap()]);
    assert!(first.status.success());
    assert_eq!(first.stderr, b"");
    assert_eq!(first.stdout, second.stdout);
    let report: Value =
        serde_json::from_slice::<Value>(&first.stdout).unwrap()["predicate"].clone();
    assert_eq!(report["structure"], "valid");
    assert_eq!(report["source_binding"], "not_checked");
    assert!(report["representation_sha256"]
        .as_str()
        .unwrap()
        .starts_with("sha256:"));

    let invalid = root.join("schemas/examples/grounding-source-negative-unknown-field.json");
    let output = run_ethos(&["grounding", "check", invalid.to_str().unwrap()]);
    assert_eq!(output.status.code(), Some(2));
    let report: Value =
        serde_json::from_slice::<Value>(&output.stdout).unwrap()["predicate"].clone();
    assert_eq!(report["structure"], "invalid");
    assert_eq!(report["error"]["code"], "unknown_field");
    assert_eq!(report["error"]["path"], "/unexpected");
}

#[test]
fn grounding_json_auto_dispatch_reaches_verifier_without_pdfium() {
    let root = repo_root();
    let output = run_ethos(&[
        "verify",
        root.join("schemas/examples/grounding-source.example.json")
            .to_str()
            .unwrap(),
        "--citations",
        root.join("examples/verify/grounding_json_citations.json")
            .to_str()
            .unwrap(),
    ]);
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let report: Value =
        serde_json::from_slice::<Value>(&output.stdout).unwrap()["predicate"].clone();
    assert_eq!(report["all_evidence_grounded"], true);
    assert_eq!(
        report["grounding"]["parser"]["adapter"],
        "ethos-grounding-json"
    );
}

#[test]
fn grounding_json_batch_dispatch_reaches_the_verifier() {
    let root = repo_root();
    let grounding = root.join("schemas/examples/grounding-source.example.json");
    let citation = root.join("examples/verify/grounding_json_citations.json");
    let citation_line = serde_json::to_string(&json_file(&citation)).unwrap() + "\n";
    let requests = temp_json("grounding-batch-citations", &citation_line);
    let valid_output = temp_output("grounding-batch-valid");
    let result = run_ethos(&[
        "verify-batch",
        grounding.to_str().unwrap(),
        "--citations-ndjson",
        requests.to_str().unwrap(),
        "--out",
        valid_output.to_str().unwrap(),
    ]);
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stderr)
    );
    let lines = std::fs::read_to_string(&valid_output).unwrap();
    assert_eq!(lines.lines().count(), 1);
    assert!(lines.contains("ethos-grounding-json"));
}

#[test]
fn grounding_json_source_hash_match_is_reported_and_verifiable() {
    let root = repo_root();
    let grounding = root.join("schemas/examples/grounding-source-bound.example.json");
    let source_pdf = root.join("fixtures/foreign/opendataloader/real/source.pdf");
    let validation = run_ethos(&[
        "grounding",
        "check",
        grounding.to_str().unwrap(),
        "--source-artifact",
        source_pdf.to_str().unwrap(),
    ]);
    assert!(validation.status.success());
    let validation_report: Value =
        serde_json::from_slice::<Value>(&validation.stdout).unwrap()["predicate"].clone();
    assert_eq!(validation_report["structure"], "valid");
    assert_eq!(validation_report["source_binding"], "matched");

    let verified = run_ethos(&[
        "verify",
        grounding.to_str().unwrap(),
        "--citations",
        root.join("examples/verify/grounding_json_bound_citations.json")
            .to_str()
            .unwrap(),
    ]);
    assert!(
        verified.status.success(),
        "{}",
        String::from_utf8_lossy(&verified.stderr)
    );
    let report: Value =
        serde_json::from_slice::<Value>(&verified.stdout).unwrap()["predicate"].clone();
    assert_eq!(report["all_evidence_grounded"], true);
}

#[test]
fn grounding_json_source_binding_rejects_non_pdf_bytes_before_report() {
    let root = repo_root();
    let grounding = root.join("schemas/examples/grounding-source.example.json");
    let non_pdf = temp_json("grounding-non-pdf", "not a PDF");
    let output = temp_output("grounding-non-pdf-report");
    let result = run_ethos(&[
        "grounding",
        "check",
        grounding.to_str().unwrap(),
        "--source-artifact",
        non_pdf.to_str().unwrap(),
        "--out",
        output.to_str().unwrap(),
    ]);
    assert_eq!(result.status.code(), Some(2));
    assert!(!output.exists());
}

#[test]
fn grounding_json_dispatch_ignores_producer_identity() {
    let root = repo_root();
    let original =
        std::fs::read_to_string(root.join("schemas/examples/grounding-source.example.json"))
            .unwrap();
    let changed = original
        .replace("\"name\": \"fixture\"", "\"name\": \"different-parser\"")
        .replace("\"version\": \"1.0.0\"", "\"version\": \"99.99.99\"");
    let input = temp_json("grounding-producer-identity", &changed);
    let output = run_ethos(&["grounding", "check", input.to_str().unwrap()]);
    assert!(output.status.success());
    let report: Value =
        serde_json::from_slice::<Value>(&output.stdout).unwrap()["predicate"].clone();
    assert_eq!(report["structure"], "valid");
}

#[test]
fn grounding_json_representation_identity_drives_staleness() {
    let root = repo_root();
    let original = root.join("schemas/examples/grounding-source.example.json");
    let citations = root.join("examples/verify/grounding_json_citations.json");
    let original_bytes = std::fs::read(&original).unwrap();
    let changed = String::from_utf8(original_bytes.clone())
        .unwrap()
        .replace("\"name\": \"fixture\"", "\"name\": \"fixture-alt\"");
    let changed_path = temp_json("grounding-representation-changed", &changed);

    let first = run_ethos(&[
        "verify",
        original.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);
    let second = run_ethos(&[
        "verify",
        changed_path.to_str().unwrap(),
        "--citations",
        citations.to_str().unwrap(),
    ]);
    assert!(first.status.success());
    assert!(second.status.success());
    let first_report: Value =
        serde_json::from_slice::<Value>(&first.stdout).unwrap()["predicate"].clone();
    let second_report: Value =
        serde_json::from_slice::<Value>(&second.stdout).unwrap()["predicate"].clone();
    assert_eq!(first_report["fingerprint_stale"], false);
    assert_eq!(first_report["all_evidence_grounded"], true);
    assert_eq!(second_report["fingerprint_stale"], true);
    assert_eq!(second_report["all_evidence_grounded"], false);
    assert_eq!(second_report["checks"][0]["status"], "stale");
    assert_ne!(
        first_report["document_fingerprint"],
        second_report["document_fingerprint"]
    );
}

#[test]
fn verify_rejects_present_but_unsupported_artifact_types_without_fallback() {
    let citations = repo_root().join("examples/verify/grounding_json_citations.json");
    let valid =
        std::fs::read_to_string(repo_root().join("schemas/examples/grounding-source.example.json"))
            .expect("fixture is readable");

    // A duplicated artifact_type must never be collapsed into a supported identity.
    let duplicated = valid.replacen(
        r#""artifact_type": "ethos.grounding.v1","#,
        r#""artifact_type": "ethos.grounding.v1", "artifact_type": "ethos.grounding.v1","#,
        1,
    );
    assert_ne!(duplicated, valid, "fixture shape changed");

    for (name, body) in [
        ("duplicate-artifact-type", duplicated),
        (
            "unknown-artifact-type",
            valid.replace("ethos.grounding.v1", "ethos.grounding.v2"),
        ),
        (
            "non-string-artifact-type",
            valid.replace(r#""ethos.grounding.v1""#, "5"),
        ),
    ] {
        let path = temp_json(name, &body);
        let output = run_ethos(&[
            "verify",
            path.to_str().unwrap(),
            "--citations",
            citations.to_str().unwrap(),
        ]);
        assert_eq!(output.status.code(), Some(2), "{name} must exit 2");
        let stderr = String::from_utf8_lossy(&output.stderr);
        // The native loader also mentions `artifact_type` (as an unknown field), so assert the
        // shared loader's own message to prove no fallback occurred.
        assert!(
            stderr.contains("unsupported top-level artifact_type"),
            "{name} must be rejected by the shared loader, got: {stderr}"
        );
        assert!(output.stdout.is_empty(), "{name} must not write a report");
    }
}
