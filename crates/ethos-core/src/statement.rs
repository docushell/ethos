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

//! The in-toto Statement wrapper for Ethos output artifacts
//! (`docs/proof-statement-v1.md`).
//!
//! Ethos emits several distinct verdict artifacts. Wrapped in a Statement, each one says
//! what kind of result it is (`predicateType`) and which artifact it concerns (`subject`),
//! so a consumer no longer has to infer either from a filename.
//!
//! **This module is the only place a Statement is constructed.** No command hand-rolls the
//! shape, for the same reason `ethos-core` owns the single c14n implementation: a wire
//! format assembled independently in several places drifts, and the drift is invisible
//! until two producers disagree.
//!
//! Scope note: statements wrap *verdicts*. Representations — `document.ethos.json`,
//! `chunks.jsonl` — stay bare, because a document graph is not an assertion about the
//! document, it is the document re-expressed (`docs/proof-statement-v1.md` §1.5).

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

use crate::c14n::{c14n_bytes, C14nError};

/// in-toto Statement schema identifier, verified against the in-toto v1 spec.
pub const IN_TOTO_STATEMENT_V1: &str = "https://in-toto.io/Statement/v1";

/// Base URI for every Ethos `predicateType` (`docs/proof-statement-v1.md` §1.2).
///
/// Permanent. A URL rather than a bare string because the namespace is what stops one
/// producer's `grounding/v1` colliding with another's.
pub const PREDICATE_BASE: &str = "https://docushell.com/ethos";

/// Build a `predicateType` URI as `<base>/<predicate>/v<version>`.
///
/// `version` versions the **predicate schema**, never the product: `grounding/v1` stays
/// `v1` across Ethos 0.6, 0.7, and 1.0, and bumps only when the predicate's own shape
/// breaks.
///
/// ```
/// use ethos_core::statement::predicate_type;
/// assert_eq!(
///     predicate_type("grounding", 1),
///     "https://docushell.com/ethos/grounding/v1"
/// );
/// ```
pub fn predicate_type(predicate: &str, version: u32) -> String {
    format!("{PREDICATE_BASE}/{predicate}/v{version}")
}

/// An artifact a statement is about: a name plus one or more digests.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Subject {
    /// Human-facing identifier. Distinguishes entries; artifacts match on digest.
    pub name: String,
    /// Algorithm-to-hex-digest map. `BTreeMap` so key order is canonical without relying
    /// on serde field order.
    pub digest: BTreeMap<String, String>,
}

impl Subject {
    /// A subject identified by a SHA-256 digest.
    ///
    /// `sha256` is bare lowercase hex with no `sha256:` prefix — in-toto puts the
    /// algorithm in the map key, so repeating it in the value would double-encode it.
    pub fn sha256(name: impl Into<String>, sha256: impl Into<String>) -> Self {
        let mut digest = BTreeMap::new();
        digest.insert("sha256".to_string(), sha256.into());
        Self {
            name: name.into(),
            digest,
        }
    }
}

/// An Ethos verdict wrapped in an in-toto Statement.
///
/// `predicate` carries the verdict verbatim. Strip the wrapper with `jq .predicate` and
/// the pre-0.6 artifact comes back byte for byte.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Statement<P> {
    /// Always [`IN_TOTO_STATEMENT_V1`].
    #[serde(rename = "_type")]
    pub statement_type: String,
    /// Artifacts this statement is about. Never empty; see [`Statement::new`].
    pub subject: Vec<Subject>,
    /// Predicate schema identifier; build it with [`predicate_type`].
    #[serde(rename = "predicateType")]
    pub predicate_type: String,
    /// The verdict.
    pub predicate: P,
}

impl<P> Statement<P> {
    /// Wrap a verdict.
    ///
    /// The signature encodes the subject ruling in `docs/proof-statement-v1.md` §1.4
    /// rather than leaving it to convention:
    ///
    /// - `representation` is what Ethos actually read, and is always `subject[0]`.
    /// - `source` is the originating document, included **only** when the binding is real.
    ///   Pass `None` rather than inventing one.
    ///
    /// That ordering matters on the Grounding JSON path, where a foreign parser produced
    /// the representation and Ethos never touched the source PDF. A statement claiming to
    /// be about `invoice.pdf` there would assert something Ethos cannot know.
    ///
    /// Taking the first subject by value makes an empty `subject` array unrepresentable,
    /// which in-toto forbids and which no Ethos artifact should ever emit.
    pub fn new(
        representation: Subject,
        source: Option<Subject>,
        predicate_type: impl Into<String>,
        predicate: P,
    ) -> Self {
        let mut subject = Vec::with_capacity(1 + usize::from(source.is_some()));
        subject.push(representation);
        subject.extend(source);
        Self {
            statement_type: IN_TOTO_STATEMENT_V1.to_string(),
            subject,
            predicate_type: predicate_type.into(),
            predicate,
        }
    }
}

/// Serialize a statement to canonical bytes.
///
/// Routes through the one c14n implementation; it does not canonicalize anything itself.
/// No trailing newline — framing is the caller's concern, since the batch path emits
/// NDJSON and the single-report path does not.
pub fn statement_bytes<P: Serialize>(statement: &Statement<P>) -> Result<Vec<u8>, C14nError> {
    let value = serde_json::to_value(statement).map_err(|e| C14nError {
        message: format!("statement is not serializable: {e}"),
    })?;
    c14n_bytes(&value)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn representation() -> Subject {
        Subject::sha256("parser-output.json", "8f3a")
    }

    #[test]
    fn predicate_type_uses_the_locked_base_and_shape() {
        assert_eq!(
            predicate_type("grounding", 1),
            "https://docushell.com/ethos/grounding/v1"
        );
        assert_eq!(
            predicate_type("evidence-anchor", 1),
            "https://docushell.com/ethos/evidence-anchor/v1"
        );
    }

    #[test]
    fn representation_is_always_the_first_subject() {
        let statement = Statement::new(
            representation(),
            Some(Subject::sha256("invoice.pdf", "3fc9")),
            predicate_type("grounding", 1),
            json!({"all_evidence_grounded": true}),
        );
        assert_eq!(statement.subject.len(), 2);
        assert_eq!(statement.subject[0].name, "parser-output.json");
        assert_eq!(statement.subject[1].name, "invoice.pdf");
    }

    #[test]
    fn absent_source_binding_is_omitted_never_invented() {
        // The Grounding JSON path: a foreign parser produced the representation and Ethos
        // never saw the PDF. One subject, and it is the thing that was actually read.
        let statement = Statement::new(
            representation(),
            None,
            predicate_type("grounding", 1),
            json!({}),
        );
        assert_eq!(statement.subject.len(), 1);
        assert_eq!(statement.subject[0].name, "parser-output.json");
    }

    #[test]
    fn statement_round_trips_through_canonical_bytes() {
        let statement = Statement::new(
            representation(),
            None,
            predicate_type("grounding", 1),
            json!({"checks": [], "all_evidence_grounded": true}),
        );
        let bytes = statement_bytes(&statement).expect("a statement serializes");
        let parsed: Statement<serde_json::Value> =
            serde_json::from_slice(&bytes).expect("canonical bytes parse back");
        assert_eq!(parsed, statement);
    }

    #[test]
    fn same_statement_serializes_to_identical_bytes() {
        let build = || {
            Statement::new(
                representation(),
                Some(Subject::sha256("invoice.pdf", "3fc9")),
                predicate_type("grounding", 1),
                json!({"b": 2, "a": 1}),
            )
        };
        assert_eq!(
            statement_bytes(&build()).expect("first"),
            statement_bytes(&build()).expect("second")
        );
    }

    #[test]
    fn wire_field_names_match_the_in_toto_spec() {
        // `_type` and `predicateType` are spec-mandated spellings, not Rust conventions.
        // Renaming either silently produces an artifact no in-toto tooling recognizes.
        let bytes = statement_bytes(&Statement::new(
            representation(),
            None,
            predicate_type("grounding", 1),
            json!({}),
        ))
        .expect("serializes");
        let text = String::from_utf8(bytes).expect("canonical bytes are utf-8");
        assert!(
            text.contains(r#""_type":"https://in-toto.io/Statement/v1""#),
            "{text}"
        );
        assert!(text.contains(r#""predicateType":"#), "{text}");
        assert!(text.contains(r#""sha256":"8f3a""#), "{text}");
    }

    #[test]
    fn predicate_survives_wrapping_byte_for_byte() {
        // The property WP-2's payload-equivalence test depends on: wrapping must not
        // reshape the verdict. `jq .predicate` has to give back exactly what went in.
        let predicate = json!({"schema_version": "1.0.0", "all_evidence_grounded": false});
        let expected = c14n_bytes(&predicate).expect("predicate canonicalizes");
        let statement = Statement::new(
            representation(),
            None,
            predicate_type("grounding", 1),
            predicate,
        );
        let bytes = statement_bytes(&statement).expect("serializes");
        let parsed: serde_json::Value =
            serde_json::from_slice(&bytes).expect("canonical bytes parse");
        let unwrapped = c14n_bytes(&parsed["predicate"]).expect("predicate canonicalizes");
        assert_eq!(unwrapped, expected);
    }
}
