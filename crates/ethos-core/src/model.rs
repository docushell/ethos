//! Canonical document model (`urn:ethos:schema:document:1`). Field-for-field mirror of
//! the schema; serialization through these types + [`crate::c14n`] is the only way Ethos
//! emits the document artifact.

use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::codes::WarningCode;
use crate::error::{ErrorCode, EthosError};
use crate::geom::QRect;

/// Top-level document artifact (`ethos.json`).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Document {
    /// Contract schema version.
    pub schema_version: String,
    /// Producing parser.
    pub parser: ParserInfo,
    /// Deterministic profile identity.
    pub profile: ProfileRef,
    /// Source identity.
    pub source: SourceInfo,
    /// sha256 of c14n(effective-config subset).
    pub config_sha256: String,
    /// sha256 of c14n(stable payload projection).
    pub payload_sha256: String,
    /// Composite document fingerprint (`sha256:…`).
    pub fingerprint: String,
    /// The emitted payload; `payload_sha256` binds its stable projection.
    pub payload: Payload,
    /// Runtime-only diagnostics; excluded from canonical equality and all fingerprints.
    /// Omitted by default (`--diagnostics` opts in) so default outputs are byte-identical.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub diagnostics: Option<Value>,
}

/// Producing parser identity.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ParserInfo {
    /// Always `"ethos"`.
    pub name: String,
    /// Crate/workspace version.
    pub version: String,
}

/// Deterministic profile reference.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ProfileRef {
    /// e.g. `"ethos-deterministic-v1"`.
    pub id: String,
    /// sha256 of c14n(profile artifact).
    pub sha256: String,
}

/// Source identity.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SourceInfo {
    /// `sha256:…` over the input bytes.
    pub fingerprint: String,
    /// Input size in bytes.
    pub bytes: u64,
}

/// The emitted document payload.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Payload {
    /// Uniform coordinate system for every bbox.
    pub coordinate_system: CoordinateSystem,
    /// Pages, ascending original index.
    pub pages: Vec<Page>,
    /// Elements — array order IS reading order.
    pub elements: Vec<Element>,
    /// Spans, content-stream order.
    pub spans: Vec<Span>,
    /// Tables.
    pub tables: Vec<Table>,
    /// Chunks.
    pub chunks: Vec<Chunk>,
    /// Non-text regions with stable coordinates.
    pub regions: Vec<Region>,
    /// Security-class warnings (contract §8 code split).
    pub security_warnings: Vec<Warning>,
    /// Parser warnings.
    pub parser_warnings: Vec<Warning>,
}

/// Coordinate system declaration.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CoordinateSystem {
    /// Always `"top-left"`.
    pub origin: String,
    /// Always `"quantum"`.
    pub unit: String,
    /// Quanta per PDF point (profile: 100).
    pub quantum_per_point: u32,
}

/// A page.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Page {
    /// `p%04d` from the 1-based original index.
    pub id: String,
    /// 1-based index in the ORIGINAL document (page-filtered parses keep original indices).
    pub index: u32,
    /// Width in quanta.
    pub width: i64,
    /// Height in quanta.
    pub height: i64,
    /// Normalized rotation: 0/90/180/270.
    pub rotation: u16,
}

/// Element type enum (wire: snake_case).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ElementType {
    /// Paragraph-level text block.
    TextBlock,
    /// Heading.
    Heading,
    /// List container.
    List,
    /// List item.
    ListItem,
    /// Table anchor element (see `table_ref`).
    Table,
    /// Non-text region anchor (see `region_ref`).
    Region,
    /// Running header.
    Header,
    /// Running footer.
    Footer,
    /// Caption.
    Caption,
    /// Anything else.
    Other,
}

/// A layout element.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Element {
    /// `e%06d`, reading order.
    pub id: String,
    /// Element type.
    #[serde(rename = "type")]
    pub element_type: ElementType,
    /// Owning page id.
    pub page: String,
    /// Bounding box.
    pub bbox: QRect,
    /// Text, when applicable. Preserved exactly as extracted.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<String>,
    /// Heading level (1–9) for headings.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub heading_level: Option<u8>,
    /// Table reference for table anchors.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub table_ref: Option<String>,
    /// Region reference for region anchors.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub region_ref: Option<String>,
    /// Heuristic confidence, integer per-mille.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub confidence: Option<u16>,
    /// Owned spans.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub span_refs: Vec<String>,
    /// Attached warnings.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub warning_refs: Vec<String>,
}

/// An extracted text span.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Span {
    /// `s%06d`, content-stream order.
    pub id: String,
    /// Owning page id.
    pub page: String,
    /// Bounding box.
    pub bbox: QRect,
    /// Stable origin-derived locator used by the fingerprint projection.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub origin_locator: Option<SpanOriginLocator>,
    /// Span text, exactly as extracted.
    pub text: String,
    /// Deterministic font identity (ADR-0003): `embedded:…` or `subst:…`.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub font_id: Option<String>,
    /// Font size in quanta.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub font_size_q: Option<i64>,
    /// Char offset into the owning element's text.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub char_start: Option<u32>,
    /// Exclusive end offset.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub char_end: Option<u32>,
    /// Attached warnings.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub warning_refs: Vec<String>,
}

/// Origin-derived text locator that remains stable when PDFium bbox dimensions drift.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SpanOriginLocator {
    /// Locator policy id.
    pub policy: String,
    /// First included character origin in top-left quanta.
    pub first_origin: [i64; 2],
    /// Last included character origin in top-left quanta.
    pub last_origin: [i64; 2],
}

/// A table.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Table {
    /// `t%04d`.
    pub id: String,
    /// Owning pages.
    pub page_refs: Vec<String>,
    /// Bounding box.
    pub bbox: QRect,
    /// Row count.
    pub n_rows: u32,
    /// Column count.
    pub n_cols: u32,
    /// Leading header rows.
    pub header_rows: u32,
    /// Leading header columns.
    pub header_cols: u32,
    /// Cells.
    pub cells: Vec<Cell>,
    /// Structure confidence, per-mille.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub confidence: Option<u16>,
    /// Structure warnings.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub warning_refs: Vec<String>,
    /// Optional derived exports — deterministic functions of cells.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub exports: Option<TableExports>,
}

/// Optional derived table exports.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TableExports {
    /// CSV form.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub csv: Option<String>,
    /// Markdown form.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub markdown: Option<String>,
}

/// A table cell.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Cell {
    /// 0-based row.
    pub row: u32,
    /// 0-based column.
    pub col: u32,
    /// Rows spanned (≥1).
    pub row_span: u32,
    /// Columns spanned (≥1).
    pub col_span: u32,
    /// Bounding box.
    pub bbox: QRect,
    /// Cell text.
    pub text: String,
    /// Contributing spans.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub span_refs: Vec<String>,
    /// Contributing elements.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub element_refs: Vec<String>,
}

/// A RAG chunk.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Chunk {
    /// `c%06d`.
    pub id: String,
    /// Chunk text.
    pub text: String,
    /// Source elements (≥1).
    pub element_refs: Vec<String>,
    /// Source pages (≥1).
    pub page_refs: Vec<String>,
    /// Citation bboxes (≥1).
    pub bboxes: Vec<PageBox>,
    /// Token estimate with pinned estimator.
    pub token_estimate: TokenEstimate,
    /// Warnings inherited from source regions. Hidden/off-page/low-contrast content
    /// is NEVER in default chunks (PRD §14).
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub warning_refs: Vec<String>,
}

/// A page-anchored bbox (citation target).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PageBox {
    /// Page id.
    pub page: String,
    /// Bbox on that page.
    pub bbox: QRect,
}

/// Token estimate.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TokenEstimate {
    /// Estimated count.
    pub count: u32,
    /// Pinned estimator id (`name@version`).
    pub estimator: String,
    /// Explicit approximation flag.
    pub approximate: bool,
}

/// Non-text region kind. Base tier emits `unknown` unless deterministic gates are met.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RegionKind {
    /// Unclassified (base tier default).
    Unknown,
    /// Raster image.
    Image,
    /// Figure.
    Figure,
    /// Formula.
    Formula,
    /// Chart.
    Chart,
}

/// A non-text region with stable coordinates.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Region {
    /// `r%04d`.
    pub id: String,
    /// Owning page.
    pub page: String,
    /// Bounding box.
    pub bbox: QRect,
    /// Kind label.
    pub kind: RegionKind,
    /// Attached warnings.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub warning_refs: Vec<String>,
}

/// A stable, deterministic warning (fixed-template message).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Warning {
    /// `w%04d` (contract §5 numbering).
    pub id: String,
    /// Stable code.
    pub code: WarningCode,
    /// Fixed-template message — no timestamps, paths, or host data.
    pub message: String,
    /// Page attachment.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub page: Option<String>,
    /// Element attachment.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub element_ref: Option<String>,
    /// Span attachment.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub span_ref: Option<String>,
    /// Region attachment.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub region_ref: Option<String>,
}

impl ElementType {
    /// Stable wire string (matches the serde snake_case form).
    pub fn as_str(self) -> &'static str {
        match self {
            ElementType::TextBlock => "text_block",
            ElementType::Heading => "heading",
            ElementType::List => "list",
            ElementType::ListItem => "list_item",
            ElementType::Table => "table",
            ElementType::Region => "region",
            ElementType::Header => "header",
            ElementType::Footer => "footer",
            ElementType::Caption => "caption",
            ElementType::Other => "other",
        }
    }
}

fn grounding_element_from_element(e: &Element) -> crate::grounding::GroundingElement {
    crate::grounding::GroundingElement {
        id: e.id.clone(),
        page: e.page.clone(),
        bbox: e.bbox.to_array(),
        kind: e.element_type.as_str().to_string(),
        text: e.text.clone(),
    }
}

/// Ethos output is itself just another grounding source (PRD §1.5): the verify layer
/// sees Ethos through the same trait as any foreign parser.
impl crate::grounding::GroundingSource for Document {
    fn parser(&self) -> crate::grounding::ParserIdentity {
        crate::grounding::ParserIdentity {
            name: self.parser.name.clone(),
            version: self.parser.version.clone(),
            adapter: None,
            adapter_version: None,
        }
    }

    fn capabilities(&self) -> crate::grounding::Capabilities {
        crate::grounding::Capabilities {
            spans: true,
            char_offsets: true,
            tables: true,
            fingerprint: true,
            coordinate_origin: crate::grounding::CoordinateOrigin::TopLeft,
            // crop support arrives with ethos-render (Milestone C/D)
            crop_support: false,
        }
    }

    fn fingerprint(&self) -> Option<String> {
        Some(self.fingerprint.clone())
    }

    fn pages(&self) -> Vec<crate::grounding::PageGeometry> {
        self.payload
            .pages
            .iter()
            .map(|p| crate::grounding::PageGeometry {
                id: p.id.clone(),
                index: p.index,
                width: p.width,
                height: p.height,
                rotation: p.rotation,
            })
            .collect()
    }

    fn elements(&self) -> Vec<crate::grounding::GroundingElement> {
        self.payload
            .elements
            .iter()
            .map(grounding_element_from_element)
            .collect()
    }

    fn element_by_id(&self, id: &str) -> Option<crate::grounding::GroundingElement> {
        self.payload
            .elements
            .iter()
            .find(|e| e.id == id)
            .map(grounding_element_from_element)
    }

    fn spans(&self) -> Vec<crate::grounding::GroundingSpan> {
        self.payload
            .spans
            .iter()
            .map(|s| crate::grounding::GroundingSpan {
                id: s.id.clone(),
                page: s.page.clone(),
                bbox: s.bbox.to_array(),
                text: s.text.clone(),
                element: None,
                char_start: s.char_start,
                char_end: s.char_end,
            })
            .collect()
    }

    fn tables(&self) -> Vec<crate::grounding::GroundingTable> {
        self.payload
            .tables
            .iter()
            .map(|t| crate::grounding::GroundingTable {
                id: t.id.clone(),
                page: t.page_refs.first().cloned().unwrap_or_default(),
                bbox: t.bbox.to_array(),
                cells: t
                    .cells
                    .iter()
                    .map(|c| crate::grounding::GroundingCell {
                        row: c.row,
                        col: c.col,
                        row_span: c.row_span,
                        col_span: c.col_span,
                        bbox: c.bbox.to_array(),
                        text: c.text.clone(),
                    })
                    .collect(),
            })
            .collect()
    }
}

impl Document {
    /// c14n bytes of the emitted payload.
    pub fn payload_c14n(&self) -> Result<Vec<u8>, EthosError> {
        let value = serde_json::to_value(&self.payload)
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.to_string()))?;
        crate::c14n::c14n_bytes(&value)
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.message))
    }

    /// Stable c14n bytes of the payload projection used by fingerprints and G3.
    pub fn payload_fingerprint_c14n(&self) -> Result<Vec<u8>, EthosError> {
        let value = stable_payload_projection(&self.payload)?;
        crate::c14n::c14n_bytes(&value)
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.message))
    }

    /// Recompute `payload_sha256` from the stable payload projection.
    pub fn compute_payload_sha256(&self) -> Result<String, EthosError> {
        let value = stable_payload_projection(&self.payload)?;
        crate::c14n::sha256_hex(&value)
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.message))
    }

    /// Compute `payload_sha256` for an assembled payload before the envelope exists.
    pub fn compute_payload_sha256_for_payload(payload: &Payload) -> Result<String, EthosError> {
        let value = stable_payload_projection(payload)?;
        crate::c14n::sha256_hex(&value)
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.message))
    }

    /// Build the stable payload projection used by `payload_sha256`.
    pub fn payload_fingerprint_value(&self) -> Result<Value, EthosError> {
        stable_payload_projection(&self.payload)
    }

    /// Recompute the raw payload hash for diagnostics only.
    pub fn compute_raw_payload_sha256(&self) -> Result<String, EthosError> {
        let value = serde_json::to_value(&self.payload)
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.to_string()))?;
        crate::c14n::sha256_hex(&value)
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.message))
    }

    /// Recompute the composite fingerprint from embedded envelope fields.
    pub fn compute_fingerprint(&self) -> Result<String, EthosError> {
        let manifest = crate::fingerprint::FingerprintManifest {
            config_sha256: self.config_sha256.clone(),
            payload_sha256: self.compute_payload_sha256()?,
            profile_id: self.profile.id.clone(),
            profile_sha256: self.profile.sha256.clone(),
            schema_version: self.schema_version.clone(),
            source_fingerprint: self.source.fingerprint.clone(),
        };
        manifest
            .document_fingerprint()
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.message))
    }

    /// Verify internal hash consistency (used by `ethos fingerprint`):
    /// embedded `payload_sha256` and `fingerprint` match recomputation.
    pub fn verify_integrity(&self) -> Result<(), EthosError> {
        let payload = self.compute_payload_sha256()?;
        if payload != self.payload_sha256 {
            return Err(EthosError::new(
                ErrorCode::InternalError,
                "payload_sha256 mismatch: document was modified or produced non-canonically",
            ));
        }
        let fp = self.compute_fingerprint()?;
        if fp != self.fingerprint {
            return Err(EthosError::new(
                ErrorCode::InternalError,
                "fingerprint mismatch: envelope and payload disagree",
            ));
        }
        Ok(())
    }
}

fn stable_payload_projection(payload: &Payload) -> Result<Value, EthosError> {
    let mut value = serde_json::to_value(payload)
        .map_err(|e| EthosError::new(ErrorCode::InternalError, e.to_string()))?;
    remove_unstable_geometry(&mut value);
    Ok(value)
}

fn remove_unstable_geometry(value: &mut Value) {
    match value {
        Value::Object(map) => {
            map.remove("bbox");
            map.remove("bboxes");
            for child in map.values_mut() {
                remove_unstable_geometry(child);
            }
        }
        Value::Array(items) => {
            for child in items {
                remove_unstable_geometry(child);
            }
        }
        _ => {}
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn example() -> (&'static str, Document) {
        let raw = include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../schemas/examples/document.example.json"
        ));
        (
            raw,
            serde_json::from_str(raw).expect("example deserializes"),
        )
    }

    #[test]
    fn example_round_trips_at_value_level() {
        let (raw, doc) = example();
        let original: Value = serde_json::from_str(raw).unwrap();
        let reserialized = serde_json::to_value(&doc).unwrap();
        assert_eq!(
            original, reserialized,
            "model drops or reorders schema fields"
        );
    }

    #[test]
    fn example_hashes_are_self_consistent() {
        let (_, doc) = example();
        doc.verify_integrity()
            .expect("example hashes must be real (regenerated, not fake)");
    }

    #[test]
    fn reserialization_is_stable() {
        let (_, doc) = example();
        let a = doc.payload_c14n().unwrap();
        let b = doc.payload_c14n().unwrap();
        assert_eq!(a, b);
        // parse(serialize(doc)) == doc
        let v = serde_json::to_value(&doc).unwrap();
        let doc2: Document = serde_json::from_value(v).unwrap();
        assert_eq!(doc, doc2);
    }

    #[test]
    fn payload_hash_ignores_precise_bbox_geometry() {
        let (_, doc) = example();
        let mut shifted = doc.clone();
        shifted.payload.elements[0].bbox = QRect::new(1, 2, 3, 4).unwrap();
        shifted.payload.spans[0].bbox = QRect::new(5, 6, 7, 8).unwrap();
        shifted.payload.tables[0].bbox = QRect::new(9, 10, 11, 12).unwrap();
        shifted.payload.tables[0].cells[0].bbox = QRect::new(13, 14, 15, 16).unwrap();
        shifted.payload.chunks[0].bboxes[0].bbox = QRect::new(17, 18, 19, 20).unwrap();
        shifted.payload.regions[0].bbox = QRect::new(21, 22, 23, 24).unwrap();

        assert_eq!(
            doc.compute_payload_sha256().unwrap(),
            shifted.compute_payload_sha256().unwrap()
        );
    }

    #[test]
    fn payload_hash_binds_origin_locator() {
        let (_, doc) = example();
        let mut changed = doc.clone();
        changed.payload.spans[0].origin_locator = Some(SpanOriginLocator {
            policy: "origin-run-locator-v1".to_string(),
            first_origin: [7200, 7200],
            last_origin: [30480, 7200],
        });

        assert_ne!(
            doc.compute_payload_sha256().unwrap(),
            changed.compute_payload_sha256().unwrap()
        );
    }
}
