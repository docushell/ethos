//! c14n v1 — the single canonical JSON serialization (determinism contract §2).
//! No other crate hand-rolls output JSON (invariant 2).
//!
//! Properties (tested below): UTF-8, no whitespace, keys sorted by code point,
//! minimal escaping, integers only (floats are a hard error), idempotent.

use serde_json::Value;
use sha2::{Digest, Sha256};

pub use crate::geom::MAX_SAFE_INT;

/// c14n failure: a float or out-of-range number in a canonical value.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct C14nError {
    /// Deterministic message.
    pub message: String,
}

impl core::fmt::Display for C14nError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.write_str(&self.message)
    }
}
impl std::error::Error for C14nError {}

fn err(message: &str) -> C14nError {
    C14nError {
        message: message.to_string(),
    }
}

/// Serialize a JSON value to canonical bytes.
///
/// Object keys are sorted **explicitly** at write time (String `Ord` = Unicode code
/// point order — exactly the contract sort). We deliberately do NOT rely on
/// `serde_json::Map`'s iteration order: Cargo feature unification means any crate in the
/// final graph enabling `serde_json/preserve_order` would silently switch the map to
/// insertion order — an instant fingerprint break. Explicit sorting makes c14n correct
/// under either map flavor. Duplicate keys cannot be represented in `Value` and thus
/// never reach c14n; our own model can never produce them.
pub fn c14n_bytes(value: &Value) -> Result<Vec<u8>, C14nError> {
    let mut out = Vec::with_capacity(256);
    write_value(value, &mut out)?;
    Ok(out)
}

fn write_value(value: &Value, out: &mut Vec<u8>) -> Result<(), C14nError> {
    match value {
        Value::Null => out.extend_from_slice(b"null"),
        Value::Bool(true) => out.extend_from_slice(b"true"),
        Value::Bool(false) => out.extend_from_slice(b"false"),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                // unsigned_abs: `i64::MIN.abs()` would overflow (panic in debug, wrap in
                // release and slip past the range check) — P2 reviewer finding.
                if i.unsigned_abs() > MAX_SAFE_INT as u64 {
                    return Err(err("integer exceeds 2^53-1 in canonical value"));
                }
                out.extend_from_slice(i.to_string().as_bytes());
            } else if let Some(u) = n.as_u64() {
                if u > MAX_SAFE_INT as u64 {
                    return Err(err("integer exceeds 2^53-1 in canonical value"));
                }
                out.extend_from_slice(u.to_string().as_bytes());
            } else {
                return Err(err("non-integer number in canonical value"));
            }
        }
        Value::String(s) => write_string(s, out),
        Value::Array(items) => {
            out.push(b'[');
            for (i, item) in items.iter().enumerate() {
                if i > 0 {
                    out.push(b',');
                }
                write_value(item, out)?;
            }
            out.push(b']');
        }
        Value::Object(map) => {
            out.push(b'{');
            // Explicit code-point sort — never trust the map's own iteration order
            // (see c14n_bytes docs: serde_json/preserve_order is an additive feature).
            let mut entries: Vec<(&String, &Value)> = map.iter().collect();
            entries.sort_unstable_by(|a, b| a.0.cmp(b.0));
            for (i, (k, v)) in entries.into_iter().enumerate() {
                if i > 0 {
                    out.push(b',');
                }
                write_string(k, out);
                out.push(b':');
                write_value(v, out)?;
            }
            out.push(b'}');
        }
    }
    Ok(())
}

fn write_string(s: &str, out: &mut Vec<u8>) {
    out.push(b'"');
    for c in s.chars() {
        match c {
            '"' => out.extend_from_slice(b"\\\""),
            '\\' => out.extend_from_slice(b"\\\\"),
            '\u{0008}' => out.extend_from_slice(b"\\b"),
            '\t' => out.extend_from_slice(b"\\t"),
            '\n' => out.extend_from_slice(b"\\n"),
            '\u{000C}' => out.extend_from_slice(b"\\f"),
            '\r' => out.extend_from_slice(b"\\r"),
            c if (c as u32) < 0x20 => {
                out.extend_from_slice(format!("\\u{:04x}", c as u32).as_bytes());
            }
            c => {
                let mut buf = [0u8; 4];
                out.extend_from_slice(c.encode_utf8(&mut buf).as_bytes());
            }
        }
    }
    out.push(b'"');
}

/// Lowercase hex sha256 over the c14n bytes of `value`.
pub fn sha256_hex(value: &Value) -> Result<String, C14nError> {
    let bytes = c14n_bytes(value)?;
    Ok(hex(&Sha256::digest(&bytes)))
}

/// Lowercase hex sha256 over raw bytes (e.g. source PDF bytes).
pub fn sha256_hex_bytes(bytes: &[u8]) -> String {
    hex(&Sha256::digest(bytes))
}

fn hex(digest: &[u8]) -> String {
    let mut s = String::with_capacity(digest.len() * 2);
    for b in digest {
        use core::fmt::Write as _;
        let _ = write!(s, "{b:02x}");
    }
    s
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;
    use serde_json::json;

    fn c14n_str(v: &Value) -> String {
        String::from_utf8(c14n_bytes(v).unwrap()).unwrap()
    }

    // --- contract test vectors (determinism contract §10; cross-checked vs Python ref) ---

    #[test]
    fn vector_v1_empty_object() {
        let v = json!({});
        assert_eq!(c14n_str(&v), "{}");
        assert_eq!(
            sha256_hex(&v).unwrap(),
            "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
        );
    }

    #[test]
    fn vector_v2_key_order() {
        let v = json!({"b": 2, "a": 1, "_": 0, "Z": -3});
        assert_eq!(c14n_str(&v), r#"{"Z":-3,"_":0,"a":1,"b":2}"#);
        assert_eq!(
            sha256_hex(&v).unwrap(),
            "9e8c5fa78b63297991b5b7b45bd334ccc61bd1058c5cd8ca6ee0451f78cd6cc1"
        );
    }

    #[test]
    fn vector_v3_strings_and_ints() {
        let v = json!({
            "text": "líne1\nl\"ine2\tend — \u{1F4A1}",
            "n_zero": 0, "n_neg": -42, "arr": [3, 1, 2], "flag": true, "nothing": null
        });
        assert_eq!(
            c14n_str(&v),
            "{\"arr\":[3,1,2],\"flag\":true,\"n_neg\":-42,\"n_zero\":0,\"nothing\":null,\"text\":\"líne1\\nl\\\"ine2\\tend — \u{1F4A1}\"}"
        );
        assert_eq!(
            sha256_hex(&v).unwrap(),
            "86b355efaa571cac1ddb71d422a9971e6042c55ec5369305cce095f2c181426e"
        );
    }

    #[test]
    fn vector_v3b_controls_and_backslash() {
        let v = json!({"bel": "\u{0007}", "backslash": "a\\b"});
        assert_eq!(
            c14n_str(&v),
            "{\"backslash\":\"a\\\\b\",\"bel\":\"\\u0007\"}"
        );
        assert_eq!(
            sha256_hex(&v).unwrap(),
            "a1cc2b96cfaf4e1d27ca13e7c2e56faadf76bd027d233fce5a57124e36ea6dfd"
        );
    }

    #[test]
    fn vector_v4_fingerprint_manifest() {
        // the fingerprint manifest of schemas/examples/document.example.json — its
        // embedded hashes are real, so this vector ties c14n, the example, and the
        // Python reference implementation together
        let v = json!({
            "config_sha256": "68cc61753d299917cc7773f069c18aca31c8ac68f43736a94cb57eee05144084",
            "payload_sha256": "ffbc011dd41764aaa3d1e4391cde435f9a1ed3c5d9bfbe64e897fc37f1a2547e",
            "profile_id": "ethos-deterministic-v1",
            "profile_sha256": "eaf73db8113d2138f9e806f13a5a33649f3e7b67b4a87489909c396565ad092a",
            "schema_version": "1.0.0",
            "source_fingerprint": "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"
        });
        assert_eq!(
            sha256_hex(&v).unwrap(),
            "575623b28349dda9fbc4746b305048ed1ac692a50365ac9bc6a21a7ceeba8755"
        );
    }

    #[test]
    fn profile_artifact_hash_is_pinned() {
        let raw = include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../profiles/ethos-deterministic-v1.json"
        ));
        let v: Value = serde_json::from_str(raw).unwrap();
        assert_eq!(
            sha256_hex(&v).unwrap(),
            "eaf73db8113d2138f9e806f13a5a33649f3e7b67b4a87489909c396565ad092a",
            "profile artifact changed without a version bump (contract §10)"
        );
    }

    #[test]
    fn floats_are_rejected() {
        assert!(c14n_bytes(&json!({"x": 1.5})).is_err());
        assert!(c14n_bytes(&json!([0.1])).is_err());
        // 2^53 boundary
        assert!(c14n_bytes(&json!(MAX_SAFE_INT)).is_ok());
        assert!(c14n_bytes(&json!(MAX_SAFE_INT + 1)).is_err());
        assert!(c14n_bytes(&json!(-MAX_SAFE_INT)).is_ok());
        assert!(c14n_bytes(&json!(-MAX_SAFE_INT - 1)).is_err());
    }

    #[test]
    fn i64_min_is_an_error_not_a_panic() {
        // regression (P2): i64::MIN.abs() overflows; unsigned_abs must catch it cleanly
        assert!(c14n_bytes(&json!(i64::MIN)).is_err());
        assert!(c14n_bytes(&json!({"n": i64::MIN})).is_err());
        assert!(c14n_bytes(&json!(u64::MAX)).is_err());
    }

    // --- property tests -----------------------------------------------------------

    fn arb_canonical_value() -> impl Strategy<Value = Value> {
        let leaf = prop_oneof![
            Just(Value::Null),
            any::<bool>().prop_map(Value::from),
            (-MAX_SAFE_INT..=MAX_SAFE_INT).prop_map(Value::from),
            "\\PC*".prop_map(Value::from),
        ];
        leaf.prop_recursive(4, 32, 8, |inner| {
            prop_oneof![
                proptest::collection::vec(inner.clone(), 0..6).prop_map(Value::Array),
                proptest::collection::btree_map("\\PC*", inner, 0..6)
                    .prop_map(|m| { Value::Object(m.into_iter().collect()) }),
            ]
        })
    }

    proptest! {
        /// c14n(parse(c14n(v))) == c14n(v) — the §11 idempotence gate.
        #[test]
        fn c14n_is_idempotent(v in arb_canonical_value()) {
            let once = c14n_bytes(&v).unwrap();
            let reparsed: Value = serde_json::from_slice(&once).unwrap();
            let twice = c14n_bytes(&reparsed).unwrap();
            prop_assert_eq!(once, twice);
        }

        /// c14n output is always valid JSON that parses back to an equal Value.
        #[test]
        fn c14n_round_trips_value(v in arb_canonical_value()) {
            let bytes = c14n_bytes(&v).unwrap();
            let reparsed: Value = serde_json::from_slice(&bytes).unwrap();
            prop_assert_eq!(v, reparsed);
        }

        /// Key order in output is byte-sorted (scan adjacent top-level keys).
        #[test]
        fn object_keys_sorted(m in proptest::collection::btree_map("[a-z]{1,8}", 0i64..100, 0..8)) {
            let v = Value::Object(m.into_iter().map(|(k, n)| (k, Value::from(n))).collect());
            let bytes = c14n_bytes(&v).unwrap();
            let reparsed: Value = serde_json::from_slice(&bytes).unwrap();
            if let Value::Object(map) = reparsed {
                let keys: Vec<_> = map.keys().cloned().collect();
                let mut sorted = keys.clone();
                sorted.sort();
                prop_assert_eq!(keys, sorted);
            }
        }
    }
}
