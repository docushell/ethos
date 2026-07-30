// Generated from the Ethos JSON Schemas. Do not edit by hand.
// Runtime JSON Schema validation remains authoritative.
// Ethos verifies citation grounding, not semantic truth.

export type EthosGroundingValidationReport = {
  [k: string]: unknown;
} & {
  artifact_type: "ethos.grounding_validation.v1";
  schema_version: "1.0.0";
  structure: "valid" | "invalid";
  source_binding: "matched" | "mismatched" | "not_checked";
  representation_sha256?: string;
  counts?: {
    pages: number;
    elements: number;
    spans: number;
    tables: number;
  };
  error?: EthosGroundingValidationError;
};

export interface EthosGroundingValidationError {
  code: string;
  path: string;
  message: string;
}
