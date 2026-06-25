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

//! # OpenDataLoader JSON grounding adapter (B alpha)
//!
//! Proves that foreign parser output can enter the [`GroundingSource`] interface
//! (PRD §16 acceptance): maps parser identity, pages, elements, optional synthetic
//! tables, bbox, text, and capabilities. This is **not** an ODL fork — ODL output
//! is consumed as data from a pinned upstream version (plan §6.5).
//!
//! ## Stub mapping assumptions (hardened against pinned real output in Milestone B)
//!
//! The adapter reads a conservative subset:
//! `{"tool": {"name", "version"}, "pages": [{"number", "width", "height"}],
//!   "elements": [{"id"?, "page", "bbox": [x0,y0,x1,y1], "type"?, "text"?}],
//!   "tables"?: [{"id", "page", "bbox", "cells": [{"row", "col", "row_span"?,
//!     "col_span"?, "bbox", "text"}]}]}`
//!
//! It also accepts the pinned OpenDataLoader 2.4.x JSON shape:
//! `{"file name", "number of pages", "kids": [{"type", "id"?, "page number",
//! "bounding box", "content"?, ...}]}`. That shape does not expose parser version
//! or page dimensions, so version is reported as `"unknown"` and page extents are
//! derived from observed bounding boxes. Coordinate origin remains unknown.
//!
//! - Geometry: source floats (points) are scaled to **centipoints** (×100,
//!   half-away-from-zero) so units align with Ethos quanta. Origin is declared
//!   [`CoordinateOrigin::Unknown`] until the B-alpha pin verifies ODL's convention —
//!   capability-driven downgrade, never silent assumption.
//! - No spans, no char offsets, no fingerprint, no crops: declared `false`.
//!   Table capability is declared when a `tables` array is present in the
//!   documented subset or when real ODL-style `rows[].cells` table structures carry
//!   enough explicit page/bbox/text data to map deterministic cells.
//!   Verification surfaces missing capabilities as `capability_limited` (PRD §5.5).

#![forbid(unsafe_code)]
#![warn(missing_docs)]

use std::collections::{HashMap, HashSet};

use ethos_core::grounding::{
    Capabilities, CoordinateOrigin, GroundingCell, GroundingElement, GroundingSource,
    GroundingTable, PageGeometry, ParserIdentity,
};
use serde_json::Value;

/// Adapter version, reported in `ParserIdentity::adapter_version`.
pub const ADAPTER_VERSION: &str = "0.1.0";

const REAL_ODL_MAX_PAGES: u32 = 10_000;

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
    if out[0] == out[2] || out[1] == out[3] {
        return Err(err("bbox must have positive area"));
    }
    Ok(out)
}

fn bbox_within_page(bbox: [i64; 4], page: &PageGeometry, label: &str) -> Result<(), AdapterError> {
    if bbox[0] < 0 || bbox[1] < 0 || bbox[2] > page.width || bbox[3] > page.height {
        return Err(err(&format!("{label} bbox exceeds page bounds")));
    }
    Ok(())
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
    pages_by_number: &HashMap<u32, PageGeometry>,
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
        let Some(page) = pages_by_number.get(&page_number) else {
            return Err(err("element.page references unknown page"));
        };
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
        bbox_within_page(bbox, page, "element")?;
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
    pages_by_number: &HashMap<u32, PageGeometry>,
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
        let Some(page) = pages_by_number.get(&page_number) else {
            return Err(err("table.page references unknown page"));
        };
        let bbox = bbox_from(table.get("bbox").ok_or_else(|| err("missing table.bbox"))?)?;
        bbox_within_page(bbox, page, "table")?;
        let cells = parse_table_cells(table)?;
        for cell in &cells {
            bbox_within_page(cell.bbox, page, "cell")?;
        }
        tables.push(GroundingTable {
            id,
            page: format!("page-{page_number}"),
            bbox,
            cells,
        });
    }
    Ok((true, tables))
}

fn parse_real_odl(root: &Value) -> Result<OdlJsonSource, AdapterError> {
    let page_count = u32_field(
        root,
        "number of pages",
        "missing number of pages",
        "number of pages must fit u32",
    )?;
    if page_count == 0 {
        return Err(err("number of pages must be positive"));
    }
    if page_count > REAL_ODL_MAX_PAGES {
        return Err(err("number of pages exceeds adapter limit"));
    }
    let kids = root
        .get("kids")
        .and_then(Value::as_array)
        .ok_or_else(|| err("missing kids array"))?;

    let mut page_extents = vec![[1i64, 1i64]; page_count as usize];
    let mut elements = Vec::new();
    let mut element_ids = HashSet::new();
    let mut tables = Vec::new();
    let mut table_ids = HashSet::new();
    let mut next_synthetic_id = 1u32;
    let mut next_synthetic_table_id = 1u32;
    for kid in kids {
        collect_real_tables(
            kid,
            page_count,
            &mut tables,
            &mut table_ids,
            &mut next_synthetic_table_id,
        )?;
        parse_real_content_element(
            kid,
            page_count,
            &mut page_extents,
            &mut elements,
            &mut element_ids,
            &mut next_synthetic_id,
        )?;
    }

    let pages = page_extents
        .into_iter()
        .enumerate()
        .map(|(index, [width, height])| PageGeometry {
            id: format!("page-{}", index + 1),
            index: (index + 1) as u32,
            width,
            height,
            rotation: 0,
        })
        .collect();

    Ok(OdlJsonSource {
        parser_name: "opendataloader-pdf".to_string(),
        parser_version: "unknown".to_string(),
        pages,
        elements,
        tables_capable: !tables.is_empty(),
        tables,
    })
}

fn collect_real_tables(
    node: &Value,
    page_count: u32,
    tables: &mut Vec<GroundingTable>,
    table_ids: &mut HashSet<String>,
    next_synthetic_table_id: &mut u32,
) -> Result<(), AdapterError> {
    if real_node_has_table_fields(node) {
        let table = parse_real_table(node, page_count, next_synthetic_table_id)?;
        if !table_ids.insert(table.id.clone()) {
            return Err(err("duplicate real table id"));
        }
        tables.push(table);
    }
    for child in real_child_elements(node)? {
        collect_real_tables(
            child,
            page_count,
            tables,
            table_ids,
            next_synthetic_table_id,
        )?;
    }
    Ok(())
}

fn real_node_has_table_fields(node: &Value) -> bool {
    node.get("rows").is_some()
        && (node.get("type").is_some()
            || node.get("id").is_some()
            || node.get("page number").is_some()
            || node.get("bounding box").is_some())
}

fn parse_real_table(
    node: &Value,
    page_count: u32,
    next_synthetic_table_id: &mut u32,
) -> Result<GroundingTable, AdapterError> {
    let page_number = u32_field(
        node,
        "page number",
        "missing table page number",
        "table page number must fit u32",
    )?;
    if page_number == 0 || page_number > page_count {
        return Err(err("table page number references unknown page"));
    }
    let bbox = bbox_from(
        node.get("bounding box")
            .ok_or_else(|| err("missing table bounding box"))?,
    )?;
    let id = real_table_id(node, next_synthetic_table_id)?;
    let rows = node
        .get("rows")
        .and_then(Value::as_array)
        .ok_or_else(|| err("rows must be an array"))?;
    let mut cells = Vec::new();
    for (row_index, row) in rows.iter().enumerate() {
        let row = row
            .as_object()
            .ok_or_else(|| err("row must be an object"))?;
        let cells_value = row
            .get("cells")
            .and_then(Value::as_array)
            .ok_or_else(|| err("row cells must be an array"))?;
        for (col_index, cell) in cells_value.iter().enumerate() {
            cells.push(parse_real_table_cell(
                cell,
                page_count,
                page_number,
                (row_index + 1) as u32,
                (col_index + 1) as u32,
            )?);
        }
    }
    Ok(GroundingTable {
        id,
        page: format!("page-{page_number}"),
        bbox,
        cells,
    })
}

fn real_table_id(node: &Value, next_synthetic_table_id: &mut u32) -> Result<String, AdapterError> {
    if let Some(raw) = node.get("id") {
        if let Some(id) = raw.as_u64() {
            let id = u32::try_from(id).map_err(|_| err("table id must fit u32"))?;
            return Ok(format!("odl-{id}"));
        }
        if let Some(id) = raw.as_str().map(str::trim).filter(|id| !id.is_empty()) {
            return Ok(format!("odl-{id}"));
        }
        return Err(err("table id must be integer or non-empty string"));
    }
    let id = *next_synthetic_table_id;
    *next_synthetic_table_id = next_synthetic_table_id.saturating_add(1);
    Ok(format!("odl-table-{id}"))
}

fn parse_real_table_cell(
    cell: &Value,
    page_count: u32,
    table_page_number: u32,
    row: u32,
    col: u32,
) -> Result<GroundingCell, AdapterError> {
    let page_number = u32_field(
        cell,
        "page number",
        "missing cell page number",
        "cell page number must fit u32",
    )?;
    if page_number == 0 || page_number > page_count {
        return Err(err("cell page number references unknown page"));
    }
    if page_number != table_page_number {
        return Err(err("cell page number must match table page number"));
    }
    let bbox = bbox_from(
        cell.get("bounding box")
            .ok_or_else(|| err("missing cell bounding box"))?,
    )?;
    let text = real_content_text(cell)?
        .filter(|text| !text.trim().is_empty())
        .ok_or_else(|| err("missing cell content"))?;
    Ok(GroundingCell {
        row,
        col,
        row_span: 1,
        col_span: 1,
        bbox,
        text,
    })
}

fn parse_real_content_element(
    node: &Value,
    page_count: u32,
    page_extents: &mut [[i64; 2]],
    elements: &mut Vec<GroundingElement>,
    element_ids: &mut HashSet<String>,
    next_synthetic_id: &mut u32,
) -> Result<Option<String>, AdapterError> {
    let children = real_child_elements(node)?;
    if !real_node_has_element_fields(node) {
        if children.is_empty() {
            return Err(err(
                "content node has no element fields or child containers",
            ));
        }
        let mut parts = Vec::new();
        for child in children {
            if let Some(text) = parse_real_content_element(
                child,
                page_count,
                page_extents,
                elements,
                element_ids,
                next_synthetic_id,
            )? {
                parts.push(text);
            }
        }
        return Ok(join_real_text(parts));
    }

    let kind = real_content_kind(node)?;
    let page_number = u32_field(
        node,
        "page number",
        "missing page number",
        "page number must fit u32",
    )?;
    if page_number == 0 || page_number > page_count {
        return Err(err("page number references unknown page"));
    }
    let bbox = bbox_from(
        node.get("bounding box")
            .ok_or_else(|| err("missing bounding box"))?,
    )?;
    update_page_extent(page_extents, page_number, bbox);

    let id = real_element_id(node, next_synthetic_id)?;
    if !element_ids.insert(id.clone()) {
        return Err(err("duplicate content id"));
    }
    let element_index = elements.len();
    elements.push(GroundingElement {
        id,
        page: format!("page-{page_number}"),
        bbox,
        kind,
        text: None,
    });

    let mut parts = Vec::new();
    if let Some(text) = real_own_text(node)? {
        if !text.is_empty() {
            parts.push(text.to_string());
        }
    }
    for child in children {
        if let Some(text) = parse_real_content_element(
            child,
            page_count,
            page_extents,
            elements,
            element_ids,
            next_synthetic_id,
        )? {
            parts.push(text);
        }
    }

    let text = join_real_text(parts);
    elements[element_index].text = text.clone();
    Ok(text)
}

fn real_node_has_element_fields(node: &Value) -> bool {
    node.get("type").is_some()
        || node.get("id").is_some()
        || node.get("page number").is_some()
        || node.get("bounding box").is_some()
        || node.get("content").is_some()
        || node.get("text").is_some()
}

fn real_content_kind(node: &Value) -> Result<String, AdapterError> {
    let Some(kind) = node.get("type") else {
        return Ok("unknown".to_string());
    };
    let kind = kind
        .as_str()
        .ok_or_else(|| err("content type must be a string"))?
        .trim();
    if kind.is_empty() {
        Ok("unknown".to_string())
    } else {
        Ok(kind.to_ascii_lowercase())
    }
}

fn update_page_extent(page_extents: &mut [[i64; 2]], page_number: u32, bbox: [i64; 4]) {
    let extent = &mut page_extents[(page_number - 1) as usize];
    extent[0] = extent[0].max(bbox[2]);
    extent[1] = extent[1].max(bbox[3]);
}

fn real_element_id(node: &Value, next_synthetic_id: &mut u32) -> Result<String, AdapterError> {
    if let Some(raw) = node.get("id") {
        if let Some(id) = raw.as_u64() {
            let id = u32::try_from(id).map_err(|_| err("content id must fit u32"))?;
            return Ok(format!("odl-{id}"));
        }
        if let Some(id) = raw.as_str().map(str::trim).filter(|id| !id.is_empty()) {
            return Ok(format!("odl-{id}"));
        }
        return Err(err("content id must be integer or non-empty string"));
    }
    let id = *next_synthetic_id;
    *next_synthetic_id = next_synthetic_id.saturating_add(1);
    Ok(format!("odl-el-{id}"))
}

fn real_content_text(node: &Value) -> Result<Option<String>, AdapterError> {
    let mut parts = Vec::new();
    collect_real_text(node, &mut parts)?;
    Ok(join_real_borrowed_text(parts))
}

fn join_real_text(parts: Vec<String>) -> Option<String> {
    if parts.is_empty() {
        None
    } else {
        Some(parts.join("\n"))
    }
}

fn join_real_borrowed_text(parts: Vec<&str>) -> Option<String> {
    if parts.is_empty() {
        None
    } else {
        Some(parts.join("\n"))
    }
}

fn collect_real_text<'a>(node: &'a Value, parts: &mut Vec<&'a str>) -> Result<(), AdapterError> {
    if let Some(text) = real_own_text(node)? {
        if !text.is_empty() {
            parts.push(text);
        }
    }
    for child in real_child_elements(node)? {
        collect_real_text(child, parts)?;
    }
    Ok(())
}

fn real_own_text(node: &Value) -> Result<Option<&str>, AdapterError> {
    let content = real_string_alias(node, "content", "content must be a string")?;
    let text = real_string_alias(node, "text", "text must be a string")?;
    match (content, text) {
        (None, None) => Ok(None),
        (Some(content), None) => Ok(Some(content)),
        (None, Some(text)) => Ok(Some(text)),
        (Some(content), Some(text)) => {
            let content_empty = content.is_empty();
            let text_empty = text.is_empty();
            if content_empty && text_empty {
                Ok(None)
            } else if content_empty {
                Ok(Some(text))
            } else if text_empty || content == text {
                Ok(Some(content))
            } else {
                Err(err("content and text fields disagree"))
            }
        }
    }
}

fn real_string_alias<'a>(
    node: &'a Value,
    field: &str,
    message: &str,
) -> Result<Option<&'a str>, AdapterError> {
    let Some(value) = node.get(field) else {
        return Ok(None);
    };
    value.as_str().map(Some).ok_or_else(|| err(message))
}

fn real_child_elements(node: &Value) -> Result<Vec<&Value>, AdapterError> {
    let mut children = Vec::new();
    children.extend(real_child_alias_array(
        node,
        &[
            ("kids", "kids must be an array"),
            ("children", "children must be an array"),
        ],
        "ambiguous kids/children containers",
    )?);
    children.extend(real_child_alias_array(
        node,
        &[
            ("list items", "list items must be an array"),
            ("list_items", "list_items must be an array"),
        ],
        "ambiguous list item containers",
    )?);
    if let Some(rows_value) = node.get("rows") {
        let rows = rows_value
            .as_array()
            .ok_or_else(|| err("rows must be an array"))?;
        for row in rows {
            let row = row
                .as_object()
                .ok_or_else(|| err("row must be an object"))?;
            if let Some(cells_value) = row.get("cells") {
                let cells = cells_value
                    .as_array()
                    .ok_or_else(|| err("row cells must be an array"))?;
                children.extend(cells);
            }
        }
    }
    Ok(children)
}

fn real_child_alias_array<'a>(
    node: &'a Value,
    fields: &[(&str, &str)],
    ambiguous_message: &str,
) -> Result<Vec<&'a Value>, AdapterError> {
    let mut found = None;
    for (field, type_message) in fields {
        let Some(value) = node.get(*field) else {
            continue;
        };
        if found.is_some() {
            return Err(err(ambiguous_message));
        }
        found = Some(value.as_array().ok_or_else(|| err(type_message))?);
    }
    Ok(found
        .map(|items| items.iter().collect())
        .unwrap_or_default())
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
        if root.get("tool").is_none()
            && root.get("file name").is_some()
            && root.get("number of pages").is_some()
            && root.get("kids").is_some()
        {
            return parse_real_odl(root);
        }

        let (parser_name, parser_version) = parse_tool(root)?;
        let (pages, page_numbers) = parse_pages(root)?;
        let pages_by_number = pages
            .iter()
            .cloned()
            .map(|page| (page.index, page))
            .collect::<HashMap<_, _>>();
        debug_assert_eq!(pages_by_number.len(), page_numbers.len());
        let elements = parse_elements(root, &pages_by_number)?;
        let (tables_capable, tables) = parse_tables(root, &pages_by_number)?;

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
    const REAL_ODL_SAMPLE: &str = r#"{
      "file name": "lorem.pdf",
      "number of pages": 1,
      "author": "leebd-public",
      "title": null,
      "creation date": "D:20251010112501+09'00'",
      "modification date": "D:20251010112501+09'00'",
      "kids": [
        {
          "type": "heading",
          "pdfua_tag": "H1",
          "id": 1,
          "level": "Doctitle",
          "page number": 1,
          "bounding box": [200.891, 706.938, 394.152, 745.132],
          "heading level": 1,
          "font": "Pretendard-Regular",
          "font size": 32.005,
          "text color": "[0.0]",
          "content": "Lorem Ipsum"
        },
        {
          "type": "paragraph",
          "pdfua_tag": "P",
          "id": 2,
          "page number": 1,
          "bounding box": [85.034, 567.936, 502.306, 659.761],
          "font": "Pretendard-Regular",
          "font size": 9.949,
          "text color": "[0.0]",
          "content": "Lorem ipsum dolor sit amet."
        }
      ]
    }"#;

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
    fn maps_real_opendataloader_json_shape() {
        let src = OdlJsonSource::from_json_str(REAL_ODL_SAMPLE).unwrap();
        let id = src.parser();
        assert_eq!(id.name, "opendataloader-pdf");
        assert_eq!(id.version, "unknown");
        assert_eq!(id.adapter.as_deref(), Some("opendataloader-json"));

        let pages = src.pages();
        assert_eq!(pages.len(), 1);
        assert_eq!(pages[0].id, "page-1");
        assert_eq!(pages[0].width, 50231);
        assert_eq!(pages[0].height, 74513);

        let els = src.elements();
        assert_eq!(els.len(), 2);
        assert_eq!(els[0].id, "odl-1");
        assert_eq!(els[0].kind, "heading");
        assert_eq!(els[0].text.as_deref(), Some("Lorem Ipsum"));
        assert_eq!(els[0].bbox, [20089, 70694, 39415, 74513]);
        assert_eq!(els[1].id, "odl-2");
        assert_eq!(els[1].kind, "paragraph");
        assert_eq!(els[1].text.as_deref(), Some("Lorem ipsum dolor sit amet."));

        let caps = src.capabilities();
        assert!(!caps.tables);
        assert!(!caps.spans && !caps.fingerprint && !caps.crop_support);
        assert_eq!(caps.coordinate_origin, CoordinateOrigin::Unknown);
    }

    #[test]
    fn maps_real_nested_child_structures_in_preorder() {
        let src = OdlJsonSource::from_json_str(
            r#"{
              "file name": "nested.pdf",
              "number of pages": 2,
              "kids": [
                {
                  "type": "section",
                  "id": 10,
                  "page number": 1,
                  "bounding box": [10, 10, 200, 100],
                  "content": "Section",
                  "kids": [
                    {
                      "type": "paragraph",
                      "id": 11,
                      "page number": 1,
                      "bounding box": [20, 30, 180, 60],
                      "content": "Nested child"
                    }
                  ]
                },
                {
                  "type": "list",
                  "page number": 1,
                  "bounding box": [10, 120, 200, 200],
                  "list items": [
                    {
                      "type": "list_item",
                      "page number": 1,
                      "bounding box": [20, 130, 180, 150],
                      "content": "First item"
                    },
                    {
                      "type": "list_item",
                      "id": 12,
                      "page number": 1,
                      "bounding box": [20, 155, 180, 175],
                      "content": "Second item"
                    }
                  ]
                },
                {
                  "type": "table",
                  "id": 13,
                  "page number": 2,
                  "bounding box": [15, 20, 250, 120],
                  "rows": [
                    {
                      "cells": [
                        {
                          "type": "table_cell",
                          "page number": 2,
                          "bounding box": [20, 30, 120, 60],
                          "content": "Cell A"
                        },
                        {
                          "type": "table_cell",
                          "page number": 2,
                          "bounding box": [130, 30, 240, 60],
                          "content": "Cell B"
                        }
                      ]
                    }
                  ]
                }
              ]
            }"#,
        )
        .unwrap();

        let elements = src.elements();
        let ids = elements
            .iter()
            .map(|element| element.id.as_str())
            .collect::<Vec<_>>();
        assert_eq!(
            ids,
            vec![
                "odl-10", "odl-11", "odl-el-1", "odl-el-2", "odl-12", "odl-13", "odl-el-3",
                "odl-el-4",
            ]
        );
        assert_eq!(elements[0].text.as_deref(), Some("Section\nNested child"));
        assert_eq!(elements[2].text.as_deref(), Some("First item\nSecond item"));
        assert_eq!(elements[6].kind, "table_cell");
        assert_eq!(elements[6].page, "page-2");
        assert_eq!(elements[6].text.as_deref(), Some("Cell A"));

        let pages = src.pages();
        assert_eq!(pages[0].width, 20000);
        assert_eq!(pages[0].height, 20000);
        assert_eq!(pages[1].width, 25000);
        assert_eq!(pages[1].height, 12000);
        assert!(src.capabilities().tables);

        let tables = src.tables();
        assert_eq!(tables.len(), 1);
        assert_eq!(tables[0].id, "odl-13");
        assert_eq!(tables[0].page, "page-2");
        assert_eq!(tables[0].bbox, [1500, 2000, 25000, 12000]);
        assert_eq!(tables[0].cells.len(), 2);
        assert_eq!(tables[0].cells[0].row, 1);
        assert_eq!(tables[0].cells[0].col, 1);
        assert_eq!(tables[0].cells[0].text, "Cell A");
        assert_eq!(tables[0].cells[0].bbox, [2000, 3000, 12000, 6000]);
        assert_eq!(tables[0].cells[1].row, 1);
        assert_eq!(tables[0].cells[1].col, 2);
        assert_eq!(tables[0].cells[1].text, "Cell B");
    }

    #[test]
    fn maps_deep_real_nested_subtree_text_without_revisiting_descendants() {
        let mut node = serde_json::json!({
            "type": "paragraph",
            "id": "node-8",
            "page number": 1,
            "bounding box": [80, 80, 90, 90],
            "content": "Node 8"
        });
        for level in (1..8).rev() {
            node = serde_json::json!({
                "type": "section",
                "id": format!("node-{level}"),
                "page number": 1,
                "bounding box": [level * 10, level * 10, 200, 200],
                "content": format!("Node {level}"),
                "children": [node]
            });
        }
        let root = serde_json::json!({
            "file name": "deep.pdf",
            "number of pages": 1,
            "kids": [node]
        });
        let src = OdlJsonSource::from_value(&root).unwrap();

        let elements = src.elements();
        assert_eq!(elements.len(), 8);
        let ids = elements
            .iter()
            .map(|element| element.id.as_str())
            .collect::<Vec<_>>();
        assert_eq!(
            ids,
            vec![
                "odl-node-1",
                "odl-node-2",
                "odl-node-3",
                "odl-node-4",
                "odl-node-5",
                "odl-node-6",
                "odl-node-7",
                "odl-node-8",
            ]
        );
        assert_eq!(
            elements[0].text.as_deref(),
            Some("Node 1\nNode 2\nNode 3\nNode 4\nNode 5\nNode 6\nNode 7\nNode 8")
        );
        assert_eq!(
            elements[3].text.as_deref(),
            Some("Node 4\nNode 5\nNode 6\nNode 7\nNode 8")
        );
        assert_eq!(elements[7].text.as_deref(), Some("Node 8"));
    }

    #[test]
    fn maps_real_text_and_child_aliases_in_preorder() {
        let src = OdlJsonSource::from_json_str(
            r#"{
              "file name": "aliases.pdf",
              "number of pages": 1,
              "kids": [
                {
                  "type": "section",
                  "id": "section-a",
                  "page number": 1,
                  "bounding box": [10, 10, 220, 90],
                  "text": "Alias section",
                  "children": [
                    {
                      "type": "paragraph",
                      "id": "child-a",
                      "page number": 1,
                      "bounding box": [20, 30, 210, 55],
                      "text": "Child text"
                    }
                  ]
                },
                {
                  "type": "list",
                  "id": "list-a",
                  "page number": 1,
                  "bounding box": [10, 100, 220, 160],
                  "list_items": [
                    {
                      "type": "list_item",
                      "id": "item-a",
                      "page number": 1,
                      "bounding box": [20, 115, 210, 140],
                      "text": "Alias item"
                    }
                  ]
                },
                {
                  "type": "table",
                  "id": "table-a",
                  "page number": 1,
                  "bounding box": [10, 170, 220, 230],
                  "rows": [
                    {
                      "cells": [
                        {
                          "type": "table_cell",
                          "page number": 1,
                          "bounding box": [20, 185, 210, 215],
                          "text": "Alias cell"
                        }
                      ]
                    }
                  ]
                }
              ]
            }"#,
        )
        .unwrap();

        let elements = src.elements();
        let ids = elements
            .iter()
            .map(|element| element.id.as_str())
            .collect::<Vec<_>>();
        assert_eq!(
            ids,
            vec![
                "odl-section-a",
                "odl-child-a",
                "odl-list-a",
                "odl-item-a",
                "odl-table-a",
                "odl-el-1",
            ]
        );
        assert_eq!(
            elements[0].text.as_deref(),
            Some("Alias section\nChild text")
        );
        assert_eq!(elements[1].text.as_deref(), Some("Child text"));
        assert_eq!(elements[2].text.as_deref(), Some("Alias item"));
        assert_eq!(elements[3].text.as_deref(), Some("Alias item"));
        assert_eq!(elements[5].text.as_deref(), Some("Alias cell"));

        let tables = src.tables();
        assert_eq!(tables.len(), 1);
        assert_eq!(tables[0].id, "odl-table-a");
        assert_eq!(tables[0].cells.len(), 1);
        assert_eq!(tables[0].cells[0].text, "Alias cell");
        assert_eq!(tables[0].cells[0].bbox, [2000, 18500, 21000, 21500]);
    }

    #[test]
    fn maps_real_structural_containers_without_table_capability() {
        let src = OdlJsonSource::from_json_str(
            r#"{
              "file name": "structural.pdf",
              "number of pages": 1,
              "kids": [
                {
                  "kids": [
                    {
                      "id": "intro",
                      "page number": 1,
                      "bounding box": [10, 10, 40, 20],
                      "content": "Intro without type"
                    }
                  ]
                },
                {
                  "list items": [
                    {
                      "type": "list_item",
                      "id": "item-a",
                      "page number": 1,
                      "bounding box": [10, 30, 50, 40],
                      "content": "Item A"
                    }
                  ]
                },
                {
                  "rows": [
                    {
                      "cells": [
                        {
                          "type": "cell",
                          "id": 13,
                          "page number": 1,
                          "bounding box": [20, 50, 70, 80],
                          "content": "Cell value"
                        }
                      ]
                    }
                  ]
                }
              ]
            }"#,
        )
        .unwrap();

        let elements = src.elements();
        assert_eq!(elements.len(), 3);
        assert_eq!(elements[0].id, "odl-intro");
        assert_eq!(elements[0].kind, "unknown");
        assert_eq!(elements[0].text.as_deref(), Some("Intro without type"));
        assert_eq!(elements[1].id, "odl-item-a");
        assert_eq!(elements[2].id, "odl-13");
        assert_eq!(elements[2].kind, "cell");

        let pages = src.pages();
        assert_eq!(pages[0].width, 7000);
        assert_eq!(pages[0].height, 8000);
        assert!(!src.capabilities().tables);
        assert!(src.tables().is_empty());
    }

    #[test]
    fn rejects_malformed_real_table_cells() {
        assert_error_contains(
            r#"{
              "file name": "table.pdf",
              "number of pages": 1,
              "kids": [
                {
                  "type": "table",
                  "id": 1,
                  "page number": 1,
                  "bounding box": [10, 10, 200, 100],
                  "rows": [
                    {
                      "cells": [
                        {
                          "type": "table_cell",
                          "page number": 2,
                          "bounding box": [20, 20, 100, 40],
                          "content": "Out of range"
                        }
                      ]
                    }
                  ]
                }
              ]
            }"#,
            "cell page number references unknown page",
        );
        assert_error_contains(
            r#"{
              "file name": "table.pdf",
              "number of pages": 1,
              "kids": [
                {
                  "type": "table",
                  "id": 1,
                  "page number": 1,
                  "bounding box": [10, 10, 200, 100],
                  "rows": [
                    {
                      "cells": [
                        {
                          "type": "table_cell",
                          "page number": 1,
                          "bounding box": [20, 20, 100, 40]
                        }
                      ]
                    }
                  ]
                }
              ]
            }"#,
            "missing cell content",
        );
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

    #[test]
    fn rejects_zero_area_bboxes() {
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[{"page":1,"bbox":[1,1,1,2]}]}"#,
            "bbox must have positive area",
        );
        assert_error_contains(
            r#"{"file name":"zero.pdf","number of pages":1,"kids":[{"type":"paragraph","page number":1,"bounding box":[1,1,2,1],"content":"A"}]}"#,
            "bbox must have positive area",
        );
    }

    #[test]
    fn rejects_documented_subset_bboxes_outside_declared_page_bounds() {
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[{"page":1,"bbox":[1,1,613,2]}]}"#,
            "element bbox exceeds page bounds",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[{"page":1,"bbox":[-1,1,2,2]}]}"#,
            "element bbox exceeds page bounds",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[],"tables":[{"id":"t1","page":1,"bbox":[1,1,613,2],"cells":[]}]}"#,
            "table bbox exceeds page bounds",
        );
        assert_error_contains(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[],"tables":[{"id":"t1","page":1,"bbox":[1,1,2,2],"cells":[{"row":1,"col":1,"bbox":[1,1,613,2],"text":"x"}]}]}"#,
            "cell bbox exceeds page bounds",
        );
    }

    #[test]
    fn accepts_documented_subset_bboxes_on_declared_page_bounds() {
        OdlJsonSource::from_json_str(
            r#"{"tool":{"name":"x","version":"1"},"pages":[{"number":1,"width":612,"height":792}],"elements":[{"page":1,"bbox":[0,0,612,792]}],"tables":[{"id":"t1","page":1,"bbox":[0,0,612,792],"cells":[{"row":1,"col":1,"bbox":[0,0,612,792],"text":"x"}]}]}"#,
        )
        .expect("exact page-boundary bboxes are valid");
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
        assert_error_contains(
            r#"{"file name":"huge.pdf","number of pages":4294967295,"kids":[]}"#,
            "number of pages exceeds adapter limit",
        );
        assert_error_contains(
            r#"{"file name":"dup.pdf","number of pages":1,"kids":[{"type":"paragraph","id":1,"page number":1,"bounding box":[1,1,2,2],"content":"A","kids":[{"type":"paragraph","id":1,"page number":1,"bounding box":[2,2,3,3],"content":"B"}]}]}"#,
            "duplicate content id",
        );
        assert_error_contains(
            r#"{"file name":"dup.pdf","number of pages":1,"kids":[{"type":"paragraph","id":"same","page number":1,"bounding box":[1,1,2,2],"content":"A"},{"type":"paragraph","id":"same","page number":1,"bounding box":[2,2,3,3],"content":"B"}]}"#,
            "duplicate content id",
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

    #[test]
    fn rejects_malformed_real_child_containers() {
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"paragraph","page number":1,"bounding box":[1,1,2,2],"kids":{}}]}"#,
            "kids must be an array",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"list","page number":1,"bounding box":[1,1,2,2],"list items":{}}]}"#,
            "list items must be an array",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"table","page number":1,"bounding box":[1,1,2,2],"rows":{}}]}"#,
            "rows must be an array",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"table","page number":1,"bounding box":[1,1,2,2],"rows":[1]}]}"#,
            "row must be an object",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"table","page number":1,"bounding box":[1,1,2,2],"rows":[{"cells":{}}]}]}"#,
            "row cells must be an array",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"paragraph","page number":1,"bounding box":[1,1,2,2],"content":7}]}"#,
            "content must be a string",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"paragraph","page number":1,"bounding box":[1,1,2,2],"text":7}]}"#,
            "text must be a string",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"paragraph","page number":1,"bounding box":[1,1,2,2],"content":"A","text":"B"}]}"#,
            "content and text fields disagree",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"children":{}}]}"#,
            "children must be an array",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"kids":[],"children":[]}]}"#,
            "ambiguous kids/children containers",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{"type":"list","page number":1,"bounding box":[1,1,2,2],"list items":[],"list_items":[]}]}"#,
            "ambiguous list item containers",
        );
        assert_error_contains(
            r#"{"file name":"bad.pdf","number of pages":1,"kids":[{}]}"#,
            "content node has no element fields or child containers",
        );
    }
}
