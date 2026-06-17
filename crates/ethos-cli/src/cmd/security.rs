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

use std::cmp::Ordering;
use std::collections::BTreeMap;

use ethos_core::codes::WarningCode;
use ethos_core::error::EthosError;
use ethos_core::model::{Document, Element, Page, Span, Warning};

use crate::{read_document, write_output, Failure, SecurityReportArgs};

pub(crate) fn security_report(args: SecurityReportArgs) -> Result<(), Failure> {
    let doc = read_document(&args.input)?;
    let out = security_report_output_bytes(&doc)?;
    write_output(args.out, &out)
}

fn security_report_output_bytes(doc: &Document) -> Result<Vec<u8>, Failure> {
    let refs = SecurityReportRefs::new(doc);
    for warning in &doc.payload.parser_warnings {
        if warning.code.is_security() {
            return Err(Failure::Usage(format!(
                "security report parser warning {} ({}) must be in security_warnings",
                warning.id,
                warning.code.as_str()
            )));
        }
    }
    let mut warnings = Vec::with_capacity(doc.payload.security_warnings.len());
    for warning in &doc.payload.security_warnings {
        if !warning.code.is_security() {
            return Err(Failure::Usage(format!(
                "security report warning {} ({}) is not a security warning code",
                warning.id,
                warning.code.as_str()
            )));
        }
        warnings.push(warning);
    }
    warnings.sort_by(|left, right| warning_order(left, right));

    let mut summary: BTreeMap<String, u64> = BTreeMap::new();
    let mut findings = Vec::with_capacity(warnings.len());
    for (index, warning) in warnings.iter().enumerate() {
        block_inventory_backed_warning(warning)?;
        *summary
            .entry(warning.code.as_str().to_string())
            .or_insert(0) += 1;
        findings.push(finding_record(index, warning, &refs)?);
    }

    let value = serde_json::json!({
        "schema_version": doc.schema_version.as_str(),
        "document_fingerprint": doc.fingerprint.as_str(),
        "source_fingerprint": doc.source.fingerprint.as_str(),
        "profile": {
            "id": doc.profile.id.as_str(),
            "sha256": doc.profile.sha256.as_str(),
        },
        "summary": summary,
        "findings": findings,
        "inventories": {
            "annotations": [],
            "actions": [],
            "attachments": [],
            "scripts": [],
            "links": [],
        },
    });
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    Ok(bytes)
}

struct SecurityReportRefs<'a> {
    pages: BTreeMap<&'a str, &'a Page>,
    elements: BTreeMap<&'a str, &'a Element>,
    spans: BTreeMap<&'a str, &'a Span>,
}

impl<'a> SecurityReportRefs<'a> {
    fn new(doc: &'a Document) -> Self {
        Self {
            pages: doc
                .payload
                .pages
                .iter()
                .map(|page| (page.id.as_str(), page))
                .collect(),
            elements: doc
                .payload
                .elements
                .iter()
                .map(|element| (element.id.as_str(), element))
                .collect(),
            spans: doc
                .payload
                .spans
                .iter()
                .map(|span| (span.id.as_str(), span))
                .collect(),
        }
    }
}

fn inventory_backed_warning_code(code: WarningCode) -> bool {
    matches!(
        code,
        WarningCode::AnnotationsPresent
            | WarningCode::ExternalLinksPresent
            | WarningCode::UnsupportedAnnotation
    )
}

fn text_backed_warning_code(code: WarningCode) -> bool {
    matches!(
        code,
        WarningCode::HiddenTextDetected
            | WarningCode::OffPageTextDetected
            | WarningCode::LowContrastTextDetected
    )
}

fn page_backed_warning_code(code: WarningCode) -> bool {
    text_backed_warning_code(code) || matches!(code, WarningCode::ImageOnlyPage)
}

fn excludes_from_default_chunks(code: WarningCode) -> bool {
    text_backed_warning_code(code)
}

fn warning_order(left: &Warning, right: &Warning) -> Ordering {
    (
        left.code.as_str(),
        left.page.as_deref().unwrap_or(""),
        left.element_ref.as_deref().unwrap_or(""),
        left.span_ref.as_deref().unwrap_or(""),
        left.region_ref.as_deref().unwrap_or(""),
        left.message.as_str(),
    )
        .cmp(&(
            right.code.as_str(),
            right.page.as_deref().unwrap_or(""),
            right.element_ref.as_deref().unwrap_or(""),
            right.span_ref.as_deref().unwrap_or(""),
            right.region_ref.as_deref().unwrap_or(""),
            right.message.as_str(),
        ))
}

fn block_inventory_backed_warning(warning: &Warning) -> Result<(), Failure> {
    if inventory_backed_warning_code(warning.code) {
        return Err(Failure::Usage(format!(
            "security report warning {} ({}) requires inventory data not available in canonical document",
            warning.id,
            warning.code.as_str()
        )));
    }
    Ok(())
}

fn finding_record(
    index: usize,
    warning: &Warning,
    refs: &SecurityReportRefs<'_>,
) -> Result<serde_json::Value, Failure> {
    validate_warning_refs(warning, refs)?;
    let mut finding = serde_json::Map::new();
    finding.insert(
        "id".to_string(),
        serde_json::Value::String(format!("f{:04}", index + 1)),
    );
    finding.insert(
        "code".to_string(),
        serde_json::Value::String(warning.code.as_str().to_string()),
    );
    finding.insert(
        "message".to_string(),
        serde_json::Value::String(warning.message.clone()),
    );
    if let Some(page) = &warning.page {
        finding.insert("page".to_string(), serde_json::Value::String(page.clone()));
    }
    if let Some(element_ref) = &warning.element_ref {
        finding.insert(
            "element_ref".to_string(),
            serde_json::Value::String(element_ref.clone()),
        );
    }
    if let Some(span_ref) = &warning.span_ref {
        finding.insert(
            "span_ref".to_string(),
            serde_json::Value::String(span_ref.clone()),
        );
    }
    if text_backed_warning_code(warning.code) {
        let span_ref = warning
            .span_ref
            .as_deref()
            .expect("text warning refs validated");
        let span = refs
            .spans
            .get(span_ref)
            .expect("text warning span_ref validated");
        let page_ref = warning
            .page
            .as_deref()
            .expect("text warning page validated");
        let page = refs
            .pages
            .get(page_ref)
            .expect("text warning page validated");
        validate_span_bbox(warning, span_ref, span, page)?;
        finding.insert("bbox".to_string(), serde_json::json!(span.bbox.to_array()));
        finding.insert(
            "text_preview".to_string(),
            serde_json::Value::String(deterministic_preview(&span.text)),
        );
    }
    finding.insert(
        "excluded_from_default_chunks".to_string(),
        serde_json::Value::Bool(excludes_from_default_chunks(warning.code)),
    );
    Ok(serde_json::Value::Object(finding))
}

fn validate_warning_refs(warning: &Warning, refs: &SecurityReportRefs<'_>) -> Result<(), Failure> {
    if let Some(region_ref) = warning.region_ref.as_deref() {
        return Err(Failure::Usage(format!(
            "security report warning {} region_ref {} is unsupported until security report schema supports region_ref",
            warning.id, region_ref
        )));
    }
    if page_backed_warning_code(warning.code) && warning.page.is_none() {
        return Err(Failure::Usage(format!(
            "security report warning {} ({}) requires page",
            warning.id,
            warning.code.as_str()
        )));
    }
    if let Some(page) = warning.page.as_deref() {
        if !refs.pages.contains_key(page) {
            return Err(Failure::Usage(format!(
                "security report warning {} references unknown page {}",
                warning.id, page
            )));
        }
    }
    let element = match warning.element_ref.as_deref() {
        Some(element_ref) => {
            let Some(element) = refs.elements.get(element_ref) else {
                return Err(Failure::Usage(format!(
                    "security report warning {} references unknown element_ref {}",
                    warning.id, element_ref
                )));
            };
            if let Some(page) = warning.page.as_deref() {
                if element.page != page {
                    return Err(Failure::Usage(format!(
                        "security report warning {} element_ref {} page {} does not match page {}",
                        warning.id, element_ref, element.page, page
                    )));
                }
            }
            Some(*element)
        }
        None => None,
    };
    if text_backed_warning_code(warning.code) && warning.span_ref.is_none() {
        return Err(Failure::Usage(format!(
            "security report warning {} ({}) requires span_ref",
            warning.id,
            warning.code.as_str()
        )));
    }
    if let Some(span_ref) = warning.span_ref.as_deref() {
        let Some(span) = refs.spans.get(span_ref) else {
            return Err(Failure::Usage(format!(
                "security report warning {} references unknown span_ref {}",
                warning.id, span_ref
            )));
        };
        if let Some(page) = warning.page.as_deref() {
            if span.page != page {
                return Err(Failure::Usage(format!(
                    "security report warning {} span_ref {} page {} does not match page {}",
                    warning.id, span_ref, span.page, page
                )));
            }
        }
        if let Some(element) = element {
            if !element.span_refs.iter().any(|id| id == span_ref) {
                return Err(Failure::Usage(format!(
                    "security report warning {} span_ref {} is not owned by element_ref {}",
                    warning.id, span_ref, element.id
                )));
            }
        }
    }
    Ok(())
}

fn validate_span_bbox(
    warning: &Warning,
    span_ref: &str,
    span: &Span,
    page: &Page,
) -> Result<(), Failure> {
    let [x0, y0, x1, y1] = span.bbox.to_array();
    if x0 >= x1 || y0 >= y1 {
        return Err(Failure::Usage(format!(
            "security report warning {} span_ref {} bbox has zero area",
            warning.id, span_ref
        )));
    }
    if x0 < 0 || y0 < 0 || x1 > page.width || y1 > page.height {
        return Err(Failure::Usage(format!(
            "security report warning {} span_ref {} bbox exceeds page {} bounds",
            warning.id, span_ref, page.id
        )));
    }
    Ok(())
}

fn deterministic_preview(text: &str) -> String {
    let mut chars = text.chars();
    let preview: String = chars.by_ref().take(120).collect();
    if chars.next().is_some() {
        format!("{preview}\u{2026}")
    } else {
        preview
    }
}
