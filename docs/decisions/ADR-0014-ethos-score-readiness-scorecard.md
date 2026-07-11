# ADR-0014: Ethos Readiness Report (V1), Quality Score Deferred (V2)

- Status: Proposed
- Date: 2026-07-10
- Decider: Gate Zero decider
- Governs: `ethos eval readiness`, `schemas/ethos-readiness-report.schema.json`, the readiness/quality
  boundary between Ethos and app layers (DocuShell), and the staged Ethos-score release plan (V1–V4).

## Context

`ethos verify` proves whether citations and evidence bind to a source (ADR-0012 added the
lower-level `ethos evidence anchor` primitive). But "verification happened" is not "this output is
safe to use downstream." A parse job can complete while its output is still weak for RAG, verified
citation display, Evidence Chat, or customer APIs — stale fingerprints, partial anchors, missing
table capability, unknown coordinate origins.

Today that readiness judgment is either skipped or reimplemented ad hoc by each consumer. The
derivation itself is small — a pure function over existing reports — so the question is not
capability but **ownership**: if every consumer reimplements "what does `capability_limited` plus
partial anchors mean for release," interpretations drift, and drift in a trust layer defeats its
purpose. DocuShell needs a gate between "parse job done" and "usable for verified citations."
Foreign-parser users (OpenDataLoader, Docling, Unstructured, LiteParse, Marker, MinerU, PyMuPDF)
need the same signal when their output enters through `GroundingSource`.

### Prior art: SCORE / unstructured-eval-metrics

The SCORE framework (arXiv:2509.19345) and `Unstructured-IO/unstructured-eval-metrics` are
**reference-based, offline benchmark** tooling: every metric (Adjusted NED, TokensFound/Added,
table content/index accuracy, element consistency) requires labeled ground truth, fuzzy alignment,
and spatial tolerance, and answers "how good is this parser against a curated corpus." What this
ADR ships is the opposite quadrant: **reference-free, runtime, deterministic** — "is this specific
job's output safe to use," with no ground truth available or needed. SCORE is prior art for the V2
parser-quality *metric definitions only*; its Python research-harness architecture (fuzzy scoring,
CSV aggregation, corpus annotation formats) is explicitly **not** adopted — tolerant scoring would
import non-determinism into the trust layer (ADR-0012, ADR-0004). One SCORE lesson *is* adopted:
aggregate numbers distort behavior and get misused, so V1 ships no numeric scores at all.

### Constraints

- `docs/public-boundary-claims.json` blocks public parser-quality, table-quality, and benchmark
  claims. Anything shipped now must not create leaderboard or superiority language — or numbers
  that can be averaged into one.
- Ethos core stays deterministic, offline, and dependency-restricted (ADR-0004); no OCR/VLM
  dependencies.
- ADR-0012 requires `ethos verify` semantics and goldens to remain unchanged, and defines a
  fail-closed per-ref rollup ordering the readiness layer must never relax.

## Decision

Release a deterministic, schema-versioned **readiness report** — not a semantic truth metric, not a
parser leaderboard, and in V1 **not a numeric score**. The layer split stays intact:

- `ethos verify` / `ethos evidence anchor`: prove whether evidence binds to a source.
- `ethos eval readiness`: summarize whether that output is ready for downstream use.
- App layers (DocuShell) own answer relevance, synthesis quality, release policy, and UX.

**Naming.** The V1 artifact is `ethos.readiness_report.v1` via `ethos eval readiness`. The name
"score" is reserved for V2's parser-quality mode, which actually scores against goldens. This
avoids implying quality measurement and avoids confusion with the SCORE framework.

### V1 surface (target: `0.4.0`, next minor — not a patch)

```bash
ethos eval readiness \
  --verification-report verification_report.json \
  --evidence-anchor-report evidence_anchor_report.json \
  --out ethos_readiness_report.json
```

At least one input report is required. When both are supplied, merge semantics are fixed and
minimal: **worst state wins; limitations are unioned**. Nothing cleverer.

The report (`schema_version: 1.0.0`, `mode: live_readiness`) contains:

- `release_state: pass | review | fail` — gate-driven, never average-driven.
- `hard_gates` — named gate results (fingerprint freshness, evidence binding, required
  capabilities).
- `counts` — integers only (checks total/grounded, anchors total/bound, stale, mismatch,
  not_found, unsupported, capability_limited).
- `limitations` — enumerated reason codes; **required and non-empty whenever
  `release_state != pass`**, so a `review` is always actionable, never a junk drawer.
- `policy` — the gate-policy identity applied (see below).
- `grounding` — parser identity and capabilities echoed from the input reports.
- `recommended_action`.

**No dimensional float scores in V1** (`evidence_readiness: 0.92` and similar are removed from the
earlier draft). Enums and integers cannot be averaged into a leaderboard number; this deletes the
benchmark-misuse vector rather than disclaiming it. Numeric scores return in V2, measured against
goldens, where they are meaningful.

**Gate policy is versioned configuration, not hardcoded.** Ethos ships a default policy; the report
embeds `policy.id` and `policy.hash`. Consumers such as DocuShell may supply a stricter or looser
policy without forking derivation semantics; determinism is preserved because the policy identity
is part of the artifact. Default policy:

- **fail**: stale fingerprint; missing required source fingerprint; any required evidence check
  stale; **any required evidence of an unsupported kind**; malformed or schema-invalid input.
- **review**: `capability_limited` present; unsupported *non-required* evidence kinds; partial
  anchors; missing table capability for table evidence; unknown coordinate origin; evidence bound
  but `semantic_unverified` appears.
- **pass**: fingerprint fresh; all supported required evidence grounded/bound; no unsupported
  required evidence; no capability limitation affecting requested evidence.

**Severity invariant (contract-tested):** the readiness derivation is never more permissive than
the ADR-0012 per-ref rollup beneath it. Unsupported required evidence kinds therefore inherit
ADR-0012's fail-closed, first-order handling (this resolves the earlier draft's placement of
unsupported kinds in `review`). No custom policy may weaken a `fail` produced by this invariant.

**Implementation:** a single pure function in `ethos-core` over existing `VerificationReport` and
`EvidenceAnchorReport`; `ethos eval readiness` in `ethos-cli` is a thin wrapper. Input validation
before derivation; exit 2 on malformed input; JSON output only; stable field ordering. No new
dependencies, no changes to `ethos-verify`. Golden examples for pass/review/fail; schema and
contract tests; `docs/ethos-readiness-v1-contract.md`; README section framing readiness as
"safe to use," never "parser is good" or "answer is correct." Python wrapper
`EthosCli.readiness(...)` if low-cost; npm via the vendored CLI binary only.

The report must answer: fingerprint present and fresh; required evidence bound; stale / missing /
mismatched / unsupported / capability-blocked citations; parser capability sufficiency; usability
tier; limitations to surface. It must **not** answer: semantic correctness of an answer, arithmetic
truth, summary relevance, parser superiority, or OCR/VLM quality.

### Who consumes it, and how

- **DocuShell**: per-job gate — `pass` shows verified-citation readiness, `review` serves parsed
  artifacts with citations marked partial (reason codes surfaced), `fail` blocks verified-citation
  display and routes to reprocessing/support. Evidence Chat caps retrieval scope on non-pass.
  Job metadata carries the summary, not raw reports.
- **RAG/pipeline builders on foreign parsers** (via `GroundingSource` adapters): use/review/block
  routing per document instead of trusting all parser JSON equally.
- **Parser maintainers**: capability diagnostics (no fingerprint, no tables, unknown coordinate
  origin) with no benchmark corpus required.
- **CI**: parser upgrades that flip fixtures `pass` → `review` fail the build.

### Staged releases

| Release | Scope | Gate to enter |
| --- | --- | --- |
| V1 (`0.4.0`) | Readiness report from existing reports; no numeric scores | This ADR accepted |
| V1.1 | DocuShell integration pack: metadata mapping, Evidence Chat gating, UI labels, API docs, acceptance test. Integration/UX only — no new metrics | V1 landed with stable examples; separate DocuShell approval lane |
| V2 | Parser-quality mode (`ethos eval score --mode parser_quality`): SCORE-derived metric math (adjusted CCT, tokens found/added, reading order, element alignment/consistency, table detection F1, cell/index accuracy, optional TEDS) reimplemented deterministically in Rust with a versioned normalization profile — SCORE's metric *definitions*, not its architecture | Golden corpus, versioned scoring config, deterministic normalization profile |
| V3 | Ecosystem: `ethos-bench`, Promptfoo/DeepEval envelopes, CI regression examples, parser adapters, redacted output mode | V2 stable |
| V4 | Public benchmark-ready output | Frozen corpus, pinned competitors, cross-platform evidence, approval records |

Until V4, readiness/score output is engineering and product-readiness evidence, never marketing
proof. Releasing V1 does **not** approve DocuShell production integration; that remains a separate
approval/closeout lane.

## Options Considered

### Option A: Deterministic readiness report, gates + counts only, policy as config (chosen)

Pros: canonical, versioned interpretation of Ethos's own reports; zero new dependencies; pure
derivation is trivially deterministic and testable; no numbers to misquote as benchmarks; policy
override without semantic forking; stays inside the public-claims boundary.
Cons: consumers wanting one quality number get a three-state decision instead; a new public schema
contract must be maintained under the `contract-change` process.

### Option B: Ship SCORE-style parser-quality metrics now (or adopt unstructured-eval-metrics architecture)

Pros: richer signal; established prior art.
Cons: requires golden corpora and normalization profiles that don't exist; SCORE's fuzzy alignment
and spatial tolerance are deliberately non-deterministic — incompatible with the trust layer; its
Python harness, corpus annotation formats, and CSV aggregation solve a benchmark problem, not a
runtime one; invites the parser-comparison claims the public boundary blocks. Deferred to V2
(metric math only), not rejected.

### Option C: Keep readiness logic inside DocuShell / publish only a derivation spec

Pros: no new Ethos surface; near-zero cost if DocuShell is the sole consumer forever.
Cons: every consumer reimplements gate logic inconsistently; foreign-parser users get nothing;
readiness rules drift from the report semantics they depend on. Rejected — but this remains the
honest fallback if no second consumer materializes.

### Option D: Extend `ethos verify` output instead of a new command

Pros: one artifact, no new namespace.
Cons: violates ADR-0012 (verify semantics and goldens unchanged); conflates proof with policy;
verify-only consumers pay for gate-policy churn. Rejected.

### Option E: Earlier draft — scorecard with dimensional floats and hardcoded gates, named "score"

Pros: richer-looking report.
Cons: floats invite averaging into a de facto leaderboard number; "score" implies quality and
collides with the SCORE framework; hardcoded policy guarantees a second, disagreeing policy layer
in DocuShell; unsupported-kind handling contradicted ADR-0012. Superseded by Option A's trims.

## Trade-off Analysis

The core trade-off is **narrow-and-honest now vs. rich-and-risky later**. A report of enums and
integers cannot be quoted as a benchmark, which is exactly the property the public-claims boundary
needs; the cost is that "readiness" will disappoint anyone expecting quality measurement, so V2
carries that expectation instead. Gate-driven `release_state` costs nuance (one stale fingerprint
fails a job with 500 bound anchors) but keeps the trust boundary fail-closed, consistent with
ADR-0012. Policy-as-config costs a small amount of schema surface (`policy` block) but removes the
worst structural risk — two disagreeing policy layers. The residual unavoidable risk is
misreading: `release_state: pass` will be read as "the document is good" by some consumers no
matter the wording; mandatory reason codes and the non-claims documentation reduce but cannot
eliminate this.

## Consequences

- Downstream consumers get a three-state release decision with mandatory reason codes; DocuShell
  gates verified-citation display and Evidence Chat scope on it.
- A new public schema contract exists under the `contract-change` process; gate-policy changes are
  versioned config events with report-embedded identity, not silent behavior drift.
- `ethos verify` and `ethos evidence anchor` behavior, semantics, and goldens remain unchanged; the
  severity invariant is contract-tested against ADR-0012's rollup.
- "Readiness" language enters public docs; wording lands in `docs/public-boundary-claims.json`
  surfaces without quality or comparison claims. No numeric values exist to leak into comparisons.
- V2 inherits a stable envelope and the reserved "score" name.
- What gets harder: resisting pressure to add a single number back into V1, and keeping the
  DocuShell integration lane from smuggling production claims into the Ethos release.
- Revisit: default policy thresholds after real DocuShell usage; whether `review` needs sub-states
  beyond reason codes; V2 entry once a golden corpus exists; Option C fallback if no second
  consumer appears by V1.1.

## Action Items

1. [ ] Accept this ADR; record decider sign-off.
2. [ ] Add `ethos.readiness_report.v1` schema (gates, counts, limitations, policy identity — no
       float scores) + pass/review/fail examples under `schemas/`.
3. [ ] Implement the pure derivation in `ethos-core` and `ethos eval readiness` in `ethos-cli`
       (policy config loading, input validation, exit 2 on malformed input, stable JSON).
4. [ ] Contract-test the severity invariant against ADR-0012 rollup ordering, including
       "unsupported required evidence → fail" and "zero evidence refs → review, not pass";
       merge tests for worst-state-wins + limitation union; no changes to `ethos verify`.
5. [ ] Write `docs/ethos-readiness-v1-contract.md`; README experimental section; release-notes
       non-claims; update `docs/public-boundary-claims.json`.
6. [ ] Ship in `0.4.0`; Python `EthosCli.readiness(...)` if low-cost; npm via vendored CLI only.
7. [ ] Open V1.1 DocuShell integration lane as a separate approval item; record V2 entry gates
       (golden corpus, normalization profile) as its own backlog item.
