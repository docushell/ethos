/*
 * Copyright 2026 The Ethos maintainers
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 */

use ethos_core::grounding_json::{GroundingJsonError, GroundingJsonSource};
use sha2::{Digest, Sha256};

use crate::grounding::ensure_pdf_magic;
use crate::{read_file_limited, write_output, Failure, GroundingCheckArgs};

pub(crate) fn check(args: GroundingCheckArgs) -> Result<(), Failure> {
    let bytes = read_file_limited(&args.input, crate::default_max_input_bytes())?;
    let source = match ethos_core::grounding_json::parse_grounding_json(&bytes) {
        Ok(source) => source,
        Err(error) => {
            let report = invalid_report(&error);
            write_validation_report(args.out, &args.input, &report)?;
            return Err(Failure::Usage(format!(
                "grounding JSON {} at {}",
                error.code.as_str(),
                error.path
            )));
        }
    };
    let source_binding = match args.source_artifact.as_deref() {
        None => SourceBinding::NotChecked,
        Some(path) => {
            let bytes = read_file_limited(path, crate::default_max_input_bytes())?;
            ensure_pdf_magic(&bytes)?;
            let actual = format!("sha256:{:x}", Sha256::digest(bytes));
            if actual == source.source_sha256() {
                SourceBinding::Matched
            } else {
                SourceBinding::Mismatched
            }
        }
    };
    let report = valid_report(&source, source_binding);
    write_validation_report(args.out, &args.input, &report)?;
    if matches!(source_binding, SourceBinding::Mismatched) {
        return Err(Failure::Usage(
            "source artifact hash does not match source.sha256".to_string(),
        ));
    }
    Ok(())
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum SourceBinding {
    Matched,
    Mismatched,
    NotChecked,
}

struct ValidationReport {
    structure: &'static str,
    source_binding: &'static str,
    representation_sha256: Option<String>,
    counts: Option<(usize, usize, usize, usize)>,
    error: Option<ReportError>,
}
struct ReportError {
    code: String,
    path: String,
    message: String,
}

fn valid_report(source: &GroundingJsonSource, binding: SourceBinding) -> ValidationReport {
    let counts = source.counts();
    ValidationReport {
        structure: "valid",
        source_binding: binding.as_str(),
        representation_sha256: Some(source.representation_sha256().to_string()),
        counts: Some(counts),
        error: (binding == SourceBinding::Mismatched).then(|| ReportError {
            code: "source_binding_mismatch".to_string(),
            path: "/source/sha256".to_string(),
            message: "source artifact bytes do not match source.sha256".to_string(),
        }),
    }
}

fn invalid_report(error: &GroundingJsonError) -> ValidationReport {
    ValidationReport {
        structure: "invalid",
        source_binding: "not_checked",
        representation_sha256: None,
        counts: None,
        error: Some(ReportError {
            code: error.code.as_str().to_string(),
            path: error.path.clone(),
            message: error.message().to_string(),
        }),
    }
}

impl SourceBinding {
    fn as_str(self) -> &'static str {
        match self {
            Self::Matched => "matched",
            Self::Mismatched => "mismatched",
            Self::NotChecked => "not_checked",
        }
    }
}

fn write_validation_report(
    out: Option<std::path::PathBuf>,
    input: &std::path::Path,
    report: &ValidationReport,
) -> Result<(), Failure> {
    let mut value = serde_json::json!({
        "artifact_type": "ethos.grounding_validation.v1",
        "schema_version": "1.0.0",
        "structure": report.structure,
        "source_binding": report.source_binding,
    });
    if let Some(hash) = &report.representation_sha256 {
        value["representation_sha256"] = serde_json::Value::String(hash.clone());
    }
    if let Some((pages, elements, spans, tables)) = report.counts {
        value["counts"] = serde_json::json!({"pages": pages, "elements": elements, "spans": spans, "tables": tables});
    }
    if let Some(error) = &report.error {
        value["error"] =
            serde_json::json!({"code": error.code, "path": error.path, "message": error.message});
    }
    // The payload keeps its `artifact_type` field. Retiring it in favour of predicateType
    // would break payload equivalence for no benefit today; ADR-0016 freezes it as a
    // consumer contract on input regardless.
    let bytes = crate::statement_json_bytes(input, "grounding-validation", &value)?;
    write_output(out, &bytes)
}
