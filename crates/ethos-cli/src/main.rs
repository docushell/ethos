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

use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Args, Parser, Subcommand, ValueEnum};
use ethos_core::config::{PageSelection, ParseConfig};
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::model::Document;
use ethos_core::traits::EthosPdfBackend as _;
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
            // deterministic machine-readable error envelope on stderr
            eprintln!(
                "{{\"error\":{{\"code\":\"{}\",\"message\":\"{}\"}}}}",
                e.code.as_str(),
                e.message.replace('\\', "\\\\").replace('"', "\\\"")
            );
            ExitCode::from(e.code.exit_code() as u8)
        }
    }
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
    // config hash is live from the skeleton on: page selection is canonical-output identity
    let _config_sha256 = config.config_sha256()?;

    let pdf_bytes = read_file(&args.input)?;
    if pdf_bytes.len() as u64 > config.limits.max_file_bytes {
        return Err(
            EthosError::new(ErrorCode::FileTooLarge, "input exceeds max_file_bytes").into(),
        );
    }

    // Backend boundary (invariant 3). Fails with a stable code until WS-ENGINE lands.
    let backend = ethos_pdf::PdfiumBackend;
    let _extraction = backend.extract(&pdf_bytes, &config)?;

    // Unreachable until the engine exists; the assembly pipeline (extraction → layout →
    // payload → fingerprints → c14n output) is Milestone A/B lane work.
    Err(EthosError::internal("document assembly lands with the engine (WS-ENGINE)").into())
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
        // PDF path goes through the backend (stable failure until WS-ENGINE lands);
        // once the engine exists this becomes parse → fingerprint of the canonical output.
        let bytes = read_file(&input)?;
        let backend = ethos_pdf::PdfiumBackend;
        backend.page_count(&bytes)?;
        return Err(
            EthosError::internal("pdf fingerprinting lands with the engine (WS-ENGINE)").into(),
        );
    }
    let doc = read_document(&input)?;
    println!("{}", doc.fingerprint);
    Ok(())
}
