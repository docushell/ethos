# Implementation Plan: Canonical Text Normalization v2 and Derived-Value Claims v1

Status: proposal — not approved, not scheduled. Follows the milestone-d contract pattern.
Every type, function, file, and schema named here was verified against the source tree at the time of writing.

Two features, one document, because they share ground rules:

- **Part A — Canonical Text Normalization v2**: stop failing real quotes over invisible
  characters, ligatures, and typographic punctuation.
- **Part B — Derived-Value Claims v1**: verify simple arithmetic ("$10 + $5 = $15") by
  deterministic re-execution over already-grounded evidence.

Part A is days of work. Part B is weeks. Part A ships first. Neither depends on the other,
but Part B's number grammar is simpler if Part A's normalization exists (it folds U+2212
MINUS SIGN and NBSP before number parsing).

---

## 0. Ground rules (non-negotiable, from existing contracts)

1. **Every verdict is a pure function** of (source, claim, config). Same inputs, same
   verdict, forever. No similarity scores, no thresholds, no ML, no network.
   (`docs/determinism-contract.md`, ADR-0007.)
2. **Canonical JSON has integers only. Floats do not exist in canonical Ethos.**
   (`docs/determinism-contract.md` §2.5.) Part B's arithmetic must be scaled-integer.
3. **Normalization applies to comparison only, never to stored or emitted text.**
   Extracted text is preserved exactly as extracted (c14n rule 4). Part A must not touch
   what is stored, fingerprinted, or echoed — only what is compared.
4. **Fail closed.** Anything unparseable, ambiguous, or out of grammar is a diagnostic,
   never a guess.
5. **No new dependencies.** `deny.toml` + ADR-0004 restrict the dependency allowlist. Both
   parts are implementable with `std` only. In particular: no `unicode-normalization`, no
   `rust_decimal`. Rationale in §A.3 and §B.6.
6. **The default profile does not change.** `VerificationConfig::default_v1()` and all
   existing goldens stay byte-identical. Both features are opt-in via config.
7. **Process**: each part needs (a) a contract doc in `docs/` following the
   `milestone-d-*-contract.md` pattern, (b) an ADR where a standing contract is amended,
   (c) fixtures + goldens + a Make target + a CI guard script, following the
   `evidence-anchor-v1` precedent (`.github/scripts/test_evidence_anchor_v1_contract.py`).

## 0.1 Gate M0: measure before building Part A's rule set

Part A's transform list below is an engineering judgment. Validate it cheaply first:

- Write a ~100-line Python script (suggested: `benchmarks/mismatch_taxonomy.py`, internal
  only) that takes (source JSON, citations JSON) pairs, runs `ethos verify`, and for every
  `mismatch`/`text_mismatch` check diffs the claimed text against the resolved target text
  character-by-character, bucketing the first differing character into: soft hyphen,
  zero-width, ligature, curly quote, dash variant, NBSP, case, real content difference.
- Corpus: the existing foreign fixtures (`fixtures/foreign/opendataloader/real/`) plus any
  internal citation sets you have from LLM runs. More corpus = better signal, but even the
  checked-in fixtures give a baseline.
- **Exit criterion**: the bucket counts either confirm the §A.2 transform list or add/remove
  rules. If "real content difference" dominates and character-class buckets are ~0, Part A
  shrinks or is dropped — do not build normalization the data says isn't needed.

---

# Part A — Canonical Text Normalization v2

## A.1 Problem and current behavior

Matching lives in `crates/ethos-verify/src/lib.rs`:

- `normalize_quote()` (~line 2070, `pub`): normalizes line endings, collapses ASCII
  whitespace runs to one ASCII space, trims. That is the **only** normalization in v1.
- `text_matches()` (~line 2045): applies `TextNormalization::None` (byte-exact) or
  `CollapseWhitespace` (via `normalize_quote`), optional lowercasing when
  `case_sensitive: false`, then `contains` for quotes / `==` for other kinds.
- `text_match_method()` (~line 2034): maps (kind × normalization) to the reported
  `MatchMethod`.
- Config enum: `TextNormalization { None, CollapseWhitespace }` in
  `crates/ethos-core/src/verify_types.rs` (~line 1155). The config schema
  (`schemas/ethos-verification-config.schema.json`) allows exactly `"none"` and
  `"collapse_whitespace"` and documents: *"no Unicode normalization (it would alter
  extraction fidelity)"*.

Consequence: source text containing U+00AD (soft hyphen), U+FB01 (ﬁ), U+201C (curly
quote), U+00A0 (NBSP), or zero-width characters will fail a match against an LLM-quoted
string that renders identically. The check reports `mismatch` / `text_mismatch` — a false
rejection from the user's point of view. This pain is concentrated in **foreign grounding
sources** and **LLM-typed quotes**; the native parser already handles ligature/hyphenation
quirks at extraction (see the layout evaluator's fixture coverage).

## A.2 Design: one new enum variant, one new pure function

Add exactly one normalization mode: `canonical_v2`. It is a **fixed, ordered pipeline of
character-table transforms**, applied to *both* sides of the comparison, in this order:

| # | Rule | Exact characters | Output |
| --- | --- | --- | --- |
| 1 | Line endings | `\r\n`, `\r` | `\n` (reuse existing logic) |
| 2 | Delete invisibles | U+00AD (soft hyphen), U+200B, U+200C, U+200D (zero-widths), U+FEFF (BOM/ZWNBSP), U+2060 (word joiner) | removed |
| 3 | Expand f-ligatures | U+FB00 ﬀ, U+FB01 ﬁ, U+FB02 ﬂ, U+FB03 ﬃ, U+FB04 ﬄ, U+FB05 ﬅ, U+FB06 ﬆ | `ff`, `fi`, `fl`, `ffi`, `ffl`, `st`, `st` |
| 4 | Fold quotes | U+2018, U+2019, U+201A, U+201B → `'`; U+201C, U+201D, U+201E, U+201F → `"` | ASCII quotes |
| 5 | Fold dashes/minus | U+2010, U+2011, U+2012, U+2013, U+2014, U+2015, U+2212 | `-` (U+002D) |
| 6 | Fold spaces | U+00A0 (NBSP), U+202F (narrow NBSP), U+2007 (figure space) | ASCII space |
| 7 | Collapse whitespace + trim | as today | one ASCII space, trimmed |

The whole pipeline is one linear pass over `char`s plus the existing collapse pass. No
Unicode library, no Unicode-version pin — the table above **is** the spec. ~60 lines of
Rust, fully enumerable in test vectors.

**Deliberately excluded (do not add without new evidence):**

- **Full NFKC.** NFKC folds `²`→`2`, `½`→`1/2`, strips superscripts — it *changes numeric
  meaning*, which is fatal for financial documents. It also drags in a Unicode-version
  dependency. The targeted table gives ~all of the benefit with none of the risk.
- **Line-break dehyphenation** (`oper-\nating` → `operating`). It cannot be made
  false-join-free with a character table (`state-of-\nthe-art` → `state-ofthe-art`). The
  native parser dehyphenates at extraction; the LLM never types `-\n`. Only foreign
  sources exposing raw line breaks hit this. **Revisit trigger**: M0 shows a dehyphenation
  bucket > ~2% of mismatches. If it fires, the conservative rule is
  `lowercase '-' '\n' lowercase → join`, shipped as `canonical_v3`, with the compound-word
  failure mode documented.
- **Case folding.** Already exists as the orthogonal `case_sensitive` config flag.
- **Fuzzy/similarity matching.** Never. A Levenshtein threshold ends the "same verdict,
  forever" claim. Everyone else (CiteFix, VeriCite, rapidfuzz pipelines) is fuzzy; the
  enumerated-whitelist approach is the differentiator.

**Decided tradeoffs (surfaced, not hidden):**

1. **Reuse `MatchMethod::NormalizedText` / `NormalizedTextContains`** rather than adding
   `canonical_text_*` variants. Cost: a check alone doesn't say which normalization ran.
   Mitigation: the report already carries `verification_config_sha256`, and the config
   carries the `text_normalization` value — provenance is complete at report level. Benefit:
   zero report-schema change. If auditors later demand per-check visibility, add the
   variant then.
2. **Dash folding is included** although en dash in ranges ("2019–2020") and minus are
   semantically distinct from hyphen. Comparison-only folding cannot corrupt stored
   evidence (ground rule 3), and dash confusion is a top LLM-quoting mismatch source. The
   risk (a claim with a hyphen matching source with an en dash where the difference was
   meaningful) is accepted for v2.
3. **Evidence anchoring is out of scope for this slice.** `ethos evidence anchor`
   hard-gates `expected_text_sha256` on `ethos_collapse_whitespace_v1`
   (`crates/ethos-verify/src/lib.rs` ~line 228; `TextNormalizationProfile` in
   `crates/ethos-core/src/evidence_anchor.rs` ~line 177). Adding
   `ethos_canonical_v2` there is a separate follow-up under the evidence-anchor v1
   contract guard — do not bundle it, the guard has its own CI drift checks.

## A.3 Exact changes (surgical touch list)

1. `crates/ethos-core/src/verify_types.rs`
   - `TextNormalization`: add variant `CanonicalV2` (serde `rename_all = "snake_case"`
     yields `"canonical_v2"` automatically). Update the doc comment that says "v1 has
     exactly these two".
2. `crates/ethos-verify/src/lib.rs`
   - Add `pub fn normalize_canonical_v2(input: &str) -> String` implementing §A.2 rules
     1–7 (call `normalize_quote`-equivalent collapse as the final step; factor the collapse
     loop out rather than duplicating it).
   - `text_matches()`: add the `TextNormalization::CanonicalV2` arm →
     `(normalize_canonical_v2(expected), normalize_canonical_v2(actual))`.
   - `text_match_method()`: `CanonicalV2` maps like `CollapseWhitespace`
     (quotes → `NormalizedTextContains`, others → `NormalizedText`).
3. `schemas/ethos-verification-config.schema.json`
   - `matching.text_normalization` enum: add `"canonical_v2"`. Update the description to
     state: character-table transforms, comparison-only, table lives in the contract doc.
4. `schemas/examples/` — add one example config using `canonical_v2` (do **not** modify
   `verification-config.example.json`; `default_v1()` mirrors it and must stay
   byte-identical).
5. Docs/process
   - New ADR (`docs/decisions/ADR-00XX-canonical-comparison-normalization.md`): amends the
     "no Unicode normalization" stance by scoping it precisely — *stored/emitted/hashed
     text keeps raw fidelity; a versioned, enumerated character table may be applied to
     comparison inputs when the config opts in*. Cite c14n rule 4 as unchanged.
   - New contract doc `docs/normalization-v2-contract.md`: the §A.2 table is the
     normative spec, plus the exclusion list and revisit triggers.
   - One-line update to `docs/determinism-contract.md` pointing at the ADR (comparison vs
     canonicalization distinction).
6. Where the anchor path hard-codes the old profile name in an error message (~line 228),
   leave it — out of scope per tradeoff 3.

No CLI changes. No Python/npm wrapper changes (config is pass-through JSON). No new crates,
no new dependencies.

## A.4 Test plan

- **Unit vectors** (in `ethos-verify` tests): one vector per table row, plus combined
  vectors, e.g. `"ﬁnancial\u{00AD} state\u{2011}ments \u{201C}Q4\u{201D}"` ⇔
  `"financial state-ments \"Q4\""`. Include negative vectors proving exclusions: `œ`, `æ`,
  `²`, `½` are NOT transformed.
- **Property tests** (repo already property-tests c14n): idempotence
  `n(n(x)) == n(x)`; output contains no character from the transform table's input column.
- **Behavioral**: a fixture citation pair that is `mismatch` under `collapse_whitespace`
  and `grounded` under `canonical_v2`; assert the *default* config still reports
  `mismatch` (proves opt-in).
- **Golden stability**: full existing golden suite (`make verify-alpha`) passes unchanged —
  this is the "default profile untouched" proof.
- **Determinism**: byte-identical repeated reports for the new example config (the
  verify-alpha harness already does this pattern).

## A.5 Success criteria

1. `make verify-alpha` green with zero golden diffs.
2. New contract Make target (e.g. `make normalization-v2-contract`) green: vectors,
   idempotence, opt-in behavioral check, byte-identical repeat run.
3. M0 taxonomy re-run over the same corpus with `canonical_v2`: character-class mismatch
   buckets drop to ~0; "real content difference" bucket unchanged (proves no
   over-matching).
4. ADR merged; config schema and contract doc merged in the same PR as the code.

Estimated effort: 2–4 days including ADR, vectors, and CI guard.

---

# Part B — Derived-Value Claims v1 (`derived_value`)

## B.1 Problem and current behavior

If the source says "$10" and "$5" and the answer says "Total is $15", no v1 claim kind can
ground "$15" — the string exists nowhere in the document. Today the honest options are a
failed check or the app-layer `claim_type: synthesis` → `needs_review` lane
(`docs/app-answer-release-contract.md`). Derived numbers are the most common synthesis in
the target domain (finance/compliance), so this is the largest single hole in coverage.

The expansion slot already exists by design: `ClaimKind::{Region, Other}` are reported as
`unsupported_claim_kinds` rather than approximated, and
`docs/milestone-d-claim-kind-boundary-contract.md` exists precisely so claim-kind expansion
is deliberate. This part uses that slot.

## B.2 Design in one paragraph

A `derived_value` claim names an **operation**, a list of **input references** (indexes of
sibling claims in the same citations file), and its claimed **result text**. The verifier
first checks the referenced sibling claims exactly as today (they are ordinary
`value`/`table_cell` claims with their own evidence, crops, and statuses). If every
referenced check grounds, the verifier parses each referenced claim's text and the derived
claim's text under a pinned numeric grammar, re-executes the operation in scaled-integer
arithmetic, and grounds the derived check iff the recomputed result equals the claimed
result under the declared rounding. Nothing probabilistic enters: the certificate is
(grounded inputs + declared operation + re-execution).

Key structural simplifications (these are the design):

- **Inputs must reference claims of kind `value` or `table_cell` only.** Never another
  `derived_value`, never `quote`/`presence`. Consequence: no recursion, no cycle detection,
  no DAG. Derived-of-derived is banned in v1.
- **The claimed result is `claim.text`** — no separate result field. One source of truth,
  parsed by the same grammar as inputs.
- **Because inputs must ground first**, input text ≡ source text under the active matcher.
  Parsing the claimed input text is parsing source-grounded text. This is the trust
  argument; put it verbatim in the contract doc.
- **Three operations only**: `sum` (n-ary, n ≥ 2), `difference` (binary, `a − b`),
  `percent_change` (binary, `(new − old) / old × 100`, rounding declaration required).
  No product, no ratio, no unit conversion, no magnitude words. Every rejected extension
  is listed in §B.8.

## B.3 Claim shape (input JSON)

```json
{
  "kind": "derived_value",
  "text": "$15",
  "derivation": {
    "operation": "sum",
    "inputs": [0, 1],
    "rounding": { "mode": "half_even", "scale": 0 }
  }
}
```

- `derivation.operation`: `"sum" | "difference" | "percent_change"`.
- `derivation.inputs`: array of 0-based indexes into the same citations file's claims
  array. Constraints, all fail-closed: index in range; referenced kind is `value` or
  `table_cell`; no self-reference; no duplicate indexes; `sum` ≥ 2 inputs, `difference`
  and `percent_change` exactly 2 (ordered: `difference` = `inputs[0] − inputs[1]`;
  `percent_change` old = `inputs[0]`, new = `inputs[1]`).
- `derivation.rounding`: optional for `sum`/`difference` (default: exact, no rounding),
  **required** for `percent_change` (exact division rarely terminates).
  `mode`: `"half_up" | "half_even"`. `scale`: integer 0–12 (digits after the decimal
  point in the rounded result).
- `citation`: **omitted.** A derived result has no source location; its provenance is its
  inputs. See §B.6 tradeoff 1 for the code consequence.
- `text`: required, non-blank (extends the existing `requires_text` set).

## B.4 Numeric grammar v1 (pinned, minimal)

Applied to the claim text of each input and of the derived claim, **after** the active
normalization profile (recommend requiring `canonical_v2` in the same config so U+2212 and
NBSP are already folded — enforce with a config-validation error if `derived_value` is
enabled without it; cheaper than duplicating folds in the parser).

```text
numeric   := sign? currency? magnitude percent?
           | '(' currency? magnitude ')' percent?      # parentheses = negative
sign      := '-'
currency  := '$' | '€' | '£'
magnitude := digits | digits frac | grouped | grouped frac
grouped   := d{1,3} (',' d{3})+                        # groups of exactly 3
frac      := '.' d{1,12}
digits    := d{1,15}
percent   := '%'
```

Whitespace between tokens: at most one ASCII space between currency and magnitude;
nothing else. Everything outside this grammar — `5 million`, `5M`, `1.2e6`, `¥`, `USD`,
trailing periods, two decimal points — **fails closed** with
`derivation_unparseable_number`. The grammar is ~40 lines of hand-rolled `std` parsing;
property-test it against a reference regex in tests.

**Units.** The parse records a unit class: one of `currency($)`, `currency(€)`,
`currency(£)`, `percent`, `none`. Rules, all fail-closed with
`derivation_unit_mismatch`:

- `sum`/`difference`: all inputs identical unit class; result unit must equal the inputs'
  unit class **or** be `none` (so "$10 + $5 = 15" grounds, "$10 + 5% = anything" never
  does).
- `percent_change`: both inputs identical unit class (any); result unit must be `percent`
  or `none`.

**Value representation.** Parse to `(sign, unscaled: i128, scale: u8)` meaning
`sign × unscaled × 10^−scale`. 15 integer digits + 12 fraction digits ⇒ unscaled ≤ 10^27,
comfortably inside i128 (max ~1.7 × 10^38). `sum`/`difference` after scale alignment over
≤ `max_checks` (256) inputs peaks around 10^30 — safe. `percent_change` at worst-case
digits and `scale: 12` multiplies up to 10^27 × 100 × 10^13 ≈ 10^42 — **this can
overflow**, so every multiply/add in the module must use `checked_*` arithmetic and map
`None` → `derivation_overflow` (status `error`, never a panic). Do not "prove" overflow
impossible; make it impossible to panic instead. Floats must not appear anywhere in the implementation — grep-guard the new module
for `f32`/`f64` in the contract CI script.

**Arithmetic.**

- `sum`/`difference`: align scales to `max(scale_i)` by multiplying unscaled values by
  powers of 10; add/subtract. If `rounding` present, round to `rounding.scale`; else
  compare exact.
- `percent_change`: exact integer computation of `(new − old) × 100 × 10^(s+1) / old`
  where `s = rounding.scale`, using integer division with remainder; final digit resolved
  by the declared mode. `half_up`: remainder×2 ≥ |divisor| rounds away from zero.
  `half_even`: remainder×2 == |divisor| ties to even last digit, otherwise as `half_up`.
  `old == 0` → `derivation_result_mismatch`? No — fail closed with its own precise label:
  reuse `derivation_unparseable_number`? No. **Decision: `old == 0` fails with
  `invalid_derivation`** (structural impossibility, status `error`).
- Equality: recomputed value equals claimed value after normalizing trailing fractional
  zeros (`15`, `15.0`, `15.00` are equal: compare at common scale). Claimed-text scale
  looser or tighter than rounded scale is fine as long as numeric equality holds at the
  common scale; if `rounding` was declared, the recomputed value is rounded before
  comparison and the claimed value must equal it exactly at common scale.

## B.5 Verifier semantics and failure taxonomy

Evaluation order: two passes over the claims list. Pass 1: every non-derived claim,
exactly the existing loop. Pass 2: derived claims, reading pass-1 `Check` outcomes. Check
ids stay `v%04d` by original input position (the existing invariant "id = input citation
order" is preserved; pass structure only changes evaluation order, not ids or report
order).

The existing early gates in `check_claim()` (`crates/ethos-verify/src/lib.rs` ~line 1045)
apply to derived claims unchanged **except** the `has_locator` gate, which is skipped for
`derived_value` only (§B.6 tradeoff 1): stale fingerprint → `stale`; config not listing
`derived_value` → `unsupported_claim_kind` (identical to today's non-v1 handling — this is
what makes the feature opt-in with zero default-profile change).

New `match_method` value: `derived_recompute` (enum variant `MatchMethod::DerivedRecompute`).

New `CheckReason` variants and their status mapping:

| Failure | Status | Reason |
| --- | --- | --- |
| `derivation` object missing/malformed beyond schema (bad index, self-ref, duplicate ref, wrong referenced kind, wrong arity, missing required rounding, `old == 0`) | `error` | `invalid_derivation` |
| Any referenced check not `grounded` (or itself `semantic_unverified`) | `mismatch` | `derivation_input_not_grounded` |
| Input or result text outside the §B.4 grammar | `mismatch` | `derivation_unparseable_number` |
| Unit-class rule violated | `mismatch` | `derivation_unit_mismatch` |
| i128 overflow at any step | `error` | `derivation_overflow` |
| Recomputed ≠ claimed | `mismatch` | `derivation_result_mismatch` |

Notes, surfaced deliberately:

- `derivation_unparseable_number` uses `mismatch` (not `error`) because it is a property
  of the claim/evidence content, not of the request structure. Debatable; pick once,
  write it in the contract doc, add a golden.
- A grounded derived check sets `semantic_unverified: false` — recomputation is a literal
  check, consistent with the field's documented meaning.
- Report-level effects: grounded derived checks have empty `resolved_element_ids` and no
  `evidence` object, so `EvidenceDispersion.unmapped_grounded_checks` counts them. That is
  accurate (they map to no element) — document it in the contract, change nothing.
- `all_evidence_grounded` and `proof_summary()` need **zero changes**: derived checks are
  ordinary checks. A failed derived check keeps `all_evidence_grounded` false; a grounded
  one is reusable if fresh. The app-answer-release contract keeps working: a claim backed
  by a grounded derived check is a `source_fact`-grade citation for release purposes —
  update that contract's wording to say so explicitly (one paragraph).

## B.6 Exact changes (surgical touch list)

1. `crates/ethos-core/src/verify_types.rs`
   - `ClaimKind`: add `DerivedValue` (serde gives `"derived_value"`).
   - New types: `Derivation { operation: DerivedOperation, inputs: Vec<u32>, rounding: Option<Rounding> }`,
     `DerivedOperation { Sum, Difference, PercentChange }`,
     `Rounding { mode: RoundingMode, scale: u8 }`, `RoundingMode { HalfUp, HalfEven }`.
     All `deny_unknown_fields`, all integers — c14n-safe by construction.
   - `Claim`: add `#[serde(skip_serializing_if = "Option::is_none")] pub derivation: Option<Derivation>`.
   - `Claim.citation`: change to `#[serde(default)] pub citation: Citation`.
     **Tradeoff 1, read this.** Today an omitted `citation` field is a serde
     missing-field error (CLI exit 2). With `#[serde(default)]`, an omitted citation on a
     *non-derived* claim deserializes to the empty `Citation` and fails per-check as
     `error`/`missing_locator` (exit 1 path) instead. That per-check path is already
     reachable today via `"citation": {}` at the Rust layer, so behavior becomes *more*
     consistent, but it is a behavior change for one class of malformed input. Alternative
     considered: `Option<Citation>` — rejected, it ripples through every constructor,
     test, and golden in the workspace for the same net semantics. Record the choice in
     the contract doc and add an explicit test for both paths.
   - `CheckReason`: add the five variants from §B.5. `MatchMethod`: add `DerivedRecompute`.
   - `VerificationConfig` validation: when `claim_kinds` contains `DerivedValue`, require
     `matching.text_normalization == CanonicalV2` (see §B.4) — reject the config otherwise
     with a usage error (exit 2).
2. New module `crates/ethos-verify/src/derived.rs` (~250–350 lines incl. tests):
   grammar parser → `ParsedNumber { neg: bool, unscaled: i128, scale: u8, unit: UnitClass }`,
   alignment/add/sub, percent-change with declared rounding, equality-at-common-scale.
   Pure functions only; no `f32`/`f64`; no allocation-order dependence.
3. `crates/ethos-verify/src/lib.rs`
   - `is_supported_kind`: add `DerivedValue`. `requires_text`: add `DerivedValue`.
   - `verify_citations` loop: split into the two passes (§B.5). Pass 2 calls a new
     `check_derived_claim(claim, sibling_checks, config) -> Check`.
   - `check_claim`: skip `has_locator` gate when `claim.kind == DerivedValue`.
4. `schemas/ethos-citations.schema.json`
   - claim `kind` enum: add `"derived_value"`.
   - add `derivation` property (`additionalProperties: false`, operation/inputs/rounding
     as in §B.3, `inputs` items `type: integer, minimum: 0`).
   - conditionals: `derived_value` requires `text` + `derivation`, forbids `citation`;
     every other kind forbids `derivation` and requires `citation` (preserve today's
     requirement via if/then — do not weaken it for v1 kinds).
5. `schemas/ethos-verification-report.schema.json`
   - claim def: mirror citations changes. `match_method` enum: add `"derived_recompute"`.
     `check_reason` def: add the five new reasons.
   - `schema_version`: reports containing ≥ 1 `derived_value` check emit `"1.2.0"`,
     mirroring the `HARDENED_VERIFICATION_SCHEMA_VERSION = "1.1.0"` precedent
     (`verify_types.rs` line 33). **Open question for the maintainer**: confirm this
     against `docs/v0-2-x-compatibility-policy.md` before implementation — if the policy
     wants a different bump discipline, follow the policy, not this doc.
6. `schemas/ethos-verification-config.schema.json`
   - `claim_kinds` items enum: add `"derived_value"`; update the "only the four v1
     literal kinds" description. This is the deliberate boundary expansion — update
     `docs/milestone-d-claim-kind-boundary-contract.md` in the same PR (that doc exists
     to force exactly this coupling).
7. Fixtures + goldens + CI, following the verify-alpha and evidence-anchor patterns:
   - `examples/verify/native_derived_grounded_citations.json` (+ golden report): $10 and
     $5 as two `value` claims, `sum` → `$15`.
   - One negative fixture + golden per row of the §B.5 failure table (6 fixtures).
   - `percent_change` fixture with `half_even`, scale 0 (e.g. 100 → 118 ⇒ `18%`).
   - Byte-identical repeat-run check; malformed-derivation exit-2 check
     (schema-invalid JSON, e.g. `inputs: [-1]`).
   - New Make target `derived-value-v1-contract` + CI guard script
     `.github/scripts/test_derived_value_v1_contract.py` (copy the evidence-anchor guard's
     structure: schema validation of fixtures, golden equality, float grep-guard on
     `derived.rs`).
8. Docs
   - New contract doc `docs/derived-value-v1-contract.md`: §§B.2–B.5 verbatim as the
     normative spec, plus non-goals (§B.8) and the trust argument.
   - `docs/app-answer-release-contract.md`: one paragraph — a claim whose `check_ids`
     resolve to grounded `derived_recompute` checks counts as citation-grounded for the
     grounding axis; relevance/synthesis axes unchanged.
   - README "Scope and Boundaries" + FAQ: update the sentence *"It does not claim …
     computed-number correctness"* to scope it to what v1 derivation now proves — only
     after the feature ships, and route the wording through the repo's public-claims
     process (`docs/public-boundary-claims.json` and its approval lane; public wording is
     gated in this repo, do not edit casually).

No CLI flag changes (`ethos verify` signature unchanged). No Python/npm wrapper changes
(citations JSON is pass-through). No `GroundingSource` trait changes — derivation never
touches the source directly, only sibling check outcomes. No new dependencies
(hand-rolled scaled-i128 beats `rust_decimal` here: ADR-0004 allowlist friction, and you
need ~5 operations, not a decimal library).

## B.7 Test matrix (minimum to call it done)

| # | Case | Expect |
| --- | --- | --- |
| 1 | `$10` + `$5` = `$15`, inputs grounded | `grounded`, `derived_recompute` |
| 2 | Same, result text `15` (unitless) | `grounded` |
| 3 | Same, result `$14` | `mismatch` / `derivation_result_mismatch` |
| 4 | One input `not_found` | `mismatch` / `derivation_input_not_grounded`; `all_evidence_grounded: false` |
| 5 | Input text `5 million` | `mismatch` / `derivation_unparseable_number` |
| 6 | `$10` + `5%` | `mismatch` / `derivation_unit_mismatch` |
| 7 | `percent_change` 100 → 118, `half_even` scale 0, claim `18%` | `grounded` |
| 8 | `percent_change` without `rounding` | exit 2 (schema) |
| 9 | `inputs: [0]` referencing itself / a `derived_value` / a `quote` | `error` / `invalid_derivation` |
| 10 | `old == 0` in `percent_change` | `error` / `invalid_derivation` |
| 11 | `derived_value` under `default-v1` config | `unsupported_claim_kind` (opt-in proof) |
| 12 | Values at max digits (15 int, 12 frac), sum of 256 inputs | `grounded` or `derivation_overflow`, never panic |
| 13 | `15` vs `15.00` recomputed | `grounded` (scale-normalized equality) |
| 14 | Repeat run byte-identical report | pass |
| 15 | Full existing golden suite | zero diffs |
| 16 | Property: parser accepts iff reference grammar regex accepts (fuzz both) | pass |
| 17 | Rounding unit tests: `half_up`/`half_even` tie cases, negative values | pass |

## B.8 Non-goals for v1 (rejected, with reasons — future work must re-argue, not assume)

- Product/ratio/average operations (average = sum + division: same non-terminating
  problem as ratio; add only with rounding-required semantics, as `percent_change` does).
- Magnitude words/suffixes (`5 million`, `5M`) — cross-magnitude unit errors are the
  most dangerous silent-wrong-answer class in the domain.
- Currency conversion, `USD`/`EUR` codes, `¥`, thousands separators other than `,`
  (European `1.234,56` is a locale trap — fail closed today, design a locale-pinned
  grammar only with evidence of demand).
- Derived-of-derived (chained derivations) — brings DAG validation for marginal value.
- Parsing numbers out of *source* text directly (bypassing input claims) — would silently
  weaken the "inputs are grounded checks" trust argument.
- Table-column aggregation ("sum of column 3") — needs table-shape guarantees the
  `GroundingSource` capability model doesn't promise yet.

## B.9 Success criteria

1. All 17 matrix rows green in CI via `make derived-value-v1-contract`.
2. `make verify-alpha` and the full workspace test suite green with zero golden diffs.
3. Determinism: repeat-run byte-identity for every new fixture report.
4. Contract doc + claim-kind boundary contract update + app-answer-release paragraph
   merged in the same PR as the code (the boundary contract's CI drift checks force this).
5. Float grep-guard on `derived.rs` wired into the contract CI script.
6. A demo: `README`-style 60-second walkthrough — two value claims + one sum, one broken
   sum — runnable without PDFium (native JSON fixtures), added to `docs/demos/`.

Estimated effort: 2–3 weeks including contract docs, negative-fixture goldens, and CI
guard. The arithmetic is the easy half; the fixtures, schemas, and process artifacts are
the real cost — budget accordingly.

---

## Rollout order and compatibility summary

1. **M0** taxonomy script (half a day) → confirms/adjusts Part A's table.
2. **Part A** (2–4 days): ADR + enum variant + pure function + schema enum + vectors.
3. **Part B** (2–3 weeks): contract-first — write `derived-value-v1-contract.md`, get it
   reviewed, then implement to it.

Compatibility invariants across both parts: `default_v1()` byte-identical; all existing
goldens byte-identical; every new behavior reachable only through a config that names it
(`canonical_v2`, `derived_value`); exit-code semantics unchanged (0/1/2); canonical JSON
still contains no floats anywhere.

## Open questions (decide before implementation, do not resolve silently)

1. Report `schema_version` bump discipline for derived checks — confirm against
   `docs/v0-2-x-compatibility-policy.md` (§B.6 item 5).
2. `#[serde(default)]` on `Claim.citation` vs `Option<Citation>` (§B.6 tradeoff 1) —
   maintainer sign-off required since it changes one malformed-input path.
3. Should `derived_value` require `canonical_v2` (this doc's position) or merely
   recommend it? Requiring it couples the features; not requiring it means the number
   grammar must handle U+2212/NBSP itself (duplicated folding). This doc chose coupling
   for less code; reverse it consciously if Part A slips.
4. Whether `unsupported_claim_kinds` reporting (`push_unsupported`) should distinguish
   "kind unknown to this build" from "kind known but not in this config" — today both
   collapse to the same list; derived_value makes the second case common. Cosmetic;
   defaulting to no change.

Refer: https://arxiv.org/pdf/2509.06902 , https://arxiv.org/pdf/2606.24124, https://arxiv.org/pdf/2605.20025, https://arxiv.org/html/2504.15629v2, https://dl.acm.org/doi/epdf/10.1145/3767695.3769505 and https://arxiv.org/html/2508.15396v1
Sources: Proof-Carrying Numbers · VeryTrace · AutoResearchClaw · CiteFix · VeriCite · Evidence-based text generation survey ·