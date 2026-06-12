# Benchmark Plan

Benchmark credibility is part of the product (PRD §11). Numbers leave the harness only as
JSON with reproduction commands; published tables are one-command reproducible. WS-HARNESS
owns the implementation (`benchmarks/harness/`).

## Categories (PRD §11.1)

- **Performance:** pages/sec, docs/sec, cold start, warm start, peak memory, install size,
  p50/p95/p99 latency. Install-size method includes PDFium payload + font assets (G2 basis).
- **Quality (from Milestone B):** text fidelity, reading order, heading hierarchy, table
  detection F1, table structure accuracy, cell text accuracy, bbox IoU, chunk usefulness.
- **Trust:** citation verification accuracy, hidden-text exclusion, fingerprint stability,
  stable failure behavior, warning precision/recall on security fixtures.

## Gate Zero protocol (week 4, days 18–20 — plan §6.4)

Frozen inputs: `benchmarks/gate-zero/manifest.json` (corpus + hardware) and
`benchmarks/competitors.lock.json` (pinned versions). Harness host must match the frozen
hardware profile. Outputs: `benchmarks/results/gate-zero/{g1,g2,g3}.json` + repro commands +
hardware attestation → decider → ADR-0005.

- **G1 throughput:** ≥ max(120 pages/sec p50, 2× in-harness-remeasured ODL) on the
  `born_digital` subset, single core, independently on every recorded performance host. The
  120 pps floor can never be lowered by a slow ODL remeasurement. EdgeParse/LiteParse numbers
  recorded as context, non-gating.
- **G2 footprint:** installed bytes on disk (CLI + dynamic libs + PDFium + schemas + fonts,
  no network) ≤ 30 MB. V8/XFA-enabled builds auto-fail. The measured Ethos/OpenDataLoader
  ratio is recorded for claims; ≤ 1/10 measured ODL is a claim threshold, not a hard gate
  (ADR-0008).
- **G3 determinism:** byte-identical canonical payload + equal fingerprints across Gate Zero
  platforms (macOS arm64 + Linux x64 minimum) on the full frozen manifest.

## Rules (PRD §11.3 — enforced by CI grep-gate and review)

No "#1" or superlative claims. Publish commands, environment, hardware, versions, failures.
Separate born-digital deterministic results from OCR/VLM results; label model tier vs
deterministic tier in every table; label publisher-owned suites (ParseBench is
LlamaIndex/run-llama-owned; OmniDocBench is neutral/community; Ethos fixtures are never
presented as neutral). Pin competitor versions and dates; re-run after major releases;
competitor crashes are data, not patch targets. No public speed claims until G1 passes
(including any approved retry). No laptop-only numbers in marketing: known-host numbers are
paired with third-party reproducible cloud-runner numbers at Milestone E.

## Fixture/golden test strategy (plan §10)

- **Golden fixtures per stage:** extraction spans → layout graphs → tables → regions →
  chunks. Fixtures-first: heuristic PRs carry their fixtures.
- **Property tests:** c14n idempotence; profile round-trip; quantization stability
  (parse == parse(parse)); chunker never splits table rows (C); no runtime field in payload.
- **Determinism:** same-platform double-parse byte-diff per PR; cross-platform nightly;
  verification-report determinism.
- **Security suite:** hidden/off-page/white-on-white, annotations/actions/attachments/
  scripts/links — assert surfacing + default-chunk exclusion; track warning precision/recall.
- **Failure suite:** corrupt, encrypted, password, image-only, oversized, rotated — stable
  PRD §10 codes, never panics; cargo-fuzz on `ethos-pdf` ingest from Milestone B.
- **Compat:** schema round-trip on CLI/Python stable surfaces; Node beta + MCP experimental
  smoke tests, clearly labeled.

## Cadence

`bench.yml` weekly + on tags; internal snapshots A–D (dev-labeled, never public claims);
the public report exists only at Milestone E with the claim audit.
