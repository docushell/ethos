import type {
  EthosAppAnswerReleaseDecision,
  EthosCitationClaim,
  EthosLlmCitationOutput,
  EthosVerificationReport,
} from "../types";

const answerRelease: EthosAppAnswerReleaseDecision = {
  artifact_type: "ethos.app_answer_release_decision.v1",
  schema_version: "1.1.0",
  question: "What is grounded?",
  grounding: {
    verification_report_ref: "verification-report.json",
    proof_status: "unverified",
    request_certified: false,
    reusable_grounded_check_ids: [],
    needs_review_check_ids: [],
    proof_limitations: ["capability_limited"],
  },
  app_status: "claim_support_needs_review",
  claims: [{
    id: "claim-1",
    text: "A claim requiring review.",
    citation_grounded: true,
    question_relevance: "direct_answer",
    claim_type: "source_fact",
    claim_support: "not_evaluated",
    release_action: "needs_review",
    release_reason: "claim_support_not_evaluated",
  }],
  final_answer_claim_ids: [],
  review_claim_ids: ["claim-1"],
  blocked_claim_ids: [],
};

const report: EthosVerificationReport = {
  schema_version: "1.1.0",
  verification_config_sha256: "0".repeat(64),
  grounding: {
    parser: { name: "consumer-parser", version: "1.0.0" },
    capabilities: {
      spans: false,
      char_offsets: false,
      tables: false,
      fingerprint: false,
      coordinate_origin: "unknown",
      crop_support: false,
    },
  },
  capability_limits: ["missing_fingerprint"],
  fingerprint_stale: false,
  all_evidence_grounded: false,
  checks: [],
  unsupported_claim_kinds: [],
  warnings: ["capability_limited"],
};

const claim: EthosCitationClaim = {
  kind: "quote",
  text: "Grounded text",
  element_id: "element-1",
};

const emission: EthosLlmCitationOutput = {
  schema_version: "1.0.0",
  answer: "An answer with a citation.",
  claims: [claim],
};

// These accesses mirror the fields DocuShell's evidence policy consumes.
report.checks.map((check) => ({
  id: check.id,
  status: check.status,
  semanticUnverified: check.semantic_unverified,
  warnings: check.warnings,
}));
emission.claims.map((item) => item.kind);
answerRelease.claims.map((item) => item.claim_support);

// @ts-expect-error citation claims fail closed when no locator is present.
const missingLocator: EthosCitationClaim = { kind: "quote", text: "No source" };
void missingLocator;

// @ts-expect-error only report schema versions represented by the source schema are accepted.
report.schema_version = "2.0.0";
