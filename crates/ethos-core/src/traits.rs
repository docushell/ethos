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

//! Crate boundaries (Milestone A skeleton): the backend trait (`EthosPdfBackend`) and the
//! layout trait. Invariant 3: only `ethos-pdf` implements the backend; public schemas and
//! APIs never expose PDFium types — everything crossing this boundary is already
//! normalized and quantized (invariant 1).

use serde::{Deserialize, Serialize};

use crate::config::ParseConfig;
use crate::error::EthosError;
use crate::model::{Element, Page, Region, Span, Warning};

/// Backend build identity — pinned into the deterministic profile (ADR-0002) and thereby
/// into every document fingerprint.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct BackendManifest {
    /// Backend id (`"pdfium"`).
    pub id: String,
    /// Distribution phase (1 = pinned bblanchon binaries, 2 = project-maintained builds).
    pub phase: u8,
    /// Backend version/release string.
    pub version: String,
    /// Per-platform artifact sha256 for the running platform.
    pub platform_sha256: String,
}

/// Extraction output: the normalized, quantized data that leaves the backend.
/// No raw `f64` geometry, no backend-native types (invariants 1 + 3).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Extraction {
    /// Pages in ascending original index (already filtered by page selection —
    /// filtering happens at the backend boundary, PRD §16).
    pub pages: Vec<Page>,
    /// Spans in normalized content-stream order, quantized.
    pub spans: Vec<Span>,
    /// Raw non-text regions (pre-classification), stable coordinates.
    pub regions: Vec<Region>,
    /// Warnings emitted during extraction (numbered later per contract §5).
    pub warnings: Vec<Warning>,
}

/// The sole PDF backend boundary. Implementations live in `ethos-pdf` only.
pub trait EthosPdfBackend {
    /// Build identity for the profile manifest.
    fn manifest(&self) -> BackendManifest;

    /// Page count after ingest validation (encryption/corruption checks happen here
    /// and fail with stable codes).
    fn page_count(&self, pdf_bytes: &[u8]) -> Result<u32, EthosError>;

    /// Extract pages/spans/regions under the given config. Page-range filtering is a
    /// backend responsibility (`config.pages`); geometry arrives quantized.
    fn extract(&self, pdf_bytes: &[u8], config: &ParseConfig) -> Result<Extraction, EthosError>;
}

/// Layout output: the element graph in reading order (Milestone B fills this in).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct LayoutOutput {
    /// Elements in reading order.
    pub elements: Vec<Element>,
    /// Layout-stage warnings.
    pub warnings: Vec<Warning>,
}

/// The layout boundary: consumes extraction (already quantized), produces the element
/// graph. Implementations live in `ethos-layout` (Milestone B, WS-LAYOUT).
pub trait LayoutEngine {
    /// Compute reading order, blocks, headings, lists.
    fn layout(&self, extraction: &Extraction) -> Result<LayoutOutput, EthosError>;
}
