// Generated from the Ethos JSON Schemas. Do not edit by hand.
// Runtime JSON Schema validation remains authoritative.
// Ethos verifies citation grounding, not semantic truth.

export type EthosEvidenceHandleId = string;
export type EthosEvidenceHandleLocator =
  | {
      page: EthosEvidenceHandleId;
    }
  | {
      element_id: EthosEvidenceHandleId;
      page?: EthosEvidenceHandleId;
    }
  | {
      span_id: EthosEvidenceHandleId;
      page?: EthosEvidenceHandleId;
    }
  | {
      table_id: EthosEvidenceHandleId;
      cell: EthosEvidenceHandleCell;
      page?: EthosEvidenceHandleId;
    };

export interface EthosEvidenceHandleContext {
  artifact_type: "ethos.evidence_handle_context.v1";
  schema_version: "1.0.0";
  document_fingerprint: string;
  /**
   * @minItems 1
   * @maxItems 1024
   */
  evidence: [EthosEvidenceHandle, ...EthosEvidenceHandle[]];
}
export interface EthosEvidenceHandle {
  evidence_id: EthosEvidenceHandleId;
  locator: EthosEvidenceHandleLocator;
  display?: string;
  excerpt?: string;
}
export interface EthosEvidenceHandleCell {
  row: number;
  col: number;
}
