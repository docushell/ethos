# Implementation Plan: Citation Emission Spec v1 and Verification Attestation v1

Status: Part A implemented on 2026-07-19; Part B remains a proposal. Follows the
milestone-d contract pattern.
Companion to `docs/derived-value-v1-and-normalization-v2-implementation-plan.md`; neither
part here depends on that plan, and the two parts here are independent of each other.

- **Part A — Citation Emission Spec v1**: the integrator-facing contract for getting an
  LLM to emit claims Ethos can verify. Docs + one new (model-facing) schema + one runnable
  example. **No verifier code changes.**
- **Part B — Verification Attestation v1**: a config-gated block in the verification
  report that records exactly what produced the verdict, making any historical verdict
  independently re-runnable. Small code change, additive schema change.

Ground rules are inherited unchanged from the companion plan §0: pure functions only,
comparison-only transformations, fail closed, no new dependencies, default profile and all
existing goldens byte-identical, contract doc + fixtures + Make target + CI guard per the
evidence-anchor precedent.

Verified facts this plan builds on (checked against source):

- `ethos verify <input> --citations <file> [--config <file>] [--grounding opendataloader-json] [--out <file>] [--format summary] [--fail-on-ungrounded]`
  — config is optional and defaults to `VerificationConfig::default_v1()`
  (`crates/ethos-cli/src/cmd/verify.rs`).
- Config hash = `ethos_core::c14n::sha256_hex(serde_json::to_value(&config))`, reported as
  `verification_config_sha256`. The same helper can hash any c14n-safe JSON value.
- Citation input shape: bare claims array, or envelope `{document_fingerprint?, claims}`
  (`schemas/ethos-citations.schema.json`).
- Exit codes: `0` all grounded; `1` verification completed, something not grounded;
  `2` usage/malformed input. Exit 2 is a process envelope, never a proof status.
- Grounding-source id formats (native): pages `p\d{4}`, elements `e\d{6}`, spans
  `s\d{6}`, tables `t\d{4}`, regions `r\d{4}`; RAG chunks `c\d{6}` with `element_refs`
  (`e\d{6}`), `page_refs`, `bboxes`, and `document_fingerprint` on every chunk line
  (`schemas/ethos-chunks.schema.json`).
- `VerificationReport` today: `schema_version`, `document_fingerprint?`,
  `verification_config_sha256`, `grounding {parser, capabilities}`, `capability_limits`,
  `fingerprint_stale`, `all_evidence_grounded`, `dispersion?`, `checks`,
  `unsupported_claim_kinds`, `warnings`. It records the **grounding parser's** identity —
  it does not record the **verifier's** identity anywhere. That is Part B's gap.
- Hardened report fields are gated by `HardeningOptions` and bump `schema_version` to
  `HARDENED_VERIFICATION_SCHEMA_VERSION = "1.1.0"` — the precedent Part B follows.

---

# Part A — Citation Emission Spec v1

## A.1 Problem

Ethos is a strict verifier with no published guidance on how to produce its input. Every
integrator independently re-derives: what the LLM should see, what the LLM should emit,
who fills in fingerprints, what to do on exit 2, and what a `mismatch` means for their UI.
Predictable results: models typing quotes by hand (maximum mismatch surface), models asked
to generate fingerprints (they will hallucinate them), retry loops that spin on exit 1
(which is evidence, not an error), and the blame landing on Ethos.

The fix is a normative spec plus a copy-paste kit. One day of writing, no verifier
changes, and it removes the single biggest integration failure mode: **the model should
never type evidence text or fingerprints when a pointer can be resolved instead.**

## A.2 The normative pipeline (pointer-first, hydrate, verify)

```text
1. PARSE      ethos doc parse → document.ethos.json  (or foreign parser + adapter)
2. CHUNK      ethos rag chunks → chunks.jsonl        (each line: c-id, text, element_refs,
                                                      page_refs, document_fingerprint)
3. RETRIEVE   your retriever selects chunk lines; pass them to the LLM verbatim,
              including ids — the ids ARE the citation vocabulary
4. EMIT       the LLM answers and emits claim refs against those ids
              (schema in §A.3 — refs and claimed text, no fingerprints)
5. HYDRATE    the orchestrator (deterministic code, not the LLM) maps refs to the
              ethos-citations shape: injects document_fingerprint from the chunk lines,
              validates id formats, drops nothing silently
6. VERIFY     ethos verify document.ethos.json --citations hydrated.json
              --fail-on-ungrounded --out report.json
7. RELEASE    apply docs/app-answer-release-contract.md over the report
```

Two emission modes, both legal; the spec must present them in this order:

**Mode P (pointer-first, recommended).** For `presence` claims the LLM emits only
`element_id`. For `quote`/`value` claims the LLM emits `element_id` **plus the claimed
text it is asserting**. The orchestrator may additionally *display* text hydrated straight
from the chunk record rather than the model's rendition.

Honest trust semantics — put this paragraph in the spec verbatim, it prevents overclaims:
pointer emission does not make the model honest; it changes what is guaranteed. Ethos
still checks the claimed text against the resolved element. What pointers buy is (a) a
small, unambiguous match target instead of a page-level haystack, (b) fabricated or
dangling ids fail loudly (`element_not_found`), (c) stale documents fail loudly
(`stale_fingerprint`), and (d) if the UI displays hydrated source text, the *displayed*
quote is source-true by construction even when the model's rendition was sloppy.

**Mode Q (typed-quote fallback).** When the orchestrator cannot access chunk records at
answer time, the LLM types the quote and cites `element_id` or `page`. Everything in the
spec still applies; expect a higher mismatch rate and point integrators at the
`canonical_v2` normalization profile (companion plan, Part A) once it ships.

Locator preference ladder (normative): `table_id`+`cell` for tabular values →
`element_id` → `span_id` (only if your pipeline exposes span ids to the model; default
chunks expose element ids) → `page` alone (presence only) → `page`+`bbox` (**discouraged**
for LLM emission — models cannot reliably produce quantized coordinates; bbox citations
are for programmatic callers). Never emit locators from two primary groups on one claim —
the verifier fails that closed as `locator_conflict`.

## A.3 The model-facing output schema (new artifact)

A **separate, smaller schema** than `ethos-citations.schema.json`, because the model must
never be asked to produce fingerprints, envelopes, or bboxes. File:
`schemas/ethos-llm-citation-output.schema.json`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:ethos:schema:llm-citation-output:1",
  "title": "LLM citation emission (model-facing)",
  "type": "object",
  "required": ["answer", "claims"],
  "additionalProperties": false,
  "properties": {
    "answer": { "type": "string" },
    "claims": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["kind"],
        "additionalProperties": false,
        "properties": {
          "kind": { "enum": ["quote", "value", "presence", "table_cell"] },
          "text": { "type": "string", "pattern": "\\S" },
          "element_id": { "type": "string", "pattern": "^e[0-9]{6}$" },
          "span_id": { "type": "string", "pattern": "^s[0-9]{6}$" },
          "page": { "type": "string", "pattern": "^p[0-9]{4}$" },
          "table_id": { "type": "string", "pattern": "^t[0-9]{4}$" },
          "cell": {
            "type": "object",
            "required": ["row", "col"],
            "additionalProperties": false,
            "properties": {
              "row": { "type": "integer", "minimum": 0 },
              "col": { "type": "integer", "minimum": 0 }
            }
          }
        },
        "allOf": [
          {
            "if": { "properties": { "kind": { "enum": ["quote", "value", "table_cell"] } } },
            "then": { "required": ["text"] }
          },
          {
            "if": { "properties": { "kind": { "const": "table_cell" } } },
            "then": { "required": ["table_id", "cell"] }
          }
        ]
      }
    }
  }
}
```

Notes for the implementer:

- Id patterns above are the **native** formats. Foreign grounding sources keep their own
  id namespaces ("id formats follow the grounding source"), so the spec must say: when
  using a foreign adapter, relax the pattern constraints to `"type": "string"` and rely on
  hydration-time validation instead. Ship the native-pinned version as the default.
- No `bbox` on purpose (ladder, §A.2). No `derivation` yet — add it when derived-value v1
  ships, as a versioned schema bump.
- `answer` is carried so one structured output holds both the prose and its claims;
  orchestrators that separate them can ignore it.

**Copy-paste system prompt block** (normative part of the spec doc; tune wording freely,
keep the invariants):

```text
You answer strictly from the provided source chunks. Each chunk line has an "id"
(c000001-style), "text", "element_refs" (e000123-style), and "page_refs" (p0001-style).

For every factual statement in your answer, emit one claim in the required JSON output:
- Quote or value taken from one element: kind "quote" or "value", the exact text you
  are asserting, and the element_id it came from (pick from that chunk's element_refs).
- A table figure: kind "table_cell" with table_id, cell {row, col}, and the cell text.
- "This section/element exists": kind "presence" with element_id or page.

Rules:
- Copy asserted text exactly as it appears in the chunk text. Do not re-format numbers.
- One atomic fact per claim. Never combine two facts in one claim.
- Only use ids that appear in the provided chunks. Never invent ids.
- If the sources do not support a statement, do not make the statement.
```

## A.4 Hydration: model output → `ethos-citations.schema.json`

Deterministic orchestrator code. The mapping table (normative):

| Model field | Citations-file field | Injected by hydration |
| --- | --- | --- |
| `kind` | `claims[].kind` | — |
| `text` | `claims[].text` | — |
| `element_id` / `span_id` / `page` | `claims[].citation.element_id` / `.span_id` / `.page` | — |
| `table_id` + `cell` | `claims[].citation.table_id` + `.cell` | — |
| — | envelope `document_fingerprint` | **yes** — from the chunk records / document JSON, never from the model |

Hydration must also enforce, rejecting the whole batch back to the model at most once
(§A.5): every id exists in the chunks actually shown to the model (kills cross-context id
reuse); exactly one primary locator group per claim; claim count ≤ the config's
`limits.max_checks` (default 256). Reference implementation: one ~80-line pure Python
function in `examples/citation-emission/` with fixture-backed tests — offline, no LLM
call in the repo example; the fixture stands in for model output.

## A.5 Failure policy (normative for integrators)

| Signal | Meaning | Integrator action |
| --- | --- | --- |
| Hydration rejection | Model emitted out-of-vocabulary ids / malformed batch | Re-prompt **once** with the specific rejection; then fail the answer. Never loop. |
| Exit `2` | Malformed citations/config — a bug in your pipeline, not evidence | Fix the pipeline. Alert, don't retry. |
| Exit `1` + report | Verification completed; some checks not grounded | **This is evidence, not an error.** Never regenerate-until-green — that is deleting negative evidence. Apply the app-answer-release contract: release certified claims, mark or drop the rest. |
| Exit `0` + report | All requested evidence grounded | Proceed to release rules. Grounding ≠ relevance; the app contract still owns relevance/synthesis. |

The "never retry exit 1 to green" rule is the spec's most important sentence. A verifier
whose negative verdicts are silently regenerated away provides zero assurance; write it
as a MUST NOT.

## A.6 Artifacts to create (surgical touch list)

1. `docs/citation-emission-spec.md` — the normative spec: §§A.2–A.5 verbatim, id-format
   table, Mode P/Q, ladder, prompt block. Mark it as an application-layer contract like
   `app-answer-release-contract.md` (it adds no verifier status or field).
2. `schemas/ethos-llm-citation-output.schema.json` — §A.3. It is model-facing and
   versioned independently; it is **not** consumed by the verifier, so no Rust changes.
3. `examples/citation-emission/` — fixture model-output JSON (one good, one with a
   dangling id, one with a locator conflict), the reference hydration function, hydrated
   outputs, and expected verification reports against
   `schemas/examples/document.example.json`. Wire into a Make target
   (`citation-emission-spec-contract`) + CI guard script mirroring
   `.github/scripts/test_evidence_anchor_v1_contract.py`: validate fixtures against both
   schemas, run `ethos verify`, byte-compare reports.
4. README: one link line under "Bring your own parser" pointing to the spec. Public
   wording is gated in this repo — route through `docs/public-boundary-claims.json`
   process if the sentence makes any new claim; a bare link should not.

Deliberately excluded: an Ethos-owned prompt-templating library or LLM client (out of
scope forever — Ethos has no network in base crates); a hydration binary in the CLI
(would drag app policy into the trust surface; keep hydration in integrator code with a
reference example); retry orchestration logic (app-owned).

## A.7 Success criteria

1. `make citation-emission-spec-contract` green: fixtures validate against both schemas;
   good fixture verifies exit 0; dangling-id fixture yields `element_not_found`; conflict
   fixture yields `locator_conflict`; reports byte-identical on repeat.
2. The spec answers, without external help: "what do I show the model", "what does the
   model return", "who fills the fingerprint", "what do I do with each exit code".
3. Zero changes under `crates/`. Zero golden diffs.

Estimated effort: 1–2 days.

---

# Part B — Verification Attestation v1

## B.1 Problem

The report proves what was checked but not **what did the checking**. It carries the
grounding parser's identity and the config hash, but not the verifier crate's name or
version, and nothing binds the exact claims input. Consequences:

- A report from v0.3 and one from v0.5 are indistinguishable unless you kept external
  notes. When a rule legitimately changes between versions (e.g. `canonical_v2` ships),
  "same claim, different verdict" looks like broken determinism instead of a versioned
  ruleset change.
- Ethos's determinism promise is per `(inputs, verifier version, config)`. Today a report
  names the config (hash) and the document (fingerprint) but leaves the other two
  reconstruction inputs — verifier version and exact claims — outside the artifact.

Precision matters here: an attestation block is a **binding record, not cryptographic
proof**. Proof requires (a) a signature over the report and (b) the old verifier version
remaining obtainable. (a) stays out of Ethos (see B.4); (b) is a release-process
commitment (see B.5). The block is what makes both possible.

## B.2 Design: one config-gated, deterministic report block

New optional report field, gated like every hardened field:

```json
"attestation": {
  "verifier": { "name": "ethos-verify", "version": "0.3.0" },
  "config_version": "default-v1",
  "claims_sha256": "3fc9…64 hex…",
  "replay": "verify(source_document, claims, config) with this verifier version reproduces this report byte-identically"
}
```

Field decisions, each surfaced:

- `verifier.name` / `verifier.version`: `env!("CARGO_PKG_NAME")` / `env!("CARGO_PKG_VERSION")`
  of `ethos-verify`. Compile-time constants — deterministic per build. **Note the honest
  limit**: this attests the crate version, not the binary provenance. A hostile operator
  can lie; the block is for cooperating parties and auditors, and binary attestation
  (reproducible builds, SLSA-style provenance) is explicitly out of scope v1.
- `config_version`: echo of the config's human label. The hash
  (`verification_config_sha256`) already exists top-level and stays authoritative; the
  echo is for humans reading a report without the config file at hand. Do not echo the
  whole config (it's an input, not an output; keep the report small).
- `claims_sha256`: `c14n::sha256_hex(serde_json::to_value(&claims))` over the **parsed
  claims array** (not the raw file bytes, which would be whitespace-fragile; not the
  envelope, so bare-array and envelope inputs with equal claims hash equal). This is the
  missing binding: report ↔ exact claims input. Uses the existing c14n helper — the same
  mechanism as the config hash, ~5 lines.
- `replay`: a fixed constant string, identical in every report (it documents the
  reproduction recipe inside the artifact itself). Constant ⇒ no determinism risk.
  Tradeoff: some will call it noise; keep it because reports outlive the people who knew
  the recipe. Drop it if review disagrees — nothing else depends on it.
- **Not included, deliberately**: timestamp (breaks byte-identical repeat runs — the
  repo's core invariant; time-of-verification is the operator's log concern), hostname/OS
  (same reason, plus privacy), rust toolchain (version string covers the release;
  toolchain is pinned per release by `rust-toolchain.toml`), report self-hash (impossible
  inside itself; compute externally over the emitted file — document the command, e.g.
  `sha256sum report.json`).

Gating: new `include_attestation: bool` on the existing `HardeningOptions`
(`crates/ethos-core/src/verify_types.rs` ~line 1207), default `false`. Reports that
include it are hardened reports (`schema_version` `1.1.0` path). Default profile emits
nothing new ⇒ all goldens byte-identical.

Tradeoff, surfaced: attestation arguably should be **always on** — an unattested report
is the thing we just argued against. v1 gates it for byte-compat discipline; flipping the
default is a one-line change to propose at the next major schema revision. Record this
intent in the contract doc so it isn't forgotten.

## B.3 Exact changes (surgical touch list)

1. `crates/ethos-core/src/verify_types.rs`
   - `HardeningOptions`: add `#[serde(default)] pub include_attestation: bool`; include it
     in `enabled()`.
   - New struct `Attestation { verifier: VerifierIdentity, config_version: String, claims_sha256: String, replay: String }`
     and `VerifierIdentity { name: String, version: String }`. All strings, c14n-safe.
   - `VerificationReport`: add
     `#[serde(skip_serializing_if = "Option::is_none")] pub attestation: Option<Attestation>`.
2. `crates/ethos-verify/src/lib.rs`
   - Where the report is assembled: if `config.hardening.map_or(false, |h| h.include_attestation)`,
     compute `claims_sha256` from the parsed claims and fill the block. The version
     constants must come from `ethos-verify`'s own `env!` macros — **not** from the CLI
     crate — so library consumers get the same attestation as CLI users.
3. `schemas/ethos-verification-config.schema.json`: `hardening` properties +
   `include_attestation` (boolean, default false).
4. `schemas/ethos-verification-report.schema.json`: optional `attestation` object,
   `additionalProperties: false`, all four fields required when present.
   **Open question (same as the companion plan's)**: whether an additive optional field
   stays within `1.1.0` or wants `1.2.0` — decide once against
   `docs/v0-2-x-compatibility-policy.md`, jointly for this plan and the derived-value
   plan, so the version story stays coherent.
5. Docs
   - New contract doc `docs/verification-attestation-contract.md`: §B.2 as normative
     spec, the "record, not proof" paragraph, the replay procedure (§B.4), and the
     excluded-fields list with reasons.
   - `docs/RELEASE_OPERATOR_RUNBOOK.md`: one added step — never yank published verifier
     crate versions except for security; released CLI artifacts stay downloadable per
     release tag. This is requirement (b) from §B.1 and it is process, not code.
6. Fixtures: one example config with `include_attestation: true` + golden report;
   byte-identical repeat-run check; a test asserting `verifier.version == env!("CARGO_PKG_VERSION")`
   so version bumps can't silently desync; Make target `attestation-v1-contract` + CI
   guard script per the established pattern.

Python/npm wrappers: no changes (JSON pass-through). `--format summary`: append one line
(`attested by ethos-verify X.Y.Z`) only when the block is present — cosmetic, optional.

## B.4 Replay and signing (documented procedure, zero new code)

Replay, to go in the contract doc:

```text
Given report.json:
1. Obtain the verifier version named in attestation.verifier (crates.io or release tag).
2. Collect: the source document JSON whose fingerprint matches document_fingerprint;
   the citations file whose parsed claims c14n-hash to claims_sha256;
   the config file whose c14n hash equals verification_config_sha256.
3. Run: ethos verify <document> --citations <file> --config <file> --out replay.json
4. cmp report.json replay.json   # byte-identical or the attestation is falsified
```

Signing stays **outside** Ethos: no keys, no crypto dependencies, no network in base
crates (standing security posture). The contract doc shows the pattern — detached
signature over the emitted report file bytes (`gpg --detach-sign report.json`, or any
org-standard equivalent) — and states plainly: Ethos provides the stable byte surface;
custody of signatures is the operator's.

## B.5 Success criteria

1. `make attestation-v1-contract` green: golden with attestation on; repeat-run
   byte-identity; version-desync test; replay procedure executed end-to-end in CI against
   the checked-in fixtures (steps 2–4 with in-repo files).
2. `make verify-alpha` and full suite green, zero golden diffs (default off).
3. Contract doc + runbook line merged in the same PR as the code.

Estimated effort: 2–3 days including contract doc, fixtures, and CI guard.

---

## Rollout and open questions

Order: Part A first (unblocks integrators, zero code risk), Part B immediately after —
or in parallel; they touch disjoint files.

Open questions to resolve before implementation, not silently:

1. Report `schema_version` discipline for the additive `attestation` field — align with
   the derived-value plan's identical question against `docs/v0-2-x-compatibility-policy.md`.
2. Keep or drop the constant `replay` string field (§B.2) — pure taste, decide in review.
3. Resolved by the implemented citation-emission contract: source IDs are bounded non-blank
   strings in the model-facing schema;
   hydration applies the selected `GroundingSource` namespace. DocuShell's concrete
   OpenDataLoader integration showed that a native-only schema would require contract forks and
   violate the parser-agnostic-first rule.
4. Whether `--format summary` mentions attestation (cosmetic; default: yes, one line).
