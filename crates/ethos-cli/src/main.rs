//! # `ethos` — CLI skeleton (Milestone A, WS-CONTRACTS weeks 3–4)
//!
//! Public command groups follow the public architecture: `ethos doc …`, `ethos rag …`,
//! `ethos verify …`, plus `ethos fingerprint` (PRD §9.1). Exit codes are the public
//! contract from docs/architecture.md: 0 success, 2 usage, 3–12 stable error codes.
//!
//! Skeleton status (honest): `doc parse` is wired through the backend boundary and fails
//! with a stable code until WS-ENGINE lands PDFium; `rag chunk` and `fingerprint` are
//! fully functional over canonical JSON; `verify` runs literal quote/value,
//! presence, and table-cell checks over native Ethos JSON and ODL-style JSON.

mod assembly;
mod cmd;
mod worker;

use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Args, Parser, Subcommand, ValueEnum};
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::model::Document;

/// Usage-error exit code (also what clap uses).
pub(crate) const EXIT_USAGE: u8 = 2;
pub(crate) const INTERNAL_GEOMETRY_PROBE_ENV: &str = "ETHOS_INTERNAL_GEOMETRY_PROBE";
pub(crate) const INTERNAL_TABLE_CANDIDATE_PROBE_ENV: &str = "ETHOS_INTERNAL_TABLE_CANDIDATE_PROBE";

#[derive(Parser)]
#[command(
    name = "ethos",
    version,
    about = "Deterministic PDF parsing, RAG artifacts, and citation evidence verification",
    propagate_version = true
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Document parsing and canonical graph (ethos-doc)
    Doc {
        #[command(subcommand)]
        command: DocCommand,
    },
    /// Chunks and retrieval-ready artifacts (ethos-rag)
    Rag {
        #[command(subcommand)]
        command: RagCommand,
    },
    /// Citation evidence verification (ethos-verify)
    Verify(VerifyArgs),
    /// Recompute and check a document fingerprint
    Fingerprint(FingerprintArgs),
    /// Internal killable PDFium worker. Not a public CLI surface.
    #[command(name = "__pdfium-worker", hide = true)]
    PdfiumWorker(PdfiumWorkerArgs),
    /// Internal PDFium geometry source probe. Not a public CLI surface.
    #[command(name = "__pdfium-geometry-probe", hide = true)]
    PdfiumGeometryProbe(PdfiumGeometryProbeArgs),
    /// Internal deterministic table-candidate probe. Not a public CLI surface.
    #[command(name = "__table-candidate-probe", hide = true)]
    TableCandidateProbe(TableCandidateProbeArgs),
}

#[derive(Subcommand)]
enum DocCommand {
    /// Parse a PDF into the canonical document graph
    Parse(DocParseArgs),
}

#[derive(Args)]
pub(crate) struct DocParseArgs {
    /// Input PDF
    pub(crate) input: PathBuf,
    /// Output format
    #[arg(long, value_enum, default_value_t = Format::Json)]
    pub(crate) format: Format,
    /// Output path (file or directory)
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
    /// Page selection, e.g. `1-5,9` (1-based, inclusive; merged canonically).
    /// Enters config_sha256: a different range is a different canonical output.
    #[arg(long)]
    pub(crate) pages: Option<String>,
    /// Include volatile runtime diagnostics (off by default so outputs stay byte-identical)
    #[arg(long)]
    pub(crate) diagnostics: bool,
    /// Internal/test override for the parse timeout limit.
    #[arg(long, hide = true)]
    pub(crate) max_parse_ms: Option<u64>,
}

#[derive(Args)]
pub(crate) struct FingerprintArgs {
    /// Canonical document (`*.ethos.json`). PDF input is parsed under the deterministic profile.
    pub(crate) input: PathBuf,
    /// Internal/test override for the parse timeout limit.
    #[arg(long, hide = true)]
    pub(crate) max_parse_ms: Option<u64>,
}

#[derive(Args)]
pub(crate) struct PdfiumWorkerArgs {
    /// Input PDF.
    pub(crate) input: PathBuf,
    /// Page selection, e.g. `1-5,9` (1-based, inclusive; merged canonically).
    #[arg(long)]
    pub(crate) pages: Option<String>,
    /// Include volatile runtime diagnostics.
    #[arg(long)]
    pub(crate) diagnostics: bool,
    /// Internal/test path where the worker writes canonical JSON instead of stdout.
    #[arg(long, hide = true)]
    pub(crate) json_out: Option<PathBuf>,
}

#[derive(Args)]
pub(crate) struct PdfiumGeometryProbeArgs {
    /// Input PDF.
    pub(crate) input: PathBuf,
    /// Page selection, e.g. `1-5,9` (1-based, inclusive; merged canonically).
    #[arg(long)]
    pub(crate) pages: Option<String>,
}

#[derive(Args)]
pub(crate) struct TableCandidateProbeArgs {
    /// Canonical Ethos document JSON.
    pub(crate) input: PathBuf,
    /// Output path for the probe report (default: stdout).
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
}

#[derive(Clone, Copy, ValueEnum)]
pub(crate) enum Format {
    Json,
    Markdown,
    Text,
}

#[derive(Subcommand)]
enum RagCommand {
    /// Derive chunks.jsonl from a canonical document (deterministic)
    Chunk(RagChunkArgs),
}

#[derive(Args)]
pub(crate) struct RagChunkArgs {
    /// Canonical document (`*.ethos.json`)
    pub(crate) input: PathBuf,
    /// Output path for chunks.jsonl (default: stdout)
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
}

#[derive(Args)]
pub(crate) struct VerifyArgs {
    /// Grounding input: canonical Ethos document, or foreign output with --grounding
    pub(crate) input: PathBuf,
    /// Citations file (JSON). Accepts either an array of claims or
    /// {"document_fingerprint": "...", "claims": [...]}.
    #[arg(long)]
    pub(crate) citations: PathBuf,
    /// Foreign grounding adapter id (e.g. `opendataloader-json`)
    #[arg(long)]
    pub(crate) grounding: Option<String>,
    /// Verification config (JSON); defaults to the pinned `default-v1`
    #[arg(long)]
    pub(crate) config: Option<PathBuf>,
    /// Output path for verification_report.json (default: stdout)
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
}

/// CLI failure: stable error code or usage error, rendered deterministically.
pub(crate) enum Failure {
    Ethos(EthosError),
    EthosWithDiagnostics {
        error: EthosError,
        diagnostics: serde_json::Value,
    },
    Usage(String),
}

impl From<EthosError> for Failure {
    fn from(e: EthosError) -> Self {
        Failure::Ethos(e)
    }
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    match run(cli) {
        Ok(()) => ExitCode::SUCCESS,
        Err(Failure::Usage(message)) => {
            eprintln!("error (usage): {message}");
            ExitCode::from(EXIT_USAGE)
        }
        Err(Failure::Ethos(e)) => {
            write_error_envelope(&e);
            ExitCode::from(e.code.exit_code() as u8)
        }
        Err(Failure::EthosWithDiagnostics { error, diagnostics }) => {
            write_error_envelope_with_diagnostics(&error, diagnostics);
            ExitCode::from(error.code.exit_code() as u8)
        }
    }
}

fn error_envelope_bytes(e: &EthosError) -> Result<Vec<u8>, ethos_core::c14n::C14nError> {
    error_output_bytes(e, None)
}

fn error_output_bytes(
    e: &EthosError,
    diagnostics: Option<serde_json::Value>,
) -> Result<Vec<u8>, ethos_core::c14n::C14nError> {
    let value = serde_json::json!({
        "error": {
            "code": e.code.as_str(),
            "message": e.message,
        }
    });
    let value = if let Some(diagnostics) = diagnostics {
        let mut object = value
            .as_object()
            .cloned()
            .expect("error envelope is object");
        object.insert("diagnostics".to_string(), diagnostics);
        serde_json::Value::Object(object)
    } else {
        value
    };
    let mut bytes = ethos_core::c14n::c14n_bytes(&value)?;
    bytes.push(b'\n');
    Ok(bytes)
}

fn write_error_envelope(e: &EthosError) {
    use std::io::Write as _;

    let bytes = error_envelope_bytes(e).expect("error envelope contains only canonical values");
    let _ = std::io::stderr().write_all(&bytes);
}

fn write_error_envelope_with_diagnostics(e: &EthosError, diagnostics: serde_json::Value) {
    use std::io::Write as _;

    let bytes = error_output_bytes(e, Some(diagnostics))
        .expect("diagnostic error envelope contains only canonical values");
    let _ = std::io::stderr().write_all(&bytes);
}

fn run(cli: Cli) -> Result<(), Failure> {
    match cli.command {
        Command::Doc {
            command: DocCommand::Parse(args),
        } => cmd::doc::doc_parse(args),
        Command::Rag {
            command: RagCommand::Chunk(args),
        } => cmd::rag::rag_chunk(args),
        Command::Verify(args) => cmd::verify::verify(args),
        Command::Fingerprint(args) => cmd::doc::fingerprint(args),
        Command::PdfiumWorker(args) => cmd::doc::pdfium_worker(args),
        Command::PdfiumGeometryProbe(args) => cmd::doc::pdfium_geometry_probe(args),
        Command::TableCandidateProbe(args) => cmd::doc::table_candidate_probe(args),
    }
}

pub(crate) fn read_file(path: &PathBuf) -> Result<Vec<u8>, Failure> {
    fs::read(path).map_err(|_| Failure::Usage(format!("cannot read input: {}", path.display())))
}

pub(crate) fn ensure_file_within_limit(path: &PathBuf, max_bytes: u64) -> Result<(), Failure> {
    let metadata = fs::metadata(path)
        .map_err(|_| Failure::Usage(format!("cannot read input: {}", path.display())))?;
    if metadata.len() > max_bytes {
        return Err(
            EthosError::new(ErrorCode::FileTooLarge, "input exceeds max_file_bytes").into(),
        );
    }
    Ok(())
}

pub(crate) fn read_file_limited(path: &PathBuf, max_bytes: u64) -> Result<Vec<u8>, Failure> {
    ensure_file_within_limit(path, max_bytes)?;
    let bytes = read_file(path)?;
    if bytes.len() as u64 > max_bytes {
        return Err(
            EthosError::new(ErrorCode::FileTooLarge, "input exceeds max_file_bytes").into(),
        );
    }
    Ok(bytes)
}

pub(crate) fn read_document(path: &PathBuf) -> Result<Document, Failure> {
    let bytes = read_file(path)?;
    let doc: Document = serde_json::from_slice(&bytes).map_err(|_| {
        Failure::Ethos(EthosError::new(
            ErrorCode::InternalError,
            "input is not a canonical ethos document (schema urn:ethos:schema:document:1)",
        ))
    })?;
    doc.verify_integrity()?;
    Ok(doc)
}

pub(crate) fn write_output(out: Option<PathBuf>, bytes: &[u8]) -> Result<(), Failure> {
    match out {
        Some(path) => fs::write(&path, bytes)
            .map_err(|_| Failure::Usage(format!("cannot write output: {}", path.display()))),
        None => {
            use std::io::Write as _;
            std::io::stdout()
                .write_all(bytes)
                .map_err(|_| Failure::Ethos(EthosError::internal("stdout write failed")))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::assembly::{assemble_document, finalize_warnings};
    use crate::cmd::doc::table_candidate_probe_report_bytes;
    use ethos_core::codes::WarningCode;
    use ethos_core::config::ParseConfig;
    use ethos_core::geom::QRect;
    use ethos_core::model::{Element, ElementType, Page, Span, Warning};
    use ethos_core::traits::{BackendManifest, Extraction};
    use std::collections::HashSet;

    fn test_span(id: &str, warning_refs: Vec<&str>) -> Span {
        Span {
            id: id.to_string(),
            page: "p0001".to_string(),
            bbox: QRect::new(0, 0, 100, 100).unwrap(),
            origin_locator: None,
            text: "text".to_string(),
            font_id: None,
            font_size_q: Some(1200),
            char_start: None,
            char_end: None,
            warning_refs: warning_refs.into_iter().map(str::to_string).collect(),
        }
    }

    fn test_element(id: &str, warning_refs: Vec<&str>) -> Element {
        Element {
            id: id.to_string(),
            element_type: ElementType::TextBlock,
            page: "p0001".to_string(),
            bbox: QRect::new(0, 0, 100, 100).unwrap(),
            text: Some("text".to_string()),
            heading_level: None,
            table_ref: None,
            region_ref: None,
            confidence: None,
            span_refs: Vec::new(),
            warning_refs: warning_refs.into_iter().map(str::to_string).collect(),
        }
    }

    fn test_warning(
        id: &str,
        code: WarningCode,
        message: &str,
        element_ref: Option<&str>,
        span_ref: Option<&str>,
    ) -> Warning {
        Warning {
            id: id.to_string(),
            code,
            message: message.to_string(),
            page: Some("p0001".to_string()),
            element_ref: element_ref.map(str::to_string),
            span_ref: span_ref.map(str::to_string),
            region_ref: None,
        }
    }

    fn test_backend_manifest() -> BackendManifest {
        BackendManifest {
            id: "pdfium".to_string(),
            phase: 1,
            version: "test".to_string(),
            platform_sha256: "0".repeat(64),
        }
    }

    fn grid_span(id: &str, x0: i64, y0: i64, x1: i64, y1: i64, text: &str) -> Span {
        Span {
            id: id.to_string(),
            page: "p0001".to_string(),
            bbox: QRect::new(x0, y0, x1, y1).unwrap(),
            origin_locator: None,
            text: text.to_string(),
            font_id: None,
            font_size_q: Some(1200),
            char_start: None,
            char_end: None,
            warning_refs: vec![],
        }
    }

    #[test]
    fn error_envelope_is_valid_json_for_control_characters() {
        let err = EthosError::new(
            ErrorCode::InternalError,
            "loader said: line one\nline two\t\"quoted\" \\ \u{0007}",
        );
        let bytes = error_envelope_bytes(&err).unwrap();
        let value: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
        assert_eq!(value["error"]["code"], "internal_error");
        assert_eq!(value["error"]["message"], err.message);
    }

    #[test]
    fn assembles_extraction_into_self_consistent_document() {
        let extraction = Extraction {
            pages: vec![Page {
                id: "p0001".to_string(),
                index: 1,
                width: 1000,
                height: 1000,
                rotation: 0,
            }],
            spans: vec![
                Span {
                    id: "s000001".to_string(),
                    page: "p0001".to_string(),
                    bbox: QRect::new(0, 0, 100, 100).unwrap(),
                    origin_locator: None,
                    text: "Hello".to_string(),
                    font_id: None,
                    font_size_q: Some(1200),
                    char_start: None,
                    char_end: None,
                    warning_refs: vec![],
                },
                Span {
                    id: "s000002".to_string(),
                    page: "p0001".to_string(),
                    bbox: QRect::new(120, 0, 220, 100).unwrap(),
                    origin_locator: None,
                    text: "Ethos".to_string(),
                    font_id: None,
                    font_size_q: Some(1200),
                    char_start: None,
                    char_end: None,
                    warning_refs: vec![],
                },
                Span {
                    id: "s000003".to_string(),
                    page: "p0001".to_string(),
                    bbox: QRect::new(0, 300, 100, 400).unwrap(),
                    origin_locator: None,
                    text: "Again".to_string(),
                    font_id: None,
                    font_size_q: Some(1200),
                    char_start: None,
                    char_end: None,
                    warning_refs: vec![],
                },
            ],
            regions: vec![],
            warnings: vec![],
        };
        let doc = assemble_document(
            b"%PDF-1.7\n",
            &ParseConfig::default(),
            extraction,
            test_backend_manifest(),
            true,
        )
        .unwrap();
        doc.verify_integrity().unwrap();
        assert_eq!(doc.payload.elements.len(), 1);
        assert_eq!(
            doc.payload.elements[0].text.as_deref(),
            Some("Hello Ethos Again")
        );
        assert_eq!(doc.payload.spans[0].char_start, Some(0));
        assert_eq!(doc.payload.spans[0].char_end, Some(5));
        assert_eq!(doc.payload.spans[1].char_start, Some(6));
        assert_eq!(doc.payload.spans[1].char_end, Some(11));
        assert_eq!(doc.payload.spans[2].char_start, Some(12));
        assert_eq!(doc.payload.spans[2].char_end, Some(17));
    }

    #[test]
    fn table_candidate_probe_report_detects_regular_grid_without_mutating_document() {
        let extraction = Extraction {
            pages: vec![Page {
                id: "p0001".to_string(),
                index: 1,
                width: 5000,
                height: 5000,
                rotation: 0,
            }],
            spans: vec![
                grid_span("s000006", 1_000, 2_000, 1_600, 2_400, "12"),
                grid_span("s000001", 0, 0, 600, 400, "Name"),
                grid_span("s000004", 1_000, 1_000, 1_600, 1_400, "10"),
                grid_span("s000003", 0, 1_000, 600, 1_400, "Alpha"),
                grid_span("s000002", 1_000, 0, 1_600, 400, "Score"),
                grid_span("s000005", 0, 2_000, 600, 2_400, "Beta"),
            ],
            regions: vec![],
            warnings: vec![],
        };
        let doc = assemble_document(
            b"%PDF-1.7\n",
            &ParseConfig::default(),
            extraction,
            test_backend_manifest(),
            false,
        )
        .unwrap();

        assert!(doc.payload.tables.is_empty());

        let bytes = table_candidate_probe_report_bytes(&doc).unwrap();
        let value: serde_json::Value = serde_json::from_slice(&bytes).unwrap();

        assert_eq!(value["schema_version"], ethos_core::SCHEMA_VERSION);
        assert_eq!(value["document_fingerprint"], doc.fingerprint);
        assert_eq!(value["summary"]["tables_total"], 1);
        assert_eq!(value["tables"][0]["table"]["id"], "t0001");
        assert_eq!(value["tables"][0]["table"]["n_rows"], 3);
        assert_eq!(value["tables"][0]["table"]["n_cols"], 2);
        assert_eq!(
            value["tables"][0]["table"]["cells"][0]["span_refs"],
            serde_json::json!(["s000001"])
        );
        assert_eq!(
            value["tables"][0]["markdown"],
            "| Name | Score |\n| --- | --- |\n| Alpha | 10 |\n| Beta | 12 |\n"
        );
        assert!(doc.payload.tables.is_empty());
    }

    #[test]
    fn final_warning_ids_do_not_collide_between_extraction_and_layout() {
        let mut spans = vec![test_span("s000001", vec!["w0001"])];
        let mut regions = Vec::new();
        let mut elements = vec![
            test_element("e000001", vec!["w0001"]),
            test_element("e000002", vec!["w0002"]),
        ];
        let extraction_warnings = vec![test_warning(
            "w0001",
            WarningCode::PartialParse,
            "partial parse completed",
            None,
            Some("s000001"),
        )];
        let layout_warnings = vec![
            test_warning(
                "w0001",
                WarningCode::LowConfidenceReadingOrder,
                "reading order confidence below threshold",
                Some("e000001"),
                None,
            ),
            test_warning(
                "w0002",
                WarningCode::UnsupportedAnnotation,
                "unsupported annotation ignored",
                Some("e000002"),
                None,
            ),
        ];

        let (security_warnings, parser_warnings) = finalize_warnings(
            &mut spans,
            &mut regions,
            &mut elements,
            extraction_warnings,
            layout_warnings,
        )
        .unwrap();

        assert_eq!(
            parser_warnings
                .iter()
                .map(|w| w.id.as_str())
                .collect::<Vec<_>>(),
            vec!["w0001", "w0002"]
        );
        assert_eq!(
            parser_warnings.iter().map(|w| w.code).collect::<Vec<_>>(),
            vec![
                WarningCode::LowConfidenceReadingOrder,
                WarningCode::PartialParse,
            ]
        );
        assert_eq!(
            security_warnings
                .iter()
                .map(|w| w.id.as_str())
                .collect::<Vec<_>>(),
            vec!["w0003"]
        );

        let ids: Vec<_> = security_warnings
            .iter()
            .chain(parser_warnings.iter())
            .map(|w| w.id.as_str())
            .collect();
        let unique_ids: HashSet<_> = ids.iter().copied().collect();
        assert_eq!(unique_ids.len(), ids.len());
        assert_eq!(spans[0].warning_refs, vec!["w0002".to_string()]);
        assert_eq!(elements[0].warning_refs, vec!["w0001".to_string()]);
        assert_eq!(elements[1].warning_refs, vec!["w0003".to_string()]);
    }
}
