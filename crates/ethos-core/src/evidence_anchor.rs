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

//! Evidence-anchor request/report schema types.
//!
//! Evidence anchoring is a deterministic source-tracing primitive: caller-provided
//! evidence refs are checked against a [`crate::grounding::GroundingSource`].
//! It does not perform semantic answer verification.

use serde::{Deserialize, Serialize};

use crate::grounding::{Capabilities, ParserIdentity};
use crate::verify_types::CapabilityLimit;

/// Request artifact type for evidence anchoring.
pub const EVIDENCE_ANCHOR_REQUEST_ARTIFACT_TYPE: &str = "ethos.evidence_anchor_request.v1";
/// Report artifact type for evidence anchoring.
pub const EVIDENCE_ANCHOR_REPORT_ARTIFACT_TYPE: &str = "ethos.evidence_anchor_report.v1";

/// Evidence-anchor request envelope.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceAnchorRequest {
    /// Artifact type identity.
    pub artifact_type: String,
    /// Schema version.
    pub schema_version: String,
    /// Optional source fingerprint the evidence refs were produced against.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_fingerprint: Option<String>,
    /// Caller-provided evidence refs in deterministic input order.
    pub evidence_refs: Vec<EvidenceRef>,
}

/// One caller-provided evidence reference.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceRef {
    /// Caller correlation key. Unique within one request.
    pub evidence_id: String,
    /// Evidence kind.
    pub evidence_kind: EvidenceKind,
    /// Minimum anchor level required by the caller.
    pub required_anchor_level: AnchorLevel,
    /// Source locator.
    pub locator: EvidenceLocator,
    /// Expected text, when text matching is required.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expected_text: Option<String>,
    /// SHA-256 of normalized expected text, when supplied by the caller.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expected_text_sha256: Option<String>,
    /// Text normalization profile for expected text.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text_normalization_profile: Option<TextNormalizationProfile>,
}

/// Supported and accepted evidence kinds.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EvidenceKind {
    /// Page existence.
    Page,
    /// Text evidence.
    Text,
    /// Text and/or region evidence.
    TextRegion,
    /// Table cell evidence.
    TableCell,
    /// Accepted but unsupported in v1.
    Region,
    /// Accepted but unsupported in v1.
    Other,
}

/// Required or achieved anchor level.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AnchorLevel {
    /// No anchor.
    None,
    /// Page anchor.
    Page,
    /// Text anchor.
    Text,
    /// Bounding-box anchor.
    Bbox,
    /// Text plus bounding-box anchor.
    TextBbox,
    /// Table-cell anchor.
    TableCell,
}

/// Source locator for an evidence ref.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceLocator {
    /// 1-based parser-neutral page index.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub page_index: Option<u32>,
    /// Parser-specific page id.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub page_id: Option<String>,
    /// Parser-specific element id.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub element_id: Option<String>,
    /// Parser-specific span id.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub span_id: Option<String>,
    /// Source bbox `[x0, y0, x1, y1]` in integer quanta.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bbox: Option<[i64; 4]>,
    /// Parser-specific table id.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub table_id: Option<String>,
    /// Table cell address.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cell: Option<AnchorCellRef>,
    /// Coordinate profile for bbox locators.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub coordinate_profile: Option<CoordinateProfile>,
}

/// 0-based table cell address.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AnchorCellRef {
    /// Row index.
    pub row: u32,
    /// Column index.
    pub col: u32,
}

/// Supported text normalization profiles.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TextNormalizationProfile {
    /// Collapse ASCII whitespace, matching the existing verifier normalization.
    EthosCollapseWhitespaceV1,
}

/// Supported coordinate profiles.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CoordinateProfile {
    /// Ethos integer quanta with top-left origin.
    EthosQuantizedTopLeftV1,
}

/// Evidence-anchor report envelope.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceAnchorReport {
    /// Artifact type identity.
    pub artifact_type: String,
    /// Schema version.
    pub schema_version: String,
    /// Source fingerprint, when declared by the grounding source.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_fingerprint: Option<String>,
    /// Grounding metadata reused from existing verification reports.
    pub grounding: EvidenceAnchorGrounding,
    /// Per-ref anchor outcomes.
    pub anchors: Vec<EvidenceAnchor>,
}

/// Grounding metadata embedded in evidence-anchor reports.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceAnchorGrounding {
    /// Producing parser identity.
    pub parser: ParserIdentity,
    /// Declared source capabilities.
    pub capabilities: Capabilities,
}

/// One evidence anchor outcome.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceAnchor {
    /// Caller correlation key.
    pub evidence_id: String,
    /// Evidence kind.
    pub evidence_kind: EvidenceKind,
    /// Rollup status.
    pub anchor_status: AnchorStatus,
    /// Required level from the request.
    pub required_anchor_level: AnchorLevel,
    /// Best deterministic level achieved.
    pub achieved_anchor_level: AnchorLevel,
    /// Per-axis checks.
    pub checks: AnchorChecks,
    /// Capability limits that affected this anchor.
    pub capability_limits: Vec<CapabilityLimit>,
}

/// Rollup status for one evidence anchor.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AnchorStatus {
    /// Required evidence bound to source evidence.
    Bound,
    /// A located target failed the expected content/location check.
    Mismatch,
    /// Required source target was not found.
    NotFound,
    /// Request/source fingerprints differ.
    StaleFingerprint,
    /// The source lacks a capability needed to decide the required anchor.
    CapabilityLimited,
    /// The evidence kind is accepted but unsupported in v1.
    UnsupportedEvidenceKind,
}

/// Per-axis evidence-anchor checks.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AnchorChecks {
    /// Fingerprint check.
    pub fingerprint: FingerprintCheck,
    /// Page check.
    pub page: PageCheck,
    /// Text check.
    pub text: TextCheck,
    /// Bbox check.
    pub bbox: BboxCheck,
    /// Table-cell check.
    pub table_cell: TableCellCheck,
}

impl Default for AnchorChecks {
    fn default() -> Self {
        AnchorChecks {
            fingerprint: FingerprintCheck::NotChecked,
            page: PageCheck::NotChecked,
            text: TextCheck::NotChecked,
            bbox: BboxCheck::NotChecked,
            table_cell: TableCellCheck::NotChecked,
        }
    }
}

/// Fingerprint axis result.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FingerprintCheck {
    /// Fingerprints match.
    Matched,
    /// Fingerprints differ.
    Stale,
    /// Not checked.
    NotChecked,
    /// Source cannot declare a fingerprint.
    CapabilityLimited,
}

/// Page axis result.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PageCheck {
    /// Page was found.
    Found,
    /// Page was not found.
    NotFound,
    /// Not checked.
    NotChecked,
}

/// Text axis result.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TextCheck {
    /// Text matched.
    Matched,
    /// Located text mismatched.
    Mismatch,
    /// Text target was not found.
    NotFound,
    /// Not checked.
    NotChecked,
    /// Source lacks required text capability.
    CapabilityLimited,
}

/// Bbox axis result.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BboxCheck {
    /// Bbox is valid.
    Valid,
    /// Located bbox mismatched.
    Invalid,
    /// Bbox target was not found.
    NotFound,
    /// Not checked.
    NotChecked,
    /// Source lacks required coordinate capability.
    CapabilityLimited,
}

/// Table-cell axis result.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TableCellCheck {
    /// Table cell matched.
    Matched,
    /// Located table cell mismatched.
    Mismatch,
    /// Table cell was not found.
    NotFound,
    /// Not checked.
    NotChecked,
    /// Source lacks table capability.
    CapabilityLimited,
}
