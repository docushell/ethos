//! # ethos-pdf — WS-ENGINE lane (Milestone A)
//!
//! The only crate that loads PDFium (invariant 3). Everything crossing
//! [`EthosPdfBackend`] is already normalized + quantized (invariant 1: quantize-at-
//! extraction lives here); public schemas/APIs never see PDFium types.
//!
//! This first WS-ENGINE slice uses a small dynamic FFI boundary over the PDFium C API.
//! Runtime loading is explicit through `ETHOS_PDFIUM_LIBRARY_PATH`, so parser output
//! cannot accidentally depend on an unknown library from a host search path.

#![deny(unsafe_op_in_unsafe_fn)]
#![warn(missing_docs)]

use std::collections::{BTreeMap, HashSet};
use std::env;
use std::ffi::{c_char, c_int, c_ulong, c_void, CString};
use std::path::{Path, PathBuf};
use std::ptr;
use std::slice;
use std::sync::{Mutex, OnceLock};

use ethos_core::codes::WarningCode;
use ethos_core::config::{PageSelection, ParseConfig};
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::geom::{quantize, QRect};
use ethos_core::ids::{page_id, span_id, warning_id};
use ethos_core::model::{Page, Span, SpanOriginLocator, Warning};
use ethos_core::traits::{BackendManifest, EthosPdfBackend, Extraction};
use serde::{Deserialize, Serialize};

/// Environment variable containing the exact PDFium dynamic library path.
pub const PDFIUM_LIBRARY_PATH_ENV: &str = "ETHOS_PDFIUM_LIBRARY_PATH";

/// Optional environment variable carrying the pinned PDFium release/version string.
pub const PDFIUM_VERSION_ENV: &str = "ETHOS_PDFIUM_VERSION";

/// Optional environment variable containing the downloaded Phase 1 release artifact path.
pub const PDFIUM_ARTIFACT_PATH_ENV: &str = "ETHOS_PDFIUM_ARTIFACT_PATH";

/// Profile quantization: 100 quanta per PDF point.
pub const QUANTUM_PER_POINT: u32 = 100;
const ORIGIN_LOCATOR_POLICY: &str = "origin-run-locator-v1";

const DETERMINISTIC_PROFILE_JSON: &str = include_str!(concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../../profiles/ethos-deterministic-v1.json"
));
const FONT_SUBSTITUTION_TABLE_JSON: &str = include_str!("../assets/font-substitution-table.json");

/// PDFium has process-global library state; serialize init/load/destroy for now.
static PDFIUM_LOCK: Mutex<()> = Mutex::new(());
static PINNED_PDFIUM_PROFILE: OnceLock<PinnedPdfiumBackend> = OnceLock::new();
static FONT_SUBSTITUTION_TABLE: OnceLock<FontSubstitutionTable> = OnceLock::new();

/// PDFium backend implementation.
#[derive(Debug, Clone, Default)]
pub struct PdfiumBackend {
    library_path: Option<PathBuf>,
    artifact_path: Option<PathBuf>,
    version: Option<String>,
}

/// Debug-only report of PDFium text geometry signals.
///
/// This is not part of the canonical document contract. It exists so Gate Zero
/// investigations can compare native PDFium geometry sources across platforms
/// before changing parser output or fingerprint policy.
#[derive(Debug, Serialize)]
pub struct GeometryProbeReport {
    /// Report schema identifier.
    pub schema_version: String,
    /// Quantization used for every reported coordinate.
    pub quantum_per_point: u32,
    /// Backend manifest for the loaded PDFium runtime.
    pub backend: BackendManifest,
    /// Probed pages.
    pub pages: Vec<GeometryProbePage>,
}

/// Per-page debug geometry signals.
#[derive(Debug, Serialize)]
pub struct GeometryProbePage {
    /// Canonical page id.
    pub id: String,
    /// 1-based original page index.
    pub index: u32,
    /// Quantized page width.
    pub width: i64,
    /// Quantized page height.
    pub height: i64,
    /// Page rotation in degrees.
    pub rotation: u16,
    /// PDFium text character count.
    pub char_count: i32,
    /// Optional PDFium text symbols available in this runtime.
    pub symbols: GeometryProbeSymbols,
    /// Per-character geometry records.
    pub chars: Vec<GeometryProbeChar>,
    /// Parser-like text runs with alternative geometry unions.
    pub runs: Vec<GeometryProbeRun>,
}

/// Optional PDFium geometry symbols discovered at runtime.
#[derive(Debug, Serialize)]
pub struct GeometryProbeSymbols {
    /// Whether FPDFText_GetCharOrigin is available.
    pub char_origin: bool,
    /// Whether FPDFText_GetLooseCharBox is available.
    pub loose_char_box: bool,
    /// Whether FPDFText_CountRects and FPDFText_GetRect are available.
    pub text_rects: bool,
}

/// Per-character geometry probe record.
#[derive(Debug, Serialize)]
pub struct GeometryProbeChar {
    /// Zero-based PDFium character index.
    pub index: i32,
    /// Unicode scalar value reported by PDFium.
    pub unicode: u32,
    /// Character as a string when it is a valid scalar value.
    pub text: Option<String>,
    /// Why this character would break or be skipped by the parser run builder.
    pub parser_action: String,
    /// Current parser-critical FPDFText_GetCharBox geometry.
    pub char_box: Option<QRect>,
    /// FPDFText_GetLooseCharBox geometry when the symbol is present.
    pub loose_char_box: Option<QRect>,
    /// FPDFText_GetCharOrigin point when the symbol is present.
    pub char_origin: Option<[i64; 2]>,
    /// Deterministic font id used by the parser.
    pub font_id: Option<String>,
    /// PDFium font descriptor flags used by the parser.
    pub font_flags: Option<u32>,
    /// Quantized font size used by the parser.
    pub font_size_q: Option<i64>,
}

/// Parser-like text run with alternative PDFium geometry sources.
#[derive(Debug, Serialize)]
pub struct GeometryProbeRun {
    /// One-based run index on this page.
    pub index: u32,
    /// Run text after parser skip/break rules.
    pub text: String,
    /// First included PDFium character index.
    pub char_start: i32,
    /// Exclusive end PDFium character index.
    pub char_end: i32,
    /// Included character indices.
    pub char_indices: Vec<i32>,
    /// Current parser span bbox: union of FPDFText_GetCharBox records.
    pub char_box_union: Option<QRect>,
    /// Union of FPDFText_GetLooseCharBox records when available.
    pub loose_char_box_union: Option<QRect>,
    /// Rectangles from FPDFText_CountRects/GetRect for the run range when available.
    pub text_rects: Vec<QRect>,
    /// Union of text_rects when available.
    pub text_rect_union: Option<QRect>,
    /// Origin of first included character when available.
    pub first_origin: Option<[i64; 2]>,
    /// Origin of last included character when available.
    pub last_origin: Option<[i64; 2]>,
    /// Deterministic font id used by the parser.
    pub font_id: Option<String>,
    /// PDFium font descriptor flags used by the parser.
    pub font_flags: Option<u32>,
    /// Quantized font size used by the parser.
    pub font_size_q: Option<i64>,
}

/// Raw crop rendered from a PDF page.
///
/// This is the pre-encoding renderer boundary used by `ethos-render` work. It
/// deliberately exposes raw BGRA bytes and a byte hash before PNG/JPEG encoding
/// is added, so callers can test the renderer itself before artifact encoding.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RawCrop {
    /// 1-based source page index.
    pub page_index: u32,
    /// Source bbox in Ethos quantized top-left coordinates.
    pub bbox: QRect,
    /// Crop width in pixels.
    pub width_px: u32,
    /// Crop height in pixels.
    pub height_px: u32,
    /// Bytes per crop row.
    pub stride: u32,
    /// Pixel format for `bytes`.
    pub pixel_format: &'static str,
    /// SHA-256 hex digest of `bytes`.
    pub sha256: String,
    /// Tightly packed crop bytes.
    pub bytes: Vec<u8>,
}

impl PdfiumBackend {
    /// Construct a backend using an explicit PDFium dynamic library path.
    pub fn from_library_path(path: impl Into<PathBuf>) -> Self {
        PdfiumBackend {
            library_path: Some(path.into()),
            artifact_path: None,
            version: None,
        }
    }

    /// Add an explicit downloaded PDFium release artifact path for archive-hash verification.
    pub fn with_artifact_path(mut self, path: impl Into<PathBuf>) -> Self {
        self.artifact_path = Some(path.into());
        self
    }

    /// Construct a backend using an explicit PDFium path and pinned version string.
    pub fn with_version(mut self, version: impl Into<String>) -> Self {
        self.version = Some(version.into());
        self
    }

    fn configured_library_path(&self) -> Option<PathBuf> {
        self.library_path
            .clone()
            .or_else(|| env::var_os(PDFIUM_LIBRARY_PATH_ENV).map(PathBuf::from))
    }

    fn configured_artifact_path(&self) -> Option<PathBuf> {
        self.artifact_path
            .clone()
            .or_else(|| env::var_os(PDFIUM_ARTIFACT_PATH_ENV).map(PathBuf::from))
    }

    fn configured_version_override(&self) -> Option<String> {
        self.version
            .clone()
            .or_else(|| env::var(PDFIUM_VERSION_ENV).ok())
    }

    fn configured_version(&self) -> String {
        self.configured_version_override()
            .unwrap_or_else(|| pinned_pdfium_profile().version.clone())
    }

    /// Produce a debug-only geometry-source probe from PDFium text APIs.
    ///
    /// The returned data is diagnostic evidence only. It is intentionally
    /// separate from [`EthosPdfBackend::extract`] so parser behavior,
    /// canonical JSON, and document fingerprints cannot change by accident.
    pub fn geometry_probe(
        &self,
        pdf_bytes: &[u8],
        config: &ParseConfig,
    ) -> Result<GeometryProbeReport, EthosError> {
        validate_pdf_header(pdf_bytes)?;
        let _guard = PDFIUM_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let runtime = PdfiumRuntime::load(self)?;
        let doc = runtime.load_document(pdf_bytes)?;
        let page_count = doc.page_count()?;
        if page_count > config.limits.max_pages {
            return Err(EthosError::new(
                ErrorCode::PageLimitExceeded,
                "page count exceeds configured limit",
            ));
        }
        validate_page_selection(&config.pages, page_count)?;

        let mut pages = Vec::new();
        for page_index in 0..page_count {
            let original_page = page_index + 1;
            if !config.pages.contains(original_page) {
                continue;
            }
            let page = doc.load_page(page_index)?;
            pages.push(page.geometry_probe_page(original_page)?);
        }

        Ok(GeometryProbeReport {
            schema_version: "ethos-pdfium-geometry-probe-v1".to_string(),
            quantum_per_point: QUANTUM_PER_POINT,
            backend: self.manifest(),
            pages,
        })
    }

    /// Render a raw BGRA crop for a 1-based page and quantized top-left bbox.
    ///
    /// The current boundary renders the page at 1 pixel per PDF point, then
    /// crops the requested bbox. It is intentionally simple; direct crop-window
    /// rendering can replace it later without changing the output contract.
    pub fn render_crop_raw(
        &self,
        pdf_bytes: &[u8],
        page_index: u32,
        bbox: QRect,
    ) -> Result<RawCrop, EthosError> {
        validate_pdf_header(pdf_bytes)?;
        if page_index == 0 {
            return Err(EthosError::new(
                ErrorCode::PageLimitExceeded,
                "page selection out of document range",
            ));
        }
        let _guard = PDFIUM_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let runtime = PdfiumRuntime::load(self)?;
        let doc = runtime.load_document(pdf_bytes)?;
        let page_count = doc.page_count()?;
        if page_index > page_count {
            return Err(EthosError::new(
                ErrorCode::PageLimitExceeded,
                "page selection out of document range",
            ));
        }
        let page = doc.load_page(page_index - 1)?;
        page.render_crop_raw(page_index, bbox)
    }
}

impl EthosPdfBackend for PdfiumBackend {
    fn manifest(&self) -> BackendManifest {
        let platform_sha256 = self
            .configured_library_path()
            .and_then(|path| std::fs::read(path).ok())
            .map(|bytes| ethos_core::c14n::sha256_hex_bytes(&bytes))
            .unwrap_or_else(|| "0".repeat(64));
        BackendManifest {
            id: "pdfium".to_string(),
            phase: 1,
            version: self.configured_version(),
            platform_sha256,
        }
    }

    fn page_count(&self, pdf_bytes: &[u8]) -> Result<u32, EthosError> {
        validate_pdf_header(pdf_bytes)?;
        let _guard = PDFIUM_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let runtime = PdfiumRuntime::load(self)?;
        let doc = runtime.load_document(pdf_bytes)?;
        doc.page_count()
    }

    fn extract(&self, pdf_bytes: &[u8], config: &ParseConfig) -> Result<Extraction, EthosError> {
        validate_pdf_header(pdf_bytes)?;
        let _guard = PDFIUM_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let runtime = PdfiumRuntime::load(self)?;
        let doc = runtime.load_document(pdf_bytes)?;
        let page_count = doc.page_count()?;
        if page_count > config.limits.max_pages {
            return Err(EthosError::new(
                ErrorCode::PageLimitExceeded,
                "page count exceeds configured limit",
            ));
        }
        validate_page_selection(&config.pages, page_count)?;

        let mut pages = Vec::new();
        let mut spans = Vec::new();
        let mut warnings = Vec::new();
        let mut next_span = 1u32;
        let mut next_warning = 1u32;

        for page_index in 0..page_count {
            let original_page = page_index + 1;
            if !config.pages.contains(original_page) {
                continue;
            }
            let page = doc.load_page(page_index)?;
            let page_model = page.model_page(original_page)?;
            let span_count_before = spans.len();
            page.extract_text_spans(&page_model, &mut next_span, &mut spans)?;
            if spans.len() == span_count_before {
                warnings.push(Warning {
                    id: warning_id(next_warning)?,
                    code: WarningCode::ImageOnlyPage,
                    message: "page has no extractable text; OCR is required for this page"
                        .to_string(),
                    page: Some(page_model.id.clone()),
                    element_ref: None,
                    span_ref: None,
                    region_ref: None,
                });
                next_warning += 1;
            }
            pages.push(page_model);
        }

        if spans.is_empty() {
            return Err(EthosError::new(
                ErrorCode::OcrRequired,
                "no extractable text; OCR is required",
            ));
        }

        Ok(Extraction {
            pages,
            spans,
            regions: Vec::new(),
            warnings,
        })
    }
}

fn validate_page_selection(selection: &PageSelection, page_count: u32) -> Result<(), EthosError> {
    selection.validate_against(page_count).map_err(|_| {
        EthosError::new(
            ErrorCode::PageLimitExceeded,
            "page selection out of document range",
        )
    })
}

fn validate_pdf_header(pdf_bytes: &[u8]) -> Result<(), EthosError> {
    let window = &pdf_bytes[..pdf_bytes.len().min(1024)];
    if window.windows(5).any(|w| w == b"%PDF-") {
        Ok(())
    } else {
        Err(EthosError::new(
            ErrorCode::InvalidPdf,
            "input does not contain a PDF header",
        ))
    }
}

fn quantize_coord(value: f64) -> Result<i64, EthosError> {
    quantize(value, QUANTUM_PER_POINT)
        .map_err(|_| EthosError::new(ErrorCode::InternalError, "coordinate quantization failed"))
}

fn pixel_extent(points: f64) -> Result<u32, EthosError> {
    if !points.is_finite() || points <= 0.0 {
        return Err(EthosError::new(
            ErrorCode::CorruptPdf,
            "PDF page has invalid dimensions",
        ));
    }
    if points.ceil() > f64::from(c_int::MAX) {
        return Err(EthosError::internal("render bitmap dimension overflow"));
    }
    Ok(points.ceil() as u32)
}

fn floor_quantized_pixel(value: i64) -> i64 {
    value.div_euclid(i64::from(QUANTUM_PER_POINT))
}

fn ceil_quantized_pixel(value: i64) -> i64 {
    let quantum = i64::from(QUANTUM_PER_POINT);
    value
        .checked_add(quantum - 1)
        .unwrap_or(i64::MAX)
        .div_euclid(quantum)
}

fn clamp_pixel(value: i64, max: u32) -> u32 {
    value.clamp(0, i64::from(max)) as u32
}

fn crop_window(
    bbox: QRect,
    page_width_px: u32,
    page_height_px: u32,
) -> Result<(u32, u32, u32, u32), EthosError> {
    let x0 = clamp_pixel(floor_quantized_pixel(bbox.x0), page_width_px);
    let y0 = clamp_pixel(floor_quantized_pixel(bbox.y0), page_height_px);
    let x1 = clamp_pixel(ceil_quantized_pixel(bbox.x1), page_width_px);
    let y1 = clamp_pixel(ceil_quantized_pixel(bbox.y1), page_height_px);
    if x0 >= x1 || y0 >= y1 {
        return Err(EthosError::internal(
            "crop bbox has no positive pixel extent",
        ));
    }
    Ok((x0, y0, x1 - x0, y1 - y0))
}

fn qrect_from_pdfium_char_box(
    page_height_pts: f64,
    left: f64,
    right: f64,
    bottom: f64,
    top: f64,
) -> Result<QRect, EthosError> {
    let x0 = left.min(right);
    let x1 = left.max(right);
    let y0 = page_height_pts - top.max(bottom);
    let y1 = page_height_pts - top.min(bottom);
    QRect::new(
        quantize_coord(x0)?,
        quantize_coord(y0)?,
        quantize_coord(x1)?,
        quantize_coord(y1)?,
    )
    .map_err(|_| EthosError::internal("malformed character bbox"))
}

fn union_rect(a: QRect, b: QRect) -> QRect {
    QRect {
        x0: a.x0.min(b.x0),
        y0: a.y0.min(b.y0),
        x1: a.x1.max(b.x1),
        y1: a.y1.max(b.y1),
    }
}

fn map_pdfium_error(code: c_ulong) -> EthosError {
    match code {
        4 => EthosError::new(
            ErrorCode::PasswordProtected,
            "document is encrypted or password-protected",
        ),
        5 => EthosError::new(
            ErrorCode::UnsupportedPdfFeature,
            "document uses a restricted security handler",
        ),
        3 => EthosError::new(ErrorCode::CorruptPdf, "PDF structure is corrupt"),
        6 => EthosError::new(ErrorCode::CorruptPdf, "PDF page tree is corrupt"),
        2 => EthosError::new(ErrorCode::CorruptPdf, "PDF could not be loaded"),
        _ => EthosError::new(ErrorCode::CorruptPdf, "PDFium could not load the document"),
    }
}

#[derive(Debug, Deserialize)]
struct DeterministicProfile {
    backend: PinnedPdfiumBackend,
}

#[derive(Debug, Deserialize)]
struct PinnedPdfiumBackend {
    id: String,
    phase: u8,
    version: String,
    upstream_version: String,
    v8: String,
    xfa: String,
    distribution: PinnedPdfiumDistribution,
    build_flags: PinnedPdfiumBuildFlags,
    platform_hashes: BTreeMap<String, String>,
    platform_artifacts: BTreeMap<String, PinnedPdfiumArtifact>,
    profile_doc: String,
}

#[derive(Debug, Deserialize)]
struct PinnedPdfiumDistribution {
    source: String,
    release_url: String,
    published_at: String,
    attestation: PinnedPdfiumAttestation,
}

#[derive(Debug, Deserialize)]
struct PinnedPdfiumAttestation {
    name: String,
    sha256: String,
}

#[derive(Debug, Deserialize)]
struct PinnedPdfiumBuildFlags {
    is_component_build: bool,
    is_debug: bool,
    pdf_enable_v8: bool,
    pdf_enable_xfa: bool,
    pdf_is_standalone: bool,
    pdf_use_partition_alloc: bool,
}

#[derive(Debug, Deserialize)]
struct PinnedPdfiumArtifact {
    name: String,
    target_os: String,
    target_cpu: String,
    runtime_library_path: String,
    runtime_library_sha256: String,
}

fn pinned_pdfium_profile() -> &'static PinnedPdfiumBackend {
    PINNED_PDFIUM_PROFILE.get_or_init(|| {
        let profile: DeterministicProfile = serde_json::from_str(DETERMINISTIC_PROFILE_JSON)
            .expect("profiles/ethos-deterministic-v1.json is valid JSON");
        validate_pinned_pdfium_profile(&profile.backend)
            .expect("profiles/ethos-deterministic-v1.json pins a valid PDFium Phase 1 profile");
        profile.backend
    })
}

fn validate_pinned_pdfium_profile(profile: &PinnedPdfiumBackend) -> Result<(), &'static str> {
    validate_pinned_pdfium_identity(profile)?;
    validate_pinned_pdfium_distribution(&profile.distribution)?;
    validate_pinned_pdfium_build_flags(&profile.build_flags)?;
    validate_pinned_pdfium_platforms(profile)?;
    Ok(())
}

fn validate_pinned_pdfium_identity(profile: &PinnedPdfiumBackend) -> Result<(), &'static str> {
    if profile.id != "pdfium"
        || profile.phase != 1
        || profile.version != "chromium/7881"
        || profile.upstream_version != "PDFium 151.0.7881.0"
        || profile.v8 != "disabled"
        || profile.xfa != "disabled"
        || profile.profile_doc != "docs/pdfium-profile.md"
    {
        return Err("unexpected PDFium profile identity");
    }
    Ok(())
}

fn validate_pinned_pdfium_distribution(
    distribution: &PinnedPdfiumDistribution,
) -> Result<(), &'static str> {
    if distribution.source != "bblanchon/pdfium-binaries"
        || distribution.attestation.name != "pdfium-attestation.json"
        || !is_sha256_hex(&distribution.attestation.sha256)
        || !distribution
            .release_url
            .starts_with("https://github.com/bblanchon/pdfium-binaries/releases/tag/")
        || !distribution.published_at.ends_with('Z')
    {
        return Err("unexpected PDFium distribution metadata");
    }
    Ok(())
}

fn validate_pinned_pdfium_build_flags(
    build_flags: &PinnedPdfiumBuildFlags,
) -> Result<(), &'static str> {
    if build_flags.is_component_build
        || build_flags.is_debug
        || build_flags.pdf_enable_v8
        || build_flags.pdf_enable_xfa
        || !build_flags.pdf_is_standalone
        || build_flags.pdf_use_partition_alloc
    {
        return Err("PDFium Phase 1 must be standalone release with V8/XFA disabled");
    }
    Ok(())
}

fn validate_pinned_pdfium_platforms(profile: &PinnedPdfiumBackend) -> Result<(), &'static str> {
    for platform in ["macos-arm64", "linux-x64", "windows-x64"] {
        let artifact_hash = profile
            .platform_hashes
            .get(platform)
            .ok_or("missing PDFium artifact hash")?;
        if !is_sha256_hex(artifact_hash) {
            return Err("malformed PDFium artifact hash");
        }
        let artifact = profile
            .platform_artifacts
            .get(platform)
            .ok_or("missing PDFium platform artifact metadata")?;
        if artifact.name.contains("-v8-")
            || artifact.name.contains("xfa")
            || !artifact.name.ends_with(".tgz")
            || artifact.runtime_library_path.is_empty()
            || !is_sha256_hex(&artifact.runtime_library_sha256)
        {
            return Err("malformed PDFium platform artifact metadata");
        }
        match platform {
            "macos-arm64"
                if artifact.name == "pdfium-mac-arm64.tgz"
                    && artifact.target_os == "mac"
                    && artifact.target_cpu == "arm64" => {}
            "linux-x64"
                if artifact.name == "pdfium-linux-x64.tgz"
                    && artifact.target_os == "linux"
                    && artifact.target_cpu == "x64" => {}
            "windows-x64"
                if artifact.name == "pdfium-win-x64.tgz"
                    && artifact.target_os == "win"
                    && artifact.target_cpu == "x64" => {}
            _ => return Err("unexpected PDFium platform artifact"),
        }
    }
    Ok(())
}

fn is_sha256_hex(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
}

fn current_platform_key() -> Option<&'static str> {
    if cfg!(all(target_os = "macos", target_arch = "aarch64")) {
        Some("macos-arm64")
    } else if cfg!(all(target_os = "linux", target_arch = "x86_64")) {
        Some("linux-x64")
    } else if cfg!(all(target_os = "windows", target_arch = "x86_64")) {
        Some("windows-x64")
    } else {
        None
    }
}

fn current_pdfium_pins(
    profile: &PinnedPdfiumBackend,
) -> Result<(&'static str, &str, &PinnedPdfiumArtifact), EthosError> {
    let platform = current_platform_key().ok_or_else(|| {
        EthosError::internal("pdfium phase 1 profile has no hash for this platform")
    })?;
    let artifact_hash = profile.platform_hashes.get(platform).ok_or_else(|| {
        EthosError::internal("pdfium phase 1 profile has no hash for this platform")
    })?;
    let artifact = profile.platform_artifacts.get(platform).ok_or_else(|| {
        EthosError::internal("pdfium phase 1 profile has no artifact for this platform")
    })?;
    Ok((platform, artifact_hash.as_str(), artifact))
}

fn validate_pinned_pdfium_payload(
    backend: &PdfiumBackend,
    library_path: &Path,
) -> Result<(), EthosError> {
    let profile = pinned_pdfium_profile();
    if let Some(version) = backend.configured_version_override() {
        let upstream_number = profile
            .upstream_version
            .strip_prefix("PDFium ")
            .unwrap_or(&profile.upstream_version);
        if version != profile.version
            && version != profile.upstream_version
            && version != upstream_number
        {
            return Err(EthosError::internal(
                "pdfium version does not match pinned phase 1 profile",
            ));
        }
    }

    let (_, artifact_hash, artifact) = current_pdfium_pins(profile)?;
    if let Some(artifact_path) = backend.configured_artifact_path() {
        if !artifact_path.is_file() {
            return Err(EthosError::internal(
                "pdfium artifact path does not point to a file",
            ));
        }
        let actual_artifact_hash = sha256_file(&artifact_path)?;
        if actual_artifact_hash != artifact_hash {
            return Err(EthosError::internal(
                "pdfium artifact does not match pinned phase 1 profile",
            ));
        }
    }

    let library_hash = sha256_file(library_path)?;
    if library_hash != artifact.runtime_library_sha256 {
        return Err(EthosError::internal(
            "pdfium library does not match pinned phase 1 profile",
        ));
    }

    Ok(())
}

fn sha256_file(path: &Path) -> Result<String, EthosError> {
    let bytes =
        std::fs::read(path).map_err(|_| EthosError::internal("failed to read pdfium payload"))?;
    Ok(ethos_core::c14n::sha256_hex_bytes(&bytes))
}

type FpdfDocument = *mut c_void;
type FpdfPage = *mut c_void;
type FpdfTextPage = *mut c_void;
type FpdfBitmap = *mut c_void;

#[cfg(not(windows))]
type FpdfInitLibrary = unsafe extern "C" fn();
#[cfg(windows)]
type FpdfInitLibrary = unsafe extern "system" fn();
#[cfg(not(windows))]
type FpdfDestroyLibrary = unsafe extern "C" fn();
#[cfg(windows)]
type FpdfDestroyLibrary = unsafe extern "system" fn();
#[cfg(not(windows))]
type FpdfLoadMemDocument64 =
    unsafe extern "C" fn(*const c_void, usize, *const c_char) -> FpdfDocument;
#[cfg(windows)]
type FpdfLoadMemDocument64 =
    unsafe extern "system" fn(*const c_void, usize, *const c_char) -> FpdfDocument;
#[cfg(not(windows))]
type FpdfCloseDocument = unsafe extern "C" fn(FpdfDocument);
#[cfg(windows)]
type FpdfCloseDocument = unsafe extern "system" fn(FpdfDocument);
#[cfg(not(windows))]
type FpdfGetLastError = unsafe extern "C" fn() -> c_ulong;
#[cfg(windows)]
type FpdfGetLastError = unsafe extern "system" fn() -> c_ulong;
#[cfg(not(windows))]
type FpdfGetPageCount = unsafe extern "C" fn(FpdfDocument) -> c_int;
#[cfg(windows)]
type FpdfGetPageCount = unsafe extern "system" fn(FpdfDocument) -> c_int;
#[cfg(not(windows))]
type FpdfLoadPage = unsafe extern "C" fn(FpdfDocument, c_int) -> FpdfPage;
#[cfg(windows)]
type FpdfLoadPage = unsafe extern "system" fn(FpdfDocument, c_int) -> FpdfPage;
#[cfg(not(windows))]
type FpdfClosePage = unsafe extern "C" fn(FpdfPage);
#[cfg(windows)]
type FpdfClosePage = unsafe extern "system" fn(FpdfPage);
#[cfg(not(windows))]
type FpdfGetPageWidthF = unsafe extern "C" fn(FpdfPage) -> f32;
#[cfg(windows)]
type FpdfGetPageWidthF = unsafe extern "system" fn(FpdfPage) -> f32;
#[cfg(not(windows))]
type FpdfGetPageHeightF = unsafe extern "C" fn(FpdfPage) -> f32;
#[cfg(windows)]
type FpdfGetPageHeightF = unsafe extern "system" fn(FpdfPage) -> f32;
#[cfg(not(windows))]
type FpdfPageGetRotation = unsafe extern "C" fn(FpdfPage) -> c_int;
#[cfg(windows)]
type FpdfPageGetRotation = unsafe extern "system" fn(FpdfPage) -> c_int;
#[cfg(not(windows))]
type FpdfTextLoadPage = unsafe extern "C" fn(FpdfPage) -> FpdfTextPage;
#[cfg(windows)]
type FpdfTextLoadPage = unsafe extern "system" fn(FpdfPage) -> FpdfTextPage;
#[cfg(not(windows))]
type FpdfTextClosePage = unsafe extern "C" fn(FpdfTextPage);
#[cfg(windows)]
type FpdfTextClosePage = unsafe extern "system" fn(FpdfTextPage);
#[cfg(not(windows))]
type FpdfTextCountChars = unsafe extern "C" fn(FpdfTextPage) -> c_int;
#[cfg(windows)]
type FpdfTextCountChars = unsafe extern "system" fn(FpdfTextPage) -> c_int;
#[cfg(not(windows))]
type FpdfTextGetUnicode = unsafe extern "C" fn(FpdfTextPage, c_int) -> u32;
#[cfg(windows)]
type FpdfTextGetUnicode = unsafe extern "system" fn(FpdfTextPage, c_int) -> u32;
#[cfg(not(windows))]
type FpdfTextGetCharBox =
    unsafe extern "C" fn(FpdfTextPage, c_int, *mut f64, *mut f64, *mut f64, *mut f64) -> c_int;
#[cfg(windows)]
type FpdfTextGetCharBox =
    unsafe extern "system" fn(FpdfTextPage, c_int, *mut f64, *mut f64, *mut f64, *mut f64) -> c_int;
#[cfg(not(windows))]
type FpdfTextGetLooseCharBox = unsafe extern "C" fn(FpdfTextPage, c_int, *mut FsRectF) -> c_int;
#[cfg(windows)]
type FpdfTextGetLooseCharBox =
    unsafe extern "system" fn(FpdfTextPage, c_int, *mut FsRectF) -> c_int;
#[cfg(not(windows))]
type FpdfTextGetCharOrigin = unsafe extern "C" fn(FpdfTextPage, c_int, *mut f64, *mut f64) -> c_int;
#[cfg(windows)]
type FpdfTextGetCharOrigin =
    unsafe extern "system" fn(FpdfTextPage, c_int, *mut f64, *mut f64) -> c_int;
#[cfg(not(windows))]
type FpdfTextCountRects = unsafe extern "C" fn(FpdfTextPage, c_int, c_int) -> c_int;
#[cfg(windows)]
type FpdfTextCountRects = unsafe extern "system" fn(FpdfTextPage, c_int, c_int) -> c_int;
#[cfg(not(windows))]
type FpdfTextGetRect =
    unsafe extern "C" fn(FpdfTextPage, c_int, *mut f64, *mut f64, *mut f64, *mut f64) -> c_int;
#[cfg(windows)]
type FpdfTextGetRect =
    unsafe extern "system" fn(FpdfTextPage, c_int, *mut f64, *mut f64, *mut f64, *mut f64) -> c_int;
#[cfg(not(windows))]
type FpdfTextGetFontSize = unsafe extern "C" fn(FpdfTextPage, c_int) -> f64;
#[cfg(windows)]
type FpdfTextGetFontSize = unsafe extern "system" fn(FpdfTextPage, c_int) -> f64;
#[cfg(not(windows))]
type FpdfTextGetFontInfo =
    unsafe extern "C" fn(FpdfTextPage, c_int, *mut c_void, c_ulong, *mut c_int) -> c_ulong;
#[cfg(windows)]
type FpdfTextGetFontInfo =
    unsafe extern "system" fn(FpdfTextPage, c_int, *mut c_void, c_ulong, *mut c_int) -> c_ulong;
#[cfg(not(windows))]
type FpdfTextIsGenerated = unsafe extern "C" fn(FpdfTextPage, c_int) -> c_int;
#[cfg(windows)]
type FpdfTextIsGenerated = unsafe extern "system" fn(FpdfTextPage, c_int) -> c_int;
#[cfg(not(windows))]
type FpdfTextIsHyphen = unsafe extern "C" fn(FpdfTextPage, c_int) -> c_int;
#[cfg(windows)]
type FpdfTextIsHyphen = unsafe extern "system" fn(FpdfTextPage, c_int) -> c_int;
#[cfg(not(windows))]
type FpdfBitmapCreate = unsafe extern "C" fn(c_int, c_int, c_int) -> FpdfBitmap;
#[cfg(windows)]
type FpdfBitmapCreate = unsafe extern "system" fn(c_int, c_int, c_int) -> FpdfBitmap;
#[cfg(not(windows))]
type FpdfBitmapDestroy = unsafe extern "C" fn(FpdfBitmap);
#[cfg(windows)]
type FpdfBitmapDestroy = unsafe extern "system" fn(FpdfBitmap);
#[cfg(not(windows))]
type FpdfBitmapFillRect = unsafe extern "C" fn(FpdfBitmap, c_int, c_int, c_int, c_int, c_ulong);
#[cfg(windows)]
type FpdfBitmapFillRect =
    unsafe extern "system" fn(FpdfBitmap, c_int, c_int, c_int, c_int, c_ulong);
#[cfg(not(windows))]
type FpdfBitmapGetBuffer = unsafe extern "C" fn(FpdfBitmap) -> *mut c_void;
#[cfg(windows)]
type FpdfBitmapGetBuffer = unsafe extern "system" fn(FpdfBitmap) -> *mut c_void;
#[cfg(not(windows))]
type FpdfBitmapGetStride = unsafe extern "C" fn(FpdfBitmap) -> c_int;
#[cfg(windows)]
type FpdfBitmapGetStride = unsafe extern "system" fn(FpdfBitmap) -> c_int;
#[cfg(not(windows))]
type FpdfRenderPageBitmap =
    unsafe extern "C" fn(FpdfBitmap, FpdfPage, c_int, c_int, c_int, c_int, c_int, c_int);
#[cfg(windows)]
type FpdfRenderPageBitmap =
    unsafe extern "system" fn(FpdfBitmap, FpdfPage, c_int, c_int, c_int, c_int, c_int, c_int);

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
struct FsRectF {
    left: f32,
    top: f32,
    right: f32,
    bottom: f32,
}

#[derive(Clone, Copy)]
struct PdfiumFunctions {
    init_library: FpdfInitLibrary,
    destroy_library: FpdfDestroyLibrary,
    load_mem_document64: FpdfLoadMemDocument64,
    close_document: FpdfCloseDocument,
    get_last_error: FpdfGetLastError,
    get_page_count: FpdfGetPageCount,
    load_page: FpdfLoadPage,
    close_page: FpdfClosePage,
    get_page_width_f: FpdfGetPageWidthF,
    get_page_height_f: FpdfGetPageHeightF,
    page_get_rotation: Option<FpdfPageGetRotation>,
    text_load_page: FpdfTextLoadPage,
    text_close_page: FpdfTextClosePage,
    text_count_chars: FpdfTextCountChars,
    text_get_unicode: FpdfTextGetUnicode,
    text_get_char_box: FpdfTextGetCharBox,
    text_get_loose_char_box: Option<FpdfTextGetLooseCharBox>,
    text_get_char_origin: Option<FpdfTextGetCharOrigin>,
    text_count_rects: Option<FpdfTextCountRects>,
    text_get_rect: Option<FpdfTextGetRect>,
    text_get_font_size: FpdfTextGetFontSize,
    text_get_font_info: Option<FpdfTextGetFontInfo>,
    text_is_generated: Option<FpdfTextIsGenerated>,
    text_is_hyphen: Option<FpdfTextIsHyphen>,
    bitmap_create: Option<FpdfBitmapCreate>,
    bitmap_destroy: Option<FpdfBitmapDestroy>,
    bitmap_fill_rect: Option<FpdfBitmapFillRect>,
    bitmap_get_buffer: Option<FpdfBitmapGetBuffer>,
    bitmap_get_stride: Option<FpdfBitmapGetStride>,
    render_page_bitmap: Option<FpdfRenderPageBitmap>,
}

impl PdfiumFunctions {
    fn load(library: &dylib::Library) -> Result<Self, EthosError> {
        // SAFETY: symbols are loaded from the configured PDFium dynamic library and
        // immediately copied into typed function pointers matching the C API.
        unsafe {
            Ok(PdfiumFunctions {
                init_library: library.symbol(b"FPDF_InitLibrary\0")?,
                destroy_library: library.symbol(b"FPDF_DestroyLibrary\0")?,
                load_mem_document64: library.symbol(b"FPDF_LoadMemDocument64\0")?,
                close_document: library.symbol(b"FPDF_CloseDocument\0")?,
                get_last_error: library.symbol(b"FPDF_GetLastError\0")?,
                get_page_count: library.symbol(b"FPDF_GetPageCount\0")?,
                load_page: library.symbol(b"FPDF_LoadPage\0")?,
                close_page: library.symbol(b"FPDF_ClosePage\0")?,
                get_page_width_f: library.symbol(b"FPDF_GetPageWidthF\0")?,
                get_page_height_f: library.symbol(b"FPDF_GetPageHeightF\0")?,
                page_get_rotation: library.optional_symbol(b"FPDFPage_GetRotation\0"),
                text_load_page: library.symbol(b"FPDFText_LoadPage\0")?,
                text_close_page: library.symbol(b"FPDFText_ClosePage\0")?,
                text_count_chars: library.symbol(b"FPDFText_CountChars\0")?,
                text_get_unicode: library.symbol(b"FPDFText_GetUnicode\0")?,
                text_get_char_box: library.symbol(b"FPDFText_GetCharBox\0")?,
                text_get_loose_char_box: library.optional_symbol(b"FPDFText_GetLooseCharBox\0"),
                text_get_char_origin: library.optional_symbol(b"FPDFText_GetCharOrigin\0"),
                text_count_rects: library.optional_symbol(b"FPDFText_CountRects\0"),
                text_get_rect: library.optional_symbol(b"FPDFText_GetRect\0"),
                text_get_font_size: library.symbol(b"FPDFText_GetFontSize\0")?,
                text_get_font_info: library.optional_symbol(b"FPDFText_GetFontInfo\0"),
                text_is_generated: library.optional_symbol(b"FPDFText_IsGenerated\0"),
                text_is_hyphen: library.optional_symbol(b"FPDFText_IsHyphen\0"),
                bitmap_create: library.optional_symbol(b"FPDFBitmap_Create\0"),
                bitmap_destroy: library.optional_symbol(b"FPDFBitmap_Destroy\0"),
                bitmap_fill_rect: library.optional_symbol(b"FPDFBitmap_FillRect\0"),
                bitmap_get_buffer: library.optional_symbol(b"FPDFBitmap_GetBuffer\0"),
                bitmap_get_stride: library.optional_symbol(b"FPDFBitmap_GetStride\0"),
                render_page_bitmap: library.optional_symbol(b"FPDF_RenderPageBitmap\0"),
            })
        }
    }

    fn geometry_probe_symbols(self) -> GeometryProbeSymbols {
        GeometryProbeSymbols {
            char_origin: self.text_get_char_origin.is_some(),
            loose_char_box: self.text_get_loose_char_box.is_some(),
            text_rects: self.text_count_rects.is_some() && self.text_get_rect.is_some(),
        }
    }
}

struct PdfiumRuntime {
    _library: dylib::Library,
    funcs: PdfiumFunctions,
    initialized: bool,
}

impl PdfiumRuntime {
    fn load(backend: &PdfiumBackend) -> Result<Self, EthosError> {
        let path = backend.configured_library_path().ok_or_else(|| {
            EthosError::internal(format!(
                "pdfium library path is not configured; set {PDFIUM_LIBRARY_PATH_ENV}"
            ))
        })?;
        if !path.is_file() {
            return Err(EthosError::internal(
                "pdfium library path does not point to a file",
            ));
        }
        validate_pinned_pdfium_payload(backend, &path)?;

        let library = dylib::Library::open(&path)?;
        let funcs = PdfiumFunctions::load(&library)?;
        // SAFETY: FPDF_InitLibrary initializes process-global PDFium state. Calls are
        // serialized by PDFIUM_LOCK.
        unsafe { (funcs.init_library)() };
        Ok(PdfiumRuntime {
            _library: library,
            funcs,
            initialized: true,
        })
    }

    fn load_document<'a>(&'a self, pdf_bytes: &[u8]) -> Result<PdfDocument<'a>, EthosError> {
        // SAFETY: PDFium reads the immutable byte slice only for the duration of
        // FPDF_LoadMemDocument64. The returned document is closed by PdfDocument::drop.
        let handle = unsafe {
            (self.funcs.load_mem_document64)(
                pdf_bytes.as_ptr().cast(),
                pdf_bytes.len(),
                ptr::null(),
            )
        };
        if handle.is_null() {
            // SAFETY: FPDF_GetLastError has no preconditions after a failed load.
            let code = unsafe { (self.funcs.get_last_error)() };
            Err(map_pdfium_error(code))
        } else {
            Ok(PdfDocument {
                funcs: &self.funcs,
                handle,
            })
        }
    }
}

impl Drop for PdfiumRuntime {
    fn drop(&mut self) {
        if self.initialized {
            // SAFETY: paired with FPDF_InitLibrary above and serialized by PDFIUM_LOCK.
            unsafe { (self.funcs.destroy_library)() };
        }
    }
}

struct PdfDocument<'a> {
    funcs: &'a PdfiumFunctions,
    handle: FpdfDocument,
}

impl PdfDocument<'_> {
    fn page_count(&self) -> Result<u32, EthosError> {
        // SAFETY: handle is a live FPDF_DOCUMENT owned by self.
        let count = unsafe { (self.funcs.get_page_count)(self.handle) };
        if count <= 0 {
            return Err(EthosError::new(
                ErrorCode::CorruptPdf,
                "PDF has no readable pages",
            ));
        }
        u32::try_from(count).map_err(|_| EthosError::internal("page count overflow"))
    }

    fn load_page(&self, page_index: u32) -> Result<PdfPage<'_>, EthosError> {
        let index =
            c_int::try_from(page_index).map_err(|_| EthosError::internal("page overflow"))?;
        // SAFETY: handle is live and index has been bounded by the caller.
        let handle = unsafe { (self.funcs.load_page)(self.handle, index) };
        if handle.is_null() {
            // SAFETY: FPDF_GetLastError has no preconditions after a failed page load.
            let code = unsafe { (self.funcs.get_last_error)() };
            Err(map_pdfium_error(code))
        } else {
            Ok(PdfPage {
                funcs: self.funcs,
                handle,
            })
        }
    }
}

impl Drop for PdfDocument<'_> {
    fn drop(&mut self) {
        // SAFETY: handle is a live FPDF_DOCUMENT and is closed exactly once here.
        unsafe { (self.funcs.close_document)(self.handle) };
    }
}

struct PdfPage<'a> {
    funcs: &'a PdfiumFunctions,
    handle: FpdfPage,
}

impl PdfPage<'_> {
    fn width_pts(&self) -> f64 {
        // SAFETY: handle is a live FPDF_PAGE.
        unsafe { (self.funcs.get_page_width_f)(self.handle) as f64 }
    }

    fn height_pts(&self) -> f64 {
        // SAFETY: handle is a live FPDF_PAGE.
        unsafe { (self.funcs.get_page_height_f)(self.handle) as f64 }
    }

    fn rotation(&self) -> u16 {
        let Some(get_rotation) = self.funcs.page_get_rotation else {
            return 0;
        };
        // SAFETY: handle is a live FPDF_PAGE.
        match unsafe { get_rotation(self.handle) }.rem_euclid(4) {
            1 => 90,
            2 => 180,
            3 => 270,
            _ => 0,
        }
    }

    fn model_page(&self, original_page: u32) -> Result<Page, EthosError> {
        Ok(Page {
            id: page_id(original_page)?,
            index: original_page,
            width: quantize_coord(self.width_pts())?,
            height: quantize_coord(self.height_pts())?,
            rotation: self.rotation(),
        })
    }

    fn geometry_probe_page(&self, original_page: u32) -> Result<GeometryProbePage, EthosError> {
        let page = self.model_page(original_page)?;
        // SAFETY: handle is a live FPDF_PAGE. Text page is closed by PdfTextPage::drop.
        let text_handle = unsafe { (self.funcs.text_load_page)(self.handle) };
        if text_handle.is_null() {
            return Ok(GeometryProbePage {
                id: page.id,
                index: page.index,
                width: page.width,
                height: page.height,
                rotation: page.rotation,
                char_count: 0,
                symbols: self.funcs.geometry_probe_symbols(),
                chars: Vec::new(),
                runs: Vec::new(),
            });
        }
        let text_page = PdfTextPage {
            funcs: self.funcs,
            handle: text_handle,
        };
        text_page.geometry_probe(&page, self.height_pts())
    }

    fn extract_text_spans(
        &self,
        page: &Page,
        next_span: &mut u32,
        spans: &mut Vec<Span>,
    ) -> Result<(), EthosError> {
        // SAFETY: handle is a live FPDF_PAGE. Text page is closed by PdfTextPage::drop.
        let text_handle = unsafe { (self.funcs.text_load_page)(self.handle) };
        if text_handle.is_null() {
            return Ok(());
        }
        let text_page = PdfTextPage {
            funcs: self.funcs,
            handle: text_handle,
        };
        text_page.extract_runs(page, self.height_pts(), next_span, spans)
    }

    fn render_crop_raw(&self, page_index: u32, bbox: QRect) -> Result<RawCrop, EthosError> {
        let bitmap = RenderBitmap::render_page(
            self.funcs,
            self.handle,
            pixel_extent(self.width_pts())?,
            pixel_extent(self.height_pts())?,
        )?;
        let (x0, y0, width_px, height_px) = crop_window(bbox, bitmap.width_px, bitmap.height_px)?;
        let bytes = bitmap.crop_bytes(x0, y0, width_px, height_px)?;
        Ok(RawCrop {
            page_index,
            bbox,
            width_px,
            height_px,
            stride: width_px
                .checked_mul(4)
                .ok_or_else(|| EthosError::internal("crop stride overflow"))?,
            pixel_format: "bgra_8u",
            sha256: ethos_core::c14n::sha256_hex_bytes(&bytes),
            bytes,
        })
    }
}

impl Drop for PdfPage<'_> {
    fn drop(&mut self) {
        // SAFETY: handle is a live FPDF_PAGE and is closed exactly once here.
        unsafe { (self.funcs.close_page)(self.handle) };
    }
}

struct PdfTextPage<'a> {
    funcs: &'a PdfiumFunctions,
    handle: FpdfTextPage,
}

struct RenderBitmap<'a> {
    funcs: &'a PdfiumFunctions,
    handle: FpdfBitmap,
    width_px: u32,
    height_px: u32,
    stride: usize,
}

impl RenderBitmap<'_> {
    fn render_page(
        funcs: &PdfiumFunctions,
        page: FpdfPage,
        width_px: u32,
        height_px: u32,
    ) -> Result<RenderBitmap<'_>, EthosError> {
        let Some(bitmap_create) = funcs.bitmap_create else {
            return Err(EthosError::internal(
                "pdfium library is missing bitmap render symbols",
            ));
        };
        let Some(bitmap_fill_rect) = funcs.bitmap_fill_rect else {
            return Err(EthosError::internal(
                "pdfium library is missing bitmap render symbols",
            ));
        };
        let Some(render_page_bitmap) = funcs.render_page_bitmap else {
            return Err(EthosError::internal(
                "pdfium library is missing bitmap render symbols",
            ));
        };
        let width = c_int::try_from(width_px)
            .map_err(|_| EthosError::internal("render bitmap width overflow"))?;
        let height = c_int::try_from(height_px)
            .map_err(|_| EthosError::internal("render bitmap height overflow"))?;

        // SAFETY: width/height are positive bounded c_int values. Bitmap is destroyed by Drop.
        let handle = unsafe { bitmap_create(width, height, 1) };
        if handle.is_null() {
            return Err(EthosError::internal(
                "pdfium failed to allocate render bitmap",
            ));
        }
        let mut bitmap = RenderBitmap {
            funcs,
            handle,
            width_px,
            height_px,
            stride: 0,
        };
        // SAFETY: handle is a live bitmap. Fill with opaque white for deterministic background.
        unsafe { bitmap_fill_rect(bitmap.handle, 0, 0, width, height, 0xFFFF_FFFF) };
        // SAFETY: handle and page are live. Render uses no callbacks and writes into the bitmap.
        unsafe { render_page_bitmap(bitmap.handle, page, 0, 0, width, height, 0, 0) };
        bitmap.stride = bitmap.read_stride()?;
        Ok(bitmap)
    }

    fn read_stride(&self) -> Result<usize, EthosError> {
        let Some(bitmap_get_stride) = self.funcs.bitmap_get_stride else {
            return Err(EthosError::internal(
                "pdfium library is missing bitmap render symbols",
            ));
        };
        // SAFETY: handle is a live bitmap.
        let stride = unsafe { bitmap_get_stride(self.handle) };
        if stride <= 0 {
            return Err(EthosError::internal(
                "pdfium render bitmap has invalid stride",
            ));
        }
        usize::try_from(stride).map_err(|_| EthosError::internal("render bitmap stride overflow"))
    }

    fn crop_bytes(
        &self,
        x0: u32,
        y0: u32,
        width_px: u32,
        height_px: u32,
    ) -> Result<Vec<u8>, EthosError> {
        let Some(bitmap_get_buffer) = self.funcs.bitmap_get_buffer else {
            return Err(EthosError::internal(
                "pdfium library is missing bitmap render symbols",
            ));
        };
        // SAFETY: handle is a live bitmap.
        let ptr = unsafe { bitmap_get_buffer(self.handle) };
        if ptr.is_null() {
            return Err(EthosError::internal("pdfium render bitmap has null buffer"));
        }
        let full_len = self
            .stride
            .checked_mul(
                usize::try_from(self.height_px)
                    .map_err(|_| EthosError::internal("render bitmap height overflow"))?,
            )
            .ok_or_else(|| EthosError::internal("render bitmap buffer length overflow"))?;
        // SAFETY: PDFium owns a live bitmap buffer of stride * height bytes for this bitmap.
        let full = unsafe { slice::from_raw_parts(ptr.cast::<u8>(), full_len) };

        let x0 = usize::try_from(x0).map_err(|_| EthosError::internal("crop x overflow"))?;
        let y0 = usize::try_from(y0).map_err(|_| EthosError::internal("crop y overflow"))?;
        let width =
            usize::try_from(width_px).map_err(|_| EthosError::internal("crop width overflow"))?;
        let height =
            usize::try_from(height_px).map_err(|_| EthosError::internal("crop height overflow"))?;
        let row_bytes = width
            .checked_mul(4)
            .ok_or_else(|| EthosError::internal("crop row width overflow"))?;
        let mut out = Vec::with_capacity(
            row_bytes
                .checked_mul(height)
                .ok_or_else(|| EthosError::internal("crop buffer length overflow"))?,
        );
        for row in 0..height {
            let src_start = y0
                .checked_add(row)
                .and_then(|y| y.checked_mul(self.stride))
                .and_then(|base| base.checked_add(x0.checked_mul(4)?))
                .ok_or_else(|| EthosError::internal("crop source offset overflow"))?;
            let src_end = src_start
                .checked_add(row_bytes)
                .ok_or_else(|| EthosError::internal("crop source row overflow"))?;
            if src_end > full.len() {
                return Err(EthosError::internal(
                    "crop source row exceeds render bitmap",
                ));
            }
            out.extend_from_slice(&full[src_start..src_end]);
        }
        Ok(out)
    }
}

impl Drop for RenderBitmap<'_> {
    fn drop(&mut self) {
        if let Some(bitmap_destroy) = self.funcs.bitmap_destroy {
            // SAFETY: handle is a live FPDF_BITMAP and is destroyed exactly once here.
            unsafe { bitmap_destroy(self.handle) };
        }
    }
}

impl PdfTextPage<'_> {
    fn geometry_probe(
        &self,
        page: &Page,
        page_height_pts: f64,
    ) -> Result<GeometryProbePage, EthosError> {
        // SAFETY: handle is a live FPDF_TEXTPAGE.
        let count = unsafe { (self.funcs.text_count_chars)(self.handle) };
        if count < 0 {
            return Err(EthosError::new(
                ErrorCode::CorruptPdf,
                "PDF text page could not be read",
            ));
        }

        let mut chars = Vec::new();
        let mut run = GeometryRunBuilder::default();
        let mut runs = Vec::new();
        let mut next_run = 1u32;
        for index in 0..count {
            let record = self.geometry_probe_char(index, page_height_pts)?;
            match record.parser_action.as_str() {
                "include" => {
                    if run.has_style_change(&record.font_id, record.font_size_q, record.font_flags)
                    {
                        run.flush(self, page_height_pts, &mut next_run, &mut runs)?;
                    }
                    run.push(&record);
                }
                "skip_generated_hyphen" => {}
                _ => run.flush(self, page_height_pts, &mut next_run, &mut runs)?,
            }
            chars.push(record);
        }
        run.flush(self, page_height_pts, &mut next_run, &mut runs)?;

        Ok(GeometryProbePage {
            id: page.id.clone(),
            index: page.index,
            width: page.width,
            height: page.height,
            rotation: page.rotation,
            char_count: count,
            symbols: self.funcs.geometry_probe_symbols(),
            chars,
            runs,
        })
    }

    fn geometry_probe_char(
        &self,
        index: c_int,
        page_height_pts: f64,
    ) -> Result<GeometryProbeChar, EthosError> {
        // SAFETY: index is in range for this text page.
        let unicode = unsafe { (self.funcs.text_get_unicode)(self.handle, index) };
        let ch = char::from_u32(unicode);
        let parser_action = match ch {
            None => "break_invalid_unicode",
            Some(_) if self.is_generated_hyphen(index) => "skip_generated_hyphen",
            Some(ch) if should_break_text_run(ch) => "break_whitespace_or_control",
            Some(_) => "include",
        };

        let font_info = self.font_info(index);
        Ok(GeometryProbeChar {
            index,
            unicode,
            text: ch.map(|ch| ch.to_string()),
            parser_action: parser_action.to_string(),
            char_box: self.char_bbox(index, page_height_pts)?,
            loose_char_box: self.loose_char_bbox(index, page_height_pts)?,
            char_origin: self.char_origin(index, page_height_pts)?,
            font_id: font_info.font_id,
            font_flags: font_info.font_flags,
            font_size_q: self.font_size_q(index),
        })
    }

    fn extract_runs(
        &self,
        page: &Page,
        page_height_pts: f64,
        next_span: &mut u32,
        spans: &mut Vec<Span>,
    ) -> Result<(), EthosError> {
        // SAFETY: handle is a live FPDF_TEXTPAGE.
        let count = unsafe { (self.funcs.text_count_chars)(self.handle) };
        if count < 0 {
            // A PDFium text-page failure invalidates extraction for the whole document.
            // Treating it as image-only would hide a backend read failure behind OCR fallback.
            return Err(EthosError::new(
                ErrorCode::CorruptPdf,
                "PDF text page could not be read",
            ));
        }
        if count == 0 {
            return Ok(());
        }

        let mut run = SpanRun::default();
        for index in 0..count {
            // SAFETY: index is in 0..count for this text page.
            let codepoint = unsafe { (self.funcs.text_get_unicode)(self.handle, index) };
            let Some(ch) = char::from_u32(codepoint) else {
                run.flush(page, next_span, spans)?;
                continue;
            };
            if self.is_generated_hyphen(index) {
                continue;
            }
            if should_break_text_run(ch) {
                run.flush(page, next_span, spans)?;
                continue;
            }

            let Some(bbox) = self.char_bbox(index, page_height_pts)? else {
                run.flush(page, next_span, spans)?;
                continue;
            };
            let font_size_q = self.font_size_q(index);
            let font_info = self.font_info(index);
            if run.has_style_change(&font_info.font_id, font_size_q) {
                run.flush(page, next_span, spans)?;
            }
            let origin = self.char_origin(index, page_height_pts)?;
            run.push(ch, bbox, origin, font_info.font_id, font_size_q);
        }
        run.flush(page, next_span, spans)
    }

    fn char_bbox(&self, index: c_int, page_height_pts: f64) -> Result<Option<QRect>, EthosError> {
        let mut left = 0.0f64;
        let mut right = 0.0f64;
        let mut bottom = 0.0f64;
        let mut top = 0.0f64;
        // SAFETY: all pointers refer to initialized local f64 values and index is in range.
        let ok = unsafe {
            (self.funcs.text_get_char_box)(
                self.handle,
                index,
                &mut left,
                &mut right,
                &mut bottom,
                &mut top,
            )
        };
        if ok == 0 {
            return Ok(None);
        }
        Ok(Some(qrect_from_pdfium_char_box(
            page_height_pts,
            left,
            right,
            bottom,
            top,
        )?))
    }

    fn loose_char_bbox(
        &self,
        index: c_int,
        page_height_pts: f64,
    ) -> Result<Option<QRect>, EthosError> {
        let Some(get_loose_char_box) = self.funcs.text_get_loose_char_box else {
            return Ok(None);
        };
        let mut rect = FsRectF::default();
        // SAFETY: rect points to initialized writable storage and index is in range.
        let ok = unsafe { get_loose_char_box(self.handle, index, &mut rect) };
        if ok == 0 {
            return Ok(None);
        }
        Ok(Some(qrect_from_pdfium_char_box(
            page_height_pts,
            f64::from(rect.left),
            f64::from(rect.right),
            f64::from(rect.bottom),
            f64::from(rect.top),
        )?))
    }

    fn char_origin(
        &self,
        index: c_int,
        page_height_pts: f64,
    ) -> Result<Option<[i64; 2]>, EthosError> {
        let Some(get_char_origin) = self.funcs.text_get_char_origin else {
            return Ok(None);
        };
        let mut x = 0.0f64;
        let mut y = 0.0f64;
        // SAFETY: pointers refer to initialized writable f64 values and index is in range.
        let ok = unsafe { get_char_origin(self.handle, index, &mut x, &mut y) };
        if ok == 0 {
            return Ok(None);
        }
        Ok(Some([
            quantize_coord(x)?,
            quantize_coord(page_height_pts - y)?,
        ]))
    }

    fn text_rects(
        &self,
        char_start: c_int,
        char_count: c_int,
        page_height_pts: f64,
    ) -> Result<Vec<QRect>, EthosError> {
        let (Some(count_rects), Some(get_rect)) =
            (self.funcs.text_count_rects, self.funcs.text_get_rect)
        else {
            return Ok(Vec::new());
        };
        if char_count <= 0 {
            return Ok(Vec::new());
        }
        // SAFETY: char_start/char_count identify a range observed from this text page.
        let rect_count = unsafe { count_rects(self.handle, char_start, char_count) };
        if rect_count <= 0 {
            return Ok(Vec::new());
        }
        let mut rects = Vec::new();
        for rect_index in 0..rect_count {
            let mut left = 0.0f64;
            let mut top = 0.0f64;
            let mut right = 0.0f64;
            let mut bottom = 0.0f64;
            // SAFETY: pointers refer to initialized writable f64 values.
            let ok = unsafe {
                get_rect(
                    self.handle,
                    rect_index,
                    &mut left,
                    &mut top,
                    &mut right,
                    &mut bottom,
                )
            };
            if ok != 0 {
                rects.push(qrect_from_pdfium_char_box(
                    page_height_pts,
                    left,
                    right,
                    bottom,
                    top,
                )?);
            }
        }
        Ok(rects)
    }

    fn font_size_q(&self, index: c_int) -> Option<i64> {
        // SAFETY: index is in range.
        let size = unsafe { (self.funcs.text_get_font_size)(self.handle, index) };
        if size <= 0.0 {
            return None;
        }
        quantize(size, QUANTUM_PER_POINT).ok()
    }

    fn font_info(&self, index: c_int) -> PdfFontInfo {
        let Some(get_font_info) = self.funcs.text_get_font_info else {
            return PdfFontInfo::default();
        };
        // SAFETY: index is in range; null buffer asks PDFium for the UTF-8 byte length.
        let len =
            unsafe { (get_font_info)(self.handle, index, ptr::null_mut(), 0, ptr::null_mut()) };
        if len == 0 || len > 4096 {
            return PdfFontInfo::default();
        }

        let Ok(len_usize) = usize::try_from(len) else {
            return PdfFontInfo::default();
        };
        let mut buffer = vec![0u8; len_usize];
        let mut flags = 0;
        // SAFETY: buffer is writable for len bytes; flags points to initialized storage.
        let written = unsafe {
            (get_font_info)(
                self.handle,
                index,
                buffer.as_mut_ptr().cast(),
                len,
                &mut flags,
            )
        };
        if written == 0 || written > len {
            return PdfFontInfo::default();
        }
        let nul = buffer.iter().position(|b| *b == 0).unwrap_or(buffer.len());
        let raw = std::str::from_utf8(&buffer[..nul]).ok();
        PdfFontInfo {
            font_id: raw.and_then(deterministic_font_id),
            font_flags: u32::try_from(flags).ok(),
        }
    }

    fn is_generated_hyphen(&self, index: c_int) -> bool {
        let (Some(text_is_generated), Some(text_is_hyphen)) =
            (self.funcs.text_is_generated, self.funcs.text_is_hyphen)
        else {
            return false;
        };
        // SAFETY: index is in range for this text page.
        unsafe {
            text_is_generated(self.handle, index) == 1 && text_is_hyphen(self.handle, index) == 1
        }
    }
}

impl Drop for PdfTextPage<'_> {
    fn drop(&mut self) {
        // SAFETY: handle is a live FPDF_TEXTPAGE and is closed exactly once here.
        unsafe { (self.funcs.text_close_page)(self.handle) };
    }
}

fn should_break_text_run(ch: char) -> bool {
    ch == '\0' || ch.is_whitespace() || ch.is_control()
}

#[derive(Default)]
struct SpanRun {
    text: String,
    bbox: Option<QRect>,
    first_origin: Option<[i64; 2]>,
    last_origin: Option<[i64; 2]>,
    font_id: Option<String>,
    font_size_q: Option<i64>,
}

#[derive(Default)]
struct GeometryRunBuilder {
    text: String,
    char_indices: Vec<i32>,
    char_box_union: Option<QRect>,
    loose_char_box_union: Option<QRect>,
    first_origin: Option<[i64; 2]>,
    last_origin: Option<[i64; 2]>,
    font_id: Option<String>,
    font_size_q: Option<i64>,
    font_flags: Option<u32>,
}

#[derive(Default)]
struct PdfFontInfo {
    font_id: Option<String>,
    font_flags: Option<u32>,
}

#[derive(Debug, Deserialize)]
struct FontSubstitutionTable {
    schema_version: String,
    table_id: String,
    version: String,
    default_unresolved_font_id: String,
    mappings: Vec<FontSubstitutionMapping>,
}

#[derive(Debug, Deserialize)]
struct FontSubstitutionMapping {
    source: String,
    font_id: String,
}

impl SpanRun {
    fn has_style_change(&self, font_id: &Option<String>, font_size_q: Option<i64>) -> bool {
        !self.text.is_empty() && (self.font_id != *font_id || self.font_size_q != font_size_q)
    }

    fn push(
        &mut self,
        ch: char,
        bbox: QRect,
        origin: Option<[i64; 2]>,
        font_id: Option<String>,
        font_size_q: Option<i64>,
    ) {
        self.text.push(ch);
        self.bbox = Some(match self.bbox {
            Some(existing) => union_rect(existing, bbox),
            None => bbox,
        });
        if self.first_origin.is_none() {
            self.first_origin = origin;
        }
        self.last_origin = origin;
        if self.font_id.is_none() {
            self.font_id = font_id;
        }
        if self.font_size_q.is_none() {
            self.font_size_q = font_size_q;
        }
    }

    fn flush(
        &mut self,
        page: &Page,
        next_span: &mut u32,
        spans: &mut Vec<Span>,
    ) -> Result<(), EthosError> {
        if self.text.is_empty() {
            return Ok(());
        }
        let bbox = self
            .bbox
            .ok_or_else(|| EthosError::internal("span run has text without bbox"))?;
        let origin_locator = match (self.first_origin.take(), self.last_origin.take()) {
            (Some(first_origin), Some(last_origin)) => Some(SpanOriginLocator {
                policy: ORIGIN_LOCATOR_POLICY.to_string(),
                first_origin,
                last_origin,
            }),
            _ => None,
        };
        spans.push(Span {
            id: span_id(*next_span)?,
            page: page.id.clone(),
            bbox,
            origin_locator,
            text: std::mem::take(&mut self.text),
            font_id: self.font_id.take(),
            font_size_q: self.font_size_q,
            char_start: None,
            char_end: None,
            warning_refs: Vec::new(),
        });
        *next_span += 1;
        self.bbox = None;
        self.first_origin = None;
        self.last_origin = None;
        self.font_id = None;
        self.font_size_q = None;
        Ok(())
    }
}

impl GeometryRunBuilder {
    fn has_style_change(
        &self,
        font_id: &Option<String>,
        font_size_q: Option<i64>,
        font_flags: Option<u32>,
    ) -> bool {
        !self.text.is_empty()
            && (self.font_id != *font_id
                || self.font_size_q != font_size_q
                || self.font_flags != font_flags)
    }

    fn push(&mut self, ch: &GeometryProbeChar) {
        if let Some(text) = &ch.text {
            self.text.push_str(text);
        }
        self.char_indices.push(ch.index);
        self.char_box_union = union_option_rect(self.char_box_union, ch.char_box);
        self.loose_char_box_union = union_option_rect(self.loose_char_box_union, ch.loose_char_box);
        if self.first_origin.is_none() {
            self.first_origin = ch.char_origin;
        }
        self.last_origin = ch.char_origin;
        if self.font_id.is_none() {
            self.font_id = ch.font_id.clone();
        }
        if self.font_size_q.is_none() {
            self.font_size_q = ch.font_size_q;
        }
        if self.font_flags.is_none() {
            self.font_flags = ch.font_flags;
        }
    }

    fn flush(
        &mut self,
        text_page: &PdfTextPage<'_>,
        page_height_pts: f64,
        next_run: &mut u32,
        runs: &mut Vec<GeometryProbeRun>,
    ) -> Result<(), EthosError> {
        if self.text.is_empty() {
            return Ok(());
        }
        let char_start = self.char_indices.first().copied().unwrap_or_default();
        let char_end = self
            .char_indices
            .last()
            .copied()
            .map(|index| index + 1)
            .unwrap_or(char_start);
        let text_rects =
            text_page.text_rects(char_start, char_end - char_start, page_height_pts)?;
        runs.push(GeometryProbeRun {
            index: *next_run,
            text: std::mem::take(&mut self.text),
            char_start,
            char_end,
            char_indices: std::mem::take(&mut self.char_indices),
            char_box_union: self.char_box_union.take(),
            loose_char_box_union: self.loose_char_box_union.take(),
            text_rect_union: union_rects(text_rects.iter().copied()),
            text_rects,
            first_origin: self.first_origin.take(),
            last_origin: self.last_origin.take(),
            font_id: self.font_id.take(),
            font_flags: self.font_flags.take(),
            font_size_q: self.font_size_q.take(),
        });
        *next_run += 1;
        self.font_size_q = None;
        self.font_flags = None;
        Ok(())
    }
}

fn union_option_rect(existing: Option<QRect>, next: Option<QRect>) -> Option<QRect> {
    match (existing, next) {
        (Some(a), Some(b)) => Some(union_rect(a, b)),
        (Some(a), None) => Some(a),
        (None, Some(b)) => Some(b),
        (None, None) => None,
    }
}

fn union_rects(mut rects: impl Iterator<Item = QRect>) -> Option<QRect> {
    let first = rects.next()?;
    Some(rects.fold(first, union_rect))
}

fn deterministic_font_id(raw_name: &str) -> Option<String> {
    let (name, subset) = strip_subset_prefix(raw_name.trim());
    let normalized = normalize_font_name(name)?;
    if subset {
        return Some(format!("embedded:{normalized}"));
    }
    font_substitution(&normalized)
        .or_else(|| Some(font_substitution_table().default_unresolved_font_id.clone()))
}

fn strip_subset_prefix(name: &str) -> (&str, bool) {
    let bytes = name.as_bytes();
    if bytes.len() > 7 && bytes[6] == b'+' && bytes[..6].iter().all(u8::is_ascii_uppercase) {
        (&name[7..], true)
    } else {
        (name, false)
    }
}

fn normalize_font_name(name: &str) -> Option<String> {
    let mut out = String::new();
    let mut previous_dash = false;
    for ch in name.trim().chars() {
        let mapped = if ch.is_ascii_alphanumeric() || matches!(ch, '-' | '_' | '.') {
            ch
        } else if ch.is_whitespace()
            || ch.is_control()
            || matches!(ch, '/' | '\\' | ':' | ',' | '(' | ')' | '[' | ']')
        {
            '-'
        } else {
            ch
        };
        if mapped == '-' {
            if previous_dash {
                continue;
            }
            previous_dash = true;
        } else {
            previous_dash = false;
        }
        out.push(mapped);
    }
    let out = out.trim_matches('-').to_string();
    (!out.is_empty()).then_some(out)
}

fn font_substitution(name: &str) -> Option<String> {
    font_substitution_table()
        .mappings
        .iter()
        .find(|mapping| mapping.source == name)
        .map(|mapping| mapping.font_id.clone())
}

fn font_substitution_table() -> &'static FontSubstitutionTable {
    FONT_SUBSTITUTION_TABLE.get_or_init(|| {
        let table: FontSubstitutionTable = serde_json::from_str(FONT_SUBSTITUTION_TABLE_JSON)
            .expect("bundled font-substitution-table.json is valid JSON");
        validate_font_substitution_table(&table)
            .expect("bundled font-substitution-table.json is internally valid");
        table
    })
}

fn validate_font_substitution_table(table: &FontSubstitutionTable) -> Result<(), &'static str> {
    if table.schema_version != "1.0.0"
        || table.table_id != "ethos-font-substitution-v1"
        || table.version != "1.0.0"
        || table.default_unresolved_font_id != "subst:liberation-sans-regular"
    {
        return Err("unexpected font substitution table metadata");
    }

    let mut seen = HashSet::new();
    for mapping in &table.mappings {
        if mapping.source.is_empty() || !mapping.font_id.starts_with("subst:") {
            return Err("malformed font substitution mapping");
        }
        if !seen.insert(mapping.source.as_str()) {
            return Err("duplicate font substitution mapping source");
        }
    }

    Ok(())
}

#[cfg(unix)]
mod dylib {
    use super::*;
    use std::os::unix::ffi::OsStrExt;

    const RTLD_NOW: c_int = 2;

    unsafe extern "C" {
        fn dlopen(filename: *const c_char, flag: c_int) -> *mut c_void;
        fn dlsym(handle: *mut c_void, symbol: *const c_char) -> *mut c_void;
        fn dlclose(handle: *mut c_void) -> c_int;
    }

    pub(super) struct Library {
        handle: *mut c_void,
    }

    impl Library {
        pub(super) fn open(path: &Path) -> Result<Self, EthosError> {
            let c_path = CString::new(path.as_os_str().as_bytes()).map_err(|_| {
                EthosError::internal("pdfium library path contains an interior NUL byte")
            })?;
            // SAFETY: c_path is NUL-terminated and lives for the call.
            let handle = unsafe { dlopen(c_path.as_ptr(), RTLD_NOW) };
            if handle.is_null() {
                Err(EthosError::internal(
                    "failed to load configured pdfium library",
                ))
            } else {
                Ok(Library { handle })
            }
        }

        pub(super) unsafe fn symbol<T: Copy>(&self, name: &'static [u8]) -> Result<T, EthosError> {
            let ptr = self.symbol_ptr(name);
            if ptr.is_null() {
                return Err(EthosError::internal(format!(
                    "pdfium library is missing symbol {}",
                    symbol_name(name)
                )));
            }
            assert_symbol_pointer_size::<T>();
            // SAFETY: caller chooses T to match the named PDFium C symbol.
            Ok(unsafe { std::mem::transmute_copy::<*mut c_void, T>(&ptr) })
        }

        pub(super) unsafe fn optional_symbol<T: Copy>(&self, name: &'static [u8]) -> Option<T> {
            let ptr = self.symbol_ptr(name);
            if ptr.is_null() {
                None
            } else {
                assert_symbol_pointer_size::<T>();
                // SAFETY: caller chooses T to match the named PDFium C symbol.
                Some(unsafe { std::mem::transmute_copy::<*mut c_void, T>(&ptr) })
            }
        }

        fn symbol_ptr(&self, name: &'static [u8]) -> *mut c_void {
            // SAFETY: handle is live; name is a static NUL-terminated symbol name.
            unsafe { dlsym(self.handle, name.as_ptr().cast()) }
        }
    }

    impl Drop for Library {
        fn drop(&mut self) {
            if !self.handle.is_null() {
                // SAFETY: handle was returned by dlopen and is closed exactly once.
                unsafe {
                    let _ = dlclose(self.handle);
                }
            }
        }
    }
}

#[cfg(windows)]
mod dylib {
    use super::*;
    use std::os::windows::ffi::OsStrExt;

    unsafe extern "system" {
        fn LoadLibraryW(lp_lib_file_name: *const u16) -> *mut c_void;
        fn GetProcAddress(h_module: *mut c_void, lp_proc_name: *const c_char) -> *mut c_void;
        fn FreeLibrary(h_lib_module: *mut c_void) -> c_int;
    }

    pub(super) struct Library {
        handle: *mut c_void,
    }

    impl Library {
        pub(super) fn open(path: &Path) -> Result<Self, EthosError> {
            let mut wide_path: Vec<u16> = path.as_os_str().encode_wide().collect();
            if wide_path.contains(&0) {
                return Err(EthosError::internal(
                    "pdfium library path contains an interior NUL code unit",
                ));
            }
            wide_path.push(0);
            // SAFETY: wide_path is NUL-terminated and lives for the call.
            let handle = unsafe { LoadLibraryW(wide_path.as_ptr()) };
            if handle.is_null() {
                Err(EthosError::internal(
                    "failed to load configured pdfium library",
                ))
            } else {
                Ok(Library { handle })
            }
        }

        pub(super) unsafe fn symbol<T: Copy>(&self, name: &'static [u8]) -> Result<T, EthosError> {
            let ptr = self.symbol_ptr(name);
            if ptr.is_null() {
                return Err(EthosError::internal(format!(
                    "pdfium library is missing symbol {}",
                    symbol_name(name)
                )));
            }
            assert_symbol_pointer_size::<T>();
            // SAFETY: caller chooses T to match the named PDFium C symbol.
            Ok(unsafe { std::mem::transmute_copy::<*mut c_void, T>(&ptr) })
        }

        pub(super) unsafe fn optional_symbol<T: Copy>(&self, name: &'static [u8]) -> Option<T> {
            let ptr = self.symbol_ptr(name);
            if ptr.is_null() {
                None
            } else {
                assert_symbol_pointer_size::<T>();
                // SAFETY: caller chooses T to match the named PDFium C symbol.
                Some(unsafe { std::mem::transmute_copy::<*mut c_void, T>(&ptr) })
            }
        }

        fn symbol_ptr(&self, name: &'static [u8]) -> *mut c_void {
            // SAFETY: handle is live; name is a static NUL-terminated symbol name.
            unsafe { GetProcAddress(self.handle, name.as_ptr().cast()) }
        }
    }

    impl Drop for Library {
        fn drop(&mut self) {
            if !self.handle.is_null() {
                // SAFETY: handle was returned by LoadLibraryW and is closed exactly once.
                unsafe {
                    let _ = FreeLibrary(self.handle);
                }
            }
        }
    }
}

fn assert_symbol_pointer_size<T>() {
    const {
        assert!(
            std::mem::size_of::<T>() == std::mem::size_of::<*mut c_void>(),
            "pdfium symbol pointer size mismatch"
        );
    }
}

fn symbol_name(name: &'static [u8]) -> String {
    let name = name.strip_suffix(b"\0").unwrap_or(name);
    String::from_utf8_lossy(name).into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn invalid_pdf_fails_before_library_load() {
        let err = PdfiumBackend::default()
            .page_count(b"not a pdf")
            .unwrap_err();
        assert_eq!(err.code, ErrorCode::InvalidPdf);
    }

    #[test]
    fn text_run_breaks_on_pdfium_control_characters() {
        assert!(should_break_text_run('\0'));
        assert!(should_break_text_run('\n'));
        assert!(should_break_text_run('\u{0002}'));
        assert!(!should_break_text_run('-'));
        assert!(!should_break_text_run('A'));
    }

    #[test]
    fn missing_library_path_is_stable_error_for_pdf_input() {
        let backend = PdfiumBackend::default();
        if env::var_os(PDFIUM_LIBRARY_PATH_ENV).is_some() {
            return;
        }
        let err = backend.page_count(b"%PDF-1.7\n").unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        assert!(err.message.contains(PDFIUM_LIBRARY_PATH_ENV));
    }

    #[test]
    fn render_crop_raw_rejects_zero_page_before_library_load() {
        let err = PdfiumBackend::default()
            .render_crop_raw(b"%PDF-1.7\n", 0, QRect::new(0, 0, 100, 100).unwrap())
            .unwrap_err();
        assert_eq!(err.code, ErrorCode::PageLimitExceeded);
        assert_eq!(err.message, "page selection out of document range");
    }

    #[test]
    fn crop_window_uses_outward_quantized_pixel_bounds() {
        assert_eq!(
            crop_window(QRect::new(7392, 5482, 19378, 7226).unwrap(), 300, 144).unwrap(),
            (73, 54, 121, 19)
        );
        assert_eq!(
            crop_window(QRect::new(-50, -50, 30100, 14500).unwrap(), 300, 144).unwrap(),
            (0, 0, 300, 144)
        );

        let err = crop_window(QRect::new(100, 100, 101, 101).unwrap(), 1, 1).unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        assert_eq!(err.message, "crop bbox has no positive pixel extent");
    }

    #[test]
    fn render_crop_raw_is_deterministic_when_pdfium_is_configured() {
        let Some(path) = env::var_os(PDFIUM_LIBRARY_PATH_ENV).map(PathBuf::from) else {
            return;
        };
        if !path.is_file() {
            return;
        }

        let fixture = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../../fixtures/synthetic/simple-text/document.pdf");
        let pdf_bytes = std::fs::read(fixture).unwrap();
        let bbox = QRect::new(7392, 5482, 19378, 7226).unwrap();
        let backend = PdfiumBackend::default();

        let first = backend.render_crop_raw(&pdf_bytes, 1, bbox).unwrap();
        let second = backend.render_crop_raw(&pdf_bytes, 1, bbox).unwrap();

        assert_eq!(first, second);
        assert_eq!(first.page_index, 1);
        assert_eq!(first.bbox, bbox);
        assert_eq!(first.width_px, 121);
        assert_eq!(first.height_px, 19);
        assert_eq!(first.stride, first.width_px * 4);
        assert_eq!(first.pixel_format, "bgra_8u");
        assert_eq!(
            first.bytes.len(),
            usize::try_from(first.stride * first.height_px).unwrap()
        );
        assert_eq!(
            first.sha256,
            ethos_core::c14n::sha256_hex_bytes(&first.bytes)
        );
        assert!(first
            .bytes
            .chunks_exact(4)
            .any(|pixel| pixel != [255, 255, 255, 255]));
    }

    #[test]
    fn invalid_configured_library_path_does_not_leak_host_path() {
        let path = env::temp_dir().join("ethos-missing-libpdfium\nwith-control.dylib");
        let backend = PdfiumBackend::from_library_path(&path);
        let err = backend.page_count(b"%PDF-1.7\n").unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        assert_eq!(err.message, "pdfium library path does not point to a file");
        assert!(!err.message.contains(path.to_string_lossy().as_ref()));
    }

    #[test]
    fn explicit_manifest_hashes_library_bytes() {
        let path = env::temp_dir().join("ethos-test-libpdfium-hash.bin");
        std::fs::write(&path, b"pdfium bytes").unwrap();
        let backend = PdfiumBackend::from_library_path(&path).with_version("test-version");
        let manifest = backend.manifest();
        assert_eq!(manifest.id, "pdfium");
        assert_eq!(manifest.phase, 1);
        assert_eq!(manifest.version, "test-version");
        assert_eq!(
            manifest.platform_sha256,
            ethos_core::c14n::sha256_hex_bytes(b"pdfium bytes")
        );
        let _ = std::fs::remove_file(path);
    }

    #[test]
    fn phase1_pdfium_profile_is_pinned_and_v8_xfa_disabled() {
        let profile = pinned_pdfium_profile();
        assert_eq!(profile.id, "pdfium");
        assert_eq!(profile.phase, 1);
        assert_eq!(profile.version, "chromium/7881");
        assert_eq!(profile.upstream_version, "PDFium 151.0.7881.0");
        assert_eq!(profile.v8, "disabled");
        assert_eq!(profile.xfa, "disabled");
        assert_eq!(profile.distribution.source, "bblanchon/pdfium-binaries");
        assert_eq!(
            profile.distribution.attestation.sha256,
            "24dec7cd76acb81106a0c29b908cceceef8215b050f6ff6ffbf875465811ef60"
        );
        assert!(!profile.build_flags.pdf_enable_v8);
        assert!(!profile.build_flags.pdf_enable_xfa);
        assert!(profile.build_flags.pdf_is_standalone);

        let expected = [
            (
                "macos-arm64",
                "pdfium-mac-arm64.tgz",
                "52e94ca5aa8847934330daf3f8150c190682c5ca93831468794f8b90d4392e40",
                "lib/libpdfium.dylib",
                "1bc45b15466b34cef96641ce25c77a876e70010c6b114f909dda2f5325fc5bd7",
            ),
            (
                "linux-x64",
                "pdfium-linux-x64.tgz",
                "1470e21b8b4a3b4ad7f85684e2da11d94f3b69a86d81dee11b9b6709d927ac1d",
                "lib/libpdfium.so",
                "f728930966f503652b92acc89b9374a2eeca00ce42e26dccd3e4b5c5161b2d64",
            ),
            (
                "windows-x64",
                "pdfium-win-x64.tgz",
                "73cc0de638ac2095e7445bf56a38200a5b7c7ca0e9f4ba144598f2457377ac08",
                "bin/pdfium.dll",
                "79d4676b656cfb1abcea88f9ade3b4b0826c5200382db5f4ec72a636c598c118",
            ),
        ];
        for (platform, name, archive_sha256, runtime_path, runtime_sha256) in expected {
            assert_eq!(profile.platform_hashes[platform], archive_sha256);
            let artifact = &profile.platform_artifacts[platform];
            assert_eq!(artifact.name, name);
            assert!(!artifact.name.contains("-v8-"));
            assert!(!artifact.name.contains("xfa"));
            assert_eq!(artifact.runtime_library_path, runtime_path);
            assert_eq!(artifact.runtime_library_sha256, runtime_sha256);
        }
    }

    #[test]
    fn mismatched_pdfium_version_is_rejected_before_library_load() {
        if current_platform_key().is_none() {
            return;
        }
        let path = env::temp_dir().join("ethos-test-libpdfium-version-mismatch.bin");
        std::fs::write(&path, b"not the pinned pdfium library").unwrap();
        let backend = PdfiumBackend::from_library_path(&path).with_version("chromium/7869");
        let err = backend.page_count(b"%PDF-1.7\n").unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        assert_eq!(
            err.message,
            "pdfium version does not match pinned phase 1 profile"
        );
        let _ = std::fs::remove_file(path);
    }

    #[test]
    fn pinned_upstream_pdfium_version_alias_is_accepted() {
        if current_platform_key().is_none() {
            return;
        }
        let path = env::temp_dir().join("ethos-test-libpdfium-upstream-version.bin");
        std::fs::write(&path, b"not the pinned pdfium library").unwrap();
        let backend = PdfiumBackend::from_library_path(&path).with_version("PDFium 151.0.7881.0");
        let err = backend.page_count(b"%PDF-1.7\n").unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        assert_eq!(
            err.message,
            "pdfium library does not match pinned phase 1 profile"
        );
        let _ = std::fs::remove_file(path);
    }

    #[test]
    fn mismatched_pdfium_artifact_is_rejected_with_stable_error() {
        if current_platform_key().is_none() {
            return;
        }
        let library_path = env::temp_dir().join("ethos-test-libpdfium-artifact-mismatch.bin");
        let artifact_path = env::temp_dir().join("ethos-test-pdfium-artifact-mismatch.tgz");
        std::fs::write(&library_path, b"not the pinned pdfium library").unwrap();
        std::fs::write(&artifact_path, b"not the pinned pdfium artifact").unwrap();
        let backend = PdfiumBackend::from_library_path(&library_path)
            .with_version("chromium/7881")
            .with_artifact_path(&artifact_path);
        let err = backend.page_count(b"%PDF-1.7\n").unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        assert_eq!(
            err.message,
            "pdfium artifact does not match pinned phase 1 profile"
        );
        let _ = std::fs::remove_file(library_path);
        let _ = std::fs::remove_file(artifact_path);
    }

    #[test]
    fn mismatched_pdfium_library_is_rejected_before_dynamic_load() {
        if current_platform_key().is_none() {
            return;
        }
        let path = env::temp_dir().join("ethos-test-libpdfium-library-mismatch.bin");
        std::fs::write(&path, b"not the pinned pdfium library").unwrap();
        let backend = PdfiumBackend::from_library_path(&path).with_version("chromium/7881");
        let err = backend.page_count(b"%PDF-1.7\n").unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        assert_eq!(
            err.message,
            "pdfium library does not match pinned phase 1 profile"
        );
        let _ = std::fs::remove_file(path);
    }

    #[test]
    fn deterministic_font_ids_strip_subset_prefixes() {
        assert_eq!(
            deterministic_font_id("ABCDEF+MinionPro-Regular").as_deref(),
            Some("embedded:MinionPro-Regular")
        );
        assert_eq!(
            deterministic_font_id("Helvetica-Bold").as_deref(),
            Some("subst:liberation-sans-bold")
        );
        assert_eq!(
            deterministic_font_id("Helvetica").as_deref(),
            Some("subst:liberation-sans-regular")
        );
        assert_eq!(
            deterministic_font_id("Helvetica-Oblique").as_deref(),
            Some("subst:liberation-sans-italic")
        );
        assert_eq!(
            deterministic_font_id("Helvetica-BoldOblique").as_deref(),
            Some("subst:liberation-sans-bold-italic")
        );
        assert_eq!(
            deterministic_font_id("Courier").as_deref(),
            Some("subst:liberation-mono-regular")
        );
        assert_eq!(
            deterministic_font_id("Times-Roman").as_deref(),
            Some("subst:liberation-serif-regular")
        );
        assert_eq!(
            deterministic_font_id("Custom Font/Regular").as_deref(),
            Some("subst:liberation-sans-regular")
        );
        assert_eq!(deterministic_font_id("   "), None);
    }

    #[test]
    fn font_substitution_table_is_well_formed() {
        use std::collections::HashSet;

        let table = font_substitution_table();
        assert_eq!(table.schema_version, "1.0.0");
        assert_eq!(table.table_id, "ethos-font-substitution-v1");
        assert_eq!(table.version, "1.0.0");
        assert_eq!(
            table.default_unresolved_font_id,
            "subst:liberation-sans-regular"
        );

        let mut seen = HashSet::new();
        for mapping in &table.mappings {
            assert!(!mapping.source.is_empty());
            assert!(mapping.font_id.starts_with("subst:"));
            assert!(
                seen.insert(mapping.source.as_str()),
                "duplicate font substitution source {}",
                mapping.source
            );
        }
        assert_eq!(table.mappings.len(), 14);
    }

    #[test]
    fn profile_pins_font_substitution_table_bytes() {
        const FONT_SUBSTITUTION_TABLE_PATH: &str =
            "crates/ethos-pdf/assets/font-substitution-table.json";
        let profile: serde_json::Value = serde_json::from_str(include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../profiles/ethos-deterministic-v1.json"
        )))
        .unwrap();
        let pin = &profile["font_policy"]["substitution_table"];
        assert_eq!(pin["path"], FONT_SUBSTITUTION_TABLE_PATH);
        assert_eq!(
            pin["sha256"],
            ethos_core::c14n::sha256_hex_bytes(FONT_SUBSTITUTION_TABLE_JSON.as_bytes())
        );
    }
}
