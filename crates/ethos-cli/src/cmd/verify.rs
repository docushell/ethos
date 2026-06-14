use std::collections::HashSet;

use ethos_core::error::EthosError;
use ethos_core::fingerprint::is_fingerprint_form;
use ethos_core::verify_types::{ClaimKind, VerificationConfig};
use ethos_grounding_opendataloader_json::OdlJsonSource;
use ethos_verify::CitationInput;

use crate::{read_document, read_file, write_output, Failure, VerifyArgs};

pub(crate) fn verify(args: VerifyArgs) -> Result<(), Failure> {
    let citations_bytes = read_file(&args.citations)?;
    let citations: CitationInput = serde_json::from_slice(&citations_bytes).map_err(|_| {
        Failure::Usage("citations file does not match the alpha citation input shape".to_string())
    })?;

    let config: VerificationConfig = match &args.config {
        Some(path) => serde_json::from_slice(&read_file(path)?).map_err(|_| {
            Failure::Usage("verification config does not match the schema".to_string())
        })?,
        None => VerificationConfig::default_v1(),
    };
    validate_verification_config(&config)?;
    validate_citation_input(&citations, &config)?;
    let config_value =
        serde_json::to_value(&config).map_err(|e| EthosError::internal(e.to_string()))?;
    let config_sha256 =
        ethos_core::c14n::sha256_hex(&config_value).map_err(|e| EthosError::internal(e.message))?;

    let report = match args.grounding.as_deref() {
        None => {
            let doc = read_document(&args.input)?;
            ethos_verify::verify_claims(&doc, citations, &config, config_sha256)
        }
        Some("opendataloader-json") => {
            let bytes = read_file(&args.input)?;
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

    let value = serde_json::to_value(&report).map_err(|e| EthosError::internal(e.to_string()))?;
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    let all_evidence_grounded = report.all_evidence_grounded;
    write_output(args.out, &bytes)?;
    if args.fail_on_ungrounded && !all_evidence_grounded {
        return Err(Failure::Ungrounded);
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
        if *kind == ClaimKind::Other {
            return Err(Failure::Usage(
                "verification config claim_kinds must not include other".to_string(),
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
