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

//! Verification report/config schema types (`urn:ethos:schema:verification-report:1`,
//! `urn:ethos:schema:verification-config:1`).
//!
//! Lives behind `verify-types` (no parser internals) so `ethos-verify` can use these
//! without ever seeing the canonical model or backend traits.

use std::collections::HashSet;
use std::error::Error;
use std::fmt;

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

/// Claim kinds. `Region` and `Other` appear only in citations/reports as unsupported non-v1
/// kinds, never in configs.
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
    /// Staleness policy requires a citation fingerprint, but input omitted it.
    MissingCitationFingerprint,
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
    /// method. Alpha literal checkers keep this false because unsupported or
    /// non-literal claims fail closed instead of being marked semantically checked.
    /// Such checks can never make `all_evidence_grounded` true.
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

/// Derived product-facing proof status for a [`VerificationReport`].
///
/// This is not serialized into `verification_report.json`; consumers derive it from
/// the canonical report when they need UI/API status wording.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProofStatus {
    /// The request is certified by `all_evidence_grounded=true`.
    Verified,
    /// The request is not certified, but one or more check ids are reusable.
    PartiallyVerified,
    /// No check id is reusable.
    Unverified,
}

impl ProofStatus {
    /// Stable snake_case label used by CLI and wrappers.
    pub fn as_str(self) -> &'static str {
        match self {
            ProofStatus::Verified => "verified",
            ProofStatus::PartiallyVerified => "partially_verified",
            ProofStatus::Unverified => "unverified",
        }
    }
}

/// Derived limitation labels that explain the proof status.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProofLimitation {
    /// The grounding source lacked one or more requested capabilities.
    CapabilityLimited,
    /// At least one citation fingerprint is stale relative to the source.
    StaleFingerprint,
    /// The input included claim kinds outside the active verifier/config scope.
    UnsupportedClaimKind,
    /// At least one check did not ground.
    NonGroundedChecks,
    /// At least one check would require semantic judgment beyond literal grounding.
    SemanticUnverified,
}

impl ProofLimitation {
    /// Stable snake_case label used by CLI and wrappers.
    pub fn as_str(self) -> &'static str {
        match self {
            ProofLimitation::CapabilityLimited => "capability_limited",
            ProofLimitation::StaleFingerprint => "stale_fingerprint",
            ProofLimitation::UnsupportedClaimKind => "unsupported_claim_kind",
            ProofLimitation::NonGroundedChecks => "non_grounded_checks",
            ProofLimitation::SemanticUnverified => "semantic_unverified",
        }
    }
}

/// Derived proof summary for UI/API wrappers.
///
/// The canonical [`VerificationReport`] remains the audit artifact. This summary is
/// a deterministic interpretation for product surfaces.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProofSummary {
    /// Product-facing proof status derived from the canonical report.
    pub proof_status: ProofStatus,
    /// Whether the request as submitted is certified. This mirrors `all_evidence_grounded`.
    pub request_certified: bool,
    /// Check ids that can be reused in downstream final answers.
    pub reusable_grounded_check_ids: Vec<String>,
    /// Check ids that must not be released without review or repair.
    pub needs_review_check_ids: Vec<String>,
    /// Limitations that qualify or explain the proof status.
    pub proof_limitations: Vec<ProofLimitation>,
}

/// Application-owned relevance label for an answer claim.
///
/// Ethos does not infer this label. Wrappers supply it before applying answer-release policy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AppQuestionRelevance {
    /// The grounded evidence directly answers the user question.
    DirectAnswer,
    /// The grounded evidence supports the answer but is not sufficient alone.
    SupportsAnswer,
    /// The grounded evidence is true but only background for the question.
    BackgroundOnly,
    /// The grounded evidence does not support the requested answer.
    Unrelated,
}

impl AppQuestionRelevance {
    /// Stable snake_case label used by wrapper envelopes.
    pub fn as_str(self) -> &'static str {
        match self {
            AppQuestionRelevance::DirectAnswer => "direct_answer",
            AppQuestionRelevance::SupportsAnswer => "supports_answer",
            AppQuestionRelevance::BackgroundOnly => "background_only",
            AppQuestionRelevance::Unrelated => "unrelated",
        }
    }
}

/// Application-owned source/synthesis label for an answer claim.
///
/// Ethos does not infer this label. Wrappers supply it before applying answer-release policy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AppClaimType {
    /// The claim is directly stated by source evidence.
    SourceFact,
    /// The claim combines multiple grounded facts or adds reasoning across them.
    Synthesis,
    /// The claim cannot be traced to grounded source evidence.
    Unsupported,
}

impl AppClaimType {
    /// Stable snake_case label used by wrapper envelopes.
    pub fn as_str(self) -> &'static str {
        match self {
            AppClaimType::SourceFact => "source_fact",
            AppClaimType::Synthesis => "synthesis",
            AppClaimType::Unsupported => "unsupported",
        }
    }
}

/// Application answer release action for a claim.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AppReleaseAction {
    /// Release the claim in the final answer.
    ShowFinal,
    /// Keep the claim in a review surface.
    NeedsReview,
    /// Keep the claim out of the final answer.
    Block,
}

impl AppReleaseAction {
    /// Stable snake_case label used by wrapper envelopes.
    pub fn as_str(self) -> &'static str {
        match self {
            AppReleaseAction::ShowFinal => "show_final",
            AppReleaseAction::NeedsReview => "needs_review",
            AppReleaseAction::Block => "block",
        }
    }
}

/// Stable reason for an application answer release action.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AppReleaseReason {
    /// The claim is a grounded relevant source fact and can enter the final answer.
    Certified,
    /// The claim is grounded and relevant, but is synthesis that needs review.
    SupportedSynthesisNeedsReview,
    /// The claim is citation-grounded but not relevant to the user question.
    GroundedButIrrelevant,
    /// The sources do not provide a releasable answer claim.
    CannotAnswerFromSources,
}

impl AppReleaseReason {
    /// Stable snake_case label used by wrapper envelopes.
    pub fn as_str(self) -> &'static str {
        match self {
            AppReleaseReason::Certified => "certified",
            AppReleaseReason::SupportedSynthesisNeedsReview => "supported_synthesis_needs_review",
            AppReleaseReason::GroundedButIrrelevant => "grounded_but_irrelevant",
            AppReleaseReason::CannotAnswerFromSources => "cannot_answer_from_sources",
        }
    }
}

/// Application-level answer status after applying grounding, relevance, and synthesis policy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AppAnswerStatus {
    /// Every submitted claim is releasable as a grounded relevant source fact.
    Certified,
    /// At least one claim is releasable, but some submitted claims are blocked or review-only.
    PartialCertified,
    /// No final claim is releasable, but grounded relevant synthesis exists for review.
    SupportedSynthesisNeedsReview,
    /// Grounded claims exist, but they are not relevant to the question.
    GroundedButIrrelevant,
    /// No relevant grounded source fact is available for final answer release.
    CannotAnswerFromSources,
}

impl AppAnswerStatus {
    /// Stable snake_case label used by wrapper envelopes.
    pub fn as_str(self) -> &'static str {
        match self {
            AppAnswerStatus::Certified => "certified",
            AppAnswerStatus::PartialCertified => "partial_certified",
            AppAnswerStatus::SupportedSynthesisNeedsReview => "supported_synthesis_needs_review",
            AppAnswerStatus::GroundedButIrrelevant => "grounded_but_irrelevant",
            AppAnswerStatus::CannotAnswerFromSources => "cannot_answer_from_sources",
        }
    }
}

/// Caller-supplied claim labels used to derive an application answer release decision.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AppAnswerClaimInput {
    /// Stable application claim id.
    pub id: String,
    /// Claim text being considered for release.
    pub text: String,
    /// Ethos verification check ids backing this claim.
    pub check_ids: Vec<String>,
    /// Optional caller-supplied grounding flag for claims without check ids.
    pub citation_grounded: Option<bool>,
    /// App-owned question relevance label.
    pub question_relevance: AppQuestionRelevance,
    /// App-owned source/synthesis label.
    pub claim_type: AppClaimType,
}

/// Claim-level decision inside an application answer release envelope.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppAnswerClaimDecision {
    /// Stable application claim id.
    pub id: String,
    /// Claim text being considered for release.
    pub text: String,
    /// Ethos verification check ids backing this claim.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub check_ids: Vec<String>,
    /// Whether the claim's cited Ethos checks are grounded and reusable.
    pub citation_grounded: bool,
    /// App-owned question relevance label.
    pub question_relevance: AppQuestionRelevance,
    /// App-owned source/synthesis label.
    pub claim_type: AppClaimType,
    /// Application release action.
    pub release_action: AppReleaseAction,
    /// Stable reason for the release action.
    pub release_reason: AppReleaseReason,
}

/// Grounding section embedded in an application answer release decision envelope.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppAnswerGrounding {
    /// Application-local pointer to the canonical `verification_report.json` used for audit.
    pub verification_report_ref: String,
    /// Product-facing proof status derived from the canonical report.
    pub proof_status: ProofStatus,
    /// Whether the request as submitted is certified.
    pub request_certified: bool,
    /// Check ids that can be reused in downstream final answers.
    pub reusable_grounded_check_ids: Vec<String>,
    /// Check ids that must not be released without review or repair.
    pub needs_review_check_ids: Vec<String>,
    /// Limitations that qualify or explain the proof status.
    pub proof_limitations: Vec<ProofLimitation>,
}

/// Non-canonical app answer release decision envelope.
///
/// This is a wrapper artifact above Ethos grounding. It is not `verification_report.json`.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AppAnswerReleaseDecision {
    /// Artifact type discriminator.
    pub artifact_type: String,
    /// Schema version for the wrapper envelope.
    pub schema_version: String,
    /// Original user question evaluated by the app-layer relevance policy.
    pub question: String,
    /// Derived Ethos proof summary plus the audit report reference.
    pub grounding: AppAnswerGrounding,
    /// Application-level answer status.
    pub app_status: AppAnswerStatus,
    /// Claim-level release decisions.
    pub claims: Vec<AppAnswerClaimDecision>,
    /// Claim ids that may enter the final answer.
    pub final_answer_claim_ids: Vec<String>,
    /// Claim ids that should be held for review.
    pub review_claim_ids: Vec<String>,
    /// Claim ids that should be blocked from the final answer.
    pub blocked_claim_ids: Vec<String>,
    /// Optional application notes.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub notes: Vec<String>,
}

/// Error returned when application answer release inputs are inconsistent.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AppAnswerReleaseError {
    message: String,
}

impl AppAnswerReleaseError {
    /// Human-readable validation message.
    pub fn message(&self) -> &str {
        &self.message
    }
}

impl fmt::Display for AppAnswerReleaseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.message)
    }
}

impl Error for AppAnswerReleaseError {}

impl VerificationReport {
    /// Derive a product-facing proof summary from this canonical report.
    pub fn proof_summary(&self) -> ProofSummary {
        derive_proof_summary(self)
    }
}

/// Derive a product-facing proof summary from a canonical verification report.
pub fn derive_proof_summary(report: &VerificationReport) -> ProofSummary {
    let mut reusable_grounded_check_ids = Vec::new();
    let mut needs_review_check_ids = Vec::new();
    for check in &report.checks {
        if is_reusable_grounded_check(report, check) {
            reusable_grounded_check_ids.push(check.id.clone());
        } else {
            needs_review_check_ids.push(check.id.clone());
        }
    }
    let request_certified = report.all_evidence_grounded;
    let proof_status = if request_certified {
        ProofStatus::Verified
    } else if reusable_grounded_check_ids.is_empty() {
        ProofStatus::Unverified
    } else {
        ProofStatus::PartiallyVerified
    };

    let mut proof_limitations = Vec::new();
    if has_capability_limit(report) {
        proof_limitations.push(ProofLimitation::CapabilityLimited);
    }
    if report.fingerprint_stale {
        proof_limitations.push(ProofLimitation::StaleFingerprint);
    }
    if !report.unsupported_claim_kinds.is_empty() {
        proof_limitations.push(ProofLimitation::UnsupportedClaimKind);
    }
    if report
        .checks
        .iter()
        .any(|check| check.status != CheckStatus::Grounded)
    {
        proof_limitations.push(ProofLimitation::NonGroundedChecks);
    }
    if report.checks.iter().any(|check| check.semantic_unverified) {
        proof_limitations.push(ProofLimitation::SemanticUnverified);
    }

    ProofSummary {
        proof_status,
        request_certified,
        reusable_grounded_check_ids,
        needs_review_check_ids,
        proof_limitations,
    }
}

/// Return whether a check is safe to reuse from a partially certified report.
///
/// Stale fingerprints are a report-level invalidator, so even a grounded check is
/// not reusable when `report.fingerprint_stale=true`.
pub fn is_reusable_grounded_check(report: &VerificationReport, check: &Check) -> bool {
    !report.fingerprint_stale && check.status == CheckStatus::Grounded && !check.semantic_unverified
}

/// Derive a non-canonical application answer release decision from a proof summary.
///
/// The caller supplies relevance and synthesis labels. This helper only applies the release policy
/// from `docs/app-answer-release-contract.md` and checks that referenced Ethos check ids are known
/// and reusable before a claim enters the final answer.
pub fn derive_app_answer_release_decision(
    question: impl Into<String>,
    proof: &ProofSummary,
    claims: Vec<AppAnswerClaimInput>,
    verification_report_ref: impl Into<String>,
    notes: Vec<String>,
) -> Result<AppAnswerReleaseDecision, AppAnswerReleaseError> {
    let question = question.into();
    if question.trim().is_empty() {
        return Err(app_answer_release_error(
            "question must be a non-empty string",
        ));
    }
    let verification_report_ref = verification_report_ref.into();
    if verification_report_ref.is_empty() {
        return Err(app_answer_release_error(
            "verification_report_ref must be a non-empty string",
        ));
    }
    for note in &notes {
        if note.is_empty() {
            return Err(app_answer_release_error(
                "notes must contain only non-empty strings",
            ));
        }
    }

    let reusable_check_ids: HashSet<&str> = proof
        .reusable_grounded_check_ids
        .iter()
        .map(String::as_str)
        .collect();
    let needs_review_check_ids: HashSet<&str> = proof
        .needs_review_check_ids
        .iter()
        .map(String::as_str)
        .collect();
    let known_check_ids: HashSet<&str> = reusable_check_ids
        .union(&needs_review_check_ids)
        .copied()
        .collect();

    let mut seen_claim_ids = HashSet::new();
    let mut decisions = Vec::with_capacity(claims.len());
    for claim in claims {
        decisions.push(app_answer_claim_decision(
            claim,
            &reusable_check_ids,
            &known_check_ids,
            &mut seen_claim_ids,
        )?);
    }

    let final_answer_claim_ids = decisions
        .iter()
        .filter(|claim| claim.release_action == AppReleaseAction::ShowFinal)
        .map(|claim| claim.id.clone())
        .collect();
    let review_claim_ids = decisions
        .iter()
        .filter(|claim| claim.release_action == AppReleaseAction::NeedsReview)
        .map(|claim| claim.id.clone())
        .collect();
    let blocked_claim_ids = decisions
        .iter()
        .filter(|claim| claim.release_action == AppReleaseAction::Block)
        .map(|claim| claim.id.clone())
        .collect();
    let app_status = app_answer_status(&decisions);

    Ok(AppAnswerReleaseDecision {
        artifact_type: "ethos.app_answer_release_decision.v1".to_string(),
        schema_version: "1.0.0".to_string(),
        question,
        grounding: AppAnswerGrounding {
            verification_report_ref,
            proof_status: proof.proof_status,
            request_certified: proof.request_certified,
            reusable_grounded_check_ids: proof.reusable_grounded_check_ids.clone(),
            needs_review_check_ids: proof.needs_review_check_ids.clone(),
            proof_limitations: proof.proof_limitations.clone(),
        },
        app_status,
        claims: decisions,
        final_answer_claim_ids,
        review_claim_ids,
        blocked_claim_ids,
        notes,
    })
}

fn has_capability_limit(report: &VerificationReport) -> bool {
    !report.capability_limits.is_empty()
        || report.warnings.contains(&WarningCode::CapabilityLimited)
        || report
            .checks
            .iter()
            .any(|check| check.warnings.contains(&WarningCode::CapabilityLimited))
}

fn app_answer_claim_decision(
    claim: AppAnswerClaimInput,
    reusable_check_ids: &HashSet<&str>,
    known_check_ids: &HashSet<&str>,
    seen_claim_ids: &mut HashSet<String>,
) -> Result<AppAnswerClaimDecision, AppAnswerReleaseError> {
    if claim.id.is_empty() {
        return Err(app_answer_release_error(
            "claim id must be a non-empty string",
        ));
    }
    if !seen_claim_ids.insert(claim.id.clone()) {
        return Err(app_answer_release_error(format!(
            "duplicate claim id: {}",
            claim.id
        )));
    }
    if claim.text.is_empty() {
        return Err(app_answer_release_error(format!(
            "claim {} text must be a non-empty string",
            claim.id
        )));
    }
    let mut seen_check_ids = HashSet::new();
    for check_id in &claim.check_ids {
        if check_id.is_empty() {
            return Err(app_answer_release_error(format!(
                "claim {} check_ids must contain only non-empty strings",
                claim.id
            )));
        }
        if !seen_check_ids.insert(check_id.as_str()) {
            return Err(app_answer_release_error(format!(
                "claim {} has duplicate check id: {}",
                claim.id, check_id
            )));
        }
    }

    let citation_grounded = if claim.check_ids.is_empty() {
        claim.citation_grounded.ok_or_else(|| {
            app_answer_release_error(format!(
                "claim {} without check_ids must set citation_grounded",
                claim.id
            ))
        })?
    } else {
        let mut computed = true;
        for check_id in &claim.check_ids {
            if !known_check_ids.contains(check_id.as_str()) {
                return Err(app_answer_release_error(format!(
                    "claim {} references unknown check id: {}",
                    claim.id, check_id
                )));
            }
            if !reusable_check_ids.contains(check_id.as_str()) {
                computed = false;
            }
        }
        if let Some(provided) = claim.citation_grounded {
            if provided != computed {
                return Err(app_answer_release_error(format!(
                    "citation_grounded for claim {} conflicts with proof summary",
                    claim.id
                )));
            }
        }
        computed
    };
    if claim.claim_type == AppClaimType::Unsupported && citation_grounded {
        return Err(app_answer_release_error(format!(
            "unsupported claim {} cannot be citation_grounded",
            claim.id
        )));
    }

    let (release_action, release_reason) = app_release_decision(
        citation_grounded,
        claim.question_relevance,
        claim.claim_type,
    );
    Ok(AppAnswerClaimDecision {
        id: claim.id,
        text: claim.text,
        check_ids: claim.check_ids,
        citation_grounded,
        question_relevance: claim.question_relevance,
        claim_type: claim.claim_type,
        release_action,
        release_reason,
    })
}

fn app_release_decision(
    citation_grounded: bool,
    question_relevance: AppQuestionRelevance,
    claim_type: AppClaimType,
) -> (AppReleaseAction, AppReleaseReason) {
    if citation_grounded
        && matches!(
            question_relevance,
            AppQuestionRelevance::DirectAnswer | AppQuestionRelevance::SupportsAnswer
        )
        && claim_type == AppClaimType::SourceFact
    {
        return (AppReleaseAction::ShowFinal, AppReleaseReason::Certified);
    }
    if citation_grounded
        && matches!(
            question_relevance,
            AppQuestionRelevance::DirectAnswer | AppQuestionRelevance::SupportsAnswer
        )
        && claim_type == AppClaimType::Synthesis
    {
        return (
            AppReleaseAction::NeedsReview,
            AppReleaseReason::SupportedSynthesisNeedsReview,
        );
    }
    if citation_grounded {
        return (
            AppReleaseAction::Block,
            AppReleaseReason::GroundedButIrrelevant,
        );
    }
    (
        AppReleaseAction::Block,
        AppReleaseReason::CannotAnswerFromSources,
    )
}

fn app_answer_status(claims: &[AppAnswerClaimDecision]) -> AppAnswerStatus {
    let has_final = claims
        .iter()
        .any(|claim| claim.release_action == AppReleaseAction::ShowFinal);
    let has_review = claims
        .iter()
        .any(|claim| claim.release_action == AppReleaseAction::NeedsReview);
    let has_blocked = claims
        .iter()
        .any(|claim| claim.release_action == AppReleaseAction::Block);

    if has_final && !has_review && !has_blocked {
        AppAnswerStatus::Certified
    } else if has_final {
        AppAnswerStatus::PartialCertified
    } else if has_review {
        AppAnswerStatus::SupportedSynthesisNeedsReview
    } else if claims
        .iter()
        .any(|claim| claim.release_reason == AppReleaseReason::GroundedButIrrelevant)
    {
        AppAnswerStatus::GroundedButIrrelevant
    } else {
        AppAnswerStatus::CannotAnswerFromSources
    }
}

fn app_answer_release_error(message: impl Into<String>) -> AppAnswerReleaseError {
    AppAnswerReleaseError {
        message: message.into(),
    }
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
    /// Supported claim kinds for this run. Configs accept only the four v1 literal kinds:
    /// quote, value, presence, and table_cell.
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
        check_with_id("v0001", status, semantic)
    }

    fn check_with_id(id: &str, status: CheckStatus, semantic: bool) -> Check {
        Check {
            id: id.into(),
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

    fn report(checks: Vec<Check>) -> VerificationReport {
        VerificationReport {
            schema_version: crate::SCHEMA_VERSION.to_string(),
            document_fingerprint: Some(
                "sha256:7164f43f104dc248193f12ea828e0ab857eae194210114c6f6c0160fd643c87b"
                    .to_string(),
            ),
            verification_config_sha256: "0".repeat(64),
            grounding: GroundingMeta {
                parser: ParserIdentity {
                    name: "ethos".to_string(),
                    version: "0.1.0".to_string(),
                    adapter: None,
                    adapter_version: None,
                },
                capabilities: Capabilities {
                    spans: true,
                    char_offsets: true,
                    tables: true,
                    fingerprint: true,
                    coordinate_origin: crate::grounding::CoordinateOrigin::TopLeft,
                    crop_support: true,
                },
            },
            capability_limits: Vec::new(),
            fingerprint_stale: false,
            all_evidence_grounded: true,
            checks,
            unsupported_claim_kinds: Vec::new(),
            warnings: Vec::new(),
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
    fn proof_summary_keeps_capability_limit_visible_without_failing_certified_request() {
        let mut report = report(vec![check(CheckStatus::Grounded, false)]);
        report.capability_limits = vec![CapabilityLimit::MissingFingerprint];
        report.warnings = vec![WarningCode::CapabilityLimited];

        let proof = derive_proof_summary(&report);

        assert_eq!(proof.proof_status, ProofStatus::Verified);
        assert!(proof.request_certified);
        assert_eq!(proof.reusable_grounded_check_ids, vec!["v0001"]);
        assert!(proof.needs_review_check_ids.is_empty());
        assert_eq!(
            proof.proof_limitations,
            vec![ProofLimitation::CapabilityLimited]
        );
    }

    #[test]
    fn proof_summary_marks_mixed_reports_as_partially_verified_without_certifying_request() {
        let mut unsupported = check_with_id("v0002", CheckStatus::UnsupportedClaimKind, false);
        unsupported.reason = Some(CheckReason::UnsupportedClaimKind);
        unsupported.match_method = MatchMethod::None;
        let mut report = report(vec![
            check_with_id("v0001", CheckStatus::Grounded, false),
            unsupported,
        ]);
        report.all_evidence_grounded = false;
        report.unsupported_claim_kinds = vec!["region".to_string()];

        let proof = report.proof_summary();

        assert_eq!(proof.proof_status, ProofStatus::PartiallyVerified);
        assert!(!proof.request_certified);
        assert_eq!(proof.reusable_grounded_check_ids, vec!["v0001"]);
        assert_eq!(proof.needs_review_check_ids, vec!["v0002"]);
        assert_eq!(
            proof.proof_limitations,
            vec![
                ProofLimitation::UnsupportedClaimKind,
                ProofLimitation::NonGroundedChecks
            ]
        );
    }

    #[test]
    fn proof_summary_excludes_grounded_checks_when_fingerprint_is_stale() {
        let mut report = report(vec![check(CheckStatus::Grounded, false)]);
        report.fingerprint_stale = true;
        report.all_evidence_grounded = false;

        let proof = report.proof_summary();

        assert_eq!(proof.proof_status, ProofStatus::Unverified);
        assert!(!proof.request_certified);
        assert!(proof.reusable_grounded_check_ids.is_empty());
        assert_eq!(proof.needs_review_check_ids, vec!["v0001"]);
        assert_eq!(
            proof.proof_limitations,
            vec![ProofLimitation::StaleFingerprint]
        );
    }

    #[test]
    fn proof_summary_excludes_semantic_unverified_grounded_checks() {
        let mut report = report(vec![check(CheckStatus::Grounded, true)]);
        report.all_evidence_grounded = false;

        let proof = report.proof_summary();

        assert_eq!(proof.proof_status, ProofStatus::Unverified);
        assert!(proof.reusable_grounded_check_ids.is_empty());
        assert_eq!(proof.needs_review_check_ids, vec!["v0001"]);
        assert_eq!(
            proof.proof_limitations,
            vec![ProofLimitation::SemanticUnverified]
        );
    }

    #[test]
    fn app_answer_release_decision_applies_relevance_and_synthesis_policy() {
        let proof = ProofSummary {
            proof_status: ProofStatus::PartiallyVerified,
            request_certified: false,
            reusable_grounded_check_ids: vec![
                "v0001".to_string(),
                "v0002".to_string(),
                "v0003".to_string(),
            ],
            needs_review_check_ids: vec!["v0004".to_string()],
            proof_limitations: vec![ProofLimitation::NonGroundedChecks],
        };

        let decision = derive_app_answer_release_decision(
            "What was Q3 2025 revenue?",
            &proof,
            vec![
                AppAnswerClaimInput {
                    id: "claim-revenue".to_string(),
                    text: "Revenue grew to $12.4M in Q3 2025.".to_string(),
                    check_ids: vec!["v0001".to_string()],
                    citation_grounded: None,
                    question_relevance: AppQuestionRelevance::DirectAnswer,
                    claim_type: AppClaimType::SourceFact,
                },
                AppAnswerClaimInput {
                    id: "claim-background".to_string(),
                    text: "The company opened a European office.".to_string(),
                    check_ids: vec!["v0002".to_string()],
                    citation_grounded: None,
                    question_relevance: AppQuestionRelevance::BackgroundOnly,
                    claim_type: AppClaimType::SourceFact,
                },
                AppAnswerClaimInput {
                    id: "claim-synthesis".to_string(),
                    text: "Revenue growth was likely driven by enterprise expansion.".to_string(),
                    check_ids: vec!["v0001".to_string(), "v0003".to_string()],
                    citation_grounded: None,
                    question_relevance: AppQuestionRelevance::SupportsAnswer,
                    claim_type: AppClaimType::Synthesis,
                },
                AppAnswerClaimInput {
                    id: "claim-margin".to_string(),
                    text: "Gross margin improved in Q3 2025.".to_string(),
                    check_ids: vec!["v0004".to_string()],
                    citation_grounded: None,
                    question_relevance: AppQuestionRelevance::DirectAnswer,
                    claim_type: AppClaimType::Unsupported,
                },
            ],
            "reports/q3-verification.json",
            vec!["application-owned relevance labels".to_string()],
        )
        .unwrap();

        assert_eq!(
            decision.artifact_type,
            "ethos.app_answer_release_decision.v1"
        );
        assert_eq!(decision.app_status, AppAnswerStatus::PartialCertified);
        assert_eq!(
            decision.grounding.verification_report_ref,
            "reports/q3-verification.json"
        );
        assert_eq!(decision.final_answer_claim_ids, vec!["claim-revenue"]);
        assert_eq!(decision.review_claim_ids, vec!["claim-synthesis"]);
        assert_eq!(
            decision.blocked_claim_ids,
            vec!["claim-background", "claim-margin"]
        );
        assert_eq!(
            decision.claims[0].release_reason,
            AppReleaseReason::Certified
        );
        assert!(decision.claims[0].citation_grounded);
        assert_eq!(
            decision.claims[1].release_reason,
            AppReleaseReason::GroundedButIrrelevant
        );
        assert_eq!(
            decision.claims[2].release_action,
            AppReleaseAction::NeedsReview
        );
        assert_eq!(decision.claims[2].check_ids, vec!["v0001", "v0003"]);
        assert!(!decision.claims[3].citation_grounded);
        assert_eq!(
            decision.claims[3].release_reason,
            AppReleaseReason::CannotAnswerFromSources
        );
        assert_eq!(decision.notes, vec!["application-owned relevance labels"]);

        let json = serde_json::to_value(&decision).unwrap();
        assert_eq!(
            json["artifact_type"],
            serde_json::Value::String("ethos.app_answer_release_decision.v1".to_string())
        );
        assert_eq!(json["claims"][2]["check_ids"][1], "v0003");
    }

    #[test]
    fn app_answer_release_decision_blocks_empty_source_answer() {
        let proof = ProofSummary {
            proof_status: ProofStatus::Unverified,
            request_certified: false,
            reusable_grounded_check_ids: Vec::new(),
            needs_review_check_ids: Vec::new(),
            proof_limitations: Vec::new(),
        };

        let decision = derive_app_answer_release_decision(
            "What was Q3 2025 revenue?",
            &proof,
            Vec::new(),
            "verification_report.json",
            Vec::new(),
        )
        .unwrap();

        assert_eq!(
            decision.app_status,
            AppAnswerStatus::CannotAnswerFromSources
        );
        assert!(decision.final_answer_claim_ids.is_empty());
        assert!(decision.review_claim_ids.is_empty());
        assert!(decision.blocked_claim_ids.is_empty());
    }

    #[test]
    fn app_answer_release_decision_rejects_conflicting_or_unknown_checks() {
        let proof = ProofSummary {
            proof_status: ProofStatus::PartiallyVerified,
            request_certified: false,
            reusable_grounded_check_ids: vec!["v0001".to_string()],
            needs_review_check_ids: vec!["v0002".to_string()],
            proof_limitations: vec![ProofLimitation::NonGroundedChecks],
        };

        let conflicting = derive_app_answer_release_decision(
            "What was Q3 2025 revenue?",
            &proof,
            vec![AppAnswerClaimInput {
                id: "claim-bad".to_string(),
                text: "Revenue grew.".to_string(),
                check_ids: vec!["v0001".to_string()],
                citation_grounded: Some(false),
                question_relevance: AppQuestionRelevance::DirectAnswer,
                claim_type: AppClaimType::SourceFact,
            }],
            "verification_report.json",
            Vec::new(),
        )
        .unwrap_err();
        assert!(conflicting
            .message()
            .contains("conflicts with proof summary"));

        let unknown = derive_app_answer_release_decision(
            "What was Q3 2025 revenue?",
            &proof,
            vec![AppAnswerClaimInput {
                id: "claim-unknown".to_string(),
                text: "Revenue grew.".to_string(),
                check_ids: vec!["v9999".to_string()],
                citation_grounded: None,
                question_relevance: AppQuestionRelevance::DirectAnswer,
                claim_type: AppClaimType::SourceFact,
            }],
            "verification_report.json",
            Vec::new(),
        )
        .unwrap_err();
        assert!(unknown.message().contains("unknown check id: v9999"));
    }

    #[test]
    fn app_answer_release_decision_rejects_duplicate_claim_ids() {
        let proof = ProofSummary {
            proof_status: ProofStatus::PartiallyVerified,
            request_certified: false,
            reusable_grounded_check_ids: vec!["v0001".to_string(), "v0002".to_string()],
            needs_review_check_ids: Vec::new(),
            proof_limitations: Vec::new(),
        };

        let duplicate = derive_app_answer_release_decision(
            "What was Q3 2025 revenue?",
            &proof,
            vec![
                AppAnswerClaimInput {
                    id: "claim-revenue".to_string(),
                    text: "Revenue grew.".to_string(),
                    check_ids: vec!["v0001".to_string()],
                    citation_grounded: None,
                    question_relevance: AppQuestionRelevance::DirectAnswer,
                    claim_type: AppClaimType::SourceFact,
                },
                AppAnswerClaimInput {
                    id: "claim-revenue".to_string(),
                    text: "Revenue increased.".to_string(),
                    check_ids: vec!["v0002".to_string()],
                    citation_grounded: None,
                    question_relevance: AppQuestionRelevance::SupportsAnswer,
                    claim_type: AppClaimType::SourceFact,
                },
            ],
            "verification_report.json",
            Vec::new(),
        )
        .unwrap_err();

        assert!(duplicate
            .message()
            .contains("duplicate claim id: claim-revenue"));
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
