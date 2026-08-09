// Generated from the Ethos JSON Schemas. Do not edit by hand.
// Runtime JSON Schema validation remains authoritative.
// Ethos verifies citation grounding, not semantic truth.

export type EthosGroundingSha256 = string;
export type EthosGroundingId = string;
/**
 * @minItems 4
 * @maxItems 4
 */
export type EthosGroundingBbox = never[];

export interface EthosGroundingSource {
  artifact_type: "ethos.grounding.v1";
  schema_version: "1.0.0";
  source: EthosGroundingSourceMetadata;
  producer: EthosGroundingProducer;
  capabilities: EthosGroundingCapabilities;
  coordinate_system: EthosGroundingCoordinateSystem;
  /**
   * @maxItems 5000
   */
  pages: EthosGroundingPage[];
  /**
   * @maxItems 1000000
   */
  elements: EthosGroundingElement[];
  /**
   * @maxItems 1000000
   */
  spans?: EthosGroundingSpan[];
  /**
   * @maxItems 100000
   */
  tables?: EthosGroundingTable[];
}
export interface EthosGroundingSourceMetadata {
  media_type: "application/pdf";
  sha256: EthosGroundingSha256;
}
export interface EthosGroundingProducer {
  name: string;
  version: string;
}
export interface EthosGroundingCapabilities {
  spans: boolean;
  char_offsets: boolean;
  tables: boolean;
}
export interface EthosGroundingCoordinateSystem {
  unit: "centipoint";
  origin: "top-left";
}
export interface EthosGroundingPage {
  id: EthosGroundingId;
  index: number;
  width: number;
  height: number;
  rotation: 0 | 90 | 180 | 270;
}
export interface EthosGroundingElement {
  id: EthosGroundingId;
  page: EthosGroundingId;
  bbox: EthosGroundingBbox;
  kind: string;
  text?: string;
}
export interface EthosGroundingSpan {
  id: EthosGroundingId;
  page: EthosGroundingId;
  bbox: EthosGroundingBbox;
  text: string;
  element?: EthosGroundingId;
  char_start?: number;
  char_end?: number;
}
export interface EthosGroundingTable {
  id: EthosGroundingId;
  page: EthosGroundingId;
  bbox: EthosGroundingBbox;
  /**
   * @maxItems 1000000
   */
  cells: EthosGroundingCell[];
}
export interface EthosGroundingCell {
  row: number;
  col: number;
  row_span: number;
  col_span: number;
  bbox: EthosGroundingBbox;
  text: string;
}
