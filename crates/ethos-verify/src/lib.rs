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

mod anchor;

pub use anchor::*;

use std::collections::{BTreeMap, BTreeSet};

use ethos_core::codes::WarningCode;
use ethos_core::grounding::{
    CoordinateOrigin, GroundingCell, GroundingElement, GroundingSource, GroundingSpan,
    GroundingTable, PageGeometry,
};
use ethos_core::verify_types::{
    compute_all_evidence_grounded, Attestation, CapabilityLimit, Check, CheckProvenance,
    CheckReason, CheckStatus, Claim, ClaimKind, ContextBoundary, ContextEcho, Evidence,
    EvidenceDispersion, EvidenceTier, GroundingMeta, MatchMethod, NearestMatch, ProvenanceStatus,
    TextNormalization, VerificationConfig, VerificationReport, VerifierIdentity,
    HARDENED_VERIFICATION_SCHEMA_VERSION,
};
use serde::{Deserialize, Serialize};

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
    claims_sha256: String,
) -> VerificationReport {
    let index = SourceIndex::for_verification(source, config);
    verify_claims_indexed(
        source,
        &index,
        citations,
        config,
        config_sha256,
        claims_sha256,
    )
}

/// [`verify_claims`] over a prebuilt [`SourceIndex::for_verification`] index. The
/// convenience wrapper builds the index per call, which is right for one request;
/// a batch caller passes the same index to every request so the document is
/// cloned, id-indexed, and text-normalized once per batch instead of once per
/// line. The index must have been built from the same source and config, or the
/// caches lie — the wrapper is the safe path, this is the fast one.
pub fn verify_claims_indexed(
    source: &dyn GroundingSource,
    index: &SourceIndex,
    citations: CitationInput,
    config: &VerificationConfig,
    config_sha256: String,
    claims_sha256: String,
) -> VerificationReport {
    // The doc comment above states the caller's obligation; this enforces it.
    //
    // The index caches text normalized under the config it was built for, and the
    // page scan compares against those cached strings. Hand this function an index
    // built under a different normalization — or one from `SourceIndex::new`, which
    // carries no caches at all — and the comparison silently runs against strings
    // normalized by rules the caller did not ask for. That is a wrong verdict
    // produced by a caching detail, and it was reachable through a `pub` function
    // whose only guard was a sentence in prose.
    //
    // A mismatch REBUILDS rather than panics or returns an error. The signature
    // returns a report, not a `Result`, and this is a performance shortcut: the
    // honest failure mode for a shortcut used wrongly is to lose the speed, never
    // the correctness. A correct caller is untouched and still pays for one index
    // per batch; an incorrect one silently gets the right answer slowly, which is
    // what the safe wrapper would have given it.
    let rebuilt;
    let index = if index.normalized_for == Some(SourceIndex::normalization_key(config))
        && index.built_from == source.fingerprint()
    {
        index
    } else {
        rebuilt = SourceIndex::for_verification(source, config);
        &rebuilt
    };
    let (citation_fingerprint, claims) = citations.into_parts();
    let source_fingerprint = source.fingerprint();
    let mut capability_limits = capability_limits_for(index.capabilities, config);
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
    let hardening = config.hardening.filter(|options| options.enabled());
    let mut unsupported = Vec::new();
    let checks: Vec<Check> = claims
        .into_iter()
        .enumerate()
        .map(|(idx, claim)| {
            check_claim(
                idx + 1,
                source,
                index,
                claim,
                config,
                CheckContext {
                    fingerprint_stale,
                    fingerprint_unverifiable,
                    citation_fingerprint_missing,
                    include_text,
                    include_crops,
                    emit_hardening: hardening.is_some(),
                    include_provenance: hardening.is_some_and(|o| o.include_provenance),
                    include_context_echo: hardening.is_some_and(|o| o.include_context_echo),
                    context_window_chars: hardening.map_or(0, |o| o.context_window_chars),
                    include_nearest_match: hardening.is_some_and(|o| o.include_nearest_match),
                },
                &mut unsupported,
            )
        })
        .collect();

    if checks.iter().any(|check| {
        check
            .provenance
            .as_ref()
            .is_some_and(|provenance| provenance.status == ProvenanceStatus::CapabilityLimited)
    }) && !capability_limits.contains(&CapabilityLimit::MissingStructure)
    {
        capability_limits.push(CapabilityLimit::MissingStructure);
    }
    let warnings = if capability_limits.is_empty() {
        Vec::new()
    } else {
        vec![WarningCode::CapabilityLimited]
    };
    let dispersion = hardening
        .filter(|options| options.include_dispersion)
        .map(|options| {
            evidence_dispersion(
                source,
                &checks,
                fingerprint_stale,
                options.include_provenance,
            )
        });

    VerificationReport {
        schema_version: if hardening.is_some() {
            HARDENED_VERIFICATION_SCHEMA_VERSION.to_string()
        } else {
            ethos_core::SCHEMA_VERSION.to_string()
        },
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
        dispersion,
        unsupported_claim_kinds: unsupported,
        attestation: Attestation {
            // The verifier's own crate identity, not the caller's, so a library consumer
            // gets the same attestation a CLI user does.
            verifier: VerifierIdentity {
                name: env!("CARGO_PKG_NAME").to_string(),
                version: env!("CARGO_PKG_VERSION").to_string(),
            },
            config_version: config.config_version.clone(),
            claims_sha256,
        },
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
    emit_hardening: bool,
    include_provenance: bool,
    include_context_echo: bool,
    context_window_chars: u32,
    include_nearest_match: bool,
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
            nearest_match: None,
            evidence: None,
            evidence_tier: None,
            resolved_element_ids: Vec::new(),
            provenance: None,
            context_echo: None,
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
            nearest_match: None,
            evidence: None,
            evidence_tier: None,
            resolved_element_ids: Vec::new(),
            provenance: None,
            context_echo: None,
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
            nearest_match: None,
            evidence: None,
            evidence_tier: None,
            resolved_element_ids: Vec::new(),
            provenance: None,
            context_echo: None,
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
            nearest_match: None,
            evidence: None,
            evidence_tier: None,
            resolved_element_ids: Vec::new(),
            provenance: None,
            context_echo: None,
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
            nearest_match: None,
            evidence: None,
            evidence_tier: None,
            resolved_element_ids: Vec::new(),
            provenance: None,
            context_echo: None,
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
            nearest_match: None,
            evidence: None,
            evidence_tier: None,
            resolved_element_ids: Vec::new(),
            provenance: None,
            context_echo: None,
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
                nearest_match: None,
                evidence: None,
                evidence_tier: None,
                resolved_element_ids: Vec::new(),
                provenance: None,
                context_echo: None,
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
                nearest_match: None,
                evidence: None,
                evidence_tier: None,
                resolved_element_ids: Vec::new(),
                provenance: None,
                context_echo: None,
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
                nearest_match: None,
                evidence: None,
                evidence_tier: None,
                resolved_element_ids: Vec::new(),
                provenance: None,
                context_echo: None,
                warnings,
            };
        }
    };

    match adjacent_quote_target(index, &claim, &target, config) {
        Ok(Some(adjacent_target)) => target = adjacent_target,
        Ok(None) => {}
        Err(reason) => {
            push_warning(&mut warnings, WarningCode::CapabilityLimited);
            return Check {
                id: check_id,
                claim,
                status: CheckStatus::CapabilityBlocked,
                reason: Some(reason),
                match_method: MatchMethod::None,
                semantic_unverified: false,
                nearest_match: None,
                evidence: None,
                evidence_tier: None,
                resolved_element_ids: Vec::new(),
                provenance: None,
                context_echo: None,
                warnings,
            };
        }
    }

    let evidence = make_evidence(source, &target, context.include_text, context.include_crops);
    let (status, match_method, reason) =
        check_resolved_claim(claim.kind, claim.text.as_deref(), &target, config);
    let provenance = context
        .include_provenance
        .then(|| check_provenance(source, &target));
    if provenance
        .as_ref()
        .is_some_and(|provenance| provenance.status == ProvenanceStatus::CapabilityLimited)
    {
        push_warning(&mut warnings, WarningCode::CapabilityLimited);
    }
    let context_echo = (context.include_context_echo && status == CheckStatus::Grounded)
        .then(|| {
            context_echo(
                claim.kind,
                claim.text.as_deref(),
                &target,
                config,
                context.context_window_chars,
            )
        })
        .flatten();
    // The tier the target actually resolved at. A check decided by a capability limit never
    // reaches here: every capability path returns early with `evidence_tier: None` and
    // `CheckStatus::CapabilityBlocked`, which already carries the fact. A tier value that
    // duplicated a status value would be two fields describing one thing, which is how they
    // start disagreeing.
    let evidence_tier = Some(target.tier);
    let nearest_match = (context.include_nearest_match
        && requires_text(claim.kind)
        && status != CheckStatus::Grounded)
        .then(|| nearest_match_for(index, &claim, config))
        .flatten();
    // The one deterministic semantic_unverified producer: a grounded text match
    // whose target is a sanctioned adjacent-element join. The quote is literally
    // present, but only as an assembly of two elements whose continuity was
    // inferred from geometry — no single element states it — so meaning was not
    // effectively checked by the literal method the report names. Setting the bit
    // fails the gate closed (`compute_all_evidence_grounded` excludes it), which
    // is the field's documented contract and the dormant amber state consumers
    // already wired.
    let semantic_unverified = status == CheckStatus::Grounded
        && requires_text(claim.kind)
        && target.element_boundary_char.is_some();
    Check {
        id: check_id,
        claim,
        status,
        reason,
        match_method,
        semantic_unverified,
        nearest_match,
        evidence,
        evidence_tier,
        resolved_element_ids: context
            .emit_hardening
            .then(|| target.element_ids.clone())
            .unwrap_or_default(),
        provenance,
        context_echo,
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
    /// Set where the target resolves, never re-derived from the citation, so the tier
    /// cannot drift from the locator precedence it describes.
    tier: EvidenceTier,
    page: Option<String>,
    bbox: Option<[i64; 4]>,
    text: Option<String>,
    from_table_cell: bool,
    element_index: Option<usize>,
    element_ids: Vec<String>,
    element_boundary_char: Option<u32>,
}

/// Per-run grounding snapshot used to avoid cloning full entity collections per claim.
///
/// The lookup maps intentionally preserve first-match-by-id behavior, matching the trait default
/// and current native/ODL adapters. If an adapter gives `element_by_id` different semantics, update
/// this index at the same time so verifier resolution does not silently diverge.
pub struct SourceIndex {
    capabilities: ethos_core::grounding::Capabilities,
    pages: Vec<PageGeometry>,
    elements: Vec<GroundingElement>,
    spans: Vec<GroundingSpan>,
    tables: Vec<GroundingTable>,
    element_by_id: BTreeMap<String, usize>,
    span_by_id: BTreeMap<String, usize>,
    table_by_id: BTreeMap<String, usize>,
    /// Element positions per page id, in document order — the page scan's index.
    elements_by_page: BTreeMap<String, Vec<usize>>,
    /// Span positions per page id, in document order.
    spans_by_page: BTreeMap<String, Vec<usize>>,
    /// Element text normalized (and case-folded) under the config this index was
    /// built for — `None` where the element has none. Populated only by
    /// [`SourceIndex::for_verification`]; the anchor path neither builds nor reads
    /// it. The page scan compares against these instead of re-normalizing the
    /// whole page's text once per claim.
    normalized_element_text: Vec<Option<String>>,
    /// Span text normalized under the same config.
    normalized_span_text: Vec<String>,
    /// The exact normalization the caches above were computed under, or `None`
    /// when this index carries no caches ([`SourceIndex::new`]). Only these two
    /// config fields reach `normalize_for`, so they are the whole of what a
    /// cached string depends on — see [`SourceIndex::normalization_key`].
    normalized_for: Option<(TextNormalization, bool)>,
    /// The fingerprint of the source these caches were built from.
    ///
    /// The other half of the obligation the doc comment on
    /// [`verify_claims_indexed`] states. A batch caller reusing one index across
    /// requests can pair it with a different document as easily as with a
    /// different config, and that failure is worse: every resolution reads the
    /// indexed document while the report carries the passed document's
    /// fingerprint, so a citation pinned to B comes back `grounded` on evidence
    /// from A.
    ///
    /// `None` when the source declares no fingerprint. Two such sources compare
    /// equal and are not distinguished — there is nothing to distinguish them by,
    /// and a source without a fingerprint is already degraded under the default
    /// staleness policy.
    built_from: Option<String>,
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
        let mut elements_by_page: BTreeMap<String, Vec<usize>> = BTreeMap::new();
        for (position, element) in elements.iter().enumerate() {
            elements_by_page
                .entry(element.page.clone())
                .or_default()
                .push(position);
        }
        let mut spans_by_page: BTreeMap<String, Vec<usize>> = BTreeMap::new();
        for (position, span) in spans.iter().enumerate() {
            spans_by_page
                .entry(span.page.clone())
                .or_default()
                .push(position);
        }

        SourceIndex {
            capabilities,
            pages,
            elements,
            spans,
            tables,
            element_by_id,
            span_by_id,
            table_by_id,
            elements_by_page,
            spans_by_page,
            normalized_for: None,
            built_from: None,
            normalized_element_text: Vec::new(),
            normalized_span_text: Vec::new(),
        }
    }

    /// Build the index once for a whole verification run under one config —
    /// including the normalized-text caches the page scan reads. `verify_claims`
    /// builds this per call; a batch caller builds it once and hands it to
    /// [`verify_claims_indexed`] per request, which is the whole point: the
    /// document is cloned, indexed, and normalized once instead of once per
    /// NDJSON line.
    pub fn for_verification(source: &dyn GroundingSource, config: &VerificationConfig) -> Self {
        let mut index = Self::new(source);
        index.normalized_element_text = index
            .elements
            .iter()
            .map(|element| {
                element
                    .text
                    .as_deref()
                    .map(|text| normalize_for(config, text))
            })
            .collect();
        index.normalized_span_text = index
            .spans
            .iter()
            .map(|span| normalize_for(config, &span.text))
            .collect();
        index.normalized_for = Some(Self::normalization_key(config));
        index.built_from = source.fingerprint();
        index
    }

    /// The config fields a cached normalized string actually depends on.
    ///
    /// `normalize_for` reads `matching.text_normalization` and
    /// `matching.case_sensitive` and nothing else, so two configs agreeing on
    /// these two produce identical caches and are interchangeable here. Deriving
    /// the key from the same pair the normalizer reads keeps the check honest: a
    /// third field added to `normalize_for` without being added here would make
    /// this key claim an equivalence that no longer holds, which is why the
    /// function sits directly beside it.
    fn normalization_key(config: &VerificationConfig) -> (TextNormalization, bool) {
        (
            config.matching.text_normalization,
            config.matching.case_sensitive,
        )
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
    let table_locator = claim.kind == ClaimKind::TableCell
        || claim.citation.table_id.is_some()
        || claim.citation.cell.is_some();
    let primary_locator_count = usize::from(table_locator)
        + usize::from(claim.citation.span_id.is_some())
        + usize::from(claim.citation.element_id.is_some())
        + usize::from(claim.citation.bbox.is_some());
    if primary_locator_count > 1 {
        return TargetResolution::Invalid(CheckReason::LocatorConflict);
    }

    if table_locator {
        return enforce_supplemental_page(resolve_table_cell(index, claim), claim);
    }

    if let Some(span_id) = claim.citation.span_id.as_deref() {
        if !index.capabilities.spans {
            return TargetResolution::CapabilityBlocked(CheckReason::MissingSpanCapability);
        }
        let resolution = index
            .span(span_id)
            .map(target_from_span)
            .map(TargetResolution::Found)
            .unwrap_or(TargetResolution::NotFound(CheckReason::SpanNotFound));
        return enforce_supplemental_page(resolution, claim);
    }

    if let Some(element_id) = claim.citation.element_id.as_deref() {
        let resolution = index
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
        return enforce_supplemental_page(resolution, claim);
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
                element.page == page
                    && element
                        .bbox
                        .is_some_and(|geom| contains_bbox(geom, bbox, tolerance))
            })
            .min_by_key(|(position, element)| {
                (element.bbox.map_or(u128::MAX, bbox_area), *position)
            })
            .map(|(position, element)| target_from_element(element, Some(position)))
            .map(TargetResolution::Found)
            .unwrap_or(TargetResolution::NotFound(CheckReason::BboxNotFound));
    }

    if claim.citation.bbox.is_some() {
        return TargetResolution::Invalid(CheckReason::MissingPageForBbox);
    }

    if let Some(page) = claim.citation.page.as_deref() {
        let Some(found) = index.pages.iter().find(|candidate| candidate.id == page) else {
            return TargetResolution::NotFound(CheckReason::PageNotFound);
        };
        // A page-only locator on a text-bearing claim kind searches the page before
        // judging. Presence claims are excluded even when they carry text — the
        // wire schema permits text on a presence claim, but presence asserts
        // existence of the locator's target, and upgrading its evidence to an
        // element the claim never named would change tier, bbox, and crop for a
        // verdict that was already grounded.
        // The alternative this replaced returned a text-less page target, which
        // check_text_claim reported as a text mismatch labelled with a match method
        // that never ran — a false verdict for a quote verbatim on the cited page,
        // and one the anchor engine already contradicted by answering Matched for
        // the identical input. Resolution order is the anchor engine's: first
        // matching element in document order, then first matching span. A quote
        // split across fragments still mismatches — the sanctioned adjacent-join
        // repair requires an element id, and a page cannot name which join was
        // meant.
        if let Some(expected) = claim.text.as_deref().filter(|_| requires_text(claim.kind)) {
            // One normalization of the claim text, compared against the index's
            // per-config caches — the scan used to re-normalize every element on
            // the page once per claim.
            let expected = normalize_for(config, expected);
            let element_hit = index
                .elements_by_page
                .get(page)
                .into_iter()
                .flatten()
                .find(|position| {
                    index
                        .normalized_element_text
                        .get(**position)
                        .and_then(Option::as_deref)
                        .is_some_and(|actual| normalized_matches(claim.kind, &expected, actual))
                })
                .and_then(|position| Some((*position, index.elements.get(*position)?)));
            if let Some((position, element)) = element_hit {
                return TargetResolution::Found(target_from_element(element, Some(position)));
            }
            let span_hit = index
                .spans_by_page
                .get(page)
                .into_iter()
                .flatten()
                .find(|position| {
                    index
                        .normalized_span_text
                        .get(**position)
                        .is_some_and(|actual| normalized_matches(claim.kind, &expected, actual))
                })
                .and_then(|position| index.spans.get(*position));
            if let Some(span) = span_hit {
                return TargetResolution::Found(target_from_span(span));
            }
        }
        return TargetResolution::Found(FoundTarget {
            page: Some(found.id.clone()),
            tier: EvidenceTier::PageScoped,
            bbox: Some([0, 0, found.width, found.height]),
            text: None,
            from_table_cell: false,
            element_index: None,
            element_ids: Vec::new(),
            element_boundary_char: None,
        });
    }

    TargetResolution::NotFound(CheckReason::MissingLocator)
}

fn enforce_supplemental_page(resolution: TargetResolution, claim: &Claim) -> TargetResolution {
    let Some(expected_page) = claim.citation.page.as_deref() else {
        return resolution;
    };
    match resolution {
        TargetResolution::Found(target) if target.page.as_deref() != Some(expected_page) => {
            TargetResolution::Invalid(CheckReason::LocatorConflict)
        }
        other => other,
    }
}

fn target_from_element(element: &GroundingElement, element_index: Option<usize>) -> FoundTarget {
    FoundTarget {
        page: Some(element.page.clone()),
        bbox: element.bbox,
        text: element.text.clone(),
        tier: EvidenceTier::ElementScoped,
        from_table_cell: false,
        element_index,
        element_ids: vec![element.id.clone()],
        element_boundary_char: None,
    }
}

fn target_from_span(span: &GroundingSpan) -> FoundTarget {
    FoundTarget {
        page: Some(span.page.clone()),
        bbox: span.bbox,
        text: Some(span.text.clone()),
        tier: EvidenceTier::ExactSpan,
        from_table_cell: false,
        element_index: None,
        element_ids: span.element.iter().cloned().collect(),
        element_boundary_char: None,
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
        bbox: cell.bbox,
        text: Some(cell.text.clone()),
        tier: EvidenceTier::TableCell,
        from_table_cell: true,
        element_index: None,
        element_ids: Vec::new(),
        element_boundary_char: None,
    }
}

fn adjacent_quote_target(
    index: &SourceIndex,
    claim: &Claim,
    target: &FoundTarget,
    config: &VerificationConfig,
) -> Result<Option<FoundTarget>, CheckReason> {
    if claim.kind != ClaimKind::Quote {
        return Ok(None);
    }
    let Some(expected) = claim.text.as_deref() else {
        return Ok(None);
    };
    if target
        .text
        .as_deref()
        .is_some_and(|actual| text_matches(ClaimKind::Quote, expected, actual, config))
    {
        return Ok(None);
    }

    if claim.citation.bbox.is_some() {
        return Ok(None);
    }

    if claim.citation.element_id.is_some() {
        if let Some(position) = target.element_index {
            if index.capabilities.coordinate_origin == CoordinateOrigin::Unknown {
                // Coordinate trust only decides the outcome when a neighbour could have
                // joined at all. When no reading-order neighbour joins with the cited
                // element to match the quote, no adjacency ruling could ground this claim,
                // so the determinate negative already computed against the cited element
                // stands. Refusing here unconditionally would discard a sound `mismatch`
                // in favour of "cannot tell". This branch can only return a non-pass:
                // `Ok(None)` falls through to the single-element comparison that has
                // already failed to match.
                if adjacent_join_has_text_candidate(index, position, expected, config) {
                    return Err(CheckReason::UnknownCoordinateOrigin);
                }
                return Ok(None);
            }
            return Ok(adjacent_text_pair_for_element(
                index, position, expected, config,
            ));
        }
    }

    Ok(None)
}

/// True when some reading-order neighbour of `position` satisfies every join precondition
/// except adjacency itself.
///
/// Used only on sources with an unknown coordinate origin, to separate "a join might have
/// grounded this and we cannot adjudicate it" from "no join was ever possible".
fn adjacent_join_has_text_candidate(
    index: &SourceIndex,
    position: usize,
    expected: &str,
    config: &VerificationConfig,
) -> bool {
    let Some(current) = index.elements.get(position) else {
        return false;
    };
    let joins_with_next = position
        .checked_add(1)
        .and_then(|next| index.elements.get(next))
        .and_then(|second| adjacent_pair_join_ignoring_geometry(current, second, expected, config))
        .is_some();
    if joins_with_next {
        return true;
    }
    position
        .checked_sub(1)
        .and_then(|previous| index.elements.get(previous))
        .and_then(|first| adjacent_pair_join_ignoring_geometry(first, current, expected, config))
        .is_some()
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

/// Every join precondition except `element_bboxes_are_adjacent`, returning the joined text.
///
/// `element_bboxes_are_adjacent` is the only predicate here that reads coordinates *as*
/// coordinates, and so the only one an unknown coordinate origin invalidates. Page identity
/// and bbox *presence* are structural facts that hold whatever the origin is: a cross-page
/// pair is never joinable by rule, and an element declaring no geometry is never "next to"
/// another. Splitting them out lets `adjacent_join_has_text_candidate` ask whether geometry
/// is load-bearing for this claim at all.
fn adjacent_pair_join_ignoring_geometry(
    first: &GroundingElement,
    second: &GroundingElement,
    expected: &str,
    config: &VerificationConfig,
) -> Option<String> {
    if first.page != second.page {
        return None;
    }
    if first.bbox.is_none() || second.bbox.is_none() {
        return None;
    }
    let first_text = first.text.as_deref()?;
    let second_text = second.text.as_deref()?;
    let joined = join_adjacent_text(first_text, second_text, config);
    // `expected` is the same string in all three comparisons, so it is normalized
    // once rather than three times. `normalized_matches` is what `text_matches`
    // calls after normalizing both sides, so the comparison is unchanged.
    let expected_normalized = normalize_for(config, expected);
    if normalized_matches(
        ClaimKind::Quote,
        &expected_normalized,
        &normalize_for(config, first_text),
    ) || normalized_matches(
        ClaimKind::Quote,
        &expected_normalized,
        &normalize_for(config, second_text),
    ) || !normalized_matches(
        ClaimKind::Quote,
        &expected_normalized,
        &normalize_for(config, &joined),
    ) {
        return None;
    }
    Some(joined)
}

fn adjacent_text_pair_target(
    first: &GroundingElement,
    second: &GroundingElement,
    expected: &str,
    config: &VerificationConfig,
) -> Option<FoundTarget> {
    let joined = adjacent_pair_join_ignoring_geometry(first, second, expected, config)?;
    // Both elements need declared geometry before adjacency can mean anything. A
    // geometry-free element is never "next to" another, which matches the existing
    // capability gate on CoordinateOrigin::Unknown: no coordinates, no join.
    let (Some(first_bbox), Some(second_bbox)) = (first.bbox, second.bbox) else {
        return None;
    };
    if !element_bboxes_are_adjacent(
        first_bbox,
        second_bbox,
        config.matching.adjacency_gap_tolerance_q.unwrap_or(0),
    ) {
        return None;
    }
    let first_text = first.text.as_deref()?;

    Some(FoundTarget {
        page: Some(first.page.clone()),
        // Two elements joined is still element precision, not span precision.
        tier: EvidenceTier::ElementScoped,
        bbox: Some(union_bbox(first_bbox, second_bbox)),
        text: Some(joined),
        from_table_cell: false,
        element_index: None,
        element_ids: vec![first.id.clone(), second.id.clone()],
        element_boundary_char: Some(match config.matching.text_normalization {
            TextNormalization::None => first_text.chars().count() as u32,
            TextNormalization::CollapseWhitespace => {
                normalize_quote(first_text).chars().count() as u32
            }
            TextNormalization::UnicodeCompatV1 => normalize_quote_unicode_compat_v1(first_text)
                .chars()
                .count() as u32,
        }),
    })
}

fn join_adjacent_text(first: &str, second: &str, config: &VerificationConfig) -> String {
    let joined = format!("{first} {second}");
    match config.matching.text_normalization {
        TextNormalization::None => joined,
        TextNormalization::CollapseWhitespace => normalize_quote(&joined),
        TextNormalization::UnicodeCompatV1 => normalize_quote_unicode_compat_v1(&joined),
    }
}

fn bbox_area(bbox: [i64; 4]) -> u128 {
    let width = bbox[2].saturating_sub(bbox[0]).max(0) as u128;
    let height = bbox[3].saturating_sub(bbox[1]).max(0) as u128;
    width.saturating_mul(height)
}

fn element_bboxes_are_adjacent(first: [i64; 4], second: [i64; 4], gap_tolerance_q: i64) -> bool {
    // The test is on the absolute distance between facing edges, so a tolerance
    // admits both gaps and slight overlaps — real extractors produce both. Zero
    // (the default, and every config that predates the knob) means exact
    // edge-to-edge touch, the original rule.
    let same_line = ranges_overlap_i64(first[1], first[3], second[1], second[3])
        && (second[0] - first[2]).abs() <= gap_tolerance_q;
    let stacked = ranges_overlap_i64(first[0], first[2], second[0], second[2])
        && (second[1] - first[3]).abs() <= gap_tolerance_q;
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

fn check_provenance(source: &dyn GroundingSource, target: &FoundTarget) -> CheckProvenance {
    let Some(element_id) = target.element_ids.first() else {
        return CheckProvenance {
            status: ProvenanceStatus::NotApplicable,
            heading_path: Vec::new(),
            element_role: None,
            previous_element_id: None,
            next_element_id: None,
        };
    };
    let Some(provenance) = source.structural_provenance(element_id) else {
        return CheckProvenance {
            status: ProvenanceStatus::CapabilityLimited,
            heading_path: Vec::new(),
            element_role: None,
            previous_element_id: None,
            next_element_id: None,
        };
    };
    if target
        .element_ids
        .iter()
        .skip(1)
        .any(|element_id| source.structural_provenance(element_id).is_none())
    {
        return CheckProvenance {
            status: ProvenanceStatus::CapabilityLimited,
            heading_path: Vec::new(),
            element_role: None,
            previous_element_id: None,
            next_element_id: None,
        };
    }
    CheckProvenance {
        status: ProvenanceStatus::Available,
        heading_path: provenance.heading_path,
        element_role: Some(provenance.element_role),
        previous_element_id: provenance.previous_element_id,
        next_element_id: provenance.next_element_id,
    }
}

struct MappedText {
    text: String,
    byte_starts: Vec<usize>,
    byte_ends: Vec<usize>,
}

fn mapped_text(input: &str, normalization: TextNormalization, case_sensitive: bool) -> MappedText {
    let chars: Vec<(char, usize, usize)> = input
        .char_indices()
        .map(|(start, ch)| (ch, start, start + ch.len_utf8()))
        .collect();
    let mut units: Vec<(char, usize, usize)> = Vec::new();
    match normalization {
        TextNormalization::None => units.extend(chars),
        TextNormalization::CollapseWhitespace => {
            let mut whitespace: Option<(usize, usize)> = None;
            for (ch, start, end) in chars {
                if ch.is_ascii_whitespace() {
                    if !units.is_empty() {
                        whitespace = Some(match whitespace {
                            Some((first, _)) => (first, end),
                            None => (start, end),
                        });
                    }
                    continue;
                }
                if let Some((ws_start, ws_end)) = whitespace.take() {
                    units.push((' ', ws_start, ws_end));
                }
                units.push((ch, start, end));
            }
        }
        TextNormalization::UnicodeCompatV1 => {
            // Every folded character maps back to its source character's byte
            // range — an expansion like fi -> "fi" yields two output chars that
            // both cite the ligature's bytes, the same shape lowercase expansion
            // already uses below.
            let mut whitespace: Option<(usize, usize)> = None;
            for (ch, start, end) in chars {
                if ch.is_whitespace() {
                    if !units.is_empty() {
                        whitespace = Some(match whitespace {
                            Some((first, _)) => (first, end),
                            None => (start, end),
                        });
                    }
                    continue;
                }
                match unicode_compat_v1_fold(ch) {
                    UnicodeFold::Drop => continue,
                    UnicodeFold::Keep(c) => {
                        if let Some((ws_start, ws_end)) = whitespace.take() {
                            units.push((' ', ws_start, ws_end));
                        }
                        units.push((c, start, end));
                    }
                    UnicodeFold::Str(s) => {
                        if let Some((ws_start, ws_end)) = whitespace.take() {
                            units.push((' ', ws_start, ws_end));
                        }
                        for c in s.chars() {
                            units.push((c, start, end));
                        }
                    }
                }
            }
        }
    }

    let mut text = String::new();
    let mut byte_starts = Vec::new();
    let mut byte_ends = Vec::new();
    for (ch, start, end) in units {
        if case_sensitive {
            push_mapped_char(&mut text, &mut byte_starts, &mut byte_ends, ch, start, end);
        } else {
            for lower in ch.to_lowercase() {
                push_mapped_char(
                    &mut text,
                    &mut byte_starts,
                    &mut byte_ends,
                    lower,
                    start,
                    end,
                );
            }
        }
    }
    MappedText {
        text,
        byte_starts,
        byte_ends,
    }
}

fn push_mapped_char(
    output: &mut String,
    byte_starts: &mut Vec<usize>,
    byte_ends: &mut Vec<usize>,
    ch: char,
    start: usize,
    end: usize,
) {
    output.push(ch);
    for _ in 0..ch.len_utf8() {
        byte_starts.push(start);
        byte_ends.push(end);
    }
}

fn matched_source_range(
    kind: ClaimKind,
    expected: &str,
    actual: &str,
    config: &VerificationConfig,
) -> Option<(usize, usize)> {
    let expected = mapped_text(
        expected,
        config.matching.text_normalization,
        config.matching.case_sensitive,
    );
    let actual = mapped_text(
        actual,
        config.matching.text_normalization,
        config.matching.case_sensitive,
    );
    let start = if kind == ClaimKind::Quote {
        actual.text.find(&expected.text)?
    } else if actual.text == expected.text {
        0
    } else {
        return None;
    };
    let end = start.checked_add(expected.text.len())?;
    if start == end {
        return None;
    }
    Some((
        *actual.byte_starts.get(start)?,
        *actual.byte_ends.get(end - 1)?,
    ))
}

fn context_echo(
    kind: ClaimKind,
    expected: Option<&str>,
    target: &FoundTarget,
    config: &VerificationConfig,
    window_chars: u32,
) -> Option<ContextEcho> {
    if !matches!(kind, ClaimKind::Quote | ClaimKind::Value) {
        return None;
    }
    let expected = expected?;
    let actual = target.text.as_deref()?;
    let (start, end) = matched_source_range(kind, expected, actual, config)?;
    let before_all = actual.get(..start)?;
    let matched = actual.get(start..end)?.to_string();
    let after_all = actual.get(end..)?;
    let before = take_last_chars(before_all, window_chars as usize);
    let after = take_first_chars(after_all, window_chars as usize);
    let echo_start = before_all
        .chars()
        .count()
        .saturating_sub(before.chars().count());
    let echo_len = before.chars().count() + matched.chars().count() + after.chars().count();
    let element_boundary = target.element_boundary_char.and_then(|boundary| {
        let boundary = boundary as usize;
        (boundary >= echo_start && boundary <= echo_start + echo_len).then(|| ContextBoundary {
            offset: (boundary - echo_start) as u32,
            left_element_id: target.element_ids.first().cloned().unwrap_or_default(),
            right_element_id: target.element_ids.get(1).cloned().unwrap_or_default(),
        })
    });
    Some(ContextEcho {
        before,
        matched,
        after,
        element_boundary,
    })
}

fn take_last_chars(input: &str, limit: usize) -> String {
    let count = input.chars().count();
    input.chars().skip(count.saturating_sub(limit)).collect()
}

fn take_first_chars(input: &str, limit: usize) -> String {
    input.chars().take(limit).collect()
}

fn evidence_dispersion(
    source: &dyn GroundingSource,
    checks: &[Check],
    fingerprint_stale: bool,
    provenance_requested: bool,
) -> EvidenceDispersion {
    let reusable: Vec<&Check> = if fingerprint_stale {
        Vec::new()
    } else {
        checks
            .iter()
            .filter(|check| check.status == CheckStatus::Grounded && !check.semantic_unverified)
            .collect()
    };
    let mut element_ids = BTreeSet::new();
    let mut pages = BTreeSet::new();
    let mut sections = BTreeSet::new();
    let mut sections_complete = provenance_requested;
    let mut unmapped = 0_u32;
    for check in &reusable {
        if check.resolved_element_ids.is_empty() {
            unmapped = unmapped.saturating_add(1);
            if provenance_requested {
                sections_complete = false;
            }
        } else {
            element_ids.extend(check.resolved_element_ids.iter().cloned());
        }
        if let Some(page) = check
            .evidence
            .as_ref()
            .and_then(|evidence| evidence.page.as_ref())
        {
            pages.insert(page.clone());
        }
        if provenance_requested {
            for element_id in &check.resolved_element_ids {
                match source.structural_provenance(element_id) {
                    Some(provenance) => {
                        if let Some(section) = provenance.heading_path.first() {
                            sections.insert(section.clone());
                        }
                    }
                    None => sections_complete = false,
                }
            }
        }
    }
    EvidenceDispersion {
        grounded_checks: reusable.len() as u32,
        elements: element_ids.len() as u32,
        pages: pages.len() as u32,
        unmapped_grounded_checks: unmapped,
        sections: sections_complete.then_some(sections.len() as u32),
    }
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
    // unicode_compat_v1 reports the same normalized_* method names as
    // collapse_whitespace: the method says a normalization ran, and which one is
    // pinned by the attested verification_config_sha256, not by a new enum value
    // every report validator would have to learn.
    match (kind, config.matching.text_normalization) {
        (ClaimKind::Quote, TextNormalization::None) => MatchMethod::ExactTextContains,
        (
            ClaimKind::Quote,
            TextNormalization::CollapseWhitespace | TextNormalization::UnicodeCompatV1,
        ) => MatchMethod::NormalizedTextContains,
        (_, TextNormalization::None) => MatchMethod::ExactText,
        (_, TextNormalization::CollapseWhitespace | TextNormalization::UnicodeCompatV1) => {
            MatchMethod::NormalizedText
        }
    }
}

/// Normalize one side of a comparison under the config's profile, case fold
/// included. `text_matches`, the page scan's cache build, and the nearest-match
/// diagnostic all go through here, so "normalized under this config" means one
/// thing everywhere.
fn normalize_for(config: &VerificationConfig, text: &str) -> String {
    let normalized = match config.matching.text_normalization {
        TextNormalization::None => text.to_string(),
        TextNormalization::CollapseWhitespace => normalize_quote(text),
        TextNormalization::UnicodeCompatV1 => normalize_quote_unicode_compat_v1(text),
    };
    if config.matching.case_sensitive {
        normalized
    } else {
        normalized.to_lowercase()
    }
}

/// The comparison itself, over already-normalized sides.
///
/// Fails closed on expected text that normalized to nothing: `contains("")` is
/// true of every element, so expected text a profile erased entirely — a lone
/// soft hyphen under unicode_compat_v1, say — would ground everywhere while
/// asserting nothing. The pre-claim gate only trims Unicode whitespace and cannot
/// see what a fold erases, and the anchor path already refuses
/// empty-after-normalization expected text; the verdict path must not be weaker.
fn normalized_matches(kind: ClaimKind, expected: &str, actual: &str) -> bool {
    if expected.is_empty() {
        return false;
    }
    if kind == ClaimKind::Quote {
        actual.contains(expected)
    } else {
        actual == expected
    }
}

fn text_matches(
    kind: ClaimKind,
    expected: &str,
    actual: &str,
    config: &VerificationConfig,
) -> bool {
    normalized_matches(
        kind,
        &normalize_for(config, expected),
        &normalize_for(config, actual),
    )
}

/// Diagnostic nearest candidate for a failed text check (`include_nearest_match`).
///
/// Candidate scope narrows with the citation: the cited element when one is
/// named, else the cited page's elements, else every element. Similarity is
/// token-set Jaccard in integer basis points — whitespace-split tokens of the
/// config-normalized texts, integer arithmetic throughout because c14n admits no
/// float. Ties break to the earlier element in document order. The verdict never
/// reads the result; it exists so a consumer can tell a near-miss from a
/// fabrication without re-reading the document.
fn nearest_match_for(
    index: &SourceIndex,
    claim: &Claim,
    config: &VerificationConfig,
) -> Option<NearestMatch> {
    const NEAREST_MATCH_TEXT_CHARS: usize = 512;
    let expected = normalize_for(config, claim.text.as_deref()?);
    let expected_tokens: std::collections::BTreeSet<&str> = expected.split_whitespace().collect();
    if expected_tokens.is_empty() {
        return None;
    }
    let candidates: Vec<usize> = if let Some(element_id) = claim.citation.element_id.as_deref() {
        index
            .element_by_id
            .get(element_id)
            .copied()
            .into_iter()
            .collect()
    } else if let Some(page) = claim.citation.page.as_deref() {
        index
            .elements_by_page
            .get(page)
            .cloned()
            .unwrap_or_default()
    } else {
        (0..index.elements.len()).collect()
    };
    let mut best: Option<(u16, usize)> = None;
    for position in candidates {
        let Some(normalized) = index
            .normalized_element_text
            .get(position)
            .and_then(Option::as_deref)
        else {
            continue;
        };
        let candidate_tokens: std::collections::BTreeSet<&str> =
            normalized.split_whitespace().collect();
        if candidate_tokens.is_empty() {
            continue;
        }
        let intersection = expected_tokens.intersection(&candidate_tokens).count();
        let union = expected_tokens.union(&candidate_tokens).count();
        let similarity_bp = ((intersection * 10_000) / union) as u16;
        if best.is_none_or(|(best_bp, _)| similarity_bp > best_bp) {
            best = Some((similarity_bp, position));
        }
    }
    let (similarity_bp, position) = best?;
    let element = index.elements.get(position)?;
    Some(NearestMatch {
        element_id: Some(element.id.clone()),
        text: element
            .text
            .as_deref()
            .unwrap_or_default()
            .chars()
            .take(NEAREST_MATCH_TEXT_CHARS)
            .collect(),
        similarity_bp,
        method: "token_jaccard_v1".to_string(),
    })
}

/// One folded character under `unicode_compat_v1`: what a single source character
/// becomes before whitespace collapse.
enum UnicodeFold {
    /// Not in the table — the character passes through untouched.
    Keep(char),
    /// Erased entirely: soft hyphen, zero-width space, U+FEFF — characters PDF
    /// extraction inserts that carry no quoted content.
    Drop,
    /// Replaced by this ASCII expansion.
    Str(&'static str),
}

/// The `unicode_compat_v1` fold table. Versioned by the profile name and never
/// edited — a different table is a different profile, exactly as a different
/// whitespace rule would be. Each row folds a character PDF extraction routinely
/// emits to the form a model quoting the same words types: the curly-quote family
/// to straight quotes, the dash family (including U+2212 minus) to hyphen-minus,
/// the common Latin ligatures to their letters, U+2026 to three dots. Whitespace
/// is deliberately absent from the table: the profile collapses every
/// `char::is_whitespace` run to one ASCII space before folding is even consulted,
/// which is what folds NBSP and its relatives.
fn unicode_compat_v1_fold(ch: char) -> UnicodeFold {
    match ch {
        '\u{2018}' | '\u{2019}' | '\u{201A}' | '\u{201B}' => UnicodeFold::Str("'"),
        '\u{201C}' | '\u{201D}' | '\u{201E}' | '\u{201F}' => UnicodeFold::Str("\""),
        '\u{2010}' | '\u{2011}' | '\u{2012}' | '\u{2013}' | '\u{2014}' | '\u{2015}'
        | '\u{2212}' => UnicodeFold::Str("-"),
        '\u{2026}' => UnicodeFold::Str("..."),
        '\u{FB00}' => UnicodeFold::Str("ff"),
        '\u{FB01}' => UnicodeFold::Str("fi"),
        '\u{FB02}' => UnicodeFold::Str("fl"),
        '\u{FB03}' => UnicodeFold::Str("ffi"),
        '\u{FB04}' => UnicodeFold::Str("ffl"),
        '\u{FB05}' | '\u{FB06}' => UnicodeFold::Str("st"),
        '\u{00AD}' | '\u{200B}' | '\u{FEFF}' => UnicodeFold::Drop,
        _ => UnicodeFold::Keep(ch),
    }
}

/// Normalize a quote under `unicode_compat_v1`: collapse runs of Unicode
/// whitespace to one ASCII space, apply [`unicode_compat_v1_fold`] to everything
/// else, and trim. Kept in lockstep with `mapped_text`'s arm by construction —
/// both consume the same fold table — and by a conformance test asserting the two
/// agree on every published vector, because two implementations of one profile
/// drifting apart is exactly the defect this family of profiles exists to
/// prevent.
pub fn normalize_quote_unicode_compat_v1(input: &str) -> String {
    let mut out = String::with_capacity(input.len());
    let mut pending_space = false;
    for ch in input.chars() {
        if ch.is_whitespace() {
            if !out.is_empty() {
                pending_space = true;
            }
            continue;
        }
        match unicode_compat_v1_fold(ch) {
            UnicodeFold::Drop => {}
            UnicodeFold::Keep(c) => {
                if pending_space {
                    out.push(' ');
                    pending_space = false;
                }
                out.push(c);
            }
            UnicodeFold::Str(s) => {
                if pending_space {
                    out.push(' ');
                    pending_space = false;
                }
                out.push_str(s);
            }
        }
    }
    out
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
pub(crate) mod tests {
    use super::*;

    /// An index built from a DIFFERENT document is rebuilt too.
    ///
    /// The config half of this obligation was enforced; the source half was not,
    /// and it is the worse of the two. Every resolution reads the indexed
    /// document while `document_fingerprint` on the report names the passed one,
    /// so a citation pinned to B could come back `grounded` on evidence from A.
    #[test]
    fn an_index_from_another_document_is_not_reused() {
        // Document B says something A does not, so reusing A's index is visible in
        // the verdict rather than only in the identity field.
        struct OtherDocument(TestSource);
        impl GroundingSource for OtherDocument {
            fn parser(&self) -> ParserIdentity {
                self.0.parser()
            }
            fn capabilities(&self) -> Capabilities {
                self.0.capabilities()
            }
            fn fingerprint(&self) -> Option<String> {
                Some(format!("sha256:{}", "b".repeat(64)))
            }
            fn pages(&self) -> Vec<PageGeometry> {
                self.0.pages()
            }
            fn elements(&self) -> Vec<GroundingElement> {
                self.0
                    .elements()
                    .into_iter()
                    .map(|mut element| {
                        element.text = Some("Losses widened in Q3 2025.".into());
                        element
                    })
                    .collect()
            }
            fn spans(&self) -> Vec<GroundingSpan> {
                Vec::new()
            }
            fn tables(&self) -> Vec<GroundingTable> {
                Vec::new()
            }
        }

        let config = VerificationConfig::default_v1();
        let source_a = TestSource::default();
        let source_b = OtherDocument(TestSource::default());

        let index_a = SourceIndex::for_verification(&source_a, &config);
        assert_eq!(index_a.built_from, source_a.fingerprint());
        assert_ne!(index_a.built_from, source_b.fingerprint());

        // A quote only document A contains. Verified against B it must not ground.
        let claims = || {
            vec![claim(
                ClaimKind::Quote,
                Some("Revenue grew to $12.4M"),
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )]
        };

        let honest = verify_claims_indexed(
            &source_b,
            &SourceIndex::for_verification(&source_b, &config),
            CitationInput::Envelope(CitationEnvelope {
                document_fingerprint: source_b.fingerprint(),
                claims: claims(),
            }),
            &config,
            "0".repeat(64),
            "1".repeat(64),
        );
        assert_ne!(
            honest.checks[0].status,
            CheckStatus::Grounded,
            "the fixture must be a quote document B does not contain"
        );

        let rebuilt = verify_claims_indexed(
            &source_b,
            &index_a,
            CitationInput::Envelope(CitationEnvelope {
                document_fingerprint: source_b.fingerprint(),
                claims: claims(),
            }),
            &config,
            "0".repeat(64),
            "1".repeat(64),
        );
        assert_eq!(
            rebuilt.checks[0].status, honest.checks[0].status,
            "A's index must not ground a claim against B"
        );
    }

    /// A mismatched index loses the shortcut, never the verdict.
    ///
    /// The fast path's obligation — "built from the same source and config, or the
    /// caches lie" — used to be prose only, reachable through a `pub` function. A
    /// caller that paired an index with the wrong config got its page scan compared
    /// against strings normalized by rules it did not ask for.
    #[test]
    fn a_mismatched_index_still_answers_under_the_config_it_was_given() {
        let source = TestSource::default();
        let mut case_sensitive = VerificationConfig::default_v1();
        case_sensitive.matching.case_sensitive = true;
        let mut case_insensitive = VerificationConfig::default_v1();
        case_insensitive.matching.case_sensitive = false;

        // A quote whose case differs from the source, so the two configs disagree
        // about it and the cached normalization is load-bearing.
        let claims = || {
            vec![claim(
                ClaimKind::Quote,
                Some("REVENUE GREW TO $12.4M"),
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )]
        };

        let honest = verify_claims_indexed(
            &source,
            &SourceIndex::for_verification(&source, &case_sensitive),
            input(&source, claims()),
            &case_sensitive,
            "0".repeat(64),
            "1".repeat(64),
        );

        // The same request handed an index built under the OTHER normalization.
        let repaired = verify_claims_indexed(
            &source,
            &SourceIndex::for_verification(&source, &case_insensitive),
            input(&source, claims()),
            &case_sensitive,
            "0".repeat(64),
            "1".repeat(64),
        );
        assert_eq!(
            repaired.checks[0].status, honest.checks[0].status,
            "a mismatched index must not change the verdict"
        );

        // An index carrying no caches at all is rebuilt the same way.
        let from_uncached = verify_claims_indexed(
            &source,
            &SourceIndex::new(&source),
            input(&source, claims()),
            &case_sensitive,
            "0".repeat(64),
            "1".repeat(64),
        );
        assert_eq!(from_uncached.checks[0].status, honest.checks[0].status);

        // And the two configs really do disagree here, or the test proves nothing.
        let other = verify_claims_indexed(
            &source,
            &SourceIndex::for_verification(&source, &case_insensitive),
            input(&source, claims()),
            &case_insensitive,
            "0".repeat(64),
            "1".repeat(64),
        );
        assert_ne!(
            other.checks[0].status, honest.checks[0].status,
            "the fixture must be one the two configs answer differently"
        );
    }

    use ethos_core::grounding::{
        Capabilities, GroundingCell, GroundingElement, GroundingProvenance, GroundingSpan,
        GroundingTable, PageGeometry, ParserIdentity,
    };
    use ethos_core::verify_types::{
        CapabilityLimit, CellRef, Citation, Claim, HardeningOptions,
        HARDENED_VERIFICATION_SCHEMA_VERSION,
    };

    #[derive(Clone)]
    // `pub(crate)` so `crate::anchor`'s own tests can share this fixture rather
    // than keeping a second copy of it in step with this one.
    pub(crate) struct TestSource {
        caps: Capabilities,
        fingerprint: Option<String>,
        crop_ref: Option<String>,
        structure: bool,
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
                structure: true,
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
                    bbox: Some([7200, 10100, 54000, 11500]),
                    kind: "text_block".into(),
                    text: Some(
                        "Revenue grew to $12.4M in Q3 2025, driven by enterprise expansion.".into(),
                    ),
                    locator: None,
                },
                GroundingElement {
                    id: "e000003".into(),
                    page: "p0001".into(),
                    bbox: Some([7200, 13000, 54000, 20000]),
                    kind: "table".into(),
                    text: None,
                    locator: None,
                },
            ]
        }
        fn structural_provenance(&self, element_id: &str) -> Option<GroundingProvenance> {
            if !self.structure || element_id != "e000002" {
                return None;
            }
            Some(GroundingProvenance {
                heading_path: vec!["Results".into()],
                element_role: "text_block".into(),
                previous_element_id: Some("e000001".into()),
                next_element_id: Some("e000003".into()),
            })
        }
        fn spans(&self) -> Vec<GroundingSpan> {
            vec![GroundingSpan {
                id: "s000002".into(),
                page: "p0001".into(),
                bbox: Some([7200, 10100, 54000, 11500]),
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
                bbox: Some([7200, 13000, 54000, 20000]),
                cells: vec![
                    GroundingCell {
                        row: 0,
                        col: 0,
                        row_span: 1,
                        col_span: 1,
                        bbox: Some([7200, 13000, 30600, 16500]),
                        text: "Metric".into(),
                    },
                    GroundingCell {
                        row: 1,
                        col: 1,
                        row_span: 1,
                        col_span: 1,
                        bbox: Some([30600, 16500, 54000, 20000]),
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
        spans: Vec<GroundingSpan>,
        coordinate_origin: CoordinateOrigin,
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
                coordinate_origin: self.coordinate_origin,
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
            self.spans.clone()
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
        verify_claims(
            source,
            input(source, claims),
            &cfg,
            "0".repeat(64),
            "1".repeat(64),
        )
    }

    fn verify_with_config(
        source: &TestSource,
        claims: Vec<Claim>,
        cfg: &VerificationConfig,
    ) -> VerificationReport {
        verify_claims(
            source,
            input(source, claims),
            cfg,
            "0".repeat(64),
            "1".repeat(64),
        )
    }

    fn hardened_config() -> VerificationConfig {
        let mut config = VerificationConfig::default_v1();
        config.schema_version = HARDENED_VERIFICATION_SCHEMA_VERSION.to_string();
        config.config_version = "hardened-v1".to_string();
        config.hardening = Some(HardeningOptions {
            include_provenance: true,
            include_context_echo: true,
            include_dispersion: true,
            context_window_chars: 12,
            include_nearest_match: false,
        });
        config
    }

    fn element(id: &str, page: &str, bbox: [i64; 4], text: Option<&str>) -> GroundingElement {
        GroundingElement {
            id: id.into(),
            page: page.into(),
            bbox: Some(bbox),
            kind: "text_block".into(),
            text: text.map(str::to_string),
            locator: None,
        }
    }

    fn verify_elements(elements: Vec<GroundingElement>, claims: Vec<Claim>) -> VerificationReport {
        verify_elements_with_origin(elements, claims, CoordinateOrigin::TopLeft)
    }

    fn verify_elements_with_origin(
        elements: Vec<GroundingElement>,
        claims: Vec<Claim>,
        coordinate_origin: CoordinateOrigin,
    ) -> VerificationReport {
        let source = ElementSource {
            elements,
            spans: Vec::new(),
            coordinate_origin,
        };
        let cfg = VerificationConfig::default_v1();
        let citations = CitationInput::Envelope(CitationEnvelope {
            document_fingerprint: source.fingerprint(),
            claims,
        });
        verify_claims(&source, citations, &cfg, "0".repeat(64), "1".repeat(64))
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
    fn hardened_report_emits_provenance_context_and_dispersion() {
        let source = TestSource::default();
        let config = hardened_config();
        let report = verify_with_config(
            &source,
            vec![claim(
                ClaimKind::Quote,
                Some("Revenue   grew to $12.4M in Q3 2025"),
                Citation {
                    element_id: Some("e000002".into()),
                    ..Default::default()
                },
            )],
            &config,
        );

        assert_eq!(report.schema_version, HARDENED_VERIFICATION_SCHEMA_VERSION);
        let check = &report.checks[0];
        assert_eq!(check.resolved_element_ids, vec!["e000002"]);
        let provenance = check.provenance.as_ref().unwrap();
        assert_eq!(provenance.status, ProvenanceStatus::Available);
        assert_eq!(provenance.heading_path, vec!["Results"]);
        assert_eq!(provenance.element_role.as_deref(), Some("text_block"));
        let echo = check.context_echo.as_ref().unwrap();
        assert_eq!(echo.before, "");
        assert_eq!(echo.matched, "Revenue grew to $12.4M in Q3 2025");
        assert_eq!(echo.after, ", driven by ");
        assert!(echo.element_boundary.is_none());
        assert_eq!(
            report.dispersion,
            Some(EvidenceDispersion {
                grounded_checks: 1,
                elements: 1,
                pages: 1,
                unmapped_grounded_checks: 0,
                sections: Some(1),
            })
        );
    }

    #[test]
    fn hardened_report_marks_missing_structure_without_invalidating_grounding() {
        let source = TestSource {
            structure: false,
            ..TestSource::default()
        };
        let config = hardened_config();
        let report = verify_with_config(
            &source,
            vec![claim(
                ClaimKind::Quote,
                Some("Revenue grew"),
                Citation {
                    element_id: Some("e000002".into()),
                    ..Default::default()
                },
            )],
            &config,
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(
            report.checks[0].provenance.as_ref().map(|p| p.status),
            Some(ProvenanceStatus::CapabilityLimited)
        );
        assert!(report
            .capability_limits
            .contains(&CapabilityLimit::MissingStructure));
        assert_eq!(report.dispersion.as_ref().and_then(|d| d.sections), None);
    }

    #[test]
    fn hardened_split_quote_preserves_both_elements_and_marks_boundary() {
        let mut config = hardened_config();
        config.hardening.as_mut().unwrap().include_provenance = false;
        let source = ElementSource {
            elements: vec![
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
            spans: Vec::new(),
            coordinate_origin: CoordinateOrigin::TopLeft,
        };
        let citations = CitationInput::Envelope(CitationEnvelope {
            document_fingerprint: source.fingerprint(),
            claims: vec![claim(
                ClaimKind::Quote,
                Some("trust loop verifies grounded"),
                Citation {
                    element_id: Some("split-a".into()),
                    ..Default::default()
                },
            )],
        });
        let report = verify_claims(&source, citations, &config, "0".repeat(64), "1".repeat(64));

        // Grounded but semantic_unverified: the join is the semantic producer's
        // one trigger, and the bit fails the gate closed by contract.
        assert!(!report.all_evidence_grounded);
        assert!(report.checks[0].semantic_unverified);
        assert_eq!(
            report.checks[0].resolved_element_ids,
            vec!["split-a", "split-b"]
        );
        let boundary = report.checks[0]
            .context_echo
            .as_ref()
            .and_then(|echo| echo.element_boundary.as_ref())
            .unwrap();
        assert_eq!(boundary.left_element_id, "split-a");
        assert_eq!(boundary.right_element_id, "split-b");
        // Dispersion counts only checks that are grounded AND semantically clean,
        // and the joined check now carries semantic_unverified — so it contributes
        // no evidence spread.
        assert_eq!(report.dispersion.as_ref().unwrap().elements, 0);
    }

    #[test]
    fn context_echo_chooses_first_repeated_match() {
        let mut config = hardened_config();
        config.hardening.as_mut().unwrap().include_provenance = false;
        config.hardening.as_mut().unwrap().include_dispersion = false;
        config.hardening.as_mut().unwrap().context_window_chars = 20;
        let source = ElementSource {
            elements: vec![element(
                "repeat",
                "p0001",
                [100, 100, 700, 200],
                Some("first target then target"),
            )],
            spans: Vec::new(),
            coordinate_origin: CoordinateOrigin::TopLeft,
        };
        let report = verify_claims(
            &source,
            CitationInput::Envelope(CitationEnvelope {
                document_fingerprint: source.fingerprint(),
                claims: vec![claim(
                    ClaimKind::Quote,
                    Some("target"),
                    Citation {
                        element_id: Some("repeat".into()),
                        ..Default::default()
                    },
                )],
            }),
            &config,
            "0".repeat(64),
            "1".repeat(64),
        );

        let echo = report.checks[0].context_echo.as_ref().unwrap();
        assert_eq!(echo.before, "first ");
        assert_eq!(echo.matched, "target");
        assert_eq!(echo.after, " then target");
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

        // The joined match still grounds the check; the semantic_unverified bit it
        // now carries keeps the report gate closed.
        assert!(!report.all_evidence_grounded);
        assert!(report.checks[0].semantic_unverified);
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
    fn conflicting_primary_locators_and_supplemental_pages_fail_closed() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![
                claim(
                    ClaimKind::Quote,
                    Some("Revenue grew"),
                    Citation {
                        page: Some("p9999".into()),
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                ),
                claim(
                    ClaimKind::Presence,
                    None,
                    Citation {
                        span_id: Some("s000002".into()),
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                ),
                claim(
                    ClaimKind::TableCell,
                    Some("$12.4M"),
                    Citation {
                        page: Some("p9999".into()),
                        table_id: Some("t0001".into()),
                        cell: Some(CellRef { row: 1, col: 1 }),
                        ..Default::default()
                    },
                ),
            ],
        );

        assert!(!report.all_evidence_grounded);
        for check in &report.checks {
            assert_eq!(check.status, CheckStatus::Error);
            assert_eq!(check.reason, Some(CheckReason::LocatorConflict));
        }
    }

    #[test]
    fn agreeing_supplemental_pages_still_ground() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![
                claim(
                    ClaimKind::Quote,
                    Some("Revenue grew"),
                    Citation {
                        page: Some("p0001".into()),
                        element_id: Some("e000002".into()),
                        ..Default::default()
                    },
                ),
                claim(
                    ClaimKind::Presence,
                    None,
                    Citation {
                        page: Some("p0001".into()),
                        span_id: Some("s000002".into()),
                        ..Default::default()
                    },
                ),
            ],
        );

        assert!(report.all_evidence_grounded);
        assert!(report
            .checks
            .iter()
            .all(|check| check.status == CheckStatus::Grounded));
    }

    #[test]
    fn split_quote_requires_known_coordinates_for_adjacent_join() {
        let report = verify_elements_with_origin(
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
            CoordinateOrigin::Unknown,
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::CapabilityBlocked);
        assert_eq!(
            report.checks[0].reason,
            Some(CheckReason::UnknownCoordinateOrigin)
        );
        assert!(report.checks[0]
            .warnings
            .contains(&WarningCode::CapabilityLimited));
    }

    #[test]
    fn single_element_quote_does_not_require_known_coordinates() {
        let report = verify_elements_with_origin(
            vec![element(
                "only",
                "p0001",
                [100, 100, 700, 200],
                Some("The complete grounded quote"),
            )],
            vec![claim(
                ClaimKind::Quote,
                Some("The complete grounded quote"),
                Citation {
                    element_id: Some("only".into()),
                    ..Default::default()
                },
            )],
            CoordinateOrigin::Unknown,
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
    }

    #[test]
    fn wrong_quote_returns_mismatch_on_unknown_coordinate_origin() {
        // The cited element does not contain the quote, and no reading-order neighbour joins
        // with it to produce one. No adjacency ruling could ground this claim, so an unknown
        // coordinate origin cannot change the outcome and the determinate negative stands.
        // Before this gate ordering, every such claim returned `capability_blocked` and the
        // sound `mismatch` was discarded.
        let report = verify_elements_with_origin(
            vec![
                element(
                    "appraised-value",
                    "p0001",
                    [100, 100, 400, 200],
                    Some("Appraised value $485,000"),
                ),
                element(
                    "effective-date",
                    "p0001",
                    [400, 100, 700, 200],
                    Some("Effective date 12 March 2026"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("Appraised value $458,000"),
                Citation {
                    element_id: Some("appraised-value".into()),
                    ..Default::default()
                },
            )],
            CoordinateOrigin::Unknown,
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(report.checks[0].reason, Some(CheckReason::TextMismatch));
        assert!(!report.checks[0]
            .warnings
            .contains(&WarningCode::CapabilityLimited));
    }

    #[test]
    fn unknown_origin_quote_spanning_a_page_break_returns_mismatch() {
        // The neighbour would join textually, but it sits on the next page and the join never
        // crosses pages. Geometry is therefore not load-bearing and the answer is determinate,
        // so this must not be reported as a capability limit.
        let report = verify_elements_with_origin(
            vec![
                element(
                    "page-one-tail",
                    "p0001",
                    [100, 600, 400, 700],
                    Some("The alpha trust loop verifies "),
                ),
                element(
                    "page-two-head",
                    "p0002",
                    [100, 100, 400, 200],
                    Some("grounded evidence"),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("The alpha trust loop verifies grounded evidence"),
                Citation {
                    element_id: Some("page-one-tail".into()),
                    ..Default::default()
                },
            )],
            CoordinateOrigin::Unknown,
        );

        assert!(!report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
    }

    #[test]
    fn adjacent_join_never_crosses_pages() {
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
                    "p0002",
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

    fn verify_elements_with_config(
        elements: Vec<GroundingElement>,
        claims: Vec<Claim>,
        cfg: &VerificationConfig,
    ) -> VerificationReport {
        let source = ElementSource {
            elements,
            spans: Vec::new(),
            coordinate_origin: CoordinateOrigin::TopLeft,
        };
        let citations = CitationInput::Envelope(CitationEnvelope {
            document_fingerprint: source.fingerprint(),
            claims,
        });
        verify_claims(&source, citations, cfg, "0".repeat(64), "1".repeat(64))
    }

    fn unicode_compat_config() -> VerificationConfig {
        let mut config = VerificationConfig::default_v1();
        config.matching.text_normalization = TextNormalization::UnicodeCompatV1;
        config
    }

    #[test]
    fn quote_claim_page_only_locator_grounds_when_one_element_contains_it() {
        let report = verify_elements(
            vec![
                element("intro", "p0001", [100, 100, 400, 200], Some("Introduction")),
                element(
                    "body",
                    "p0001",
                    [100, 300, 700, 400],
                    Some("The alpha trust loop verifies grounded evidence."),
                ),
            ],
            vec![claim(
                ClaimKind::Quote,
                Some("verifies grounded evidence"),
                Citation {
                    page: Some("p0001".into()),
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
        // The page was searched and one element held the quote, so the tier says
        // element precision — a page-only citation no longer reports a comparison
        // that never ran, in either direction.
        assert_eq!(
            report.checks[0].evidence_tier,
            Some(EvidenceTier::ElementScoped)
        );
    }

    #[test]
    fn presence_claim_page_only_locator_stays_page_scoped() {
        let report = verify_elements(
            vec![element("a", "p0001", [100, 100, 400, 200], Some("text"))],
            vec![claim(
                ClaimKind::Presence,
                None,
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            report.checks[0].evidence_tier,
            Some(EvidenceTier::PageScoped)
        );
    }

    #[test]
    fn unicode_compat_profile_grounds_extraction_artifacts_the_default_profile_rejects() {
        let elements = vec![element(
            "e1",
            "p0001",
            [100, 100, 700, 200],
            // What PDF extraction actually emits: NBSP, curly quotes, an ffi
            // ligature, a soft-hyphenated line break, and an en dash.
            Some("Revenue\u{00A0}grew \u{2018}e\u{FB03}cient\u{2019} evi\u{00AD}dence \u{2013} 5"),
        )];
        // What a model quoting the same words types.
        let quote = "Revenue grew 'efficient' evidence - 5";
        let citation = Citation {
            element_id: Some("e1".into()),
            ..Default::default()
        };

        let default_profile = verify_elements(
            elements.clone(),
            vec![claim(ClaimKind::Quote, Some(quote), citation.clone())],
        );
        assert_eq!(default_profile.checks[0].status, CheckStatus::Mismatch);

        let unicode_profile = verify_elements_with_config(
            elements,
            vec![claim(ClaimKind::Quote, Some(quote), citation)],
            &unicode_compat_config(),
        );
        assert!(unicode_profile.all_evidence_grounded);
        assert_eq!(unicode_profile.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            unicode_profile.checks[0].match_method,
            MatchMethod::NormalizedTextContains
        );
    }

    #[test]
    fn unicode_compat_profile_never_grounds_a_paraphrase() {
        let report = verify_elements_with_config(
            vec![element(
                "e1",
                "p0001",
                [100, 100, 700, 200],
                Some("We will approve the request."),
            )],
            vec![claim(
                ClaimKind::Quote,
                Some("We may approve the request."),
                Citation {
                    element_id: Some("e1".into()),
                    ..Default::default()
                },
            )],
            &unicode_compat_config(),
        );

        assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
        assert_eq!(report.checks[0].reason, Some(CheckReason::TextMismatch));
    }

    #[test]
    fn unicode_compat_normalize_and_mapped_text_agree() {
        // The verdict path (normalize_quote_unicode_compat_v1) and the echo path
        // (mapped_text) are two consumers of one fold table; this pins that they
        // stay one profile. Probes cover every fold class plus the whitespace and
        // trim edges.
        let probes = [
            "it\u{2019}s",
            "\u{201C}quoted\u{201D}",
            "\u{201A}a\u{2018}b\u{201B}c\u{201F}d\u{201E}e",
            "2019\u{2013}2020 \u{2014} \u{2212}5 \u{2010}\u{2011}\u{2012}\u{2015}",
            "a\u{2026}b",
            "e\u{FB03}cient \u{FB00}\u{FB01}\u{FB02}\u{FB04}\u{FB05}\u{FB06}",
            "evi\u{00AD}dence a\u{200B}b \u{FEFF}c",
            "a\u{00A0}\u{00A0}b\u{3000}c\u{000B}d\u{2028}e",
            "  leading and trailing  ",
            "a \u{00AD} b",
            "",
            "plain ascii text",
        ];
        for probe in probes {
            assert_eq!(
                normalize_quote_unicode_compat_v1(probe),
                mapped_text(probe, TextNormalization::UnicodeCompatV1, true).text,
                "normalize and mapped_text disagree on {probe:?}"
            );
        }
        // Case-insensitive agreement too, minus the one known boundary shared with
        // collapse_whitespace: text_matches lowercases the whole normalized string
        // (str::to_lowercase, which applies the Greek final-sigma context rule)
        // while mapped_text lowercases per character. Its only effect is a grounded
        // check echoing no context when a final sigma ends the match; no probe here
        // contains sigma, so the two paths must agree exactly.
        for probe in probes {
            assert_eq!(
                normalize_quote_unicode_compat_v1(probe).to_lowercase(),
                mapped_text(probe, TextNormalization::UnicodeCompatV1, false).text,
                "case-insensitive normalize and mapped_text disagree on {probe:?}"
            );
        }
    }

    #[test]
    fn unicode_compat_context_echo_maps_a_folded_match_back_to_source_bytes() {
        let mut config = hardened_config();
        config.matching.text_normalization = TextNormalization::UnicodeCompatV1;
        let report = verify_elements_with_config(
            vec![element(
                "e1",
                "p0001",
                [100, 100, 700, 200],
                Some("the e\u{FB03}cient\u{00A0}engine wins"),
            )],
            vec![claim(
                ClaimKind::Quote,
                Some("efficient engine"),
                Citation {
                    element_id: Some("e1".into()),
                    ..Default::default()
                },
            )],
            &config,
        );

        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        let echo = report.checks[0]
            .context_echo
            .as_ref()
            .expect("hardened config echoes context");
        // The echo quotes the source as extracted — ligature and NBSP intact —
        // because the fold maps every normalized character back to the source
        // bytes it came from.
        assert_eq!(echo.matched, "e\u{FB03}cient\u{00A0}engine");
    }

    #[test]
    fn claim_text_the_fold_erases_entirely_never_grounds() {
        // A lone soft hyphen passes the pre-claim gate (it is not Unicode
        // whitespace) but normalizes to "" under unicode_compat_v1, and
        // contains("") is true of every element — so without the fail-closed guard
        // this claim would ground anywhere, element-cited or page-scanned.
        for citation in [
            Citation {
                element_id: Some("e1".into()),
                ..Default::default()
            },
            Citation {
                page: Some("p0001".into()),
                ..Default::default()
            },
        ] {
            let report = verify_elements_with_config(
                vec![element("e1", "p0001", [100, 100, 700, 200], Some("text"))],
                vec![claim(ClaimKind::Quote, Some("\u{00AD}"), citation)],
                &unicode_compat_config(),
            );
            assert!(!report.all_evidence_grounded);
            assert_eq!(report.checks[0].status, CheckStatus::Mismatch);
            assert_eq!(report.checks[0].reason, Some(CheckReason::TextMismatch));
        }
    }

    #[test]
    fn presence_claim_with_text_and_page_locator_stays_page_scoped() {
        // The wire schema permits text on a presence claim; the page scan must not
        // use it to upgrade the evidence to an element the claim never named.
        let report = verify_elements(
            vec![element("e1", "p0001", [100, 100, 700, 200], Some("text"))],
            vec![claim(
                ClaimKind::Presence,
                Some("text"),
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )],
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(
            report.checks[0].evidence_tier,
            Some(EvidenceTier::PageScoped)
        );
    }

    #[test]
    fn quote_claim_page_only_locator_grounds_from_a_span_when_no_element_matches() {
        let source = ElementSource {
            elements: vec![element(
                "e1",
                "p0001",
                [100, 100, 400, 200],
                Some("unrelated prose"),
            )],
            spans: vec![GroundingSpan {
                id: "s1".into(),
                page: "p0001".into(),
                bbox: Some([100, 300, 400, 380]),
                text: "the quoted sentence survives".into(),
                element: Some("e1".into()),
                char_start: None,
                char_end: None,
            }],
            coordinate_origin: CoordinateOrigin::TopLeft,
        };
        let citations = CitationInput::Envelope(CitationEnvelope {
            document_fingerprint: source.fingerprint(),
            claims: vec![claim(
                ClaimKind::Quote,
                Some("quoted sentence"),
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )],
        });
        let report = verify_claims(
            &source,
            citations,
            &VerificationConfig::default_v1(),
            "0".repeat(64),
            "1".repeat(64),
        );

        assert!(report.all_evidence_grounded);
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            report.checks[0].evidence_tier,
            Some(EvidenceTier::ExactSpan)
        );
    }

    #[test]
    fn a_page_less_office_source_grounds_a_quote_by_element_id() {
        // The end of the strand: an office artifact entering by the wire (schema
        // 1.1.0), and a quote grounding against it by element id — no page, no
        // bbox, no invented geometry anywhere. Evidence precision is element
        // scope, which is exactly what a page-less address can honestly claim.
        let artifact = r#"{"artifact_type":"ethos.grounding.v1","schema_version":"1.1.0","source":{"media_type":"application/vnd.openxmlformats-officedocument.wordprocessingml.document","sha256":"sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"},"producer":{"name":"ethos-engine","version":"0.39.0"},"capabilities":{"spans":false,"char_offsets":false,"tables":false},"coordinate_system":{"unit":"centipoint","origin":"top-left"},"pages":[],"elements":[{"id":"s1","kind":"text_run","locator":"{\"paragraph\":1,\"part\":\"word/document.xml\",\"run\":1}","text":"Revenue grew to $12.4M in Q3 2025"}]}"#;
        let source = ethos_core::grounding_json::parse_grounding_json(artifact.as_bytes()).unwrap();
        let cfg = VerificationConfig::default_v1();
        let citations = CitationInput::Envelope(CitationEnvelope {
            document_fingerprint: source.fingerprint(),
            claims: vec![claim(
                ClaimKind::Quote,
                Some("Revenue grew"),
                Citation {
                    element_id: Some("s1".into()),
                    ..Default::default()
                },
            )],
        });
        let report = verify_claims(&source, citations, &cfg, "0".repeat(64), "1".repeat(64));
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(
            report.checks[0].evidence_tier,
            Some(EvidenceTier::ElementScoped)
        );
    }

    #[test]
    fn verify_claims_indexed_report_equals_the_unindexed_wrapper() {
        let elements = vec![element(
            "e1",
            "p0001",
            [100, 100, 700, 200],
            Some("Revenue grew to $12.4M in Q3 2025"),
        )];
        let claims = vec![claim(
            ClaimKind::Quote,
            Some("Revenue grew"),
            Citation {
                page: Some("p0001".into()),
                ..Default::default()
            },
        )];
        let source = ElementSource {
            elements: elements.clone(),
            spans: Vec::new(),
            coordinate_origin: CoordinateOrigin::TopLeft,
        };
        let cfg = VerificationConfig::default_v1();
        let citations = || {
            CitationInput::Envelope(CitationEnvelope {
                document_fingerprint: source.fingerprint(),
                claims: claims.clone(),
            })
        };
        let wrapped = verify_claims(&source, citations(), &cfg, "0".repeat(64), "1".repeat(64));
        let index = SourceIndex::for_verification(&source, &cfg);
        let indexed = verify_claims_indexed(
            &source,
            &index,
            citations(),
            &cfg,
            "0".repeat(64),
            "1".repeat(64),
        );
        assert_eq!(wrapped, indexed);
    }

    #[test]
    fn nearest_match_names_the_near_miss_and_stays_off_the_verdict() {
        let mut config = unicode_compat_config();
        config.schema_version = HARDENED_VERIFICATION_SCHEMA_VERSION.to_string();
        config.hardening = Some(HardeningOptions {
            include_provenance: false,
            include_context_echo: false,
            include_dispersion: false,
            context_window_chars: 0,
            include_nearest_match: true,
        });
        let elements = vec![
            element("intro", "p0001", [100, 100, 400, 200], Some("Introduction")),
            element(
                "body",
                "p0001",
                [100, 300, 700, 400],
                Some("Operating revenue grew to $12.4M in Q3 2025"),
            ),
        ];

        // One word off: the diagnostic names the culprit element with a high
        // score, and the verdict is still a mismatch.
        let near_miss = verify_elements_with_config(
            elements.clone(),
            vec![claim(
                ClaimKind::Quote,
                Some("Operating revenue grew to $12.5M in Q3 2025"),
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )],
            &config,
        );
        assert_eq!(near_miss.checks[0].status, CheckStatus::Mismatch);
        let nearest = near_miss.checks[0]
            .nearest_match
            .as_ref()
            .expect("near miss carries a diagnostic");
        assert_eq!(nearest.element_id.as_deref(), Some("body"));
        assert_eq!(nearest.method, "token_jaccard_v1");
        assert!(
            nearest.similarity_bp >= 7000,
            "one token off should score high, got {}",
            nearest.similarity_bp
        );

        // A fabricated quote scores near zero — same field, opposite triage.
        let fabricated = verify_elements_with_config(
            elements,
            vec![claim(
                ClaimKind::Quote,
                Some("The board approved the merger unanimously"),
                Citation {
                    page: Some("p0001".into()),
                    ..Default::default()
                },
            )],
            &config,
        );
        let nearest = fabricated.checks[0]
            .nearest_match
            .as_ref()
            .expect("fabrication still gets a best candidate");
        assert!(
            nearest.similarity_bp <= 2000,
            "unrelated text should score low, got {}",
            nearest.similarity_bp
        );
    }

    #[test]
    fn nearest_match_is_absent_without_the_flag_and_on_grounded_checks() {
        let elements = vec![element(
            "e1",
            "p0001",
            [100, 100, 700, 200],
            Some("Revenue grew to $12.4M in Q3 2025"),
        )];
        let default_profile = verify_elements(
            elements.clone(),
            vec![claim(
                ClaimKind::Quote,
                Some("nothing like the document"),
                Citation {
                    element_id: Some("e1".into()),
                    ..Default::default()
                },
            )],
        );
        assert!(default_profile.checks[0].nearest_match.is_none());

        let mut config = VerificationConfig::default_v1();
        config.schema_version = HARDENED_VERIFICATION_SCHEMA_VERSION.to_string();
        config.hardening = Some(HardeningOptions {
            include_provenance: false,
            include_context_echo: false,
            include_dispersion: false,
            context_window_chars: 0,
            include_nearest_match: true,
        });
        let grounded = verify_elements_with_config(
            elements,
            vec![claim(
                ClaimKind::Quote,
                Some("Revenue grew"),
                Citation {
                    element_id: Some("e1".into()),
                    ..Default::default()
                },
            )],
            &config,
        );
        assert_eq!(grounded.checks[0].status, CheckStatus::Grounded);
        assert!(grounded.checks[0].nearest_match.is_none());
    }

    #[test]
    fn adjacency_gap_tolerance_joins_fragments_the_exact_rule_refuses() {
        let elements = vec![
            element(
                "split-a",
                "p0001",
                [100, 100, 400, 200],
                Some("The alpha trust loop verifies "),
            ),
            // A 30q gap between the facing edges — real extractors leave one.
            element(
                "split-b",
                "p0001",
                [430, 100, 700, 200],
                Some("grounded evidence"),
            ),
        ];
        let quote = claim(
            ClaimKind::Quote,
            Some("The alpha trust loop verifies grounded evidence"),
            Citation {
                element_id: Some("split-a".into()),
                ..Default::default()
            },
        );

        let exact_rule = verify_elements(elements.clone(), vec![quote.clone()]);
        assert_eq!(exact_rule.checks[0].status, CheckStatus::Mismatch);

        let mut config = VerificationConfig::default_v1();
        config.matching.adjacency_gap_tolerance_q = Some(50);
        let tolerant = verify_elements_with_config(elements.clone(), vec![quote.clone()], &config);
        assert_eq!(tolerant.checks[0].status, CheckStatus::Grounded);
        // Joined evidence still carries the semantic bit and holds the gate.
        assert!(tolerant.checks[0].semantic_unverified);
        assert!(!tolerant.all_evidence_grounded);

        // Some(0) is the exact rule by another spelling, not a third behavior.
        let mut zero = VerificationConfig::default_v1();
        zero.matching.adjacency_gap_tolerance_q = Some(0);
        let explicit_zero = verify_elements_with_config(elements, vec![quote.clone()], &zero);
        assert_eq!(explicit_zero.checks[0].status, CheckStatus::Mismatch);

        // The tolerance is on the absolute edge distance, so a slight overlap —
        // which real extractors also produce — joins under the same knob.
        let overlapping = vec![
            element(
                "split-a",
                "p0001",
                [100, 100, 400, 200],
                Some("The alpha trust loop verifies "),
            ),
            element(
                "split-b",
                "p0001",
                [370, 100, 700, 200],
                Some("grounded evidence"),
            ),
        ];
        let mut config = VerificationConfig::default_v1();
        config.matching.adjacency_gap_tolerance_q = Some(50);
        let overlapped = verify_elements_with_config(overlapping, vec![quote], &config);
        assert_eq!(overlapped.checks[0].status, CheckStatus::Grounded);
        assert!(overlapped.checks[0].semantic_unverified);
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

        // Grounded via the sanctioned join, so the check carries
        // semantic_unverified and the gate stays closed.
        assert!(!report.all_evidence_grounded);
        assert!(report.checks[0].semantic_unverified);
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
            "1".repeat(64),
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
            "1".repeat(64),
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
            "1".repeat(64),
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
            structure: false,
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
            "1".repeat(64),
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
