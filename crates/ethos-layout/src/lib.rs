//! Basic deterministic layout over quantized extraction spans.
//!
//! This WS-LAYOUT slice intentionally makes only two claims:
//! nearby lines in the same detected column become one `text_block` paragraph, and
//! multi-column text is ordered by column before vertical position. Higher-level heading,
//! list, and table semantics belong to later layout lanes.

use ethos_core::error::EthosError;
use ethos_core::geom::QRect;
use ethos_core::ids::element_id;
use ethos_core::model::{Element, ElementType, Span};
use ethos_core::traits::{Extraction, LayoutEngine, LayoutOutput};

/// Deterministic paragraph-level layout engine.
#[derive(Debug, Clone, Copy, Default)]
pub struct BasicLayoutEngine;

impl LayoutEngine for BasicLayoutEngine {
    fn layout(&self, extraction: &Extraction) -> Result<LayoutOutput, EthosError> {
        let mut elements = Vec::new();
        let mut next_element = 1u32;

        for page in &extraction.pages {
            let page_spans: Vec<SpanRef<'_>> = extraction
                .spans
                .iter()
                .enumerate()
                .filter_map(|(index, span)| {
                    (span.page == page.id).then_some(SpanRef {
                        index,
                        span,
                        center_y: center_y(span.bbox),
                    })
                })
                .collect();

            let mut columns = group_columns(group_lines(page_spans));
            columns.sort_by(column_order);

            for column in columns {
                for paragraph in group_paragraphs(column.lines) {
                    let paragraph_spans = paragraph_spans(&paragraph);
                    let element = build_text_block(next_element, &page.id, &paragraph_spans)?;
                    elements.push(element);
                    next_element += 1;
                }
            }
        }

        Ok(LayoutOutput {
            elements,
            warnings: Vec::new(),
        })
    }
}

#[derive(Clone, Copy)]
struct SpanRef<'a> {
    index: usize,
    span: &'a Span,
    center_y: i64,
}

struct Line<'a> {
    spans: Vec<SpanRef<'a>>,
    bbox: QRect,
    center_y: i64,
}

struct Column<'a> {
    lines: Vec<Line<'a>>,
    bbox: QRect,
    center_x: i64,
}

struct Paragraph<'a> {
    lines: Vec<Line<'a>>,
    bbox: QRect,
}

fn group_lines(mut spans: Vec<SpanRef<'_>>) -> Vec<Line<'_>> {
    spans.sort_by(span_line_order);
    let vertical_tolerance = line_tolerance(&spans);
    let horizontal_tolerance = line_gap_tolerance(&spans);
    let mut lines: Vec<Line<'_>> = Vec::new();

    for span_ref in spans {
        if let Some(line) = lines
            .iter_mut()
            .find(|line| same_line(line, span_ref, vertical_tolerance, horizontal_tolerance))
        {
            line.bbox = union_rect(line.bbox, span_ref.span.bbox);
            line.center_y = center_y(line.bbox);
            line.spans.push(span_ref);
        } else {
            lines.push(Line {
                spans: vec![span_ref],
                bbox: span_ref.span.bbox,
                center_y: span_ref.center_y,
            });
        }
    }

    lines
}

fn group_columns(mut lines: Vec<Line<'_>>) -> Vec<Column<'_>> {
    lines.sort_by(column_seed_order);
    let tolerance = column_tolerance(&lines);
    let mut columns: Vec<Column<'_>> = Vec::new();

    for line in lines {
        let target = columns
            .iter()
            .enumerate()
            .filter(|(_, column)| same_column(column, &line, tolerance))
            .min_by(|(_, a), (_, b)| column_distance(a, &line).cmp(&column_distance(b, &line)))
            .map(|(idx, _)| idx);

        if let Some(idx) = target {
            let column = &mut columns[idx];
            column.bbox = union_rect(column.bbox, line.bbox);
            column.center_x = center_x(column.bbox);
            column.lines.push(line);
        } else {
            columns.push(Column {
                bbox: line.bbox,
                center_x: center_x(line.bbox),
                lines: vec![line],
            });
        }
    }

    columns
}

fn group_paragraphs(mut lines: Vec<Line<'_>>) -> Vec<Paragraph<'_>> {
    lines.sort_by(line_order);
    let threshold = paragraph_gap_threshold(&lines);
    let mut paragraphs: Vec<Paragraph<'_>> = Vec::new();

    for line in lines {
        if let Some(paragraph) = paragraphs.last_mut() {
            if same_paragraph(
                paragraph
                    .lines
                    .last()
                    .expect("paragraphs are created with one line"),
                &line,
                threshold,
            ) {
                paragraph.bbox = union_rect(paragraph.bbox, line.bbox);
                paragraph.lines.push(line);
                continue;
            }
        }

        paragraphs.push(Paragraph {
            bbox: line.bbox,
            lines: vec![line],
        });
    }

    paragraphs
}

fn line_tolerance(spans: &[SpanRef<'_>]) -> i64 {
    let mut heights: Vec<i64> = spans
        .iter()
        .map(|span| (span.span.bbox.y1 - span.span.bbox.y0).max(1))
        .collect();
    heights.sort_unstable();
    let median = heights.get(heights.len() / 2).copied().unwrap_or(1);
    (median / 2).max(50)
}

fn line_gap_tolerance(spans: &[SpanRef<'_>]) -> i64 {
    let mut heights: Vec<i64> = spans
        .iter()
        .map(|span| line_height(span.span.bbox).max(1))
        .collect();
    heights.sort_unstable();
    let median = heights.get(heights.len() / 2).copied().unwrap_or(1);
    (median * 2).max(500)
}

fn column_tolerance(lines: &[Line<'_>]) -> i64 {
    let mut widths: Vec<i64> = lines
        .iter()
        .map(|line| line_width(line.bbox).max(1))
        .collect();
    widths.sort_unstable();
    let median = widths.get(widths.len() / 2).copied().unwrap_or(1);
    (median / 4).max(500)
}

fn paragraph_gap_threshold(lines: &[Line<'_>]) -> i64 {
    let mut heights: Vec<i64> = lines
        .iter()
        .map(|line| line_height(line.bbox).max(1))
        .collect();
    heights.sort_unstable();
    let median = heights.get(heights.len() / 2).copied().unwrap_or(1);
    ((median * 5) / 4).max(250)
}

fn same_line(
    line: &Line<'_>,
    span_ref: SpanRef<'_>,
    vertical_tolerance: i64,
    horizontal_tolerance: i64,
) -> bool {
    let vertically_aligned = (span_ref.center_y - line.center_y).abs() <= vertical_tolerance
        || vertical_overlap(line.bbox, span_ref.span.bbox) > 0;
    vertically_aligned && horizontal_gap(line.bbox, span_ref.span.bbox) <= horizontal_tolerance
}

fn same_column(column: &Column<'_>, line: &Line<'_>, tolerance: i64) -> bool {
    horizontal_overlap(column.bbox, line.bbox) > 0
        || (line.bbox.x0 - column.bbox.x0).abs() <= tolerance
        || (center_x(line.bbox) - column.center_x).abs() <= tolerance
}

fn same_paragraph(previous: &Line<'_>, current: &Line<'_>, threshold: i64) -> bool {
    let gap = current.bbox.y0 - previous.bbox.y1;
    gap >= -threshold && gap <= threshold
}

fn vertical_overlap(a: QRect, b: QRect) -> i64 {
    a.y1.min(b.y1) - a.y0.max(b.y0)
}

fn horizontal_overlap(a: QRect, b: QRect) -> i64 {
    a.x1.min(b.x1) - a.x0.max(b.x0)
}

fn horizontal_gap(a: QRect, b: QRect) -> i64 {
    if a.x1 < b.x0 {
        b.x0 - a.x1
    } else if b.x1 < a.x0 {
        a.x0 - b.x1
    } else {
        0
    }
}

fn column_distance(column: &Column<'_>, line: &Line<'_>) -> i64 {
    (line.bbox.x0 - column.bbox.x0).abs() + (center_x(line.bbox) - column.center_x).abs()
}

fn paragraph_spans<'a>(paragraph: &Paragraph<'a>) -> Vec<SpanRef<'a>> {
    let mut spans = Vec::new();
    for line in &paragraph.lines {
        let mut line_spans = line.spans.clone();
        line_spans.sort_by(span_reading_order);
        spans.extend(line_spans);
    }
    spans
}

fn build_text_block(
    ordinal: u32,
    page_id: &str,
    spans: &[SpanRef<'_>],
) -> Result<Element, EthosError> {
    let mut text = String::new();
    let mut bbox: Option<QRect> = None;
    let mut span_refs = Vec::with_capacity(spans.len());

    for span_ref in spans {
        if !text.is_empty() {
            text.push(' ');
        }
        text.push_str(&span_ref.span.text);
        bbox = Some(match bbox {
            Some(existing) => union_rect(existing, span_ref.span.bbox),
            None => span_ref.span.bbox,
        });
        span_refs.push(span_ref.span.id.clone());
    }

    Ok(Element {
        id: element_id(ordinal)?,
        element_type: ElementType::TextBlock,
        page: page_id.to_string(),
        bbox: bbox.ok_or_else(|| EthosError::internal("text block has no bbox"))?,
        text: Some(text),
        heading_level: None,
        table_ref: None,
        region_ref: None,
        confidence: None,
        span_refs,
        warning_refs: Vec::new(),
    })
}

fn span_line_order(a: &SpanRef<'_>, b: &SpanRef<'_>) -> std::cmp::Ordering {
    a.center_y
        .cmp(&b.center_y)
        .then_with(|| a.span.bbox.y0.cmp(&b.span.bbox.y0))
        .then_with(|| a.span.bbox.x0.cmp(&b.span.bbox.x0))
        .then_with(|| a.index.cmp(&b.index))
}

fn column_seed_order(a: &Line<'_>, b: &Line<'_>) -> std::cmp::Ordering {
    a.bbox
        .x0
        .cmp(&b.bbox.x0)
        .then_with(|| a.bbox.y0.cmp(&b.bbox.y0))
        .then_with(|| a.center_y.cmp(&b.center_y))
}

fn column_order(a: &Column<'_>, b: &Column<'_>) -> std::cmp::Ordering {
    a.bbox
        .x0
        .cmp(&b.bbox.x0)
        .then_with(|| a.bbox.y0.cmp(&b.bbox.y0))
        .then_with(|| a.center_x.cmp(&b.center_x))
}

fn span_reading_order(a: &SpanRef<'_>, b: &SpanRef<'_>) -> std::cmp::Ordering {
    a.span
        .bbox
        .x0
        .cmp(&b.span.bbox.x0)
        .then_with(|| a.span.bbox.y0.cmp(&b.span.bbox.y0))
        .then_with(|| a.index.cmp(&b.index))
}

fn line_order(a: &Line<'_>, b: &Line<'_>) -> std::cmp::Ordering {
    a.bbox
        .y0
        .cmp(&b.bbox.y0)
        .then_with(|| a.bbox.x0.cmp(&b.bbox.x0))
        .then_with(|| a.center_y.cmp(&b.center_y))
}

fn center_y(bbox: QRect) -> i64 {
    bbox.y0 + ((bbox.y1 - bbox.y0) / 2)
}

fn center_x(bbox: QRect) -> i64 {
    bbox.x0 + ((bbox.x1 - bbox.x0) / 2)
}

fn line_width(bbox: QRect) -> i64 {
    bbox.x1 - bbox.x0
}

fn line_height(bbox: QRect) -> i64 {
    bbox.y1 - bbox.y0
}

fn union_rect(a: QRect, b: QRect) -> QRect {
    QRect {
        x0: a.x0.min(b.x0),
        y0: a.y0.min(b.y0),
        x1: a.x1.max(b.x1),
        y1: a.y1.max(b.y1),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ethos_core::model::{Page, Region, Warning};

    fn span(id: &str, page: &str, bbox: QRect, text: &str) -> Span {
        Span {
            id: id.to_string(),
            page: page.to_string(),
            bbox,
            text: text.to_string(),
            font_id: None,
            font_size_q: Some(1200),
            char_start: None,
            char_end: None,
            warning_refs: vec![],
        }
    }

    fn extraction(spans: Vec<Span>) -> Extraction {
        Extraction {
            pages: vec![Page {
                id: "p0001".to_string(),
                index: 1,
                width: 20_000,
                height: 20_000,
                rotation: 0,
            }],
            spans,
            regions: Vec::<Region>::new(),
            warnings: Vec::<Warning>::new(),
        }
    }

    #[test]
    fn groups_nearby_lines_into_paragraphs() {
        let extraction = extraction(vec![
            span(
                "s000002",
                "p0001",
                QRect::new(1_200, 0, 2_000, 500).unwrap(),
                "world",
            ),
            span(
                "s000003",
                "p0001",
                QRect::new(0, 900, 700, 1_400).unwrap(),
                "Second",
            ),
            span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 1_000, 500).unwrap(),
                "Hello",
            ),
            span(
                "s000004",
                "p0001",
                QRect::new(900, 900, 1_500, 1_400).unwrap(),
                "line",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert_eq!(output.elements.len(), 1);
        assert_eq!(output.elements[0].id, "e000001");
        assert_eq!(
            output.elements[0].text.as_deref(),
            Some("Hello world Second line")
        );
        assert_eq!(
            output.elements[0].span_refs,
            vec![
                "s000001".to_string(),
                "s000002".to_string(),
                "s000003".to_string(),
                "s000004".to_string(),
            ]
        );
    }

    #[test]
    fn separates_paragraphs_across_large_vertical_gaps() {
        let extraction = extraction(vec![
            span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 700, 500).unwrap(),
                "First",
            ),
            span(
                "s000002",
                "p0001",
                QRect::new(900, 0, 1_400, 500).unwrap(),
                "block",
            ),
            span(
                "s000003",
                "p0001",
                QRect::new(0, 2_200, 800, 2_700).unwrap(),
                "Second",
            ),
            span(
                "s000004",
                "p0001",
                QRect::new(1_000, 2_200, 1_500, 2_700).unwrap(),
                "block",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert_eq!(output.elements.len(), 2);
        assert_eq!(output.elements[0].text.as_deref(), Some("First block"));
        assert_eq!(output.elements[1].text.as_deref(), Some("Second block"));
    }

    #[test]
    fn orders_column_paragraphs_left_to_right_before_top_to_bottom() {
        let extraction = extraction(vec![
            span(
                "s000003",
                "p0001",
                QRect::new(6_000, 0, 6_700, 500).unwrap(),
                "Right",
            ),
            span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 600, 500).unwrap(),
                "Left",
            ),
            span(
                "s000004",
                "p0001",
                QRect::new(6_900, 0, 7_300, 500).unwrap(),
                "top",
            ),
            span(
                "s000002",
                "p0001",
                QRect::new(800, 0, 1_200, 500).unwrap(),
                "top",
            ),
            span(
                "s000007",
                "p0001",
                QRect::new(6_000, 900, 6_700, 1_400).unwrap(),
                "Right",
            ),
            span(
                "s000005",
                "p0001",
                QRect::new(0, 900, 600, 1_400).unwrap(),
                "Left",
            ),
            span(
                "s000008",
                "p0001",
                QRect::new(6_900, 900, 7_800, 1_400).unwrap(),
                "bottom",
            ),
            span(
                "s000006",
                "p0001",
                QRect::new(800, 900, 1_700, 1_400).unwrap(),
                "bottom",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert_eq!(output.elements.len(), 2);
        assert_eq!(
            output.elements[0].text.as_deref(),
            Some("Left top Left bottom")
        );
        assert_eq!(
            output.elements[0].span_refs,
            vec![
                "s000001".to_string(),
                "s000002".to_string(),
                "s000005".to_string(),
                "s000006".to_string(),
            ]
        );
        assert_eq!(
            output.elements[1].text.as_deref(),
            Some("Right top Right bottom")
        );
        assert_eq!(
            output.elements[1].span_refs,
            vec![
                "s000003".to_string(),
                "s000004".to_string(),
                "s000007".to_string(),
                "s000008".to_string(),
            ]
        );
    }

    #[test]
    fn keeps_pages_isolated() {
        let extraction = Extraction {
            pages: vec![
                Page {
                    id: "p0001".to_string(),
                    index: 1,
                    width: 10_000,
                    height: 10_000,
                    rotation: 0,
                },
                Page {
                    id: "p0002".to_string(),
                    index: 2,
                    width: 10_000,
                    height: 10_000,
                    rotation: 0,
                },
            ],
            spans: vec![
                span(
                    "s000002",
                    "p0002",
                    QRect::new(0, 0, 1_000, 500).unwrap(),
                    "Two",
                ),
                span(
                    "s000001",
                    "p0001",
                    QRect::new(0, 0, 1_000, 500).unwrap(),
                    "One",
                ),
            ],
            regions: vec![],
            warnings: vec![],
        };

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert_eq!(output.elements.len(), 2);
        assert_eq!(output.elements[0].page, "p0001");
        assert_eq!(output.elements[0].text.as_deref(), Some("One"));
        assert_eq!(output.elements[1].page, "p0002");
        assert_eq!(output.elements[1].text.as_deref(), Some("Two"));
    }
}
