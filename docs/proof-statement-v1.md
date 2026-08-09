# Proof Statement v1

Status: **ruled, not implemented.** The three decisions in §1 are settled. Nothing here
is built yet.

Base URI is locked to `https://docushell.com/ethos/` (§1.2). Build sequencing and the
file-by-file touch list live in `docs/proof-statement-v1-implementation-plan.md`.

Scope: this makes Ethos output artifacts self-describing and self-attesting. It changes
no verification semantics. If a proposal alters what `grounded` means for any
existing claim, it does not belong in this document.

---

## 1. Decisions

### 1.1 Artifact shape — RULED: in-toto Statement

Ethos emits six distinct top-level output artifacts today. One of them, the grounding
validation report, carries `artifact_type: "ethos.grounding_validation.v1"` as a required
field. The other five are identified by filename convention alone, carry no source
binding, and say nothing about what produced them.

`crates/ethos-cli/src/grounding.rs` already implements type dispatch on input:
`ARTIFACT_TYPE_KEY`, `probe_artifact_type()`, fail-closed handling of unknown types, and
duplicate-key counting. **v0.6.0 reached for self-describing artifacts and stopped at
one.** This document finishes that, rather than importing a foreign idea.

Ruled: the in-toto Statement is the native artifact.

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    { "name": "invoice.pdf", "digest": { "sha256": "3fc9…" } }
  ],
  "predicateType": "https://docushell.com/ethos/grounding/v1",
  "predicate": { }
}
```

Why this over a bespoke envelope: an established shape, existing tooling, and auditor
familiarity for no invented format. `subject[].digest.sha256` is already exactly what
Ethos computes as a source fingerprint.

**Not DSSE as the artifact.** DSSE base64-encodes the payload. For a build attestation
that is fine because tooling reads it. For document evidence, where opening the file and
reading it is half the value, it is a regression. DSSE stays a signing wrapper for T2
(§6) and never becomes the thing on disk at T0 or T1.

Verify the current `_type` revision against the in-toto spec before freezing it.

### 1.2 URI namespace — RULED: `https://docushell.com/ethos/`

`predicateType` URIs are permanent. A URL rather than a bare string because the namespace
is what stops one vendor's `grounding/v1` colliding with another's, which matters as soon
as a system consumes statements from more than one producer.

**Base URI, locked:** `https://docushell.com/ethos/`

```
https://docushell.com/ethos/grounding/v1
https://docushell.com/ethos/evidence-anchor/v1
https://docushell.com/ethos/security/v1
```

Shape is `<base>/<predicate>/v<n>` for all six, with no exceptions.

Chosen over a dedicated Ethos domain because a purchase and a perpetual renewal
obligation is a poor trade against a weak branding signal. Independence is carried by the
Apache-2.0 licence, offline key-free operation, and byte-reproducible results — none of
which a hostname affects. The `/ethos/` path segment scopes the namespace, so a later move
to a dedicated domain is a rename that keeps the old string as a recognised alias.

**`v<n>` versions the predicate schema, never the product.** `grounding/v1` stays `v1`
across Ethos 0.6, 0.7, and 1.0. It bumps only when the predicate's own shape breaks.

### 1.3 Source identity — RULED: representation hash authoritative

`representation_sha256` stays the authoritative fingerprint, per the standing ruling in
`docs/v0-6-0-release.md` §8. Ethos names what it actually read.

This matters most on the Grounding JSON path, where a foreign parser produced the
representation and **Ethos never touched the source PDF**. An artifact claiming to be
"about invoice.pdf" would be asserting something Ethos cannot know.

### 1.4 Subject shape — RULED: both, representation first

`subject` is an array, so the honest answer and the useful one are not in conflict.

```json
"subject": [
  { "name": "parser-output.json", "digest": { "sha256": "8f3a…" } },
  { "name": "invoice.pdf",        "digest": { "sha256": "3fc9…" } }
]
```

- `subject[0]` is always the representation Ethos read. Required.
- `subject[1]` is the source document, present **only** when the binding is real. Omitted
  otherwise, never guessed.

Consumers must not assume `subject[0]` is the PDF. That is a documentation obligation and
it goes in the contract doc and in `CLAIMS.md`.

Claims and config do not appear in `subject`. A verdict depends on three inputs — document,
claims, config — and in-toto's subject model is artifact-centric, so the other two bind in
the attestation block (§4) instead. Two reports over one document with different claims
share a subject, which is correct: both are statements *about* that document.

### 1.5 Representations — RULED: stay bare

`document.ethos.json` and `chunks.jsonl` are **not** wrapped. Statements are for verdicts
only.

A statement means "X asserts P about Y." A document graph is not an assertion *about* the
document; it is the document re-expressed. Wrapping it would read as "here is a claim
about invoice.pdf, and the claim is invoice.pdf." Wrap everything and `statement` stops
distinguishing anything, which costs the design the one line an integrator has to hold in
their head.

Three supporting reasons:

- `chunks.jsonl` is streaming NDJSON. Wrapping each line bloats every record; wrapping the
  file breaks streaming.
- Both are consumed by other tools, including DocuShell's retrieval path. Wrapping changes
  working consumers for no benefit they would notice.
- The provenance argument does not apply: both already carry a document fingerprint,
  profile hash, and config hash per `SPEC.md`. They are self-describing already.

This is the same instinct as the `II.1` rule in DocuShell's workbench architecture, applied
one level down: the thing being judged must not look like the judgment.

---

## 2. Payload and envelope

The split is enforced, not merely documented.

```
predicate   deterministic. byte-identical across runs. no time, no host,
            no identity, no run id. this is what hashes and what replays.
statement   subject, predicateType, _type. stable, but outside the
            determinism contract.
wrapper     DSSE at T2. signatures, timestamps, operator claims. later.
```

Enforce it by type, the way `QuantizedGeom` enforces quantize-at-extraction. A predicate
struct that cannot hold a `SystemTime` cannot break the goldens. This is what makes
signing safe to add later without a second migration.

The contract doc carries a field table stating which layer every field lives in, and an
explicit warning that basing policy decisions on wrapper fields is unsafe. Signet's
`SECURITY.md` is the model here: it tabulates signed versus unsigned fields and spells
out the attack when a developer trusts an unsigned one.

---

## 3. Predicate types

| Predicate | Replaces | Status |
| --- | --- | --- |
| `grounding/v1` | `verification_report.json` | migrate |
| `grounding-validation/v1` | `ethos.grounding_validation.v1` | migrate, URI-ify |
| `evidence-anchor/v1` | `evidence_anchor_report.json` | migrate |
| `security/v1` | `security_report.json` | migrate |
| `crop/v1` | crop descriptors | migrate |
| `answer-release/v1` | app-answer-release decision | migrate |

Migration of each existing artifact is a **pure re-wrap**: the current schema becomes the
predicate schema unchanged, and the statement wraps it. A payload-equivalence test asserts
the new `predicate` block is byte-identical to the old top-level report, which reduces the
migration to a provably pure re-wrapping and forces any semantic change into its own
visible commit.

If the release starts dragging, `crop/v1` and `answer-release/v1` are the first to defer.
They have the fewest consumers.

---

## 4. Attestation block

Non-optional, inside every predicate. Promotes Part B of
`docs/citation-emission-spec-and-attestation-implementation-plan.md` from proposal to
foundational.

```json
"attestation": {
  "verifier": { "name": "ethos-verify", "version": "0.6.0" },
  "config":   { "version": "default-v1", "sha256": "…" },
  "inputs":   { "claims_sha256": "…", "source_fingerprint": "sha256:…" },
  "replay":   "verify(source, claims, config) with this verifier version reproduces this predicate byte-identically"
}
```

Version constants come from `ethos-verify`'s own `env!` macros rather than the CLI's, so
library callers get the same attestation as CLI callers.

Deliberately absent: timestamp, hostname, toolchain. All three break byte-identical repeat
runs, which is the core invariant. They belong in the wrapper if anywhere.

**Honest limit, and it goes in `CLAIMS.md`:** this attests the crate version, not binary
provenance. A hostile operator can lie. The block is for cooperating parties and auditors.

One process commitment starts immediately, independent of code: **published verifier crate
versions are never yanked except for security.** It is the only part of this release that
degrades retroactively if skipped, because a report naming an unobtainable verifier version
stops being replayable.

---

## 5. Evidence tier

```json
"evidence_tier": "exact_span"
```

One deterministic enum saying how strong the match was, derived from the existing locator
precedence. Values: `exact_span`, `element_scoped`, `page_scoped`, `capability_limited`.

Generalises AetherProof's `model_root_type`: put the strength of what was proven into the
artifact as a single field, so a consumer reads one value instead of interpreting a
capability matrix.

**Multi-source is deliberately absent.** An earlier draft carried `sources: []` to support
running two parsers and comparing them. That capability is dropped (see §7), and an array
that is always length one, never exercised, is exactly the kind of unvalidated shape that
forces a `v2` later. The singular `grounding` field stays as it is.

---

## 6. Proof tiers

Publish these as a table. The ordering is counterintuitive and the top rung is the one
nobody else can occupy.

| Tier | Claim | Key required |
| --- | --- | --- |
| **T0 Reproducible** | anyone re-runs and gets identical bytes | no |
| **T1 Attested** | the record names the verifier, config, and exact claims that produced it | no |
| **T2 Signed** | a named key asserts who ran it and when | yes |

Ethos ships T0 and T1 in this release. T2 is deliberately out: the statement shape makes
signing a wrapper you add later without touching the artifact, which is the whole reason
for getting the shape right first.

The message the tiers carry: everyone else starts at T2 and calls it proof. T2 says someone
claimed this. T0 says check it yourself.

---

## 7. Out of scope

Corroboration and multi-source comparison. Multi-format grounding (DOCX, XLSX, PPTX).
Signing and keys. A keystore. Hash-chained logs. Bundle export and an offline verifier.
A conformance vector corpus. MCP proxying. Semantic checking. New parsers. Any change to
verification semantics.

**On multi-format specifically.** `docs/v0-6-0-release.md` §10.1 already scoped it: the
verifier binds text with no geometry today, and the requirement lives in five gates in the
artifact schema and its validator, not in the verification algorithm. It is out of scope
here because no DocuShell workflow needs it — WORKBENCH Part I puts "any format other than
PDF" out of scope, and Part II names no trigger for it. Docling supporting every format is
a fact about Docling, not a requirement on Ethos.

Two things keep the option open at near-zero cost, and both are in WP-0 of the
implementation plan: a test locking the geometry-free text path, which is currently an
audit finding with nothing enforcing it, and `Option<[i64; 4]>` for `bbox` in the trait,
which rides the breaking change WP-3 already makes rather than needing a second one. The
schema does not move.

**Trigger to revisit:** a named DocuShell workflow requiring DOCX or XLSX verification, a
design partner asking, or a real corpus where non-PDF is a meaningful share. Not before.

The five gates, where each lives, and the DOCX → XLSX → PPTX sequencing are recorded in
`docs/bring-your-own-parser.md` so nobody re-derives them.

**On corroboration specifically.** Running two independently derived parsers and reporting
their disagreement is the only deterministic answer to "who checks the parser?", and it is
cut anyway. No external user has asked for it, two parsers sharing an upstream share
failure modes, it doubles parse cost, and nobody has measured the divergence rate on real
documents — a rate near zero makes it not worth building and a rate that is high makes it
noise reviewers learn to ignore. The compensating control already shipped: DocuShell shows
a reviewer the rendered crop of the actual page region. Revisit only with a measured
divergence number, not a threat model.

Bundles and the conformance corpus are the two most likely to be argued back in. Both are
commitment devices whose job is to make change expensive, and there are currently zero
third-party implementers to make that worth paying for. They ship when someone external
depends on the format, or when an auditor asks for a portable bundle — whichever comes
first.

---

## 8. Order of work

```
1.  Statement wrapper: one builder in ethos-core, no command hand-rolls a statement
2.  grounding/v1 as a pure re-wrap + payload-equivalence test + regenerated goldens
3.  Attestation block, non-optional
4.  evidence_tier
5.  Remaining five predicates
6.  CLAIMS.md + README reframe
```

Step 2 lands as one commit that changes nothing but shape. Every golden moves at once, so
determinism CI goes blind exactly when it matters most; the payload-equivalence test is
what keeps that survivable.

## 9. Prior art

Two adjacent projects informed this and neither contributed code.

**Signet** (Prismer-AI, Apache-2.0/MIT) builds its signable payload by hand in four
different shapes across two files, with no schema anywhere. It works, and nothing enforces
that it keeps working. §2's single-builder rule exists so that failure mode is structurally
impossible here rather than merely discouraged. Its `SECURITY.md` signed-versus-unsigned
field table is the model for the §2 field table, and its bundle manifest separates
chain-start from chain-tip so a partial export is honest about being partial.

**AetherProof** (pulkit6732, Apache-2.0) contributes two ideas. `model_root_type` puts the
tier of what was proven inside the signed payload, which §5.1 generalizes as
`evidence_tier`. Its `docs/CLAIMS.md` pairs a proves table with a does-not-prove table
carrying a residual-gap column, plus a paste-ready paragraph for security questionnaires;
that structure is what Ethos's own `CLAIMS.md` should copy. Its signing preimage is
length-prefixed with `len()` counting Python code points, which is injective in Python and
diverges in a JavaScript or Rust port — a reminder that a format defined in one language is
not a format, and the reason §1.1 prefers an established shape.
