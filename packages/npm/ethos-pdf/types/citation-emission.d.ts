// Generated from the Ethos JSON Schemas. Do not edit by hand.
// Runtime JSON Schema validation remains authoritative.
// Ethos verifies citation grounding, not semantic truth.

export type EthosCitationClaim =
  EthosCitationQuote | EthosCitationValue | EthosCitationPresence | EthosCitationTableCell;
export type EthosCitationQuote =
  | {
      kind: "quote";
      text: EthosCitationText;
      page?: EthosCitationSourceId;
      element_id: EthosCitationSourceId;
    }
  | {
      kind: "quote";
      text: EthosCitationText;
      page?: EthosCitationSourceId;
      span_id: EthosCitationSourceId;
    }
  | {
      kind: "quote";
      text: EthosCitationText;
      page: EthosCitationSourceId;
    };
export type EthosCitationText = string;
/**
 * An identifier copied from the retrieval context. Its namespace and stricter syntax belong to the selected GroundingSource.
 */
export type EthosCitationSourceId = string;
export type EthosCitationValue =
  | {
      kind: "value";
      text: EthosCitationText;
      page?: EthosCitationSourceId;
      element_id: EthosCitationSourceId;
    }
  | {
      kind: "value";
      text: EthosCitationText;
      page?: EthosCitationSourceId;
      span_id: EthosCitationSourceId;
    }
  | {
      kind: "value";
      text: EthosCitationText;
      page: EthosCitationSourceId;
    };
export type EthosCitationPresence =
  | {
      kind: "presence";
      page?: EthosCitationSourceId;
      element_id: EthosCitationSourceId;
    }
  | {
      kind: "presence";
      page?: EthosCitationSourceId;
      span_id: EthosCitationSourceId;
    }
  | {
      kind: "presence";
      page: EthosCitationSourceId;
    };

/**
 * Application-layer structured output emitted by a model or framework callback before deterministic hydration into ethos-citations. It is versioned independently from verification reports and deliberately excludes fingerprints and bounding boxes.
 */
export interface EthosLlmCitationOutput {
  schema_version: "1.0.0";
  answer: string;
  /**
   * @minItems 1
   * @maxItems 256
   */
  claims: [EthosCitationClaim, ...EthosCitationClaim[]];
}
export interface EthosCitationTableCell {
  kind: "table_cell";
  text: EthosCitationText;
  page?: EthosCitationSourceId;
  table_id: EthosCitationSourceId;
  cell: EthosCitationCell;
}
export interface EthosCitationCell {
  row: number;
  col: number;
}
