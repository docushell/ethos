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

use std::path::PathBuf;

use ethos_core::config::{PageSelection, ParseConfig};
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::model::{Document, ElementType};
use ethos_core::traits::EthosPdfBackend as _;

use crate::assembly::assemble_document;
use crate::worker::{
    maybe_emit_worker_stdout_for_pipe_limit_test, maybe_exit_for_worker_failure_diagnostics_test,
    maybe_fail_for_worker_memory_limit_test, maybe_sleep_for_worker_timeout_test,
    parse_pdf_json_artifact_with_worker, parse_pdf_with_worker, sha256_hex,
    worker_json_artifact_header_bytes, WorkerJsonArtifact,
};
use crate::{
    ensure_file_within_limit, read_document, read_file_limited, write_output, DocParseArgs,
    Failure, FingerprintArgs, Format, PdfiumGeometryProbeArgs, PdfiumWorkerArgs,
    TableCandidateProbeArgs, INTERNAL_GEOMETRY_PROBE_ENV, INTERNAL_TABLE_CANDIDATE_PROBE_ENV,
};

pub(crate) fn doc_parse(args: DocParseArgs) -> Result<(), Failure> {
    let config = parse_config(args.pages.as_deref(), args.max_parse_ms)?;
    ensure_file_within_limit(&args.input, config.limits.max_file_bytes)?;
    if matches!(args.format, Format::Json) {
        let artifact = parse_pdf_json_artifact_with_worker(
            &args.input,
            args.pages.as_deref(),
            &config,
            args.diagnostics,
        )?;
        return write_json_artifact_output(args.out, &artifact);
    }
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
    maybe_emit_worker_stdout_for_pipe_limit_test();
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
    if let Some(json_out) = args.json_out {
        return write_json_artifact(&json_out, &doc);
    }
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
        let artifact = parse_pdf_json_artifact_with_worker(&input, None, &config, false)?;
        println!("{}", artifact.document_fingerprint());
        return Ok(());
    }
    let doc = read_document(&input)?;
    println!("{}", doc.fingerprint);
    Ok(())
}

fn write_document(format: Format, out: Option<PathBuf>, doc: &Document) -> Result<(), Failure> {
    let bytes = document_output_bytes(format, doc)?;
    write_output(out, &bytes)
}

fn write_json_artifact(path: &PathBuf, doc: &Document) -> Result<(), Failure> {
    doc.verify_integrity()?;
    let bytes = document_json_output_bytes(doc)?;
    let output_sha256 = sha256_hex(&bytes);
    std::fs::write(path, &bytes)
        .map_err(|_| EthosError::internal("pdfium worker failed to write JSON artifact"))?;
    let header = worker_json_artifact_header_bytes(
        &doc.fingerprint,
        &doc.payload_sha256,
        &output_sha256,
        bytes.len() as u64,
    )?;
    write_output(None, &header)
}

fn write_json_artifact_output(
    out: Option<PathBuf>,
    artifact: &WorkerJsonArtifact,
) -> Result<(), Failure> {
    match out {
        Some(path) => {
            std::fs::copy(artifact.path(), &path)
                .map_err(|_| Failure::Usage(format!("cannot write output: {}", path.display())))?;
            Ok(())
        }
        None => {
            let mut file = std::fs::File::open(artifact.path())
                .map_err(|_| EthosError::internal("pdfium worker JSON artifact missing"))?;
            let mut stdout = std::io::stdout();
            std::io::copy(&mut file, &mut stdout)
                .map_err(|_| EthosError::internal("stdout write failed"))?;
            Ok(())
        }
    }
}

fn document_output_bytes(format: Format, doc: &Document) -> Result<Vec<u8>, EthosError> {
    match format {
        Format::Json => document_json_output_bytes(doc),
        Format::Markdown => {
            let mut bytes = render_markdown(doc).into_bytes();
            bytes.push(b'\n');
            Ok(bytes)
        }
        Format::Text => {
            let mut bytes = render_text(doc).into_bytes();
            bytes.push(b'\n');
            Ok(bytes)
        }
    }
}

fn document_json_output_bytes(doc: &Document) -> Result<Vec<u8>, EthosError> {
    let value = serde_json::to_value(doc).map_err(|e| EthosError::internal(e.to_string()))?;
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    Ok(bytes)
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
    doc.payload
        .elements
        .iter()
        .filter_map(|element| {
            let text = element.text.as_deref()?;
            if element.element_type == ElementType::Heading {
                let level = element.heading_level.unwrap_or(1).clamp(1, 6);
                Some(format!("{} {text}", "#".repeat(level as usize)))
            } else {
                Some(text.to_string())
            }
        })
        .collect::<Vec<_>>()
        .join("\n\n")
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

#[cfg(test)]
mod tests {
    use super::*;
    use ethos_core::geom::QRect;
    use ethos_core::model::{
        CoordinateSystem, Element, ParserInfo, Payload, ProfileRef, SourceInfo,
    };

    fn doc_with_elements(elements: Vec<Element>) -> Document {
        Document {
            schema_version: ethos_core::SCHEMA_VERSION.to_string(),
            parser: ParserInfo {
                name: "ethos".to_string(),
                version: "test".to_string(),
            },
            profile: ProfileRef {
                id: "ethos-deterministic-v1".to_string(),
                sha256: "0".repeat(64),
            },
            source: SourceInfo {
                fingerprint: format!("sha256:{}", "0".repeat(64)),
                bytes: 0,
            },
            config_sha256: "0".repeat(64),
            payload_sha256: "0".repeat(64),
            fingerprint: format!("sha256:{}", "1".repeat(64)),
            payload: Payload {
                coordinate_system: CoordinateSystem {
                    origin: "top-left".to_string(),
                    unit: "quantum".to_string(),
                    quantum_per_point: 100,
                },
                pages: Vec::new(),
                elements,
                spans: Vec::new(),
                tables: Vec::new(),
                chunks: Vec::new(),
                regions: Vec::new(),
                security_warnings: Vec::new(),
                parser_warnings: Vec::new(),
            },
            diagnostics: None,
        }
    }

    fn text_element(id: &str, element_type: ElementType, text: &str) -> Element {
        Element {
            id: id.to_string(),
            element_type,
            page: "p0001".to_string(),
            bbox: QRect::new(0, 0, 100, 100).unwrap(),
            text: Some(text.to_string()),
            heading_level: (element_type == ElementType::Heading).then_some(1),
            table_ref: None,
            region_ref: None,
            confidence: None,
            span_refs: Vec::new(),
            warning_refs: Vec::new(),
        }
    }

    #[test]
    fn markdown_renders_heading_elements_with_hash_prefixes() {
        let doc = doc_with_elements(vec![
            text_element("e000001", ElementType::Heading, "Overview"),
            text_element("e000002", ElementType::TextBlock, "Body text"),
        ]);

        assert_eq!(render_text(&doc), "Overview\n\nBody text");
        assert_eq!(render_markdown(&doc), "# Overview\n\nBody text");
    }
}
