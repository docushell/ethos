/*
 * Copyright 2026 The Ethos maintainers
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 */

//! Strict loading and invariant validation for `ethos.grounding.v1` JSON.
//!
//! The parser deliberately checks duplicate keys before constructing a JSON value. This keeps
//! the accepted representation deterministic across JSON implementations.

use crate::geom::MAX_SAFE_INT;
use crate::grounding::{
    GroundingCell, GroundingElement, GroundingSource, GroundingSpan, GroundingTable, PageGeometry,
    ParserIdentity,
};
use serde::de::{DeserializeSeed, MapAccess, SeqAccess, Visitor};
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value};
use sha2::{Digest, Sha256};
use std::collections::HashSet;
use std::fmt;

/// Maximum accepted input size, matching the existing default document limit.
pub const MAX_INPUT_BYTES: usize = 256 * 1024 * 1024;
/// Maximum accepted nesting depth.
pub const MAX_DEPTH: usize = 64;
/// Maximum number of pages.
pub const MAX_PAGES: usize = 5_000;
/// Maximum number of elements or spans.
pub const MAX_ELEMENTS: usize = 1_000_000;
/// Maximum number of tables.
pub const MAX_TABLES: usize = 100_000;
/// Maximum number of table cells.
pub const MAX_CELLS: usize = 1_000_000;
/// Maximum identifier length.
pub const MAX_ID_BYTES: usize = 256;
/// Maximum text/string length.
pub const MAX_STRING_BYTES: usize = 16_384;

/// Stable validation error codes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum GroundingJsonErrorCode {
    /// The input is not valid UTF-8 or JSON.
    InvalidJson,
    /// The input began with a UTF-8 BOM.
    BomNotAllowed,
    /// A JSON object repeated a key.
    DuplicateKey,
    /// An object contains a field outside the contract.
    UnknownField,
    /// A required field is absent or has the wrong shape.
    InvalidField,
    /// The artifact identity is not the supported v1 identity.
    UnsupportedVersion,
    /// A capability combination is contradictory.
    InvalidCapabilities,
    /// A page, element, span, or table identifier was repeated.
    DuplicateId,
    /// A referenced page or element does not exist.
    UnknownReference,
    /// An array ordering invariant failed.
    InvalidOrder,
    /// A bounding box is malformed or outside its page.
    InvalidBBox,
    /// Character offsets do not match the owning text.
    InvalidOffsets,
    /// A table or cell invariant failed.
    InvalidTable,
    /// A reference, order, identifier, or geometry invariant failed.
    InvalidInvariant,
    /// An accepted structural limit was exceeded.
    LimitExceeded,
}

impl GroundingJsonErrorCode {
    /// Stable wire spelling used by validation reports.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::InvalidJson => "invalid_json",
            Self::BomNotAllowed => "bom_not_allowed",
            Self::DuplicateKey => "duplicate_key",
            Self::UnknownField => "unknown_field",
            Self::InvalidField => "invalid_field",
            Self::UnsupportedVersion => "unsupported_version",
            Self::InvalidCapabilities => "invalid_capabilities",
            Self::DuplicateId => "duplicate_id",
            Self::UnknownReference => "unknown_reference",
            Self::InvalidOrder => "invalid_order",
            Self::InvalidBBox => "invalid_bbox",
            Self::InvalidOffsets => "invalid_offsets",
            Self::InvalidTable => "invalid_table",
            Self::InvalidInvariant => "invalid_invariant",
            Self::LimitExceeded => "limit_exceeded",
        }
    }
}

/// One deterministic validation failure.
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct GroundingJsonError {
    /// Stable machine-readable code.
    pub code: GroundingJsonErrorCode,
    /// Bounded JSON path.
    pub path: String,
}

impl GroundingJsonError {
    /// Return a bounded correction-oriented message.
    pub fn message(&self) -> &'static str {
        match self.code {
            GroundingJsonErrorCode::InvalidJson => {
                "submit valid UTF-8 JSON without unsupported numeric forms"
            }
            GroundingJsonErrorCode::BomNotAllowed => "remove the UTF-8 BOM",
            GroundingJsonErrorCode::DuplicateKey => "remove the duplicate object key",
            GroundingJsonErrorCode::UnknownField => "remove the unknown field",
            GroundingJsonErrorCode::InvalidField => "correct the field type or required fields",
            GroundingJsonErrorCode::UnsupportedVersion => {
                "use ethos.grounding.v1 with schema_version 1.0.0"
            }
            GroundingJsonErrorCode::InvalidCapabilities => {
                "make capabilities agree with supplied arrays and offsets"
            }
            GroundingJsonErrorCode::DuplicateId => {
                "make identifiers unique within their typed namespace"
            }
            GroundingJsonErrorCode::UnknownReference => "reference an existing page or element",
            GroundingJsonErrorCode::InvalidOrder => {
                "preserve the required deterministic array order"
            }
            GroundingJsonErrorCode::InvalidBBox => "submit a positive bounding box within its page",
            GroundingJsonErrorCode::InvalidOffsets => {
                "make Unicode scalar offsets select the span text exactly"
            }
            GroundingJsonErrorCode::InvalidTable => {
                "correct table cell order, ranges, and overlaps"
            }
            GroundingJsonErrorCode::InvalidInvariant => "correct the referenced value or invariant",
            GroundingJsonErrorCode::LimitExceeded => {
                "reduce the submitted artifact within the measured limits"
            }
        }
    }
}

impl fmt::Display for GroundingJsonError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}: {}", self.code, self.path)
    }
}

impl std::error::Error for GroundingJsonError {}

/// The validated Grounding JSON source. Its fingerprint is the hash of the exact accepted bytes.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GroundingJsonSource {
    artifact: Artifact,
    representation_sha256: String,
}

impl GroundingJsonSource {
    /// Return the exact accepted representation fingerprint.
    pub fn representation_sha256(&self) -> &str {
        &self.representation_sha256
    }

    /// Return the producer-declared original PDF hash.
    pub fn source_sha256(&self) -> &str {
        &self.artifact.source.sha256
    }

    /// Return page, element, span, and table counts for validation reports.
    pub fn counts(&self) -> (usize, usize, usize, usize) {
        (
            self.artifact.pages.len(),
            self.artifact.elements.len(),
            self.artifact.spans.as_ref().map_or(0, Vec::len),
            self.artifact.tables.as_ref().map_or(0, Vec::len),
        )
    }
}

impl GroundingSource for GroundingJsonSource {
    fn parser(&self) -> ParserIdentity {
        ParserIdentity {
            name: self.artifact.producer.name.clone(),
            version: self.artifact.producer.version.clone(),
            adapter: Some("ethos-grounding-json".to_owned()),
            adapter_version: Some("1.0.0".to_owned()),
        }
    }
    fn capabilities(&self) -> crate::grounding::Capabilities {
        crate::grounding::Capabilities {
            spans: self.artifact.capabilities.spans,
            char_offsets: self.artifact.capabilities.char_offsets,
            tables: self.artifact.capabilities.tables,
            fingerprint: true,
            coordinate_origin: crate::grounding::CoordinateOrigin::TopLeft,
            crop_support: false,
        }
    }
    fn fingerprint(&self) -> Option<String> {
        Some(self.representation_sha256.clone())
    }
    fn pages(&self) -> Vec<PageGeometry> {
        self.artifact
            .pages
            .iter()
            .map(|p| PageGeometry {
                id: p.id.clone(),
                index: p.index,
                width: p.width,
                height: p.height,
                rotation: p.rotation,
            })
            .collect()
    }
    fn elements(&self) -> Vec<GroundingElement> {
        self.artifact
            .elements
            .iter()
            .map(|e| GroundingElement {
                id: e.id.clone(),
                page: e.page.clone(),
                bbox: e.bbox,
                kind: e.kind.clone(),
                text: e.text.clone(),
            })
            .collect()
    }
    fn spans(&self) -> Vec<GroundingSpan> {
        self.artifact
            .spans
            .clone()
            .unwrap_or_default()
            .into_iter()
            .map(|s| GroundingSpan {
                id: s.id,
                page: s.page,
                bbox: s.bbox,
                text: s.text,
                element: s.element,
                char_start: s.char_start,
                char_end: s.char_end,
            })
            .collect()
    }
    fn tables(&self) -> Vec<GroundingTable> {
        self.artifact
            .tables
            .clone()
            .unwrap_or_default()
            .into_iter()
            .map(|t| GroundingTable {
                id: t.id,
                page: t.page,
                bbox: t.bbox,
                cells: t
                    .cells
                    .into_iter()
                    .map(|c| GroundingCell {
                        row: c.row,
                        col: c.col,
                        row_span: c.row_span,
                        col_span: c.col_span,
                        bbox: c.bbox,
                        text: c.text,
                    })
                    .collect(),
            })
            .collect()
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Artifact {
    artifact_type: String,
    schema_version: String,
    source: Source,
    producer: Producer,
    capabilities: Capabilities,
    coordinate_system: CoordinateSystem,
    pages: Vec<Page>,
    elements: Vec<Element>,
    #[serde(default)]
    spans: Option<Vec<Span>>,
    #[serde(default)]
    tables: Option<Vec<Table>>,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Source {
    media_type: String,
    sha256: String,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Producer {
    name: String,
    version: String,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Capabilities {
    spans: bool,
    char_offsets: bool,
    tables: bool,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct CoordinateSystem {
    unit: String,
    origin: String,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Page {
    id: String,
    index: u32,
    width: i64,
    height: i64,
    rotation: u16,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Element {
    id: String,
    page: String,
    bbox: [i64; 4],
    kind: String,
    text: Option<String>,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Span {
    id: String,
    page: String,
    bbox: [i64; 4],
    text: String,
    element: Option<String>,
    char_start: Option<u32>,
    char_end: Option<u32>,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Table {
    id: String,
    page: String,
    bbox: [i64; 4],
    cells: Vec<Cell>,
}
#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Cell {
    row: u32,
    col: u32,
    row_span: u32,
    col_span: u32,
    bbox: [i64; 4],
    text: String,
}

struct StrictValueSeed {
    depth: usize,
}
struct StrictValueVisitor {
    depth: usize,
}

impl<'de> DeserializeSeed<'de> for StrictValueSeed {
    type Value = Value;
    fn deserialize<D>(self, deserializer: D) -> Result<Value, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        deserializer.deserialize_any(StrictValueVisitor { depth: self.depth })
    }
}
impl<'de> Visitor<'de> for StrictValueVisitor {
    type Value = Value;
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str("strict JSON value")
    }
    fn visit_bool<E>(self, v: bool) -> Result<Value, E> {
        Ok(Value::Bool(v))
    }
    fn visit_i64<E>(self, v: i64) -> Result<Value, E>
    where
        E: serde::de::Error,
    {
        if v.unsigned_abs() > MAX_SAFE_INT as u64 {
            return Err(serde::de::Error::custom("integer limit exceeded"));
        }
        Ok(Value::Number(v.into()))
    }
    fn visit_u64<E>(self, v: u64) -> Result<Value, E>
    where
        E: serde::de::Error,
    {
        if v > MAX_SAFE_INT as u64 {
            return Err(serde::de::Error::custom("integer limit exceeded"));
        }
        Ok(Value::Number(v.into()))
    }
    fn visit_f64<E>(self, _: f64) -> Result<Value, E>
    where
        E: serde::de::Error,
    {
        Err(E::custom("floating point values are not allowed"))
    }
    fn visit_str<E>(self, v: &str) -> Result<Value, E>
    where
        E: serde::de::Error,
    {
        if v.len() > MAX_STRING_BYTES {
            return Err(E::custom("string limit exceeded"));
        }
        Ok(Value::String(v.to_owned()))
    }
    fn visit_string<E>(self, v: String) -> Result<Value, E>
    where
        E: serde::de::Error,
    {
        if v.len() > MAX_STRING_BYTES {
            return Err(E::custom("string limit exceeded"));
        }
        Ok(Value::String(v))
    }
    fn visit_none<E>(self) -> Result<Value, E>
    where
        E: serde::de::Error,
    {
        Err(E::custom("null values are not allowed"))
    }
    fn visit_unit<E>(self) -> Result<Value, E>
    where
        E: serde::de::Error,
    {
        Err(E::custom("null values are not allowed"))
    }
    fn visit_seq<A>(self, mut seq: A) -> Result<Value, A::Error>
    where
        A: SeqAccess<'de>,
    {
        if self.depth >= MAX_DEPTH {
            return Err(serde::de::Error::custom("depth limit exceeded"));
        }
        let mut out = Vec::new();
        while let Some(value) = seq.next_element_seed(StrictValueSeed {
            depth: self.depth + 1,
        })? {
            if out.len() >= MAX_ELEMENTS {
                return Err(serde::de::Error::custom("array limit exceeded"));
            }
            out.push(value);
        }
        Ok(Value::Array(out))
    }
    fn visit_map<A>(self, mut map: A) -> Result<Value, A::Error>
    where
        A: MapAccess<'de>,
    {
        if self.depth >= MAX_DEPTH {
            return Err(serde::de::Error::custom("depth limit exceeded"));
        }
        let mut out = Map::new();
        let mut keys = HashSet::new();
        while let Some(key) = map.next_key::<String>()? {
            if !keys.insert(key.clone()) {
                return Err(serde::de::Error::custom("duplicate object key"));
            }
            let value = map.next_value_seed(StrictValueSeed {
                depth: self.depth + 1,
            })?;
            out.insert(key, value);
        }
        Ok(Value::Object(out))
    }
}

/// Parse and validate one Grounding JSON representation.
pub fn parse_grounding_json(bytes: &[u8]) -> Result<GroundingJsonSource, GroundingJsonError> {
    if bytes.len() > MAX_INPUT_BYTES {
        return Err(error(GroundingJsonErrorCode::LimitExceeded, "/"));
    }
    if bytes.starts_with(&[0xef, 0xbb, 0xbf]) {
        return Err(error(GroundingJsonErrorCode::BomNotAllowed, "/"));
    }
    let mut de = serde_json::Deserializer::from_slice(bytes);
    let value = StrictValueSeed { depth: 0 }
        .deserialize(&mut de)
        .map_err(|e| {
            let message = e.to_string();
            if message.contains("duplicate object key") {
                error(GroundingJsonErrorCode::DuplicateKey, "/")
            } else if message.contains("limit exceeded") {
                error(GroundingJsonErrorCode::LimitExceeded, "/")
            } else {
                error(GroundingJsonErrorCode::InvalidJson, "/")
            }
        })?;
    de.end()
        .map_err(|_| error(GroundingJsonErrorCode::InvalidJson, "/"))?;
    reject_unknown_fields(&value)?;
    let artifact: Artifact = serde_json::from_value(value).map_err(|e| {
        if e.to_string().contains("unknown field") {
            error(GroundingJsonErrorCode::UnknownField, "/")
        } else {
            error(GroundingJsonErrorCode::InvalidField, "/")
        }
    })?;
    validate(&artifact)?;
    let mut hash = Sha256::new();
    hash.update(bytes);
    Ok(GroundingJsonSource {
        artifact,
        representation_sha256: format!("sha256:{:x}", hash.finalize()),
    })
}

fn reject_unknown_fields(value: &Value) -> Result<(), GroundingJsonError> {
    let Some(root) = value.as_object() else {
        return Ok(());
    };
    check_object(
        root,
        &[
            "artifact_type",
            "schema_version",
            "source",
            "producer",
            "capabilities",
            "coordinate_system",
            "pages",
            "elements",
            "spans",
            "tables",
        ],
        "/",
    )?;
    check_child(root.get("source"), &["media_type", "sha256"], "/source")?;
    check_child(root.get("producer"), &["name", "version"], "/producer")?;
    check_child(
        root.get("capabilities"),
        &["spans", "char_offsets", "tables"],
        "/capabilities",
    )?;
    check_child(
        root.get("coordinate_system"),
        &["unit", "origin"],
        "/coordinate_system",
    )?;
    check_array(
        root.get("pages"),
        &["id", "index", "width", "height", "rotation"],
        "/pages",
    )?;
    check_array(
        root.get("elements"),
        &["id", "page", "bbox", "kind", "text"],
        "/elements",
    )?;
    check_array(
        root.get("spans"),
        &[
            "id",
            "page",
            "bbox",
            "text",
            "element",
            "char_start",
            "char_end",
        ],
        "/spans",
    )?;
    if let Some(Value::Array(tables)) = root.get("tables") {
        for (index, table) in tables.iter().enumerate() {
            let path = format!("/tables/{index}");
            if let Some(object) = table.as_object() {
                check_object(object, &["id", "page", "bbox", "cells"], &path)?;
                check_array(
                    object.get("cells"),
                    &["row", "col", "row_span", "col_span", "bbox", "text"],
                    &format!("{path}/cells"),
                )?;
            }
        }
    }
    Ok(())
}

fn check_child(
    value: Option<&Value>,
    allowed: &[&str],
    path: &str,
) -> Result<(), GroundingJsonError> {
    if let Some(Value::Object(object)) = value {
        check_object(object, allowed, path)?;
    }
    Ok(())
}

fn check_array(
    value: Option<&Value>,
    allowed: &[&str],
    path: &str,
) -> Result<(), GroundingJsonError> {
    if let Some(Value::Array(items)) = value {
        for (index, item) in items.iter().enumerate() {
            if let Some(object) = item.as_object() {
                check_object(object, allowed, &format!("{path}/{index}"))?;
            }
        }
    }
    Ok(())
}

fn check_object(
    object: &Map<String, Value>,
    allowed: &[&str],
    path: &str,
) -> Result<(), GroundingJsonError> {
    if let Some(key) = object.keys().find(|key| !allowed.contains(&key.as_str())) {
        let field_path = if path == "/" {
            format!("/{key}")
        } else {
            format!("{path}/{key}")
        };
        return Err(error(GroundingJsonErrorCode::UnknownField, &field_path));
    }
    Ok(())
}

fn error(code: GroundingJsonErrorCode, path: &str) -> GroundingJsonError {
    GroundingJsonError {
        code,
        path: path.to_owned(),
    }
}
fn valid_id(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= MAX_ID_BYTES
        && value
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'.' || b == b'_' || b == b':' || b == b'-')
        && value.as_bytes()[0].is_ascii_alphanumeric()
}
fn validate(artifact: &Artifact) -> Result<(), GroundingJsonError> {
    if artifact.artifact_type != "ethos.grounding.v1" || artifact.schema_version != "1.0.0" {
        return Err(error(
            GroundingJsonErrorCode::UnsupportedVersion,
            "/artifact_type",
        ));
    }
    if artifact.source.media_type != "application/pdf"
        || !artifact.source.sha256.starts_with("sha256:")
        || artifact.source.sha256.len() != 71
        || !artifact.source.sha256[7..]
            .bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
    {
        return Err(error(GroundingJsonErrorCode::InvalidField, "/source"));
    }
    if artifact.coordinate_system.unit != "centipoint"
        || artifact.coordinate_system.origin != "top-left"
    {
        return Err(error(
            GroundingJsonErrorCode::InvalidInvariant,
            "/coordinate_system",
        ));
    }
    if artifact.capabilities.char_offsets && !artifact.capabilities.spans
        || artifact.capabilities.spans != artifact.spans.is_some()
        || artifact.capabilities.tables != artifact.tables.is_some()
    {
        return Err(error(
            GroundingJsonErrorCode::InvalidCapabilities,
            "/capabilities",
        ));
    }
    if artifact.pages.len() > MAX_PAGES
        || artifact.elements.len() > MAX_ELEMENTS
        || artifact
            .spans
            .as_ref()
            .is_some_and(|v| v.len() > MAX_ELEMENTS)
        || artifact
            .tables
            .as_ref()
            .is_some_and(|v| v.len() > MAX_TABLES)
    {
        return Err(error(GroundingJsonErrorCode::LimitExceeded, "/"));
    }
    let mut page_ids = HashSet::new();
    let mut pages = HashSet::new();
    let mut expected = 1u32;
    for (i, p) in artifact.pages.iter().enumerate() {
        let path = format!("/pages/{i}");
        if !valid_id(&p.id) {
            return Err(error(
                GroundingJsonErrorCode::InvalidField,
                &format!("{path}/id"),
            ));
        }
        if !page_ids.insert(p.id.clone()) {
            return Err(error(
                GroundingJsonErrorCode::DuplicateId,
                &format!("{path}/id"),
            ));
        }
        if p.index != expected {
            return Err(error(
                GroundingJsonErrorCode::InvalidOrder,
                &format!("{path}/index"),
            ));
        }
        if p.width <= 0 || p.height <= 0 || p.width > MAX_SAFE_INT || p.height > MAX_SAFE_INT {
            return Err(error(GroundingJsonErrorCode::InvalidInvariant, &path));
        }
        if !matches!(p.rotation, 0 | 90 | 180 | 270) {
            return Err(error(
                GroundingJsonErrorCode::InvalidInvariant,
                &format!("{path}/rotation"),
            ));
        }
        expected += 1;
        pages.insert(p.id.clone());
    }
    let mut ids = HashSet::new();
    for (i, e) in artifact.elements.iter().enumerate() {
        let path = format!("/elements/{i}");
        if !valid_id(&e.id) {
            return Err(error(
                GroundingJsonErrorCode::InvalidField,
                &format!("{path}/id"),
            ));
        }
        if !ids.insert(e.id.clone()) {
            return Err(error(
                GroundingJsonErrorCode::DuplicateId,
                &format!("{path}/id"),
            ));
        }
        if !pages.contains(&e.page) {
            return Err(error(
                GroundingJsonErrorCode::UnknownReference,
                &format!("{path}/page"),
            ));
        }
        if !valid_bbox(e.bbox, artifact.pages.iter().find(|p| p.id == e.page)) {
            return Err(error(
                GroundingJsonErrorCode::InvalidBBox,
                &format!("{path}/bbox"),
            ));
        }
        if e.kind.is_empty()
            || e.kind
                .bytes()
                .any(|b| !(b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'_' || b == b'-'))
        {
            return Err(error(
                GroundingJsonErrorCode::InvalidField,
                &format!("{path}/kind"),
            ));
        }
    }
    if let Some(spans) = &artifact.spans {
        let mut seen = HashSet::new();
        for (i, s) in spans.iter().enumerate() {
            let path = format!("/spans/{i}");
            if !valid_id(&s.id) {
                return Err(error(
                    GroundingJsonErrorCode::InvalidField,
                    &format!("{path}/id"),
                ));
            }
            if !seen.insert(s.id.clone()) {
                return Err(error(
                    GroundingJsonErrorCode::DuplicateId,
                    &format!("{path}/id"),
                ));
            }
            if !pages.contains(&s.page) {
                return Err(error(
                    GroundingJsonErrorCode::UnknownReference,
                    &format!("{path}/page"),
                ));
            }
            if !valid_bbox(s.bbox, artifact.pages.iter().find(|p| p.id == s.page)) {
                return Err(error(
                    GroundingJsonErrorCode::InvalidBBox,
                    &format!("{path}/bbox"),
                ));
            }
            if s.element.as_ref().is_some_and(|id| !ids.contains(id)) {
                return Err(error(
                    GroundingJsonErrorCode::UnknownReference,
                    &format!("{path}/element"),
                ));
            }
            let offsets_present = s.char_start.is_some() || s.char_end.is_some();
            let offsets_complete = s.char_start.is_some() && s.char_end.is_some();
            let offsets_match = match (s.element.as_ref(), s.char_start, s.char_end) {
                (Some(element_id), Some(start), Some(end)) => artifact
                    .elements
                    .iter()
                    .find(|e| e.id == *element_id)
                    .and_then(|e| e.text.as_ref())
                    .map(|text| {
                        let chars: Vec<char> = text.chars().collect();
                        start <= end
                            && end as usize <= chars.len()
                            && chars[start as usize..end as usize]
                                .iter()
                                .collect::<String>()
                                == s.text
                    })
                    .unwrap_or(false),
                _ => false,
            };
            if offsets_present != artifact.capabilities.char_offsets
                || (artifact.capabilities.char_offsets && (!offsets_complete || !offsets_match))
            {
                return Err(error(GroundingJsonErrorCode::InvalidOffsets, &path));
            }
        }
    }
    if let Some(tables) = &artifact.tables {
        let mut seen = HashSet::new();
        for (i, t) in tables.iter().enumerate() {
            let path = format!("/tables/{i}");
            if !valid_id(&t.id) {
                return Err(error(
                    GroundingJsonErrorCode::InvalidField,
                    &format!("{path}/id"),
                ));
            }
            if !seen.insert(t.id.clone()) {
                return Err(error(
                    GroundingJsonErrorCode::DuplicateId,
                    &format!("{path}/id"),
                ));
            }
            if !pages.contains(&t.page) {
                return Err(error(
                    GroundingJsonErrorCode::UnknownReference,
                    &format!("{path}/page"),
                ));
            }
            if !valid_bbox(t.bbox, artifact.pages.iter().find(|p| p.id == t.page)) {
                return Err(error(
                    GroundingJsonErrorCode::InvalidBBox,
                    &format!("{path}/bbox"),
                ));
            }
            if t.cells.len() > MAX_CELLS {
                return Err(error(
                    GroundingJsonErrorCode::LimitExceeded,
                    &format!("/tables/{i}/cells"),
                ));
            }
            let mut occupied = HashSet::new();
            let mut previous = None;
            for c in &t.cells {
                let row_end = c.row.checked_add(c.row_span);
                let col_end = c.col.checked_add(c.col_span);
                if c.row_span == 0
                    || c.col_span == 0
                    || !valid_bbox(c.bbox, artifact.pages.iter().find(|p| p.id == t.page))
                    || previous.is_some_and(|(row, col)| (c.row, c.col) <= (row, col))
                    || row_end.is_none()
                    || col_end.is_none()
                {
                    return Err(error(
                        GroundingJsonErrorCode::InvalidTable,
                        &format!("/tables/{i}/cells"),
                    ));
                }
                previous = Some((c.row, c.col));
                for row in c.row..row_end.unwrap() {
                    for col in c.col..col_end.unwrap() {
                        if !occupied.insert((row, col)) {
                            return Err(error(
                                GroundingJsonErrorCode::InvalidTable,
                                &format!("/tables/{i}/cells"),
                            ));
                        }
                        if occupied.len() > MAX_CELLS {
                            return Err(error(
                                GroundingJsonErrorCode::LimitExceeded,
                                &format!("/tables/{i}/cells"),
                            ));
                        }
                    }
                }
            }
        }
    }
    Ok(())
}
fn valid_bbox(b: [i64; 4], page: Option<&Page>) -> bool {
    page.is_some_and(|p| {
        b.iter().all(|v| *v >= 0 && *v <= MAX_SAFE_INT)
            && b[2] > b[0]
            && b[3] > b[1]
            && b[2] <= p.width
            && b[3] <= p.height
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::grounding::GroundingSource;
    fn valid() -> String {
        r#"{"artifact_type":"ethos.grounding.v1","schema_version":"1.0.0","source":{"media_type":"application/pdf","sha256":"sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"},"producer":{"name":"test","version":"1.0.0"},"capabilities":{"spans":false,"char_offsets":false,"tables":false},"coordinate_system":{"unit":"centipoint","origin":"top-left"},"pages":[{"id":"page-1","index":1,"width":61200,"height":79200,"rotation":0}],"elements":[{"id":"block-1","page":"page-1","bbox":[7200,8400,54000,10200],"kind":"text_block","text":"héllo"}]}"#.to_owned()
    }
    #[test]
    fn accepts_unicode_and_projects_source() {
        let source = parse_grounding_json(valid().as_bytes()).unwrap();
        assert_eq!(source.elements()[0].text.as_deref(), Some("héllo"));
        assert_eq!(source.pages()[0].index, 1);
        assert!(source.fingerprint().unwrap().starts_with("sha256:"));
    }
    #[test]
    fn accepts_spans_offsets_and_non_overlapping_cells() {
        let source = parse_grounding_json(include_bytes!(
            "../../../schemas/examples/grounding-source-full.example.json"
        ))
        .unwrap();
        assert_eq!(source.spans().len(), 1);
        assert_eq!(source.tables()[0].cells.len(), 2);
    }
    #[test]
    fn rejects_duplicate_keys_at_nested_depth() {
        let input = valid().replacen(
            "\"unit\":\"centipoint\",\"origin\":\"top-left\"",
            "\"unit\":\"centipoint\",\"unit\":\"centipoint\",\"origin\":\"top-left\"",
            1,
        );
        assert_eq!(
            parse_grounding_json(input.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::DuplicateKey
        );
    }
    #[test]
    fn rejects_float_unknown_field_and_null() {
        let float = valid().replacen("61200", "61200.0", 1);
        assert_eq!(
            parse_grounding_json(float.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::InvalidJson
        );
        let unknown = valid().replacen("{\"artifact_type\"", "{\"extra\":1,\"artifact_type\"", 1);
        let error = parse_grounding_json(unknown.as_bytes()).unwrap_err();
        assert_eq!(error.code, GroundingJsonErrorCode::UnknownField);
        assert_eq!(error.path, "/extra");
        let null = valid().replacen("\"text\":\"héllo\"", "\"text\":null", 1);
        assert_eq!(
            parse_grounding_json(null.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::InvalidJson
        );
        assert_eq!(
            parse_grounding_json(b"{} {}\n").unwrap_err().code,
            GroundingJsonErrorCode::InvalidJson
        );
        assert_eq!(
            parse_grounding_json(&[0xef, 0xbb, 0xbf]).unwrap_err().code,
            GroundingJsonErrorCode::BomNotAllowed
        );
        assert_eq!(
            parse_grounding_json(&[0xff, 0xfe]).unwrap_err().code,
            GroundingJsonErrorCode::InvalidJson
        );
    }
    #[test]
    fn rejects_identity_capability_and_bounds() {
        let bad = valid().replace("ethos.grounding.v1", "other.v1");
        assert_eq!(
            parse_grounding_json(bad.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::UnsupportedVersion
        );
        let bad = valid().replace("\"spans\":false", "\"spans\":true");
        assert_eq!(
            parse_grounding_json(bad.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::InvalidCapabilities
        );
        let bad = valid().replace("54000,10200", "64000,10200");
        assert_eq!(
            parse_grounding_json(bad.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::InvalidBBox
        );
    }
    #[test]
    fn reports_stable_reference_order_and_id_errors() {
        // Append a second page that reuses the first page id.
        let duplicate_page = valid().replace(
            "}],\"elements\"",
            "},{\"id\":\"page-1\",\"index\":2,\"width\":61200,\"height\":79200,\"rotation\":0}],\"elements\"",
        );
        let error = parse_grounding_json(duplicate_page.as_bytes()).unwrap_err();
        assert_eq!(error.code, GroundingJsonErrorCode::DuplicateId);
        assert_eq!(error.path, "/pages/1/id");
        assert_eq!(
            error.message(),
            "make identifiers unique within their typed namespace"
        );

        let unknown_page = valid().replace("\"page\":\"page-1\"", "\"page\":\"missing\"");
        let error = parse_grounding_json(unknown_page.as_bytes()).unwrap_err();
        assert_eq!(error.code, GroundingJsonErrorCode::UnknownReference);
        assert_eq!(error.path, "/elements/0/page");

        let out_of_order = valid().replace("\"index\":1", "\"index\":2");
        let error = parse_grounding_json(out_of_order.as_bytes()).unwrap_err();
        assert_eq!(error.code, GroundingJsonErrorCode::InvalidOrder);
        assert_eq!(error.path, "/pages/0/index");
    }
    #[test]
    fn rejects_fixture_limits_and_unsafe_integers() {
        let cases = [
            (
                &include_bytes!(
                    "../../../schemas/examples/grounding-source-negative-duplicate.json"
                )[..],
                GroundingJsonErrorCode::DuplicateKey,
            ),
            (
                &include_bytes!("../../../schemas/examples/grounding-source-negative-float.json")[..],
                GroundingJsonErrorCode::InvalidJson,
            ),
            (
                &include_bytes!(
                    "../../../schemas/examples/grounding-source-negative-unsafe-integer.json"
                )[..],
                GroundingJsonErrorCode::LimitExceeded,
            ),
            (
                &include_bytes!("../../../schemas/examples/grounding-source-negative-depth.json")[..],
                GroundingJsonErrorCode::LimitExceeded,
            ),
        ];
        for (input, expected) in cases {
            assert_eq!(parse_grounding_json(input).unwrap_err().code, expected);
        }
        assert_eq!(
            parse_grounding_json(include_bytes!(
                "../../../schemas/examples/grounding-source-negative-unknown-field.json"
            ))
            .unwrap_err()
            .code,
            GroundingJsonErrorCode::UnknownField
        );
    }
    #[test]
    fn rejects_inconsistent_offsets_and_overlapping_cells() {
        let offset_mismatch =
            include_str!("../../../schemas/examples/grounding-source-full.example.json")
                .replace("\"char_end\": 5", "\"char_end\": 4");
        assert_eq!(
            parse_grounding_json(offset_mismatch.as_bytes())
                .unwrap_err()
                .code,
            GroundingJsonErrorCode::InvalidOffsets
        );
        let overlap = include_str!("../../../schemas/examples/grounding-source-full.example.json")
            .replace("\"row\": 0, \"col\": 1", "\"row\": 0, \"col\": 0");
        assert_eq!(
            parse_grounding_json(overlap.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::InvalidTable
        );
    }
    /// Build a spans+offsets artifact over `text`, with `span` selected by `[start, end)`.
    fn offsets_fixture(text: &str, span: &str, start: usize, end: usize) -> String {
        include_str!("../../../schemas/examples/grounding-source-full.example.json")
            .replace("\"text\": \"héllo\", \"element\"", &format!("\"text\": \"{span}\", \"element\""))
            .replace("\"text\": \"héllo\"", &format!("\"text\": \"{text}\""))
            .replace("\"char_start\": 0", &format!("\"char_start\": {start}"))
            .replace("\"char_end\": 5", &format!("\"char_end\": {end}"))
    }

    /// Offsets are Unicode scalar indexes, not UTF-16 code units and not grapheme clusters.
    ///
    /// Both vectors are where a JavaScript or Python mapper silently produces wrong offsets that
    /// still satisfy every structural rule: `"😀".length` is 2 in JavaScript but one scalar, and a
    /// combining mark renders as one character while occupying two scalars.
    #[test]
    fn offsets_are_unicode_scalar_indexes_for_emoji_and_combining_marks() {
        // "a😀b" is 3 scalars. Selecting the emoji alone is [1, 2).
        let astral = offsets_fixture("a😀b", "😀", 1, 2);
        assert_eq!(parse_grounding_json(astral.as_bytes()).unwrap().spans().len(), 1);

        // UTF-16 code units would make the emoji [1, 3) and "b" [3, 4). Both must fail.
        for (start, end) in [(1, 3), (3, 4)] {
            let utf16 = offsets_fixture("a😀b", "😀", start, end);
            assert_eq!(
                parse_grounding_json(utf16.as_bytes()).unwrap_err().code,
                GroundingJsonErrorCode::InvalidOffsets,
                "UTF-16 offsets [{start}, {end}) must not validate"
            );
        }

        // "e" + U+0301 renders as one grapheme but is 2 scalars; selecting it is [0, 2).
        let combining = offsets_fixture("e\u{301}x", "e\u{301}", 0, 2);
        assert_eq!(parse_grounding_json(combining.as_bytes()).unwrap().spans().len(), 1);

        // Counting the grapheme as one scalar selects only the base letter.
        let grapheme = offsets_fixture("e\u{301}x", "e\u{301}", 0, 1);
        assert_eq!(
            parse_grounding_json(grapheme.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::InvalidOffsets
        );

        // An end past the final scalar fails rather than panicking on the slice.
        let past_end = offsets_fixture("a😀b", "b", 2, 9);
        assert_eq!(
            parse_grounding_json(past_end.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::InvalidOffsets
        );
    }

    /// Accepted validator resource ceiling (decider, 2026-07-31).
    ///
    /// Measured at the frozen 1,000,000-element limit: 26.5 µs and 1.29 KB peak RSS per element.
    /// The ceiling carries roughly 1.5× headroom over that. See
    /// `docs/validation/v0-6-0-validator-resource-baseline.md`.
    ///
    /// Wall clock tracks element count rather than bytes, so a per-element figure is the
    /// meaningful shape. Peak RSS is recorded in that document rather than asserted here, because
    /// measuring it portably in-process would cost more than it proves.
    const CEILING_MICROS_PER_ELEMENT: f64 = 40.0;

    /// Opt-in because shared CI runners make wall-clock assertions flaky, and debug builds run
    /// roughly an order of magnitude slower than the release profile the ceiling describes.
    ///
    /// Run with:
    /// `ETHOS_CHECK_VALIDATOR_CEILING=1 cargo test --release -p ethos-doc-core validator_stays`
    #[test]
    fn validator_stays_within_the_accepted_resource_ceiling() {
        if std::env::var_os("ETHOS_CHECK_VALIDATOR_CEILING").is_none() {
            eprintln!("skipping validator ceiling check: set ETHOS_CHECK_VALIDATOR_CEILING=1");
            return;
        }
        assert!(
            !cfg!(debug_assertions),
            "the ceiling describes the release profile; re-run with --release"
        );

        // A tenth of the frozen element limit. Cost is linear, so this is representative while
        // staying fast enough to run on demand.
        const ELEMENTS: usize = 100_000;
        let mut artifact = String::with_capacity(ELEMENTS * 160);
        artifact.push_str(
            r#"{"artifact_type":"ethos.grounding.v1","schema_version":"1.0.0","source":{"media_type":"application/pdf","sha256":"sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"},"producer":{"name":"ceiling","version":"1.0.0"},"capabilities":{"spans":false,"char_offsets":false,"tables":false},"coordinate_system":{"unit":"centipoint","origin":"top-left"},"pages":[{"id":"page-1","index":1,"width":61200,"height":79200,"rotation":0}],"elements":["#,
        );
        for index in 0..ELEMENTS {
            if index > 0 {
                artifact.push(',');
            }
            artifact.push_str(&format!(
                r#"{{"id":"block-{index}","page":"page-1","bbox":[100,100,5000,900],"kind":"text_block","text":"Revenue line {index} increased materially."}}"#
            ));
        }
        artifact.push_str("]}");

        let started = std::time::Instant::now();
        let source = parse_grounding_json(artifact.as_bytes()).expect("ceiling fixture is valid");
        let micros_per_element = started.elapsed().as_secs_f64() * 1e6 / ELEMENTS as f64;

        assert_eq!(source.counts().1, ELEMENTS);
        assert!(
            micros_per_element <= CEILING_MICROS_PER_ELEMENT,
            "validation cost {micros_per_element:.1} µs/element, over the accepted ceiling of \
             {CEILING_MICROS_PER_ELEMENT:.1} µs/element. Re-measure and update \
             docs/validation/v0-6-0-validator-resource-baseline.md before raising this."
        );
    }

    #[test]
    fn rejects_oversized_strings_before_typed_validation() {
        let oversized = valid().replace("héllo", &"x".repeat(MAX_STRING_BYTES + 1));
        assert_eq!(
            parse_grounding_json(oversized.as_bytes()).unwrap_err().code,
            GroundingJsonErrorCode::LimitExceeded
        );
    }
    #[test]
    fn double_run_fingerprint_is_stable() {
        let bytes = valid();
        let a = parse_grounding_json(bytes.as_bytes()).unwrap();
        let b = parse_grounding_json(bytes.as_bytes()).unwrap();
        assert_eq!(a.representation_sha256(), b.representation_sha256());
    }
    #[test]
    fn rejection_code_and_path_are_stable_across_runs() {
        let input = include_bytes!(
            "../../../schemas/examples/grounding-source-negative-unknown-field.json"
        );
        let first = parse_grounding_json(input).unwrap_err();
        let second = parse_grounding_json(input).unwrap_err();
        assert_eq!(first, second);
    }
}
