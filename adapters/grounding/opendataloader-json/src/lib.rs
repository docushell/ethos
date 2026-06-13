//! # OpenDataLoader JSON grounding adapter (Milestone A stub)
//!
//! Proves that foreign parser output can enter the [`GroundingSource`] interface
//! (PRD §16 acceptance): maps parser identity, pages, elements, optional tables,
//! bbox, text, and capabilities. This is **not** an ODL fork — ODL output is
//! consumed as data from a pinned upstream version (plan §6.5).
//!
//! ## Stub mapping assumptions (hardened against pinned real output in Milestone B)
//!
//! The stub reads a conservative subset:
//! `{"tool": {"name", "version"}, "pages": [{"number", "width", "height"}],
//!   "elements": [{"id"?, "page", "bbox": [x0,y0,x1,y1], "type"?, "text"?}],
//!   "tables"?: [{"id", "page", "bbox", "cells": [{"row", "col", "row_span"?,
//!     "col_span"?, "bbox", "text"}]}]}`
//!
//! - Geometry: source floats (points) are scaled to **centipoints** (×100,
//!   half-away-from-zero) so units align with Ethos quanta. Origin is declared
//!   [`CoordinateOrigin::Unknown`] until the B-alpha pin verifies ODL's convention —
//!   capability-driven downgrade, never silent assumption.
//! - No spans, no char offsets, no fingerprint, no crops: declared `false`.
//!   Table capability is declared only when a `tables` array is present.
//!   Verification surfaces missing capabilities as `capability_limited` (PRD §5.5).

#![forbid(unsafe_code)]
#![warn(missing_docs)]

use std::collections::HashSet;

use ethos_core::grounding::{
    Capabilities, CoordinateOrigin, GroundingCell, GroundingElement, GroundingSource,
    GroundingTable, PageGeometry, ParserIdentity,
};
use serde_json::Value;

/// Adapter version, reported in `ParserIdentity::adapter_version`.
pub const ADAPTER_VERSION: &str = "0.1.0";

/// Mapping failure: input is valid JSON but not recognizable ODL output.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AdapterError {
    /// Deterministic message.
    pub message: String,
}

impl core::fmt::Display for AdapterError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str(&self.message)
    }
}
impl std::error::Error for AdapterError {}

fn err(message: &str) -> AdapterError {
    AdapterError {
        message: message.to_string(),
    }
}

fn string_field(
    object: &Value,
    field: &str,
    missing_message: &str,
) -> Result<String, AdapterError> {
    let value = object
        .get(field)
        .and_then(Value::as_str)
        .ok_or_else(|| err(missing_message))?;
    if value.trim().is_empty() {
        return Err(err(missing_message));
    }
    Ok(value.to_string())
}

fn u32_field(
    object: &Value,
    field: &str,
    missing_message: &str,
    overflow_message: &str,
) -> Result<u32, AdapterError> {
    let value = object
        .get(field)
        .and_then(Value::as_u64)
        .ok_or_else(|| err(missing_message))?;
    u32::try_from(value).map_err(|_| err(overflow_message))
}

/// A parsed ODL JSON document exposed as a [`GroundingSource`].
#[derive(Debug, Clone)]
pub struct OdlJsonSource {
    parser_name: String,
    parser_version: String,
    pages: Vec<PageGeometry>,
    elements: Vec<GroundingElement>,
    tables_capable: bool,
    tables: Vec<GroundingTable>,
}

/// Scale points → centipoints, half-away-from-zero.
///
/// This intentionally mirrors `ethos_core::geom::quantize(pts, 100)` while staying local:
/// the production adapter depends only on the parser-free `grounding` feature.
fn to_centipoints(v: f64) -> Option<i64> {
    if !v.is_finite() {
        return None;
    }
    let scaled = v * 100.0;
    let rounded = if scaled >= 0.0 {
        (scaled + 0.5).floor()
    } else {
        (scaled - 0.5).ceil()
    };
    if rounded.abs() > 9_007_199_254_740_991.0 {
        return None;
    }
    Some(rounded as i64)
}

fn positive_centipoints(object: &Value, field: &str, message: &str) -> Result<i64, AdapterError> {
    let raw = object
        .get(field)
        .and_then(Value::as_f64)
        .ok_or_else(|| err(message))?;
    let value = to_centipoints(raw).ok_or_else(|| err(message))?;
    if value <= 0 {
        return Err(err(message));
    }
    Ok(value)
}

fn bbox_from(value: &Value) -> Result<[i64; 4], AdapterError> {
    let arr = value
        .as_array()
        .ok_or_else(|| err("bbox is not an array"))?;
    if arr.len() != 4 {
        return Err(err("bbox must have 4 entries"));
    }
    let mut out = [0i64; 4];
    for (i, v) in arr.iter().enumerate() {
        let f = v
            .as_f64()
            .ok_or_else(|| err("bbox entry is not a number"))?;
        out[i] = to_centipoints(f).ok_or_else(|| err("bbox entry is not finite"))?;
    }
    if out[0] > out[2] || out[1] > out[3] {
        return Err(err("bbox is malformed (x0>x1 or y0>y1)"));
    }
    Ok(out)
}

fn optional_positive_u32_field(
    object: &Value,
    field: &str,
    default: u32,
    overflow_message: &str,
    zero_message: &str,
) -> Result<u32, AdapterError> {
    let Some(value) = object.get(field) else {
        return Ok(default);
    };
    let Some(raw) = value.as_u64() else {
        return Err(err(overflow_message));
    };
    let value = u32::try_from(raw).map_err(|_| err(overflow_message))?;
    if value == 0 {
        return Err(err(zero_message));
    }
    Ok(value)
}

fn parse_tool(root: &Value) -> Result<(String, String), AdapterError> {
    let tool = root
        .get("tool")
        .ok_or_else(|| err("missing 'tool' object"))?;
    Ok((
        string_field(tool, "name", "missing tool.name")?,
        string_field(tool, "version", "missing tool.version")?,
    ))
}

fn parse_pages(root: &Value) -> Result<(Vec<PageGeometry>, HashSet<u32>), AdapterError> {
    let mut pages = Vec::new();
    let mut page_numbers = HashSet::new();
    for page in root
        .get("pages")
        .and_then(Value::as_array)
        .ok_or_else(|| err("missing 'pages' array"))?
    {
        let number = u32_field(
            page,
            "number",
            "missing page.number",
            "page.number must fit u32",
        )?;
        if number == 0 {
            return Err(err("page.number must be 1-based"));
        }
        if !page_numbers.insert(number) {
            return Err(err("duplicate page.number"));
        }
        let width = positive_centipoints(page, "width", "page width must be positive finite")?;
        let height = positive_centipoints(page, "height", "page height must be positive finite")?;
        pages.push(PageGeometry {
            id: format!("page-{number}"),
            index: number,
            width,
            height,
            rotation: 0,
        });
    }
    pages.sort_by_key(|p| p.index);
    Ok((pages, page_numbers))
}

fn parse_elements(
    root: &Value,
    page_numbers: &HashSet<u32>,
) -> Result<Vec<GroundingElement>, AdapterError> {
    let mut elements = Vec::new();
    let mut element_ids = HashSet::new();
    for (i, el) in root
        .get("elements")
        .and_then(Value::as_array)
        .ok_or_else(|| err("missing 'elements' array"))?
        .iter()
        .enumerate()
    {
        let page_number = u32_field(
            el,
            "page",
            "missing element.page",
            "element.page must fit u32",
        )?;
        if page_number == 0 {
            return Err(err("element.page must be 1-based"));
        }
        if !page_numbers.contains(&page_number) {
            return Err(err("element.page references unknown page"));
        }
        let id = el
            .get("id")
            .and_then(Value::as_str)
            .map(str::trim)
            .filter(|id| !id.is_empty())
            .map(str::to_string)
            .unwrap_or_else(|| format!("odl-el-{}", i + 1));
        if !element_ids.insert(id.clone()) {
            return Err(err("duplicate element.id"));
        }
        let bbox = bbox_from(el.get("bbox").ok_or_else(|| err("missing element.bbox"))?)?;
        let kind = el
            .get("type")
            .and_then(Value::as_str)
            .map(str::trim)
            .filter(|kind| !kind.is_empty())
            .unwrap_or("unknown")
            .to_ascii_lowercase();
        let text = el.get("text").and_then(Value::as_str).map(str::to_string);
        elements.push(GroundingElement {
            id,
            page: format!("page-{page_number}"),
            bbox,
            kind,
            text,
        });
    }
    Ok(elements)
}

fn parse_tables(
    root: &Value,
    page_numbers: &HashSet<u32>,
) -> Result<(bool, Vec<GroundingTable>), AdapterError> {
    let Some(tables_value) = root.get("tables") else {
        return Ok((false, Vec::new()));
    };

    let mut tables = Vec::new();
    let mut table_ids = HashSet::new();
    let table_array = tables_value
        .as_array()
        .ok_or_else(|| err("'tables' is not an array"))?;
    for table in table_array {
        let id = string_field(table, "id", "missing table.id")?;
        if !table_ids.insert(id.clone()) {
            return Err(err("duplicate table.id"));
        }
        let page_number = u32_field(
            table,
            "page",
            "missing table.page",
            "table.page must fit u32",
        )?;
        if page_number == 0 {
            return Err(err("table.page must be 1-based"));
        }
        if !page_numbers.contains(&page_number) {
            return Err(err("table.page references unknown page"));
        }
        let bbox = bbox_from(table.get("bbox").ok_or_else(|| err("missing table.bbox"))?)?;
        let cells = parse_table_cells(table)?;
        tables.push(GroundingTable {
            id,
            page: format!("page-{page_number}"),
            bbox,
            cells,
        });
    }
    Ok((true, tables))
}

fn parse_table_cells(table: &Value) -> Result<Vec<GroundingCell>, AdapterError> {
    let mut cells = Vec::new();
    for cell in table
        .get("cells")
        .and_then(Value::as_array)
        .ok_or_else(|| err("missing table.cells array"))?
    {
        let candidate = parse_table_cell(cell)?;
        if cells_overlap(&cells, &candidate) {
            return Err(err("overlapping table cell address range"));
        }
        cells.push(candidate);
    }
    Ok(cells)
}

fn parse_table_cell(cell: &Value) -> Result<GroundingCell, AdapterError> {
    let row = u32_field(cell, "row", "missing cell.row", "cell.row must fit u32")?;
    let col = u32_field(cell, "col", "missing cell.col", "cell.col must fit u32")?;
    let row_span = optional_positive_u32_field(
        cell,
        "row_span",
        1,
        "cell.row_span must fit u32",
        "cell.row_span must be positive",
    )?;
    let col_span = optional_positive_u32_field(
        cell,
        "col_span",
        1,
        "cell.col_span must fit u32",
        "cell.col_span must be positive",
    )?;
    let bbox = bbox_from(cell.get("bbox").ok_or_else(|| err("missing cell.bbox"))?)?;
    let text = string_field(cell, "text", "missing cell.text")?;
    Ok(GroundingCell {
        row,
        col,
        row_span,
        col_span,
        bbox,
        text,
    })
}

impl OdlJsonSource {
    /// Build from ODL JSON text.
    pub fn from_json_str(json: &str) -> Result<Self, AdapterError> {
        let root: Value = serde_json::from_str(json).map_err(|_| err("input is not valid JSON"))?;
        Self::from_value(&root)
    }

    /// Build from a parsed JSON value.
    pub fn from_value(root: &Value) -> Result<Self, AdapterError> {
        let (parser_name, parser_version) = parse_tool(root)?;
        let (pages, page_numbers) = parse_pages(root)?;
        let elements = parse_elements(root, &page_numbers)?;
        let (tables_capable, tables) = parse_tables(root, &page_numbers)?;

        Ok(OdlJsonSource {
            parser_name,
            parser_version,
            pages,
            elements,
            tables_capable,
            tables,
        })
    }
}

impl GroundingSource for OdlJsonSource {
    fn parser(&self) -> ParserIdentity {
        ParserIdentity {
            name: self.parser_name.clone(),
            version: self.parser_version.clone(),
            adapter: Some("opendataloader-json".to_string()),
            adapter_version: Some(ADAPTER_VERSION.to_string()),
        }
    }

    fn capabilities(&self) -> Capabilities {
        Capabilities {
            spans: false,
            char_offsets: false,
            tables: self.tables_capable,
            fingerprint: false,
            coordinate_origin: CoordinateOrigin::Unknown,
            crop_support: false,
        }
    }

    fn fingerprint(&self) -> Option<String> {
        None
    }

    fn pages(&self) -> Vec<PageGeometry> {
        self.pages.clone()
    }

    fn elements(&self) -> Vec<GroundingElement> {
        self.elements.clone()
    }

    fn element_by_id(&self, id: &str) -> Option<GroundingElement> {
        self.elements
            .iter()
            .find(|element| element.id == id)
            .cloned()
    }

    fn tables(&self) -> Vec<GroundingTable> {
        self.tables.clone()
    }
}

fn cells_overlap(cells: &[GroundingCell], candidate: &GroundingCell) -> bool {
    cells.iter().any(|cell| {
        ranges_overlap(
            cell.row,
            cell.row.saturating_add(cell.row_span),
            candidate.row,
            candidate.row.saturating_add(candidate.row_span),
        ) && ranges_overlap(
            cell.col,
            cell.col.saturating_add(cell.col_span),
            candidate.col,
            candidate.col.saturating_add(candidate.col_span),
        )
    })
}

fn ranges_overlap(a_start: u32, a_end: u32, b_start: u32, b_end: u32) -> bool {
    a_start < b_end && b_start < a_end
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = include_str!("../tests/fixtures/odl-sample.json");

    #[test]
    fn maps_the_documented_subset() {
        let src = OdlJsonSource::from_json_str(SAMPLE).unwrap();
        let id = src.parser();
        assert_eq!(id.name, "opendataloader-pdf");
        assert_eq!(id.adapter.as_deref(), Some("opendataloader-json"));

        let pages = src.pages();
        assert_eq!(pages.len(), 1);
        assert_eq!(pages[0].index, 1);
        assert_eq!(pages[0].width, 61200); // 612pt → centipoints

        let els = src.elements();
        assert_eq!(els.len(), 2);
        assert_eq!(els[0].kind, "heading");
        assert_eq!(els[0].text.as_deref(), Some("Quarterly Report"));
        assert_eq!(els[0].bbox, [7200, 7200, 30480, 9000]);

        let tables = src.tables();
        assert_eq!(tables.len(), 1);
        assert_eq!(tables[0].id, "odl-t1");
        assert_eq!(tables[0].page, "page-1");
        assert_eq!(tables[0].cells.len(), 2);
        assert_eq!(tables[0].cells[1].text, "$12.4M");
        assert_eq!(tables[0].cells[1].bbox, [30600, 16500, 54000, 20000]);

        let caps = src.capabilities();
        assert!(caps.tables);
        assert!(!caps.spans && !caps.fingerprint && !caps.crop_support);
        assert_eq!(caps.coordinate_origin, CoordinateOrigin::Unknown);
        assert!(src.fingerprint().is_none());
    }

    #[test]
    fn centipoint_quantization_matches_core_semantics() {
        let samples = [
            f64::NAN,
            f64::INFINITY,
            1e17,
            -0.0,
            0.0,
            0.004,
            -0.004,
            0.005,
            -0.005,
            1.234,
            -1.234,
            612.0,
            -612.0,
        ];

        for sample in samples {
            assert_eq!(
                to_centipoints(sample),
                ethos_core::geom::quantize(sample, 100).ok()
            );
        }
    }

    #[test]
    fn rejects_unrecognizable_input() {
        assert!(OdlJsonSource::from_json_str("not json").is_err());
        assert!(OdlJsonSource::from_json_str("{}").is_err());
        assert!(OdlJsonSource::from_json_str(r#"{"tool":{"name":"x","version":"1"},"pages":[],"elements":[{"page":1,"bbox":[5,5,1,1]}]}"#).is_err());
    }

    fn assert_error_contains(json: &str, expected: &str) {
        let error = OdlJsonSource::from_json_str(json).unwrap_err();
        assert!(
            error.message.contains(expected),
            "expected error containing {expected:?}, got {:?}",
            error.message
        );
    }

    #[test]
    fn rejects_ambiguous_or_unbounded_identity_fields() {
        assert_error_contains(
            r#"{"tool":{"name":" ","version":"1"},"pages":[],"elements":[]}"#,
            "missing tool.name",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792},{"number":1,"width":612,"height":792}],"elements":[]}"#,
            "duplicate page.number",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[{"id":"dup","page":1,"bbox":[1,1,2,2]},{"id":"dup","page":1,"bbox":[3,3,4,4]}]}"#,
            "duplicate element.id",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[{"id":"odl-el-2","page":1,"bbox":[1,1,2,2]},{"page":1,"bbox":[3,3,4,4]}]}"#,
            "duplicate element.id",
        );
    }

    #[test]
    fn rejects_invalid_page_numbers_and_references() {
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":0,"width":612,"height":792}],"elements":[]}"#,
            "page.number must be 1-based",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":4294967296,"width":612,"height":792}],"elements":[]}"#,
            "page.number must fit u32",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[{"page":2,"bbox":[1,1,2,2]}]}"#,
            "element.page references unknown page",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[{"page":4294967296,"bbox":[1,1,2,2]}]}"#,
            "element.page must fit u32",
        );
    }

    #[test]
    fn rejects_missing_or_nonpositive_page_dimensions() {
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"height":792}],"elements":[]}"#,
            "page width must be positive finite",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":0,"height":792}],"elements":[]}"#,
            "page width must be positive finite",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":-1}],"elements":[]}"#,
            "page height must be positive finite",
        );
    }

    #[test]
    fn rejects_malformed_tables() {
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[],"tables":[{"id":"t1","page":2,"bbox":[1,1,2,2],"cells":[]}]}"#,
            "table.page references unknown page",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[],"tables":[{"id":"t1","page":1,"bbox":[1,1,2,2],"cells":[{"row":1,"col":1,"bbox":[1,1,2,2],"text":"x"},{"row":1,"col":1,"bbox":[1,1,2,2],"text":"y"}]}]}"#,
            "overlapping table cell address range",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[],"tables":[{"id":"t1","page":1,"bbox":[1,1,2,2],"cells":[{"row":0,"col":0,"row_span":2,"bbox":[1,1,2,2],"text":"x"},{"row":1,"col":0,"bbox":[1,1,2,2],"text":"y"}]}]}"#,
            "overlapping table cell address range",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[],"tables":[{"id":"t1","page":1,"bbox":[1,1,2,2],"cells":[{"row":1,"col":1,"row_span":0,"bbox":[1,1,2,2],"text":"x"}]}]}"#,
            "cell.row_span must be positive",
        );
    }
}
