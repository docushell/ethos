use std::path::PathBuf;

use ethos_core::config::{PageSelection, ParseConfig};
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::model::Document;
use ethos_core::traits::EthosPdfBackend as _;

use crate::assembly::assemble_document;
use crate::worker::{
    maybe_exit_for_worker_failure_diagnostics_test, maybe_fail_for_worker_memory_limit_test,
    maybe_sleep_for_worker_timeout_test, parse_pdf_with_worker,
};
use crate::{
    ensure_file_within_limit, read_document, read_file_limited, write_output, DocParseArgs,
    Failure, FingerprintArgs, Format, PdfiumGeometryProbeArgs, PdfiumWorkerArgs,
    TableCandidateProbeArgs, INTERNAL_GEOMETRY_PROBE_ENV, INTERNAL_TABLE_CANDIDATE_PROBE_ENV,
};

pub(crate) fn doc_parse(args: DocParseArgs) -> Result<(), Failure> {
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

pub(crate) fn pdfium_worker(args: PdfiumWorkerArgs) -> Result<(), Failure> {
    maybe_sleep_for_worker_timeout_test();
    maybe_exit_for_worker_failure_diagnostics_test();
    maybe_fail_for_worker_memory_limit_test()?;
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

pub(crate) fn pdfium_geometry_probe(args: PdfiumGeometryProbeArgs) -> Result<(), Failure> {
    if std::env::var(INTERNAL_GEOMETRY_PROBE_ENV).as_deref() != Ok("1") {
        return Err(Failure::Usage(format!(
            "__pdfium-geometry-probe requires {INTERNAL_GEOMETRY_PROBE_ENV}=1"
        )));
    }
    let config = parse_config(args.pages.as_deref(), None)?;
    let pdf_bytes = read_file_limited(&args.input, config.limits.max_file_bytes)?;
    let backend = ethos_pdf::PdfiumBackend::default();
    let report = backend
        .geometry_probe(&pdf_bytes, &config)
        .map_err(classify_worker_extract_error)?;
    let value = serde_json::to_value(&report).map_err(|e| EthosError::internal(e.to_string()))?;
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    write_output(None, &bytes)
}

pub(crate) fn table_candidate_probe(args: TableCandidateProbeArgs) -> Result<(), Failure> {
    if std::env::var(INTERNAL_TABLE_CANDIDATE_PROBE_ENV).as_deref() != Ok("1") {
        return Err(Failure::Usage(format!(
            "__table-candidate-probe requires {INTERNAL_TABLE_CANDIDATE_PROBE_ENV}=1"
        )));
    }
    let doc = read_document(&args.input)?;
    let bytes = table_candidate_probe_report_bytes(&doc)?;
    write_output(args.out, &bytes)
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

pub(crate) fn fingerprint(args: FingerprintArgs) -> Result<(), Failure> {
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

pub(crate) fn table_candidate_probe_report_bytes(doc: &Document) -> Result<Vec<u8>, EthosError> {
    let tables = ethos_tables::detect_document_regular_grid_candidates(
        doc,
        &ethos_tables::TableCandidateConfig::default(),
    )?;
    let table_reports: Vec<serde_json::Value> = tables
        .iter()
        .map(|table| {
            serde_json::json!({
                "table": table,
                "markdown": ethos_tables::render_markdown(table),
            })
        })
        .collect();
    let value = serde_json::json!({
        "schema_version": ethos_core::SCHEMA_VERSION,
        "document_fingerprint": doc.fingerprint,
        "summary": {
            "tables_total": table_reports.len(),
        },
        "tables": table_reports,
    });
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    Ok(bytes)
}
