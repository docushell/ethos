use ethos_core::verify_types::{VerificationReport, HARDENED_VERIFICATION_SCHEMA_VERSION};

use crate::{read_file_limited, Failure, ReportHtmlArgs};

pub(crate) fn html(args: ReportHtmlArgs) -> Result<(), Failure> {
    let report: VerificationReport = serde_json::from_slice(&read_file_limited(&args.input, crate::default_max_input_bytes())?)
        .map_err(|_| Failure::Usage("input is not a supported verification report".to_string()))?;
    if report.schema_version != ethos_core::SCHEMA_VERSION && report.schema_version != HARDENED_VERIFICATION_SCHEMA_VERSION {
        return Err(Failure::Usage("verification report schema_version is not supported".to_string()));
    }
    let crop_root = args.crop_root.as_deref().map(validate_crop_root).transpose()?;
    let bytes = render(&report, crop_root.as_deref()).into_bytes();
    std::fs::write(&args.out, bytes).map_err(|_| Failure::Usage(format!("cannot write output: {}", args.out.display())))
}

fn validate_crop_root(value: &str) -> Result<String, Failure> {
    if value.is_empty() || value.starts_with('/') || value.contains("\\") || value.contains("..") || value.contains('?') || value.contains('#') || value.contains("://") || value.split('/').any(str::is_empty) {
        return Err(Failure::Usage("--crop-root must be a safe relative prefix".to_string()));
    }
    Ok(value.trim_end_matches('/').to_string())
}

fn escape(value: &str) -> String { value.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;").replace('\'', "&#39;") }

fn safe_crop_basename(value: &str) -> Option<&str> {
    (!value.is_empty() && !value.contains(['/', '\\', '?', '#']) && !value.contains(".."))
        .then_some(value)
}

fn render(report: &VerificationReport, crop_root: Option<&str>) -> String {
    let proof = report.proof_summary();
    let mut out = String::from("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>Ethos proof report</title><style>body{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem}code{overflow-wrap:anywhere}article{border-top:1px solid #ccc;padding:1rem 0}.ok{color:#075b2d}.bad{color:#9b1c1c}</style></head><body><h1>Ethos proof report</h1>");
    out.push_str(&format!("<p class=\"{}\">Proof status: <strong>{}</strong>; request certified: <strong>{}</strong>.</p>", if report.all_evidence_grounded {"ok"} else {"bad"}, proof.proof_status.as_str(), report.all_evidence_grounded));
    out.push_str(&format!("<dl><dt>Document fingerprint</dt><dd><code>{}</code></dd><dt>Fingerprint stale</dt><dd>{}</dd><dt>Verification config hash</dt><dd><code>{}</code></dd><dt>Grounding parser</dt><dd>{} {}</dd></dl>", escape(report.document_fingerprint.as_deref().unwrap_or("unavailable")), report.fingerprint_stale, escape(&report.verification_config_sha256), escape(&report.grounding.parser.name), escape(&report.grounding.parser.version)));
    out.push_str("<p>Ethos verifies citation grounding, not semantic truth, answer relevance, completeness, or synthesis quality.</p><h2>Checks</h2>");
    for check in &report.checks {
        out.push_str(&format!("<article><h3>{}: {:?}</h3><p>Status: <strong>{:?}</strong>; match method: {:?}; semantic unverified: {}.</p><p>Claim: {}</p><p>Locator: <code>{}</code></p>", escape(&check.id), check.claim.kind, check.status, check.match_method, check.semantic_unverified, escape(check.claim.text.as_deref().unwrap_or("(presence)")), escape(&serde_json::to_string(&check.claim.citation).unwrap_or_default())));
        if let Some(evidence) = &check.evidence {
            out.push_str(&format!("<p>Evidence: {}</p><p>Page: {}; bbox: {}</p>", escape(evidence.text.as_deref().unwrap_or("unavailable")), escape(evidence.page.as_deref().unwrap_or("unavailable")), escape(&evidence.bbox.map(|bbox| format!("{:?}", bbox)).unwrap_or_else(|| "unavailable".to_string()))));
            if let Some(crop_ref) = evidence.crop_ref.as_deref() {
                if let (Some(root), Some(name)) = (crop_root, safe_crop_basename(crop_ref)) {
                    out.push_str(&format!("<p>Crop: <a href=\"{}/{}\">{}</a></p>", escape(root), escape(name), escape(name)));
                } else { out.push_str(&format!("<p>Crop unavailable in this standalone report: {}</p>", escape(crop_ref))); }
            }
        }
        out.push_str("</article>");
    }
    out.push_str("</body></html>\n"); out
}
