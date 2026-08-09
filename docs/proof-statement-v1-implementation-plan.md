# Implementation Plan: Proof Statement v1

Status: **approved for build, not started.** Companion to `docs/proof-statement-v1.md`,
which owns the format. This document owns sequencing, the file-by-file touch list, and
the acceptance evidence for each step.

Follows the milestone-d contract pattern: ground rules, verified facts, surgical touch
list, tests, acceptance.

---

## Start here

New to this work? Read in this order:

1. `docs/proof-statement-v1.md` §1 — what was ruled and why. Twenty minutes.
2. §0 below — the six ground rules. A change that breaks one is out of scope regardless
   of how good it is.
3. The task board — pick an unclaimed task whose dependencies are done.

### Prerequisites

```bash
rustup show                                    # pinned toolchain from rust-toolchain.toml
pip install "jsonschema>=4.18"                 # schema validation
pip install -r requirements-dev.txt            # repo dev tooling
cp scripts/hooks/commit-msg .git/hooks/ && chmod +x .git/hooks/commit-msg
```

That last line is not optional. Every commit needs a `Signed-off-by` trailer in the final
paragraph, CI checks the whole PR range, and the hook catches the two ways it goes wrong.

PDFium is **not** needed for this work. Nothing here touches parsing.

### The loop

```bash
cargo test --locked --workspace --all-features    # expect 400+ passing, 0 failing
cargo fmt --all && cargo clippy --locked --workspace --all-targets --all-features -- -D warnings
python3 schemas/validate_examples.py              # after any schema change
make -n release-gates                             # must still expand; parked gates stay reachable
```

Before opening a PR, run what CI runs. The nine jobs are listed in `docs/ci-scope.md`.

### Rules for claiming work

- One work package per branch, one task per commit where practical.
- **Goldens move in a commit that changes nothing else.** Never bundle a golden
  regeneration with a behaviour change; that is the one thing that makes this migration
  unreviewable.
- If a task turns out to need a decision, stop and raise it. Do not decide format
  questions in a PR — `docs/proof-statement-v1.md` §1 is where those live.

### Definition of a finished task

Code, test, schema, and golden all in the same state. A task with passing code and a stale
schema is not done. Each task below names its own acceptance evidence.

---

## Task board

Dependencies run top to bottom. Nothing in WP-2 starts before WP-1 lands.

| ID | Task | Acceptance | Depends on |
| --- | --- | --- | --- |
| **0.1** | Test the geometry-free text path — `{element_id, expected_text}`, no page, no bbox | fails if `resolve_page` returns `NotFound` or `requires_bbox` turns true at `AnchorLevel::Text` | — |
| **0.2** | `bbox` → `Option<[i64; 4]>` on element, span, table, cell; schema unchanged | workspace green; grounding validation byte-identical (goldens unmoved) | — |
| **0.3** | Record the five multi-format gates and the DOCX → XLSX → PPTX sequencing | contract doc section exists | — |
| **1.1** | New `crates/ethos-core/src/statement.rs`: `Subject`, `Statement<P>`, `statement_bytes` | compiles; `digest` is a `BTreeMap` | — |
| **1.2** | Export from `lib.rs`, gated behind the `verify-types` feature | `cargo check -p ethos-doc-core --no-default-features --features grounding` passes | 1.1 |
| **1.3** | Round-trip test: build → serialise → parse → compare | test passes | 1.1 |
| **1.4** | Byte-stability test: same input twice, identical bytes | test passes | 1.1 |
| **2.1** | New `schemas/ethos-proof-statement.schema.json` | `validate_examples.py` passes | 1.2 |
| **2.2** | Wrap in `verification_report_json_bytes` (`cmd/verify.rs:233`) | single + batch NDJSON paths both wrapped | 1.2 |
| **2.3** | Subject construction: `[0]` representation always, `[1]` source only when bound | test proving `[1]` is omitted, never synthesised | 2.2 |
| **2.4** | **Payload-equivalence test** — `c14n(new.predicate)` == `c14n(old_report)` for every golden | the whole re-wrap proven to be a no-op | 2.2 |
| **2.5** | Regenerate goldens, standalone commit | determinism workflow green | 2.4 |
| **2.6** | Wrapped example under `schemas/examples/` | `validate_examples.py` passes | 2.1 |
| **3.1** | `Attestation`, `VerifierIdentity`, `ConfigIdentity`, `InputIdentity` in `verify_types.rs`; field is required, not `Option` | compiles | 2.5 |
| **3.2** | Populate in `ethos-verify` using **its own** `env!` macros, not the CLI's | library callers get the same attestation as CLI callers | 3.1 |
| **3.3** | `claims_sha256` from the **parsed claims array** | bare-array and envelope inputs with equal claims hash equal | 3.1 |
| **3.4** | Schema: `attestation` required | `validate_examples.py` passes | 3.1 |
| **3.5** | Version-desync test: `verifier.version == env!("CARGO_PKG_VERSION")` | a version bump cannot silently desync | 3.2 |
| **3.6** | Replay test: regenerate a golden from its named inputs, `cmp` byte-identical | passes | 3.2 |
| **4.1** | `EvidenceTier` enum in `verify_types.rs` | compiles | 3.6 |
| **4.2** | Derive from locator precedence in `resolve_target` | one test per locator kind | 4.1 |
| **4.3** | Schema + goldens | existing capability-downgrade tests unchanged | 4.2 |
| **5.1** | Shared serialiser — the other five artifacts serialise inline today | one code path for all six | 4.3 |
| **5.2** | `grounding-validation/v1`; keep accepting `artifact_type` on **input** (ADR-0016 frozen error vocabulary) | payload-equivalence test | 5.1 |
| **5.3** | `evidence-anchor/v1` | payload-equivalence test | 5.1 |
| **5.4** | `security/v1` | payload-equivalence test | 5.1 |
| **5.5** | `crop/v1` — *first to defer if the release drags* | payload-equivalence test | 5.1 |
| **5.6** | `answer-release/v1` — *first to defer if the release drags* | payload-equivalence test | 5.1 |
| **6.1** | `docs/CLAIMS.md` | contains all five does-not-prove rows listed in WP-6 | 5.6 |
| **6.2** | `docs/proof-statement-contract.md` — payload-vs-envelope field table | every field assigned a layer | 5.6 |
| **6.3** | README reframe | — | 6.1 |
| **6.4** | Migration guide: `jq .predicate` recovers the pre-0.6 shape | — | 6.1 |

**2.4 is the one that matters most.** Every golden moves at once during this migration,
which blinds determinism CI exactly when it is most needed. That test reduces the whole
re-wrap to a provable no-op, so any real semantic change is forced into its own visible
commit. `.github/scripts/check_golden_change_rationale.py` exists for this — use it rather
than working around it.

---

## 0. Ground rules

Non-negotiable. A change that breaks one of these is out of scope regardless of merit.

1. **Shape changes, semantics do not.** If a change alters what `grounded` means for any
   existing claim, it is not in this release. The predicate content is a pure re-wrap.
2. **One statement builder.** `ethos-core` owns it. No command hand-rolls a statement, the
   same rule that already governs c14n (invariant 3). This is the single most important
   rule here — Signet's four hand-built signable shapes across two files is the failure
   mode being designed out.
3. **Predicates are deterministic.** No time, host, identity, or run id inside a
   predicate. Enforced by type where possible.
4. **Fail closed.** An unknown `predicateType` is an error, never a fallback. This matches
   the existing dispatch in `crates/ethos-cli/src/grounding.rs`.
5. **No new dependencies.** Everything needed is already in the tree.
6. **Goldens move once, in a commit that changes nothing else.**

---

## 1. Verified facts this plan builds on

Checked against the source tree at `main` (`c7d893d`). Re-verify before relying on line
numbers.

| Fact | Location |
| --- | --- |
| `VerificationReport` — 11 fields, `schema_version` first | `crates/ethos-core/src/verify_types.rs:360` |
| `HardeningOptions` — `include_provenance`, `include_context_echo`, `include_dispersion`, `context_window_chars` | `verify_types.rs:1207` |
| Report serialiser: serde → `c14n_bytes` → trailing newline | `crates/ethos-cli/src/cmd/verify.rs:233` |
| c14n API: `c14n_bytes(&Value)`, `sha256_hex(&Value)`, `sha256_hex_bytes(&[u8])` | `crates/ethos-core/src/c14n.rs:57,140,146` |
| Config hash already computed as `sha256_hex(c14n(config))` | `cmd/verify.rs:128` |
| `write_output(Option<PathBuf>, &[u8])` — 12 call sites across 8 command modules | `crates/ethos-cli/src/main.rs:539` |
| Input artifact-type dispatch already exists, fail-closed, duplicate-key aware | `crates/ethos-cli/src/grounding.rs:22,118,177` |
| Grounding validation report already requires `artifact_type` (`const`) | `schemas/ethos-grounding-validation-report.schema.json` |
| Baseline: 400 Rust tests pass on `main` | `cargo test --workspace --all-features` |

Two consequences worth stating. `verification_report_json_bytes` is the **only**
`*_json_bytes` serialiser in the CLI; the other five artifacts serialise inline at their
call sites, so step 1 has to introduce a shared path rather than edit one. And the config
hash mechanism needed for the attestation block already exists and needs no new code.

---

## 2. Work packages

Dependency order. Each lands as its own commit with its own acceptance evidence.

### WP-0 — Keep the multi-format path open

**Goal:** remove future obstacles without adding future features. Multi-format support is
**not** in this release (`docs/proof-statement-v1.md` §7). This work package only stops the
door closing.

Runs alongside WP-1. Nothing in the statement work depends on it, and it depends on nothing.

**0.1 — Test the geometry-free text path.** `docs/v0-6-0-release.md` §10.1 established by
source audit that an evidence ref of `{element_id, expected_text}` with no page and no bbox
reaches `AnchorStatus::Bound` at `AnchorLevel::Text` with no capability limit. **Nothing
tests it.** A refactor could close that path and no one would find out until someone tried a
flow document years later.

Assert all four steps, not just the outcome: `page_locator_required` is false,
`resolve_page` returns `PageCheck::NotChecked` rather than `NotFound`, `resolve_bbox` is
never reached, and the result is `Bound` with an empty capability-limit list.

This converts an audit finding into an enforced invariant. Audit findings decay; tests do
not.

**0.2 — `bbox` becomes `Option<[i64; 4]>` in the trait.** Four fields in
`crates/ethos-core/src/grounding.rs` (element, span, table, cell) plus every read site in
`ethos-verify` and the OpenDataLoader adapter.

§10.1 frames the choice as "unread in-memory sentinel versus `Option` and a breaking change
to the published `0.5.0` baseline". **v0.6.0 is already a breaking change to that baseline** —
WP-3 adds a required `attestation` field to `VerificationReport`. So the honest option costs
nothing extra now and costs a second breaking release later.

**The schema does not move.** `bbox` stays required in `ethos.grounding.v1`, `media_type`
stays `const "application/pdf"`, and the positive-area check stays. The Rust type becomes
able to express absence; the wire contract still refuses it. Relaxing the schema *is* the
feature, and the feature is out of scope.

Mechanical but not trivial — the compiler finds every site, but there are many. Half a day.

**0.3 — Record the extension points.** A short section in the contract doc naming the five
gates from §10.1, where each lives, and the DOCX → XLSX → PPTX sequencing, so nobody
re-derives it.

**Not in scope for WP-0**, and each for a reason:

- Relaxing any schema gate — that is the feature.
- A format registry, a `Format` enum, or a plugin layer — speculative abstraction against a
  requirement nobody has stated.
- New locator kinds. `GroundingCell` already carries `row`, `col`, `row_span`, `col_span`.
  **Row/column addressing is R1C1**, so an XLSX sheet maps onto the existing table model with
  no new locator concept. The only blocker is `bbox` on cells, which 0.2 handles.

**Acceptance**
- 0.1 fails if `resolve_page` is changed to return `NotFound`, or if `requires_bbox` starts
  returning true for `AnchorLevel::Text`
- 0.2: `cargo test --workspace --all-features` green; `ethos.grounding.v1` validation
  behaviour byte-identical, proven by unchanged goldens
- `make -n release-gates` still expands

### WP-1 — Statement builder

**Goal:** one place that turns `(subject, predicateType, predicate)` into canonical bytes.

New module `crates/ethos-core/src/statement.rs`:

```rust
pub const IN_TOTO_STATEMENT_V1: &str = "https://in-toto.io/Statement/v1";
pub const PREDICATE_BASE: &str = "https://docushell.com/ethos";

pub struct Subject { pub name: String, pub digest: BTreeMap<String, String> }
pub struct Statement<P> { _type, subject: Vec<Subject>, predicate_type: String, predicate: P }

pub fn statement_bytes<P: Serialize>(stmt: &Statement<P>) -> Result<Vec<u8>, C14nError>;
```

`digest` is a `BTreeMap` so key order is canonical without relying on serde field order.
`statement_bytes` routes through the existing `c14n_bytes`; it does not reimplement
canonicalisation.

**Touch list**
- `crates/ethos-core/src/statement.rs` (new)
- `crates/ethos-core/src/lib.rs` — export the module
- `crates/ethos-core/Cargo.toml` — gate behind the existing `verify-types` feature so
  invariant 5 holds (`ethos-verify` must still build with `--no-default-features
  --features grounding`)

**Acceptance**
- `cargo check -p ethos-doc-core --no-default-features --features grounding` still passes
- round-trip test: build a statement, serialise, parse, compare
- byte-stability test: same input twice, identical bytes

### WP-2 — `grounding/v1` as a pure re-wrap

**Goal:** `ethos verify` emits a statement. The predicate is the current report, unchanged.

**Touch list**
- `crates/ethos-cli/src/cmd/verify.rs:233` — `verification_report_json_bytes` wraps before
  c14n. Single edit; both the single-report and batch/NDJSON paths flow through it.
- `schemas/ethos-proof-statement.schema.json` (new) — the statement envelope
- `schemas/ethos-verification-report.schema.json` — unchanged, becomes the predicate schema
- `schemas/examples/` — add a wrapped example
- Goldens under `crates/ethos-cli/tests/` — regenerate

**Subject construction** (per spec §1.4):
- `subject[0]` = representation. `name` from the input path's file name, `digest.sha256`
  from `representation_sha256`.
- `subject[1]` = source document, **only** when a real binding exists. Never synthesised.

**Acceptance — the critical one**
- **Payload-equivalence test:** for every golden, `c14n(new.predicate)` is byte-identical
  to `c14n(old_report)`. This reduces WP-2 to a provably pure re-wrapping.
- goldens regenerated in a commit that changes nothing else
- determinism workflow green
- `make -n release-gates` still expands

### WP-3 — Attestation block

**Goal:** every predicate names what produced it. Non-optional.

**Touch list**
- `crates/ethos-core/src/verify_types.rs` — `Attestation`, `VerifierIdentity`,
  `ConfigIdentity`, `InputIdentity`; add `attestation: Attestation` to `VerificationReport`
  (required, not `Option`)
- `crates/ethos-verify/src/lib.rs` — populate at report assembly. Version constants come
  from `ethos-verify`'s own `env!("CARGO_PKG_NAME")` / `env!("CARGO_PKG_VERSION")`, **not**
  the CLI's, so library callers get the same attestation as CLI callers.
- `crates/ethos-cli/src/cmd/verify.rs` — pass `claims_sha256`, computed as
  `sha256_hex(to_value(&parsed_claims))` over the **parsed claims array**, not raw file
  bytes (whitespace-fragile) and not the envelope (so bare-array and envelope inputs with
  equal claims hash equal)
- `schemas/ethos-verification-report.schema.json` — add `attestation`, required
- Goldens — regenerate

**Excluded deliberately:** timestamp, hostname, toolchain. Each breaks byte-identical
repeat runs.

**Acceptance**
- test asserting `attestation.verifier.version == env!("CARGO_PKG_VERSION")` so a version
  bump cannot silently desync
- double-run byte equality
- replay: regenerate a golden from its named inputs, `cmp` byte-identical

**Process commitment, starts now, no code:** published verifier crate versions are never
yanked except for security. A report naming an unobtainable verifier version stops being
replayable, and that damage is retroactive.

### WP-4 — `evidence_tier`

**Touch list**
- `verify_types.rs` — `evidence_tier: EvidenceTier` enum
- `crates/ethos-verify/src/lib.rs` — derive it from the existing locator precedence in
  `resolve_target`
- schema + goldens

`EvidenceTier`: `exact_span | element_scoped | page_scoped | capability_limited`.

**The singular `grounding` field is unchanged.** An earlier draft replaced it with
`sources: Vec<_>` to support corroboration. That capability is cut, so the array would be
frozen at length one and never exercised — the exact unvalidated shape that forces a `v2`.

**Acceptance:** tier derivation covered per locator kind; existing capability-downgrade
tests still pass unchanged.

### WP-5 — Remaining five predicates

`grounding-validation/v1`, `evidence-anchor/v1`, `security/v1`, `crop/v1`,
`answer-release/v1`. Each a pure re-wrap with its own payload-equivalence test.

Requires a shared serialiser first, since these five currently serialise inline at their
`write_output` call sites in `cmd/{grounding,evidence,security,crop}.rs`.

`grounding-validation/v1` additionally retires its `artifact_type` field in favour of
`predicateType`. Keep accepting the old field on **input** — `probe_artifact_type` is a
consumer contract with a frozen error vocabulary under ADR-0016.

**If the release drags, `crop/v1` and `answer-release/v1` defer to 0.6.1.** Fewest
consumers.

### WP-6 — Documentation

- `docs/CLAIMS.md` (new) — proves / does-not-prove / regulatory mapping with a residual-gap
  column / a paste-ready questionnaire paragraph
- `docs/proof-statement-contract.md` — the payload-vs-envelope field table
- README reframe
- migration guide: `jq .predicate` recovers the pre-0.6 shape

Rows that must appear in the does-not-prove table:
- attestation names the crate version, not binary provenance
- corroboration raises confidence, it does not prove parser fidelity
- Ethos does not compare across runs; each verification is independent
- a reworded claim fails as `mismatch` even when the underlying fact is right
- `subject[0]` is what Ethos read, which is not always the source PDF

---

## 3. Migration and goldens

Every golden changes at once, so determinism CI goes blind exactly when it matters. Two
rules make that survivable, and both are mandatory.

**One pure re-wrap commit.** Goldens regenerate in a commit touching nothing else.

**Payload equivalence.** For every migrated artifact, assert the new `predicate` is
byte-identical to the old top-level document. Any real semantic change then has to appear
in its own visible commit. `.github/scripts/check_golden_change_rationale.py` already
exists for this; use it rather than working around it.

---

## 4. Out of scope

Corroboration and multi-source comparison. Signing and keys. A keystore. Hash-chained
logs. Bundle export and an offline verifier. A conformance vector corpus. MCP proxying.
Semantic checking. New parsers. Any change to verification semantics.

Bundles and the conformance corpus are the two most likely to be argued back in. Both are
commitment devices whose purpose is to make change expensive, and there are zero
third-party implementers today to make that worth paying for. They ship when an external
party depends on the format, or when an auditor asks for a portable bundle.

---

## 5. Definition of done

- All six predicate types emit statements through one builder
- Payload equivalence proven for all six migrated artifacts
- Attestation present and non-optional in every predicate
- 400+ tests pass; determinism workflow green; `make -n release-gates` expands
- `CLAIMS.md` published
- Nothing published to any registry — that is a separate decision under `release-gates`
