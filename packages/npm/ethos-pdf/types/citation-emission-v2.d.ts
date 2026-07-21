// Generated from the Ethos JSON Schemas. Do not edit by hand.
// Runtime JSON Schema validation remains authoritative.
// Ethos verifies citation grounding, not semantic truth.

export type EthosEvidenceHandleCitationClaim = EthosEvidenceHandleTextualCitation | EthosEvidenceHandlePresenceCitation;
export type EthosEvidenceHandleCitationText = string;
export type EthosEvidenceHandleCitationId = string;

/**
 * Structured claims[].evidence_id values are the only citation channel. The answer is untrusted prose: consumers must not infer, link, or mark verified any handle-shaped token found only in answer text.
 */
export interface EthosLlmCitationOutputV2 {
  schema_version: "2.0.0";
  answer: string;
  /**
   * @minItems 1
   * @maxItems 256
   */
  claims: [EthosEvidenceHandleCitationClaim, ...EthosEvidenceHandleCitationClaim[]];
}
export interface EthosEvidenceHandleTextualCitation {
  kind: "quote" | "value" | "table_cell";
  text: EthosEvidenceHandleCitationText;
  evidence_id: EthosEvidenceHandleCitationId;
}
export interface EthosEvidenceHandlePresenceCitation {
  kind: "presence";
  evidence_id: EthosEvidenceHandleCitationId;
}
