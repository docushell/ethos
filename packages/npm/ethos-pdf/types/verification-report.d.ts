// Generated from the Ethos JSON Schemas. Do not edit by hand.
// Runtime JSON Schema validation remains authoritative.
// Ethos verifies citation grounding, not semantic truth.

/**
 * @minItems 4
 * @maxItems 4
 */
export type EthosVerificationBbox = [number, number, number, number];
export type EthosVerificationWarningCode =
  | "low_confidence_reading_order"
  | "low_confidence_table_structure"
  | "hidden_text_detected"
  | "off_page_text_detected"
  | "low_contrast_text_detected"
  | "annotations_present"
  | "external_links_present"
  | "image_only_page"
  | "unsupported_annotation"
  | "partial_parse"
  | "capability_limited";

/**
 * Citation evidence verification over any GroundingSource (Ethos or foreign parser output). Verification is EVIDENCE GROUNDING — the cited region exists, its text matches by a declared method, the fingerprint is fresh. It is never pixel-level, semantic, or arithmetic proof of an answer. Capability-driven downgrades are explicit: missing spans, missing fingerprints, or foreign coordinate systems appear as capability_limited warnings, never silent approximation. INVARIANT (PRD §8): all_evidence_grounded is true only when (a) at least one supported check exists, (b) every supported check has status 'grounded', (c) no check has semantic_unverified=true, (d) unsupported_claim_kinds is empty, and (e) fingerprint_stale is false. The reference implementation enforces this; the schema documents it.
 */
export interface EthosVerificationReport {
  schema_version: "1.0.0" | "1.1.0";
  /**
   * Fingerprint of the grounding document when the source declares one; absent (with capability warning) otherwise.
   */
  document_fingerprint?: string;
  verification_config_sha256: string;
  grounding: {
    parser: {
      name: string;
      version: string;
      /**
       * Adapter identifier, e.g. 'opendataloader-json'.
       */
      adapter?: string;
      adapter_version?: string;
    };
    capabilities: {
      spans: boolean;
      char_offsets: boolean;
      tables: boolean;
      fingerprint: boolean;
      coordinate_origin: "top-left" | "bottom-left" | "unknown";
      crop_support: boolean;
    };
  };
  /**
   * True when the citations were produced against a different document fingerprint than the grounding source presents (staleness check). Stale evidence can never be grounded.
   */
  fingerprint_stale: boolean;
  /**
   * Structured capability gaps that caused any capability_limited warning. Empty when the grounding source declares every capability the active verification config needs.
   */
  capability_limits: (
    | "missing_spans"
    | "missing_char_offsets"
    | "missing_tables"
    | "missing_fingerprint"
    | "unknown_coordinate_origin"
    | "missing_crop_support"
    | "missing_structure"
  )[];
  all_evidence_grounded: boolean;
  dispersion?: {
    grounded_checks: number;
    elements: number;
    pages: number;
    unmapped_grounded_checks: number;
    sections?: number;
  };
  checks: {
    id: string;
    claim: {
      kind: "quote" | "value" | "presence" | "table_cell" | "region" | "other";
      /**
       * The claimed quote/value text, when textual.
       */
      text?: string;
      /**
       * Where the claim says the evidence lives. At least one locator required; id formats follow the grounding source.
       */
      citation: {
        page?: string;
        element_id?: string;
        span_id?: string;
        table_id?: string;
        cell?: {
          row: number;
          col: number;
        };
        bbox?: EthosVerificationBbox;
      };
    };
    status: "grounded" | "not_found" | "mismatch" | "stale" | "unsupported_claim_kind" | "capability_blocked" | "error";
    /**
     * Stable diagnostic reason for a non-grounded check outcome. Omitted for grounded checks.
     */
    reason?:
      | "missing_locator"
      | "missing_required_text"
      | "unsupported_claim_kind"
      | "stale_fingerprint"
      | "missing_source_fingerprint"
      | "missing_citation_fingerprint"
      | "missing_span_capability"
      | "missing_table_capability"
      | "unknown_coordinate_origin"
      | "element_not_found"
      | "span_not_found"
      | "page_not_found"
      | "bbox_not_found"
      | "locator_conflict"
      | "missing_page_for_bbox"
      | "missing_table_cell_locator"
      | "table_not_found"
      | "table_cell_not_found"
      | "text_mismatch";
    /**
     * How evidence was matched. Equality methods require the target text to equal the claim text after the configured normalization. '*_contains' methods are explicit substring containment and are used only for quote evidence inside a larger target. 'normalized_text' uses ONLY the whitespace rule pinned in the verification config; nothing fuzzier exists in v1.
     */
    match_method:
      | "exact_text"
      | "normalized_text"
      | "exact_text_contains"
      | "normalized_text_contains"
      | "table_cell_lookup"
      | "bbox_containment"
      | "presence_only"
      | "none";
    /**
     * True whenever grounding the claim would require semantic judgment beyond the declared match method (e.g. paraphrase, arithmetic, cross-region synthesis). In v1, literal checkers always set this false; non-literal claims fail closed as unsupported_claim_kind instead. Such checks can never make all_evidence_grounded true.
     */
    semantic_unverified: boolean;
    resolved_element_ids?: string[];
    provenance?: {
      status: "available" | "capability_limited" | "not_applicable";
      heading_path?: string[];
      element_role?: string;
      previous_element_id?: string;
      next_element_id?: string;
    };
    context_echo?: {
      before: string;
      match: string;
      after: string;
      element_boundary?: {
        offset: number;
        left_element_id: string;
        right_element_id: string;
      };
    };
    /**
     * What was found at the citation target. Page-only presence checks synthesize bbox as the full page extent. crop_ref is an opaque audit pointer emitted only when the verification config requests crops and the GroundingSource declares crop_support.
     */
    evidence?: {
      text?: string;
      page?: string;
      bbox?: EthosVerificationBbox;
      crop_ref?: string;
    };
    warnings: EthosVerificationWarningCode[];
    /**
     * How precisely this check bound its evidence. Absent when nothing resolved.
     */
    evidence_tier?: "exact_span" | "table_cell" | "element_scoped" | "page_scoped" | "capability_limited";
  }[];
  /**
   * Claim kinds present in the input that this verifier/config does not support. Non-empty => all_evidence_grounded=false.
   */
  unsupported_claim_kinds: string[];
  /**
   * Report-level stable warning codes (capability downgrades land here as capability_limited).
   */
  warnings: EthosVerificationWarningCode[];
  /**
   * What produced this verdict. A binding record, not cryptographic proof: it attests the verifier crate version, not binary provenance.
   */
  attestation: {
    verifier: {
      name: string;
      version: string;
    };
    /**
     * Echo of the config label. verification_config_sha256 stays authoritative.
     */
    config_version: string;
    /**
     * sha256(c14n(claims)) over the parsed claims array, not the raw file bytes and not the envelope.
     */
    claims_sha256: string;
  };
}
