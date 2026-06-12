//! Fingerprints (determinism contract §6). The composite document fingerprint binds
//! payload, source, config, and profile identity into one comparable value.

use serde_json::Value;

use crate::c14n;

/// Prefix a raw lowercase-hex sha256 as the contract fingerprint form.
pub fn fingerprint_form(hex: &str) -> String {
    format!("sha256:{hex}")
}

/// True when `value` is the public fingerprint wire form: `sha256:` plus
/// exactly 64 lowercase hexadecimal characters.
pub fn is_fingerprint_form(value: &str) -> bool {
    let Some(hex) = value.strip_prefix("sha256:") else {
        return false;
    };
    hex.len() == 64
        && hex
            .bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
}

/// `source.fingerprint`: sha256 over the original input bytes.
pub fn source_fingerprint(bytes: &[u8]) -> String {
    fingerprint_form(&c14n::sha256_hex_bytes(bytes))
}

/// Inputs to the composite document fingerprint — exactly the contract §6 manifest.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FingerprintManifest {
    /// sha256 of c14n(effective-config subset).
    pub config_sha256: String,
    /// sha256 of c14n(payload).
    pub payload_sha256: String,
    /// Deterministic profile id.
    pub profile_id: String,
    /// sha256 of c14n(profile artifact).
    pub profile_sha256: String,
    /// Document schema version.
    pub schema_version: String,
    /// `sha256:…` of the source bytes.
    pub source_fingerprint: String,
}

impl FingerprintManifest {
    /// The manifest as a canonical JSON object (c14n sorts the keys).
    pub fn to_value(&self) -> Value {
        let mut map = serde_json::Map::new();
        map.insert(
            "config_sha256".into(),
            Value::String(self.config_sha256.clone()),
        );
        map.insert(
            "payload_sha256".into(),
            Value::String(self.payload_sha256.clone()),
        );
        map.insert("profile_id".into(), Value::String(self.profile_id.clone()));
        map.insert(
            "profile_sha256".into(),
            Value::String(self.profile_sha256.clone()),
        );
        map.insert(
            "schema_version".into(),
            Value::String(self.schema_version.clone()),
        );
        map.insert(
            "source_fingerprint".into(),
            Value::String(self.source_fingerprint.clone()),
        );
        Value::Object(map)
    }

    /// The composite document fingerprint: `sha256:` + sha256(c14n(manifest)).
    pub fn document_fingerprint(&self) -> Result<String, c14n::C14nError> {
        Ok(fingerprint_form(&c14n::sha256_hex(&self.to_value())?))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn matches_contract_vector_v4() {
        // the example document's manifest (real hashes) — contract §10 V4
        let m = FingerprintManifest {
            config_sha256: "68cc61753d299917cc7773f069c18aca31c8ac68f43736a94cb57eee05144084"
                .into(),
            payload_sha256: "9a392e2e555770423214eb134d44b18b19cb496ee8145598cea9089afc78a074"
                .into(),
            profile_id: "ethos-deterministic-v1".into(),
            profile_sha256: "d6145b9210845db39ad592ea549788432b52a649778c9947f5b2d91173e38070"
                .into(),
            schema_version: "1.0.0".into(),
            source_fingerprint:
                "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef".into(),
        };
        assert_eq!(
            m.document_fingerprint().unwrap(),
            "sha256:adf86dcf40c0b4f14aca15108a78fc01051fb171b8638722b627904d4ecd6bf2"
        );
    }

    #[test]
    fn source_fingerprint_of_known_bytes() {
        // sha256("") is the canonical empty-input digest
        assert_eq!(
            source_fingerprint(b""),
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
    }

    #[test]
    fn fingerprint_form_validation_is_strict() {
        assert!(is_fingerprint_form(
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ));
        assert!(!is_fingerprint_form(
            "sha256:E3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ));
        assert!(!is_fingerprint_form(
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85"
        ));
        assert!(!is_fingerprint_form(
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ));
        assert!(!is_fingerprint_form(
            "sha256:g3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ));
    }
}
