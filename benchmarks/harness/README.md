# Benchmarks Harness

WS-HARNESS owns one-command reproduction and JSON-only reporting. Public numbers must come
from harness JSON, not prose or ad hoc terminal output.

## Fixture Baseline

The first runner is fixture-scoped:

```sh
make -C benchmarks/harness fixtures
```

It builds `target/release/ethos`, parses every entry in `fixtures/manifest.json`, checks
successful fixtures against their `extraction.json` and `layout.json` goldens, checks failure
fixtures against their stable error envelopes, and writes:

```text
benchmarks/results/fixtures/baseline.json
```

The report schema is `ethos-harness-fixtures-v1`. It includes fixture pass/fail status,
fingerprints, payload hashes, p50/p95/p99 parse timing, and the pinned PDFium environment
used for the run.

## PDFium Environment

The runner uses the public `ethos doc parse` CLI, so successful fixtures require the pinned
PDFium profile environment:

```sh
export ETHOS_PDFIUM_LIBRARY_PATH=/tmp/ethos-pdfium/lib/libpdfium.dylib
export ETHOS_PDFIUM_VERSION=chromium/7881
export ETHOS_PDFIUM_ARTIFACT_PATH=/tmp/ethos-pdfium-mac-arm64.tgz
```

Use the matching artifact and runtime library path from
`profiles/ethos-deterministic-v1.json` on other platforms.

## Gate Zero Readiness

`make -C benchmarks/harness bench` is fail-closed. It first writes:

```text
benchmarks/results/gate-zero/readiness.json
```

The report schema is `ethos-gate-zero-readiness-v1`. It records the exact manifest and
competitor-lock hashes plus actionable blockers. The target exits non-zero until:

- `benchmarks/gate-zero/manifest.json` is frozen and signed.
- `benchmarks/competitors.lock.json` pins ODL, EdgeParse, LiteParse, and PyMuPDF4LLM.
- Gate Zero hosts provide the pinned PDFium runtime.

When readiness is green, the target still exits non-zero until the G1/G2/G3 measurement runner is
implemented. This prevents `bench` from accidentally emitting fixture-baseline evidence as public
benchmark evidence.

Until then, fixture baseline JSON is engineering evidence only. It is not a public benchmark
claim.
