use std::path::{Path, PathBuf};
use std::process::{Command, Output};

use serde_json::Value;

fn ethos_bin() -> &'static str {
    env!("CARGO_BIN_EXE_ethos")
}

fn fixture_pdf() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../fixtures/synthetic/simple-text/document.pdf")
}

fn two_line_fixture_pdf() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../fixtures/synthetic/two-lines/document.pdf")
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
