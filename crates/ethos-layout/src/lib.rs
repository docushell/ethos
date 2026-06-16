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

//! Basic deterministic layout over quantized extraction spans.
//!
//! This WS-LAYOUT slice intentionally stays deterministic: nearby lines in the same
//! detected column become text-block paragraphs, visually larger/bold short lines are
//! emitted as grounded headings, and multi-column text is ordered by column before
//! vertical position.

use ethos_core::error::EthosError;
use ethos_core::geom::QRect;
use ethos_core::ids::element_id;
use ethos_core::model::{Element, ElementType, Span};
use ethos_core::traits::{Extraction, LayoutEngine, LayoutOutput};

/// Deterministic paragraph-level layout engine.
#[derive(Debug, Clone, Copy, Default)]
pub struct BasicLayoutEngine;

const HEADING_MIN_SIZE_RATIO_PERCENT: i64 = 115;
const HEADING_MAX_CHARS: usize = 120;
const HEADING_MAX_WORDS: usize = 12;
const HEADING_CONFIDENCE_LARGER_AND_BOLD: u16 = 900;
const HEADING_CONFIDENCE_LARGER: u16 = 850;
const HEADING_CONFIDENCE_BOLD_SAME_SIZE: u16 = 720;
const MAX_HEADING_LEVEL: u8 = 3;

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

            let body_font_size_q = body_font_size_q(&page_spans);
            let mut columns = group_columns(group_lines(page_spans));
            columns.sort_by(column_order);
            let heading_sizes = heading_size_levels(&columns, body_font_size_q);

            for column in columns {
                layout_column_lines(
                    column.lines,
                    body_font_size_q,
                    &heading_sizes,
                    &page.id,
                    &mut next_element,
                    &mut elements,
                )?;
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

#[derive(Clone, Copy)]
struct HeadingSignal {
    size_q: i64,
    confidence: u16,
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

fn body_font_size_q(spans: &[SpanRef<'_>]) -> Option<i64> {
    let mut counts = std::collections::BTreeMap::<i64, usize>::new();
    for span_ref in spans {
        if let Some(size) = span_ref.span.font_size_q {
            *counts.entry(size).or_default() += 1;
        }
    }

    counts
        .into_iter()
        .max_by(|(size_a, count_a), (size_b, count_b)| {
            count_a.cmp(count_b).then_with(|| size_b.cmp(size_a))
        })
        .map(|(size, _)| size)
}

fn heading_size_levels(columns: &[Column<'_>], body_font_size_q: Option<i64>) -> Vec<i64> {
    let mut sizes: Vec<i64> = columns
        .iter()
        .flat_map(|column| &column.lines)
        .filter_map(|line| heading_signal(line, body_font_size_q).map(|signal| signal.size_q))
        .collect();
    sizes.sort_unstable_by(|a, b| b.cmp(a));
    sizes.dedup();
    sizes
}

fn layout_column_lines<'a>(
    mut lines: Vec<Line<'a>>,
    body_font_size_q: Option<i64>,
    heading_sizes: &[i64],
    page_id: &str,
    next_element: &mut u32,
    elements: &mut Vec<Element>,
) -> Result<(), EthosError> {
    lines.sort_by(line_order);
    let mut text_lines = Vec::new();
    let mut line_iter = lines.into_iter().peekable();

    while let Some(line) = line_iter.next() {
        if let Some(signal) = heading_signal(&line, body_font_size_q) {
            flush_text_lines(&mut text_lines, page_id, next_element, elements)?;
            let level = heading_level(signal.size_q, heading_sizes);
            let mut confidence = signal.confidence;
            let mut heading_lines = vec![line];
            while let Some(next_line) = line_iter.peek() {
                let Some(next_signal) = heading_signal(next_line, body_font_size_q) else {
                    break;
                };
                if heading_level(next_signal.size_q, heading_sizes) != level
                    || !same_wrapped_heading_line(
                        heading_lines
                            .last()
                            .expect("heading_lines is initialized with one line"),
                        next_line,
                    )
                {
                    break;
                }
                let next_line = line_iter
                    .next()
                    .expect("peeked heading line must still be available");
                confidence = confidence.min(next_signal.confidence);
                heading_lines.push(next_line);
            }
            let heading_spans = lines_spans(&heading_lines);
            elements.push(build_element(
                *next_element,
                page_id,
                &heading_spans,
                ElementType::Heading,
                Some(level),
                Some(confidence),
            )?);
            *next_element += 1;
        } else {
            text_lines.push(line);
        }
    }

    flush_text_lines(&mut text_lines, page_id, next_element, elements)
}

fn flush_text_lines<'a>(
    text_lines: &mut Vec<Line<'a>>,
    page_id: &str,
    next_element: &mut u32,
    elements: &mut Vec<Element>,
) -> Result<(), EthosError> {
    if text_lines.is_empty() {
        return Ok(());
    }
    for paragraph in group_paragraphs(std::mem::take(text_lines)) {
        let paragraph_spans = paragraph_spans(&paragraph);
        elements.push(build_element(
            *next_element,
            page_id,
            &paragraph_spans,
            ElementType::TextBlock,
            None,
            None,
        )?);
        *next_element += 1;
    }
    Ok(())
}

fn heading_signal(line: &Line<'_>, body_font_size_q: Option<i64>) -> Option<HeadingSignal> {
    let body_size = body_font_size_q?;
    let line_size = line_font_size_q(line)?;
    let text = line_text(line);
    let trimmed = text.trim();
    if trimmed.is_empty()
        || trimmed.chars().count() > HEADING_MAX_CHARS
        || word_count(trimmed) > HEADING_MAX_WORDS
    {
        return None;
    }
    if trimmed.ends_with('.') || trimmed.ends_with(',') || trimmed.ends_with(';') {
        return None;
    }

    let larger =
        line_size > body_size && line_size * 100 >= body_size * HEADING_MIN_SIZE_RATIO_PERCENT;
    let bold_same_size = line_size >= body_size && line_is_boldish(line);
    if !larger && !bold_same_size {
        return None;
    }

    let confidence = if larger && bold_same_size {
        HEADING_CONFIDENCE_LARGER_AND_BOLD
    } else if larger {
        HEADING_CONFIDENCE_LARGER
    } else if bold_same_size {
        HEADING_CONFIDENCE_BOLD_SAME_SIZE
    } else {
        return None;
    };
    Some(HeadingSignal {
        size_q: line_size,
        confidence,
    })
}

fn heading_level(size_q: i64, heading_sizes: &[i64]) -> u8 {
    heading_sizes
        .iter()
        .position(|size| *size == size_q)
        .map(|index| (index as u8 + 1).min(MAX_HEADING_LEVEL))
        .unwrap_or(MAX_HEADING_LEVEL)
}

fn line_font_size_q(line: &Line<'_>) -> Option<i64> {
    line.spans
        .iter()
        .filter_map(|span_ref| span_ref.span.font_size_q)
        .max()
}

fn line_text(line: &Line<'_>) -> String {
    line_spans(line)
        .iter()
        .map(|span_ref| span_ref.span.text.as_str())
        .collect::<Vec<_>>()
        .join(" ")
}

fn word_count(text: &str) -> usize {
    text.split_whitespace().count()
}

fn line_is_boldish(line: &Line<'_>) -> bool {
    !line.spans.is_empty()
        && line
            .spans
            .iter()
            .all(|span_ref| span_is_boldish(span_ref.span))
}

fn span_is_boldish(span: &Span) -> bool {
    span.font_id.as_deref().is_some_and(|font_id| {
        let font_id = font_id.to_ascii_lowercase();
        font_id.contains("bold") || font_id.contains("semibold") || font_id.contains("black")
    })
}

fn same_wrapped_heading_line(previous: &Line<'_>, current: &Line<'_>) -> bool {
    let gap = current.bbox.y0 - previous.bbox.y1;
    let height = line_height(previous.bbox)
        .max(line_height(current.bbox))
        .max(1);
    gap >= -height && gap <= height * 2 && horizontal_overlap(previous.bbox, current.bbox) > 0
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
        spans.extend(line_spans(line));
    }
    spans
}

fn lines_spans<'a>(lines: &[Line<'a>]) -> Vec<SpanRef<'a>> {
    lines.iter().flat_map(line_spans).collect()
}

fn line_spans<'a>(line: &Line<'a>) -> Vec<SpanRef<'a>> {
    let mut line_spans = line.spans.clone();
    line_spans.sort_by(span_reading_order);
    line_spans
}

fn build_element(
    ordinal: u32,
    page_id: &str,
    spans: &[SpanRef<'_>],
    element_type: ElementType,
    heading_level: Option<u8>,
    confidence: Option<u16>,
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
        element_type,
        page: page_id.to_string(),
        bbox: bbox.ok_or_else(|| EthosError::internal("text block has no bbox"))?,
        text: Some(text),
        heading_level,
        table_ref: None,
        region_ref: None,
        confidence,
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
        styled_span(id, page, bbox, text, None, Some(1200))
    }

    fn styled_span(
        id: &str,
        page: &str,
        bbox: QRect,
        text: &str,
        font_id: Option<&str>,
        font_size_q: Option<i64>,
    ) -> Span {
        Span {
            id: id.to_string(),
            page: page.to_string(),
            bbox,
            origin_locator: None,
            text: text.to_string(),
            font_id: font_id.map(str::to_string),
            font_size_q,
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
    fn classifies_large_line_as_heading_before_paragraph_merge() {
        let extraction = extraction(vec![
            styled_span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 900, 700).unwrap(),
                "Overview",
                None,
                Some(1800),
            ),
            span(
                "s000002",
                "p0001",
                QRect::new(0, 850, 700, 1_350).unwrap(),
                "Body",
            ),
            span(
                "s000003",
                "p0001",
                QRect::new(850, 850, 1_300, 1_350).unwrap(),
                "text",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert_eq!(output.elements.len(), 2);
        assert_eq!(output.elements[0].element_type, ElementType::Heading);
        assert_eq!(output.elements[0].heading_level, Some(1));
        assert_eq!(output.elements[0].confidence, Some(850));
        assert_eq!(output.elements[0].text.as_deref(), Some("Overview"));
        assert_eq!(output.elements[0].span_refs, vec!["s000001".to_string()]);
        assert_eq!(output.elements[1].element_type, ElementType::TextBlock);
        assert_eq!(output.elements[1].text.as_deref(), Some("Body text"));
    }

    #[test]
    fn classifies_same_size_bold_line_as_heading() {
        let extraction = extraction(vec![
            styled_span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 900, 500).unwrap(),
                "Background",
                Some("embedded:Fixture-Bold"),
                Some(1200),
            ),
            span(
                "s000002",
                "p0001",
                QRect::new(0, 800, 600, 1_300).unwrap(),
                "Plain",
            ),
            span(
                "s000003",
                "p0001",
                QRect::new(750, 800, 1_100, 1_300).unwrap(),
                "body",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert_eq!(output.elements.len(), 2);
        assert_eq!(output.elements[0].element_type, ElementType::Heading);
        assert_eq!(output.elements[0].heading_level, Some(1));
        assert_eq!(output.elements[0].confidence, Some(720));
        assert_eq!(output.elements[0].text.as_deref(), Some("Background"));
        assert_eq!(output.elements[1].text.as_deref(), Some("Plain body"));
    }

    #[test]
    fn does_not_classify_sentence_like_large_line_as_heading() {
        let extraction = extraction(vec![
            styled_span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 1_200, 700).unwrap(),
                "Overview.",
                None,
                Some(1800),
            ),
            span(
                "s000002",
                "p0001",
                QRect::new(0, 1_100, 700, 1_600).unwrap(),
                "Body",
            ),
            span(
                "s000003",
                "p0001",
                QRect::new(850, 1_100, 1_300, 1_600).unwrap(),
                "text",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert!(output
            .elements
            .iter()
            .all(|element| element.element_type == ElementType::TextBlock));
    }

    #[test]
    fn does_not_classify_long_large_line_as_heading() {
        let extraction = extraction(vec![
            styled_span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 6_000, 700).unwrap(),
                "One two three four five six seven eight nine ten eleven twelve thirteen",
                None,
                Some(1800),
            ),
            span(
                "s000002",
                "p0001",
                QRect::new(0, 1_100, 700, 1_600).unwrap(),
                "Body",
            ),
            span(
                "s000003",
                "p0001",
                QRect::new(850, 1_100, 1_300, 1_600).unwrap(),
                "text",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert!(output
            .elements
            .iter()
            .all(|element| element.element_type == ElementType::TextBlock));
    }

    #[test]
    fn does_not_classify_slightly_larger_line_as_heading() {
        let extraction = extraction(vec![
            styled_span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 900, 600).unwrap(),
                "Overview",
                None,
                Some(1300),
            ),
            span(
                "s000002",
                "p0001",
                QRect::new(0, 900, 700, 1_400).unwrap(),
                "Body",
            ),
            span(
                "s000003",
                "p0001",
                QRect::new(850, 900, 1_300, 1_400).unwrap(),
                "text",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert!(output
            .elements
            .iter()
            .all(|element| element.element_type == ElementType::TextBlock));
    }

    #[test]
    fn caps_heading_levels_at_three() {
        let extraction = extraction(vec![
            styled_span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 900, 500).unwrap(),
                "Title",
                None,
                Some(2400),
            ),
            styled_span(
                "s000002",
                "p0001",
                QRect::new(0, 2_000, 900, 2_500).unwrap(),
                "Section",
                None,
                Some(2100),
            ),
            styled_span(
                "s000003",
                "p0001",
                QRect::new(0, 4_000, 900, 4_500).unwrap(),
                "Subsection",
                None,
                Some(1800),
            ),
            styled_span(
                "s000004",
                "p0001",
                QRect::new(0, 6_000, 900, 6_500).unwrap(),
                "Detail",
                None,
                Some(1600),
            ),
            span(
                "s000005",
                "p0001",
                QRect::new(0, 8_000, 600, 8_500).unwrap(),
                "Body",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();
        let levels = output
            .elements
            .iter()
            .filter_map(|element| element.heading_level)
            .collect::<Vec<_>>();

        assert_eq!(levels, vec![1, 2, 3, MAX_HEADING_LEVEL]);
    }

    #[test]
    fn merges_adjacent_wrapped_heading_lines() {
        let extraction = extraction(vec![
            styled_span(
                "s000001",
                "p0001",
                QRect::new(0, 0, 2_600, 700).unwrap(),
                "Very Long Title",
                None,
                Some(1800),
            ),
            styled_span(
                "s000002",
                "p0001",
                QRect::new(0, 850, 2_100, 1_550).unwrap(),
                "Continued",
                None,
                Some(1800),
            ),
            span(
                "s000003",
                "p0001",
                QRect::new(0, 2_200, 700, 2_700).unwrap(),
                "Body",
            ),
            span(
                "s000004",
                "p0001",
                QRect::new(850, 2_200, 1_300, 2_700).unwrap(),
                "text",
            ),
        ]);

        let output = BasicLayoutEngine.layout(&extraction).unwrap();

        assert_eq!(output.elements.len(), 2);
        assert_eq!(output.elements[0].element_type, ElementType::Heading);
        assert_eq!(
            output.elements[0].text.as_deref(),
            Some("Very Long Title Continued")
        );
        assert_eq!(
            output.elements[0].span_refs,
            vec!["s000001".to_string(), "s000002".to_string()]
        );
        assert_eq!(output.elements[1].text.as_deref(), Some("Body text"));
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
