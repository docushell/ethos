//! Fingerprints (determinism contract §6). The composite document fingerprint binds
//! payload, source, config, and profile identity into one comparable value.

use serde_json::Value;

use crate::c14n;

/// Prefix a raw lowercase-hex sha256 as the contract fingerprint form.
pub fn fingerprint_form(hex: &str) -> String {
    format!("sha256:{hex}")
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
            payload_sha256: "ffbc011dd41764aaa3d1e4391cde435f9a1ed3c5d9bfbe64e897fc37f1a2547e"
                .into(),
            profile_id: "ethos-deterministic-v1".into(),
            profile_sha256: "73c4883acfbe32727b97d4ede0dce7e65c9053a8a98883545cb02a2fe0733a77"
                .into(),
            schema_version: "1.0.0".into(),
            source_fingerprint:
                "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef".into(),
        };
        assert_eq!(
            m.document_fingerprint().unwrap(),
            "sha256:ace86a9fd5f262ed22abb9dcfc7aa0b4eaea12d6f2de696272944f3d416fb194"
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
}
