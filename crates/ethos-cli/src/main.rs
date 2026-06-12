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

use std::collections::{HashMap, HashSet};
use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;
use std::process::{Command as ProcessCommand, ExitCode, ExitStatus, Output, Stdio};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use clap::{Args, Parser, Subcommand, ValueEnum};
use ethos_core::config::{PageSelection, ParseConfig};
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::fingerprint::{is_fingerprint_form, source_fingerprint, FingerprintManifest};
use ethos_core::ids::warning_id;
use ethos_core::model::{
    CoordinateSystem, Document, Element, ParserInfo, Payload, ProfileRef, Region, SourceInfo, Span,
    Warning,
};
use ethos_core::traits::{BackendManifest, EthosPdfBackend as _, Extraction, LayoutEngine as _};
use ethos_core::verify_types::{ClaimKind, VerificationConfig};
use ethos_grounding_opendataloader_json::OdlJsonSource;
use ethos_verify::CitationInput;

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
    Fingerprint(FingerprintArgs),
    /// Internal killable PDFium worker. Not a public CLI surface.
    #[command(name = "__pdfium-worker", hide = true)]
    PdfiumWorker(PdfiumWorkerArgs),
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
    /// Internal/test override for the parse timeout limit.
    #[arg(long, hide = true)]
    max_parse_ms: Option<u64>,
}

#[derive(Args)]
struct FingerprintArgs {
    /// Canonical document (`*.ethos.json`). PDF input is parsed under the deterministic profile.
    input: PathBuf,
    /// Internal/test override for the parse timeout limit.
    #[arg(long, hide = true)]
    max_parse_ms: Option<u64>,
}

#[derive(Args)]
struct PdfiumWorkerArgs {
    /// Input PDF.
    input: PathBuf,
    /// Page selection, e.g. `1-5,9` (1-based, inclusive; merged canonically).
    #[arg(long)]
    pages: Option<String>,
    /// Include volatile runtime diagnostics.
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
    /// Citations file (JSON). Accepts either an array of claims or
    /// {"document_fingerprint": "...", "claims": [...]}.
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
        } => doc_parse(args),
        Command::Rag {
            command: RagCommand::Chunk(args),
        } => rag_chunk(args),
        Command::Verify(args) => verify(args),
        Command::Fingerprint(args) => fingerprint(args),
        Command::PdfiumWorker(args) => pdfium_worker(args),
    }
}

fn read_file(path: &PathBuf) -> Result<Vec<u8>, Failure> {
    fs::read(path).map_err(|_| Failure::Usage(format!("cannot read input: {}", path.display())))
}

fn ensure_file_within_limit(path: &PathBuf, max_bytes: u64) -> Result<(), Failure> {
    let metadata = fs::metadata(path)
        .map_err(|_| Failure::Usage(format!("cannot read input: {}", path.display())))?;
    if metadata.len() > max_bytes {
        return Err(
            EthosError::new(ErrorCode::FileTooLarge, "input exceeds max_file_bytes").into(),
        );
    }
    Ok(())
}

fn read_file_limited(path: &PathBuf, max_bytes: u64) -> Result<Vec<u8>, Failure> {
    ensure_file_within_limit(path, max_bytes)?;
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
    let config = parse_config(args.pages.as_deref(), args.max_parse_ms)?;
    ensure_file_within_limit(&args.input, config.limits.max_file_bytes)?;
    let doc = parse_pdf_with_worker(
        &args.input,
        args.pages.as_deref(),
        &config,
        args.diagnostics,
    )?;
    write_document(args.format, args.out, &doc)
}

fn parse_config(pages: Option<&str>, max_parse_ms: Option<u64>) -> Result<ParseConfig, Failure> {
    let pages = match pages {
        Some(spec) => {
            PageSelection::parse(spec).map_err(|e| Failure::Usage(format!("--pages: {e}")))?
        }
        None => PageSelection::All,
    };
    let mut config = ParseConfig {
        pages,
        ..Default::default()
    };
    if let Some(max_parse_ms) = max_parse_ms {
        if max_parse_ms == 0 {
            return Err(Failure::Usage(
                "--max-parse-ms must be greater than zero".to_string(),
            ));
        }
        config.limits.max_parse_ms = max_parse_ms;
    }
    Ok(config)
}

fn pdfium_worker(args: PdfiumWorkerArgs) -> Result<(), Failure> {
    maybe_sleep_for_worker_timeout_test();
    maybe_exit_for_worker_failure_diagnostics_test();
    let config = parse_config(args.pages.as_deref(), None)?;
    let pdf_bytes = read_file_limited(&args.input, config.limits.max_file_bytes)?;
    let backend = ethos_pdf::PdfiumBackend::default();
    let extraction = backend
        .extract(&pdf_bytes, &config)
        .map_err(classify_worker_extract_error)?;
    let doc = assemble_document(
        &pdf_bytes,
        &config,
        extraction,
        backend.manifest(),
        args.diagnostics,
    )?;
    write_document(Format::Json, None, &doc)
}

fn classify_worker_extract_error(error: EthosError) -> Failure {
    if error.code == ErrorCode::PageLimitExceeded
        && error.message == "page selection out of document range"
    {
        Failure::Usage("--pages: page selection out of document range".to_string())
    } else {
        Failure::Ethos(error)
    }
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
    let citations_bytes = read_file(&args.citations)?;
    let citations: CitationInput = serde_json::from_slice(&citations_bytes).map_err(|_| {
        Failure::Usage("citations file does not match the alpha citation input shape".to_string())
    })?;

    let config: VerificationConfig = match &args.config {
        Some(path) => serde_json::from_slice(&read_file(path)?).map_err(|_| {
            Failure::Usage("verification config does not match the schema".to_string())
        })?,
        None => VerificationConfig::default_v1(),
    };
    validate_verification_config(&config)?;
    validate_citation_input(&citations, &config)?;
    let config_value =
        serde_json::to_value(&config).map_err(|e| EthosError::internal(e.to_string()))?;
    let config_sha256 =
        ethos_core::c14n::sha256_hex(&config_value).map_err(|e| EthosError::internal(e.message))?;

    let report = match args.grounding.as_deref() {
        None => {
            let doc = read_document(&args.input)?;
            ethos_verify::verify_claims(&doc, citations, &config, config_sha256)
        }
        Some("opendataloader-json") => {
            let bytes = read_file(&args.input)?;
            let text = String::from_utf8(bytes)
                .map_err(|_| Failure::Usage("grounding input is not UTF-8".to_string()))?;
            let source = OdlJsonSource::from_json_str(&text)
                .map_err(|e| Failure::Usage(format!("opendataloader-json adapter: {e}")))?;
            ethos_verify::verify_claims(&source, citations, &config, config_sha256)
        }
        Some(other) => {
            return Err(Failure::Usage(format!(
                "unknown grounding adapter '{other}' (available: opendataloader-json)"
            )));
        }
    };

    let value = serde_json::to_value(&report).map_err(|e| EthosError::internal(e.to_string()))?;
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    write_output(args.out, &bytes)
}

fn validate_citation_input(
    citations: &CitationInput,
    config: &VerificationConfig,
) -> Result<(), Failure> {
    let claims = citations.claims();
    if claims.is_empty() {
        return Err(Failure::Usage(
            "citations file must contain at least one claim".to_string(),
        ));
    }
    if claims.len() > config.limits.max_checks as usize {
        return Err(Failure::Usage(format!(
            "citations file exceeds max_checks ({})",
            config.limits.max_checks
        )));
    }
    if citations
        .document_fingerprint()
        .is_some_and(|fingerprint| !is_fingerprint_form(fingerprint))
    {
        return Err(Failure::Usage(
            "citations document_fingerprint must be sha256:<64 lowercase hex chars>".to_string(),
        ));
    }
    for (idx, claim) in claims.iter().enumerate() {
        if !claim.citation.has_locator() {
            return Err(Failure::Usage(format!(
                "claim {} citation must contain at least one locator",
                idx + 1
            )));
        }
        if matches!(
            claim.kind,
            ClaimKind::Quote | ClaimKind::Value | ClaimKind::TableCell
        ) && claim
            .text
            .as_ref()
            .is_none_or(|text| text.trim().is_empty())
        {
            return Err(Failure::Usage(format!(
                "claim {} text must be non-empty for quote, value, and table_cell",
                idx + 1
            )));
        }
    }
    Ok(())
}

fn validate_verification_config(config: &VerificationConfig) -> Result<(), Failure> {
    if config.schema_version != ethos_core::SCHEMA_VERSION {
        return Err(Failure::Usage(format!(
            "verification config schema_version must be {}",
            ethos_core::SCHEMA_VERSION
        )));
    }
    if config.claim_kinds.is_empty() {
        return Err(Failure::Usage(
            "verification config claim_kinds must not be empty".to_string(),
        ));
    }
    let mut seen = HashSet::new();
    for kind in &config.claim_kinds {
        if *kind == ClaimKind::Other {
            return Err(Failure::Usage(
                "verification config claim_kinds must not include other".to_string(),
            ));
        }
        if !seen.insert(*kind) {
            return Err(Failure::Usage(
                "verification config claim_kinds must be unique".to_string(),
            ));
        }
    }
    if config
        .matching
        .bbox_containment_tolerance_q
        .is_some_and(|tolerance| tolerance < 0)
    {
        return Err(Failure::Usage(
            "verification config bbox_containment_tolerance_q must be non-negative".to_string(),
        ));
    }
    if config.limits.max_checks == 0 {
        return Err(Failure::Usage(
            "verification config max_checks must be at least 1".to_string(),
        ));
    }
    Ok(())
}

fn fingerprint(args: FingerprintArgs) -> Result<(), Failure> {
    let input = args.input;
    if input
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case("pdf"))
    {
        let config = parse_config(None, args.max_parse_ms)?;
        ensure_file_within_limit(&input, config.limits.max_file_bytes)?;
        let doc = parse_pdf_with_worker(&input, None, &config, false)?;
        println!("{}", doc.fingerprint);
        return Ok(());
    }
    let doc = read_document(&input)?;
    println!("{}", doc.fingerprint);
    Ok(())
}

fn parse_pdf_with_worker(
    input: &PathBuf,
    pages: Option<&str>,
    config: &ParseConfig,
    diagnostics: bool,
) -> Result<Document, Failure> {
    let mut command = ProcessCommand::new(
        std::env::current_exe()
            .map_err(|_| EthosError::internal("failed to locate current executable"))?,
    );
    command.arg("__pdfium-worker").arg(input);
    if let Some(pages) = pages {
        command.arg("--pages").arg(pages);
    }
    if diagnostics {
        command.arg("--diagnostics");
    }

    let output =
        run_worker_with_timeout(command, Duration::from_millis(config.limits.max_parse_ms))?;
    if output.status.success() {
        let doc: Document = serde_json::from_slice(&output.stdout).map_err(|_| {
            EthosError::internal("pdfium worker returned an invalid canonical document")
        })?;
        doc.verify_integrity()?;
        return Ok(doc);
    }

    if output.status.code() == Some(EXIT_USAGE as i32) {
        return Err(Failure::Usage(worker_usage_message(&output.stderr)));
    }
    if let Some(error) = worker_ethos_error(&output.stderr) {
        return Err(error.into());
    }
    let error = EthosError::internal("pdfium worker failed");
    if diagnostics {
        return Err(Failure::EthosWithDiagnostics {
            error,
            diagnostics: worker_failure_diagnostics(&output),
        });
    }
    Err(error.into())
}

fn run_worker_with_timeout(
    mut command: ProcessCommand,
    timeout: Duration,
) -> Result<Output, Failure> {
    command
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command
        .spawn()
        .map_err(|_| EthosError::internal("failed to spawn pdfium worker"))?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| EthosError::internal("pdfium worker stdout unavailable"))?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| EthosError::internal("pdfium worker stderr unavailable"))?;
    let stdout_handle = thread::spawn(move || read_pipe(stdout));
    let stderr_handle = thread::spawn(move || read_pipe(stderr));

    let start = Instant::now();
    loop {
        if let Some(status) = child
            .try_wait()
            .map_err(|_| EthosError::internal("pdfium worker wait failed"))?
        {
            return collect_worker_output(status, stdout_handle, stderr_handle);
        }
        if start.elapsed() >= timeout {
            if let Some(status) = child
                .try_wait()
                .map_err(|_| EthosError::internal("pdfium worker wait failed"))?
            {
                return collect_worker_output(status, stdout_handle, stderr_handle);
            }
            let _ = child.kill();
            let _ = child.wait();
            let _ = join_reader(stdout_handle);
            let _ = join_reader(stderr_handle);
            return Err(
                EthosError::new(ErrorCode::ParseTimeout, "parse exceeded max_parse_ms").into(),
            );
        }

        let remaining = timeout.saturating_sub(start.elapsed());
        thread::sleep(remaining.min(Duration::from_millis(10)));
    }
}

fn read_pipe<R: Read>(mut pipe: R) -> io::Result<Vec<u8>> {
    let mut bytes = Vec::new();
    pipe.read_to_end(&mut bytes)?;
    Ok(bytes)
}

fn collect_worker_output(
    status: ExitStatus,
    stdout_handle: JoinHandle<io::Result<Vec<u8>>>,
    stderr_handle: JoinHandle<io::Result<Vec<u8>>>,
) -> Result<Output, Failure> {
    Ok(Output {
        status,
        stdout: join_reader(stdout_handle)?,
        stderr: join_reader(stderr_handle)?,
    })
}

fn join_reader(handle: JoinHandle<io::Result<Vec<u8>>>) -> Result<Vec<u8>, Failure> {
    handle
        .join()
        .map_err(|_| EthosError::internal("pdfium worker pipe reader failed"))?
        .map_err(|_| EthosError::internal("pdfium worker pipe read failed").into())
}

fn worker_usage_message(stderr: &[u8]) -> String {
    let raw = String::from_utf8_lossy(stderr);
    let trimmed = raw.trim();
    trimmed
        .strip_prefix("error (usage): ")
        .unwrap_or(trimmed)
        .to_string()
}

fn worker_ethos_error(stderr: &[u8]) -> Option<EthosError> {
    let value: serde_json::Value = serde_json::from_slice(stderr).ok()?;
    let error = value.get("error")?;
    let code: ErrorCode = serde_json::from_value(error.get("code")?.clone()).ok()?;
    let message = error.get("message")?.as_str()?;
    Some(EthosError::new(code, message))
}

fn worker_failure_diagnostics(output: &Output) -> serde_json::Value {
    let mut worker = serde_json::Map::new();
    if let Some(code) = output.status.code() {
        worker.insert("exit_code".to_string(), serde_json::json!(code));
    }
    #[cfg(unix)]
    {
        use std::os::unix::process::ExitStatusExt as _;

        if let Some(signal) = output.status.signal() {
            worker.insert("signal".to_string(), serde_json::json!(signal));
        }
    }
    if !output.stderr.is_empty() {
        worker.insert(
            "stderr".to_string(),
            serde_json::Value::String(String::from_utf8_lossy(&output.stderr).to_string()),
        );
    }
    serde_json::json!({
        "pdfium_worker": serde_json::Value::Object(worker),
    })
}

#[cfg(debug_assertions)]
fn maybe_sleep_for_worker_timeout_test() {
    if let Ok(raw) = std::env::var("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_SLEEP_MS") {
        if let Ok(ms) = raw.parse::<u64>() {
            thread::sleep(Duration::from_millis(ms));
        }
    }
}

#[cfg(not(debug_assertions))]
fn maybe_sleep_for_worker_timeout_test() {}

#[cfg(debug_assertions)]
fn maybe_exit_for_worker_failure_diagnostics_test() {
    if let Ok(stderr) = std::env::var("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_STDERR") {
        eprint!("{stderr}");
        let code = std::env::var("ETHOS_INTERNAL_TEST_PDFIUM_WORKER_EXIT_CODE")
            .ok()
            .and_then(|raw| raw.parse::<i32>().ok())
            .unwrap_or(101);
        std::process::exit(code);
    }
}

#[cfg(not(debug_assertions))]
fn maybe_exit_for_worker_failure_diagnostics_test() {}

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
    let mut elements = layout.elements;
    let mut regions = extraction.regions;
    let (security_warnings, parser_warnings) = finalize_warnings(
        &mut spans,
        &mut regions,
        &mut elements,
        extraction.warnings,
        layout.warnings,
    )?;

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
        regions,
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

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
enum WarningOrigin {
    Extraction,
    Layout,
}

struct PendingWarning {
    origin: WarningOrigin,
    source_index: usize,
    original_id: String,
    warning: Warning,
}

fn finalize_warnings(
    spans: &mut [Span],
    regions: &mut [Region],
    elements: &mut [Element],
    extraction_warnings: Vec<Warning>,
    layout_warnings: Vec<Warning>,
) -> Result<(Vec<Warning>, Vec<Warning>), EthosError> {
    let mut pending = Vec::with_capacity(extraction_warnings.len() + layout_warnings.len());
    for (source_index, warning) in extraction_warnings.into_iter().enumerate() {
        pending.push(PendingWarning {
            origin: WarningOrigin::Extraction,
            source_index,
            original_id: warning.id.clone(),
            warning,
        });
    }
    for (source_index, warning) in layout_warnings.into_iter().enumerate() {
        pending.push(PendingWarning {
            origin: WarningOrigin::Layout,
            source_index,
            original_id: warning.id.clone(),
            warning,
        });
    }

    pending.sort_by(|a, b| {
        warning_order(&a.warning, &b.warning)
            .then_with(|| a.origin.cmp(&b.origin))
            .then_with(|| a.source_index.cmp(&b.source_index))
    });

    let mut extraction_ids = HashMap::new();
    let mut layout_ids = HashMap::new();
    let mut security_warnings = Vec::new();
    let mut parser_warnings = Vec::new();

    for (index, pending_warning) in pending.into_iter().enumerate() {
        let ordinal =
            u32::try_from(index + 1).map_err(|_| EthosError::internal("warning id overflow"))?;
        let final_id = warning_id(ordinal)?;
        match pending_warning.origin {
            WarningOrigin::Extraction => {
                extraction_ids.insert(pending_warning.original_id, final_id.clone());
            }
            WarningOrigin::Layout => {
                layout_ids.insert(pending_warning.original_id, final_id.clone());
            }
        }

        let mut warning = pending_warning.warning;
        warning.id = final_id;
        if warning.code.is_security() {
            security_warnings.push(warning);
        } else {
            parser_warnings.push(warning);
        }
    }

    for span in spans {
        rewrite_warning_refs(&mut span.warning_refs, &extraction_ids, &layout_ids);
    }
    for region in regions {
        rewrite_warning_refs(&mut region.warning_refs, &extraction_ids, &layout_ids);
    }
    for element in elements {
        rewrite_warning_refs(&mut element.warning_refs, &layout_ids, &extraction_ids);
    }

    Ok((security_warnings, parser_warnings))
}

fn warning_order(a: &Warning, b: &Warning) -> std::cmp::Ordering {
    a.code
        .as_str()
        .cmp(b.code.as_str())
        .then_with(|| a.page.cmp(&b.page))
        .then_with(|| a.element_ref.cmp(&b.element_ref))
        .then_with(|| a.span_ref.cmp(&b.span_ref))
        .then_with(|| a.region_ref.cmp(&b.region_ref))
        .then_with(|| a.message.cmp(&b.message))
}

fn rewrite_warning_refs(
    warning_refs: &mut [String],
    primary_ids: &HashMap<String, String>,
    secondary_ids: &HashMap<String, String>,
) {
    for warning_ref in warning_refs {
        if let Some(final_id) = primary_ids
            .get(warning_ref)
            .or_else(|| secondary_ids.get(warning_ref))
        {
            *warning_ref = final_id.clone();
        }
    }
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
    use ethos_core::codes::WarningCode;
    use ethos_core::geom::QRect;
    use ethos_core::model::{ElementType, Page, Span};
    use ethos_core::traits::Extraction;

    fn test_span(id: &str, warning_refs: Vec<&str>) -> Span {
        Span {
            id: id.to_string(),
            page: "p0001".to_string(),
            bbox: QRect::new(0, 0, 100, 100).unwrap(),
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
