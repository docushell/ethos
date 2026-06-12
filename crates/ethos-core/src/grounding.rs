//! The `GroundingSource` trait module (PRD §5.5) — the sole boundary between
//! `ethos-verify` and any parser, Ethos included.
//!
//! Design rules (invariant 4):
//! - This module depends on `serde` only — no canonical model, no backend types,
//!   no PDFium, nothing Ethos-parser-internal.
//! - Foreign adapters (e.g. `adapters/grounding/opendataloader-json`) implement
//!   [`GroundingSource`] over foreign output; missing capabilities become explicit
//!   `capability_limited` downgrades in verification reports, never silent approximation.
//!
//! Geometry here is integer quanta when the source declares a compatible coordinate
//! system; foreign sources that cannot provide that declare it via [`Capabilities`].

use serde::{Deserialize, Serialize};

/// Identity of the parser that produced the grounding data.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ParserIdentity {
    /// Parser name, e.g. `"ethos"` or `"opendataloader-pdf"`.
    pub name: String,
    /// Parser version string as reported by the parser.
    pub version: String,
    /// Adapter identifier when the data flows through a foreign-parser adapter.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub adapter: Option<String>,
    /// Adapter version, when applicable.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub adapter_version: Option<String>,
}

/// Coordinate origin declared by the grounding source.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum CoordinateOrigin {
    /// Origin at top-left, y grows downward (Ethos canonical).
    TopLeft,
    /// Origin at bottom-left, y grows upward (raw PDF space).
    BottomLeft,
    /// Unknown/undeclared — bbox checks are capability-limited.
    Unknown,
}

/// Capability declaration (PRD §5.5). Capability-driven downgrades are explicit:
/// whatever is `false`/`Unknown` here must surface as a `capability_limited` warning
/// in verification reports that needed it.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Capabilities {
    /// Source exposes text spans.
    pub spans: bool,
    /// Spans carry char offsets into their owning element text.
    pub char_offsets: bool,
    /// Source declares a document fingerprint.
    pub fingerprint: bool,
    /// Declared coordinate origin.
    pub coordinate_origin: CoordinateOrigin,
    /// Source can produce region crops (L2 evidence, Milestone D).
    pub crop_support: bool,
}

/// Page geometry as declared by the grounding source.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PageGeometry {
    /// Page id in the source's namespace (Ethos: `p0001`…).
    pub id: String,
    /// 1-based page index in the original document.
    pub index: u32,
    /// Page width in the source's declared units.
    pub width: i64,
    /// Page height in the source's declared units.
    pub height: i64,
    /// Normalized rotation in degrees (0/90/180/270).
    pub rotation: u16,
}

/// An addressable element exposed for evidence checks.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GroundingElement {
    /// Element id in the source's namespace.
    pub id: String,
    /// Owning page id.
    pub page: String,
    /// `[x0, y0, x1, y1]` in the source's declared units/origin.
    pub bbox: [i64; 4],
    /// Element kind, lowercased, source-defined (e.g. `"text_block"`, `"heading"`).
    pub kind: String,
    /// Text content when applicable.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text: Option<String>,
}

/// Optional span with char offsets (capability `spans` / `char_offsets`).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GroundingSpan {
    /// Span id in the source's namespace.
    pub id: String,
    /// Owning page id.
    pub page: String,
    /// `[x0, y0, x1, y1]` in the source's declared units/origin.
    pub bbox: [i64; 4],
    /// Span text.
    pub text: String,
    /// Owning element id, when ownership is known.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub element: Option<String>,
    /// Char offset range within the owning element's text.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub char_start: Option<u32>,
    /// Exclusive end offset.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub char_end: Option<u32>,
}

/// A table cell exposed for `table_cell` claims.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GroundingCell {
    /// 0-based row.
    pub row: u32,
    /// 0-based column.
    pub col: u32,
    /// Rows spanned (≥1).
    pub row_span: u32,
    /// Columns spanned (≥1).
    pub col_span: u32,
    /// Cell bbox.
    pub bbox: [i64; 4],
    /// Cell text.
    pub text: String,
}

/// A table exposed for `table_cell` claims.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GroundingTable {
    /// Table id in the source's namespace.
    pub id: String,
    /// Owning page id (first page for multi-page tables).
    pub page: String,
    /// Table bbox.
    pub bbox: [i64; 4],
    /// Cells; absence of a (row, col) means an empty/covered cell.
    pub cells: Vec<GroundingCell>,
}

/// Parser output as evidence: everything `ethos-verify` is allowed to know about a
/// document. Implementations must be deterministic — same underlying artifact, same
/// returned data, same order.
pub trait GroundingSource {
    /// Identity of the producing parser (+ adapter when foreign).
    fn parser(&self) -> ParserIdentity;
    /// Capability declaration; drives explicit verification downgrades.
    fn capabilities(&self) -> Capabilities;
    /// Document fingerprint when the source declares one (`sha256:…` for Ethos).
    fn fingerprint(&self) -> Option<String>;
    /// Page geometry, ascending page index.
    fn pages(&self) -> Vec<PageGeometry>;
    /// Elements in the source's canonical order.
    fn elements(&self) -> Vec<GroundingElement>;
    /// Spans, when capability `spans` is true. Default: none.
    fn spans(&self) -> Vec<GroundingSpan> {
        Vec::new()
    }
    /// Tables, when the source models them. Default: none (verification of
    /// `table_cell` claims downgrades accordingly).
    fn tables(&self) -> Vec<GroundingTable> {
        Vec::new()
    }
    /// Stable crop reference for an evidence region, when `crop_support` is true.
    /// The verify layer treats this as an opaque audit pointer; sources own how the
    /// referenced crop artifact is generated and stored.
    fn crop_ref(&self, _page: &str, _bbox: [i64; 4]) -> Option<String> {
        None
    }
    /// Element lookup by id. Default: linear scan over [`Self::elements`].
    fn element_by_id(&self, id: &str) -> Option<GroundingElement> {
        self.elements().into_iter().find(|e| e.id == id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    struct Tiny;
    impl GroundingSource for Tiny {
        fn parser(&self) -> ParserIdentity {
            ParserIdentity {
                name: "tiny".into(),
                version: "0.0.0".into(),
                adapter: None,
                adapter_version: None,
            }
        }
        fn capabilities(&self) -> Capabilities {
            Capabilities {
                spans: false,
                char_offsets: false,
                fingerprint: false,
                coordinate_origin: CoordinateOrigin::Unknown,
                crop_support: false,
            }
        }
        fn fingerprint(&self) -> Option<String> {
            None
        }
        fn pages(&self) -> Vec<PageGeometry> {
            vec![PageGeometry {
                id: "p1".into(),
                index: 1,
                width: 10,
                height: 10,
                rotation: 0,
            }]
        }
        fn elements(&self) -> Vec<GroundingElement> {
            vec![GroundingElement {
                id: "e1".into(),
                page: "p1".into(),
                bbox: [0, 0, 5, 5],
                kind: "text_block".into(),
                text: Some("hello".into()),
            }]
        }
    }

    #[test]
    fn defaults_are_safe() {
        let t = Tiny;
        assert!(t.spans().is_empty());
        assert!(t.tables().is_empty());
        assert_eq!(
            t.element_by_id("e1").unwrap().text.as_deref(),
            Some("hello")
        );
        assert!(t.element_by_id("nope").is_none());
        assert!(t.crop_ref("p1", [0, 0, 5, 5]).is_none());
    }
}
