# Proof Statement v1

Status: **ruled, not implemented.** The three decisions in §1 are settled. Nothing here
is built yet.

Base URI is locked to `https://docushell.com/ethos/` (§1.2). Build sequencing and the
file-by-file touch list live in `docs/proof-statement-v1-implementation-plan.md`.

Scope: this changes the *shape* of Ethos output artifacts and adds corroboration. It
changes no verification semantics. If a proposal alters what `grounded` means for any
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
https://docushell.com/ethos/corroboration/v1
https://docushell.com/ethos/security/v1
```

Shape is `<base>/<predicate>/v<n>` for all seven, with no exceptions.

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

### 1.5 Decided while drafting, override if wrong

**Representations stay bare.** `document.ethos.json` and `chunks.jsonl` are representations,
not assertions about anything. Statements are for verdicts.

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
| `corroboration/v1` | nothing | new (§5) |

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

## 5. Multi-source and corroboration

### 5.1 `sources[]`

```json
"sources": [
  { "parser": { }, "capabilities": { }, "fingerprint": "sha256:…" }
],
"evidence_tier": "exact_span"
```

An array even when N=1. Widening a frozen schema from one to many costs a major version;
starting wide costs nothing today.

`evidence_tier` generalizes AetherProof's `model_root_type`: put the *strength of what was
proven* into the artifact as one enum, so a consumer reads one field rather than
interpreting a capabilities matrix. Values: `exact_span`, `element_scoped`, `page_scoped`,
`capability_limited`. Derived deterministically from locator precedence.

### 5.2 `corroboration/v1`

The reason this release is worth a migration.

Run N independently derived grounding sources over one subject. Compare bindings under
declared tolerance. Emit one state:

| State | Meaning |
| --- | --- |
| `corroborated` | every source binds the claim, locators agree |
| `single_source` | N=1, stated plainly rather than implied |
| `divergent` | sources disagree — the most useful signal Ethos can produce |
| `capability_asymmetric` | only some sources could answer |

Source independence is **declared, never assumed**. Two adapters both wrapping PDFium share
failure modes, and the predicate has to say so.

This is a deterministic dent in the gap `docs/hallucination-threat-model.md` and DocuShell's
own MVP notes both name: a parser error that both drafts and verifies consistently is
otherwise invisible. It does not close that gap. It makes one class of it visible.

Corroboration raises confidence. It does not prove fidelity. That sentence belongs in
`CLAIMS.md` on day one, before anyone reads `divergent` as a verdict.

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

Signing and keys. A keystore. Hash-chained logs. Bundle export and an offline verifier.
A conformance vector corpus. MCP proxying. Semantic checking. New parsers. Any change to
verification semantics.

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
4.  sources[] + evidence_tier
5.  corroboration/v1
6.  Remaining five predicates
7.  CLAIMS.md + README reframe
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
