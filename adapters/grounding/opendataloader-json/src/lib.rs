//! # OpenDataLoader JSON grounding adapter (Milestone A stub)
//!
//! Proves that foreign parser output can enter the [`GroundingSource`] interface
//! (PRD §16 acceptance): maps parser identity, pages, elements, bbox, text, and
//! capabilities. This is **not** an ODL fork — ODL output is consumed as data from a
//! pinned upstream version (plan §6.5).
//!
//! ## Stub mapping assumptions (hardened against pinned real output in Milestone B)
//!
//! The stub reads a conservative subset:
//! `{"tool": {"name", "version"}, "pages": [{"number", "width", "height"}],
//!   "elements": [{"id"?, "page", "bbox": [x0,y0,x1,y1], "type"?, "text"?}]}`
//!
//! - Geometry: source floats (points) are scaled to **centipoints** (×100,
//!   half-away-from-zero) so units align with Ethos quanta. Origin is declared
//!   [`CoordinateOrigin::Unknown`] until the B-alpha pin verifies ODL's convention —
//!   capability-driven downgrade, never silent assumption.
//! - No spans, no char offsets, no fingerprint, no crops: declared `false`, which
//!   verification must surface as `capability_limited` (PRD §5.5).

#![forbid(unsafe_code)]
#![warn(missing_docs)]

use ethos_core::grounding::{
    Capabilities, CoordinateOrigin, GroundingElement, GroundingSource, PageGeometry, ParserIdentity,
};
use serde_json::Value;

/// Adapter version, reported in `ParserIdentity::adapter_version`.
pub const ADAPTER_VERSION: &str = "0.1.0";

/// Mapping failure: input is valid JSON but not recognizable ODL output.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AdapterError {
    /// Deterministic message.
    pub message: String,
}

impl core::fmt::Display for AdapterError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str(&self.message)
    }
}
impl std::error::Error for AdapterError {}

fn err(message: &str) -> AdapterError {
    AdapterError {
        message: message.to_string(),
    }
}

/// A parsed ODL JSON document exposed as a [`GroundingSource`].
#[derive(Debug, Clone)]
pub struct OdlJsonSource {
    parser_name: String,
    parser_version: String,
    pages: Vec<PageGeometry>,
    elements: Vec<GroundingElement>,
}

/// Scale points → centipoints, half-away-from-zero (kept local: this crate deliberately
/// cannot see `ethos-core::geom`, which is behind the `full` feature).
fn to_centipoints(v: f64) -> Option<i64> {
    if !v.is_finite() {
        return None;
    }
    let scaled = v * 100.0;
    let rounded = if scaled >= 0.0 {
        (scaled + 0.5).floor()
    } else {
        (scaled - 0.5).ceil()
    };
    if rounded.abs() > 9_007_199_254_740_991.0 {
        return None;
    }
    Some(rounded as i64)
}

fn bbox_from(value: &Value) -> Result<[i64; 4], AdapterError> {
    let arr = value
        .as_array()
        .ok_or_else(|| err("bbox is not an array"))?;
    if arr.len() != 4 {
        return Err(err("bbox must have 4 entries"));
    }
    let mut out = [0i64; 4];
    for (i, v) in arr.iter().enumerate() {
        let f = v
            .as_f64()
            .ok_or_else(|| err("bbox entry is not a number"))?;
        out[i] = to_centipoints(f).ok_or_else(|| err("bbox entry is not finite"))?;
    }
    if out[0] > out[2] || out[1] > out[3] {
        return Err(err("bbox is malformed (x0>x1 or y0>y1)"));
    }
    Ok(out)
}

impl OdlJsonSource {
    /// Build from ODL JSON text.
    pub fn from_json_str(json: &str) -> Result<Self, AdapterError> {
        let root: Value = serde_json::from_str(json).map_err(|_| err("input is not valid JSON"))?;
        Self::from_value(&root)
    }

    /// Build from a parsed JSON value.
    pub fn from_value(root: &Value) -> Result<Self, AdapterError> {
        let tool = root
            .get("tool")
            .ok_or_else(|| err("missing 'tool' object"))?;
        let parser_name = tool
            .get("name")
            .and_then(Value::as_str)
            .ok_or_else(|| err("missing tool.name"))?
            .to_string();
        let parser_version = tool
            .get("version")
            .and_then(Value::as_str)
            .ok_or_else(|| err("missing tool.version"))?
            .to_string();

        let mut pages = Vec::new();
        for page in root
            .get("pages")
            .and_then(Value::as_array)
            .ok_or_else(|| err("missing 'pages' array"))?
        {
            let number = page
                .get("number")
                .and_then(Value::as_u64)
                .ok_or_else(|| err("missing page.number"))? as u32;
            if number == 0 {
                return Err(err("page.number must be 1-based"));
            }
            let width = page.get("width").and_then(Value::as_f64).unwrap_or(0.0);
            let height = page.get("height").and_then(Value::as_f64).unwrap_or(0.0);
            pages.push(PageGeometry {
                id: format!("page-{number}"),
                index: number,
                width: to_centipoints(width).ok_or_else(|| err("page width not finite"))?,
                height: to_centipoints(height).ok_or_else(|| err("page height not finite"))?,
                rotation: 0,
            });
        }
        pages.sort_by_key(|p| p.index);

        let mut elements = Vec::new();
        for (i, el) in root
            .get("elements")
            .and_then(Value::as_array)
            .ok_or_else(|| err("missing 'elements' array"))?
            .iter()
            .enumerate()
        {
            let page_number = el
                .get("page")
                .and_then(Value::as_u64)
                .ok_or_else(|| err("missing element.page"))? as u32;
            let id = el
                .get("id")
                .and_then(Value::as_str)
                .map(str::to_string)
                .unwrap_or_else(|| format!("odl-el-{}", i + 1));
            let bbox = bbox_from(el.get("bbox").ok_or_else(|| err("missing element.bbox"))?)?;
            let kind = el
                .get("type")
                .and_then(Value::as_str)
                .unwrap_or("unknown")
                .to_ascii_lowercase();
            let text = el.get("text").and_then(Value::as_str).map(str::to_string);
            elements.push(GroundingElement {
                id,
                page: format!("page-{page_number}"),
                bbox,
                kind,
                text,
            });
        }

        Ok(OdlJsonSource {
            parser_name,
            parser_version,
            pages,
            elements,
        })
    }
}

impl GroundingSource for OdlJsonSource {
    fn parser(&self) -> ParserIdentity {
        ParserIdentity {
            name: self.parser_name.clone(),
            version: self.parser_version.clone(),
            adapter: Some("opendataloader-json".to_string()),
            adapter_version: Some(ADAPTER_VERSION.to_string()),
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
        self.pages.clone()
    }

    fn elements(&self) -> Vec<GroundingElement> {
        self.elements.clone()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = include_str!("../tests/fixtures/odl-sample.json");

    #[test]
    fn maps_the_documented_subset() {
        let src = OdlJsonSource::from_json_str(SAMPLE).unwrap();
        let id = src.parser();
        assert_eq!(id.name, "opendataloader-pdf");
        assert_eq!(id.adapter.as_deref(), Some("opendataloader-json"));

        let pages = src.pages();
        assert_eq!(pages.len(), 1);
        assert_eq!(pages[0].index, 1);
        assert_eq!(pages[0].width, 61200); // 612pt → centipoints

        let els = src.elements();
        assert_eq!(els.len(), 2);
        assert_eq!(els[0].kind, "heading");
        assert_eq!(els[0].text.as_deref(), Some("Quarterly Report"));
        assert_eq!(els[0].bbox, [7200, 7200, 30480, 9000]);

        let caps = src.capabilities();
        assert!(!caps.spans && !caps.fingerprint && !caps.crop_support);
        assert_eq!(caps.coordinate_origin, CoordinateOrigin::Unknown);
        assert!(src.fingerprint().is_none());
    }

    #[test]
    fn rejects_unrecognizable_input() {
        assert!(OdlJsonSource::from_json_str("not json").is_err());
        assert!(OdlJsonSource::from_json_str("{}").is_err());
        assert!(OdlJsonSource::from_json_str(r#"{"tool":{"name":"x","version":"1"},"pages":[],"elements":[{"page":1,"bbox":[5,5,1,1]}]}"#).is_err());
    }
}
