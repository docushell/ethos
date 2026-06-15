# Public Evidence Safety Scan - 2026-06-15

## Purpose

Record the public-release evidence safety scan required by `docs/public-release-checklist.md`.

This scan checks the tracked repository for public-unsafe generated evidence, especially private
usernames, private hostnames, one-off absolute paths, and generated Gate Zero outputs that belong
in `ethos-bench`.

## Status

Status: **completed for current tree**.

This scan does not make Ethos public-release ready. Remaining blockers are tracked in
`docs/public-release-checklist.md`.

## Scope

Scanned tracked and local evidence-relevant paths:

- `benchmarks/results/`
- `benchmarks/harness/README.md`
- `fixtures/`
- `docs/validation/`
- generated-result filename patterns such as `g1.json`, `g2.json`, `g3.json`,
  `gate-zero*.json`, and `result*.json`

Search themes:

- private local usernames and hostnames;
- local machine-specific absolute paths;
- generated Gate Zero result JSON in the main repository;
- generated diagnostics or result files that should live in `ethos-bench`.

## Findings

- No tracked generated Gate Zero result JSON is present in `benchmarks/results/gate-zero/`.
  That directory now contains only `README.md`.
- `benchmarks/results/fixtures/baseline.json` exists locally as an ignored fixture run artifact
  on this workstation, but it is not tracked by Git. `.gitignore` already excludes
  `benchmarks/results/fixtures/*.json`.
- No tracked evidence file exposed private workstation usernames, private hostnames, or
  workstation-specific absolute paths.
- Benchmark harness docs contained macOS-specific temporary-directory example paths. Those were
  replaced with generic `/tmp/...` example paths.
- Governance docs and Gate Zero manifests intentionally contain the project decider name and
  benchmark hardware identifiers. Those are release governance facts, not generated-evidence
  leaks.

## Result

The current tracked tree passes the public evidence safety scan for this gate. Generated Gate Zero
outputs must continue to be written to `ethos-bench`, not committed under `benchmarks/results/`
in this repository.

Re-run this scan before public push if benchmark outputs, validation records, fixture baselines,
or reproduction sidecars change.
