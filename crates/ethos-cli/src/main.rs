//! # `ethos` — CLI skeleton (Milestone A, WS-CONTRACTS weeks 3–4)
//!
//! Public command groups follow the public architecture: `ethos doc …`, `ethos rag …`,
//! `ethos verify …`, plus `ethos fingerprint` (PRD §9.1). Exit codes are the public
//! contract from docs/architecture.md: 0 success, 2 usage, 3–12 stable error codes.
//!
//! Skeleton status (honest): `doc parse` is wired through the backend boundary and fails
//! with a stable code until WS-ENGINE lands PDFium; `rag chunk` and `fingerprint` are
//! fully functional over canonical JSON; `verify` emits a schema-valid report with zero
//! checks (the check engine is the Milestone B alpha, WS-VERIFY-ALPHA).

use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Args, Parser, Subcommand, ValueEnum};
use ethos_core::config::{PageSelection, ParseConfig};
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::fingerprint::{source_fingerprint, FingerprintManifest};
use ethos_core::model::{
    CoordinateSystem, Document, Element, ParserInfo, Payload, ProfileRef, SourceInfo,
};
use ethos_core::traits::{BackendManifest, EthosPdfBackend as _, Extraction, LayoutEngine as _};
use ethos_core::verify_types::VerificationConfig;
use ethos_grounding_opendataloader_json::OdlJsonSource;

/// Usage-error exit code (also what clap uses).
const EXIT_USAGE: u8 = 2;

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
    Fingerprint {
        /// Canonical document (`*.ethos.json`). PDF input works once the engine lands.
        input: PathBuf,
    },
}

#[derive(Subcommand)]
enum DocCommand {
    /// Parse a PDF into the canonical document graph
    Parse(DocParseArgs),
}

#[derive(Args)]
struct DocParseArgs {
    /// Input PDF
    input: PathBuf,
    /// Output format
    #[arg(long, value_enum, default_value_t = Format::Json)]
    format: Format,
    /// Output path (file or directory)
    #[arg(long)]
    out: Option<PathBuf>,
    /// Page selection, e.g. `1-5,9` (1-based, inclusive; merged canonically).
    /// Enters config_sha256: a different range is a different canonical output.
    #[arg(long)]
    pages: Option<String>,
    /// Include volatile runtime diagnostics (off by default so outputs stay byte-identical)
    #[arg(long)]
    diagnostics: bool,
}

#[derive(Clone, Copy, ValueEnum)]
enum Format {
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
struct RagChunkArgs {
    /// Canonical document (`*.ethos.json`)
    input: PathBuf,
    /// Output path for chunks.jsonl (default: stdout)
    #[arg(long)]
    out: Option<PathBuf>,
}

#[derive(Args)]
struct VerifyArgs {
    /// Grounding input: canonical Ethos document, or foreign output with --grounding
    input: PathBuf,
    /// Citations file (JSON). NOTE (skeleton): accepted and validated, but checks land
    /// in Milestone B — the report carries zero checks until then.
    #[arg(long)]
    citations: PathBuf,
    /// Foreign grounding adapter id (e.g. `opendataloader-json`)
    #[arg(long)]
    grounding: Option<String>,
    /// Verification config (JSON); defaults to the pinned `default-v1`
    #[arg(long)]
    config: Option<PathBuf>,
    /// Output path for verification_report.json (default: stdout)
    #[arg(long)]
    out: Option<PathBuf>,
}

/// CLI failure: stable error code or usage error, rendered deterministically.
enum Failure {
    Ethos(EthosError),
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
    }
}

fn error_envelope_bytes(e: &EthosError) -> Result<Vec<u8>, ethos_core::c14n::C14nError> {
    let value = serde_json::json!({
        "error": {
            "code": e.code.as_str(),
            "message": e.message,
        }
    });
    let mut bytes = ethos_core::c14n::c14n_bytes(&value)?;
    bytes.push(b'\n');
    Ok(bytes)
}

fn write_error_envelope(e: &EthosError) {
    use std::io::Write as _;

    let bytes = error_envelope_bytes(e).expect("error envelope contains only canonical values");
    let _ = std::io::stderr().write_all(&bytes);
}

fn run(cli: Cli) -> Result<(), Failure> {
    match cli.command {
        Command::Doc {
            command: DocCommand::Parse(args),
        } => doc_parse(args),
        Command::Rag {
            command: RagCommand::Chunk(args),
        } => rag_chunk(args),
        Command::Verify(args) => verify(args),
        Command::Fingerprint { input } => fingerprint(input),
    }
}

fn read_file(path: &PathBuf) -> Result<Vec<u8>, Failure> {
    fs::read(path).map_err(|_| Failure::Usage(format!("cannot read input: {}", path.display())))
}

fn read_file_limited(path: &PathBuf, max_bytes: u64) -> Result<Vec<u8>, Failure> {
    let metadata = fs::metadata(path)
        .map_err(|_| Failure::Usage(format!("cannot read input: {}", path.display())))?;
    if metadata.len() > max_bytes {
        return Err(
            EthosError::new(ErrorCode::FileTooLarge, "input exceeds max_file_bytes").into(),
        );
    }

    let bytes = read_file(path)?;
    if bytes.len() as u64 > max_bytes {
        return Err(
            EthosError::new(ErrorCode::FileTooLarge, "input exceeds max_file_bytes").into(),
        );
    }
    Ok(bytes)
}

fn read_document(path: &PathBuf) -> Result<Document, Failure> {
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

fn write_output(out: Option<PathBuf>, bytes: &[u8]) -> Result<(), Failure> {
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

fn doc_parse(args: DocParseArgs) -> Result<(), Failure> {
    let pages = match &args.pages {
        Some(spec) => {
            PageSelection::parse(spec).map_err(|e| Failure::Usage(format!("--pages: {e}")))?
        }
        None => PageSelection::All,
    };
    let config = ParseConfig {
        pages,
        ..Default::default()
    };
    let pdf_bytes = read_file_limited(&args.input, config.limits.max_file_bytes)?;

    let backend = ethos_pdf::PdfiumBackend::default();
    let page_count = backend.page_count(&pdf_bytes)?;
    config
        .pages
        .validate_against(page_count)
        .map_err(|e| Failure::Usage(format!("--pages: {e}")))?;
    let extraction = backend.extract(&pdf_bytes, &config)?;
    let doc = assemble_document(
        &pdf_bytes,
        &config,
        extraction,
        backend.manifest(),
        args.diagnostics,
    )?;
    write_document(args.format, args.out, &doc)
}

fn rag_chunk(args: RagChunkArgs) -> Result<(), Failure> {
    let doc = read_document(&args.input)?;

    // warning id → code lookup for inherited chunk warnings
    let warning_code = |id: &str| -> Option<&'static str> {
        doc.payload
            .security_warnings
            .iter()
            .chain(doc.payload.parser_warnings.iter())
            .find(|w| w.id == id)
            .map(|w| w.code.as_str())
    };

    let mut out = Vec::with_capacity(4096);
    for chunk in &doc.payload.chunks {
        let mut record = serde_json::Map::new();
        record.insert(
            "schema_version".into(),
            serde_json::Value::String(doc.schema_version.clone()),
        );
        record.insert(
            "document_fingerprint".into(),
            serde_json::Value::String(doc.fingerprint.clone()),
        );
        record.insert(
            "source_fingerprint".into(),
            serde_json::Value::String(doc.source.fingerprint.clone()),
        );
        record.insert(
            "config_sha256".into(),
            serde_json::Value::String(doc.config_sha256.clone()),
        );
        record.insert("id".into(), serde_json::Value::String(chunk.id.clone()));
        record.insert("text".into(), serde_json::Value::String(chunk.text.clone()));
        record.insert(
            "element_refs".into(),
            serde_json::Value::Array(
                chunk
                    .element_refs
                    .iter()
                    .cloned()
                    .map(serde_json::Value::String)
                    .collect(),
            ),
        );
        record.insert(
            "page_refs".into(),
            serde_json::Value::Array(
                chunk
                    .page_refs
                    .iter()
                    .cloned()
                    .map(serde_json::Value::String)
                    .collect(),
            ),
        );
        record.insert(
            "bboxes".into(),
            serde_json::to_value(&chunk.bboxes).map_err(|e| EthosError::internal(e.to_string()))?,
        );
        record.insert(
            "token_estimate".into(),
            serde_json::to_value(&chunk.token_estimate)
                .map_err(|e| EthosError::internal(e.to_string()))?,
        );
        let warnings: Vec<serde_json::Value> = chunk
            .warning_refs
            .iter()
            .filter_map(|id| warning_code(id))
            .map(|c| serde_json::Value::String(c.to_string()))
            .collect();
        record.insert("warnings".into(), serde_json::Value::Array(warnings));

        let line = ethos_core::c14n::c14n_bytes(&serde_json::Value::Object(record))
            .map_err(|e| EthosError::internal(e.message))?;
        out.extend_from_slice(&line);
        out.push(b'\n');
    }
    write_output(args.out, &out)
}

fn verify(args: VerifyArgs) -> Result<(), Failure> {
    // citations must at least be valid JSON, even in the skeleton
    let citations_bytes = read_file(&args.citations)?;
    serde_json::from_slice::<serde_json::Value>(&citations_bytes)
        .map_err(|_| Failure::Usage("citations file is not valid JSON".to_string()))?;

    let config: VerificationConfig = match &args.config {
        Some(path) => serde_json::from_slice(&read_file(path)?).map_err(|_| {
            Failure::Usage("verification config does not match the schema".to_string())
        })?,
        None => VerificationConfig::default_v1(),
    };
    let config_value =
        serde_json::to_value(&config).map_err(|e| EthosError::internal(e.to_string()))?;
    let config_sha256 =
        ethos_core::c14n::sha256_hex(&config_value).map_err(|e| EthosError::internal(e.message))?;

    let report = match args.grounding.as_deref() {
        None => {
            let doc = read_document(&args.input)?;
            ethos_verify::verify_skeleton(&doc, &config, config_sha256)
        }
        Some("opendataloader-json") => {
            let bytes = read_file(&args.input)?;
            let text = String::from_utf8(bytes)
                .map_err(|_| Failure::Usage("grounding input is not UTF-8".to_string()))?;
            let source = OdlJsonSource::from_json_str(&text)
                .map_err(|e| Failure::Usage(format!("opendataloader-json adapter: {e}")))?;
            ethos_verify::verify_skeleton(&source, &config, config_sha256)
        }
        Some(other) => {
            return Err(Failure::Usage(format!(
                "unknown grounding adapter '{other}' (available: opendataloader-json)"
            )));
        }
    };

    eprintln!(
        "note: verify is a Milestone A skeleton — the report contains zero checks; \
         the check engine lands as the Milestone B alpha (WS-VERIFY-ALPHA)"
    );

    let value = serde_json::to_value(&report).map_err(|e| EthosError::internal(e.to_string()))?;
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    write_output(args.out, &bytes)
}

fn fingerprint(input: PathBuf) -> Result<(), Failure> {
    if input
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case("pdf"))
    {
        let config = ParseConfig::default();
        let bytes = read_file_limited(&input, config.limits.max_file_bytes)?;
        let backend = ethos_pdf::PdfiumBackend::default();
        let extraction = backend.extract(&bytes, &config)?;
        let doc = assemble_document(&bytes, &config, extraction, backend.manifest(), false);
        println!("{}", doc?.fingerprint);
        return Ok(());
    }
    let doc = read_document(&input)?;
    println!("{}", doc.fingerprint);
    Ok(())
}

fn assemble_document(
    source_bytes: &[u8],
    config: &ParseConfig,
    extraction: Extraction,
    backend_manifest: BackendManifest,
    include_diagnostics: bool,
) -> Result<Document, EthosError> {
    let layout = ethos_layout::BasicLayoutEngine.layout(&extraction)?;
    let mut spans = extraction.spans;
    assign_span_offsets(&layout.elements, &mut spans)?;
    let elements = layout.elements;
    let mut security_warnings = Vec::new();
    let mut parser_warnings = Vec::new();
    for warning in extraction.warnings.into_iter().chain(layout.warnings) {
        if warning.code.is_security() {
            security_warnings.push(warning);
        } else {
            parser_warnings.push(warning);
        }
    }

    let payload = Payload {
        coordinate_system: CoordinateSystem {
            origin: "top-left".to_string(),
            unit: "quantum".to_string(),
            quantum_per_point: 100,
        },
        pages: extraction.pages,
        elements,
        spans,
        tables: Vec::new(),
        chunks: Vec::new(),
        regions: extraction.regions,
        security_warnings,
        parser_warnings,
    };

    let payload_value =
        serde_json::to_value(&payload).map_err(|e| EthosError::internal(e.to_string()))?;
    let payload_sha256 = ethos_core::c14n::sha256_hex(&payload_value)
        .map_err(|e| EthosError::internal(e.message))?;
    let profile_sha256 = profile_sha256()?;
    let source_fingerprint = source_fingerprint(source_bytes);
    let config_sha256 = config.config_sha256()?;
    let manifest = FingerprintManifest {
        config_sha256: config_sha256.clone(),
        payload_sha256: payload_sha256.clone(),
        profile_id: ethos_core::PROFILE_ID.to_string(),
        profile_sha256: profile_sha256.clone(),
        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
        source_fingerprint: source_fingerprint.clone(),
    };
    let fingerprint = manifest
        .document_fingerprint()
        .map_err(|e| EthosError::internal(e.message))?;

    let diagnostics = if include_diagnostics {
        Some(serde_json::json!({
            "backend": backend_manifest,
            "surface": "ethos-cli",
        }))
    } else {
        None
    };

    Ok(Document {
        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
        parser: ParserInfo {
            name: "ethos".to_string(),
            version: env!("CARGO_PKG_VERSION").to_string(),
        },
        profile: ProfileRef {
            id: ethos_core::PROFILE_ID.to_string(),
            sha256: profile_sha256,
        },
        source: SourceInfo {
            fingerprint: source_fingerprint,
            bytes: source_bytes.len() as u64,
        },
        config_sha256,
        payload_sha256,
        fingerprint,
        payload,
        diagnostics,
    })
}

fn assign_span_offsets(
    elements: &[Element],
    spans: &mut [ethos_core::model::Span],
) -> Result<(), EthosError> {
    for span in spans.iter_mut() {
        span.char_start = None;
        span.char_end = None;
    }

    let span_indices: HashMap<String, usize> = spans
        .iter()
        .enumerate()
        .map(|(idx, span)| (span.id.clone(), idx))
        .collect();
    let mut assigned = HashSet::new();

    for element in elements {
        let Some(text) = element.text.as_deref() else {
            continue;
        };
        if element.span_refs.is_empty() {
            continue;
        }

        let mut char_cursor = 0u32;
        for (pos, span_id) in element.span_refs.iter().enumerate() {
            if !assigned.insert(span_id.clone()) {
                return Err(EthosError::internal(
                    "span is assigned to multiple elements",
                ));
            }
            if pos > 0 {
                char_cursor = char_cursor
                    .checked_add(1)
                    .ok_or_else(|| EthosError::internal("span offset overflow"))?;
            }

            let idx = *span_indices
                .get(span_id)
                .ok_or_else(|| EthosError::internal("element references an unknown span"))?;
            let span_text_chars = spans[idx].text.chars().count();
            let span_text_chars = u32::try_from(span_text_chars)
                .map_err(|_| EthosError::internal("span text length overflow"))?;
            spans[idx].char_start = Some(char_cursor);
            char_cursor = char_cursor
                .checked_add(span_text_chars)
                .ok_or_else(|| EthosError::internal("span offset overflow"))?;
            spans[idx].char_end = Some(char_cursor);
        }

        let text_chars = u32::try_from(text.chars().count())
            .map_err(|_| EthosError::internal("element text length overflow"))?;
        if char_cursor != text_chars {
            return Err(EthosError::internal("layout text/span offsets disagree"));
        }
    }

    Ok(())
}

fn profile_sha256() -> Result<String, EthosError> {
    let raw = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../profiles/ethos-deterministic-v1.json"
    ));
    let value: serde_json::Value =
        serde_json::from_str(raw).map_err(|e| EthosError::internal(e.to_string()))?;
    ethos_core::c14n::sha256_hex(&value).map_err(|e| EthosError::internal(e.message))
}

fn write_document(format: Format, out: Option<PathBuf>, doc: &Document) -> Result<(), Failure> {
    let mut bytes = match format {
        Format::Json => {
            let value =
                serde_json::to_value(doc).map_err(|e| EthosError::internal(e.to_string()))?;
            ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?
        }
        Format::Markdown => render_markdown(doc).into_bytes(),
        Format::Text => render_text(doc).into_bytes(),
    };
    bytes.push(b'\n');
    write_output(out, &bytes)
}

fn render_text(doc: &Document) -> String {
    doc.payload
        .elements
        .iter()
        .filter_map(|element| element.text.as_deref())
        .collect::<Vec<_>>()
        .join("\n\n")
}

fn render_markdown(doc: &Document) -> String {
    render_text(doc)
}

#[cfg(test)]
mod tests {
    use super::*;
    use ethos_core::geom::QRect;
    use ethos_core::model::{Page, Span};
    use ethos_core::traits::Extraction;

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
            BackendManifest {
                id: "pdfium".to_string(),
                phase: 1,
                version: "test".to_string(),
                platform_sha256: "0".repeat(64),
            },
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
}
