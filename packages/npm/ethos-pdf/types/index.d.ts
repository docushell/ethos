// Generated from the Ethos JSON Schemas. Do not edit by hand.
// Runtime JSON Schema validation remains authoritative.
// Ethos verifies citation grounding, not semantic truth.

import type { EthosLlmCitationOutput } from "./citation-emission";
import type { EthosVerificationReport } from "./verification-report";
import type { EthosGroundingValidationReport } from "./grounding-validation-report";

export * from "./verification-report";
export * from "./citation-emission";
export * from "./evidence-handle-context";
export * from "./citation-emission-v2";
export * from "./answer-release";
export * from "./grounding-source";
export * from "./grounding-validation-report";

export interface EthosCommandResult<T> {
  exitCode: number;
  artifact: T | null;
  reason: string | null;
}

export interface CheckGroundingOptions {
  inputPath: string;
  outputPath?: string;
  sourceArtifactPath?: string;
  timeoutMs?: number;
  signal?: AbortSignal;
}

export interface VerifyClaimsOptions {
  inputPath: string;
  citationsPath?: string;
  citations?: EthosLlmCitationOutput;
  configPath?: string;
  outputPath?: string;
  failOnUngrounded?: boolean;
  grounding?: "opendataloader-json";
  timeoutMs?: number;
  signal?: AbortSignal;
}

export function checkGrounding(options: CheckGroundingOptions): Promise<EthosCommandResult<EthosGroundingValidationReport>>;
export function verifyClaims(options: VerifyClaimsOptions): Promise<EthosCommandResult<EthosVerificationReport>>;
