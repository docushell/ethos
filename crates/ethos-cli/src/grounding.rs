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
use serde::de::{IgnoredAny, MapAccess, Visitor};
use sha2::{Digest, Sha256};
use std::fmt;
use std::path::Path;

/// The only auto-detectable foreign artifact type.
const GROUNDING_V1_ARTIFACT_TYPE: &str = "ethos.grounding.v1";
/// The only top-level key the shared loader inspects.
const ARTIFACT_TYPE_KEY: &str = "artifact_type";

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
        Some("ethos-json") => Ok(LoadedGrounding::Native(read_document(path)?)),
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
            "unknown grounding adapter '{other}' (available: ethos-json, ethos-grounding-json, opendataloader-json)"
        ))),
        None => {
            let bytes = read_file_limited(path, max_input_bytes)?;
            match probe_artifact_type(&bytes) {
                // An absent artifact type keeps the existing native Ethos loader.
                ArtifactType::Absent => Ok(LoadedGrounding::Native(read_document(path)?)),
                ArtifactType::GroundingV1 => {
                    let source = ethos_core::grounding_json::parse_grounding_json(&bytes)
                        .map_err(grounding_json_failure)?;
                    Ok(LoadedGrounding::GroundingJson(source))
                }
                // A present but duplicate, non-string, or unsupported artifact type never
                // falls back to another loader.
                ArtifactType::Unsupported => Err(Failure::Usage(format!(
                    "unsupported top-level artifact_type (expected exactly \
                     '{GROUNDING_V1_ARTIFACT_TYPE}', or omit the field for native Ethos JSON)"
                ))),
            }
        }
    }
}

pub(crate) fn load_grounding_json(path: &Path) -> Result<LoadedGrounding, Failure> {
    let bytes = read_file_limited(path, default_max_input_bytes())?;
    let source =
        ethos_core::grounding_json::parse_grounding_json(&bytes).map_err(grounding_json_failure)?;
    Ok(LoadedGrounding::GroundingJson(source))
}

/// Render one bounded, stable Grounding JSON validation failure as a usage error.
fn grounding_json_failure(error: ethos_core::grounding_json::GroundingJsonError) -> Failure {
    Failure::Usage(format!(
        "grounding JSON {} at {}",
        error.code.as_str(),
        error.path
    ))
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

/// What the optional top-level `artifact_type` selects. Nothing else is inspected, so no input
/// is ever reclassified by guessing field names.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ArtifactType {
    /// No top-level `artifact_type`.
    Absent,
    /// Exactly `ethos.grounding.v1`, declared once, as a string.
    GroundingV1,
    /// Present but duplicated, non-string, or not a supported artifact type.
    Unsupported,
}

/// Inspect only the optional top-level `artifact_type`.
///
/// Malformed input and non-object roots report [`ArtifactType::Absent`] so the existing native
/// loader keeps ownership of its own error messages. A present artifact type is never allowed to
/// reach a different loader.
fn probe_artifact_type(bytes: &[u8]) -> ArtifactType {
    let Ok(value) = serde_json::from_slice::<serde_json::Value>(bytes) else {
        return ArtifactType::Absent;
    };
    let Some(object) = value.as_object() else {
        return ArtifactType::Absent;
    };
    let Some(artifact_type) = object.get(ARTIFACT_TYPE_KEY) else {
        return ArtifactType::Absent;
    };
    // `serde_json::Value` collapses duplicate keys, so count them on a second strict pass before
    // trusting the collapsed value.
    let mut deserializer = serde_json::Deserializer::from_slice(bytes);
    let declared_once = matches!(
        serde::Deserializer::deserialize_map(&mut deserializer, ArtifactTypeKeyCount),
        Ok(1)
    );
    if !declared_once {
        return ArtifactType::Unsupported;
    }
    match artifact_type.as_str() {
        Some(GROUNDING_V1_ARTIFACT_TYPE) => ArtifactType::GroundingV1,
        _ => ArtifactType::Unsupported,
    }
}

/// Count top-level `artifact_type` keys without collapsing duplicates.
struct ArtifactTypeKeyCount;

impl<'de> Visitor<'de> for ArtifactTypeKeyCount {
    type Value = usize;

    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str("a JSON object")
    }

    fn visit_map<A>(self, mut map: A) -> Result<usize, A::Error>
    where
        A: MapAccess<'de>,
    {
        let mut count = 0usize;
        while let Some(key) = map.next_key::<String>()? {
            if key == ARTIFACT_TYPE_KEY {
                count = count.saturating_add(1);
            }
            map.next_value::<IgnoredAny>()?;
        }
        Ok(count)
    }
}

#[cfg(test)]
mod tests {
    use super::{probe_artifact_type, ArtifactType};

    #[test]
    fn absent_artifact_type_selects_the_native_loader() {
        assert_eq!(
            probe_artifact_type(br#"{"schema_version":"1.0.0"}"#),
            ArtifactType::Absent
        );
    }

    #[test]
    fn exact_artifact_type_selects_grounding_json() {
        assert_eq!(
            probe_artifact_type(br#"{"artifact_type":"ethos.grounding.v1"}"#),
            ArtifactType::GroundingV1
        );
    }

    #[test]
    fn unknown_non_string_and_duplicate_artifact_types_never_fall_back() {
        for input in [
            br#"{"artifact_type":"ethos.grounding.v2"}"#.as_slice(),
            br#"{"artifact_type":"ethos.grounding.V1"}"#.as_slice(),
            br#"{"artifact_type":5}"#.as_slice(),
            br#"{"artifact_type":null}"#.as_slice(),
            br#"{"artifact_type":["ethos.grounding.v1"]}"#.as_slice(),
            br#"{"artifact_type":"ethos.grounding.v1","artifact_type":"ethos.grounding.v1"}"#
                .as_slice(),
            br#"{"artifact_type":"other","artifact_type":"ethos.grounding.v1"}"#.as_slice(),
        ] {
            assert_eq!(
                probe_artifact_type(input),
                ArtifactType::Unsupported,
                "input must not reach another loader: {}",
                String::from_utf8_lossy(input)
            );
        }
    }

    #[test]
    fn malformed_and_non_object_roots_stay_with_the_native_loader() {
        for input in [b"not json".as_slice(), b"[]".as_slice(), b"7".as_slice()] {
            assert_eq!(probe_artifact_type(input), ArtifactType::Absent);
        }
    }
}
