use std::collections::BTreeMap;
use std::collections::HashSet;
use std::path::{Path, PathBuf};

use ethos_core::error::EthosError;
use ethos_core::fingerprint::{is_fingerprint_form, source_fingerprint};
use ethos_core::grounding::{
    Capabilities, GroundingElement, GroundingSource, GroundingSpan, GroundingTable, PageGeometry,
    ParserIdentity,
};
use ethos_core::model::Document;
use ethos_core::verify_types::{
    ClaimKind, EvidenceOptions, VerificationConfig, VerificationReport,
};
use ethos_grounding_opendataloader_json::OdlJsonSource;
use ethos_verify::CitationInput;

use crate::{read_document, read_file, write_output, Failure, VerifyArgs};

pub(crate) fn verify(args: VerifyArgs) -> Result<(), Failure> {
    let citations_bytes = read_file(&args.citations)?;
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
        Some(path) => serde_json::from_slice(&read_file(path)?).map_err(|_| {
            Failure::Usage("verification config does not match the schema".to_string())
        })?,
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
            if let Some(source_pdf) = args.crop_source_pdf.as_deref() {
                validate_crop_source_pdf_binding(&doc, source_pdf)?;
                return Err(Failure::Usage(
                    "rendered crop production is not implemented yet; rerun without --crop-source-pdf to write descriptor-only crop artifacts"
                        .to_string(),
                ));
            }
            match args.crop_dir.as_ref() {
                Some(_) => {
                    let source = NativeCropSource { document: &doc };
                    ethos_verify::verify_claims(&source, citations, &config, config_sha256)
                }
                None => ethos_verify::verify_claims(&doc, citations, &config, config_sha256),
            }
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
    if let Some(crop_dir) = args.crop_dir.as_deref() {
        write_crop_descriptors(crop_dir, &report)?;
    }
    write_output(args.out, &bytes)?;
    if args.fail_on_ungrounded && !all_evidence_grounded {
        return Err(Failure::Ungrounded);
    }
    Ok(())
}

fn validate_crop_source_pdf_binding(doc: &Document, source_pdf: &Path) -> Result<(), Failure> {
    let bytes = std::fs::read(source_pdf)
        .map_err(|_| Failure::Usage(format!("cannot read input: {}", source_pdf.display())))?;
    if !bytes[..bytes.len().min(1024)]
        .windows(5)
        .any(|window| window == b"%PDF-")
    {
        return Err(Failure::Usage(
            "crop source PDF does not contain a PDF header".to_string(),
        ));
    }
    let actual = source_fingerprint(&bytes);
    if actual != doc.source.fingerprint {
        return Err(Failure::Usage(
            "crop source PDF fingerprint does not match document source fingerprint".to_string(),
        ));
    }
    Ok(())
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
        Some(crop_ref_for(page, bbox)?)
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

#[derive(Debug)]
struct CropDescriptor {
    page: String,
    bbox: [i64; 4],
    check_ids: Vec<String>,
    text_sha256: Option<String>,
}

fn write_crop_descriptors(crop_dir: &Path, report: &VerificationReport) -> Result<(), Failure> {
    std::fs::create_dir_all(crop_dir).map_err(|_| {
        Failure::Usage(format!(
            "cannot create crop artifact directory: {}",
            crop_dir.display()
        ))
    })?;

    let mut descriptors: BTreeMap<String, CropDescriptor> = BTreeMap::new();
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
                descriptors.insert(
                    crop_ref.to_string(),
                    CropDescriptor {
                        page: page.to_string(),
                        bbox,
                        check_ids: vec![check.id.clone()],
                        text_sha256,
                    },
                );
            }
        }
    }

    for (crop_ref, descriptor) in descriptors {
        let path = crop_descriptor_path(crop_dir, &crop_ref)?;
        let mut object = serde_json::Map::new();
        object.insert(
            "artifact_type".to_string(),
            serde_json::Value::String("ethos.crop_descriptor.v1".to_string()),
        );
        object.insert("bbox".to_string(), serde_json::json!(descriptor.bbox));
        object.insert(
            "check_ids".to_string(),
            serde_json::json!(descriptor.check_ids),
        );
        object.insert("crop_ref".to_string(), serde_json::Value::String(crop_ref));
        if let Some(document_fingerprint) = &report.document_fingerprint {
            object.insert(
                "document_fingerprint".to_string(),
                serde_json::Value::String(document_fingerprint.clone()),
            );
        }
        object.insert(
            "page".to_string(),
            serde_json::Value::String(descriptor.page),
        );
        object.insert(
            "rendering_status".to_string(),
            serde_json::Value::String("descriptor_only".to_string()),
        );
        object.insert(
            "schema_version".to_string(),
            serde_json::Value::String(ethos_core::SCHEMA_VERSION.to_string()),
        );
        if let Some(text_sha256) = descriptor.text_sha256 {
            object.insert(
                "text_sha256".to_string(),
                serde_json::Value::String(text_sha256),
            );
        }
        let mut bytes = ethos_core::c14n::c14n_bytes(&serde_json::Value::Object(object))
            .map_err(|e| EthosError::internal(e.message))?;
        bytes.push(b'\n');
        std::fs::write(&path, bytes).map_err(|_| {
            Failure::Usage(format!(
                "cannot write crop descriptor artifact: {}",
                path.display()
            ))
        })?;
    }

    Ok(())
}

fn crop_descriptor_path(crop_dir: &Path, crop_ref: &str) -> Result<PathBuf, Failure> {
    let path = Path::new(crop_ref);
    if path.components().count() != 1
        || path.file_name().and_then(|name| name.to_str()) != Some(crop_ref)
    {
        return Err(Failure::Ethos(EthosError::internal(
            "crop_ref is not a safe descriptor filename",
        )));
    }
    Ok(crop_dir.join(path))
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
