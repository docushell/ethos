/*
 * Copyright 2026 The Ethos maintainers
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

use std::collections::BTreeMap;
use std::collections::HashSet;
use std::path::{Path, PathBuf};

use ethos_core::codes::WarningCode;
use ethos_core::crop_element::{CropElementDescriptor, CropElementRendering};
use ethos_core::error::EthosError;
use ethos_core::fingerprint::is_fingerprint_form;
use ethos_core::grounding::{
    Capabilities, CoordinateOrigin, GroundingElement, GroundingSource, GroundingSpan,
    GroundingTable, PageGeometry, ParserIdentity,
};
use ethos_core::model::Document;
use ethos_core::verify_types::{
    CapabilityLimit, Check, CheckReason, CheckStatus, ClaimKind, EvidenceOptions, MatchMethod,
    VerificationConfig, VerificationReport,
};
use ethos_grounding_opendataloader_json::OdlJsonSource;
use ethos_verify::CitationInput;

use crate::cmd::crop_artifacts::{
    load_bound_crop_source_pdf, write_crop_descriptor_artifact, write_rendered_crop_artifact,
    CropSourcePdf,
};
use crate::{
    default_max_input_bytes, read_document, read_file_limited, write_output, Failure, VerifyArgs,
    VerifyOutputFormat,
};

pub(crate) fn verify(args: VerifyArgs) -> Result<(), Failure> {
    let max_input_bytes = default_max_input_bytes();
    let citations_bytes = read_file_limited(&args.citations, max_input_bytes)?;
    let citations: CitationInput = serde_json::from_slice(&citations_bytes).map_err(|_| {
        Failure::Usage("citations file does not match the alpha citation input shape".to_string())
    })?;

    if args.crop_dir.is_some() && args.grounding.is_some() {
        return Err(Failure::Usage(
            "--crop-dir is currently supported only for native Ethos document grounding"
                .to_string(),
        ));
    }
    if args.crop_source_pdf.is_some() && args.crop_dir.is_none() {
        return Err(Failure::Usage(
            "--crop-source-pdf requires --crop-dir".to_string(),
        ));
    }

    let mut config: VerificationConfig = match &args.config {
        Some(path) => {
            serde_json::from_slice(&read_file_limited(path, max_input_bytes)?).map_err(|_| {
                Failure::Usage("verification config does not match the schema".to_string())
            })?
        }
        None => VerificationConfig::default_v1(),
    };
    if args.crop_dir.is_some() {
        config
            .evidence
            .get_or_insert_with(EvidenceOptions::default)
            .include_crops = true;
    }
    validate_verification_config(&config)?;
    validate_citation_input(&citations, &config)?;
    let config_value =
        serde_json::to_value(&config).map_err(|e| EthosError::internal(e.to_string()))?;
    let config_sha256 =
        ethos_core::c14n::sha256_hex(&config_value).map_err(|e| EthosError::internal(e.message))?;

    let report = match args.grounding.as_deref() {
        None => {
            let doc = read_document(&args.input)?;
            let crop_source_pdf = args
                .crop_source_pdf
                .as_deref()
                .map(|source_pdf| load_bound_crop_source_pdf(&doc, source_pdf))
                .transpose()?;
            match args.crop_dir.as_ref() {
                Some(_) => {
                    let source = NativeCropSource { document: &doc };
                    let mut report =
                        ethos_verify::verify_claims(&source, citations, &config, config_sha256);
                    assign_logical_crop_refs(&mut report)?;
                    if let Some(crop_dir) = args.crop_dir.as_deref() {
                        write_crop_artifacts(crop_dir, &report, crop_source_pdf.as_ref())?;
                    }
                    return write_report(args.out, args.format, report, args.fail_on_ungrounded);
                }
                None => ethos_verify::verify_claims(&doc, citations, &config, config_sha256),
            }
        }
        Some("opendataloader-json") => {
            let bytes = read_file_limited(&args.input, max_input_bytes)?;
            let text = String::from_utf8(bytes)
                .map_err(|_| Failure::Usage("grounding input is not UTF-8".to_string()))?;
            let source = OdlJsonSource::from_json_str(&text)
                .map_err(|e| Failure::Usage(format!("opendataloader-json adapter: {e}")))?;
            ethos_verify::verify_claims(&source, citations, &config, config_sha256)
        }
        Some(other) => {
            return Err(Failure::Usage(format!(
                "unknown grounding adapter '{other}' (available: opendataloader-json)"
            )));
        }
    };

    write_report(args.out, args.format, report, args.fail_on_ungrounded)
}

fn write_report(
    out: Option<PathBuf>,
    format: VerifyOutputFormat,
    report: VerificationReport,
    fail_on_ungrounded: bool,
) -> Result<(), Failure> {
    let bytes = match format {
        VerifyOutputFormat::Json => verification_report_json_bytes(&report)?,
        VerifyOutputFormat::Summary => verification_report_summary_bytes(&report)?,
    };
    let all_evidence_grounded = report.all_evidence_grounded;
    write_output(out, &bytes)?;
    if fail_on_ungrounded && !all_evidence_grounded {
        return Err(Failure::Ungrounded);
    }
    Ok(())
}

fn verification_report_json_bytes(report: &VerificationReport) -> Result<Vec<u8>, Failure> {
    let value = serde_json::to_value(report).map_err(|e| EthosError::internal(e.to_string()))?;
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    Ok(bytes)
}

fn verification_report_summary_bytes(report: &VerificationReport) -> Result<Vec<u8>, Failure> {
    let proof = proof_summary(report);
    let mut out = String::new();
    out.push_str("ethos verify summary\n");
    out.push_str(&format!("schema_version: {}\n", report.schema_version));
    out.push_str(&format!(
        "verification_config_sha256: {}\n",
        report.verification_config_sha256
    ));
    out.push_str(&format!(
        "all_evidence_grounded: {}\n",
        report.all_evidence_grounded
    ));
    out.push_str(&format!(
        "fingerprint_stale: {}\n",
        report.fingerprint_stale
    ));
    out.push_str(&format!(
        "proof_status: {}\n",
        proof_status_label(proof.proof_status)
    ));
    out.push_str(&format!("request_certified: {}\n", proof.request_certified));
    out.push_str(&format!(
        "reusable_grounded_checks: {}\n",
        string_list(&proof.reusable_grounded_check_ids)
    ));
    out.push_str(&format!(
        "needs_review_checks: {}\n",
        string_list(&proof.needs_review_check_ids)
    ));
    out.push_str(&format!(
        "proof_limitations: {}\n",
        list_labels(&proof.proof_limitations, proof_limitation_label)
    ));
    out.push_str(&format!("recovery_hint: {}\n", proof_recovery_hint(&proof)));
    if let Some(fingerprint) = report.document_fingerprint.as_deref() {
        out.push_str(&format!("document_fingerprint: {fingerprint}\n"));
    }
    out.push_str(&format!(
        "grounding: {} {}\n",
        report.grounding.parser.name, report.grounding.parser.version
    ));
    if let Some(adapter) = report.grounding.parser.adapter.as_deref() {
        out.push_str(&format!("grounding_adapter: {adapter}\n"));
    }
    if let Some(adapter_version) = report.grounding.parser.adapter_version.as_deref() {
        out.push_str(&format!("grounding_adapter_version: {adapter_version}\n"));
    }
    out.push_str(&format!(
        "grounding_capabilities: {}\n",
        grounding_capabilities_label(report.grounding.capabilities)
    ));
    out.push_str(&format!("checks_total: {}\n", report.checks.len()));
    for status in [
        CheckStatus::Grounded,
        CheckStatus::NotFound,
        CheckStatus::Mismatch,
        CheckStatus::Stale,
        CheckStatus::UnsupportedClaimKind,
        CheckStatus::CapabilityBlocked,
        CheckStatus::Error,
    ] {
        let count = report
            .checks
            .iter()
            .filter(|check| check.status == status)
            .count();
        out.push_str(&format!("checks_{}: {count}\n", status_label(status)));
    }
    out.push_str(&format!(
        "capability_limits: {}\n",
        list_labels(&report.capability_limits, capability_limit_label)
    ));
    out.push_str(&format!(
        "unsupported_claim_kinds: {}\n",
        if report.unsupported_claim_kinds.is_empty() {
            "none".to_string()
        } else {
            report.unsupported_claim_kinds.join(",")
        }
    ));
    out.push_str(&format!(
        "warnings: {}\n",
        serde_label_list(&report.warnings)?
    ));
    out.push_str("non_grounded_checks:\n");
    let mut non_grounded = report
        .checks
        .iter()
        .filter(|check| check.status != CheckStatus::Grounded)
        .peekable();
    if non_grounded.peek().is_none() {
        out.push_str("- none\n");
    } else {
        for check in non_grounded {
            out.push_str(&format!(
                "- {} status={} reason={} kind={} locator={} match_method={}\n",
                check.id,
                status_label(check.status),
                check
                    .reason
                    .map(check_reason_label)
                    .unwrap_or("unspecified"),
                claim_kind_label(check.claim.kind),
                citation_locator_label(&check.claim.citation),
                match_method_label(check.match_method)
            ));
            out.push_str(&format!("  diagnostic: {}\n", check_diagnostic(check)));
        }
    }
    Ok(out.into_bytes())
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ProofStatus {
    Verified,
    PartiallyVerified,
    Unverified,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ProofLimitation {
    CapabilityLimited,
    StaleFingerprint,
    UnsupportedClaimKind,
    NonGroundedChecks,
    SemanticUnverified,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ProofSummary {
    proof_status: ProofStatus,
    request_certified: bool,
    reusable_grounded_check_ids: Vec<String>,
    needs_review_check_ids: Vec<String>,
    proof_limitations: Vec<ProofLimitation>,
}

fn proof_summary(report: &VerificationReport) -> ProofSummary {
    let reusable_grounded_check_ids = report
        .checks
        .iter()
        .filter(|check| is_reusable_grounded_check(report, check))
        .map(|check| check.id.clone())
        .collect::<Vec<_>>();
    let needs_review_check_ids = report
        .checks
        .iter()
        .filter(|check| !is_reusable_grounded_check(report, check))
        .map(|check| check.id.clone())
        .collect::<Vec<_>>();
    let request_certified = report.all_evidence_grounded;
    let proof_status = if request_certified {
        ProofStatus::Verified
    } else if reusable_grounded_check_ids.is_empty() {
        ProofStatus::Unverified
    } else {
        ProofStatus::PartiallyVerified
    };

    let mut proof_limitations = Vec::new();
    if has_capability_limit(report) {
        proof_limitations.push(ProofLimitation::CapabilityLimited);
    }
    if report.fingerprint_stale {
        proof_limitations.push(ProofLimitation::StaleFingerprint);
    }
    if !report.unsupported_claim_kinds.is_empty() {
        proof_limitations.push(ProofLimitation::UnsupportedClaimKind);
    }
    if report
        .checks
        .iter()
        .any(|check| check.status != CheckStatus::Grounded)
    {
        proof_limitations.push(ProofLimitation::NonGroundedChecks);
    }
    if report.checks.iter().any(|check| check.semantic_unverified) {
        proof_limitations.push(ProofLimitation::SemanticUnverified);
    }

    ProofSummary {
        proof_status,
        request_certified,
        reusable_grounded_check_ids,
        needs_review_check_ids,
        proof_limitations,
    }
}

fn is_reusable_grounded_check(report: &VerificationReport, check: &Check) -> bool {
    !report.fingerprint_stale && check.status == CheckStatus::Grounded && !check.semantic_unverified
}

fn has_capability_limit(report: &VerificationReport) -> bool {
    !report.capability_limits.is_empty()
        || report
            .warnings
            .iter()
            .any(|warning| *warning == WarningCode::CapabilityLimited)
        || report.checks.iter().any(|check| {
            check
                .warnings
                .iter()
                .any(|warning| *warning == WarningCode::CapabilityLimited)
        })
}

fn proof_status_label(status: ProofStatus) -> &'static str {
    match status {
        ProofStatus::Verified => "verified",
        ProofStatus::PartiallyVerified => "partially_verified",
        ProofStatus::Unverified => "unverified",
    }
}

fn proof_limitation_label(limitation: ProofLimitation) -> &'static str {
    match limitation {
        ProofLimitation::CapabilityLimited => "capability_limited",
        ProofLimitation::StaleFingerprint => "stale_fingerprint",
        ProofLimitation::UnsupportedClaimKind => "unsupported_claim_kind",
        ProofLimitation::NonGroundedChecks => "non_grounded_checks",
        ProofLimitation::SemanticUnverified => "semantic_unverified",
    }
}

fn proof_recovery_hint(proof: &ProofSummary) -> &'static str {
    if proof.proof_status == ProofStatus::Verified && proof.proof_limitations.is_empty() {
        return "none";
    }
    if proof.proof_status == ProofStatus::Verified {
        return "inspect proof_limitations before widening the proof claim";
    }
    if proof.proof_status == ProofStatus::PartiallyVerified {
        return "assemble final output only from reusable_grounded_checks and repair needs_review_checks";
    }
    if proof
        .proof_limitations
        .contains(&ProofLimitation::StaleFingerprint)
    {
        return "refresh citations against the current source fingerprint";
    }
    if proof
        .proof_limitations
        .contains(&ProofLimitation::CapabilityLimited)
    {
        return "use a source with the required grounding capabilities or lower the proof requirement";
    }
    if proof
        .proof_limitations
        .contains(&ProofLimitation::SemanticUnverified)
    {
        return "rewrite semantic claims into literal source-backed citation claims";
    }
    "inspect needs_review_checks and repair stale, missing, mismatched, unsupported, or capability-blocked citations"
}

fn status_label(status: CheckStatus) -> &'static str {
    match status {
        CheckStatus::Grounded => "grounded",
        CheckStatus::NotFound => "not_found",
        CheckStatus::Mismatch => "mismatch",
        CheckStatus::Stale => "stale",
        CheckStatus::UnsupportedClaimKind => "unsupported_claim_kind",
        CheckStatus::CapabilityBlocked => "capability_blocked",
        CheckStatus::Error => "error",
    }
}

fn check_reason_label(reason: CheckReason) -> &'static str {
    match reason {
        CheckReason::MissingLocator => "missing_locator",
        CheckReason::MissingRequiredText => "missing_required_text",
        CheckReason::UnsupportedClaimKind => "unsupported_claim_kind",
        CheckReason::StaleFingerprint => "stale_fingerprint",
        CheckReason::MissingSourceFingerprint => "missing_source_fingerprint",
        CheckReason::MissingCitationFingerprint => "missing_citation_fingerprint",
        CheckReason::MissingSpanCapability => "missing_span_capability",
        CheckReason::MissingTableCapability => "missing_table_capability",
        CheckReason::UnknownCoordinateOrigin => "unknown_coordinate_origin",
        CheckReason::ElementNotFound => "element_not_found",
        CheckReason::SpanNotFound => "span_not_found",
        CheckReason::PageNotFound => "page_not_found",
        CheckReason::BboxNotFound => "bbox_not_found",
        CheckReason::MissingPageForBbox => "missing_page_for_bbox",
        CheckReason::MissingTableCellLocator => "missing_table_cell_locator",
        CheckReason::TableNotFound => "table_not_found",
        CheckReason::TableCellNotFound => "table_cell_not_found",
        CheckReason::TextMismatch => "text_mismatch",
    }
}

fn check_diagnostic(check: &Check) -> String {
    match check.reason {
        Some(CheckReason::MissingLocator) => {
            "citation has no locator; provide page, element_id, span_id, table_id/cell, or bbox"
                .to_string()
        }
        Some(CheckReason::MissingRequiredText) => {
            "textual claim is missing required text".to_string()
        }
        Some(CheckReason::UnsupportedClaimKind) => {
            "claim kind is outside the active verifier scope".to_string()
        }
        Some(CheckReason::StaleFingerprint) => {
            "citation fingerprint does not match grounding source fingerprint".to_string()
        }
        Some(CheckReason::MissingSourceFingerprint) => {
            "citations are fingerprint-pinned, but the grounding source did not declare a fingerprint"
                .to_string()
        }
        Some(CheckReason::MissingCitationFingerprint) => {
            "active staleness policy requires a citation fingerprint".to_string()
        }
        Some(CheckReason::MissingSpanCapability) => {
            "span locator requires a source with span capability".to_string()
        }
        Some(CheckReason::MissingTableCapability) => {
            "table_cell lookup requires a source with table capability".to_string()
        }
        Some(CheckReason::UnknownCoordinateOrigin) => {
            "bbox locator requires a known coordinate origin".to_string()
        }
        Some(CheckReason::ElementNotFound) => {
            "element_id locator did not resolve in the grounding source".to_string()
        }
        Some(CheckReason::SpanNotFound) => {
            "span_id locator did not resolve in the grounding source".to_string()
        }
        Some(CheckReason::PageNotFound) => {
            "page locator did not resolve in the grounding source".to_string()
        }
        Some(CheckReason::BboxNotFound) => {
            "bbox locator did not resolve to a containing grounding element".to_string()
        }
        Some(CheckReason::MissingPageForBbox) => {
            "bbox locator requires page unless another target locator is present".to_string()
        }
        Some(CheckReason::MissingTableCellLocator) => {
            "table_cell claim requires both table_id and cell locator".to_string()
        }
        Some(CheckReason::TableNotFound) => {
            "table_id locator did not resolve in the grounding source".to_string()
        }
        Some(CheckReason::TableCellNotFound) => {
            "table resolved, but the cited cell address was not found".to_string()
        }
        Some(CheckReason::TextMismatch) => format!(
            "target resolved, but target text did not match claimed text under {}; no semantic inference was attempted",
            match_method_label(check.match_method)
        ),
        None => "check did not ground and no stable reason was reported".to_string(),
    }
}

fn capability_limit_label(limit: CapabilityLimit) -> &'static str {
    match limit {
        CapabilityLimit::MissingSpans => "missing_spans",
        CapabilityLimit::MissingCharOffsets => "missing_char_offsets",
        CapabilityLimit::MissingTables => "missing_tables",
        CapabilityLimit::MissingFingerprint => "missing_fingerprint",
        CapabilityLimit::UnknownCoordinateOrigin => "unknown_coordinate_origin",
        CapabilityLimit::MissingCropSupport => "missing_crop_support",
    }
}

fn grounding_capabilities_label(capabilities: Capabilities) -> String {
    format!(
        "spans={},char_offsets={},tables={},fingerprint={},coordinate_origin={},crop_support={}",
        capabilities.spans,
        capabilities.char_offsets,
        capabilities.tables,
        capabilities.fingerprint,
        coordinate_origin_label(capabilities.coordinate_origin),
        capabilities.crop_support
    )
}

fn coordinate_origin_label(origin: CoordinateOrigin) -> &'static str {
    match origin {
        CoordinateOrigin::TopLeft => "top-left",
        CoordinateOrigin::BottomLeft => "bottom-left",
        CoordinateOrigin::Unknown => "unknown",
    }
}

fn claim_kind_label(kind: ClaimKind) -> &'static str {
    match kind {
        ClaimKind::Quote => "quote",
        ClaimKind::Value => "value",
        ClaimKind::Presence => "presence",
        ClaimKind::TableCell => "table_cell",
        ClaimKind::Region => "region",
        ClaimKind::Other => "other",
    }
}

fn match_method_label(method: MatchMethod) -> &'static str {
    match method {
        MatchMethod::ExactText => "exact_text",
        MatchMethod::NormalizedText => "normalized_text",
        MatchMethod::ExactTextContains => "exact_text_contains",
        MatchMethod::NormalizedTextContains => "normalized_text_contains",
        MatchMethod::TableCellLookup => "table_cell_lookup",
        MatchMethod::BboxContainment => "bbox_containment",
        MatchMethod::PresenceOnly => "presence_only",
        MatchMethod::None => "none",
    }
}

fn citation_locator_label(citation: &ethos_core::verify_types::Citation) -> String {
    let mut parts = Vec::new();
    if let Some(page) = citation.page.as_deref() {
        parts.push(format!("page:{page}"));
    }
    if let Some(element_id) = citation.element_id.as_deref() {
        parts.push(format!("element_id:{element_id}"));
    }
    if let Some(span_id) = citation.span_id.as_deref() {
        parts.push(format!("span_id:{span_id}"));
    }
    if let Some(table_id) = citation.table_id.as_deref() {
        parts.push(format!("table_id:{table_id}"));
    }
    if let Some(cell) = citation.cell {
        parts.push(format!("cell:{},{}", cell.row, cell.col));
    }
    if let Some(bbox) = citation.bbox {
        parts.push(format!(
            "bbox:[{},{},{},{}]",
            bbox[0], bbox[1], bbox[2], bbox[3]
        ));
    }
    if parts.is_empty() {
        "none".to_string()
    } else {
        parts.join(";")
    }
}

fn list_labels<T: Copy>(values: &[T], label: fn(T) -> &'static str) -> String {
    if values.is_empty() {
        "none".to_string()
    } else {
        values
            .iter()
            .map(|value| label(*value))
            .collect::<Vec<_>>()
            .join(",")
    }
}

fn string_list(values: &[String]) -> String {
    if values.is_empty() {
        "none".to_string()
    } else {
        values.join(",")
    }
}

fn serde_label_list<T: serde::Serialize>(values: &[T]) -> Result<String, Failure> {
    if values.is_empty() {
        return Ok("none".to_string());
    }
    let mut labels = Vec::new();
    for value in values {
        let value = serde_json::to_value(value).map_err(|e| EthosError::internal(e.to_string()))?;
        let Some(label) = value.as_str() else {
            return Err(Failure::Ethos(EthosError::internal(
                "summary label serialization did not produce a string",
            )));
        };
        labels.push(label.to_string());
    }
    Ok(labels.join(","))
}

struct NativeCropSource<'a> {
    document: &'a Document,
}

impl GroundingSource for NativeCropSource<'_> {
    fn parser(&self) -> ParserIdentity {
        self.document.parser()
    }

    fn capabilities(&self) -> Capabilities {
        let mut capabilities = self.document.capabilities();
        capabilities.crop_support = true;
        capabilities
    }

    fn fingerprint(&self) -> Option<String> {
        self.document.fingerprint()
    }

    fn pages(&self) -> Vec<PageGeometry> {
        self.document.pages()
    }

    fn elements(&self) -> Vec<GroundingElement> {
        self.document.elements()
    }

    fn spans(&self) -> Vec<GroundingSpan> {
        self.document.spans()
    }

    fn tables(&self) -> Vec<GroundingTable> {
        self.document.tables()
    }

    fn crop_ref(&self, page: &str, bbox: [i64; 4]) -> Option<String> {
        crop_ref_for(page, bbox)
    }

    fn element_by_id(&self, id: &str) -> Option<GroundingElement> {
        self.document.element_by_id(id)
    }
}

fn crop_ref_for(page: &str, bbox: [i64; 4]) -> Option<String> {
    let value = serde_json::json!({
        "bbox": bbox,
        "page": page,
    });
    let hash = ethos_core::c14n::sha256_hex(&value).ok()?;
    Some(format!("crop-{hash}.json"))
}

fn logical_crop_ref_for(
    document_fingerprint: &str,
    check_id: &str,
    page: &str,
) -> Result<String, Failure> {
    ethos_core::crop_element::crop_element_crop_ref(document_fingerprint, check_id, page)
        .map_err(Failure::Ethos)
}

fn assign_logical_crop_refs(report: &mut VerificationReport) -> Result<(), Failure> {
    let Some(document_fingerprint) = report.document_fingerprint.as_deref() else {
        return Ok(());
    };
    for check in &mut report.checks {
        let Some(evidence) = check.evidence.as_mut() else {
            continue;
        };
        if evidence.crop_ref.is_none() {
            continue;
        }
        let Some(page) = evidence.page.as_deref() else {
            continue;
        };
        let crop_ref = logical_crop_ref_for(document_fingerprint, &check.id, page)?;
        evidence.crop_ref = Some(crop_ref);
    }
    Ok(())
}

fn write_crop_artifacts(
    crop_dir: &Path,
    report: &VerificationReport,
    source_pdf: Option<&CropSourcePdf>,
) -> Result<(), Failure> {
    std::fs::create_dir_all(crop_dir).map_err(|_| {
        Failure::Usage(format!(
            "cannot create crop artifact directory: {}",
            crop_dir.display()
        ))
    })?;

    let mut descriptors: BTreeMap<String, CropElementDescriptor> = BTreeMap::new();
    for check in &report.checks {
        let Some(evidence) = check.evidence.as_ref() else {
            continue;
        };
        let (Some(crop_ref), Some(page), Some(bbox)) = (
            evidence.crop_ref.as_deref(),
            evidence.page.as_deref(),
            evidence.bbox,
        ) else {
            continue;
        };
        let text_sha256 = evidence
            .text
            .as_deref()
            .map(|text| ethos_core::c14n::sha256_hex_bytes(text.as_bytes()));

        match descriptors.get_mut(crop_ref) {
            Some(existing) => {
                if existing.page != page
                    || existing.bbox != bbox
                    || existing.text_sha256 != text_sha256
                {
                    return Err(Failure::Ethos(EthosError::internal(
                        "crop_ref collision while writing crop descriptors",
                    )));
                }
                existing.check_ids.push(check.id.clone());
            }
            None => {
                let document_fingerprint =
                    report.document_fingerprint.clone().ok_or_else(|| {
                        Failure::Ethos(EthosError::internal(
                            "crop descriptor requires document fingerprint",
                        ))
                    })?;
                descriptors.insert(
                    crop_ref.to_string(),
                    CropElementDescriptor {
                        artifact_type: "ethos.crop_descriptor.v1".to_string(),
                        schema_version: ethos_core::SCHEMA_VERSION.to_string(),
                        crop_ref: crop_ref.to_string(),
                        document_fingerprint,
                        page: page.to_string(),
                        bbox,
                        check_ids: vec![check.id.clone()],
                        rendering_status: if source_pdf.is_some() {
                            CropElementRendering::Rendered
                        } else {
                            CropElementRendering::DescriptorOnly
                        },
                        source_pdf_fingerprint: None,
                        rendered_ref: None,
                        rendered_format: None,
                        rendered_sha256: None,
                        rendered_width_px: None,
                        rendered_height_px: None,
                        text_sha256,
                    },
                );
            }
        }
    }

    for (_, descriptor) in descriptors {
        let mut descriptor = descriptor;
        if let Some(source_pdf) = source_pdf {
            write_rendered_crop_artifact(crop_dir, &mut descriptor, source_pdf)?;
        }
        write_crop_descriptor_artifact(crop_dir, &descriptor)?;
    }

    Ok(())
}

fn validate_citation_input(
    citations: &CitationInput,
    config: &VerificationConfig,
) -> Result<(), Failure> {
    let claims = citations.claims();
    if claims.is_empty() {
        return Err(Failure::Usage(
            "citations file must contain at least one claim".to_string(),
        ));
    }
    if claims.len() > config.limits.max_checks as usize {
        return Err(Failure::Usage(format!(
            "citations file exceeds max_checks ({})",
            config.limits.max_checks
        )));
    }
    if citations
        .document_fingerprint()
        .is_some_and(|fingerprint| !is_fingerprint_form(fingerprint))
    {
        return Err(Failure::Usage(
            "citations document_fingerprint must be sha256:<64 lowercase hex chars>".to_string(),
        ));
    }
    for (idx, claim) in claims.iter().enumerate() {
        if !claim.citation.has_locator() {
            return Err(Failure::Usage(format!(
                "claim {} citation must contain at least one locator",
                idx + 1
            )));
        }
        if claim.citation.table_id.is_some() != claim.citation.cell.is_some() {
            return Err(Failure::Usage(format!(
                "claim {} citation table_id and cell must be provided together",
                idx + 1
            )));
        }
        if claim.kind == ClaimKind::TableCell
            && (claim.citation.table_id.is_none() || claim.citation.cell.is_none())
        {
            return Err(Failure::Usage(format!(
                "claim {} table_cell citation must include table_id and cell",
                idx + 1
            )));
        }
        if claim.citation.bbox.is_some()
            && claim.citation.page.is_none()
            && claim.citation.element_id.is_none()
            && claim.citation.span_id.is_none()
            && claim.citation.table_id.is_none()
        {
            return Err(Failure::Usage(format!(
                "claim {} citation bbox requires page unless another target locator is present",
                idx + 1
            )));
        }
        if claim
            .citation
            .bbox
            .is_some_and(|bbox| bbox[0] >= bbox[2] || bbox[1] >= bbox[3])
        {
            return Err(Failure::Usage(format!(
                "claim {} citation bbox must have positive area",
                idx + 1
            )));
        }
        if matches!(
            claim.kind,
            ClaimKind::Quote | ClaimKind::Value | ClaimKind::TableCell
        ) && claim
            .text
            .as_ref()
            .is_none_or(|text| text.trim().is_empty())
        {
            return Err(Failure::Usage(format!(
                "claim {} text must be non-empty for quote, value, and table_cell",
                idx + 1
            )));
        }
    }
    Ok(())
}

fn validate_verification_config(config: &VerificationConfig) -> Result<(), Failure> {
    if config.schema_version != ethos_core::SCHEMA_VERSION {
        return Err(Failure::Usage(format!(
            "verification config schema_version must be {}",
            ethos_core::SCHEMA_VERSION
        )));
    }
    if config.claim_kinds.is_empty() {
        return Err(Failure::Usage(
            "verification config claim_kinds must not be empty".to_string(),
        ));
    }
    let mut seen = HashSet::new();
    for kind in &config.claim_kinds {
        if matches!(kind, ClaimKind::Region | ClaimKind::Other) {
            return Err(Failure::Usage(
                "verification config claim_kinds must include only quote, value, presence, and table_cell"
                    .to_string(),
            ));
        }
        if !seen.insert(*kind) {
            return Err(Failure::Usage(
                "verification config claim_kinds must be unique".to_string(),
            ));
        }
    }
    if config
        .matching
        .bbox_containment_tolerance_q
        .is_some_and(|tolerance| tolerance < 0)
    {
        return Err(Failure::Usage(
            "verification config bbox_containment_tolerance_q must be non-negative".to_string(),
        ));
    }
    if config.limits.max_checks == 0 {
        return Err(Failure::Usage(
            "verification config max_checks must be at least 1".to_string(),
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use ethos_core::verify_types::{Check, CheckStatus, Evidence, GroundingMeta, MatchMethod};

    const TEST_DOCUMENT_FINGERPRINT: &str =
        "sha256:7164f43f104dc248193f12ea828e0ab857eae194210114c6f6c0160fd643c87b";

    fn crop_report(document_fingerprint: Option<&str>, checks: Vec<Check>) -> VerificationReport {
        VerificationReport {
            schema_version: ethos_core::SCHEMA_VERSION.to_string(),
            document_fingerprint: document_fingerprint.map(str::to_string),
            verification_config_sha256: "0".repeat(64),
            grounding: GroundingMeta {
                parser: ParserIdentity {
                    name: "ethos".to_string(),
                    version: "0.1.0".to_string(),
                    adapter: None,
                    adapter_version: None,
                },
                capabilities: Capabilities {
                    spans: true,
                    char_offsets: true,
                    tables: true,
                    fingerprint: true,
                    coordinate_origin: ethos_core::grounding::CoordinateOrigin::TopLeft,
                    crop_support: true,
                },
            },
            capability_limits: Vec::new(),
            fingerprint_stale: false,
            all_evidence_grounded: true,
            checks,
            unsupported_claim_kinds: Vec::new(),
            warnings: Vec::new(),
        }
    }

    fn crop_check(id: &str, crop_ref: &str, bbox: [i64; 4], text: Option<&str>) -> Check {
        Check {
            id: id.to_string(),
            claim: ethos_core::verify_types::Claim {
                kind: ClaimKind::Quote,
                text: Some("Hello".to_string()),
                citation: ethos_core::verify_types::Citation {
                    page: None,
                    element_id: Some("e000001".to_string()),
                    span_id: None,
                    table_id: None,
                    cell: None,
                    bbox: None,
                },
            },
            status: CheckStatus::Grounded,
            reason: None,
            match_method: MatchMethod::ExactTextContains,
            semantic_unverified: false,
            evidence: Some(Evidence {
                text: text.map(str::to_string),
                page: Some("p0001".to_string()),
                bbox: Some(bbox),
                crop_ref: Some(crop_ref.to_string()),
            }),
            warnings: Vec::new(),
        }
    }

    #[test]
    fn proof_summary_keeps_capability_limit_visible_without_failing_certified_request() {
        let mut report = crop_report(
            Some(TEST_DOCUMENT_FINGERPRINT),
            vec![crop_check(
                "v0001",
                &format!("crop-{}.json", "a".repeat(64)),
                [7392, 5482, 19378, 7226],
                Some("Hello world"),
            )],
        );
        report.capability_limits = vec![CapabilityLimit::MissingFingerprint];
        report.warnings = vec![WarningCode::CapabilityLimited];

        let proof = proof_summary(&report);

        assert_eq!(proof.proof_status, ProofStatus::Verified);
        assert!(proof.request_certified);
        assert_eq!(proof.reusable_grounded_check_ids, vec!["v0001"]);
        assert!(proof.needs_review_check_ids.is_empty());
        assert_eq!(
            proof.proof_limitations,
            vec![ProofLimitation::CapabilityLimited]
        );
    }

    #[test]
    fn proof_summary_marks_mixed_reports_as_partially_verified_without_certifying_request() {
        let grounded = crop_check(
            "v0001",
            &format!("crop-{}.json", "a".repeat(64)),
            [7392, 5482, 19378, 7226],
            Some("Hello world"),
        );
        let mut unsupported = crop_check(
            "v0002",
            &format!("crop-{}.json", "b".repeat(64)),
            [7392, 5482, 19378, 7226],
            None,
        );
        unsupported.status = CheckStatus::UnsupportedClaimKind;
        unsupported.reason = Some(CheckReason::UnsupportedClaimKind);
        unsupported.match_method = MatchMethod::None;
        unsupported.evidence = None;
        let mut report = crop_report(Some(TEST_DOCUMENT_FINGERPRINT), vec![grounded, unsupported]);
        report.all_evidence_grounded = false;
        report.unsupported_claim_kinds = vec!["region".to_string()];

        let proof = proof_summary(&report);

        assert_eq!(proof.proof_status, ProofStatus::PartiallyVerified);
        assert!(!proof.request_certified);
        assert_eq!(proof.reusable_grounded_check_ids, vec!["v0001"]);
        assert_eq!(proof.needs_review_check_ids, vec!["v0002"]);
        assert_eq!(
            proof.proof_limitations,
            vec![
                ProofLimitation::UnsupportedClaimKind,
                ProofLimitation::NonGroundedChecks
            ]
        );
    }

    #[test]
    fn proof_summary_excludes_grounded_checks_when_fingerprint_is_stale() {
        let mut report = crop_report(
            Some(TEST_DOCUMENT_FINGERPRINT),
            vec![crop_check(
                "v0001",
                &format!("crop-{}.json", "a".repeat(64)),
                [7392, 5482, 19378, 7226],
                Some("Hello world"),
            )],
        );
        report.fingerprint_stale = true;
        report.all_evidence_grounded = false;

        let proof = proof_summary(&report);

        assert_eq!(proof.proof_status, ProofStatus::Unverified);
        assert!(!proof.request_certified);
        assert!(proof.reusable_grounded_check_ids.is_empty());
        assert_eq!(proof.needs_review_check_ids, vec!["v0001"]);
        assert_eq!(
            proof.proof_limitations,
            vec![ProofLimitation::StaleFingerprint]
        );
    }

    #[test]
    fn proof_summary_excludes_semantic_unverified_grounded_checks() {
        let mut check = crop_check(
            "v0001",
            &format!("crop-{}.json", "a".repeat(64)),
            [7392, 5482, 19378, 7226],
            Some("Hello world"),
        );
        check.semantic_unverified = true;
        let mut report = crop_report(Some(TEST_DOCUMENT_FINGERPRINT), vec![check]);
        report.all_evidence_grounded = false;

        let proof = proof_summary(&report);

        assert_eq!(proof.proof_status, ProofStatus::Unverified);
        assert!(proof.reusable_grounded_check_ids.is_empty());
        assert_eq!(proof.needs_review_check_ids, vec!["v0001"]);
        assert_eq!(
            proof.proof_limitations,
            vec![ProofLimitation::SemanticUnverified]
        );
    }

    #[test]
    fn logical_crop_ref_uses_check_identity_not_bbox() {
        let first = logical_crop_ref_for(
            "sha256:7164f43f104dc248193f12ea828e0ab857eae194210114c6f6c0160fd643c87b",
            "v0001",
            "p0001",
        )
        .unwrap_or_else(|_| panic!("logical crop ref should be generated"));
        let second = logical_crop_ref_for(
            "sha256:7164f43f104dc248193f12ea828e0ab857eae194210114c6f6c0160fd643c87b",
            "v0001",
            "p0001",
        )
        .unwrap_or_else(|_| panic!("logical crop ref should be generated"));
        let different_check = logical_crop_ref_for(
            "sha256:7164f43f104dc248193f12ea828e0ab857eae194210114c6f6c0160fd643c87b",
            "v0002",
            "p0001",
        )
        .unwrap_or_else(|_| panic!("logical crop ref should be generated"));

        assert_eq!(first, second);
        assert_ne!(first, different_check);
        assert!(first.starts_with("crop-"));
        assert!(first.ends_with(".json"));
    }

    #[test]
    fn assign_logical_crop_refs_rewrites_existing_native_refs_only() {
        let mut report = VerificationReport {
            schema_version: ethos_core::SCHEMA_VERSION.to_string(),
            document_fingerprint: Some(
                "sha256:7164f43f104dc248193f12ea828e0ab857eae194210114c6f6c0160fd643c87b"
                    .to_string(),
            ),
            verification_config_sha256: "0".repeat(64),
            grounding: GroundingMeta {
                parser: ParserIdentity {
                    name: "ethos".to_string(),
                    version: "0.1.0".to_string(),
                    adapter: None,
                    adapter_version: None,
                },
                capabilities: Capabilities {
                    spans: true,
                    char_offsets: true,
                    tables: true,
                    fingerprint: true,
                    coordinate_origin: ethos_core::grounding::CoordinateOrigin::TopLeft,
                    crop_support: true,
                },
            },
            capability_limits: Vec::new(),
            fingerprint_stale: false,
            all_evidence_grounded: true,
            checks: vec![
                Check {
                    id: "v0001".to_string(),
                    claim: ethos_core::verify_types::Claim {
                        kind: ClaimKind::Quote,
                        text: Some("Hello".to_string()),
                        citation: ethos_core::verify_types::Citation {
                            page: None,
                            element_id: Some("e000001".to_string()),
                            span_id: None,
                            table_id: None,
                            cell: None,
                            bbox: None,
                        },
                    },
                    status: CheckStatus::Grounded,
                    reason: None,
                    match_method: MatchMethod::ExactTextContains,
                    semantic_unverified: false,
                    evidence: Some(Evidence {
                        text: Some("Hello world".to_string()),
                        page: Some("p0001".to_string()),
                        bbox: Some([7392, 5482, 19378, 7226]),
                        crop_ref: Some("crop-old.json".to_string()),
                    }),
                    warnings: Vec::new(),
                },
                Check {
                    id: "v0002".to_string(),
                    claim: ethos_core::verify_types::Claim {
                        kind: ClaimKind::Presence,
                        text: None,
                        citation: ethos_core::verify_types::Citation {
                            page: Some("p0001".to_string()),
                            element_id: None,
                            span_id: None,
                            table_id: None,
                            cell: None,
                            bbox: None,
                        },
                    },
                    status: CheckStatus::Grounded,
                    reason: None,
                    match_method: MatchMethod::PresenceOnly,
                    semantic_unverified: false,
                    evidence: Some(Evidence {
                        text: None,
                        page: Some("p0001".to_string()),
                        bbox: Some([0, 0, 100, 100]),
                        crop_ref: None,
                    }),
                    warnings: Vec::new(),
                },
            ],
            unsupported_claim_kinds: Vec::new(),
            warnings: Vec::new(),
        };

        assign_logical_crop_refs(&mut report)
            .unwrap_or_else(|_| panic!("logical crop refs should be assigned"));

        let expected = logical_crop_ref_for(
            report.document_fingerprint.as_deref().unwrap(),
            "v0001",
            "p0001",
        )
        .unwrap_or_else(|_| panic!("logical crop ref should be generated"));
        assert_eq!(
            report.checks[0]
                .evidence
                .as_ref()
                .and_then(|evidence| evidence.crop_ref.as_deref()),
            Some(expected.as_str())
        );
        assert_eq!(
            report.checks[1]
                .evidence
                .as_ref()
                .and_then(|evidence| evidence.crop_ref.as_deref()),
            None
        );
    }

    #[test]
    fn write_crop_artifacts_requires_document_fingerprint_for_descriptors() {
        let crop_dir = tempfile::tempdir().unwrap();
        let report = crop_report(
            None,
            vec![crop_check(
                "v0001",
                &format!("crop-{}.json", "a".repeat(64)),
                [7392, 5482, 19378, 7226],
                Some("Hello world"),
            )],
        );

        let err = write_crop_artifacts(crop_dir.path(), &report, None)
            .expect_err("crop descriptors require document fingerprint");

        match err {
            Failure::Ethos(error) => {
                assert_eq!(
                    error.message,
                    "crop descriptor requires document fingerprint"
                );
            }
            _ => panic!("expected ethos failure"),
        }
        assert_eq!(std::fs::read_dir(crop_dir.path()).unwrap().count(), 0);
    }

    #[test]
    fn write_crop_artifacts_rejects_crop_ref_collisions() {
        let crop_dir = tempfile::tempdir().unwrap();
        let crop_ref = format!("crop-{}.json", "b".repeat(64));
        let report = crop_report(
            Some(TEST_DOCUMENT_FINGERPRINT),
            vec![
                crop_check(
                    "v0001",
                    &crop_ref,
                    [7392, 5482, 19378, 7226],
                    Some("Hello world"),
                ),
                crop_check(
                    "v0002",
                    &crop_ref,
                    [7392, 5482, 19378, 8000],
                    Some("Hello world"),
                ),
            ],
        );

        let err = write_crop_artifacts(crop_dir.path(), &report, None)
            .expect_err("colliding crop refs must fail");

        match err {
            Failure::Ethos(error) => {
                assert_eq!(
                    error.message,
                    "crop_ref collision while writing crop descriptors"
                );
            }
            _ => panic!("expected ethos failure"),
        }
        assert_eq!(std::fs::read_dir(crop_dir.path()).unwrap().count(), 0);
    }
}
