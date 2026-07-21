# v0.5.0 npm B Freeze Runbook

This runbook applies only after core commit A has been frozen and both `ethos-full` target
smoke records have been retained. It does not authorize publication or change the currently
published npm `0.4.0` payload.

## Required inputs

The operator must retain, for each `macos-arm64` and `linux-x64` target:

- the `ethos-full-0.5.0-<target>.tar.gz` archive;
- its canonical `<sha256>  <archive-name>` checksum file;
- the `ethos.full_candidate_inventory.v1` inventory; and
- the `ethos.full_candidate_smoke.v1` target-smoke record.

Create an evidence manifest with schema `ethos.npm_b_activation_evidence.v1`, the frozen
core-A commit ID, `core_version: "0.5.0"`, and safe relative paths to those four records per
target. Keep the manifest beside the evidence files.

## Refresh and verify B

1. Refresh the npm package metadata, lockfile, generated types, and vendor payload from the
   retained core-A release assets. Do not rebuild the core binaries during this step.
2. Run the package tests and consumer compilation:

   ```sh
   npm test --prefix packages/npm/ethos-pdf
   ```

3. Validate the A-to-B binding before staging:

   ```sh
   python3 .github/scripts/validate_npm_b_activation.py \
     --evidence /absolute/path/to/evidence.json \
     --package-root packages/npm/ethos-pdf
   ```

The validator must pass with package metadata and `vendor/manifest.json` at `0.5.0`. If it
fails, keep the published `0.4.0` payload and do not publish.

## Freeze and closeout

Record the B commit and tree, rerun the unaffected candidate reproducibility checks, run the
performance gate against the retained A and B bytes, and complete the external registry/GitHub
closeout only after all accepted hashes match. Publication remains an operator action; this
repository must not claim it from a local dry run.
