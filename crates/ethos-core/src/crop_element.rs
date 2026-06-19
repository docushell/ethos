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

//! Internal source-only `crop_element` resolver for Milestone D contract work.
//!
//! This module validates the committed request and descriptor identity rules over
//! native Ethos document JSON. It intentionally does not add a CLI command,
//! binding surface, rendered backend, or sandbox boundary.

use crate::c14n;
use crate::error::EthosError;
use crate::model::{Document, Page};
use crate::SCHEMA_VERSION;
use serde::{Deserialize, Serialize};
use serde_json::json;

const CROP_ELEMENT_REQUEST_ARTIFACT_TYPE: &str = "ethos.crop_element_request.v1";
const CROP_DESCRIPTOR_ARTIFACT_TYPE: &str = "ethos.crop_descriptor.v1";
const CROP_ELEMENT_REQUEST_REF_VERSION: &str = "ethos.crop_element_request_ref.v1";
const LOGICAL_CROP_REF_VERSION: &str = "ethos.logical_crop_ref.v1";

/// Source-only `crop_element` request envelope.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CropElementRequest {
    /// Request artifact type, currently `ethos.crop_element_request.v1`.
    pub artifact_type: String,
    /// Contract schema version.
    pub schema_version: String,
    /// Stable request identity.
    pub request_ref: String,
    /// Expected canonical document fingerprint.
    pub document_fingerprint: String,
    /// Element id in the canonical Ethos document graph.
    pub element_id: String,
    /// Requested rendering mode.
    pub rendering: CropElementRendering,
    /// Fingerprint of caller-provided source PDF bytes for rendered requests.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_pdf_fingerprint: Option<String>,
}

/// Supported `crop_element` rendering modes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CropElementRendering {
    /// Emit only a JSON crop descriptor.
    DescriptorOnly,
    /// Emit a crop descriptor plus rendered crop artifact.
    Rendered,
}

impl CropElementRendering {
    fn as_contract_str(self) -> &'static str {
        match self {
            CropElementRendering::DescriptorOnly => "descriptor_only",
            CropElementRendering::Rendered => "rendered",
        }
    }
}

/// Deterministic JSON descriptor for one resolved crop element.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CropElementDescriptor {
    /// Descriptor artifact type, currently `ethos.crop_descriptor.v1`.
    pub artifact_type: String,
    /// Contract schema version.
    pub schema_version: String,
    /// Stable descriptor filename.
    pub crop_ref: String,
    /// Canonical document fingerprint.
    pub document_fingerprint: String,
    /// Resolved page id.
    pub page: String,
    /// Resolved element bounding box in contract array form.
    pub bbox: [i64; 4],
    /// Logical verification check ids bound to this descriptor.
    pub check_ids: Vec<String>,
    /// Descriptor rendering status.
    pub rendering_status: CropElementRendering,
    /// Fingerprint of caller-provided source PDF bytes for rendered descriptors.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_pdf_fingerprint: Option<String>,
    /// Stable rendered crop filename.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rendered_ref: Option<String>,
    /// Rendered crop format.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rendered_format: Option<String>,
    /// SHA-256 of rendered crop bytes.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rendered_sha256: Option<String>,
    /// Rendered crop width in pixels.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rendered_width_px: Option<u32>,
    /// Rendered crop height in pixels.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rendered_height_px: Option<u32>,
    /// SHA-256 of resolved element text when textual evidence is present.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text_sha256: Option<String>,
}

/// Fail-closed `crop_element` resolver diagnostic.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CropElementError {
    diagnostic: &'static str,
}

impl CropElementError {
    /// Deterministic diagnostic message for the resolver failure.
    pub fn diagnostic(&self) -> &'static str {
        self.diagnostic
    }

    fn new(diagnostic: &'static str) -> Self {
        CropElementError { diagnostic }
    }
}

impl core::fmt::Display for CropElementError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str(self.diagnostic)
    }
}

impl std::error::Error for CropElementError {}

/// Compute the source-only `crop_element` request identity.
pub fn crop_element_request_ref(request: &CropElementRequest) -> Result<String, EthosError> {
    let mut identity = json!({
        "document_fingerprint": request.document_fingerprint,
        "element_id": request.element_id,
        "rendering": request.rendering.as_contract_str(),
        "version": CROP_ELEMENT_REQUEST_REF_VERSION,
    });
    if let Some(source_pdf_fingerprint) = &request.source_pdf_fingerprint {
        identity.as_object_mut().expect("json object").insert(
            "source_pdf_fingerprint".to_string(),
            json!(source_pdf_fingerprint),
        );
    }
    let digest = c14n::sha256_hex(&identity)
        .map_err(|err| EthosError::internal(format!("crop_element request_ref error: {err}")))?;
    Ok(format!("request-{digest}"))
}

/// Compute the logical crop descriptor filename for a bound verification check.
pub fn crop_element_crop_ref(
    document_fingerprint: &str,
    check_id: &str,
    page: &str,
) -> Result<String, EthosError> {
    let identity = json!({
        "check_id": check_id,
        "document_fingerprint": document_fingerprint,
        "page": page,
        "version": LOGICAL_CROP_REF_VERSION,
    });
    let digest = c14n::sha256_hex(&identity)
        .map_err(|err| EthosError::internal(format!("crop_element crop_ref error: {err}")))?;
    Ok(format!("crop-{digest}.json"))
}

/// Resolve one descriptor-only crop descriptor from a native Ethos document and request.
pub fn resolve_crop_element_descriptor(
    document: &Document,
    request: &CropElementRequest,
    check_id: &str,
) -> Result<CropElementDescriptor, CropElementError> {
    if request.artifact_type != CROP_ELEMENT_REQUEST_ARTIFACT_TYPE {
        return Err(CropElementError::new(
            "request artifact_type is not ethos.crop_element_request.v1",
        ));
    }
    if request.schema_version != SCHEMA_VERSION {
        return Err(CropElementError::new(
            "request schema_version is not supported",
        ));
    }
    if request.request_ref.is_empty() {
        return Err(CropElementError::new("request_ref is missing"));
    }
    if request.document_fingerprint.is_empty() || document.fingerprint.is_empty() {
        return Err(CropElementError::new("document_fingerprint is missing"));
    }
    let expected_request_ref = crop_element_request_ref(request).map_err(|_| {
        CropElementError::new("request_ref does not match crop element request identity tuple")
    })?;
    if request.request_ref != expected_request_ref {
        return Err(CropElementError::new(
            "request_ref does not match crop element request identity tuple",
        ));
    }
    if request.document_fingerprint != document.fingerprint {
        return Err(CropElementError::new(
            "request document_fingerprint does not match document fingerprint",
        ));
    }
    if !is_check_id(check_id) {
        return Err(CropElementError::new(
            "descriptor must bind exactly one logical check id",
        ));
    }
    if request.rendering == CropElementRendering::Rendered {
        return Err(CropElementError::new(
            "rendered crop_element requests remain blocked for internal descriptor resolver",
        ));
    }
    if request.source_pdf_fingerprint.is_some() {
        return Err(CropElementError::new(
            "descriptor_only crop_element request must not include source_pdf_fingerprint",
        ));
    }

    let element = document
        .payload
        .elements
        .iter()
        .find(|element| element.id == request.element_id)
        .ok_or_else(|| CropElementError::new("request element_id does not resolve in document"))?;
    let page = document
        .payload
        .pages
        .iter()
        .find(|page| page.id == element.page)
        .ok_or_else(|| CropElementError::new("resolved element is missing page"))?;
    validate_resolved_bbox(element.bbox, page)?;

    let text_sha256 = element
        .text
        .as_deref()
        .map(|text| c14n::sha256_hex_bytes(text.as_bytes()));
    let crop_ref =
        crop_element_crop_ref(&document.fingerprint, check_id, &element.page).map_err(|_| {
            CropElementError::new("descriptor crop_ref does not match logical identity tuple")
        })?;

    Ok(CropElementDescriptor {
        artifact_type: CROP_DESCRIPTOR_ARTIFACT_TYPE.to_string(),
        schema_version: SCHEMA_VERSION.to_string(),
        crop_ref,
        document_fingerprint: document.fingerprint.clone(),
        page: element.page.clone(),
        bbox: element.bbox.to_array(),
        check_ids: vec![check_id.to_string()],
        rendering_status: CropElementRendering::DescriptorOnly,
        source_pdf_fingerprint: None,
        rendered_ref: None,
        rendered_format: None,
        rendered_sha256: None,
        rendered_width_px: None,
        rendered_height_px: None,
        text_sha256,
    })
}

fn validate_resolved_bbox(bbox: crate::geom::QRect, page: &Page) -> Result<(), CropElementError> {
    let [x0, y0, x1, y1] = bbox.to_array();
    if x0 >= x1 || y0 >= y1 {
        return Err(CropElementError::new(
            "resolved element bbox has non-positive area",
        ));
    }
    if x0 < 0 || y0 < 0 || x1 > page.width || y1 > page.height {
        return Err(CropElementError::new(
            "resolved element bbox exceeds page bounds",
        ));
    }
    Ok(())
}

fn is_check_id(value: &str) -> bool {
    value.len() == 5
        && value
            .strip_prefix('v')
            .is_some_and(|digits| digits.chars().all(|ch| ch.is_ascii_digit()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::Document;
    use serde_json::Value;

    fn fixture_document() -> Document {
        serde_json::from_str(include_str!(
            "../../../schemas/examples/document.example.json"
        ))
        .unwrap()
    }

    fn fixture_request() -> CropElementRequest {
        serde_json::from_str(include_str!(
            "../../../schemas/examples/crop-element-request.example.json"
        ))
        .unwrap()
    }

    fn expected_descriptor_value() -> Value {
        serde_json::from_str(include_str!(
            "../../../schemas/examples/crop-descriptor.example.json"
        ))
        .unwrap()
    }

    #[test]
    fn crop_element_descriptor_matches_committed_example() {
        let descriptor =
            resolve_crop_element_descriptor(&fixture_document(), &fixture_request(), "v0001")
                .unwrap();

        assert_eq!(
            serde_json::to_value(descriptor).unwrap(),
            expected_descriptor_value()
        );
    }

    #[test]
    fn crop_element_request_ref_matches_committed_example() {
        let request = fixture_request();

        assert_eq!(
            crop_element_request_ref(&request).unwrap(),
            request.request_ref
        );
    }

    #[test]
    fn crop_element_crop_ref_matches_committed_descriptor() {
        let document = fixture_document();
        let descriptor = expected_descriptor_value();

        assert_eq!(
            crop_element_crop_ref(&document.fingerprint, "v0001", "p0001").unwrap(),
            descriptor["crop_ref"]
        );
    }

    #[test]
    fn stale_request_ref_fails_closed() {
        let mut request = fixture_request();
        request.request_ref = format!("request-{}", "0".repeat(64));

        let err = resolve_crop_element_descriptor(&fixture_document(), &request, "v0001")
            .expect_err("stale request_ref must fail");

        assert_eq!(
            err.diagnostic(),
            "request_ref does not match crop element request identity tuple"
        );
    }

    #[test]
    fn document_fingerprint_mismatch_fails_closed() {
        let mut request = fixture_request();
        request.document_fingerprint = format!("sha256:{}", "0".repeat(64));
        request.request_ref = crop_element_request_ref(&request).unwrap();

        let err = resolve_crop_element_descriptor(&fixture_document(), &request, "v0001")
            .expect_err("document fingerprint mismatch must fail");

        assert_eq!(
            err.diagnostic(),
            "request document_fingerprint does not match document fingerprint"
        );
    }

    #[test]
    fn missing_document_fingerprint_fails_closed() {
        let mut document = fixture_document();
        document.fingerprint.clear();
        let mut request = fixture_request();
        request.document_fingerprint.clear();
        request.request_ref = crop_element_request_ref(&request).unwrap();

        let err = resolve_crop_element_descriptor(&document, &request, "v0001")
            .expect_err("missing document fingerprint must fail");

        assert_eq!(err.diagnostic(), "document_fingerprint is missing");
    }

    #[test]
    fn unresolved_element_fails_closed() {
        let mut request = fixture_request();
        request.element_id = "e999999".to_string();
        request.request_ref = crop_element_request_ref(&request).unwrap();

        let err = resolve_crop_element_descriptor(&fixture_document(), &request, "v0001")
            .expect_err("unknown element must fail");

        assert_eq!(
            err.diagnostic(),
            "request element_id does not resolve in document"
        );
    }

    #[test]
    fn missing_element_page_fails_closed() {
        let mut document = fixture_document();
        document.payload.pages.clear();

        let err = resolve_crop_element_descriptor(&document, &fixture_request(), "v0001")
            .expect_err("missing page must fail");

        assert_eq!(err.diagnostic(), "resolved element is missing page");
    }

    #[test]
    fn zero_area_element_bbox_fails_closed() {
        let mut document = fixture_document();
        let element = document
            .payload
            .elements
            .iter_mut()
            .find(|element| element.id == fixture_request().element_id)
            .expect("fixture element exists");
        element.bbox = crate::geom::QRect::new(10, 20, 10, 30).unwrap();

        let err = resolve_crop_element_descriptor(&document, &fixture_request(), "v0001")
            .expect_err("zero-area bbox must fail");

        assert_eq!(
            err.diagnostic(),
            "resolved element bbox has non-positive area"
        );
    }

    #[test]
    fn negative_element_bbox_fails_closed() {
        let mut document = fixture_document();
        let element = document
            .payload
            .elements
            .iter_mut()
            .find(|element| element.id == fixture_request().element_id)
            .expect("fixture element exists");
        element.bbox = crate::geom::QRect::new(-1, 0, 10, 10).unwrap();

        let err = resolve_crop_element_descriptor(&document, &fixture_request(), "v0001")
            .expect_err("negative bbox coordinate must fail");

        assert_eq!(
            err.diagnostic(),
            "resolved element bbox exceeds page bounds"
        );
    }

    #[test]
    fn page_overflow_element_bbox_fails_closed() {
        let mut document = fixture_document();
        let page = document
            .payload
            .pages
            .iter()
            .find(|page| page.id == "p0001")
            .expect("fixture page exists")
            .clone();
        let element = document
            .payload
            .elements
            .iter_mut()
            .find(|element| element.id == fixture_request().element_id)
            .expect("fixture element exists");
        element.bbox = crate::geom::QRect::new(0, 0, page.width + 1, 10).unwrap();

        let err = resolve_crop_element_descriptor(&document, &fixture_request(), "v0001")
            .expect_err("bbox beyond page width must fail");

        assert_eq!(
            err.diagnostic(),
            "resolved element bbox exceeds page bounds"
        );
    }

    #[test]
    fn malformed_check_id_fails_closed() {
        let err = resolve_crop_element_descriptor(&fixture_document(), &fixture_request(), "v1")
            .expect_err("malformed check id must fail");

        assert_eq!(
            err.diagnostic(),
            "descriptor must bind exactly one logical check id"
        );
    }

    #[test]
    fn rendered_request_fails_closed_in_internal_resolver() {
        let mut request = fixture_request();
        request.rendering = CropElementRendering::Rendered;
        request.source_pdf_fingerprint = Some(fixture_document().source.fingerprint);
        request.request_ref = crop_element_request_ref(&request).unwrap();

        let err = resolve_crop_element_descriptor(&fixture_document(), &request, "v0001")
            .expect_err("rendered request must remain blocked");

        assert_eq!(
            err.diagnostic(),
            "rendered crop_element requests remain blocked for internal descriptor resolver"
        );
    }
}
