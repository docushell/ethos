# Claim-Language Scan - 2026-06-15

## Purpose

Record the public-release claim-language scan required by `docs/public-release-checklist.md`.

This scan checks whether public-facing repository text overclaims Ethos parser quality, speed,
footprint, table extraction, heading extraction, semantic truth checking, benchmark standing, or
rendered-crop determinism.

## Status

Status: **completed for current tree**.

The scan supports the current allowed public wording:

```text
Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
native Ethos JSON and supported foreign parser outputs.
```

It does not make Ethos public-release ready. Remaining blockers are tracked in
`docs/public-release-checklist.md`.

## Scope

Scanned paths:

- `README.md`
- `docs/`
- `examples/`
- `benchmarks/`
- `schemas/`
- `fixtures/`
- Rust crate sources and tests under `crates/`

Search themes:

- parser speed and "fastest parser" claims;
- production-grade table or heading extraction claims;
- benchmark winner or leaderboard claims;
- 10x/superlative footprint claims;
- semantic truth-checking claims;
- cross-platform rendered-crop byte-identity claims;
- release-ready or public-release-ready claims.

## Changes Made

`README.md` and the README-positioning block in `docs/ethos-product-requirements.md` were
adjusted to remove unsupported speed/footprint/table wording:

- `fast, deterministic, runtime-light PDF parser` became `deterministic PDF parser`;
- the top-level artifact list no longer says the parser turns PDFs into `tables`;
- `One small native parser` became `One native parser`;
- Release 1 scope now says `conservative structure` instead of naming headings/lists/tables in
  a way that could read as current release-readiness.

## Remaining Matches

Remaining matches are intentional guardrails or validation records:

- rendered-crop validation records explicitly say cross-platform rendered crop byte identity
  failed or is not claimed;
- benchmark ownership docs explicitly ban parser-speed, production-readiness, and
  rendered-crop byte-identity claims;
- the public-release checklist explicitly says Ethos is not public-release ready and lists
  blocked claim categories;
- Gate Zero evidence tests assert that summaries do not claim Ethos is the fastest parser;
- PRD competitor and Gate Zero sections discuss speed/footprint only as competitive context or
  internal decision criteria, not as current Ethos public claims;
- PRD scope statements say `ethos-rag` does not own semantic truth scoring;
- source comments and fixture docs use ordinary words such as `small` for implementation or
  fixture size, not product footprint claims.

## Result

Current public-facing language passes this claim scan for pre-alpha publication, subject to the
remaining public-release checklist gates. Re-run this scan before any public push if README,
docs, examples, benchmark summaries, or generated evidence change.
