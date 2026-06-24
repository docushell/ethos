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

//! # ethos-verify (Milestone A skeleton → B alpha → D v1)
//!
//! Parser-agnostic citation evidence verification. Consumes any parser's output through
//! [`ethos_core::grounding::GroundingSource`] — Ethos itself is just another grounding
//! source behind an adapter (PRD §1.5, §5.4).
//!
//! **Scope discipline:** verification is evidence grounding — the cited region exists,
//! its text matches by a declared literal method, the fingerprint is fresh. It is never
//! pixel-level, semantic, or arithmetic proof (PRD §14).
//!
//! The WS-VERIFY check engine intentionally supports only literal quote/value,
//! presence, and table-cell lookup claims. Unsupported claim kinds remain
//! explicit; no fuzzy, semantic, arithmetic, crop, OCR, layout, or
//! parser-internal behavior belongs here.

#![forbid(unsafe_code)]
#![warn(missing_docs)]

use std::collections::BTreeMap;

use ethos_core::codes::WarningCode;
use ethos_core::evidence_anchor::{
    AnchorChecks, AnchorLevel, AnchorStatus, BboxCheck, CoordinateProfile, EvidenceAnchor,
    EvidenceAnchorGrounding, EvidenceAnchorReport, EvidenceAnchorRequest, EvidenceKind,
    EvidenceRef, FingerprintCheck, PageCheck, TableCellCheck, TextCheck, TextNormalizationProfile,
    EVIDENCE_ANCHOR_REPORT_ARTIFACT_TYPE,
};
use ethos_core::grounding::{
    CoordinateOrigin, GroundingCell, GroundingElement, GroundingSource, GroundingSpan,
    GroundingTable, PageGeometry,
};
use ethos_core::verify_types::{
    compute_all_evidence_grounded, CapabilityLimit, Check, CheckReason, CheckStatus, Claim,
    ClaimKind, Evidence, GroundingMeta, MatchMethod, TextNormalization, VerificationConfig,
    VerificationReport,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

/// Citation input accepted by the alpha verifier.
///
/// The public CLI accepts either a bare array of [`Claim`] objects or this envelope
/// form. `document_fingerprint`, when present, is compared with the grounding
/// source fingerprint under the active staleness policy.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(untagged)]
pub enum CitationInput {
    /// Bare claim list.
    Claims(Vec<Claim>),
    /// Claim list with optional fingerprint anchor.
    Envelope(CitationEnvelope),
}

/// Envelope form of citation input.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CitationEnvelope {
    /// Fingerprint the citations were produced against.
    #[serde(default)]
    pub document_fingerprint: Option<String>,
    /// Claims to verify, in deterministic input order.
    pub claims: Vec<Claim>,
}

/// Validation or source-shape error for evidence anchoring.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EvidenceAnchorError {
    message: String,
}

impl EvidenceAnchorError {
    fn new(message: impl Into<String>) -> Self {
        EvidenceAnchorError {
            message: message.into(),
        }
    }
}

impl std::fmt::Display for EvidenceAnchorError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.message)
    }
}

impl std::error::Error for EvidenceAnchorError {}

/// Validate and resolve evidence refs over one grounding source.
pub fn anchor_evidence(
    source: &dyn GroundingSource,
    request: EvidenceAnchorRequest,
) -> Result<EvidenceAnchorReport, EvidenceAnchorError> {
    validate_anchor_request(&request)?;
    let index = SourceIndex::new(source);
    let fingerprint_check = fingerprint_check(request.source_fingerprint.as_deref(), source);
    let source_fingerprint = source.fingerprint();
    let grounding = EvidenceAnchorGrounding {
        parser: source.parser(),
        capabilities: source.capabilities(),
    };
    let anchors = request
        .evidence_refs
        .iter()
        .map(|evidence_ref| anchor_one(&index, fingerprint_check, evidence_ref))
        .collect();
    Ok(EvidenceAnchorReport {
        artifact_type: EVIDENCE_ANCHOR_REPORT_ARTIFACT_TYPE.to_string(),
        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
        source_fingerprint,
        grounding,
        anchors,
    })
}

fn validate_anchor_request(request: &EvidenceAnchorRequest) -> Result<(), EvidenceAnchorError> {
    if request.artifact_type != ethos_core::evidence_anchor::EVIDENCE_ANCHOR_REQUEST_ARTIFACT_TYPE {
        return Err(EvidenceAnchorError::new(
            "evidence anchor request artifact_type is not supported",
        ));
    }
    if request.schema_version != ethos_core::SCHEMA_VERSION {
        return Err(EvidenceAnchorError::new(
            "evidence anchor request schema_version is not supported",
        ));
    }
    let mut ids = std::collections::BTreeSet::new();
    for evidence_ref in &request.evidence_refs {
        if !ids.insert(evidence_ref.evidence_id.as_str()) {
            return Err(EvidenceAnchorError::new(format!(
                "duplicate evidence_id '{}'",
                evidence_ref.evidence_id
            )));
        }
        validate_evidence_ref(evidence_ref)?;
    }
    Ok(())
}

fn validate_evidence_ref(evidence_ref: &EvidenceRef) -> Result<(), EvidenceAnchorError> {
    if evidence_ref.locator.page_index == Some(0) {
        return Err(EvidenceAnchorError::new("page_index must be 1-based"));
    }
    if evidence_ref.locator.page_index.is_some() && evidence_ref.locator.page_id.is_some() {
        return Err(EvidenceAnchorError::new(
            "use exactly one of page_index or page_id",
        ));
    }
    if evidence_ref.locator.bbox.is_some()
        && evidence_ref.locator.coordinate_profile
            != Some(CoordinateProfile::EthosQuantizedTopLeftV1)
    {
        return Err(EvidenceAnchorError::new(
            "bbox requires coordinate_profile ethos_quantized_top_left_v1",
        ));
    }
    if evidence_ref.expected_text_sha256.is_some() {
        let Some(expected_text) = evidence_ref.expected_text.as_deref() else {
            return Err(EvidenceAnchorError::new(
                "expected_text_sha256 requires expected_text",
            ));
        };
        if evidence_ref.text_normalization_profile
            != Some(TextNormalizationProfile::EthosCollapseWhitespaceV1)
        {
            return Err(EvidenceAnchorError::new(
                "expected_text_sha256 requires text_normalization_profile ethos_collapse_whitespace_v1",
            ));
        }
        let expected_hash = format!(
            "sha256:{}",
            sha256_hex(normalize_expected_text(expected_text).as_bytes())
        );
        if evidence_ref.expected_text_sha256.as_deref() != Some(expected_hash.as_str()) {
            return Err(EvidenceAnchorError::new(
                "expected_text_sha256 does not match normalized expected_text",
            ));
        }
    }
    match evidence_ref.evidence_kind {
        EvidenceKind::Page if evidence_ref.required_anchor_level != AnchorLevel::Page => {
            return Err(EvidenceAnchorError::new(
                "page evidence supports only required_anchor_level page",
            ));
        }
        EvidenceKind::Text if evidence_ref.required_anchor_level != AnchorLevel::Text => {
            return Err(EvidenceAnchorError::new(
                "text evidence supports only required_anchor_level text",
            ));
        }
        EvidenceKind::TextRegion
            if !matches!(
                evidence_ref.required_anchor_level,
                AnchorLevel::Text | AnchorLevel::Bbox | AnchorLevel::TextBbox
            ) =>
        {
            return Err(EvidenceAnchorError::new(
                "text_region evidence supports only text, bbox, or text_bbox anchor levels",
            ));
        }
        EvidenceKind::TableCell if evidence_ref.required_anchor_level != AnchorLevel::TableCell => {
            return Err(EvidenceAnchorError::new(
                "table_cell evidence supports only required_anchor_level table_cell",
            ));
        }
        EvidenceKind::TableCell
            if evidence_ref.locator.table_id.is_none() || evidence_ref.locator.cell.is_none() =>
        {
            return Err(EvidenceAnchorError::new(
                "table_cell evidence requires table_id and cell",
            ));
        }
        EvidenceKind::Region | EvidenceKind::Other => {}
        _ => {}
    }
    if page_locator_required(evidence_ref)
        && evidence_ref.locator.page_index.is_none()
        && evidence_ref.locator.page_id.is_none()
    {
        return Err(EvidenceAnchorError::new(
            "page_index or page_id is required for this evidence ref",
        ));
    }
    Ok(())
}

fn page_locator_required(evidence_ref: &EvidenceRef) -> bool {
    matches!(evidence_ref.evidence_kind, EvidenceKind::Page)
        || evidence_ref.locator.bbox.is_some()
        || (evidence_ref.locator.element_id.is_none()
            && evidence_ref.locator.span_id.is_none()
            && evidence_ref.locator.table_id.is_none())
}

fn fingerprint_check(
    request_fingerprint: Option<&str>,
    source: &dyn GroundingSource,
) -> FingerprintCheck {
    match (request_fingerprint, source.fingerprint()) {
        (None, _) => FingerprintCheck::NotChecked,
        (Some(_), None) => FingerprintCheck::CapabilityLimited,
        (Some(expected), Some(actual)) if expected == actual => FingerprintCheck::Matched,
        (Some(_), Some(_)) => FingerprintCheck::Stale,
    }
}

fn anchor_one(
    index: &SourceIndex,
    fingerprint: FingerprintCheck,
    evidence_ref: &EvidenceRef,
) -> EvidenceAnchor {
    let mut checks = AnchorChecks {
        fingerprint,
        ..AnchorChecks::default()
    };
    let mut capability_limits = Vec::new();

    if matches!(
        evidence_ref.evidence_kind,
        EvidenceKind::Region | EvidenceKind::Other
    ) {
        return anchor_result(
            evidence_ref,
            AnchorStatus::UnsupportedEvidenceKind,
            AnchorLevel::None,
            checks,
            capability_limits,
        );
    }
    if fingerprint == FingerprintCheck::Stale {
        return anchor_result(
            evidence_ref,
            AnchorStatus::StaleFingerprint,
            AnchorLevel::None,
            checks,
            capability_limits,
        );
    }
    if fingerprint == FingerprintCheck::CapabilityLimited {
        capability_limits.push(CapabilityLimit::MissingFingerprint);
    }

    let page = resolve_page(index, evidence_ref);
    checks.page = page.check;
    let mut achieved_page = page.check == PageCheck::Found;
    let mut text_ok = false;
    let mut bbox_ok = false;
    let mut table_ok = false;

    match evidence_ref.evidence_kind {
        EvidenceKind::Page => {}
        EvidenceKind::Text | EvidenceKind::TextRegion => {
            if anchor_requires_text(evidence_ref) {
                let text = resolve_text(index, evidence_ref, page.page_id.as_deref());
                checks.text = text.check;
                text_ok = text.check == TextCheck::Matched;
                if text.check == TextCheck::CapabilityLimited {
                    capability_limits.push(CapabilityLimit::MissingSpans);
                }
            }
            if requires_bbox(evidence_ref) {
                let bbox = resolve_bbox(index, evidence_ref, page.page_id.as_deref());
                checks.bbox = bbox;
                bbox_ok = bbox == BboxCheck::Valid;
                if bbox == BboxCheck::CapabilityLimited {
                    capability_limits.push(CapabilityLimit::UnknownCoordinateOrigin);
                }
            }
        }
        EvidenceKind::TableCell => {
            let table = resolve_anchor_table_cell(index, evidence_ref);
            checks.table_cell = table.check;
            table_ok = table.check == TableCellCheck::Matched;
            achieved_page = table.page_found;
            if table.check == TableCellCheck::CapabilityLimited {
                capability_limits.push(CapabilityLimit::MissingTables);
            }
        }
        EvidenceKind::Region | EvidenceKind::Other => {}
    }

    capability_limits.sort_by_key(|limit| format!("{limit:?}"));
    capability_limits.dedup();
    let achieved_anchor_level =
        achieved_anchor_level(evidence_ref, achieved_page, text_ok, bbox_ok, table_ok);
    let anchor_status = anchor_status(evidence_ref, &checks, &capability_limits);
    anchor_result(
        evidence_ref,
        anchor_status,
        achieved_anchor_level,
        checks,
        capability_limits,
    )
}

fn anchor_result(
    evidence_ref: &EvidenceRef,
    anchor_status: AnchorStatus,
    achieved_anchor_level: AnchorLevel,
    checks: AnchorChecks,
    capability_limits: Vec<CapabilityLimit>,
) -> EvidenceAnchor {
    EvidenceAnchor {
        evidence_id: evidence_ref.evidence_id.clone(),
        evidence_kind: evidence_ref.evidence_kind,
        anchor_status,
        required_anchor_level: evidence_ref.required_anchor_level,
        achieved_anchor_level,
        checks,
        capability_limits,
    }
}

struct PageResolution {
    check: PageCheck,
    page_id: Option<String>,
}

fn resolve_page(index: &SourceIndex, evidence_ref: &EvidenceRef) -> PageResolution {
    if let Some(page_id) = evidence_ref.locator.page_id.as_deref() {
        return if index.pages.iter().any(|page| page.id == page_id) {
            PageResolution {
                check: PageCheck::Found,
                page_id: Some(page_id.to_string()),
            }
        } else {
            PageResolution {
                check: PageCheck::NotFound,
                page_id: None,
            }
        };
    }
    if let Some(page_index) = evidence_ref.locator.page_index {
        return index
            .pages
            .iter()
            .find(|page| page.index == page_index)
            .map(|page| PageResolution {
                check: PageCheck::Found,
                page_id: Some(page.id.clone()),
            })
            .unwrap_or(PageResolution {
                check: PageCheck::NotFound,
                page_id: None,
            });
    }
    PageResolution {
        check: PageCheck::NotChecked,
        page_id: None,
    }
}

struct TextResolution {
    check: TextCheck,
}

fn resolve_text(
    index: &SourceIndex,
    evidence_ref: &EvidenceRef,
    page_id: Option<&str>,
) -> TextResolution {
    let Some(expected_text) = evidence_ref.expected_text.as_deref() else {
        return TextResolution {
            check: TextCheck::NotFound,
        };
    };
    if let Some(span_id) = evidence_ref.locator.span_id.as_deref() {
        if !index.capabilities.spans {
            return TextResolution {
                check: TextCheck::CapabilityLimited,
            };
        }
        return match index.span(span_id) {
            Some(span) => TextResolution {
                check: text_check(expected_text, &span.text),
            },
            None => TextResolution {
                check: TextCheck::NotFound,
            },
        };
    }
    if let Some(element_id) = evidence_ref.locator.element_id.as_deref() {
        return index
            .element_by_id
            .get(element_id)
            .and_then(|position| index.elements.get(*position))
            .and_then(|element| element.text.as_deref())
            .map(|actual| TextResolution {
                check: text_check(expected_text, actual),
            })
            .unwrap_or(TextResolution {
                check: TextCheck::NotFound,
            });
    }
    let Some(page_id) = page_id else {
        return TextResolution {
            check: TextCheck::NotFound,
        };
    };
    if index
        .elements
        .iter()
        .filter(|element| element.page == page_id)
        .filter_map(|element| element.text.as_deref())
        .any(|actual| text_check(expected_text, actual) == TextCheck::Matched)
    {
        return TextResolution {
            check: TextCheck::Matched,
        };
    }
    if index
        .spans
        .iter()
        .filter(|span| span.page == page_id)
        .any(|span| text_check(expected_text, &span.text) == TextCheck::Matched)
    {
        return TextResolution {
            check: TextCheck::Matched,
        };
    }
    TextResolution {
        check: if index.elements.iter().any(|element| element.page == page_id)
            || index.spans.iter().any(|span| span.page == page_id)
        {
            TextCheck::Mismatch
        } else {
            TextCheck::NotFound
        },
    }
}

fn resolve_bbox(
    index: &SourceIndex,
    evidence_ref: &EvidenceRef,
    page_id: Option<&str>,
) -> BboxCheck {
    let Some(bbox) = evidence_ref.locator.bbox else {
        return BboxCheck::NotChecked;
    };
    if index.capabilities.coordinate_origin != CoordinateOrigin::TopLeft {
        return BboxCheck::CapabilityLimited;
    }
    let Some(page_id) = page_id else {
        return BboxCheck::NotFound;
    };
    let tolerance = VerificationConfig::default_v1()
        .matching
        .bbox_containment_tolerance_q
        .unwrap_or(0);
    if index
        .elements
        .iter()
        .any(|element| element.page == page_id && contains_bbox(element.bbox, bbox, tolerance))
        || index
            .spans
            .iter()
            .any(|span| span.page == page_id && contains_bbox(span.bbox, bbox, tolerance))
        || index
            .tables
            .iter()
            .any(|table| table.page == page_id && contains_bbox(table.bbox, bbox, tolerance))
    {
        BboxCheck::Valid
    } else {
        BboxCheck::NotFound
    }
}

struct TableResolution {
    check: TableCellCheck,
    page_found: bool,
}

fn resolve_anchor_table_cell(index: &SourceIndex, evidence_ref: &EvidenceRef) -> TableResolution {
    if !index.capabilities.tables {
        return TableResolution {
            check: TableCellCheck::CapabilityLimited,
            page_found: false,
        };
    }
    let Some(table_id) = evidence_ref.locator.table_id.as_deref() else {
        return TableResolution {
            check: TableCellCheck::NotFound,
            page_found: false,
        };
    };
    let Some(cell_ref) = evidence_ref.locator.cell else {
        return TableResolution {
            check: TableCellCheck::NotFound,
            page_found: false,
        };
    };
    let Some(table) = index.table(table_id) else {
        return TableResolution {
            check: TableCellCheck::NotFound,
            page_found: false,
        };
    };
    let page_found = index.pages.iter().any(|page| page.id == table.page);
    let Some(cell) = table
        .cells
        .iter()
        .find(|cell| table_cell_covers(cell, cell_ref.row, cell_ref.col))
    else {
        return TableResolution {
            check: TableCellCheck::NotFound,
            page_found,
        };
    };
    let check = match evidence_ref.expected_text.as_deref() {
        Some(expected) => {
            if text_check(expected, &cell.text) == TextCheck::Matched {
                TableCellCheck::Matched
            } else {
                TableCellCheck::Mismatch
            }
        }
        None => TableCellCheck::Matched,
    };
    TableResolution { check, page_found }
}

fn anchor_requires_text(evidence_ref: &EvidenceRef) -> bool {
    matches!(
        evidence_ref.required_anchor_level,
        AnchorLevel::Text | AnchorLevel::TextBbox
    )
}

fn requires_bbox(evidence_ref: &EvidenceRef) -> bool {
    matches!(
        evidence_ref.required_anchor_level,
        AnchorLevel::Bbox | AnchorLevel::TextBbox
    )
}

fn text_check(expected: &str, actual: &str) -> TextCheck {
    if normalize_expected_text(actual).contains(&normalize_expected_text(expected)) {
        TextCheck::Matched
    } else {
        TextCheck::Mismatch
    }
}

fn normalize_expected_text(input: &str) -> String {
    normalize_quote(input)
}

fn sha256_hex(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    format!("{:x}", hasher.finalize())
}

fn achieved_anchor_level(
    evidence_ref: &EvidenceRef,
    page_ok: bool,
    text_ok: bool,
    bbox_ok: bool,
    table_ok: bool,
) -> AnchorLevel {
    match evidence_ref.evidence_kind {
        EvidenceKind::Page if page_ok => AnchorLevel::Page,
        EvidenceKind::Text if text_ok => AnchorLevel::Text,
        EvidenceKind::TextRegion if text_ok && bbox_ok => AnchorLevel::TextBbox,
        EvidenceKind::TextRegion if text_ok => AnchorLevel::Text,
        EvidenceKind::TextRegion if bbox_ok => AnchorLevel::Bbox,
        EvidenceKind::TableCell if table_ok => AnchorLevel::TableCell,
        _ => AnchorLevel::None,
    }
}

fn anchor_status(
    evidence_ref: &EvidenceRef,
    checks: &AnchorChecks,
    capability_limits: &[CapabilityLimit],
) -> AnchorStatus {
    if checks.page == PageCheck::NotFound
        || checks.text == TextCheck::NotFound
        || checks.bbox == BboxCheck::NotFound
        || checks.table_cell == TableCellCheck::NotFound
    {
        return AnchorStatus::NotFound;
    }
    if checks.text == TextCheck::Mismatch
        || checks.bbox == BboxCheck::Invalid
        || checks.table_cell == TableCellCheck::Mismatch
    {
        return AnchorStatus::Mismatch;
    }
    if checks.fingerprint == FingerprintCheck::CapabilityLimited
        || checks.text == TextCheck::CapabilityLimited
        || checks.bbox == BboxCheck::CapabilityLimited
        || checks.table_cell == TableCellCheck::CapabilityLimited
        || !capability_limits.is_empty()
    {
        return AnchorStatus::CapabilityLimited;
    }
    let bound = match evidence_ref.required_anchor_level {
        AnchorLevel::Page => checks.page == PageCheck::Found,
        AnchorLevel::Text => checks.text == TextCheck::Matched,
        AnchorLevel::Bbox => checks.bbox == BboxCheck::Valid,
        AnchorLevel::TextBbox => {
            checks.text == TextCheck::Matched && checks.bbox == BboxCheck::Valid
        }
        AnchorLevel::TableCell => checks.table_cell == TableCellCheck::Matched,
        AnchorLevel::None => false,
    };
    if bound {
        AnchorStatus::Bound
    } else {
        AnchorStatus::NotFound
    }
}

impl CitationInput {
    /// Claims in deterministic input order.
    pub fn claims(&self) -> &[Claim] {
        match self {
            CitationInput::Claims(claims) => claims,
            CitationInput::Envelope(envelope) => &envelope.claims,
        }
    }

    /// Fingerprint anchor declared by the citation envelope, when present.
    pub fn document_fingerprint(&self) -> Option<&str> {
        match self {
            CitationInput::Claims(_) => None,
            CitationInput::Envelope(envelope) => envelope.document_fingerprint.as_deref(),
        }
    }

    fn into_parts(self) -> (Option<String>, Vec<Claim>) {
        match self {
            CitationInput::Claims(claims) => (None, claims),
            CitationInput::Envelope(envelope) => (envelope.document_fingerprint, envelope.claims),
        }
    }
}

/// Compute the capability-downgrade warnings for a source under a config (PRD §5.5):
/// every missing capability the run would rely on surfaces as `capability_limited` —
/// explicitly, never as silent approximation.
pub fn capability_warnings(
    source: &dyn GroundingSource,
    config: &VerificationConfig,
) -> Vec<WarningCode> {
    if capability_limits(source, config).is_empty() {
        Vec::new()
    } else {
        vec![WarningCode::CapabilityLimited]
    }
}

/// Compute structured capability gaps for the run. These explain the stable
/// `capability_limited` warning without minting parser-warning codes for every
/// verification capability.
pub fn capability_limits(
    source: &dyn GroundingSource,
    config: &VerificationConfig,
) -> Vec<CapabilityLimit> {
    capability_limits_for(source.capabilities(), config)
}

fn capability_limits_for(
    caps: ethos_core::grounding::Capabilities,
    config: &VerificationConfig,
) -> Vec<CapabilityLimit> {
    let mut limits = Vec::new();
    if !caps.fingerprint && config.staleness.require_fingerprint_match {
        limits.push(CapabilityLimit::MissingFingerprint);
    }
    if !caps.spans {
        limits.push(CapabilityLimit::MissingSpans);
    }
    if !caps.char_offsets {
        limits.push(CapabilityLimit::MissingCharOffsets);
    }
    if !caps.tables && config.claim_kinds.contains(&ClaimKind::TableCell) {
        limits.push(CapabilityLimit::MissingTables);
    }
    if caps.coordinate_origin == CoordinateOrigin::Unknown {
        limits.push(CapabilityLimit::UnknownCoordinateOrigin);
    }
    if config.evidence.is_some_and(|e| e.include_crops) && !caps.crop_support {
        limits.push(CapabilityLimit::MissingCropSupport);
    }
    limits
}

fn push_warning(warnings: &mut Vec<WarningCode>, warning: WarningCode) {
    if !warnings.contains(&warning) {
        warnings.push(warning);
    }
}

/// Verify citation claims over a parser-agnostic [`GroundingSource`].
pub fn verify_claims(
    source: &dyn GroundingSource,
    citations: CitationInput,
    config: &VerificationConfig,
    config_sha256: String,
) -> VerificationReport {
    let (citation_fingerprint, claims) = citations.into_parts();
    let index = SourceIndex::new(source);
    let source_fingerprint = source.fingerprint();
    let capability_limits = capability_limits_for(index.capabilities, config);
    let warnings = if capability_limits.is_empty() {
        Vec::new()
    } else {
        vec![WarningCode::CapabilityLimited]
    };
    let fingerprint_stale = config.staleness.require_fingerprint_match
        && matches!(
            (citation_fingerprint.as_deref(), source_fingerprint.as_deref()),
            (Some(expected), Some(actual)) if expected != actual
        );
    let fingerprint_unverifiable = config.staleness.require_fingerprint_match
        && citation_fingerprint.is_some()
        && source_fingerprint.is_none();
    let citation_fingerprint_missing = config.staleness.require_fingerprint_match
        && citation_fingerprint.is_none()
        && source_fingerprint.is_some();
    let include_text = config.evidence.is_some_and(|e| e.include_text);
    let include_crops = config.evidence.is_some_and(|e| e.include_crops);
    let mut unsupported = Vec::new();
    let checks: Vec<Check> = claims
        .into_iter()
        .enumerate()
        .map(|(idx, claim)| {
            check_claim(
                idx + 1,
                source,
                &index,
                claim,
                config,
                CheckContext {
                    fingerprint_stale,
                    fingerprint_unverifiable,
                    citation_fingerprint_missing,
                    include_text,
                    include_crops,
                },
                &mut unsupported,
            )
        })
        .collect();

    VerificationReport {
        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
        document_fingerprint: source_fingerprint,
        verification_config_sha256: config_sha256,
        grounding: GroundingMeta {
            parser: source.parser(),
            capabilities: index.capabilities,
        },
        capability_limits,
        fingerprint_stale,
        all_evidence_grounded: compute_all_evidence_grounded(
            &checks,
            &unsupported,
            fingerprint_stale,
        ),
        checks,
        unsupported_claim_kinds: unsupported,
        warnings,
    }
}

#[derive(Debug, Clone, Copy)]
struct CheckContext {
    fingerprint_stale: bool,
    fingerprint_unverifiable: bool,
    citation_fingerprint_missing: bool,
    include_text: bool,
    include_crops: bool,
}

fn check_claim(
    id: usize,
    source: &dyn GroundingSource,
    index: &SourceIndex,
    claim: Claim,
    config: &VerificationConfig,
    context: CheckContext,
    unsupported: &mut Vec<String>,
) -> Check {
    let mut warnings = Vec::new();
    let check_id = format!("v{id:04}");

    if !claim.citation.has_locator() {
        return Check {
            id: check_id,
            claim,
            status: CheckStatus::Error,
            reason: Some(CheckReason::MissingLocator),
            match_method: MatchMethod::None,
            semantic_unverified: false,
            evidence: None,
            warnings,
        };
    }

    if !is_supported_kind(claim.kind) || !config.claim_kinds.contains(&claim.kind) {
        push_unsupported(unsupported, claim.kind);
        return Check {
            id: check_id,
            claim,
            status: CheckStatus::UnsupportedClaimKind,
            reason: Some(CheckReason::UnsupportedClaimKind),
            match_method: MatchMethod::None,
            semantic_unverified: false,
            evidence: None,
            warnings,
        };
    }

    if requires_text(claim.kind)
        && claim
            .text
            .as_deref()
            .is_none_or(|text| text.trim().is_empty())
    {
        return Check {
            id: check_id,
            claim,
            status: CheckStatus::Error,
            reason: Some(CheckReason::MissingRequiredText),
            match_method: MatchMethod::None,
            semantic_unverified: false,
            evidence: None,
            warnings,
        };
    }

    if context.fingerprint_stale {
        return Check {
            id: check_id,
            claim,
            status: CheckStatus::Stale,
            reason: Some(CheckReason::StaleFingerprint),
            match_method: MatchMethod::None,
            semantic_unverified: false,
            evidence: None,
            warnings,
        };
    }

    if context.fingerprint_unverifiable {
        push_warning(&mut warnings, WarningCode::CapabilityLimited);
        return Check {
            id: check_id,
            claim,
            status: CheckStatus::CapabilityBlocked,
            reason: Some(CheckReason::MissingSourceFingerprint),
            match_method: MatchMethod::None,
            semantic_unverified: false,
            evidence: None,
            warnings,
        };
    }

    if context.citation_fingerprint_missing {
        return Check {
            id: check_id,
            claim,
            status: CheckStatus::Stale,
            reason: Some(CheckReason::MissingCitationFingerprint),
            match_method: MatchMethod::None,
            semantic_unverified: false,
            evidence: None,
            warnings,
        };
    }

    let mut target = match resolve_target(index, &claim, config) {
        TargetResolution::Found(target) => target,
        TargetResolution::NotFound(reason) => {
            return Check {
                id: check_id,
                claim,
                status: CheckStatus::NotFound,
                reason: Some(reason),
                match_method: MatchMethod::None,
                semantic_unverified: false,
                evidence: None,
                warnings,
            };
        }
        TargetResolution::Invalid(reason) => {
            return Check {
                id: check_id,
                claim,
                status: CheckStatus::Error,
                reason: Some(reason),
                match_method: MatchMethod::None,
                semantic_unverified: false,
                evidence: None,
                warnings,
            };
        }
        TargetResolution::CapabilityBlocked(reason) => {
            push_warning(&mut warnings, WarningCode::CapabilityLimited);
            return Check {
                id: check_id,
                claim,
                status: CheckStatus::CapabilityBlocked,
                reason: Some(reason),
                match_method: MatchMethod::None,
                semantic_unverified: false,
                evidence: None,
                warnings,
            };
        }
    };

    if let Some(adjacent_target) = adjacent_quote_target(index, &claim, &target, config) {
        target = adjacent_target;
    }

    let evidence = make_evidence(source, &target, context.include_text, context.include_crops);
    let (status, match_method, reason) =
        check_resolved_claim(claim.kind, claim.text.as_deref(), &target, config);
    Check {
        id: check_id,
        claim,
        status,
        reason,
        match_method,
        semantic_unverified: false,
        evidence,
        warnings,
    }
}

fn check_resolved_claim(
    kind: ClaimKind,
    expected_text: Option<&str>,
    target: &FoundTarget,
    config: &VerificationConfig,
) -> (CheckStatus, MatchMethod, Option<CheckReason>) {
    match kind {
        ClaimKind::Presence => check_presence_claim(),
        ClaimKind::Quote | ClaimKind::Value | ClaimKind::TableCell => {
            check_text_claim(kind, expected_text, target, config)
        }
        _ => unreachable!("unsupported kinds returned before matching"),
    }
}

fn check_presence_claim() -> (CheckStatus, MatchMethod, Option<CheckReason>) {
    (CheckStatus::Grounded, MatchMethod::PresenceOnly, None)
}

fn check_text_claim(
    kind: ClaimKind,
    expected_text: Option<&str>,
    target: &FoundTarget,
    config: &VerificationConfig,
) -> (CheckStatus, MatchMethod, Option<CheckReason>) {
    let match_method = if target.from_table_cell {
        MatchMethod::TableCellLookup
    } else {
        text_match_method(kind, config)
    };
    let (status, reason) = match (expected_text, target.text.as_deref()) {
        (Some(expected), Some(actual)) if text_matches(kind, expected, actual, config) => {
            (CheckStatus::Grounded, None)
        }
        _ => (CheckStatus::Mismatch, Some(CheckReason::TextMismatch)),
    };
    (status, match_method, reason)
}

fn is_supported_kind(kind: ClaimKind) -> bool {
    matches!(
        kind,
        ClaimKind::Quote | ClaimKind::Value | ClaimKind::Presence | ClaimKind::TableCell
    )
}

fn requires_text(kind: ClaimKind) -> bool {
    matches!(
        kind,
        ClaimKind::Quote | ClaimKind::Value | ClaimKind::TableCell
    )
}

fn push_unsupported(unsupported: &mut Vec<String>, kind: ClaimKind) {
    let name = claim_kind_name(kind).to_string();
    if !unsupported.contains(&name) {
        unsupported.push(name);
    }
}

fn claim_kind_name(kind: ClaimKind) -> &'static str {
    match kind {
        ClaimKind::Quote => "quote",
        ClaimKind::Value => "value",
        ClaimKind::Presence => "presence",
        ClaimKind::TableCell => "table_cell",
        ClaimKind::Region => "region",
        ClaimKind::Other => "other",
    }
}

#[derive(Debug, Clone)]
struct FoundTarget {
    page: Option<String>,
    bbox: Option<[i64; 4]>,
    text: Option<String>,
    from_table_cell: bool,
    element_index: Option<usize>,
}

/// Per-run grounding snapshot used to avoid cloning full entity collections per claim.
///
/// The lookup maps intentionally preserve first-match-by-id behavior, matching the trait default
/// and current native/ODL adapters. If an adapter gives `element_by_id` different semantics, update
/// this index at the same time so verifier resolution does not silently diverge.
struct SourceIndex {
    capabilities: ethos_core::grounding::Capabilities,
    pages: Vec<PageGeometry>,
    elements: Vec<GroundingElement>,
    spans: Vec<GroundingSpan>,
    tables: Vec<GroundingTable>,
    element_by_id: BTreeMap<String, usize>,
    span_by_id: BTreeMap<String, usize>,
    table_by_id: BTreeMap<String, usize>,
}

impl SourceIndex {
    fn new(source: &dyn GroundingSource) -> Self {
        let capabilities = source.capabilities();
        let pages = source.pages();
        let elements = source.elements();
        let spans = if capabilities.spans {
            source.spans()
        } else {
            Vec::new()
        };
        let tables = if capabilities.tables {
            source.tables()
        } else {
            Vec::new()
        };
        let element_by_id = index_elements(&elements);
        let span_by_id = index_spans(&spans);
        let table_by_id = index_tables(&tables);

        SourceIndex {
            capabilities,
            pages,
            elements,
            spans,
            tables,
            element_by_id,
            span_by_id,
            table_by_id,
        }
    }

    fn span(&self, id: &str) -> Option<&GroundingSpan> {
        self.span_by_id
            .get(id)
            .and_then(|index| self.spans.get(*index))
    }

    fn table(&self, id: &str) -> Option<&GroundingTable> {
        self.table_by_id
            .get(id)
            .and_then(|index| self.tables.get(*index))
    }
}

fn index_elements(elements: &[GroundingElement]) -> BTreeMap<String, usize> {
    let mut index = BTreeMap::new();
    for (position, element) in elements.iter().enumerate() {
        index.entry(element.id.clone()).or_insert(position);
    }
    index
}

fn index_spans(spans: &[GroundingSpan]) -> BTreeMap<String, usize> {
    let mut index = BTreeMap::new();
    for (position, span) in spans.iter().enumerate() {
        index.entry(span.id.clone()).or_insert(position);
    }
    index
}

fn index_tables(tables: &[GroundingTable]) -> BTreeMap<String, usize> {
    let mut index = BTreeMap::new();
    for (position, table) in tables.iter().enumerate() {
        index.entry(table.id.clone()).or_insert(position);
    }
    index
}

enum TargetResolution {
    Found(FoundTarget),
    NotFound(CheckReason),
    Invalid(CheckReason),
    CapabilityBlocked(CheckReason),
}

fn resolve_target(
    index: &SourceIndex,
    claim: &Claim,
    config: &VerificationConfig,
) -> TargetResolution {
    if claim.kind == ClaimKind::TableCell
        || claim.citation.table_id.is_some()
        || claim.citation.cell.is_some()
    {
        return resolve_table_cell(index, claim);
    }

    if let Some(span_id) = claim.citation.span_id.as_deref() {
        if !index.capabilities.spans {
            return TargetResolution::CapabilityBlocked(CheckReason::MissingSpanCapability);
        }
        return index
            .span(span_id)
            .map(target_from_span)
            .map(TargetResolution::Found)
            .unwrap_or(TargetResolution::NotFound(CheckReason::SpanNotFound));
    }

    if let Some(element_id) = claim.citation.element_id.as_deref() {
        return index
            .element_by_id
            .get(element_id)
            .and_then(|position| {
                index
                    .elements
                    .get(*position)
                    .map(|element| (*position, element))
            })
            .map(|(position, element)| target_from_element(element, Some(position)))
            .map(TargetResolution::Found)
            .unwrap_or(TargetResolution::NotFound(CheckReason::ElementNotFound));
    }

    if let (Some(page), Some(bbox)) = (claim.citation.page.as_deref(), claim.citation.bbox) {
        if index.capabilities.coordinate_origin == CoordinateOrigin::Unknown {
            return TargetResolution::CapabilityBlocked(CheckReason::UnknownCoordinateOrigin);
        }
        let tolerance = config.matching.bbox_containment_tolerance_q.unwrap_or(0);
        return index
            .elements
            .iter()
            .enumerate()
            .filter(|(_, element)| {
                element.page == page && contains_bbox(element.bbox, bbox, tolerance)
            })
            .min_by_key(|(position, element)| (bbox_area(element.bbox), *position))
            .map(|(position, element)| target_from_element(element, Some(position)))
            .map(TargetResolution::Found)
            .unwrap_or(TargetResolution::NotFound(CheckReason::BboxNotFound));
    }

    if claim.citation.bbox.is_some() {
        return TargetResolution::Invalid(CheckReason::MissingPageForBbox);
    }

    if let Some(page) = claim.citation.page.as_deref() {
        return index
            .pages
            .iter()
            .find(|candidate| candidate.id == page)
            .map(|found| {
                TargetResolution::Found(FoundTarget {
                    page: Some(found.id.clone()),
                    bbox: Some([0, 0, found.width, found.height]),
                    text: None,
                    from_table_cell: false,
                    element_index: None,
                })
            })
            .unwrap_or(TargetResolution::NotFound(CheckReason::PageNotFound));
    }

    TargetResolution::NotFound(CheckReason::MissingLocator)
}

fn target_from_element(element: &GroundingElement, element_index: Option<usize>) -> FoundTarget {
    FoundTarget {
        page: Some(element.page.clone()),
        bbox: Some(element.bbox),
        text: element.text.clone(),
        from_table_cell: false,
        element_index,
    }
}

fn target_from_span(span: &GroundingSpan) -> FoundTarget {
    FoundTarget {
        page: Some(span.page.clone()),
        bbox: Some(span.bbox),
        text: Some(span.text.clone()),
        from_table_cell: false,
        element_index: None,
    }
}

fn resolve_table_cell(index: &SourceIndex, claim: &Claim) -> TargetResolution {
    let Some(table_id) = claim.citation.table_id.as_deref() else {
        return TargetResolution::Invalid(CheckReason::MissingTableCellLocator);
    };
    let Some(cell_ref) = claim.citation.cell else {
        return TargetResolution::Invalid(CheckReason::MissingTableCellLocator);
    };
    if !index.capabilities.tables {
        return TargetResolution::CapabilityBlocked(CheckReason::MissingTableCapability);
    }
    let Some(table) = index.table(table_id) else {
        return TargetResolution::NotFound(CheckReason::TableNotFound);
    };
    target_from_table_cell(table, cell_ref.row, cell_ref.col)
        .map(TargetResolution::Found)
        .unwrap_or(TargetResolution::NotFound(CheckReason::TableCellNotFound))
}

fn target_from_table_cell(table: &GroundingTable, row: u32, col: u32) -> Option<FoundTarget> {
    table
        .cells
        .iter()
        .find(|cell| table_cell_covers(cell, row, col))
        .map(|cell| target_from_cell(&table.page, cell))
}

fn table_cell_covers(cell: &GroundingCell, row: u32, col: u32) -> bool {
    let row_end = cell.row.saturating_add(cell.row_span.max(1));
    let col_end = cell.col.saturating_add(cell.col_span.max(1));
    row >= cell.row && row < row_end && col >= cell.col && col < col_end
}

fn target_from_cell(page: &str, cell: &GroundingCell) -> FoundTarget {
    FoundTarget {
        page: Some(page.to_string()),
        bbox: Some(cell.bbox),
        text: Some(cell.text.clone()),
        from_table_cell: true,
        element_index: None,
    }
}

fn adjacent_quote_target(
    index: &SourceIndex,
    claim: &Claim,
    target: &FoundTarget,
    config: &VerificationConfig,
) -> Option<FoundTarget> {
    if claim.kind != ClaimKind::Quote {
        return None;
    }
    let expected = claim.text.as_deref()?;
    if target
        .text
        .as_deref()
        .is_some_and(|actual| text_matches(ClaimKind::Quote, expected, actual, config))
    {
        return None;
    }

    if claim.citation.bbox.is_some() {
        return None;
    }

    if claim.citation.element_id.is_some() {
        if let Some(position) = target.element_index {
            return adjacent_text_pair_for_element(index, position, expected, config);
        }
    }

    None
}

fn adjacent_text_pair_for_element(
    index: &SourceIndex,
    position: usize,
    expected: &str,
    config: &VerificationConfig,
) -> Option<FoundTarget> {
    let current = index.elements.get(position)?;
    if let Some(second) = position
        .checked_add(1)
        .and_then(|next| index.elements.get(next))
    {
        if let Some(target) = adjacent_text_pair_target(current, second, expected, config) {
            return Some(target);
        }
    }
    position
        .checked_sub(1)
        .and_then(|previous| index.elements.get(previous))
        .and_then(|first| adjacent_text_pair_target(first, current, expected, config))
}

fn adjacent_text_pair_target(
    first: &GroundingElement,
    second: &GroundingElement,
    expected: &str,
    config: &VerificationConfig,
) -> Option<FoundTarget> {
    if first.page != second.page {
        return None;
    }
    if !element_bboxes_are_adjacent(first.bbox, second.bbox) {
        return None;
    }
    let first_text = first.text.as_deref()?;
    let second_text = second.text.as_deref()?;
    let joined = join_adjacent_text(first_text, second_text, config);
    if text_matches(ClaimKind::Quote, expected, first_text, config)
        || text_matches(ClaimKind::Quote, expected, second_text, config)
        || !text_matches(ClaimKind::Quote, expected, &joined, config)
    {
        return None;
    }

    Some(FoundTarget {
        page: Some(first.page.clone()),
        bbox: Some(union_bbox(first.bbox, second.bbox)),
        text: Some(joined),
        from_table_cell: false,
        element_index: None,
    })
}

fn join_adjacent_text(first: &str, second: &str, config: &VerificationConfig) -> String {
    let joined = format!("{first} {second}");
    match config.matching.text_normalization {
        TextNormalization::None => joined,
        TextNormalization::CollapseWhitespace => normalize_quote(&joined),
    }
}

fn bbox_area(bbox: [i64; 4]) -> u128 {
    let width = bbox[2].saturating_sub(bbox[0]).max(0) as u128;
    let height = bbox[3].saturating_sub(bbox[1]).max(0) as u128;
    width.saturating_mul(height)
}

fn element_bboxes_are_adjacent(first: [i64; 4], second: [i64; 4]) -> bool {
    let same_line =
        ranges_overlap_i64(first[1], first[3], second[1], second[3]) && first[2] == second[0];
    let stacked =
        ranges_overlap_i64(first[0], first[2], second[0], second[2]) && first[3] == second[1];
    same_line || stacked
}

fn ranges_overlap_i64(a_start: i64, a_end: i64, b_start: i64, b_end: i64) -> bool {
    a_start < b_end && b_start < a_end
}

fn union_bbox(left: [i64; 4], right: [i64; 4]) -> [i64; 4] {
    [
        left[0].min(right[0]),
        left[1].min(right[1]),
        left[2].max(right[2]),
        left[3].max(right[3]),
    ]
}

fn make_evidence(
    source: &dyn GroundingSource,
    target: &FoundTarget,
    include_text: bool,
    include_crops: bool,
) -> Option<Evidence> {
    let crop_ref = if include_crops && source.capabilities().crop_support {
        target
            .page
            .as_deref()
            .zip(target.bbox)
            .and_then(|(page, bbox)| source.crop_ref(page, bbox))
    } else {
        None
    };
    Some(Evidence {
        text: include_text.then(|| target.text.clone()).flatten(),
        page: target.page.clone(),
        bbox: target.bbox,
        crop_ref,
    })
}

fn contains_bbox(container: [i64; 4], inner: [i64; 4], tolerance: i64) -> bool {
    inner[0] >= container[0] - tolerance
        && inner[1] >= container[1] - tolerance
        && inner[2] <= container[2] + tolerance
        && inner[3] <= container[3] + tolerance
}

fn text_match_method(kind: ClaimKind, config: &VerificationConfig) -> MatchMethod {
    match (kind, config.matching.text_normalization) {
        (ClaimKind::Quote, TextNormalization::None) => MatchMethod::ExactTextContains,
        (ClaimKind::Quote, TextNormalization::CollapseWhitespace) => {
            MatchMethod::NormalizedTextContains
        }
        (_, TextNormalization::None) => MatchMethod::ExactText,
        (_, TextNormalization::CollapseWhitespace) => MatchMethod::NormalizedText,
    }
}

fn text_matches(
    kind: ClaimKind,
    expected: &str,
    actual: &str,
    config: &VerificationConfig,
) -> bool {
    let (mut expected, mut actual) = match config.matching.text_normalization {
        TextNormalization::None => (expected.to_string(), actual.to_string()),
        TextNormalization::CollapseWhitespace => {
            (normalize_quote(expected), normalize_quote(actual))
        }
    };
    if !config.matching.case_sensitive {
        expected = expected.to_lowercase();
        actual = actual.to_lowercase();
    }
    if kind == ClaimKind::Quote {
        actual.contains(&expected)
    } else {
        actual == expected
    }
}

/// Normalize a quote for literal matching: normalize line endings, collapse ASCII
/// whitespace runs to one ASCII space, then trim.
pub fn normalize_quote(input: &str) -> String {
    let line_normalized = input.replace("\r\n", "\n").replace('\r', "\n");
    let mut out = String::with_capacity(line_normalized.len());
    let mut in_ascii_ws = false;
    for ch in line_normalized.chars() {
        if ch.is_ascii_whitespace() {
            if !in_ascii_ws {
                out.push(' ');
                in_ascii_ws = true;
            }
        } else {
            out.push(ch);
            in_ascii_ws = false;
        }
    }
    out.trim().to_string()
}

#[cfg(test)]
mod tests {
    use super::*;
    use ethos_core::grounding::{
        Capabilities, GroundingCell, GroundingElement, GroundingSpan, GroundingTable, PageGeometry,
        ParserIdentity,
    };
    use ethos_core::verify_types::{CapabilityLimit, CellRef, Citation, Claim};

    #[derive(Clone)]
    struct TestSource {
        caps: Capabilities,
        fingerprint: Option<String>,
        crop_ref: Option<String>,
    }

    impl Default for TestSource {
        fn default() -> Self {
            Self {
                caps: Capabilities {
                    spans: true,
                    char_offsets: true,
                    tables: true,
                    fingerprint: true,
                    coordinate_origin: CoordinateOrigin::TopLeft,
                    crop_support: false,
                },
                fingerprint: Some(
                    "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3"
                        .into(),
                ),
                crop_ref: None,
            }
        }
    }

    impl GroundingSource for TestSource {
        fn parser(&self) -> ParserIdentity {
            ParserIdentity {
                name: "test-parser".into(),
                version: "0.1.0".into(),
                adapter: None,
                adapter_version: None,
            }
        }
        fn capabilities(&self) -> Capabilities {
            self.caps
        }
        fn fingerprint(&self) -> Option<String> {
            self.fingerprint.clone()
        }
        fn pages(&self) -> Vec<PageGeometry> {
            vec![PageGeometry {
                id: "p0001".into(),
                index: 1,
                width: 61200,
                height: 79200,
                rotation: 0,
            }]
        }
        fn elements(&self) -> Vec<GroundingElement> {
            vec![
                GroundingElement {
                    id: "e000002".into(),
                    page: "p0001".into(),
                    bbox: [7200, 10100, 54000, 11500],
                    kind: "text_block".into(),
                    text: Some(
                        "Revenue grew to $12.4M in Q3 2025, driven by enterprise expansion.".into(),
                    ),
                },
                GroundingElement {
                    id: "e000003".into(),
                    page: "p0001".into(),
                    bbox: [7200, 13000, 54000, 20000],
                    kind: "table".into(),
                    text: None,
                },
            ]
        }
        fn spans(&self) -> Vec<GroundingSpan> {
            vec![GroundingSpan {
                id: "s000002".into(),
                page: "p0001".into(),
                bbox: [7200, 10100, 54000, 11500],
                text: "Revenue grew to $12.4M in Q3 2025".into(),
                element: Some("e000002".into()),
                char_start: Some(0),
                char_end: Some(34),
            }]
        }
        fn tables(&self) -> Vec<GroundingTable> {
            vec![GroundingTable {
                id: "t0001".into(),
                page: "p0001".into(),
                bbox: [7200, 13000, 54000, 20000],
                cells: vec![
                    GroundingCell {
                        row: 0,
                        col: 0,
                        row_span: 1,
                        col_span: 1,
                        bbox: [7200, 13000, 30600, 16500],
                        text: "Metric".into(),
                    },
                    GroundingCell {
                        row: 1,
                        col: 1,
                        row_span: 1,
                        col_span: 1,
                        bbox: [30600, 16500, 54000, 20000],
                        text: "$12.4M".into(),
                    },
                ],
            }]
        }
        fn crop_ref(&self, page: &str, bbox: [i64; 4]) -> Option<String> {
            if page == "p0001" && bbox == [7200, 10100, 54000, 11500] {
                self.crop_ref.clone()
            } else {
                None
            }
        }
    }

    struct ElementSource {
        elements: Vec<GroundingElement>,
    }

    impl GroundingSource for ElementSource {
        fn parser(&self) -> ParserIdentity {
            ParserIdentity {
                name: "element-test-parser".into(),
                version: "0.1.0".into(),
                adapter: None,
                adapter_version: None,
            }
        }
        fn capabilities(&self) -> Capabilities {
            Capabilities {
                spans: true,
                char_offsets: true,
                tables: true,
                fingerprint: true,
                coordinate_origin: CoordinateOrigin::TopLeft,
                crop_support: false,
            }
        }
        fn fingerprint(&self) -> Option<String> {
            Some("sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3".into())
        }
        fn pages(&self) -> Vec<PageGeometry> {
            vec![
                PageGeometry {
                    id: "p0001".into(),
                    index: 1,
                    width: 61200,
                    height: 79200,
                    rotation: 0,
                },
                PageGeometry {
                    id: "p0002".into(),
                    index: 2,
                    width: 61200,
                    height: 79200,
                    rotation: 0,
                },
            ]
        }
        fn elements(&self) -> Vec<GroundingElement> {
            self.elements.clone()
        }
        fn spans(&self) -> Vec<GroundingSpan> {
            Vec::new()
        }
        fn tables(&self) -> Vec<GroundingTable> {
            Vec::new()
        }
    }

    fn claim(kind: ClaimKind, text: Option<&str>, citation: Citation) -> Claim {
        Claim {
            kind,
            text: text.map(str::to_string),
            citation,
        }
    }

    fn input(source: &TestSource, claims: Vec<Claim>) -> CitationInput {
        CitationInput::Envelope(CitationEnvelope {
            document_fingerprint: source.fingerprint(),
            claims,
        })
    }

    fn verify(source: &TestSource, claims: Vec<Claim>) -> VerificationReport {
        let cfg = VerificationConfig::default_v1();
        verify_claims(source, input(source, claims), &cfg, "0".repeat(64))
    }

    fn verify_with_config(
        source: &TestSource,
        claims: Vec<Claim>,
        cfg: &VerificationConfig,
    ) -> VerificationReport {
        verify_claims(source, input(source, claims), cfg, "0".repeat(64))
    }

    fn element(id: &str, page: &str, bbox: [i64; 4], text: Option<&str>) -> GroundingElement {
        GroundingElement {
            id: id.into(),
            page: page.into(),
            bbox,
            kind: "text_block".into(),
            text: text.map(str::to_string),
        }
    }

    fn verify_elements(elements: Vec<GroundingElement>, claims: Vec<Claim>) -> VerificationReport {
        let source = ElementSource { elements };
        let cfg = VerificationConfig::default_v1();
        let citations = CitationInput::Envelope(CitationEnvelope {
            document_fingerprint: source.fingerprint(),
            claims,
        });
        verify_claims(&source, citations, &cfg, "0".repeat(64))
    }

    #[test]
    fn quote_and_presence_claims_ground_with_literal_matching() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![
                claim(
                    ClaimKind::Quote,
                    Some("Revenue grew to $12.4M in Q3 2025"),
                    Citation {
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                ),
                claim(
                    ClaimKind::Presence,
                    None,
                    Citation {
                        span_id: Some("s000002".into()),
                        ..Default::default()
                    },
                ),
            ],
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.checks.len(), 2);
        assert_eq!(report.capability_limits, Vec::<CapabilityLimit>::new());
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            report.checks[0].match_method,
            MatchMethod::NormalizedTextContains
        );
        assert_eq!(report.checks[1].status, CheckStatus::Grounded);
        assert_eq!(report.checks[1].match_method, MatchMethod::PresenceOnly);
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.text.as_deref()),
            Some("Revenue grew to $12.4M in Q3 2025, driven by enterprise expansion.")
        );
        assert_eq!(report.warnings, Vec::<WarningCode>::new());
    }

    #[test]
    fn quote_claim_grounds_across_adjacent_element_text_fragments() {
        let report = verify_elements(
            vec![
                element(
                    "split-a",
                    "p0001",
                    [100, 100, 400, 200],
                    Some("The alpha trust loop verifies "),
                ),
                element(
                    "split-b",
                    "p0001",
                    [400, 100, 700, 200],
                    Some("grounded evidence"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The alpha trust loop verifies grounded evidence"),
                Citation {
                    element_id: Some("split-a".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            report.checks[0].match_method,
            MatchMethod::NormalizedTextContains
        );
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.text.as_deref()),
            Some("The alpha trust loop verifies grounded evidence")
        );
        assert_eq!(
            report.checks[0].evidence.as_ref().and_then(|e| e.bbox),
            Some([100, 100, 700, 200])
        );
    }

    #[test]
    fn quote_claim_page_only_locator_does_not_search_adjacent_fragments() {
        let report = verify_elements(
            vec![
                element(
                    "split-a",
                    "p0001",
                    [100, 100, 400, 200],
                    Some("The alpha trust loop verifies "),
                ),
                element(
                    "split-b",
                    "p0001",
                    [400, 100, 700, 200],
                    Some("grounded evidence"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The alpha trust loop verifies grounded evidence"),
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(report.checks[0].reason, Some(CheckReason::TextMismatch));
    }

    #[test]
    fn quote_claim_grounds_when_element_id_points_to_second_adjacent_fragment() {
        let report = verify_elements(
            vec![
                element(
                    "split-a",
                    "p0001",
                    [100, 100, 400, 200],
                    Some("The alpha trust loop verifies "),
                ),
                element(
                    "split-b",
                    "p0001",
                    [400, 100, 700, 200],
                    Some("grounded evidence"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The alpha trust loop verifies grounded evidence"),
                Citation {
                    element_id: Some("split-b".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.text.as_deref()),
            Some("The alpha trust loop verifies grounded evidence")
        );
        assert_eq!(
            report.checks[0].evidence.as_ref().and_then(|e| e.bbox),
            Some([100, 100, 700, 200])
        );
    }

    #[test]
    fn quote_claim_does_not_stitch_non_touching_element_bboxes() {
        let report = verify_elements(
            vec![
                element(
                    "split-a",
                    "p0001",
                    [100, 100, 390, 200],
                    Some("The alpha trust loop verifies "),
                ),
                element(
                    "split-b",
                    "p0001",
                    [400, 100, 700, 200],
                    Some("grounded evidence"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The alpha trust loop verifies grounded evidence"),
                Citation {
                    element_id: Some("split-a".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(report.checks[0].reason, Some(CheckReason::TextMismatch));
    }

    #[test]
    fn quote_claim_bbox_locator_does_not_expand_outside_cited_region() {
        let report = verify_elements(
            vec![
                element(
                    "split-a",
                    "p0001",
                    [100, 100, 400, 200],
                    Some("The alpha trust loop verifies "),
                ),
                element(
                    "split-b",
                    "p0001",
                    [400, 100, 700, 200],
                    Some("grounded evidence"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The alpha trust loop verifies grounded evidence"),
                Citation {
                    page: Some("p0001".into()),
                    bbox: Some([120, 120, 380, 180]),
                    ..Default::default()
                },
            )],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(report.checks[0].reason, Some(CheckReason::TextMismatch));
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.text.as_deref()),
            Some("The alpha trust loop verifies ")
        );
        assert_eq!(
            report.checks[0].evidence.as_ref().and_then(|e| e.bbox),
            Some([100, 100, 400, 200])
        );
    }

    #[test]
    fn bbox_locator_prefers_smallest_containing_element() {
        let report = verify_elements(
            vec![
                element(
                    "container",
                    "p0001",
                    [0, 0, 1000, 1000],
                    Some("outer wrapper text"),
                ),
                element(
                    "inner",
                    "p0001",
                    [100, 100, 400, 200],
                    Some("The exact cited quote"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The exact cited quote"),
                Citation {
                    page: Some("p0001".into()),
                    bbox: Some([120, 120, 380, 180]),
                    ..Default::default()
                },
            )],
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.text.as_deref()),
            Some("The exact cited quote")
        );
        assert_eq!(
            report.checks[0].evidence.as_ref().and_then(|e| e.bbox),
            Some([100, 100, 400, 200])
        );
    }

    #[test]
    fn quote_claim_does_not_ground_across_non_adjacent_or_wrong_page_fragments() {
        let non_adjacent = verify_elements(
            vec![
                element(
                    "split-a",
                    "p0001",
                    [100, 100, 400, 200],
                    Some("The alpha trust loop verifies "),
                ),
                element(
                    "between",
                    "p0001",
                    [100, 220, 700, 320],
                    Some("separate evidence"),
                ),
                element(
                    "split-b",
                    "p0001",
                    [400, 100, 700, 200],
                    Some("grounded evidence"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The alpha trust loop verifies grounded evidence"),
                Citation {
                    element_id: Some("split-a".into()),
                    ..Default::default()
                },
            )],
        );
        assert!(!non_adjacent.all_evidence_grounded);
        assert_eq!(non_adjacent.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(
            non_adjacent.checks[0].reason,
            Some(CheckReason::TextMismatch)
        );

        let wrong_page = verify_elements(
            vec![
                element(
                    "split-a",
                    "p0001",
                    [100, 100, 400, 200],
                    Some("The alpha trust loop verifies "),
                ),
                element(
                    "split-b",
                    "p0002",
                    [400, 100, 700, 200],
                    Some("grounded evidence"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The alpha trust loop verifies grounded evidence"),
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )],
        );
        assert!(!wrong_page.all_evidence_grounded);
        assert_eq!(wrong_page.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(wrong_page.checks[0].reason, Some(CheckReason::TextMismatch));
    }

    #[test]
    fn mismatch_and_not_found_keep_gate_false() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![
                claim(
                    ClaimKind::Quote,
                    Some("Revenue fell to $1"),
                    Citation {
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                ),
                claim(
                    ClaimKind::Presence,
                    None,
                    Citation {
                        element_id: Some("missing".into()),
                        ..Default::default()
                    },
                ),
            ],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(report.checks[0].reason, Some(CheckReason::TextMismatch));
        assert_eq!(report.checks[1].status, CheckStatus::NotFound);
        assert_eq!(report.checks[1].reason, Some(CheckReason::ElementNotFound));
    }

    #[test]
    fn value_claims_use_literal_text_matching() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::Value,
                Some("Revenue grew to $12.4M in Q3 2025, driven by enterprise expansion."),
                Citation {
                    element_id: Some("e000002".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.unsupported_claim_kinds, Vec::<String>::new());
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(report.checks[0].match_method, MatchMethod::NormalizedText);
    }

    #[test]
    fn value_substrings_do_not_ground() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::Value,
                Some("1"),
                Citation {
                    element_id: Some("e000002".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(report.checks[0].reason, Some(CheckReason::TextMismatch));
        assert_eq!(report.checks[0].match_method, MatchMethod::NormalizedText);
    }

    #[test]
    fn table_cell_claims_lookup_cell_and_match_text() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::TableCell,
                Some("$12.4M"),
                Citation {
                    table_id: Some("t0001".into()),
                    cell: Some(CellRef { row: 1, col: 1 }),
                    ..Default::default()
                },
            )],
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.unsupported_claim_kinds, Vec::<String>::new());
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(report.checks[0].match_method, MatchMethod::TableCellLookup);
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.text.as_deref()),
            Some("$12.4M")
        );
    }

    #[test]
    fn table_cell_missing_cell_is_not_found() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::TableCell,
                Some("$12.4M"),
                Citation {
                    table_id: Some("t0001".into()),
                    cell: Some(CellRef { row: 9, col: 9 }),
                    ..Default::default()
                },
            )],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::NotFound);
        assert_eq!(
            report.checks[0].reason,
            Some(CheckReason::TableCellNotFound)
        );
        assert_eq!(report.checks[0].match_method, MatchMethod::None);
    }

    #[test]
    fn empty_table_collection_is_not_found_when_tables_are_supported() {
        let source = TestSource {
            caps: Capabilities {
                tables: true,
                ..TestSource::default().caps
            },
            ..TestSource::default()
        };
        struct NoTables(TestSource);
        impl GroundingSource for NoTables {
            fn parser(&self) -> ParserIdentity {
                self.0.parser()
            }
            fn capabilities(&self) -> Capabilities {
                self.0.capabilities()
            }
            fn fingerprint(&self) -> Option<String> {
                self.0.fingerprint()
            }
            fn pages(&self) -> Vec<PageGeometry> {
                self.0.pages()
            }
            fn elements(&self) -> Vec<GroundingElement> {
                self.0.elements()
            }
            fn spans(&self) -> Vec<GroundingSpan> {
                self.0.spans()
            }
            fn tables(&self) -> Vec<GroundingTable> {
                Vec::new()
            }
        }
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::TableCell,
                Some("$12.4M"),
                Citation {
                    table_id: Some("missing".into()),
                    cell: Some(CellRef { row: 1, col: 1 }),
                    ..Default::default()
                },
            )],
        );
        assert_eq!(report.checks[0].status, CheckStatus::NotFound);

        let no_tables = NoTables(source);
        let cfg = VerificationConfig::default_v1();
        let report = verify_claims(
            &no_tables,
            CitationInput::Envelope(CitationEnvelope {
                document_fingerprint: no_tables.fingerprint(),
                claims: vec![claim(
                    ClaimKind::TableCell,
                    Some("$12.4M"),
                    Citation {
                        table_id: Some("missing".into()),
                        cell: Some(CellRef { row: 1, col: 1 }),
                        ..Default::default()
                    },
                )],
            }),
            &cfg,
            "0".repeat(64),
        );
        assert_eq!(report.checks[0].status, CheckStatus::NotFound);
    }

    #[test]
    fn missing_table_capability_blocks_table_cell_claims() {
        let source = TestSource {
            caps: Capabilities {
                tables: false,
                ..TestSource::default().caps
            },
            ..TestSource::default()
        };
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::TableCell,
                Some("$12.4M"),
                Citation {
                    table_id: Some("t0001".into()),
                    cell: Some(CellRef { row: 1, col: 1 }),
                    ..Default::default()
                },
            )],
        );

        assert_eq!(report.checks[0].status, CheckStatus::CapabilityBlocked);
        assert_eq!(
            report.checks[0].reason,
            Some(CheckReason::MissingTableCapability)
        );
        assert_eq!(
            report.capability_limits,
            vec![CapabilityLimit::MissingTables]
        );
        assert!(report.checks[0]
            .warnings
            .contains(&WarningCode::CapabilityLimited));
    }

    #[test]
    fn crop_refs_are_echoed_only_when_requested_and_supported() {
        let source = TestSource {
            caps: Capabilities {
                crop_support: true,
                ..TestSource::default().caps
            },
            crop_ref: Some("crop://p0001/e000002.png".into()),
            ..TestSource::default()
        };
        let claim = claim(
            ClaimKind::Quote,
            Some("Revenue grew to $12.4M in Q3 2025"),
            Citation {
                element_id: Some("e000002".into()),
                ..Default::default()
            },
        );

        let mut cfg = VerificationConfig::default_v1();
        cfg.evidence.as_mut().unwrap().include_crops = true;
        let with_crops = verify_with_config(&source, vec![claim.clone()], &cfg);
        assert_eq!(
            with_crops.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.crop_ref.as_deref()),
            Some("crop://p0001/e000002.png")
        );

        cfg.evidence.as_mut().unwrap().include_crops = false;
        let without_crops = verify_with_config(&source, vec![claim], &cfg);
        assert_eq!(
            without_crops.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.crop_ref.as_deref()),
            None
        );
    }

    #[test]
    fn requested_crop_refs_without_source_support_remain_capability_limited() {
        let source = TestSource {
            crop_ref: Some("crop://p0001/e000002.png".into()),
            ..TestSource::default()
        };
        let mut cfg = VerificationConfig::default_v1();
        cfg.evidence.as_mut().unwrap().include_crops = true;

        let report = verify_with_config(
            &source,
            vec![claim(
                ClaimKind::Quote,
                Some("Revenue grew to $12.4M in Q3 2025"),
                Citation {
                    element_id: Some("e000002".into()),
                    ..Default::default()
                },
            )],
            &cfg,
        );

        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            report.capability_limits,
            vec![CapabilityLimit::MissingCropSupport]
        );
        assert!(report.warnings.contains(&WarningCode::CapabilityLimited));
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.crop_ref.as_deref()),
            None
        );
    }

    #[test]
    fn stale_fingerprint_marks_checks_stale_and_gate_false() {
        let source = TestSource::default();
        let cfg = VerificationConfig::default_v1();
        let report = verify_claims(
            &source,
            CitationInput::Envelope(CitationEnvelope {
                document_fingerprint: Some(
                    "sha256:0000000000000000000000000000000000000000000000000000000000000000"
                        .into(),
                ),
                claims: vec![claim(
                    ClaimKind::Presence,
                    None,
                    Citation {
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                )],
            }),
            &cfg,
            "0".repeat(64),
        );

        assert!(report.fingerprint_stale);
        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Stale);
        assert_eq!(report.checks[0].reason, Some(CheckReason::StaleFingerprint));
    }

    #[test]
    fn missing_citation_fingerprint_blocks_when_required() {
        let source = TestSource::default();
        let cfg = VerificationConfig::default_v1();
        let report = verify_claims(
            &source,
            CitationInput::Envelope(CitationEnvelope {
                document_fingerprint: None,
                claims: vec![claim(
                    ClaimKind::Presence,
                    None,
                    Citation {
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                )],
            }),
            &cfg,
            "0".repeat(64),
        );

        assert!(!report.fingerprint_stale);
        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Stale);
        assert_eq!(
            report.checks[0].reason,
            Some(CheckReason::MissingCitationFingerprint)
        );
    }

    #[test]
    fn unsupported_claim_kinds_are_explicit() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::Region,
                None,
                Citation {
                    element_id: Some("e000002".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::UnsupportedClaimKind);
        assert_eq!(
            report.checks[0].reason,
            Some(CheckReason::UnsupportedClaimKind)
        );
        assert_eq!(report.unsupported_claim_kinds, vec!["region"]);
    }

    #[test]
    fn non_v1_claim_kinds_are_deduped_and_keep_gate_false() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![
                claim(
                    ClaimKind::Presence,
                    None,
                    Citation {
                        page: Some("p0001".into()),
                        ..Default::default()
                    },
                ),
                claim(
                    ClaimKind::Region,
                    None,
                    Citation {
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                ),
                claim(
                    ClaimKind::Other,
                    Some("$12.4M equals 12400000"),
                    Citation {
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                ),
                claim(
                    ClaimKind::Region,
                    None,
                    Citation {
                        page: Some("p0001".into()),
                        ..Default::default()
                    },
                ),
            ],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(report.checks[1].status, CheckStatus::UnsupportedClaimKind);
        assert_eq!(report.checks[2].status, CheckStatus::UnsupportedClaimKind);
        assert_eq!(report.checks[3].status, CheckStatus::UnsupportedClaimKind);
        assert_eq!(report.checks[1].match_method, MatchMethod::None);
        assert_eq!(report.checks[2].match_method, MatchMethod::None);
        assert_eq!(report.checks[3].match_method, MatchMethod::None);
        assert_eq!(
            report.checks[1].reason,
            Some(CheckReason::UnsupportedClaimKind)
        );
        assert_eq!(
            report.checks[2].reason,
            Some(CheckReason::UnsupportedClaimKind)
        );
        assert_eq!(
            report.checks[3].reason,
            Some(CheckReason::UnsupportedClaimKind)
        );
        assert!(report.checks[1].evidence.is_none());
        assert!(report.checks[2].evidence.is_none());
        assert!(report.checks[3].evidence.is_none());
        assert!(report.checks[1].warnings.is_empty());
        assert!(report.checks[2].warnings.is_empty());
        assert!(report.checks[3].warnings.is_empty());
        assert!(!report.checks[1].semantic_unverified);
        assert!(!report.checks[2].semantic_unverified);
        assert!(!report.checks[3].semantic_unverified);
        assert_eq!(report.unsupported_claim_kinds, vec!["region", "other"]);
    }

    #[test]
    fn missing_span_capability_blocks_span_locator() {
        let source = TestSource {
            caps: Capabilities {
                spans: false,
                char_offsets: false,
                tables: false,
                fingerprint: false,
                coordinate_origin: CoordinateOrigin::Unknown,
                crop_support: false,
            },
            fingerprint: None,
            crop_ref: None,
        };
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::Presence,
                None,
                Citation {
                    span_id: Some("s000002".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::CapabilityBlocked);
        assert_eq!(
            report.checks[0].reason,
            Some(CheckReason::MissingSpanCapability)
        );
        assert_eq!(
            report.capability_limits,
            vec![
                CapabilityLimit::MissingFingerprint,
                CapabilityLimit::MissingSpans,
                CapabilityLimit::MissingCharOffsets,
                CapabilityLimit::MissingTables,
                CapabilityLimit::UnknownCoordinateOrigin
            ]
        );
        assert!(report.warnings.contains(&WarningCode::CapabilityLimited));
        assert!(report.checks[0]
            .warnings
            .contains(&WarningCode::CapabilityLimited));
    }

    #[test]
    fn citation_fingerprint_without_source_fingerprint_blocks_checks() {
        let source = TestSource {
            caps: Capabilities {
                fingerprint: false,
                ..TestSource::default().caps
            },
            fingerprint: None,
            ..TestSource::default()
        };
        let cfg = VerificationConfig::default_v1();
        let report = verify_claims(
            &source,
            CitationInput::Envelope(CitationEnvelope {
                document_fingerprint: Some(
                    "sha256:b5d30710d0c25cc38d8dec924ecaf57ae4f81276dd5dc14d75cb3b5b6bde62d3"
                        .into(),
                ),
                claims: vec![claim(
                    ClaimKind::Presence,
                    None,
                    Citation {
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                )],
            }),
            &cfg,
            "0".repeat(64),
        );

        assert!(!report.fingerprint_stale);
        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::CapabilityBlocked);
        assert_eq!(
            report.checks[0].reason,
            Some(CheckReason::MissingSourceFingerprint)
        );
        assert_eq!(
            report.capability_limits,
            vec![CapabilityLimit::MissingFingerprint]
        );
        assert!(report.warnings.contains(&WarningCode::CapabilityLimited));
        assert!(report.checks[0]
            .warnings
            .contains(&WarningCode::CapabilityLimited));
    }

    #[test]
    fn missing_text_is_error_for_library_callers() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::Quote,
                None,
                Citation {
                    element_id: Some("e000002".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Error);
        assert_eq!(
            report.checks[0].reason,
            Some(CheckReason::MissingRequiredText)
        );
        assert_eq!(report.checks[0].match_method, MatchMethod::None);
    }

    #[test]
    fn quote_normalization_is_ascii_whitespace_only() {
        assert_eq!(normalize_quote("  a\r\n\t b  "), "a b");
        assert_eq!(normalize_quote("a\u{00a0}b"), "a\u{00a0}b");
    }

    #[test]
    fn report_serializes_to_schema_shape() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::Presence,
                None,
                Citation {
                    element_id: Some("e000002".into()),
                    ..Default::default()
                },
            )],
        );
        let v = serde_json::to_value(&report).unwrap();
        assert_eq!(v["grounding"]["parser"]["name"], "test-parser");
        assert_eq!(v["fingerprint_stale"], false);
        assert_eq!(v["checks"].as_array().unwrap().len(), 1);
    }
}
