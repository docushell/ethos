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

use ethos_core::config::ParseConfig;
use ethos_core::traits::{EthosPdfBackend as _, LayoutEngine as _};
use serde_json::Value;

fn ethos_bin() -> &'static str {
    env!("CARGO_BIN_EXE_ethos")
}

fn fixtures_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../fixtures")
}

fn cli_test_fixtures_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures")
}

fn fixture_manifest_entries() -> Vec<Value> {
    let manifest_path = fixtures_root().join("manifest.json");
    let bytes = std::fs::read(&manifest_path).expect("fixture manifest is readable");
    let manifest: Value = serde_json::from_slice(&bytes).expect("fixture manifest is JSON");
    manifest["fixtures"]
        .as_array()
        .expect("fixture manifest entries are an array")
        .clone()
}

fn fixture_manifest_entry(id: &str) -> Value {
    fixture_manifest_entries()
        .into_iter()
        .find(|entry| entry["id"].as_str() == Some(id))
        .unwrap_or_else(|| panic!("fixture manifest contains {id}"))
}

fn fixture_pdf_by_id(id: &str) -> PathBuf {
    let entry = fixture_manifest_entry(id);
    fixtures_root().join(
        entry["file"]
            .as_str()
            .expect("fixture file path is a string"),
    )
}

fn fixture_dir_by_id(id: &str) -> PathBuf {
    fixture_pdf_by_id(id)
        .parent()
        .expect("fixture document has a parent directory")
        .to_path_buf()
}

fn successful_fixture_ids() -> Vec<String> {
    fixture_manifest_entries()
        .into_iter()
        .filter(|entry| {
            !entry["subsets"]
                .as_array()
                .expect("fixture subsets are an array")
                .iter()
                .any(|subset| subset.as_str() == Some("failure"))
        })
        .map(|entry| {
            entry["id"]
                .as_str()
                .expect("fixture id is a string")
                .to_string()
        })
        .collect()
}

fn fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("simple-text")
}

fn two_line_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("synthetic-two-lines")
}

fn heading_export_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("synthetic-heading-export")
}

fn two_column_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("synthetic-two-columns")
}

fn rotation_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("synthetic-rotation-90")
}

fn hyphenated_line_break_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("synthetic-hyphenated-line-break")
}

fn ligature_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("synthetic-ligature-fi-embedded-font")
}

fn invalid_header_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("failure-invalid-header")
}

fn corrupt_header_valid_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("failure-corrupt-header-valid")
}

fn blank_page_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("failure-image-only-or-blank-page")
}

fn memory_limit_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("failure-memory-limit-simulated")
}

fn password_protected_fixture_pdf() -> PathBuf {
    fixture_pdf_by_id("failure-password-protected")
}

fn font_isolation_fixture_pdf(name: &str) -> PathBuf {
    cli_test_fixtures_root()
        .join("font-isolation")
        .join(format!("{name}.pdf"))
}

fn pdfium_configured() -> bool {
    std::env::var_os("ETHOS_PDFIUM_LIBRARY_PATH")
        .map(PathBuf::from)
        .is_some_and(|path| path.is_file())
}

fn run_ethos(args: &[&str]) -> Output {
    Command::new(ethos_bin())
        .args(args)
        .output()
        .expect("ethos command runs")
}

fn run_ethos_with_env(args: &[&str], envs: &[(&str, &str)]) -> Output {
    let mut command = Command::new(ethos_bin());
    command.args(args);
    for (key, value) in envs {
        command.env(key, value);
    }
    command.output().expect("ethos command runs")
}

fn parse_json(args: &[&str]) -> Value {
    let output = run_ethos(args);
    assert!(
        output.status.success(),
        "ethos failed\nstatus: {:?}\nstderr:\n{}\nstdout:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    serde_json::from_slice(&output.stdout).expect("stdout is JSON")
}

fn assert_span_fonts(doc: &Value, expected_font_id: &str) {
    for span in doc["payload"]["spans"].as_array().unwrap() {
        assert_eq!(span["font_id"], expected_font_id);
        assert!(span["font_size_q"].as_i64().unwrap() > 0);
    }
}

fn assert_span_font_namespace(doc: &Value) {
    for span in doc["payload"]["spans"].as_array().unwrap() {
        let font_id = span["font_id"].as_str().expect("span font_id is string");
        assert!(
            font_id.starts_with("subst:") || font_id.starts_with("embedded:"),
            "font_id must be deterministic, got {font_id}"
        );
    }
}

fn font_isolation_env() -> Vec<(String, String)> {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock after unix epoch")
        .as_nanos();
    let root = std::env::temp_dir().join(format!("ethos-font-isolation-{nanos}"));
    vec![
        ("FONTCONFIG_FILE".to_string(), "/dev/null".to_string()),
        (
            "FONTCONFIG_PATH".to_string(),
            root.join("fontconfig").to_string_lossy().to_string(),
        ),
        (
            "XDG_CACHE_HOME".to_string(),
            root.join("cache").to_string_lossy().to_string(),
        ),
        (
            "HOME".to_string(),
            root.join("home").to_string_lossy().to_string(),
        ),
    ]
}

fn env_pairs(env: &[(String, String)]) -> Vec<(&str, &str)> {
    env.iter()
        .map(|(key, value)| (key.as_str(), value.as_str()))
        .collect()
}

fn assert_no_control_chars(text: &str) {
    assert!(
        !text.chars().any(char::is_control),
        "text contains a control character: {text:?}"
    );
}

fn assert_or_accept_golden(path: PathBuf, value: &Value) {
    let mut expected = ethos_core::c14n::c14n_bytes(value).expect("golden value is canonical");
    expected.push(b'\n');

    if std::env::var("ETHOS_ACCEPT_GOLDENS").as_deref() == Ok("1") {
        std::fs::write(&path, expected).expect("golden can be written");
        return;
    }

    let actual = std::fs::read(&path).unwrap_or_else(|err| {
        panic!(
            "missing golden {}; rerun with ETHOS_ACCEPT_GOLDENS=1 after review: {err}",
            path.display()
        )
    });
    assert_eq!(
        actual,
        expected,
        "golden drift for {}; rerun with ETHOS_ACCEPT_GOLDENS=1 only after reviewing the parser change",
        path.display()
    );
}

fn assert_stdout_matches_fixture_file(
    output: Output,
    expected_path: PathBuf,
    fixture_id: &str,
    format: &str,
) {
    assert!(
        output.status.success(),
        "ethos doc parse --format {format} failed for {fixture_id}\nstatus: {:?}\nstderr:\n{}\nstdout:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    assert!(
        output.stderr.is_empty(),
        "ethos doc parse --format {format} wrote stderr for {fixture_id}:\n{}",
        String::from_utf8_lossy(&output.stderr)
    );
    if std::env::var("ETHOS_ACCEPT_GOLDENS").as_deref() == Ok("1") {
        std::fs::write(&expected_path, &output.stdout)
            .unwrap_or_else(|err| panic!("{} can be written: {err}", expected_path.display()));
        return;
    }
    let expected = std::fs::read(&expected_path)
        .unwrap_or_else(|err| panic!("{} is readable: {err}", expected_path.display()));
    assert_eq!(
        output.stdout,
        expected,
        "stdout for {fixture_id} --format {format} must match {}",
        expected_path.display()
    );
}

#[test]
fn successful_fixtures_match_extraction_and_layout_goldens_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping stage golden test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let backend = ethos_pdf::PdfiumBackend::default();
    let config = ParseConfig::default();
    let layout_engine = ethos_layout::BasicLayoutEngine;

    for fixture_id in successful_fixture_ids() {
        let fixture = fixture_pdf_by_id(&fixture_id);
        let pdf_bytes = std::fs::read(&fixture).expect("fixture PDF is readable");
        let extraction = backend
            .extract(&pdf_bytes, &config)
            .unwrap_or_else(|err| panic!("extracts {fixture_id}: {err:?}"));
        let extraction_value =
            serde_json::to_value(&extraction).expect("extraction serializes to JSON");
        assert_or_accept_golden(
            fixture_dir_by_id(&fixture_id).join("extraction.json"),
            &extraction_value,
        );

        let layout = layout_engine
            .layout(&extraction)
            .unwrap_or_else(|err| panic!("layouts {fixture_id}: {err:?}"));
        let layout_value = serde_json::to_value(&layout).expect("layout serializes to JSON");
        assert_or_accept_golden(
            fixture_dir_by_id(&fixture_id).join("layout.json"),
            &layout_value,
        );
    }
}

#[test]
fn doc_parse_text_and_markdown_exports_match_fixture_goldens_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping text/Markdown export golden test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    for fixture_id in successful_fixture_ids() {
        let fixture = fixture_pdf_by_id(&fixture_id);
        let fixture_dir = fixture_dir_by_id(&fixture_id);
        for (format, golden) in [("text", "text.txt"), ("markdown", "markdown.md")] {
            let output = run_ethos(&[
                "doc",
                "parse",
                fixture.to_str().unwrap(),
                "--format",
                format,
            ]);
            assert_stdout_matches_fixture_file(
                output,
                fixture_dir.join(golden),
                &fixture_id,
                format,
            );
        }
    }
}

#[test]
fn parses_heading_fixture_and_exports_markdown_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!(
            "skipping heading export fixture test: ETHOS_PDFIUM_LIBRARY_PATH is not configured"
        );
        return;
    }

    let fixture = heading_export_fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);
    let elements = doc["payload"]["elements"].as_array().unwrap();
    assert_eq!(elements.len(), 2);
    assert_eq!(elements[0]["type"], "heading");
    assert_eq!(elements[0]["heading_level"], 1);
    assert_eq!(elements[0]["text"], "Alpha Overview");
    assert_eq!(elements[1]["type"], "text_block");
    assert_eq!(elements[1]["text"], "Trust loop evidence stays explicit");

    let output = run_ethos(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "markdown",
    ]);
    assert!(
        output.status.success(),
        "ethos doc parse --format markdown failed for heading fixture\nstatus: {:?}\nstderr:\n{}\nstdout:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    assert_eq!(
        String::from_utf8(output.stdout).expect("markdown stdout is UTF-8"),
        "# Alpha Overview\n\nTrust loop evidence stays explicit\n"
    );
}

#[cfg(debug_assertions)]
#[test]
fn doc_parse_timeout_kills_pdfium_worker() {
    let fixture = fixture_pdf();
    let output = run_ethos_with_env(
        &[
            "doc",
            "parse",
            fixture.to_str().unwrap(),
            "--format",
            "json",
            "--max-parse-ms",
            "25",
        ],
        &[("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_SLEEP_MS", "250")],
    );
    assert_eq!(output.status.code(), Some(10));
    assert!(output.stdout.is_empty());
    let error: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(error["error"]["code"], "parse_timeout");
    assert_eq!(error["error"]["message"], "parse exceeded max_parse_ms");
}

#[cfg(debug_assertions)]
#[test]
fn pdf_fingerprint_timeout_kills_pdfium_worker() {
    let fixture = fixture_pdf();
    let output = run_ethos_with_env(
        &[
            "fingerprint",
            fixture.to_str().unwrap(),
            "--max-parse-ms",
            "25",
        ],
        &[("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_SLEEP_MS", "250")],
    );
    assert_eq!(output.status.code(), Some(10));
    assert!(output.stdout.is_empty());
    let error: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(error["error"]["code"], "parse_timeout");
}

#[cfg(debug_assertions)]
#[test]
fn doc_parse_non_envelope_worker_failure_stays_canonical_without_diagnostics() {
    let fixture = fixture_pdf();
    let output = run_ethos_with_env(
        &[
            "doc",
            "parse",
            fixture.to_str().unwrap(),
            "--format",
            "json",
        ],
        &[
            (
                "ETHOS_INTERNAL_TEST_PDFIUM_WORKER_STDERR",
                "native pdfium stderr sentinel\nsecond line",
            ),
            ("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_EXIT_CODE", "101"),
        ],
    );
    assert_eq!(output.status.code(), Some(12));
    assert!(output.stdout.is_empty());
    assert_eq!(
        String::from_utf8_lossy(&output.stderr),
        "{\"error\":{\"code\":\"internal_error\",\"message\":\"pdfium worker failed\"}}\n"
    );
}

#[cfg(debug_assertions)]
#[test]
fn doc_parse_non_envelope_worker_failure_includes_stderr_with_diagnostics() {
    let fixture = fixture_pdf();
    let output = run_ethos_with_env(
        &[
            "doc",
            "parse",
            fixture.to_str().unwrap(),
            "--format",
            "json",
            "--diagnostics",
        ],
        &[
            (
                "ETHOS_INTERNAL_TEST_PDFIUM_WORKER_STDERR",
                "native pdfium stderr sentinel\nsecond line",
            ),
            ("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_EXIT_CODE", "101"),
        ],
    );
    assert_eq!(output.status.code(), Some(12));
    assert!(output.stdout.is_empty());
    let error: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(error["error"]["code"], "internal_error");
    assert_eq!(error["error"]["message"], "pdfium worker failed");
    assert_eq!(error["diagnostics"]["pdfium_worker"]["exit_code"], 101);
    assert_eq!(
        error["diagnostics"]["pdfium_worker"]["stderr"],
        "native pdfium stderr sentinel\nsecond line"
    );
}

#[cfg(debug_assertions)]
#[test]
fn doc_parse_memory_limit_worker_failure_is_stable() {
    let fixture = memory_limit_fixture_pdf();
    let output = run_ethos_with_env(
        &[
            "doc",
            "parse",
            fixture.to_str().unwrap(),
            "--format",
            "json",
        ],
        &[("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_MEMORY_LIMIT", "1")],
    );
    assert_eq!(output.status.code(), Some(11));
    assert!(output.stdout.is_empty());
    let error: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(error["error"]["code"], "memory_limit_exceeded");
    assert_eq!(error["error"]["message"], "parse exceeded memory limit");
}

#[test]
fn doc_parse_relays_worker_stable_error_envelope() {
    let fixture = invalid_header_fixture_pdf();
    let output = run_ethos(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);
    assert_eq!(output.status.code(), Some(3));
    assert!(output.stdout.is_empty());
    let error: Value = serde_json::from_slice(&output.stderr).unwrap();
    assert_eq!(error["error"]["code"], "invalid_pdf");
    assert_eq!(
        error["error"]["message"],
        "input does not contain a PDF header"
    );
}

#[test]
fn pdfium_failure_fixtures_emit_stable_error_envelopes_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!(
            "skipping PDFium failure fixture test: ETHOS_PDFIUM_LIBRARY_PATH is not configured"
        );
        return;
    }

    let cases = [
        (
            corrupt_header_valid_fixture_pdf(),
            4,
            "corrupt_pdf",
            "PDF structure is corrupt",
        ),
        (
            blank_page_fixture_pdf(),
            8,
            "ocr_required",
            "no extractable text; OCR is required",
        ),
        (
            password_protected_fixture_pdf(),
            5,
            "password_protected",
            "document is encrypted or password-protected",
        ),
    ];

    for (fixture, exit_code, code, message) in cases {
        let output = run_ethos(&[
            "doc",
            "parse",
            fixture.to_str().unwrap(),
            "--format",
            "json",
        ]);
        assert_eq!(
            output.status.code(),
            Some(exit_code),
            "unexpected exit code for {}",
            fixture.display()
        );
        assert!(
            output.stdout.is_empty(),
            "failure case must not write stdout for {}",
            fixture.display()
        );
        let error: Value = serde_json::from_slice(&output.stderr).unwrap();
        assert_eq!(error["error"]["code"], code, "{}", fixture.display());
        assert_eq!(error["error"]["message"], message, "{}", fixture.display());
    }
}

#[test]
fn parses_two_column_pdf_in_geometry_reading_order_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping two-column layout test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = two_column_fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);

    let elements = doc["payload"]["elements"].as_array().unwrap();
    assert_eq!(elements.len(), 2);
    assert_eq!(elements[0]["id"], "e000001");
    assert_eq!(elements[0]["text"], "Left top Left bottom");
    assert_eq!(elements[1]["id"], "e000002");
    assert_eq!(elements[1]["text"], "Right top Right bottom");

    let left_bbox = elements[0]["bbox"].as_array().unwrap();
    let right_bbox = elements[1]["bbox"].as_array().unwrap();
    assert!(
        left_bbox[0].as_i64().unwrap() < right_bbox[0].as_i64().unwrap(),
        "left column must sort before right column by geometry"
    );

    let spans = doc["payload"]["spans"].as_array().unwrap();
    assert_eq!(spans.len(), 8);
    assert_span_fonts(&doc, "subst:liberation-sans-regular");
    for element in elements {
        let text = element["text"].as_str().unwrap();
        let joined = element["span_refs"]
            .as_array()
            .unwrap()
            .iter()
            .map(|span_ref| {
                let span_id = span_ref.as_str().unwrap();
                spans
                    .iter()
                    .find(|span| span["id"] == span_id)
                    .and_then(|span| span["text"].as_str())
                    .unwrap()
            })
            .collect::<Vec<_>>()
            .join(" ");
        assert_eq!(joined, text);
    }
}

#[test]
fn parses_two_line_pdf_into_paragraph_text_block_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping two-line layout test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = two_line_fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);

    let elements = doc["payload"]["elements"].as_array().unwrap();
    assert_eq!(elements.len(), 1);
    assert_eq!(elements[0]["id"], "e000001");
    assert_eq!(elements[0]["text"], "First line Second line");
    assert_eq!(
        elements[0]["span_refs"],
        serde_json::json!(["s000001", "s000002", "s000003", "s000004"])
    );

    let spans = doc["payload"]["spans"].as_array().unwrap();
    assert_eq!(spans.len(), 4);
    assert_span_fonts(&doc, "subst:liberation-sans-regular");
    assert_eq!(spans[0]["char_start"], 0);
    assert_eq!(spans[0]["char_end"], 5);
    assert_eq!(spans[1]["char_start"], 6);
    assert_eq!(spans[1]["char_end"], 10);
    assert_eq!(spans[2]["char_start"], 11);
    assert_eq!(spans[2]["char_end"], 17);
    assert_eq!(spans[3]["char_start"], 18);
    assert_eq!(spans[3]["char_end"], 22);
}

#[test]
fn parses_rotation_90_pdf_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping rotation PDFium test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = rotation_fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);

    let pages = doc["payload"]["pages"].as_array().unwrap();
    assert_eq!(pages.len(), 1);
    assert_eq!(pages[0]["rotation"], 90);
    assert_eq!(pages[0]["width"], 30000);
    assert_eq!(pages[0]["height"], 14400);

    let elements = doc["payload"]["elements"].as_array().unwrap();
    assert_eq!(elements.len(), 1);
    assert_eq!(elements[0]["text"], "Rotate Ninety");
    assert_eq!(
        elements[0]["span_refs"],
        serde_json::json!(["s000001", "s000002"])
    );

    let spans = doc["payload"]["spans"].as_array().unwrap();
    assert_eq!(spans.len(), 2);
    assert_eq!(spans[0]["text"], "Rotate");
    assert_eq!(spans[1]["text"], "Ninety");
    assert_span_fonts(&doc, "subst:liberation-sans-regular");
    assert_eq!(spans[0]["char_start"], 0);
    assert_eq!(spans[0]["char_end"], 6);
    assert_eq!(spans[1]["char_start"], 7);
    assert_eq!(spans[1]["char_end"], 13);
}

#[test]
fn parses_hyphenated_line_break_without_control_chars_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping hyphenation PDFium test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = hyphenated_line_break_fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);

    let elements = doc["payload"]["elements"].as_array().unwrap();
    assert_eq!(elements.len(), 1);
    assert_eq!(elements[0]["text"], "hyphen ated");
    assert_no_control_chars(elements[0]["text"].as_str().unwrap());
    assert_eq!(
        elements[0]["span_refs"],
        serde_json::json!(["s000001", "s000002"])
    );

    let spans = doc["payload"]["spans"].as_array().unwrap();
    assert_eq!(spans.len(), 2);
    assert_eq!(spans[0]["text"], "hyphen");
    assert_eq!(spans[1]["text"], "ated");
    assert_span_fonts(&doc, "subst:liberation-sans-regular");
    for span in spans {
        assert_no_control_chars(span["text"].as_str().unwrap());
    }
    assert_eq!(spans[0]["char_start"], 0);
    assert_eq!(spans[0]["char_end"], 6);
    assert_eq!(spans[1]["char_start"], 7);
    assert_eq!(spans[1]["char_end"], 11);
}

#[test]
fn parses_ligature_fixture_with_embedded_font_identity_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping ligature PDFium test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = ligature_fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);

    let elements = doc["payload"]["elements"].as_array().unwrap();
    assert_eq!(elements.len(), 1);
    assert_eq!(elements[0]["text"], "office file");
    assert_no_control_chars(elements[0]["text"].as_str().unwrap());
    assert_eq!(
        elements[0]["span_refs"],
        serde_json::json!(["s000001", "s000002"])
    );

    let spans = doc["payload"]["spans"].as_array().unwrap();
    assert_eq!(spans.len(), 2);
    assert_eq!(spans[0]["text"], "office");
    assert_eq!(spans[1]["text"], "file");
    for span in spans {
        assert_eq!(span["font_id"], "embedded:EthosLigatureFixture-Regular");
        assert!(span["font_size_q"].as_i64().unwrap() > 0);
        assert_no_control_chars(span["text"].as_str().unwrap());
    }
    assert_eq!(spans[0]["char_start"], 0);
    assert_eq!(spans[0]["char_end"], 6);
    assert_eq!(spans[1]["char_start"], 7);
    assert_eq!(spans[1]["char_end"], 11);
    assert_eq!(
        doc["payload"]["parser_warnings"].as_array().unwrap().len(),
        0
    );
}

#[test]
fn font_mapping_is_stable_under_isolated_system_font_environment() {
    if !pdfium_configured() {
        eprintln!("skipping font isolation test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let cases = [
        (
            "standard14-fonts",
            vec![
                "subst:liberation-sans-bold",
                "subst:liberation-mono-italic",
                "subst:liberation-serif-italic",
            ],
        ),
        ("missing-font", vec!["subst:liberation-sans-regular"]),
    ];
    let isolated_env = font_isolation_env();
    let isolated_pairs = env_pairs(&isolated_env);

    for (fixture_name, expected_fonts) in cases {
        let fixture = font_isolation_fixture_pdf(fixture_name);
        let args = [
            "doc",
            "parse",
            fixture.to_str().unwrap(),
            "--format",
            "json",
        ];
        let normal = run_ethos(&args);
        let isolated = run_ethos_with_env(&args, &isolated_pairs);

        assert!(
            normal.status.success(),
            "normal font run failed for {fixture_name}: {}",
            String::from_utf8_lossy(&normal.stderr)
        );
        assert!(
            isolated.status.success(),
            "isolated font run failed for {fixture_name}: {}",
            String::from_utf8_lossy(&isolated.stderr)
        );
        assert_eq!(
            normal.stdout, isolated.stdout,
            "font-isolated output drifted for {fixture_name}"
        );

        let doc: Value = serde_json::from_slice(&normal.stdout).unwrap();
        assert_span_font_namespace(&doc);
        let mut actual_fonts = doc["payload"]["spans"]
            .as_array()
            .unwrap()
            .iter()
            .map(|span| span["font_id"].as_str().unwrap())
            .collect::<Vec<_>>();
        actual_fonts.dedup();
        assert_eq!(actual_fonts, expected_fonts, "{fixture_name}");
    }
}

#[test]
fn cid_cjk_like_font_fixture_is_deterministic_under_isolated_system_font_environment() {
    if !pdfium_configured() {
        eprintln!("skipping CID/CJK-like font isolation test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = font_isolation_fixture_pdf("cid-cjk-like");
    let args = [
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ];
    let isolated_env = font_isolation_env();
    let isolated_pairs = env_pairs(&isolated_env);
    let normal = run_ethos(&args);
    let isolated = run_ethos_with_env(&args, &isolated_pairs);

    assert_eq!(normal.status.code(), isolated.status.code());
    assert_eq!(
        normal.stdout, isolated.stdout,
        "CID/CJK-like output drifted under font isolation"
    );
    assert_eq!(
        normal.stderr, isolated.stderr,
        "CID/CJK-like error envelope drifted under font isolation"
    );

    if normal.status.success() {
        let doc: Value = serde_json::from_slice(&normal.stdout).unwrap();
        assert_span_font_namespace(&doc);
    } else {
        let error: Value = serde_json::from_slice(&normal.stderr).unwrap();
        assert!(
            matches!(
                error["error"]["code"].as_str(),
                Some("ocr_required" | "unsupported_pdf_feature" | "corrupt_pdf")
            ),
            "unexpected CID/CJK-like stable error: {error}"
        );
    }
}

#[test]
fn parses_simple_pdf_into_quantized_spans_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping real PDFium parse test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);

    assert_eq!(doc["payload"]["pages"].as_array().unwrap().len(), 1);
    assert_eq!(doc["payload"]["elements"].as_array().unwrap().len(), 1);
    assert_eq!(doc["payload"]["elements"][0]["text"], "Hello Ethos");
    assert_eq!(doc["payload"]["spans"].as_array().unwrap().len(), 2);
    assert_eq!(doc["payload"]["spans"][0]["text"], "Hello");
    assert_eq!(doc["payload"]["spans"][1]["text"], "Ethos");
    assert_span_fonts(&doc, "subst:liberation-sans-regular");
    assert_eq!(doc["payload"]["spans"][0]["char_start"], 0);
    assert_eq!(doc["payload"]["spans"][0]["char_end"], 5);
    assert_eq!(doc["payload"]["spans"][1]["char_start"], 6);
    assert_eq!(doc["payload"]["spans"][1]["char_end"], 11);
    assert_eq!(
        doc["payload"]["parser_warnings"].as_array().unwrap().len(),
        0
    );
}

#[test]
fn pdfium_geometry_probe_reports_alternative_geometry_signals_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!(
            "skipping PDFium geometry probe test: ETHOS_PDFIUM_LIBRARY_PATH is not configured"
        );
        return;
    }

    let fixture = fixture_pdf();
    let output = run_ethos_with_env(
        &["__pdfium-geometry-probe", fixture.to_str().unwrap()],
        &[("ETHOS_INTERNAL_GEOMETRY_PROBE", "1")],
    );
    assert!(
        output.status.success(),
        "geometry probe failed\nstatus: {:?}\nstderr:\n{}\nstdout:\n{}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    let probe: Value = serde_json::from_slice(&output.stdout).expect("stdout is JSON");

    assert_eq!(probe["schema_version"], "ethos-pdfium-geometry-probe-v1");
    assert_eq!(probe["quantum_per_point"], 100);
    assert_eq!(probe["backend"]["id"], "pdfium");
    let page = &probe["pages"].as_array().unwrap()[0];
    assert_eq!(page["id"], "p0001");
    assert_eq!(page["index"], 1);
    assert!(page["symbols"]["char_origin"].is_boolean());
    assert!(page["symbols"]["loose_char_box"].is_boolean());
    assert!(page["symbols"]["text_rects"].is_boolean());

    let chars = page["chars"].as_array().unwrap();
    assert!(!chars.is_empty());
    assert_eq!(chars[0]["parser_action"], "include");
    assert_eq!(chars[0]["char_box"].as_array().unwrap().len(), 4);

    let runs = page["runs"].as_array().unwrap();
    assert_eq!(runs.len(), 2);
    assert_eq!(runs[0]["text"], "Hello");
    assert_eq!(runs[1]["text"], "Ethos");
    assert_eq!(runs[0]["char_box_union"].as_array().unwrap().len(), 4);
    assert_eq!(runs[0]["char_start"], 0);
    assert_eq!(runs[0]["char_end"], 5);
}

#[test]
fn page_range_filters_and_out_of_range_fails_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping page-range PDFium test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
        "--pages",
        "1",
    ]);
    assert_eq!(doc["payload"]["pages"].as_array().unwrap().len(), 1);
    assert_eq!(doc["payload"]["pages"][0]["index"], 1);

    let output = run_ethos(&["doc", "parse", fixture.to_str().unwrap(), "--pages", "2"]);
    assert_eq!(output.status.code(), Some(2));
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("page selection out of document range")
    );
}

#[test]
fn double_parse_is_byte_identical_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping double-parse PDFium test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = fixture_pdf();
    let args = [
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ];
    let first = run_ethos(&args);
    let second = run_ethos(&args);
    assert!(first.status.success());
    assert!(second.status.success());
    assert_eq!(first.stdout, second.stdout);

    let doc: Value = serde_json::from_slice(&first.stdout).unwrap();
    assert_eq!(doc["payload_sha256"].as_str().unwrap().len(), 64);
    assert!(doc["fingerprint"].as_str().unwrap().starts_with("sha256:"));
}

#[test]
fn pdf_fingerprint_matches_parsed_document_when_pdfium_is_configured() {
    if !pdfium_configured() {
        eprintln!("skipping PDF fingerprint test: ETHOS_PDFIUM_LIBRARY_PATH is not configured");
        return;
    }

    let fixture = fixture_pdf();
    let doc = parse_json(&[
        "doc",
        "parse",
        fixture.to_str().unwrap(),
        "--format",
        "json",
    ]);
    let output = run_ethos(&["fingerprint", fixture.to_str().unwrap()]);
    assert!(
        output.status.success(),
        "fingerprint failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        doc["fingerprint"].as_str().unwrap()
    );
}
