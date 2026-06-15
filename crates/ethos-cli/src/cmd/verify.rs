use std::collections::BTreeMap;
use std::collections::HashSet;
use std::path::{Path, PathBuf};

use ethos_core::error::EthosError;
use ethos_core::fingerprint::{is_fingerprint_form, source_fingerprint};
use ethos_core::geom::QRect;
use ethos_core::grounding::{
    Capabilities, GroundingElement, GroundingSource, GroundingSpan, GroundingTable, PageGeometry,
    ParserIdentity,
};
use ethos_core::model::Document;
use ethos_core::verify_types::{
    ClaimKind, EvidenceOptions, VerificationConfig, VerificationReport,
};
use ethos_grounding_opendataloader_json::OdlJsonSource;
use ethos_pdf::PdfiumBackend;
use ethos_verify::CitationInput;

use crate::{
    default_max_input_bytes, read_document, read_file_limited, write_output, Failure, VerifyArgs,
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
                    assign_logical_crop_refs(&mut report);
                    if let Some(crop_dir) = args.crop_dir.as_deref() {
                        write_crop_artifacts(crop_dir, &report, crop_source_pdf.as_ref())?;
                    }
                    return write_report(args.out, report, args.fail_on_ungrounded);
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

    write_report(args.out, report, args.fail_on_ungrounded)
}

fn write_report(
    out: Option<PathBuf>,
    report: VerificationReport,
    fail_on_ungrounded: bool,
) -> Result<(), Failure> {
    let value = serde_json::to_value(&report).map_err(|e| EthosError::internal(e.to_string()))?;
    let mut bytes =
        ethos_core::c14n::c14n_bytes(&value).map_err(|e| EthosError::internal(e.message))?;
    bytes.push(b'\n');
    let all_evidence_grounded = report.all_evidence_grounded;
    write_output(out, &bytes)?;
    if fail_on_ungrounded && !all_evidence_grounded {
        return Err(Failure::Ungrounded);
    }
    Ok(())
}

struct CropSourcePdf {
    bytes: Vec<u8>,
    fingerprint: String,
}

fn load_bound_crop_source_pdf(doc: &Document, source_pdf: &Path) -> Result<CropSourcePdf, Failure> {
    let bytes = read_file_limited(source_pdf, default_max_input_bytes())?;
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
    Ok(CropSourcePdf {
        bytes,
        fingerprint: actual,
    })
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

fn logical_crop_ref_for(
    document_fingerprint: &str,
    check_id: &str,
    page: &str,
) -> Result<String, Failure> {
    let value = serde_json::json!({
        "check_id": check_id,
        "document_fingerprint": document_fingerprint,
        "page": page,
        "version": "ethos.logical_crop_ref.v1",
    });
    let hash = ethos_core::c14n::sha256_hex(&value)
        .map_err(|e| Failure::Ethos(EthosError::internal(e.message)))?;
    Ok(format!("crop-{hash}.json"))
}

fn assign_logical_crop_refs(report: &mut VerificationReport) {
    let Some(document_fingerprint) = report.document_fingerprint.as_deref() else {
        return;
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
        if let Ok(crop_ref) = logical_crop_ref_for(document_fingerprint, &check.id, page) {
            evidence.crop_ref = Some(crop_ref);
        }
    }
}

#[derive(Debug)]
struct CropDescriptor {
    page: String,
    bbox: [i64; 4],
    check_ids: Vec<String>,
    text_sha256: Option<String>,
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
        object.insert(
            "crop_ref".to_string(),
            serde_json::Value::String(crop_ref.clone()),
        );
        if let Some(document_fingerprint) = &report.document_fingerprint {
            object.insert(
                "document_fingerprint".to_string(),
                serde_json::Value::String(document_fingerprint.clone()),
            );
        }
        object.insert(
            "page".to_string(),
            serde_json::Value::String(descriptor.page.clone()),
        );
        object.insert(
            "rendering_status".to_string(),
            serde_json::Value::String(if source_pdf.is_some() {
                "rendered".to_string()
            } else {
                "descriptor_only".to_string()
            }),
        );
        object.insert(
            "schema_version".to_string(),
            serde_json::Value::String(ethos_core::SCHEMA_VERSION.to_string()),
        );
        if let Some(text_sha256) = &descriptor.text_sha256 {
            object.insert(
                "text_sha256".to_string(),
                serde_json::Value::String(text_sha256.clone()),
            );
        }
        if let Some(source_pdf) = source_pdf {
            let rendered = render_crop_png(source_pdf, &descriptor)?;
            let rendered_ref = rendered_ref_for(&crop_ref)?;
            let rendered_path = crop_artifact_path(crop_dir, &rendered_ref)?;
            std::fs::write(&rendered_path, &rendered.bytes).map_err(|_| {
                Failure::Usage(format!(
                    "cannot write rendered crop artifact: {}",
                    rendered_path.display()
                ))
            })?;
            object.insert(
                "rendered_format".to_string(),
                serde_json::Value::String("png".to_string()),
            );
            object.insert(
                "rendered_height_px".to_string(),
                serde_json::json!(rendered.height_px),
            );
            object.insert(
                "rendered_ref".to_string(),
                serde_json::Value::String(rendered_ref),
            );
            object.insert(
                "rendered_sha256".to_string(),
                serde_json::Value::String(ethos_core::c14n::sha256_hex_bytes(&rendered.bytes)),
            );
            object.insert(
                "rendered_width_px".to_string(),
                serde_json::json!(rendered.width_px),
            );
            object.insert(
                "source_pdf_fingerprint".to_string(),
                serde_json::Value::String(source_pdf.fingerprint.clone()),
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
    crop_artifact_path(crop_dir, crop_ref)
}

fn crop_artifact_path(crop_dir: &Path, crop_ref: &str) -> Result<PathBuf, Failure> {
    let path = Path::new(crop_ref);
    if path.components().count() != 1
        || path.file_name().and_then(|name| name.to_str()) != Some(crop_ref)
    {
        return Err(Failure::Ethos(EthosError::internal(
            "crop_ref is not a safe artifact filename",
        )));
    }
    Ok(crop_dir.join(path))
}

struct RenderedCrop {
    width_px: u32,
    height_px: u32,
    bytes: Vec<u8>,
}

fn render_crop_png(
    source_pdf: &CropSourcePdf,
    descriptor: &CropDescriptor,
) -> Result<RenderedCrop, Failure> {
    let page_index = native_page_index(&descriptor.page)?;
    let bbox = QRect::new(
        descriptor.bbox[0],
        descriptor.bbox[1],
        descriptor.bbox[2],
        descriptor.bbox[3],
    )
    .map_err(|_| Failure::Ethos(EthosError::internal("crop descriptor bbox is malformed")))?;
    let raw = PdfiumBackend::default().render_crop_raw(&source_pdf.bytes, page_index, bbox)?;
    let bytes = png_from_bgra(raw.width_px, raw.height_px, raw.stride, &raw.bytes)?;
    Ok(RenderedCrop {
        width_px: raw.width_px,
        height_px: raw.height_px,
        bytes,
    })
}

fn native_page_index(page: &str) -> Result<u32, Failure> {
    let Some(digits) = page.strip_prefix('p') else {
        return Err(Failure::Ethos(EthosError::internal(
            "crop descriptor page is not a native Ethos page id",
        )));
    };
    if digits.len() != 4 || !digits.as_bytes().iter().all(u8::is_ascii_digit) {
        return Err(Failure::Ethos(EthosError::internal(
            "crop descriptor page is not a native Ethos page id",
        )));
    }
    let page_index = digits
        .parse::<u32>()
        .map_err(|_| EthosError::internal("crop descriptor page index overflow"))?;
    if page_index == 0 {
        return Err(Failure::Ethos(EthosError::internal(
            "crop descriptor page index must be positive",
        )));
    }
    Ok(page_index)
}

fn rendered_ref_for(crop_ref: &str) -> Result<String, Failure> {
    let Some(stem) = crop_ref.strip_suffix(".json") else {
        return Err(Failure::Ethos(EthosError::internal(
            "crop_ref is not a descriptor filename",
        )));
    };
    Ok(format!("{stem}.png"))
}

fn png_from_bgra(
    width_px: u32,
    height_px: u32,
    stride: u32,
    bgra: &[u8],
) -> Result<Vec<u8>, Failure> {
    let width =
        usize::try_from(width_px).map_err(|_| EthosError::internal("PNG width overflow"))?;
    let height =
        usize::try_from(height_px).map_err(|_| EthosError::internal("PNG height overflow"))?;
    let stride =
        usize::try_from(stride).map_err(|_| EthosError::internal("PNG stride overflow"))?;
    let row_bytes = width
        .checked_mul(4)
        .ok_or_else(|| EthosError::internal("PNG row width overflow"))?;
    if stride < row_bytes {
        return Err(Failure::Ethos(EthosError::internal(
            "rendered crop stride is smaller than row width",
        )));
    }
    let expected_len = stride
        .checked_mul(height)
        .ok_or_else(|| EthosError::internal("rendered crop buffer length overflow"))?;
    if bgra.len() != expected_len {
        return Err(Failure::Ethos(EthosError::internal(
            "rendered crop buffer length mismatch",
        )));
    }

    let scanline_bytes = row_bytes
        .checked_add(1)
        .and_then(|row| row.checked_mul(height))
        .ok_or_else(|| EthosError::internal("PNG scanline buffer length overflow"))?;
    let mut scanlines = Vec::with_capacity(scanline_bytes);
    for row in 0..height {
        scanlines.push(0);
        let row_start = row
            .checked_mul(stride)
            .ok_or_else(|| EthosError::internal("PNG source row offset overflow"))?;
        for pixel in bgra[row_start..row_start + row_bytes].chunks_exact(4) {
            scanlines.extend_from_slice(&[pixel[2], pixel[1], pixel[0], pixel[3]]);
        }
    }

    let mut png = Vec::new();
    png.extend_from_slice(b"\x89PNG\r\n\x1a\n");
    let mut ihdr = Vec::with_capacity(13);
    ihdr.extend_from_slice(&width_px.to_be_bytes());
    ihdr.extend_from_slice(&height_px.to_be_bytes());
    ihdr.extend_from_slice(&[8, 6, 0, 0, 0]);
    write_png_chunk(&mut png, b"IHDR", &ihdr)?;
    let idat = zlib_store(&scanlines)?;
    write_png_chunk(&mut png, b"IDAT", &idat)?;
    write_png_chunk(&mut png, b"IEND", &[])?;
    Ok(png)
}

fn zlib_store(data: &[u8]) -> Result<Vec<u8>, Failure> {
    let mut out = Vec::new();
    out.extend_from_slice(&[0x78, 0x01]);
    let mut remaining = data;
    while !remaining.is_empty() {
        let len = remaining.len().min(u16::MAX as usize);
        let final_block = len == remaining.len();
        out.push(if final_block { 0x01 } else { 0x00 });
        let len_u16 = u16::try_from(len).expect("block length is capped at u16::MAX");
        out.extend_from_slice(&len_u16.to_le_bytes());
        out.extend_from_slice(&(!len_u16).to_le_bytes());
        out.extend_from_slice(&remaining[..len]);
        remaining = &remaining[len..];
    }
    if data.is_empty() {
        out.push(0x01);
        out.extend_from_slice(&0u16.to_le_bytes());
        out.extend_from_slice(&u16::MAX.to_le_bytes());
    }
    out.extend_from_slice(&adler32(data).to_be_bytes());
    Ok(out)
}

fn write_png_chunk(out: &mut Vec<u8>, kind: &[u8; 4], data: &[u8]) -> Result<(), Failure> {
    let len = u32::try_from(data.len()).map_err(|_| EthosError::internal("PNG chunk too large"))?;
    out.extend_from_slice(&len.to_be_bytes());
    out.extend_from_slice(kind);
    out.extend_from_slice(data);
    let mut crc_input = Vec::with_capacity(kind.len() + data.len());
    crc_input.extend_from_slice(kind);
    crc_input.extend_from_slice(data);
    out.extend_from_slice(&crc32(&crc_input).to_be_bytes());
    Ok(())
}

fn adler32(data: &[u8]) -> u32 {
    const MOD_ADLER: u32 = 65_521;
    let mut a = 1u32;
    let mut b = 0u32;
    for byte in data {
        a = (a + u32::from(*byte)) % MOD_ADLER;
        b = (b + a) % MOD_ADLER;
    }
    (b << 16) | a
}

fn crc32(data: &[u8]) -> u32 {
    let mut crc = 0xFFFF_FFFFu32;
    for byte in data {
        crc ^= u32::from(*byte);
        for _ in 0..8 {
            let mask = 0u32.wrapping_sub(crc & 1);
            crc = (crc >> 1) ^ (0xEDB8_8320 & mask);
        }
    }
    !crc
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

#[cfg(test)]
mod tests {
    use super::*;
    use ethos_core::verify_types::{Check, CheckStatus, Evidence, GroundingMeta, MatchMethod};

    #[test]
    fn png_from_bgra_writes_png_signature_and_dimensions() {
        let bgra = [
            0, 0, 255, 255, // red, opaque
            0, 255, 0, 128, // green, half alpha
        ];
        let png = match png_from_bgra(2, 1, 8, &bgra) {
            Ok(png) => png,
            Err(_) => panic!("PNG encoding should succeed"),
        };

        assert!(png.starts_with(b"\x89PNG\r\n\x1a\n"));
        assert_eq!(&png[12..16], b"IHDR");
        assert_eq!(u32::from_be_bytes(png[16..20].try_into().unwrap()), 2);
        assert_eq!(u32::from_be_bytes(png[20..24].try_into().unwrap()), 1);
        assert_eq!(&png[png.len() - 8..png.len() - 4], b"IEND");
    }

    #[test]
    fn png_from_bgra_rejects_mismatched_buffer_length() {
        let err = png_from_bgra(2, 1, 8, &[0, 0, 0, 255]).unwrap_err();
        match err {
            Failure::Ethos(error) => {
                assert_eq!(error.message, "rendered crop buffer length mismatch");
            }
            _ => panic!("expected ethos failure"),
        }
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

        assign_logical_crop_refs(&mut report);

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
}
