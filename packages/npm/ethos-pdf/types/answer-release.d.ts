// Generated from the Ethos JSON Schemas. Do not edit by hand.
// Runtime JSON Schema validation remains authoritative.
// Ethos verifies citation grounding, not semantic truth.

export type EthosProofStatus = "verified" | "partially_verified" | "unverified";
export type EthosProofLimitation =
  "capability_limited" | "stale_fingerprint" | "unsupported_claim_kind" | "non_grounded_checks" | "semantic_unverified";
export type EthosAppStatus =
  | "certified"
  | "partial_certified"
  | "supported_synthesis_needs_review"
  | "grounded_but_irrelevant"
  | "claim_support_needs_review"
  | "claim_support_rejected"
  | "cannot_answer_from_sources";
export type EthosQuestionRelevance = "direct_answer" | "supports_answer" | "background_only" | "unrelated";
export type EthosClaimType = "source_fact" | "synthesis";
export type EthosClaimSupport = "supported" | "unsupported" | "contradicted" | "not_evaluated";
export type EthosReleaseAction = "show_final" | "needs_review" | "block";
export type EthosReleaseReason =
  | "certified"
  | "supported_synthesis_needs_review"
  | "grounded_but_irrelevant"
  | "claim_support_not_evaluated"
  | "unsupported_claim"
  | "contradicted_claim"
  | "cannot_answer_from_sources";

/**
 * Non-canonical wrapper artifact for applications that combine Ethos citation-grounding proof summaries with app-owned question relevance and synthesis policy. This is not verification_report.json and is not emitted by the verifier.
 */
export interface EthosAppAnswerReleaseDecision {
  artifact_type: "ethos.app_answer_release_decision.v1";
  schema_version: "1.1.0";
  /**
   * Original user question evaluated by the app-layer relevance policy.
   */
  question: string;
  grounding: {
    /**
     * Application-local pointer to the canonical verification_report.json used for audit.
     */
    verification_report_ref: string;
    proof_status: EthosProofStatus;
    request_certified: boolean;
    reusable_grounded_check_ids: string[];
    needs_review_check_ids: string[];
    proof_limitations: EthosProofLimitation[];
  };
  app_status: EthosAppStatus;
  /**
   * Application claim decisions. Claim ids must be unique within this array; helper APIs enforce id-level uniqueness.
   */
  claims: EthosClaimDecision[];
  final_answer_claim_ids: string[];
  review_claim_ids: string[];
  blocked_claim_ids: string[];
  notes?: string[];
}
export interface EthosClaimDecision {
  /**
   * Stable application claim id. Each id must be unique within the claims array.
   */
  id: string;
  text: string;
  /**
   * One or more Ethos verification check IDs used by this claim.
   *
   * @minItems 1
   */
  check_ids?: [string, ...string[]];
  citation_grounded: boolean;
  question_relevance: EthosQuestionRelevance;
  claim_type?: EthosClaimType;
  claim_support: EthosClaimSupport;
  release_action: EthosReleaseAction;
  release_reason: EthosReleaseReason;
}
