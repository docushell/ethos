//! Parse configuration: page selection (`--pages 1-5,9`), resource limits, and the
//! effective-config hash subset (determinism contract §7).

use serde::{Deserialize, Serialize};

use crate::error::{ErrorCode, EthosError};

/// Canonical page selection. Page selection enters `config_sha256`: a different range is a
/// legitimately different canonical output.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub enum PageSelection {
    /// All pages (canonical form: the string `"all"`).
    #[default]
    All,
    /// Merged, sorted, 1-based inclusive ranges (canonical form: `[[lo, hi], …]`).
    Ranges(Vec<(u32, u32)>),
}

impl PageSelection {
    /// Parse `--pages` syntax: comma-separated 1-based pages or inclusive ranges,
    /// e.g. `1-5,9`. Overlapping/adjacent ranges merge; order normalizes ascending.
    ///
    /// Syntax and out-of-range failures are [`PageSelectionError`] — *usage* errors the
    /// CLI maps to exit code 2, deliberately distinct from the 10 stable parse-failure
    /// codes (those describe the document, not the invocation).
    pub fn parse(input: &str) -> Result<Self, PageSelectionError> {
        let trimmed = input.trim();
        if trimmed.is_empty() {
            return Err(PageSelectionError::new("empty page selection"));
        }
        if trimmed == "all" {
            return Ok(PageSelection::All);
        }
        let mut ranges: Vec<(u32, u32)> = Vec::new();
        for part in trimmed.split(',') {
            let part = part.trim();
            if part.is_empty() {
                return Err(PageSelectionError::new("empty segment in page selection"));
            }
            let (lo, hi) = match part.split_once('-') {
                Some((a, b)) => (parse_page_number(a)?, parse_page_number(b)?),
                None => {
                    let n = parse_page_number(part)?;
                    (n, n)
                }
            };
            if lo > hi {
                return Err(PageSelectionError::new(
                    "descending range in page selection",
                ));
            }
            ranges.push((lo, hi));
        }
        ranges.sort_unstable();
        let mut merged: Vec<(u32, u32)> = Vec::with_capacity(ranges.len());
        for (lo, hi) in ranges {
            match merged.last_mut() {
                Some((_, prev_hi)) if lo <= prev_hi.saturating_add(1) => {
                    *prev_hi = (*prev_hi).max(hi);
                }
                _ => merged.push((lo, hi)),
            }
        }
        Ok(PageSelection::Ranges(merged))
    }

    /// True when `page` (1-based) is selected.
    pub fn contains(&self, page: u32) -> bool {
        match self {
            PageSelection::All => true,
            PageSelection::Ranges(rs) => rs.iter().any(|&(lo, hi)| page >= lo && page <= hi),
        }
    }

    /// Highest selected page, when bounded.
    pub fn max_page(&self) -> Option<u32> {
        match self {
            PageSelection::All => None,
            PageSelection::Ranges(rs) => rs.last().map(|&(_, hi)| hi),
        }
    }

    /// Validate against the document's page count: out-of-range selection is a stable
    /// error (`page_limit_exceeded` is about limits; out-of-range selection is usage —
    /// PRD §16 wants a stable error on out-of-range, mapped here to `invalid` usage error).
    pub fn validate_against(&self, page_count: u32) -> Result<(), PageSelectionError> {
        if let Some(max) = self.max_page() {
            if max > page_count {
                return Err(PageSelectionError::new(
                    "page selection out of document range",
                ));
            }
        }
        Ok(())
    }

    /// Canonical JSON form for the config hash (contract §7):
    /// `"all"` or `[[lo, hi], …]`.
    #[cfg(feature = "full")]
    pub fn canonical_value(&self) -> serde_json::Value {
        match self {
            PageSelection::All => serde_json::Value::String("all".to_string()),
            PageSelection::Ranges(rs) => serde_json::Value::Array(
                rs.iter()
                    .map(|&(lo, hi)| {
                        serde_json::Value::Array(vec![
                            serde_json::Value::from(lo),
                            serde_json::Value::from(hi),
                        ])
                    })
                    .collect(),
            ),
        }
    }
}

/// Page-selection syntax/validation error — a *usage* error (CLI exit 2), distinct from
/// the stable parse-failure codes.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PageSelectionError {
    /// Deterministic message.
    pub message: String,
}

impl PageSelectionError {
    fn new(message: impl Into<String>) -> Self {
        PageSelectionError {
            message: message.into(),
        }
    }
}

impl core::fmt::Display for PageSelectionError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str(&self.message)
    }
}
impl std::error::Error for PageSelectionError {}

fn parse_page_number(s: &str) -> Result<u32, PageSelectionError> {
    let s = s.trim();
    if s.is_empty() || !s.bytes().all(|b| b.is_ascii_digit()) {
        return Err(PageSelectionError::new("malformed page number"));
    }
    let n: u32 = s
        .parse()
        .map_err(|_| PageSelectionError::new("page number out of range"))?;
    if n == 0 {
        return Err(PageSelectionError::new("pages are 1-based"));
    }
    Ok(n)
}

/// Resource limits (PRD §10 base requirements). Defaults are deliberately conservative.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Limits {
    /// Max input file size in bytes.
    pub max_file_bytes: u64,
    /// Max page count.
    pub max_pages: u32,
    /// Max wall-time per parse, milliseconds.
    pub max_parse_ms: u64,
}

impl Default for Limits {
    fn default() -> Self {
        Limits {
            max_file_bytes: 256 * 1024 * 1024,
            max_pages: 5000,
            max_parse_ms: 120_000,
        }
    }
}

/// Effective parse configuration.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ParseConfig {
    /// Page selection.
    pub pages: PageSelection,
    /// Resource limits.
    pub limits: Limits,
}

impl ParseConfig {
    /// The config-hash subset (contract §7): exactly the profile's `config_hash_inputs`
    /// (v1: `pages`), as a canonical JSON object.
    #[cfg(feature = "full")]
    pub fn config_hash_subset(&self) -> serde_json::Value {
        let mut map = serde_json::Map::new();
        map.insert("pages".to_string(), self.pages.canonical_value());
        serde_json::Value::Object(map)
    }

    /// `config_sha256` over c14n of the hash subset.
    #[cfg(feature = "full")]
    pub fn config_sha256(&self) -> Result<String, EthosError> {
        crate::c14n::sha256_hex(&self.config_hash_subset())
            .map_err(|e| EthosError::new(ErrorCode::InternalError, e.to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;

    #[test]
    fn parses_prd_syntax() {
        assert_eq!(
            PageSelection::parse("1-5,9").unwrap(),
            PageSelection::Ranges(vec![(1, 5), (9, 9)])
        );
        assert_eq!(PageSelection::parse("all").unwrap(), PageSelection::All);
        assert_eq!(
            PageSelection::parse("3").unwrap(),
            PageSelection::Ranges(vec![(3, 3)])
        );
        // merge: overlap and adjacency normalize to one canonical form
        assert_eq!(
            PageSelection::parse("4-6,1-3").unwrap(),
            PageSelection::Ranges(vec![(1, 6)])
        );
        assert_eq!(
            PageSelection::parse("2,1,3").unwrap(),
            PageSelection::Ranges(vec![(1, 3)])
        );
    }

    #[test]
    fn rejects_malformed() {
        for bad in ["", "0", "5-2", "1,,2", "a-b", "1-", "-3", "1.5"] {
            assert!(PageSelection::parse(bad).is_err(), "should reject {bad:?}");
        }
    }

    #[test]
    fn validates_document_range() {
        let s = PageSelection::parse("1-5,9").unwrap();
        assert!(s.validate_against(9).is_ok());
        assert!(s.validate_against(8).is_err());
        assert!(PageSelection::All.validate_against(1).is_ok());
    }

    #[test]
    fn canonical_value_and_hash_are_stable() {
        let s = PageSelection::parse("9,1-5").unwrap();
        assert_eq!(s.canonical_value().to_string(), "[[1,5],[9,9]]");
        let cfg = ParseConfig {
            pages: s,
            ..Default::default()
        };
        // equivalent input spellings hash identically
        let cfg2 = ParseConfig {
            pages: PageSelection::parse("1-3,4-5,9").unwrap(),
            ..Default::default()
        };
        assert_eq!(cfg.config_sha256().unwrap(), cfg2.config_sha256().unwrap());
        // and the default ("all") differs
        assert_ne!(
            cfg.config_sha256().unwrap(),
            ParseConfig::default().config_sha256().unwrap()
        );
    }

    proptest! {
        #[test]
        fn parse_is_idempotent_through_canonical_form(
            ranges in proptest::collection::vec((1u32..200, 0u32..20), 1..6)
        ) {
            // build an arbitrary syntax string, parse, render canonical, re-parse: fixed point
            let syntax = ranges.iter()
                .map(|&(lo, span)| if span == 0 { format!("{lo}") } else { format!("{lo}-{}", lo + span) })
                .collect::<Vec<_>>()
                .join(",");
            let parsed = PageSelection::parse(&syntax).unwrap();
            if let PageSelection::Ranges(rs) = &parsed {
                let rendered = rs.iter().map(|&(lo, hi)| if lo == hi { format!("{lo}") } else { format!("{lo}-{hi}") }).collect::<Vec<_>>().join(",");
                prop_assert_eq!(PageSelection::parse(&rendered).unwrap(), parsed);
            }
        }
    }
}
