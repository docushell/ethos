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

//! # `ethos` — source-only pre-alpha CLI
//!
//! Current command groups are `ethos doc …`, `ethos rag …`, `ethos security …`,
//! `ethos verify …`, plus `ethos fingerprint`. Exit codes follow the contract from
//! docs/architecture.md: 0 success, 2 usage, 3–12 stable error codes.
//!
//! Current status (honest): `doc parse` is wired through the backend boundary; `rag chunk`,
//! `security report`, and `fingerprint` operate over canonical JSON; `verify` runs literal
//! quote/value, presence, and table-cell checks over native Ethos JSON and ODL-style JSON.

mod assembly;
mod cmd;
mod grounding;
mod worker;

use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use clap::{Args, Parser, Subcommand, ValueEnum};
use ethos_core::config::ParseConfig;
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::model::Document;

/// Usage-error exit code (also what clap uses).
pub(crate) const EXIT_USAGE: u8 = 2;
/// Verification completed, but the requested grounding gate did not pass.
pub(crate) const EXIT_UNGROUNDED: u8 = 1;
pub(crate) const INTERNAL_GEOMETRY_PROBE_ENV: &str = "ETHOS_INTERNAL_GEOMETRY_PROBE";
pub(crate) const INTERNAL_TABLE_CANDIDATE_PROBE_ENV: &str = "ETHOS_INTERNAL_TABLE_CANDIDATE_PROBE";
pub(crate) const INTERNAL_PDFIUM_LOAD_PROBE_ENV: &str = "ETHOS_INTERNAL_PDFIUM_LOAD_PROBE";

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
    /// Security report artifacts (ethos-security)
    Security {
        #[command(subcommand)]
        command: SecurityCommand,
    },
    /// Deterministic evidence anchoring
    Evidence {
        #[command(subcommand)]
        command: EvidenceCommand,
    },
    /// Citation evidence verification (ethos-verify)
    Verify(VerifyArgs),
    /// Validate and inspect parser-neutral Grounding JSON
    Grounding {
        #[command(subcommand)]
        command: GroundingCommand,
    },
    /// Verify many citation requests against one loaded grounding source
    VerifyBatch(VerifyBatchArgs),
    /// Render a deterministic human-readable proof report
    Report {
        #[command(subcommand)]
        command: ReportCommand,
    },
    /// Recompute and check a document fingerprint
    Fingerprint(FingerprintArgs),
    /// Diagnose local Ethos and caller-provided PDFium setup
    Doctor(DoctorArgs),
    /// Source-only pre-alpha crop descriptor for one native document element
    #[command(name = "crop_element")]
    CropElement(CropElementArgs),
    /// Internal killable PDFium worker. Not a public CLI surface.
    #[command(name = "__pdfium-worker", hide = true)]
    PdfiumWorker(PdfiumWorkerArgs),
    /// Internal PDFium geometry source probe. Not a public CLI surface.
    #[command(name = "__pdfium-geometry-probe", hide = true)]
    PdfiumGeometryProbe(PdfiumGeometryProbeArgs),
    /// Internal PDFium load probe. Not a public CLI surface.
    #[command(name = "__pdfium-load-probe", hide = true)]
    PdfiumLoadProbe,
    /// Internal deterministic table-candidate probe. Not a public CLI surface.
    #[command(name = "__table-candidate-probe", hide = true)]
    TableCandidateProbe(TableCandidateProbeArgs),
}

#[derive(Subcommand)]
enum DocCommand {
    /// Parse a PDF into the canonical document graph
    Parse(DocParseArgs),
}

#[derive(Subcommand)]
enum GroundingCommand {
    /// Validate Grounding JSON and optionally bind it to original PDF bytes
    Check(GroundingCheckArgs),
}

#[derive(Args)]
pub(crate) struct GroundingCheckArgs {
    /// Grounding JSON input.
    pub(crate) input: PathBuf,
    /// Optional original PDF whose bytes must match source.sha256.
    #[arg(long)]
    pub(crate) source_artifact: Option<PathBuf>,
    /// Output path for grounding-validation.json (default: stdout).
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
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
pub(crate) struct DoctorArgs {
    /// Fail if caller-provided PDFium is not configured and usable by Ethos.
    #[arg(long)]
    pub(crate) require_pdfium: bool,
}

#[derive(Args)]
pub(crate) struct CropElementArgs {
    /// Canonical document (`*.ethos.json`)
    pub(crate) input: PathBuf,
    /// Source-only crop_element request envelope
    #[arg(long)]
    pub(crate) request: PathBuf,
    /// Logical check id to bind into the descriptor
    #[arg(long, default_value = "v0001")]
    pub(crate) check_id: String,
    /// Directory for rendered crop descriptor and PNG artifacts
    #[arg(long)]
    pub(crate) crop_dir: Option<PathBuf>,
    /// Original PDF bytes for rendered crop production
    #[arg(long)]
    pub(crate) crop_source_pdf: Option<PathBuf>,
    /// Output path for crop descriptor JSON (default: stdout)
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
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

#[derive(Subcommand)]
enum SecurityCommand {
    /// Derive security_report.json from canonical document warnings
    Report(SecurityReportArgs),
}

#[derive(Subcommand)]
enum EvidenceCommand {
    /// Check caller-provided evidence refs against source evidence
    Anchor(EvidenceAnchorArgs),
}

#[derive(Subcommand)]
enum ReportCommand {
    /// Render a verification report as self-contained HTML
    Html(ReportHtmlArgs),
}

#[derive(Args)]
pub(crate) struct ReportHtmlArgs {
    /// Canonical verification report JSON.
    pub(crate) input: PathBuf,
    /// Destination HTML file.
    #[arg(long)]
    pub(crate) out: PathBuf,
    /// Safe relative prefix used only for existing crop references.
    #[arg(long)]
    pub(crate) crop_root: Option<String>,
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
pub(crate) struct SecurityReportArgs {
    /// Canonical document (`*.ethos.json`)
    pub(crate) input: PathBuf,
    /// Output path for security_report.json (default: stdout)
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
}

#[derive(Args)]
pub(crate) struct EvidenceAnchorArgs {
    /// Grounding input: canonical Ethos document, or foreign output with --grounding
    pub(crate) input: PathBuf,
    /// Evidence refs request JSON.
    #[arg(long)]
    pub(crate) evidence_refs: PathBuf,
    /// Grounding adapter id: ethos-json, ethos-grounding-json, or opendataloader-json.
    /// Omit to select the loader from the optional top-level `artifact_type`.
    #[arg(long)]
    pub(crate) grounding: Option<String>,
    /// Output path for evidence_anchor_report.json (default: stdout)
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
    /// Verification config (JSON); defaults to the pinned `default-v1`. A config setting
    /// `hardening` adds structural provenance, source-context echo, and evidence dispersion
    /// to the report (schema 1.1.0); see schemas/examples/verification-config.hardened.example.json
    #[arg(long)]
    pub(crate) config: Option<PathBuf>,
    /// Output path for verification_report.json (default: stdout)
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
    /// Output format. JSON is the canonical report; summary is a compact text view.
    #[arg(long, value_enum, default_value_t = VerifyOutputFormat::Json)]
    pub(crate) format: VerifyOutputFormat,
    /// Directory for crop descriptor artifacts. With --crop-source-pdf, also writes rendered PNG
    /// crops bound by descriptor hashes.
    #[arg(long)]
    pub(crate) crop_dir: Option<PathBuf>,
    /// Original PDF bytes for rendered crop production. The source fingerprint must match the
    /// native Ethos document source fingerprint.
    #[arg(long)]
    pub(crate) crop_source_pdf: Option<PathBuf>,
    /// Exit 1 after writing the report when any requested evidence is not grounded.
    #[arg(long)]
    pub(crate) fail_on_ungrounded: bool,
}

#[derive(Args)]
pub(crate) struct VerifyBatchArgs {
    /// Grounding input: canonical Ethos document, or foreign output with --grounding.
    pub(crate) input: PathBuf,
    /// NDJSON file containing one canonical citation input per non-empty line.
    #[arg(long)]
    pub(crate) citations_ndjson: PathBuf,
    /// Foreign grounding adapter id (e.g. `opendataloader-json`).
    #[arg(long)]
    pub(crate) grounding: Option<String>,
    /// Verification config (JSON); defaults to the pinned `default-v1`. A config setting
    /// `hardening` adds structural provenance, source-context echo, and evidence dispersion
    /// to each report (schema 1.1.0); see schemas/examples/verification-config.hardened.example.json.
    #[arg(long)]
    pub(crate) config: Option<PathBuf>,
    /// Output path for canonical verification-report NDJSON (default: stdout).
    #[arg(long)]
    pub(crate) out: Option<PathBuf>,
    /// Emit one canonical verification report over every request instead of NDJSON:
    /// claims concatenate in request order under a single attestation, so a consumer
    /// never folds per-request reports by hand — a hand-folded report inherits one
    /// batch's attestation and dispersion and misstates the rest. The output is
    /// byte-identical to one `verify` run over the concatenated claims, so the same
    /// rules bind: every request must name the same document_fingerprint or none may
    /// name one, and the merged claim total must satisfy the config's max_checks —
    /// pass a config raising it for large batches.
    #[arg(long)]
    pub(crate) merged: bool,
    /// Exit 1 after writing reports when any request is not fully grounded.
    #[arg(long)]
    pub(crate) fail_on_ungrounded: bool,
}

#[derive(Clone, Copy, ValueEnum)]
pub(crate) enum VerifyOutputFormat {
    Json,
    Summary,
}

/// CLI failure: stable error code or usage error, rendered deterministically.
pub(crate) enum Failure {
    Ethos(EthosError),
    EthosWithDiagnostics {
        error: EthosError,
        diagnostics: serde_json::Value,
    },
    Ungrounded,
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
        Err(Failure::Ungrounded) => ExitCode::from(EXIT_UNGROUNDED),
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
        Command::Security {
            command: SecurityCommand::Report(args),
        } => cmd::security::security_report(args),
        Command::Evidence {
            command: EvidenceCommand::Anchor(args),
        } => cmd::evidence::evidence_anchor(args),
        Command::Verify(args) => cmd::verify::verify(args),
        Command::Grounding {
            command: GroundingCommand::Check(args),
        } => cmd::grounding::check(args),
        Command::VerifyBatch(args) => cmd::verify::verify_batch(args),
        Command::Report {
            command: ReportCommand::Html(args),
        } => cmd::report::html(args),
        Command::Fingerprint(args) => cmd::doc::fingerprint(args),
        Command::Doctor(args) => cmd::doctor::doctor(args),
        Command::CropElement(args) => cmd::crop::crop_element(args),
        Command::PdfiumWorker(args) => cmd::doc::pdfium_worker(args),
        Command::PdfiumGeometryProbe(args) => cmd::doc::pdfium_geometry_probe(args),
        Command::PdfiumLoadProbe => cmd::doctor::pdfium_load_probe(),
        Command::TableCandidateProbe(args) => cmd::doc::table_candidate_probe(args),
    }
}

pub(crate) fn default_max_input_bytes() -> u64 {
    ParseConfig::default().limits.max_file_bytes
}

pub(crate) fn read_file(path: &Path) -> Result<Vec<u8>, Failure> {
    fs::read(path).map_err(|_| Failure::Usage(format!("cannot read input: {}", path.display())))
}

pub(crate) fn ensure_file_within_limit(path: &Path, max_bytes: u64) -> Result<(), Failure> {
    let metadata = fs::metadata(path)
        .map_err(|_| Failure::Usage(format!("cannot read input: {}", path.display())))?;
    if metadata.len() > max_bytes {
        return Err(
            EthosError::new(ErrorCode::FileTooLarge, "input exceeds max_file_bytes").into(),
        );
    }
    Ok(())
}

pub(crate) fn read_file_limited(path: &Path, max_bytes: u64) -> Result<Vec<u8>, Failure> {
    ensure_file_within_limit(path, max_bytes)?;
    let bytes = read_file(path)?;
    if bytes.len() as u64 > max_bytes {
        return Err(
            EthosError::new(ErrorCode::FileTooLarge, "input exceeds max_file_bytes").into(),
        );
    }
    Ok(bytes)
}

pub(crate) fn read_document(path: &Path) -> Result<Document, Failure> {
    let bytes = read_file_limited(path, default_max_input_bytes())?;
    let doc: Document = serde_json::from_slice(&bytes).map_err(|error| {
        Failure::Usage(format!(
            "input is not a canonical ethos document (schema urn:ethos:schema:document:1): {error}"
        ))
    })?;
    doc.verify_integrity().map_err(|error| {
        Failure::Usage(format!(
            "input document failed integrity check: {}",
            error.message
        ))
    })?;
    Ok(doc)
}

/// Write one output artifact.
///
/// Regular files (and paths that do not exist yet) are written atomically through a temporary
/// file in the same directory, so an interrupted write cannot leave a truncated artifact behind.
///
/// Anything that is *not* a regular file — a symlink, FIFO, or device node such as
/// `/dev/stdout` — is written through directly. Renaming over those destinations would replace
/// the inode instead of writing to it, which destroys the symlink or FIFO the caller named.
/// Atomicity is not available for those targets and was never claimed for them.
/// Serialize a verdict as a proof statement (`docs/proof-statement-v1.md`).
///
/// The single path from an Ethos verdict to bytes on disk. Every command that emits a
/// verdict goes through here, so the statement shape cannot drift between producers — the
/// same reason `ethos-core` owns one c14n implementation.
///
/// Representations are not verdicts and do not come through here: `ethos doc parse` and
/// `ethos rag chunk` stay bare (§1.5).
pub(crate) fn statement_json_bytes<P: serde::Serialize>(
    input: &Path,
    predicate: &str,
    payload: &P,
) -> Result<Vec<u8>, Failure> {
    let statement = ethos_core::statement::Statement::new(
        representation_subject(input)?,
        // subject[1] is omitted everywhere: the only source binding available is
        // producer-declared, and an in-toto subject is matched by digest (§1.4).
        None,
        ethos_core::statement::predicate_type(predicate, 1),
        payload,
    );
    let mut bytes = ethos_core::statement::statement_bytes(&statement)
        .map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    Ok(bytes)
}

/// `subject[0]`: the representation Ethos read, digested by the input file's bytes.
///
/// in-toto matches subjects by digest, so the value must be computable by a consumer
/// holding the same file. A document fingerprint would not be.
fn representation_subject(input: &Path) -> Result<ethos_core::statement::Subject, Failure> {
    let bytes = read_file_limited(input, default_max_input_bytes())?;
    let name = input
        .file_name()
        .map(|name| name.to_string_lossy().into_owned())
        .unwrap_or_default();
    Ok(ethos_core::statement::Subject::sha256(
        name,
        ethos_core::c14n::sha256_hex_bytes(&bytes),
    ))
}

pub(crate) fn write_output(out: Option<PathBuf>, bytes: &[u8]) -> Result<(), Failure> {
    use std::io::Write as _;

    let Some(path) = out else {
        return std::io::stdout()
            .write_all(bytes)
            .map_err(|_| Failure::Ethos(EthosError::internal("stdout write failed")));
    };

    let cannot_write = || Failure::Usage(format!("cannot write output: {}", path.display()));

    // `symlink_metadata` does not follow links, so a symlinked destination is correctly
    // classified as a symlink rather than as whatever it points at.
    let existing = fs::symlink_metadata(&path).ok();
    if existing
        .as_ref()
        .is_some_and(|metadata| !metadata.is_file())
    {
        return fs::write(&path, bytes).map_err(|_| cannot_write());
    }

    let parent = path
        .parent()
        .filter(|parent| !parent.as_os_str().is_empty())
        .unwrap_or(Path::new("."));
    let mut temporary = tempfile::NamedTempFile::new_in(parent).map_err(|_| cannot_write())?;
    temporary
        .write_all(bytes)
        .and_then(|_| temporary.as_file().sync_all())
        .map_err(|_| cannot_write())?;
    // NamedTempFile creates with mode 0600 and `persist` keeps it. Restore the mode a plain
    // `fs::write` would have produced: the existing file's mode when overwriting, otherwise the
    // usual 0644 default, so report consumers running as another user keep their read access.
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt as _;
        let mode = existing
            .as_ref()
            .map_or(0o644, |metadata| metadata.permissions().mode() & 0o777);
        temporary
            .as_file()
            .set_permissions(std::fs::Permissions::from_mode(mode))
            .map_err(|_| cannot_write())?;
    }
    temporary.persist(&path).map_err(|_| cannot_write())?;
    Ok(())
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
    fn write_output_replaces_a_regular_file_atomically() {
        let dir = tempfile::tempdir().expect("temp dir can be created");
        let path = dir.path().join("report.json");
        fs::write(&path, b"stale").expect("seed file can be written");

        assert!(
            write_output(Some(path.clone()), b"fresh").is_ok(),
            "regular file write failed"
        );

        assert_eq!(fs::read(&path).expect("output is readable"), b"fresh");
        let leftovers: Vec<_> = fs::read_dir(dir.path())
            .expect("temp dir is readable")
            .filter_map(|entry| entry.ok())
            .filter(|entry| entry.path() != path)
            .collect();
        assert!(
            leftovers.is_empty(),
            "atomic write left a temporary file behind"
        );
    }

    #[test]
    fn write_output_writes_through_a_symlink_instead_of_replacing_it() {
        // A rename() would swap the symlink for a regular file and never touch the target.
        let dir = tempfile::tempdir().expect("temp dir can be created");
        let target = dir.path().join("target.json");
        let link = dir.path().join("latest.json");
        fs::write(&target, b"stale").expect("target can be written");
        #[cfg(unix)]
        std::os::unix::fs::symlink(&target, &link).expect("symlink can be created");
        #[cfg(not(unix))]
        return;

        assert!(
            write_output(Some(link.clone()), b"fresh").is_ok(),
            "symlink write failed"
        );

        assert!(
            fs::symlink_metadata(&link)
                .expect("link still exists")
                .is_symlink(),
            "symlink destination was replaced by a regular file"
        );
        assert_eq!(
            fs::read(&target).expect("target is readable"),
            b"fresh",
            "write did not reach the symlink target"
        );
    }

    #[test]
    #[cfg(unix)]
    fn write_output_keeps_group_and_other_read_access() {
        use std::os::unix::fs::PermissionsExt as _;

        let dir = tempfile::tempdir().expect("temp dir can be created");

        // A path that does not exist yet gets the ordinary 0644 default, not the 0600 a bare
        // temporary file would carry.
        let created = dir.path().join("created.json");
        assert!(
            write_output(Some(created.clone()), b"{}").is_ok(),
            "new file write failed"
        );
        let mode = fs::metadata(&created)
            .expect("new file is readable")
            .permissions()
            .mode()
            & 0o777;
        assert_eq!(mode, 0o644, "new output file is not world-readable");

        // An existing file keeps whatever mode the operator gave it.
        let existing = dir.path().join("existing.json");
        fs::write(&existing, b"stale").expect("seed file can be written");
        fs::set_permissions(&existing, fs::Permissions::from_mode(0o664)).expect("mode can be set");
        assert!(
            write_output(Some(existing.clone()), b"{}").is_ok(),
            "existing file write failed"
        );
        let mode = fs::metadata(&existing)
            .expect("existing file is readable")
            .permissions()
            .mode()
            & 0o777;
        assert_eq!(mode, 0o664, "existing output file mode was not preserved");
    }

    #[test]
    #[cfg(unix)]
    fn write_output_accepts_a_character_device_destination() {
        // `--out /dev/null` and `--out /dev/stdout` cannot be written by rename: the parent
        // directory is not writable and the destination is not a regular file.
        assert!(
            write_output(Some(PathBuf::from("/dev/null")), b"{}").is_ok(),
            "character device destination was rejected"
        );
    }

    #[test]
    fn read_file_limited_rejects_oversized_file_before_read() {
        let file = tempfile::NamedTempFile::new().expect("temp file can be created");
        file.as_file()
            .set_len(4)
            .expect("temp file length can be set");

        let error = match read_file_limited(file.path(), 3) {
            Ok(_) => panic!("oversized file was accepted"),
            Err(error) => error,
        };

        match error {
            Failure::Ethos(error) => {
                assert_eq!(error.code, ErrorCode::FileTooLarge);
                assert_eq!(error.message, "input exceeds max_file_bytes");
            }
            _ => panic!("expected stable file_too_large failure"),
        }
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
    fn assembly_emits_regular_grid_table_candidates() {
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

        doc.verify_integrity().unwrap();
        assert_eq!(doc.payload.tables.len(), 1);
        let table = &doc.payload.tables[0];
        assert_eq!(table.id, "t0001");
        assert_eq!(table.page_refs, vec!["p0001"]);
        assert_eq!(table.n_rows, 3);
        assert_eq!(table.n_cols, 2);
        assert_eq!(table.header_rows, 1);
        assert_eq!(table.header_cols, 0);
        assert_eq!(table.cells.len(), 6);
        assert_eq!(table.cells[0].text, "Name");
        assert_eq!(table.cells[0].span_refs, vec!["s000001"]);
        assert_eq!(table.cells[5].text, "12");
        assert_eq!(table.cells[5].span_refs, vec!["s000006"]);

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
