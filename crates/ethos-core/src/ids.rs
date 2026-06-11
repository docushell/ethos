//! Deterministic ID formatting/parsing (ids-v1, determinism contract §5).
//! IDs are functions of canonical order — never random, never time-based.

use crate::error::{ErrorCode, EthosError};

macro_rules! id_kind {
    ($fmt_fn:ident, $parse_fn:ident, $prefix:literal, $width:literal, $max:literal, $doc:literal) => {
        #[doc = $doc]
        ///
        /// Errors with `internal_error` on width overflow (resource limits bound real
        /// documents far below these widths).
        pub fn $fmt_fn(n: u32) -> Result<String, EthosError> {
            if !(1..=$max).contains(&n) {
                return Err(EthosError::new(
                    ErrorCode::InternalError,
                    concat!("id overflow: ", $prefix, " width ", $width),
                ));
            }
            Ok(format!(concat!($prefix, "{:0", $width, "}"), n))
        }

        /// Parse the 1-based ordinal out of an id; `None` when malformed.
        pub fn $parse_fn(id: &str) -> Option<u32> {
            let digits = id.strip_prefix($prefix)?;
            if digits.len() != $width || !digits.bytes().all(|b| b.is_ascii_digit()) {
                return None;
            }
            let n: u32 = digits.parse().ok()?;
            (1..=$max).contains(&n).then_some(n)
        }
    };
}

id_kind!(
    page_id,
    parse_page_id,
    "p",
    4,
    9999,
    "Format a page id (`p%04d`, 1-based original document index)."
);
id_kind!(
    element_id,
    parse_element_id,
    "e",
    6,
    999_999,
    "Format an element id (`e%06d`, reading order)."
);
id_kind!(
    span_id,
    parse_span_id,
    "s",
    6,
    999_999,
    "Format a span id (`s%06d`, content-stream order)."
);
id_kind!(
    table_id,
    parse_table_id,
    "t",
    4,
    9999,
    "Format a table id (`t%04d`, reading-order anchor)."
);
id_kind!(
    chunk_id,
    parse_chunk_id,
    "c",
    6,
    999_999,
    "Format a chunk id (`c%06d`, chunker emission order)."
);
id_kind!(
    region_id,
    parse_region_id,
    "r",
    4,
    9999,
    "Format a region id (`r%04d`, page/y/x/stream order)."
);
id_kind!(
    warning_id,
    parse_warning_id,
    "w",
    4,
    9999,
    "Format a warning id (`w%04d`, sorted emission — contract §5)."
);
id_kind!(
    finding_id,
    parse_finding_id,
    "f",
    4,
    9999,
    "Format a security finding id (`f%04d`)."
);
id_kind!(
    check_id,
    parse_check_id,
    "v",
    4,
    9999,
    "Format a verification check id (`v%04d`, input order)."
);

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;

    #[test]
    fn formats_match_contract() {
        assert_eq!(page_id(1).unwrap(), "p0001");
        assert_eq!(element_id(42).unwrap(), "e000042");
        assert_eq!(span_id(999_999).unwrap(), "s999999");
        assert_eq!(warning_id(7).unwrap(), "w0007");
        assert!(page_id(0).is_err());
        assert!(page_id(10_000).is_err());
        assert!(element_id(1_000_000).is_err());
    }

    #[test]
    fn parse_rejects_malformed() {
        assert_eq!(parse_page_id("p0001"), Some(1));
        assert_eq!(parse_page_id("p001"), None);
        assert_eq!(parse_page_id("p00001"), None);
        assert_eq!(parse_page_id("q0001"), None);
        assert_eq!(parse_page_id("p0000"), None);
        assert_eq!(parse_element_id("e000042"), Some(42));
        assert_eq!(parse_element_id("e00004x"), None);
    }

    proptest! {
        #[test]
        fn round_trip(n in 1u32..=9999) {
            prop_assert_eq!(parse_page_id(&page_id(n).unwrap()), Some(n));
            prop_assert_eq!(parse_table_id(&table_id(n).unwrap()), Some(n));
            prop_assert_eq!(parse_warning_id(&warning_id(n).unwrap()), Some(n));
        }
    }
}
