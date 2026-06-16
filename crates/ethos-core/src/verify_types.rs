//! Verification report/config schema types (`urn:ethos:schema:verification-report:1`,
//! `urn:ethos:schema:verification-config:1`).
//!
//! Lives behind `verify-types` (no parser internals) so `ethos-verify` can use these
//! without ever seeing the canonical model or backend traits.

use serde::{Deserialize, Serialize};

use crate::codes::WarningCode;
use crate::grounding::{Capabilities, ParserIdentity};

/// Structured capability limitations that caused `capability_limited` warnings.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CapabilityLimit {
    /// Source cannot expose text spans.
    MissingSpans,
    /// Source spans do not carry char offsets.
    MissingCharOffsets,
    /// Source cannot model tables/cells.
    MissingTables,
    /// Source cannot declare a document fingerprint.
    MissingFingerprint,
    /// Source coordinate origin is unknown.
    UnknownCoordinateOrigin,
    /// Source cannot produce crop references.
    MissingCropSupport,
}

/// Claim kinds. `Other` appears only in reports (as an unsupported kind), never in configs.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ClaimKind {
    /// A verbatim quote is claimed to exist at the citation target.
    Quote,
    /// A specific value (number/date/string) is claimed at the target.
    Value,
    /// The cited element/region merely exists.
    Presence,
    /// A value is claimed in a specific table cell.
    TableCell,
    /// A non-text region is cited.
    Region,
    /// Anything else — always unsupported in v1.
    Other,
}

/// Per-check status.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CheckStatus {
    /// Evidence found and matched by the declared method.
    Grounded,
    /// Citation target does not exist in the grounding source.
    NotFound,
    /// Target exists but content does not match.
    Mismatch,
    /// Evidence is stale (fingerprint mismatch).
    Stale,
    /// Claim kind not supported by the active config/verifier.
    UnsupportedClaimKind,
    /// The grounding source lacks a capability this check requires.
    CapabilityBlocked,
    /// Internal error while checking (never a panic).
    Error,
}

/// Stable reason for a non-grounded check outcome.
///
/// These are diagnostic labels only. They explain why the check did not ground
/// under the active literal verifier; they do not add semantic judgment.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CheckReason {
    /// Citation had no usable locator.
    MissingLocator,
    /// Textual claim kind was missing required text.
    MissingRequiredText,
    /// Claim kind is unsupported by the verifier or active config.
    UnsupportedClaimKind,
    /// Citation fingerprint differs from the grounding source fingerprint.
    StaleFingerprint,
    /// Citation was fingerprint-pinned but the source did not declare one.
    MissingSourceFingerprint,
    /// Span locator was used with a source that does not expose spans.
    MissingSpanCapability,
    /// Table-cell locator was used with a source that does not expose tables.
    MissingTableCapability,
    /// Bbox locator was used with a source whose coordinate origin is unknown.
    UnknownCoordinateOrigin,
    /// Element id was not found.
    ElementNotFound,
    /// Span id was not found.
    SpanNotFound,
    /// Page id was not found.
    PageNotFound,
    /// Bbox locator did not resolve to a grounding element.
    BboxNotFound,
    /// Bbox locator did not include a page locator.
    MissingPageForBbox,
    /// Table-cell citation did not include both table id and cell address.
    MissingTableCellLocator,
    /// Table id was not found.
    TableNotFound,
    /// Cell address was not found in the table.
    TableCellNotFound,
    /// Target text did not match the claimed text under the active matcher.
    TextMismatch,
}

/// How evidence was matched. v1 is deliberately literal — nothing fuzzy, nothing semantic.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MatchMethod {
    /// Byte-exact text equality.
    ExactText,
    /// Equality after the pinned whitespace normalization (config).
    NormalizedText,
    /// Byte-exact substring containment, used only for quote evidence inside a larger target.
    ExactTextContains,
    /// Substring containment after the pinned whitespace normalization, used only for quotes.
    NormalizedTextContains,
    /// Table cell lookup by (table id, row, col).
    TableCellLookup,
    /// Citation bbox contained in evidence bbox within pinned tolerance.
    BboxContainment,
    /// Existence of the cited target only.
    PresenceOnly,
    /// No match was attempted/possible.
    None,
}

/// Citation locator — where the claim says the evidence lives. At least one field must be
/// present (schema `minProperties: 1`); [`Citation::has_locator`] checks it.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Citation {
    /// Page id in the grounding source's namespace.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub page: Option<String>,
    /// Element id.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub element_id: Option<String>,
    /// Span id.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub span_id: Option<String>,
    /// Table id.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub table_id: Option<String>,
    /// Cell address within `table_id`.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cell: Option<CellRef>,
    /// Cited bbox `[x0, y0, x1, y1]`.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bbox: Option<[i64; 4]>,
}

impl Citation {
    /// True when at least one locator field is present.
    pub fn has_locator(&self) -> bool {
        self.page.is_some()
            || self.element_id.is_some()
            || self.span_id.is_some()
            || self.table_id.is_some()
            || self.cell.is_some()
            || self.bbox.is_some()
    }
}

/// 0-based cell address.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CellRef {
    /// Row index.
    pub row: u32,
    /// Column index.
    pub col: u32,
}

/// A single claim to verify.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Claim {
    /// Claim kind.
    pub kind: ClaimKind,
    /// Claimed text, when textual.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<String>,
    /// Citation locator.
    pub citation: Citation,
}

/// Evidence echoed back for audit.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct Evidence {
    /// Found text.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<String>,
    /// Page where evidence was found.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub page: Option<String>,
    /// Evidence bbox.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bbox: Option<[i64; 4]>,
    /// Crop reference (L2 evidence, Milestone D).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub crop_ref: Option<String>,
}

/// One verification check (`v0001`…).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Check {
    /// Check id, `v%04d`, input citation order.
    pub id: String,
    /// The claim under check.
    pub claim: Claim,
    /// Outcome.
    pub status: CheckStatus,
    /// Stable reason for a non-grounded outcome.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reason: Option<CheckReason>,
    /// Method used.
    pub match_method: MatchMethod,
    /// True when grounding would require semantic judgment beyond the declared
    /// method. Such checks can never make `all_evidence_grounded` true.
    pub semantic_unverified: bool,
    /// Echoed evidence, when configured.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub evidence: Option<Evidence>,
    /// Per-check warnings.
    pub warnings: Vec<WarningCode>,
}

/// Grounding metadata embedded in the report.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GroundingMeta {
    /// Producing parser identity.
    pub parser: ParserIdentity,
    /// Capability declaration that drove any downgrades.
    pub capabilities: Capabilities,
}

/// The verification report (`verification_report.json`).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct VerificationReport {
    /// Report schema version.
    pub schema_version: String,
    /// Grounding document fingerprint, when declared by the source.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub document_fingerprint: Option<String>,
    /// sha256 of c14n(verification config).
    pub verification_config_sha256: String,
    /// Grounding parser + capabilities.
    pub grounding: GroundingMeta,
    /// Structured capability gaps that drove any `capability_limited` warning.
    pub capability_limits: Vec<CapabilityLimit>,
    /// Staleness outcome (citations vs grounding fingerprint).
    pub fingerprint_stale: bool,
    /// The PRD §8 gate — see [`compute_all_evidence_grounded`].
    pub all_evidence_grounded: bool,
    /// All checks, `v%04d` in input order.
    pub checks: Vec<Check>,
    /// Claim kinds present in input but unsupported. Non-empty ⇒ gate is false.
    pub unsupported_claim_kinds: Vec<String>,
    /// Report-level warnings (capability downgrades land here).
    pub warnings: Vec<WarningCode>,
}

/// The PRD §8 invariant, in one place. True only when:
/// at least one supported check exists; every supported check is `Grounded`;
/// no check is `semantic_unverified`; no unsupported claim kind is present;
/// and the fingerprint is not stale.
pub fn compute_all_evidence_grounded(
    checks: &[Check],
    unsupported_claim_kinds: &[String],
    fingerprint_stale: bool,
) -> bool {
    if fingerprint_stale || !unsupported_claim_kinds.is_empty() {
        return false;
    }
    let supported: Vec<&Check> = checks
        .iter()
        .filter(|c| c.status != CheckStatus::UnsupportedClaimKind)
        .collect();
    if supported.is_empty() {
        return false;
    }
    supported.iter().all(|c| c.status == CheckStatus::Grounded)
        && checks.iter().all(|c| !c.semantic_unverified)
}

/// Text normalization modes (config). v1 has exactly these two.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TextNormalization {
    /// Byte-exact comparison.
    None,
    /// Trim + collapse ASCII whitespace runs to one ASCII space. The only
    /// normalization in v1 (no Unicode normalization — it would alter fidelity).
    CollapseWhitespace,
}

/// Matching parameters.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Matching {
    /// Normalization applied before text comparison.
    pub text_normalization: TextNormalization,
    /// Case sensitivity of text comparison.
    pub case_sensitive: bool,
    /// Tolerance in quanta for bbox containment checks.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bbox_containment_tolerance_q: Option<i64>,
}

/// Staleness policy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Staleness {
    /// Require fingerprint equality when the source declares one.
    pub require_fingerprint_match: bool,
}

/// Resource limits.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Limits {
    /// Maximum number of checks per run.
    pub max_checks: u32,
}

/// Evidence echo options.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceOptions {
    /// Echo found evidence text into the report.
    #[serde(default)]
    pub include_text: bool,
    /// Crop-aware L2 evidence (Milestone D; requires `crop_support`).
    #[serde(default)]
    pub include_crops: bool,
}

/// The verification config (`urn:ethos:schema:verification-config:1`). Its c14n hash is
/// `verification_config_sha256` in reports — comparable runs share the hash.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VerificationConfig {
    /// Config schema version.
    pub schema_version: String,
    /// User-facing config label, e.g. `"default-v1"`.
    pub config_version: String,
    /// Supported claim kinds for this run (never `Other`).
    pub claim_kinds: Vec<ClaimKind>,
    /// Matching parameters.
    pub matching: Matching,
    /// Staleness policy.
    pub staleness: Staleness,
    /// Resource limits.
    pub limits: Limits,
    /// Evidence echo options.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub evidence: Option<EvidenceOptions>,
}

impl VerificationConfig {
    /// The pinned default config (`default-v1`), mirroring
    /// `schemas/examples/verification-config.example.json`.
    pub fn default_v1() -> Self {
        VerificationConfig {
            schema_version: crate::SCHEMA_VERSION.to_string(),
            config_version: "default-v1".to_string(),
            claim_kinds: vec![
                ClaimKind::Quote,
                ClaimKind::Value,
                ClaimKind::Presence,
                ClaimKind::TableCell,
            ],
            matching: Matching {
                text_normalization: TextNormalization::CollapseWhitespace,
                case_sensitive: true,
                bbox_containment_tolerance_q: Some(50),
            },
            staleness: Staleness {
                require_fingerprint_match: true,
            },
            limits: Limits { max_checks: 256 },
            evidence: Some(EvidenceOptions {
                include_text: true,
                include_crops: false,
            }),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn check(status: CheckStatus, semantic: bool) -> Check {
        Check {
            id: "v0001".into(),
            claim: Claim {
                kind: ClaimKind::Quote,
                text: Some("x".into()),
                citation: Citation {
                    element_id: Some("e000001".into()),
                    ..Default::default()
                },
            },
            status,
            reason: None,
            match_method: MatchMethod::ExactText,
            semantic_unverified: semantic,
            evidence: None,
            warnings: vec![],
        }
    }

    #[test]
    fn gate_requires_a_supported_grounded_check() {
        assert!(!compute_all_evidence_grounded(&[], &[], false));
        assert!(compute_all_evidence_grounded(
            &[check(CheckStatus::Grounded, false)],
            &[],
            false
        ));
        assert!(!compute_all_evidence_grounded(
            &[check(CheckStatus::Mismatch, false)],
            &[],
            false
        ));
    }

    #[test]
    fn gate_fails_on_stale_unsupported_or_semantic() {
        let g = check(CheckStatus::Grounded, false);
        assert!(!compute_all_evidence_grounded(
            std::slice::from_ref(&g),
            &[],
            true
        ));
        assert!(!compute_all_evidence_grounded(
            std::slice::from_ref(&g),
            &["arithmetic".into()],
            false
        ));
        assert!(!compute_all_evidence_grounded(
            &[check(CheckStatus::Grounded, true)],
            &[],
            false
        ));
        // unsupported-kind checks alone can never satisfy the gate
        assert!(!compute_all_evidence_grounded(
            &[check(CheckStatus::UnsupportedClaimKind, false)],
            &["other".into()],
            false
        ));
    }

    #[test]
    fn report_example_round_trips() {
        let json = include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../schemas/examples/verification-report.example.json"
        ));
        let report: VerificationReport = serde_json::from_str(json).unwrap();
        assert!(report.all_evidence_grounded);
        assert_eq!(report.checks.len(), 2);
        assert_eq!(
            report.all_evidence_grounded,
            compute_all_evidence_grounded(
                &report.checks,
                &report.unsupported_claim_kinds,
                report.fingerprint_stale
            )
        );
        // round-trip stability at the Value level
        let v1: serde_json::Value = serde_json::from_str(json).unwrap();
        let v2 = serde_json::to_value(&report).unwrap();
        assert_eq!(v1, v2);
    }

    #[test]
    fn config_example_matches_default_v1() {
        let json = include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../schemas/examples/verification-config.example.json"
        ));
        let cfg: VerificationConfig = serde_json::from_str(json).unwrap();
        assert_eq!(cfg, VerificationConfig::default_v1());
    }
}
