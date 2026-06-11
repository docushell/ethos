//! # ethos-pdf — WS-ENGINE lane (Milestone A; this skeleton is the lane's starting point)
//!
//! The ONLY crate that will link PDFium (invariant 3). Everything crossing
//! [`EthosPdfBackend`] is already normalized + quantized (invariant 1: quantize-at-
//! extraction lives HERE, via [`ethos_core::geom::quantize`]); public schemas/APIs never
//! see PDFium types.
//!
//! WS-ENGINE fills this crate per plan §6.1:
//! - week 1: Phase 1 pinned `bblanchon/pdfium-binaries` (V8/XFA off, hashes →
//!   `docs/pdfium-profile.md` + profile artifact `backend` block);
//! - week 2: font-mapper override (ADR-0003): embedded → `assets/font-substitution-table.json`
//!   → bundled Liberation; system fonts disabled; deterministic `.notdef`;
//! - weeks 2–3: `QuantizedGeom` extraction with page-range filtering at this boundary;
//! - week 3: stable error codes on corrupt/encrypted/password/image-only + limits;
//! - weeks 3–4: sandbox/subprocess feasibility (build-out in Milestone D, PRD §6.3).
//!
//! Until the engine lands, [`PdfiumBackend`] returns stable `internal_error`s so the CLI
//! and harness have a real (if unhappy) code path, never a panic.

#![forbid(unsafe_code)] // re-evaluated by WS-ENGINE behind a reviewed FFI boundary module
#![warn(missing_docs)]

use ethos_core::config::ParseConfig;
use ethos_core::error::EthosError;
use ethos_core::traits::{BackendManifest, EthosPdfBackend, Extraction};

/// Placeholder backend — structural stand-in for the WS-ENGINE implementation.
#[derive(Debug, Default, Clone, Copy)]
pub struct PdfiumBackend;

/// Fixed message for the not-yet-implemented state (deterministic template).
const NOT_IMPLEMENTED: &str =
    "pdf backend not yet implemented (WS-ENGINE, Milestone A); see docs/pdfium-profile.md";

impl EthosPdfBackend for PdfiumBackend {
    fn manifest(&self) -> BackendManifest {
        BackendManifest {
            id: "pdfium".to_string(),
            phase: 1,
            version: "0.0.0-unpinned".to_string(),
            platform_sha256: "0".repeat(64),
        }
    }

    fn page_count(&self, _pdf_bytes: &[u8]) -> Result<u32, EthosError> {
        Err(EthosError::internal(NOT_IMPLEMENTED))
    }

    fn extract(&self, _pdf_bytes: &[u8], _config: &ParseConfig) -> Result<Extraction, EthosError> {
        Err(EthosError::internal(NOT_IMPLEMENTED))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ethos_core::error::ErrorCode;

    #[test]
    fn placeholder_fails_with_stable_code_never_panics() {
        let backend = PdfiumBackend;
        let err = backend.page_count(b"%PDF-1.7").unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        let err = backend
            .extract(b"%PDF-1.7", &ParseConfig::default())
            .unwrap_err();
        assert_eq!(err.code, ErrorCode::InternalError);
        assert_eq!(backend.manifest().id, "pdfium");
    }
}
