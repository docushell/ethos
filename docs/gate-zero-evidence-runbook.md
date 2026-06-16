# Gate Zero Evidence Runbook

This runbook starts the controlled evidence path required before Ethos can move beyond
source-only pre-alpha language.

It does not approve benchmark publication, package publication, release artifacts, or launch
claims. Generated Gate Zero result files and evidence bundles belong in the sibling
`ethos-bench` repository, not in this repository.

## Current Boundary

Use this repository for:

- frozen corpus, manifest, gates, profiles, source code, and implementation-facing harness code;
- local preflight checks before controlled host runs;
- human-readable status and validation records.

Use `../ethos-bench` for:

- generated `g1.json`, `g2.json`, and `g3.json` result files;
- per-gate evidence bundles and checksum manifests;
- public-safe derived benchmark evidence.

Do not commit generated Gate Zero output under `ethos/benchmarks/results/gate-zero/`.

## Required Inputs

Before running host evidence:

- `benchmarks/gate-zero/manifest.json` is frozen and signed.
- `benchmarks/competitors.lock.json` pins the selected direct competitor artifacts.
- `benchmarks/gate-zero/gates.json` records the active G2/G3 definitions.
- The host is one of the recorded Gate Zero hosts in the manifest.
- The matching pinned PDFium runtime and artifact are available for the host.
- The sibling `ethos-bench` checkout is clean and ready to receive generated evidence.

## Preflight

Run from the Ethos checkout:

```bash
git switch main
git pull --ff-only
make verify-alpha PYTHON=/private/tmp/ethos-jsonschema-venv/bin/python
python3 .github/scripts/readiness_gate.py gate-zero
python3 .github/scripts/gate_zero_evidence_preflight.py prepare --ethos-bench ../ethos-bench
make -C benchmarks/harness smoke
make -C benchmarks/harness test
git status --short --branch
```

The `readiness_gate.py gate-zero` command only checks that frozen inputs and pins are present. It
does not produce benchmark results.
The `gate_zero_evidence_preflight.py prepare` command checks that generated Gate Zero outputs are
not present in this repository and that the sibling `ethos-bench` checkout is ready to receive
controlled-run output.

## Per-Host G1 Result

Set these paths for each controlled host:

```bash
export ETHOS_REPO=/path/to/ethos
export ETHOS_BENCH=/path/to/ethos-bench
export GATE_ZERO_PLATFORM=macos-arm64   # or linux-x64
export ETHOS_PDFIUM_LIBRARY_PATH=/path/to/libpdfium
export ETHOS_PDFIUM_VERSION=chromium/7881
export ETHOS_PDFIUM_ARTIFACT_PATH=/path/to/pdfium-artifact
```

Then run the G1 result into `ethos-bench`:

```bash
make -C "$ETHOS_REPO/benchmarks/harness" gate-zero-results \
  GATE_ZERO_PLATFORM="$GATE_ZERO_PLATFORM" \
  GATE_ZERO_RESULT_REPORT="$ETHOS_BENCH/benchmarks/results/gate-zero/$GATE_ZERO_PLATFORM/g1.json" \
  OPENDATALOADER_COMMAND=/path/to/opendataloader-pdf \
  OPENDATALOADER_ARTIFACT=/path/to/opendataloader_pdf-2.4.7-py3-none-any.whl \
  OPENDATALOADER_INSTALL_PATH=/path/to/opendataloader-install
```

Add other competitor command/artifact/install variables only when those pinned adapters are ready
for the controlled run. Missing competitor evidence must remain explicit; do not backfill it from
ad hoc terminal output.

## Per-Host G2 Result

Run G2 into `ethos-bench` with explicit footprint inputs:

```bash
make -C "$ETHOS_REPO/benchmarks/harness" gate-zero-g2 \
  GATE_ZERO_PLATFORM="$GATE_ZERO_PLATFORM" \
  GATE_ZERO_G2_RESULT_REPORT="$ETHOS_BENCH/benchmarks/results/gate-zero/$GATE_ZERO_PLATFORM/g2.json" \
  'GATE_ZERO_ETHOS_FOOTPRINT=ethos-cli=target/release/ethos pdfium-library=/path/to/libpdfium' \
  OPENDATALOADER_INSTALL_PATH=/path/to/opendataloader-install \
  OPENDATALOADER_ARTIFACT=/path/to/opendataloader_pdf-2.4.7-py3-none-any.whl \
  GATE_ZERO_PDFIUM_LIBRARY_PATH=/path/to/libpdfium \
  GATE_ZERO_PDFIUM_ARTIFACT=/path/to/pdfium-artifact
```

G2 must cite the active gate definition hash through the runner output. Do not replace the full
base-parser artifact set with a narrower measurement.

## Cross-Host G3 Result

After both platform-scoped G1 files exist in `ethos-bench`, generate G3:

```bash
make -C "$ETHOS_REPO/benchmarks/harness" gate-zero-g3 \
  GATE_ZERO_G3_RESULT_REPORT="$ETHOS_BENCH/benchmarks/results/gate-zero/g3.json" \
  GATE_ZERO_G3_PLATFORM_RESULTS="macos-arm64=$ETHOS_BENCH/benchmarks/results/gate-zero/macos-arm64/g1.json linux-x64=$ETHOS_BENCH/benchmarks/results/gate-zero/linux-x64/g1.json"
```

G3 cannot pass from one host. Diagnostic geometry experiments can explain failures, but they are
not Gate Zero pass/fail results.

## Evidence Bundles

For each saved result file, build an evidence bundle in `ethos-bench`:

```bash
make -C "$ETHOS_REPO/benchmarks/harness" gate-zero-evidence \
  GATE_ZERO_PLATFORM="$GATE_ZERO_PLATFORM" \
  GATE_ZERO_GATE=g1 \
  GATE_ZERO_RESULT_REPORT="$ETHOS_BENCH/benchmarks/results/gate-zero/$GATE_ZERO_PLATFORM/g1.json" \
  GATE_ZERO_EVIDENCE_OUT_ROOT="$ETHOS_BENCH/benchmarks/results/gate-zero" \
  GATE_ZERO_REPRODUCTION_COMMAND_FILE=/path/to/reproduction-command.txt \
  GATE_ZERO_REPRODUCTION_ENV_FILE=/path/to/reproduction-env.json \
  GATE_ZERO_BENCHMARK_COMMIT="$(git -C "$ETHOS_REPO" rev-parse HEAD)"
```

Repeat for G2 and G3 with the matching gate/result paths. Reproduction command and environment
sidecars must describe the actual controlled run; placeholders keep the bundle incomplete.
For the cross-host G3 bundle, use `GATE_ZERO_PLATFORM=cross-platform` and
`GATE_ZERO_GATE=g3`.

## Decision Step

ADR-0005 is accepted for the current internal Gate Zero decision. For a future amendment or
successor decision, update the decision record only after:

- required G1 files exist for both recorded hosts;
- required G2 files exist for both recorded hosts;
- G3 has compared the required hosts;
- evidence bundles exist for the source result files;
- the decider has reviewed the result JSON and reproduction sidecars.

Before amending the decision record, run:

```bash
python3 .github/scripts/gate_zero_evidence_preflight.py decision --ethos-bench ../ethos-bench
```

This checks the expected `ethos-bench` result paths, timestamped evidence bundle sidecars,
complete reproduction environments, and bundle checksum manifests. It does not decide whether
Gate Zero passes.

Even after ADR-0005 acceptance, public language remains:

```text
Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
native Ethos JSON and supported foreign parser outputs.
```

ADR-0005 authorizes internal Milestone B continuation only. It does not authorize public benchmark
reports, releases, packages, production positioning, or unsupported result wording.
