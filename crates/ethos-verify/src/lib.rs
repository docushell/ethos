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
//! Milestone A ships the crate boundary + capability-downgrade plumbing so CI can prove
//! invariant 4 (this crate compiles against the trait module alone) from the first
//! commit. The check engine lands as the Milestone B alpha (WS-VERIFY-ALPHA).

#![forbid(unsafe_code)]
#![warn(missing_docs)]

use ethos_core::codes::WarningCode;
use ethos_core::grounding::{CoordinateOrigin, GroundingSource};
use ethos_core::verify_types::{
    compute_all_evidence_grounded, Check, GroundingMeta, VerificationConfig, VerificationReport,
};

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
        warnings.push(WarningCode::CapabilityLimited);
    }
    if !caps.spans {
        warnings.push(WarningCode::CapabilityLimited);
    }
    if caps.coordinate_origin == CoordinateOrigin::Unknown {
        warnings.push(WarningCode::CapabilityLimited);
    }
    warnings
}

/// Milestone A placeholder run: validates the wiring end-to-end and emits a
/// schema-valid report with **no checks** — `all_evidence_grounded` is therefore
/// always `false` (the PRD §8 gate requires at least one supported grounded check).
/// The real check engine replaces the body in Milestone B (WS-VERIFY-ALPHA).
pub fn verify_skeleton(
    source: &dyn GroundingSource,
    config: &VerificationConfig,
    config_sha256: String,
) -> VerificationReport {
    let checks: Vec<Check> = Vec::new();
    let unsupported: Vec<String> = Vec::new();
    let fingerprint_stale = false;
    VerificationReport {
        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
        document_fingerprint: source.fingerprint(),
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

#[cfg(test)]
mod tests {
    use super::*;
    use ethos_core::grounding::{Capabilities, GroundingElement, PageGeometry, ParserIdentity};

    struct Foreign;
    impl GroundingSource for Foreign {
        fn parser(&self) -> ParserIdentity {
            ParserIdentity {
                name: "foreign-parser".into(),
                version: "9.9.9".into(),
                adapter: Some("test".into()),
                adapter_version: Some("0.0.1".into()),
            }
        }
        fn capabilities(&self) -> Capabilities {
            Capabilities {
                spans: false,
                char_offsets: false,
                fingerprint: false,
                coordinate_origin: CoordinateOrigin::Unknown,
                crop_support: false,
            }
        }
        fn fingerprint(&self) -> Option<String> {
            None
        }
        fn pages(&self) -> Vec<PageGeometry> {
            vec![]
        }
        fn elements(&self) -> Vec<GroundingElement> {
            vec![]
        }
    }

    #[test]
    fn skeleton_report_is_schema_shaped_and_never_grounded() {
        let cfg = VerificationConfig::default_v1();
        let report = verify_skeleton(&Foreign, &cfg, "0".repeat(64));
        assert!(
            !report.all_evidence_grounded,
            "empty check set can never ground"
        );
        assert!(report.warnings.contains(&WarningCode::CapabilityLimited));
        assert!(report.document_fingerprint.is_none());
        // serializes (schema-shape sanity; full schema validation runs in CI via python)
        let v = serde_json::to_value(&report).unwrap();
        assert_eq!(v["grounding"]["parser"]["name"], "foreign-parser");
        assert_eq!(v["fingerprint_stale"], false);
    }
}
