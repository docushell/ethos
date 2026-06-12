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

## Gate Zero G2/G3 Definitions

G2 and G3 are defined before they are runnable:

```text
benchmarks/gate-zero/gates.json
benchmarks/gate-zero/gates.schema.json
```

`gates.json` encodes the existing PRD/implementation-plan contract:

- G2 is the base-parser installed footprint gate: `<= 30 MB decimal` and `<= 1/10`
  in-harness measured OpenDataLoader footprint, with V8/XFA-enabled PDFium builds auto-failing.
- G3 is the cross-platform determinism gate: byte-identical canonical payload and equal
  document fingerprints across at least `macos-arm64` and `linux-x64` on the full frozen
  manifest. A macOS-only result cannot pass G3 by itself.

Do not emit `g2.json` or `g3.json` until the runner cites the definition file hash, manifest hash,
competitor-lock hash, and required evidence listed in `gates.json`.

## OpenDataLoader PDF Adapter

The Gate Zero runner can execute the pinned OpenDataLoader PDF wheel recorded in
`benchmarks/competitors.lock.json`. Use the wheel entrypoint, not a mutable source checkout helper:

```sh
python3.12 -m venv /tmp/ethos-odl-wheel-venv312
/tmp/ethos-odl-wheel-venv312/bin/pip install --no-index /tmp/opendataloader_pdf-2.4.7-py3-none-any.whl

env \
  ETHOS_PDFIUM_LIBRARY_PATH=/tmp/ethos-pdfium/lib/libpdfium.dylib \
  ETHOS_PDFIUM_VERSION=chromium/7881 \
  ETHOS_PDFIUM_ARTIFACT_PATH=/tmp/ethos-pdfium-mac-arm64.tgz \
  make -C benchmarks/harness gate-zero-results \
    OPENDATALOADER_COMMAND=/tmp/ethos-odl-wheel-venv312/bin/opendataloader-pdf \
    OPENDATALOADER_ARTIFACT=/tmp/opendataloader_pdf-2.4.7-py3-none-any.whl \
    OPENDATALOADER_INSTALL_PATH=/tmp/ethos-odl-wheel-venv312
```

The adapter runs:

```text
<opendataloader-command> --quiet --format json --image-output external --reading-order xycut --table-method default --threads 1 --output-dir <output-dir> <input-pdf>
```

The result file keeps Ethos runs at top level and records OpenDataLoader evidence under
`competitors.runs.opendataloader-pdf`.

## Gate Zero Evidence Bundle

After a platform-scoped G1 result is saved, build the sidecar evidence bundle from that JSON:

```sh
make -C benchmarks/harness gate-zero-evidence \
  GATE_ZERO_PLATFORM=macos-arm64 \
  GATE_ZERO_GATE=g1 \
  GATE_ZERO_REPRODUCTION_COMMAND_FILE=/tmp/ethos-g1-reproduction-command.txt \
  GATE_ZERO_BENCHMARK_COMMIT=c68389c28535bbab74a1efbe5bd923c8ff4ec341
```

The reproduction command file must contain the exact command used to create the source
`g1.json`. The evidence builder writes a timestamped bundle under:

```text
benchmarks/results/gate-zero/<platform>/evidence/<gate>/<timestamp>/
```

Each bundle contains the byte-preserved raw result archive, reproduction command,
host attestation, human-readable summary, checksum manifest, and checksum-manifest
digest. The digest is not a public-key signature.
