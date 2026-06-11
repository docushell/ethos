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

use std::collections::HashSet;
use std::env;
use std::ffi::{c_char, c_int, c_ulong, c_void, CString};
use std::path::{Path, PathBuf};
use std::ptr;
use std::sync::{Mutex, OnceLock};

use ethos_core::codes::WarningCode;
use ethos_core::config::{PageSelection, ParseConfig};
use ethos_core::error::{ErrorCode, EthosError};
use ethos_core::geom::{quantize, QRect};
use ethos_core::ids::{page_id, span_id, warning_id};
use ethos_core::model::{Page, Span, Warning};
use ethos_core::traits::{BackendManifest, EthosPdfBackend, Extraction};
use serde::Deserialize;

/// Environment variable containing the exact PDFium dynamic library path.
pub const PDFIUM_LIBRARY_PATH_ENV: &str = "ETHOS_PDFIUM_LIBRARY_PATH";

/// Optional environment variable carrying the pinned PDFium release/version string.
pub const PDFIUM_VERSION_ENV: &str = "ETHOS_PDFIUM_VERSION";

/// Profile quantization: 100 quanta per PDF point.
const QUANTUM_PER_POINT: u32 = 100;

const FONT_SUBSTITUTION_TABLE_JSON: &str = include_str!("../assets/font-substitution-table.json");

/// PDFium has process-global library state; serialize init/load/destroy for now.
static PDFIUM_LOCK: Mutex<()> = Mutex::new(());
static FONT_SUBSTITUTION_TABLE: OnceLock<FontSubstitutionTable> = OnceLock::new();

/// PDFium backend implementation.
#[derive(Debug, Clone, Default)]
pub struct PdfiumBackend {
    library_path: Option<PathBuf>,
    version: Option<String>,
}

impl PdfiumBackend {
    /// Construct a backend using an explicit PDFium dynamic library path.
    pub fn from_library_path(path: impl Into<PathBuf>) -> Self {
        PdfiumBackend {
            library_path: Some(path.into()),
            version: None,
        }
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

    fn configured_version(&self) -> String {
        self.version
            .clone()
            .or_else(|| env::var(PDFIUM_VERSION_ENV).ok())
            .unwrap_or_else(|| "runtime-dynamic".to_string())
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

type FpdfDocument = *mut c_void;
type FpdfPage = *mut c_void;
type FpdfTextPage = *mut c_void;

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
type FpdfTextGetFontSize = unsafe extern "C" fn(FpdfTextPage, c_int) -> f64;
#[cfg(windows)]
type FpdfTextGetFontSize = unsafe extern "system" fn(FpdfTextPage, c_int) -> f64;
#[cfg(not(windows))]
type FpdfTextGetFontInfo =
    unsafe extern "C" fn(FpdfTextPage, c_int, *mut c_void, c_ulong, *mut c_int) -> c_ulong;
#[cfg(windows)]
type FpdfTextGetFontInfo =
    unsafe extern "system" fn(FpdfTextPage, c_int, *mut c_void, c_ulong, *mut c_int) -> c_ulong;

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
    text_get_font_size: FpdfTextGetFontSize,
    text_get_font_info: Option<FpdfTextGetFontInfo>,
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
                text_get_font_size: library.symbol(b"FPDFText_GetFontSize\0")?,
                text_get_font_info: library.optional_symbol(b"FPDFText_GetFontInfo\0"),
            })
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
            return Err(EthosError::internal(format!(
                "pdfium library path does not point to a file: {}",
                path.display()
            )));
        }

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

impl PdfTextPage<'_> {
    fn extract_runs(
        &self,
        page: &Page,
        page_height_pts: f64,
        next_span: &mut u32,
        spans: &mut Vec<Span>,
    ) -> Result<(), EthosError> {
        // SAFETY: handle is a live FPDF_TEXTPAGE.
        let count = unsafe { (self.funcs.text_count_chars)(self.handle) };
        if count <= 0 {
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
            if ch == '\0' {
                run.flush(page, next_span, spans)?;
                continue;
            }
            if ch.is_whitespace() {
                run.flush(page, next_span, spans)?;
                continue;
            }

            let Some(bbox) = self.char_bbox(index, page_height_pts)? else {
                run.flush(page, next_span, spans)?;
                continue;
            };
            let font_size_q = self.font_size_q(index);
            let font_id = self.font_id(index);
            if run.has_style_change(&font_id, font_size_q) {
                run.flush(page, next_span, spans)?;
            }
            run.push(ch, bbox, font_id, font_size_q);
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

    fn font_size_q(&self, index: c_int) -> Option<i64> {
        // SAFETY: index is in range.
        let size = unsafe { (self.funcs.text_get_font_size)(self.handle, index) };
        quantize(size, QUANTUM_PER_POINT).ok()
    }

    fn font_id(&self, index: c_int) -> Option<String> {
        let get_font_info = self.funcs.text_get_font_info?;
        // SAFETY: index is in range; null buffer asks PDFium for the UTF-8 byte length.
        let len =
            unsafe { (get_font_info)(self.handle, index, ptr::null_mut(), 0, ptr::null_mut()) };
        if len == 0 || len > 4096 {
            return None;
        }

        let mut buffer = vec![0u8; usize::try_from(len).ok()?];
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
            return None;
        }
        let nul = buffer.iter().position(|b| *b == 0).unwrap_or(buffer.len());
        let raw = std::str::from_utf8(&buffer[..nul]).ok()?;
        deterministic_font_id(raw)
    }
}

impl Drop for PdfTextPage<'_> {
    fn drop(&mut self) {
        // SAFETY: handle is a live FPDF_TEXTPAGE and is closed exactly once here.
        unsafe { (self.funcs.text_close_page)(self.handle) };
    }
}

#[derive(Default)]
struct SpanRun {
    text: String,
    bbox: Option<QRect>,
    font_id: Option<String>,
    font_size_q: Option<i64>,
}

#[derive(Debug, Deserialize)]
struct FontSubstitutionTable {
    schema_version: String,
    table_id: String,
    version: String,
    default_unresolved_prefix: String,
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

    fn push(&mut self, ch: char, bbox: QRect, font_id: Option<String>, font_size_q: Option<i64>) {
        self.text.push(ch);
        self.bbox = Some(match self.bbox {
            Some(existing) => union_rect(existing, bbox),
            None => bbox,
        });
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
        spans.push(Span {
            id: span_id(*next_span)?,
            page: page.id.clone(),
            bbox,
            text: std::mem::take(&mut self.text),
            font_id: self.font_id.take(),
            font_size_q: self.font_size_q,
            char_start: None,
            char_end: None,
            warning_refs: Vec::new(),
        });
        *next_span += 1;
        self.bbox = None;
        self.font_id = None;
        self.font_size_q = None;
        Ok(())
    }
}

fn deterministic_font_id(raw_name: &str) -> Option<String> {
    let (name, subset) = strip_subset_prefix(raw_name.trim());
    let normalized = normalize_font_name(name)?;
    if subset {
        return Some(format!("embedded:{normalized}"));
    }
    font_substitution(&normalized).or_else(|| {
        Some(format!(
            "{}{normalized}",
            font_substitution_table().default_unresolved_prefix
        ))
    })
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
            Some(ch)
        } else if ch.is_whitespace()
            || ch.is_control()
            || matches!(ch, '/' | '\\' | ':' | ',' | '(' | ')' | '[' | ']')
        {
            Some('-')
        } else {
            Some(ch)
        };
        let Some(mapped) = mapped else {
            continue;
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
        || table.default_unresolved_prefix != "source:"
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
    use std::ffi::CStr;
    use std::os::unix::ffi::OsStrExt;

    const RTLD_NOW: c_int = 2;

    unsafe extern "C" {
        fn dlopen(filename: *const c_char, flag: c_int) -> *mut c_void;
        fn dlsym(handle: *mut c_void, symbol: *const c_char) -> *mut c_void;
        fn dlclose(handle: *mut c_void) -> c_int;
        fn dlerror() -> *const c_char;
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
                Err(EthosError::internal(format!(
                    "failed to load pdfium library: {}",
                    dl_error()
                )))
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
            // SAFETY: caller chooses T to match the named PDFium C symbol.
            Ok(unsafe { std::mem::transmute_copy::<*mut c_void, T>(&ptr) })
        }

        pub(super) unsafe fn optional_symbol<T: Copy>(&self, name: &'static [u8]) -> Option<T> {
            let ptr = self.symbol_ptr(name);
            if ptr.is_null() {
                None
            } else {
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

    fn dl_error() -> String {
        // SAFETY: dlerror returns a thread-local C string or null.
        let ptr = unsafe { dlerror() };
        if ptr.is_null() {
            "unknown loader error".to_string()
        } else {
            // SAFETY: ptr is a NUL-terminated C string owned by the loader.
            unsafe { CStr::from_ptr(ptr) }
                .to_string_lossy()
                .into_owned()
        }
    }
}

#[cfg(windows)]
mod dylib {
    use super::*;

    unsafe extern "system" {
        fn LoadLibraryA(lp_lib_file_name: *const c_char) -> *mut c_void;
        fn GetProcAddress(h_module: *mut c_void, lp_proc_name: *const c_char) -> *mut c_void;
        fn FreeLibrary(h_lib_module: *mut c_void) -> c_int;
    }

    pub(super) struct Library {
        handle: *mut c_void,
    }

    impl Library {
        pub(super) fn open(path: &Path) -> Result<Self, EthosError> {
            let c_path = CString::new(path.to_string_lossy().as_bytes()).map_err(|_| {
                EthosError::internal("pdfium library path contains an interior NUL byte")
            })?;
            // SAFETY: c_path is NUL-terminated and lives for the call.
            let handle = unsafe { LoadLibraryA(c_path.as_ptr()) };
            if handle.is_null() {
                Err(EthosError::internal("failed to load pdfium library"))
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
            // SAFETY: caller chooses T to match the named PDFium C symbol.
            Ok(unsafe { std::mem::transmute_copy::<*mut c_void, T>(&ptr) })
        }

        pub(super) unsafe fn optional_symbol<T: Copy>(&self, name: &'static [u8]) -> Option<T> {
            let ptr = self.symbol_ptr(name);
            if ptr.is_null() {
                None
            } else {
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
                // SAFETY: handle was returned by LoadLibraryA and is closed exactly once.
                unsafe {
                    let _ = FreeLibrary(self.handle);
                }
            }
        }
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
    fn deterministic_font_ids_strip_subset_prefixes() {
        assert_eq!(
            deterministic_font_id("ABCDEF+MinionPro-Regular").as_deref(),
            Some("embedded:MinionPro-Regular")
        );
        assert_eq!(
            deterministic_font_id("Helvetica-Bold").as_deref(),
            Some("subst:liberation-sans")
        );
        assert_eq!(
            deterministic_font_id("Courier").as_deref(),
            Some("subst:liberation-mono")
        );
        assert_eq!(
            deterministic_font_id("Times-Roman").as_deref(),
            Some("subst:liberation-serif")
        );
        assert_eq!(
            deterministic_font_id("Custom Font/Regular").as_deref(),
            Some("source:Custom-Font-Regular")
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
        assert_eq!(table.default_unresolved_prefix, "source:");

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
