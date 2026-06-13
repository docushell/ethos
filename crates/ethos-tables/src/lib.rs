//! Deterministic table-candidate extraction over already-quantized Ethos spans.
//!
//! This crate does not perform OCR and does not interpret table semantics. Its first
//! contract is intentionally strict: when a supplied span set forms a regular text grid,
//! it can be represented as a table candidate with cell-level span provenance.

#![forbid(unsafe_code)]
#![warn(missing_docs)]

use ethos_core::error::EthosError;
use ethos_core::geom::QRect;
use ethos_core::ids::table_id;
use ethos_core::model::{Cell, Document, Span, Table};

/// Configuration for regular-grid table candidate detection.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TableCandidateConfig {
    /// Minimum number of detected rows required to emit a candidate.
    pub min_rows: usize,
    /// Minimum number of detected columns required to emit a candidate.
    pub min_cols: usize,
    /// Number of leading rows treated as headers in the emitted table.
    pub header_rows: u32,
    /// Structure confidence assigned to strict regular-grid candidates.
    pub confidence: u16,
}

impl Default for TableCandidateConfig {
    fn default() -> Self {
        Self {
            min_rows: 3,
            min_cols: 2,
            header_rows: 1,
            confidence: 700,
        }
    }
}

/// Detect at most one regular-grid table candidate from a page-local span set.
///
/// This function is deterministic for a fixed `(page_id, spans, first_table_ordinal,
/// config)` tuple. It sorts by quantized geometry and span id, never by caller input
/// order. If the spans do not form a complete regular grid, it returns an empty vector.
pub fn detect_regular_grid_candidates(
    page_id: &str,
    spans: &[Span],
    first_table_ordinal: u32,
    config: &TableCandidateConfig,
) -> Result<Vec<Table>, EthosError> {
    validate_config(config)?;

    let span_refs: Vec<SpanRef<'_>> = spans
        .iter()
        .filter(|span| span.page == page_id && !span.text.is_empty())
        .map(|span| SpanRef {
            span,
            center_x: center_x(span.bbox),
            center_y: center_y(span.bbox),
        })
        .collect();

    if span_refs.len() < config.min_rows.saturating_mul(config.min_cols) {
        return Ok(Vec::new());
    }

    let rows = group_rows(span_refs);
    if rows.len() < config.min_rows {
        return Ok(Vec::new());
    }

    let columns = group_columns(&rows);
    if columns.len() < config.min_cols {
        return Ok(Vec::new());
    }

    let Some(cells) = build_cells(&rows, &columns) else {
        return Ok(Vec::new());
    };

    let Some(bbox) = cells.iter().map(|cell| cell.bbox).reduce(union_rect) else {
        return Ok(Vec::new());
    };

    let table = Table {
        id: table_id(first_table_ordinal)?,
        page_refs: vec![page_id.to_string()],
        bbox,
        n_rows: rows.len() as u32,
        n_cols: columns.len() as u32,
        header_rows: config.header_rows.min(rows.len() as u32),
        header_cols: 0,
        cells,
        confidence: Some(config.confidence),
        warning_refs: Vec::new(),
        exports: None,
    };

    Ok(vec![table])
}

/// Detect regular-grid table candidates across every page in a canonical document.
///
/// Candidate ids are assigned in page order and then candidate order within each page.
/// The current detector emits at most one candidate per page.
pub fn detect_document_regular_grid_candidates(
    doc: &Document,
    config: &TableCandidateConfig,
) -> Result<Vec<Table>, EthosError> {
    let mut tables = Vec::new();
    let mut next_table_ordinal = 1u32;

    for page in &doc.payload.pages {
        let page_tables = detect_regular_grid_candidates(
            &page.id,
            &doc.payload.spans,
            next_table_ordinal,
            config,
        )?;
        next_table_ordinal += page_tables.len() as u32;
        tables.extend(page_tables);
    }

    Ok(tables)
}

/// Render a table candidate as deterministic GitHub-flavored Markdown.
///
/// The first header row is used when `table.header_rows > 0`; otherwise every row is
/// rendered as body content and no separator row is inserted.
pub fn render_markdown(table: &Table) -> String {
    let matrix = table_matrix(table);
    if matrix.is_empty() {
        return String::new();
    }

    let mut out = String::new();
    let has_header = table.header_rows > 0;

    for (row_index, row) in matrix.iter().enumerate() {
        out.push('|');
        for cell in row {
            out.push(' ');
            out.push_str(&escape_markdown_cell(cell));
            out.push(' ');
            out.push('|');
        }
        out.push('\n');

        if has_header && row_index == 0 {
            out.push('|');
            for _ in row {
                out.push_str(" --- |");
            }
            out.push('\n');
        }
    }

    out
}

#[derive(Clone, Copy)]
struct SpanRef<'a> {
    span: &'a Span,
    center_x: i64,
    center_y: i64,
}

struct Row<'a> {
    spans: Vec<SpanRef<'a>>,
    bbox: QRect,
    center_y: i64,
}

struct Column {
    bbox: QRect,
    center_x: i64,
}

fn validate_config(config: &TableCandidateConfig) -> Result<(), EthosError> {
    if config.min_rows == 0 || config.min_cols == 0 || config.confidence > 1000 {
        return Err(EthosError::internal("invalid table candidate config"));
    }
    Ok(())
}

fn group_rows(mut spans: Vec<SpanRef<'_>>) -> Vec<Row<'_>> {
    spans.sort_by(span_row_order);
    let tolerance = row_tolerance(&spans);
    let mut rows: Vec<Row<'_>> = Vec::new();

    for span_ref in spans {
        if let Some(row) = rows
            .iter_mut()
            .find(|row| same_row(row, span_ref, tolerance))
        {
            row.bbox = union_rect(row.bbox, span_ref.span.bbox);
            row.center_y = center_y(row.bbox);
            row.spans.push(span_ref);
        } else {
            rows.push(Row {
                spans: vec![span_ref],
                bbox: span_ref.span.bbox,
                center_y: span_ref.center_y,
            });
        }
    }

    for row in &mut rows {
        row.spans.sort_by(span_column_order);
    }
    rows.sort_by(row_order);
    rows
}

fn group_columns(rows: &[Row<'_>]) -> Vec<Column> {
    let mut spans: Vec<SpanRef<'_>> = rows
        .iter()
        .flat_map(|row| row.spans.iter().copied())
        .collect();
    spans.sort_by(span_column_order);
    let tolerance = column_tolerance(&spans);
    let mut columns: Vec<Column> = Vec::new();

    for span_ref in spans {
        if let Some(column) = columns
            .iter_mut()
            .find(|column| same_column(column, span_ref, tolerance))
        {
            column.bbox = union_rect(column.bbox, span_ref.span.bbox);
            column.center_x = center_x(column.bbox);
        } else {
            columns.push(Column {
                bbox: span_ref.span.bbox,
                center_x: span_ref.center_x,
            });
        }
    }

    columns.sort_by(column_order);
    columns
}

fn build_cells(rows: &[Row<'_>], columns: &[Column]) -> Option<Vec<Cell>> {
    let mut cells = Vec::with_capacity(rows.len() * columns.len());

    for (row_index, row) in rows.iter().enumerate() {
        let mut buckets: Vec<Vec<SpanRef<'_>>> = vec![Vec::new(); columns.len()];

        for span_ref in &row.spans {
            let col_index = nearest_column(*span_ref, columns)?;
            buckets[col_index].push(*span_ref);
        }

        if buckets.iter().any(Vec::is_empty) {
            return None;
        }

        for (col_index, mut bucket) in buckets.into_iter().enumerate() {
            bucket.sort_by(span_column_order);
            let bbox = bucket
                .iter()
                .map(|span_ref| span_ref.span.bbox)
                .reduce(union_rect)?;
            let text = bucket
                .iter()
                .map(|span_ref| span_ref.span.text.as_str())
                .collect::<Vec<_>>()
                .join(" ");
            let span_refs = bucket
                .iter()
                .map(|span_ref| span_ref.span.id.clone())
                .collect();

            cells.push(Cell {
                row: row_index as u32,
                col: col_index as u32,
                row_span: 1,
                col_span: 1,
                bbox,
                text,
                span_refs,
                element_refs: Vec::new(),
            });
        }
    }

    Some(cells)
}

fn nearest_column(span_ref: SpanRef<'_>, columns: &[Column]) -> Option<usize> {
    columns
        .iter()
        .enumerate()
        .min_by_key(|(_, column)| {
            (span_ref.span.bbox.x0 - column.bbox.x0).abs()
                + (span_ref.center_x - column.center_x).abs()
        })
        .map(|(index, _)| index)
}

fn table_matrix(table: &Table) -> Vec<Vec<String>> {
    let mut matrix = vec![vec![String::new(); table.n_cols as usize]; table.n_rows as usize];

    for cell in &table.cells {
        if let Some(row) = matrix.get_mut(cell.row as usize) {
            if let Some(slot) = row.get_mut(cell.col as usize) {
                *slot = cell.text.clone();
            }
        }
    }

    matrix
}

fn escape_markdown_cell(cell: &str) -> String {
    cell.replace('|', "\\|").replace('\n', "<br>")
}

fn row_tolerance(spans: &[SpanRef<'_>]) -> i64 {
    let mut heights: Vec<i64> = spans
        .iter()
        .map(|span| height(span.span.bbox).max(1))
        .collect();
    heights.sort_unstable();
    let median = heights.get(heights.len() / 2).copied().unwrap_or(1);
    (median / 2).max(50)
}

fn column_tolerance(spans: &[SpanRef<'_>]) -> i64 {
    let mut widths: Vec<i64> = spans
        .iter()
        .map(|span| width(span.span.bbox).max(1))
        .collect();
    widths.sort_unstable();
    let median = widths.get(widths.len() / 2).copied().unwrap_or(1);
    (median / 2).max(250)
}

fn same_row(row: &Row<'_>, span_ref: SpanRef<'_>, tolerance: i64) -> bool {
    (span_ref.center_y - row.center_y).abs() <= tolerance
        || vertical_overlap(row.bbox, span_ref.span.bbox) > 0
}

fn same_column(column: &Column, span_ref: SpanRef<'_>, tolerance: i64) -> bool {
    (span_ref.span.bbox.x0 - column.bbox.x0).abs() <= tolerance
        || (span_ref.center_x - column.center_x).abs() <= tolerance
}

fn vertical_overlap(a: QRect, b: QRect) -> i64 {
    a.y1.min(b.y1) - a.y0.max(b.y0)
}

fn union_rect(a: QRect, b: QRect) -> QRect {
    QRect {
        x0: a.x0.min(b.x0),
        y0: a.y0.min(b.y0),
        x1: a.x1.max(b.x1),
        y1: a.y1.max(b.y1),
    }
}

fn center_x(bbox: QRect) -> i64 {
    bbox.x0 + ((bbox.x1 - bbox.x0) / 2)
}

fn center_y(bbox: QRect) -> i64 {
    bbox.y0 + ((bbox.y1 - bbox.y0) / 2)
}

fn width(bbox: QRect) -> i64 {
    bbox.x1 - bbox.x0
}

fn height(bbox: QRect) -> i64 {
    bbox.y1 - bbox.y0
}

fn span_row_order(a: &SpanRef<'_>, b: &SpanRef<'_>) -> std::cmp::Ordering {
    a.span
        .bbox
        .y0
        .cmp(&b.span.bbox.y0)
        .then_with(|| a.center_y.cmp(&b.center_y))
        .then_with(|| a.span.bbox.x0.cmp(&b.span.bbox.x0))
        .then_with(|| a.span.id.cmp(&b.span.id))
}

fn span_column_order(a: &SpanRef<'_>, b: &SpanRef<'_>) -> std::cmp::Ordering {
    a.span
        .bbox
        .x0
        .cmp(&b.span.bbox.x0)
        .then_with(|| a.center_x.cmp(&b.center_x))
        .then_with(|| a.span.bbox.y0.cmp(&b.span.bbox.y0))
        .then_with(|| a.span.id.cmp(&b.span.id))
}

fn row_order(a: &Row<'_>, b: &Row<'_>) -> std::cmp::Ordering {
    a.bbox
        .y0
        .cmp(&b.bbox.y0)
        .then_with(|| a.center_y.cmp(&b.center_y))
        .then_with(|| a.bbox.x0.cmp(&b.bbox.x0))
}

fn column_order(a: &Column, b: &Column) -> std::cmp::Ordering {
    a.bbox
        .x0
        .cmp(&b.bbox.x0)
        .then_with(|| a.center_x.cmp(&b.center_x))
        .then_with(|| a.bbox.y0.cmp(&b.bbox.y0))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn span(id: &str, x0: i64, y0: i64, x1: i64, y1: i64, text: &str) -> Span {
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
            warning_refs: Vec::new(),
        }
    }

    fn grid_spans() -> Vec<Span> {
        vec![
            span("s000008", 2_000, 2_000, 2_600, 2_400, "2025"),
            span("s000001", 0, 0, 600, 400, "Name"),
            span("s000005", 1_000, 1_000, 1_600, 1_400, "10"),
            span("s000003", 2_000, 0, 2_600, 400, "Year"),
            span("s000007", 1_000, 2_000, 1_600, 2_400, "12"),
            span("s000002", 1_000, 0, 1_600, 400, "Score"),
            span("s000009", 0, 2_000, 600, 2_400, "Beta"),
            span("s000004", 0, 1_000, 600, 1_400, "Alpha"),
            span("s000006", 2_000, 1_000, 2_600, 1_400, "2024"),
        ]
    }

    #[test]
    fn detects_regular_grid_with_cell_span_refs() {
        let tables = detect_regular_grid_candidates(
            "p0001",
            &grid_spans(),
            1,
            &TableCandidateConfig::default(),
        )
        .unwrap();

        assert_eq!(tables.len(), 1);
        let table = &tables[0];
        assert_eq!(table.id, "t0001");
        assert_eq!(table.n_rows, 3);
        assert_eq!(table.n_cols, 3);
        assert_eq!(table.header_rows, 1);
        assert_eq!(table.bbox, QRect::new(0, 0, 2_600, 2_400).unwrap());
        assert_eq!(table.cells.len(), 9);
        assert_eq!(table.cells[0].text, "Name");
        assert_eq!(table.cells[0].span_refs, vec!["s000001"]);
        assert_eq!(table.cells[4].text, "10");
        assert_eq!(table.cells[4].span_refs, vec!["s000005"]);
        assert_eq!(table.cells[8].text, "2025");
        assert_eq!(table.cells[8].span_refs, vec!["s000008"]);
    }

    #[test]
    fn detection_is_independent_of_input_order() {
        let forward = grid_spans();
        let mut reversed = forward.clone();
        reversed.reverse();

        let a =
            detect_regular_grid_candidates("p0001", &forward, 7, &TableCandidateConfig::default())
                .unwrap();
        let b =
            detect_regular_grid_candidates("p0001", &reversed, 7, &TableCandidateConfig::default())
                .unwrap();

        assert_eq!(a, b);
    }

    #[test]
    fn rejects_incomplete_grid() {
        let spans = vec![
            span("s000001", 0, 0, 600, 400, "Name"),
            span("s000002", 1_000, 0, 1_600, 400, "Score"),
            span("s000003", 0, 1_000, 600, 1_400, "Alpha"),
        ];

        let tables =
            detect_regular_grid_candidates("p0001", &spans, 1, &TableCandidateConfig::default())
                .unwrap();

        assert!(tables.is_empty());
    }

    #[test]
    fn render_markdown_is_deterministic_and_escapes_cells() {
        let mut table = detect_regular_grid_candidates(
            "p0001",
            &grid_spans(),
            1,
            &TableCandidateConfig::default(),
        )
        .unwrap()
        .remove(0);
        table.cells[4].text = "10|11".to_string();

        assert_eq!(
            render_markdown(&table),
            "| Name | Score | Year |\n| --- | --- | --- |\n| Alpha | 10\\|11 | 2024 |\n| Beta | 12 | 2025 |\n"
        );
    }

    #[test]
    fn invalid_config_is_rejected() {
        let config = TableCandidateConfig {
            min_rows: 0,
            ..TableCandidateConfig::default()
        };

        let err = detect_regular_grid_candidates("p0001", &grid_spans(), 1, &config).unwrap_err();
        assert_eq!(err.message, "invalid table candidate config");
    }
}
