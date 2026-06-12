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

use ethos_core::codes::WarningCode;
use ethos_core::grounding::{
    CoordinateOrigin, GroundingCell, GroundingElement, GroundingSource, GroundingSpan,
    GroundingTable,
};
use ethos_core::verify_types::{
    compute_all_evidence_grounded, Check, CheckStatus, Claim, ClaimKind, Evidence, GroundingMeta,
    MatchMethod, TextNormalization, VerificationConfig, VerificationReport,
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
    let caps = source.capabilities();
    let mut warnings = Vec::new();
    if !caps.fingerprint && config.staleness.require_fingerprint_match {
        push_warning(&mut warnings, WarningCode::CapabilityLimited);
    }
    if !caps.spans {
        push_warning(&mut warnings, WarningCode::CapabilityLimited);
    }
    if !caps.char_offsets {
        push_warning(&mut warnings, WarningCode::CapabilityLimited);
    }
    if caps.coordinate_origin == CoordinateOrigin::Unknown {
        push_warning(&mut warnings, WarningCode::CapabilityLimited);
    }
    if !caps.crop_support {
        push_warning(&mut warnings, WarningCode::CapabilityLimited);
    }
    warnings
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
    let source_fingerprint = source.fingerprint();
    let fingerprint_stale = config.staleness.require_fingerprint_match
        && matches!(
            (citation_fingerprint.as_deref(), source_fingerprint.as_deref()),
            (Some(expected), Some(actual)) if expected != actual
        );
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
                claim,
                config,
                fingerprint_stale,
                include_text,
                include_crops,
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
            capabilities: source.capabilities(),
        },
        fingerprint_stale,
        all_evidence_grounded: compute_all_evidence_grounded(
            &checks,
            &unsupported,
            fingerprint_stale,
        ),
        checks,
        unsupported_claim_kinds: unsupported,
        warnings: capability_warnings(source, config),
    }
}

fn check_claim(
    id: usize,
    source: &dyn GroundingSource,
    claim: Claim,
    config: &VerificationConfig,
    fingerprint_stale: bool,
    include_text: bool,
    include_crops: bool,
    unsupported: &mut Vec<String>,
) -> Check {
    let mut warnings = Vec::new();
    let check_id = format!("v{id:04}");

    if !claim.citation.has_locator() {
        return Check {
            id: check_id,
            claim,
            status: CheckStatus::Error,
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
            match_method: MatchMethod::None,
            semantic_unverified: false,
            evidence: None,
            warnings,
        };
    }

    if fingerprint_stale {
        return Check {
            id: check_id,
            claim,
            status: CheckStatus::Stale,
            match_method: MatchMethod::None,
            semantic_unverified: false,
            evidence: None,
            warnings,
        };
    }

    let target = match resolve_target(source, &claim, config) {
        TargetResolution::Found(target) => target,
        TargetResolution::NotFound => {
            return Check {
                id: check_id,
                claim,
                status: CheckStatus::NotFound,
                match_method: MatchMethod::None,
                semantic_unverified: false,
                evidence: None,
                warnings,
            };
        }
        TargetResolution::CapabilityBlocked => {
            push_warning(&mut warnings, WarningCode::CapabilityLimited);
            return Check {
                id: check_id,
                claim,
                status: CheckStatus::CapabilityBlocked,
                match_method: MatchMethod::None,
                semantic_unverified: false,
                evidence: None,
                warnings,
            };
        }
    };

    let evidence = make_evidence(source, &target, include_text, include_crops);
    match claim.kind {
        ClaimKind::Presence => Check {
            id: check_id,
            claim,
            status: CheckStatus::Grounded,
            match_method: MatchMethod::PresenceOnly,
            semantic_unverified: false,
            evidence,
            warnings,
        },
        ClaimKind::Quote | ClaimKind::Value | ClaimKind::TableCell => {
            let method = text_match_method(config);
            let status = if let (Some(expected), Some(actual)) =
                (claim.text.as_deref(), target.text.as_deref())
            {
                if text_matches(expected, actual, config) {
                    CheckStatus::Grounded
                } else {
                    CheckStatus::Mismatch
                }
            } else {
                CheckStatus::Mismatch
            };
            Check {
                id: check_id,
                claim,
                status,
                match_method: if target.from_table_cell {
                    MatchMethod::TableCellLookup
                } else {
                    method
                },
                semantic_unverified: false,
                evidence,
                warnings,
            }
        }
        _ => unreachable!("unsupported kinds returned before matching"),
    }
}

fn is_supported_kind(kind: ClaimKind) -> bool {
    matches!(
        kind,
        ClaimKind::Quote | ClaimKind::Value | ClaimKind::Presence | ClaimKind::TableCell
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
}

enum TargetResolution {
    Found(FoundTarget),
    NotFound,
    CapabilityBlocked,
}

fn resolve_target(
    source: &dyn GroundingSource,
    claim: &Claim,
    config: &VerificationConfig,
) -> TargetResolution {
    if claim.kind == ClaimKind::TableCell || claim.citation.table_id.is_some() {
        return resolve_table_cell(source, claim);
    }

    if let Some(span_id) = claim.citation.span_id.as_deref() {
        if !source.capabilities().spans {
            return TargetResolution::CapabilityBlocked;
        }
        return source
            .spans()
            .into_iter()
            .find(|span| span.id == span_id)
            .map(target_from_span)
            .map(TargetResolution::Found)
            .unwrap_or(TargetResolution::NotFound);
    }

    if let Some(element_id) = claim.citation.element_id.as_deref() {
        return source
            .element_by_id(element_id)
            .map(target_from_element)
            .map(TargetResolution::Found)
            .unwrap_or(TargetResolution::NotFound);
    }

    if let (Some(page), Some(bbox)) = (claim.citation.page.as_deref(), claim.citation.bbox) {
        if source.capabilities().coordinate_origin == CoordinateOrigin::Unknown {
            return TargetResolution::CapabilityBlocked;
        }
        let tolerance = config.matching.bbox_containment_tolerance_q.unwrap_or(0);
        return source
            .elements()
            .into_iter()
            .find(|element| element.page == page && contains_bbox(element.bbox, bbox, tolerance))
            .map(target_from_element)
            .map(TargetResolution::Found)
            .unwrap_or(TargetResolution::NotFound);
    }

    if let Some(page) = claim.citation.page.as_deref() {
        return source
            .pages()
            .into_iter()
            .find(|candidate| candidate.id == page)
            .map(|found| {
                TargetResolution::Found(FoundTarget {
                    page: Some(found.id),
                    bbox: Some([0, 0, found.width, found.height]),
                    text: None,
                    from_table_cell: false,
                })
            })
            .unwrap_or(TargetResolution::NotFound);
    }

    TargetResolution::NotFound
}

fn target_from_element(element: GroundingElement) -> FoundTarget {
    FoundTarget {
        page: Some(element.page),
        bbox: Some(element.bbox),
        text: element.text,
        from_table_cell: false,
    }
}

fn target_from_span(span: GroundingSpan) -> FoundTarget {
    FoundTarget {
        page: Some(span.page),
        bbox: Some(span.bbox),
        text: Some(span.text),
        from_table_cell: false,
    }
}

fn resolve_table_cell(source: &dyn GroundingSource, claim: &Claim) -> TargetResolution {
    let Some(table_id) = claim.citation.table_id.as_deref() else {
        return TargetResolution::NotFound;
    };
    let Some(cell_ref) = claim.citation.cell else {
        return TargetResolution::NotFound;
    };
    let tables = source.tables();
    if tables.is_empty() {
        return TargetResolution::CapabilityBlocked;
    }
    tables
        .into_iter()
        .find(|table| table.id == table_id)
        .and_then(|table| target_from_table_cell(table, cell_ref.row, cell_ref.col))
        .map(TargetResolution::Found)
        .unwrap_or(TargetResolution::NotFound)
}

fn target_from_table_cell(table: GroundingTable, row: u32, col: u32) -> Option<FoundTarget> {
    table
        .cells
        .into_iter()
        .find(|cell| table_cell_covers(cell, row, col))
        .map(|cell| target_from_cell(table.page, cell))
}

fn table_cell_covers(cell: &GroundingCell, row: u32, col: u32) -> bool {
    let row_end = cell.row.saturating_add(cell.row_span.max(1));
    let col_end = cell.col.saturating_add(cell.col_span.max(1));
    row >= cell.row && row < row_end && col >= cell.col && col < col_end
}

fn target_from_cell(page: String, cell: GroundingCell) -> FoundTarget {
    FoundTarget {
        page: Some(page),
        bbox: Some(cell.bbox),
        text: Some(cell.text),
        from_table_cell: true,
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

fn text_match_method(config: &VerificationConfig) -> MatchMethod {
    match config.matching.text_normalization {
        TextNormalization::None => MatchMethod::ExactText,
        TextNormalization::CollapseWhitespace => MatchMethod::NormalizedText,
    }
}

fn text_matches(expected: &str, actual: &str, config: &VerificationConfig) -> bool {
    let (expected, actual) = match config.matching.text_normalization {
        TextNormalization::None => (expected.to_string(), actual.to_string()),
        TextNormalization::CollapseWhitespace => {
            (normalize_quote(expected), normalize_quote(actual))
        }
    };
    if config.matching.case_sensitive {
        actual.contains(&expected)
    } else {
        actual.to_lowercase().contains(&expected.to_lowercase())
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
    use ethos_core::verify_types::{CellRef, Citation, Claim};

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
                    fingerprint: true,
                    coordinate_origin: CoordinateOrigin::TopLeft,
                    crop_support: false,
                },
                fingerprint: Some(
                    "sha256:579dbf857db19649463cd6716a6f7c5f43c44dd9a5e798e47f25760f0ffaae02"
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
        assert_eq!(report.checks[0].status, CheckStatus::Grounded);
        assert_eq!(report.checks[0].match_method, MatchMethod::NormalizedText);
        assert_eq!(report.checks[1].status, CheckStatus::Grounded);
        assert_eq!(report.checks[1].match_method, MatchMethod::PresenceOnly);
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|e| e.text.as_deref()),
            Some("Revenue grew to $12.4M in Q3 2025, driven by enterprise expansion.")
        );
        assert!(report.warnings.contains(&WarningCode::CapabilityLimited));
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
        assert_eq!(report.checks[1].status, CheckStatus::NotFound);
    }

    #[test]
    fn value_claims_use_literal_text_matching() {
        let source = TestSource::default();
        let report = verify(
            &source,
            vec![claim(
                ClaimKind::Value,
                Some("$12.4M"),
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
        assert_eq!(report.checks[0].match_method, MatchMethod::None);
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
        assert_eq!(report.unsupported_claim_kinds, vec!["region"]);
    }

    #[test]
    fn missing_span_capability_blocks_span_locator() {
        let source = TestSource {
            caps: Capabilities {
                spans: false,
                char_offsets: false,
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
        assert!(report.warnings.contains(&WarningCode::CapabilityLimited));
        assert!(report.checks[0]
            .warnings
            .contains(&WarningCode::CapabilityLimited));
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
