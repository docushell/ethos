/*
 * Copyright 2026 The Ethos maintainers
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 */

//! Shared exact-dispatch loader for CLI grounding inputs.

use ethos_core::grounding::GroundingSource;
use ethos_core::grounding_json::GroundingJsonSource;
use ethos_core::model::Document;
use ethos_grounding_opendataloader_json::OdlJsonSource;

use crate::{default_max_input_bytes, read_document, read_file_limited, Failure};
use sha2::{Digest, Sha256};
use std::path::Path;

/// One owned grounding source selected by the shared loader.
pub(crate) enum LoadedGrounding {
    /// Native Ethos canonical document.
    Native(Document),
    /// Explicit OpenDataLoader adapter output.
    OpenDataLoader(OdlJsonSource),
    /// Exact `ethos.grounding.v1` representation.
    GroundingJson(GroundingJsonSource),
}

impl GroundingSource for LoadedGrounding {
    fn parser(&self) -> ethos_core::grounding::ParserIdentity {
        match self {
            Self::Native(source) => source.parser(),
            Self::OpenDataLoader(source) => source.parser(),
            Self::GroundingJson(source) => source.parser(),
        }
    }
    fn capabilities(&self) -> ethos_core::grounding::Capabilities {
        match self {
            Self::Native(source) => source.capabilities(),
            Self::OpenDataLoader(source) => source.capabilities(),
            Self::GroundingJson(source) => source.capabilities(),
        }
    }
    fn fingerprint(&self) -> Option<String> {
        match self {
            Self::Native(source) => source.fingerprint(),
            Self::OpenDataLoader(source) => source.fingerprint(),
            Self::GroundingJson(source) => source.fingerprint(),
        }
    }
    fn pages(&self) -> Vec<ethos_core::grounding::PageGeometry> {
        match self {
            Self::Native(source) => source.pages(),
            Self::OpenDataLoader(source) => source.pages(),
            Self::GroundingJson(source) => source.pages(),
        }
    }
    fn elements(&self) -> Vec<ethos_core::grounding::GroundingElement> {
        match self {
            Self::Native(source) => source.elements(),
            Self::OpenDataLoader(source) => source.elements(),
            Self::GroundingJson(source) => source.elements(),
        }
    }
    fn structural_provenance(
        &self,
        id: &str,
    ) -> Option<ethos_core::grounding::GroundingProvenance> {
        match self {
            Self::Native(source) => source.structural_provenance(id),
            Self::OpenDataLoader(source) => source.structural_provenance(id),
            Self::GroundingJson(source) => source.structural_provenance(id),
        }
    }
    fn spans(&self) -> Vec<ethos_core::grounding::GroundingSpan> {
        match self {
            Self::Native(source) => source.spans(),
            Self::OpenDataLoader(source) => source.spans(),
            Self::GroundingJson(source) => source.spans(),
        }
    }
    fn tables(&self) -> Vec<ethos_core::grounding::GroundingTable> {
        match self {
            Self::Native(source) => source.tables(),
            Self::OpenDataLoader(source) => source.tables(),
            Self::GroundingJson(source) => source.tables(),
        }
    }
}

/// Load one source using explicit adapter selection or exact Grounding JSON identity detection.
pub(crate) fn load_source(
    path: &Path,
    grounding: Option<&str>,
) -> Result<LoadedGrounding, Failure> {
    let max_input_bytes = default_max_input_bytes();
    match grounding {
        Some("opendataloader-json") => {
            let bytes = read_file_limited(path, max_input_bytes)?;
            let text = String::from_utf8(bytes)
                .map_err(|_| Failure::Usage("grounding input is not UTF-8".to_string()))?;
            let source = OdlJsonSource::from_json_str(&text)
                .map_err(|e| Failure::Usage(format!("opendataloader-json adapter: {e}")))?;
            Ok(LoadedGrounding::OpenDataLoader(source))
        }
        Some("ethos-grounding-json") => load_grounding_json(path),
        Some(other) => Err(Failure::Usage(format!(
            "unknown grounding adapter '{other}' (available: ethos-grounding-json, opendataloader-json)"
        ))),
        None => {
            let bytes = read_file_limited(path, max_input_bytes)?;
            if is_exact_grounding_json(&bytes) {
                let source = ethos_core::grounding_json::parse_grounding_json(&bytes)
                    .map_err(|error| Failure::Usage(format!("grounding JSON {} at {}", error.code.as_str(), error.path)))?;
                Ok(LoadedGrounding::GroundingJson(source))
            } else {
                Ok(LoadedGrounding::Native(read_document(path)?))
            }
        }
    }
}

pub(crate) fn load_grounding_json(path: &Path) -> Result<LoadedGrounding, Failure> {
    let bytes = read_file_limited(path, default_max_input_bytes())?;
    let source = ethos_core::grounding_json::parse_grounding_json(&bytes).map_err(|error| {
        Failure::Usage(format!(
            "grounding JSON {} at {}",
            error.code.as_str(),
            error.path
        ))
    })?;
    Ok(LoadedGrounding::GroundingJson(source))
}

/// Check optional original-PDF binding without changing verification semantics.
pub(crate) fn check_source_binding(source: &LoadedGrounding, path: &Path) -> Result<(), Failure> {
    let expected = match source {
        LoadedGrounding::GroundingJson(source) => source.source_sha256(),
        _ => {
            return Err(Failure::Usage(
                "--source-artifact requires Grounding JSON input".to_string(),
            ))
        }
    };
    let bytes = crate::read_file_limited(path, crate::default_max_input_bytes())?;
    ensure_pdf_magic(&bytes)?;
    let actual = format!("sha256:{:x}", Sha256::digest(bytes));
    if actual != expected {
        return Err(Failure::Usage(
            "source artifact hash does not match source.sha256".to_string(),
        ));
    }
    Ok(())
}

pub(crate) fn ensure_pdf_magic(bytes: &[u8]) -> Result<(), Failure> {
    if !bytes.starts_with(b"%PDF-") {
        return Err(Failure::Usage("source artifact is not a PDF".to_string()));
    }
    Ok(())
}

fn is_exact_grounding_json(bytes: &[u8]) -> bool {
    serde_json::from_slice::<serde_json::Value>(bytes)
        .ok()
        .and_then(|value| {
            value
                .get("artifact_type")
                .and_then(serde_json::Value::as_str)
                .map(str::to_owned)
        })
        .is_some_and(|artifact_type| artifact_type == "ethos.grounding.v1")
}
