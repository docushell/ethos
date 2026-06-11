//! Basic deterministic layout over quantized extraction spans.
//!
//! This first WS-ENGINE/WS-LAYOUT slice intentionally makes only one claim:
//! spans on the same detected text line become one `text_block` element. Higher-level
//! paragraph, heading, list, column, and table semantics belong to later layout lanes.

use ethos_core::error::EthosError;
use ethos_core::geom::QRect;
use ethos_core::ids::element_id;
use ethos_core::model::{Element, ElementType, Span};
use ethos_core::traits::{Extraction, LayoutEngine, LayoutOutput};

/// Deterministic line-level layout engine.
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

            let mut lines = group_lines(page_spans);
            lines.sort_by(line_order);

            for line in lines {
                let mut line_spans = line.spans;
                line_spans.sort_by(span_reading_order);
                let element = build_text_block(next_element, &page.id, &line_spans)?;
                elements.push(element);
                next_element += 1;
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

fn group_lines(mut spans: Vec<SpanRef<'_>>) -> Vec<Line<'_>> {
    spans.sort_by(span_line_order);
    let tolerance = line_tolerance(&spans);
    let mut lines: Vec<Line<'_>> = Vec::new();

    for span_ref in spans {
        if let Some(line) = lines
            .iter_mut()
            .find(|line| same_line(line, span_ref, tolerance))
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

fn line_tolerance(spans: &[SpanRef<'_>]) -> i64 {
    let mut heights: Vec<i64> = spans
        .iter()
        .map(|span| (span.span.bbox.y1 - span.span.bbox.y0).max(1))
        .collect();
    heights.sort_unstable();
    let median = heights.get(heights.len() / 2).copied().unwrap_or(1);
    (median / 2).max(50)
}

fn same_line(line: &Line<'_>, span_ref: SpanRef<'_>, tolerance: i64) -> bool {
    (span_ref.center_y - line.center_y).abs() <= tolerance
        || vertical_overlap(line.bbox, span_ref.span.bbox) > 0
}

fn vertical_overlap(a: QRect, b: QRect) -> i64 {
    a.y1.min(b.y1) - a.y0.max(b.y0)
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
    fn groups_spans_by_line_in_reading_order() {
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

        assert_eq!(output.elements.len(), 2);
        assert_eq!(output.elements[0].id, "e000001");
        assert_eq!(output.elements[0].text.as_deref(), Some("Hello world"));
        assert_eq!(
            output.elements[0].span_refs,
            vec!["s000001".to_string(), "s000002".to_string()]
        );
        assert_eq!(output.elements[1].id, "e000002");
        assert_eq!(output.elements[1].text.as_deref(), Some("Second line"));
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
