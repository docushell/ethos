# Release Operator Runbook

Ethos is public beta evaluation for source, Rust crate, Python wheel, macOS arm64 CLI artifact,
Linux x64 CLI artifact, and npm `@docushell/ethos-pdf@0.1.1` surfaces. This runbook describes the
operator checks required before any public promotion. It does not authorize new GitHub Release
artifacts, new package publication, hosted surfaces, production positioning, Windows packaged
artifacts, bundled project-maintained PDFium builds, or benchmark reports.

## Who Can Release

The operator is the person or team explicitly named by the approval record for the target release
surface. Repository write access or workflow access alone is not release authority. If no approval
record names an operator or approving group, treat the workflow output as draft evidence only.

## Current Draft Workflow

1. Confirm the intended source commit and release scope against `docs/public-release-checklist.md`.
2. Run the release workflow from GitHub Actions or by pushing a `v*` test tag.
3. Wait for the `preflight` job to pass.
4. Download the `ethos-cli-draft-*` workflow artifacts.
5. For each archive, verify the adjacent `.sha256` file.
6. Inspect each `*.inventory.json` and confirm it is marked draft/blocked, matches the archive
   filename, and records the expected platform target.
7. Treat the downloaded archives as CI evidence only unless a separate approval record authorizes
   the exact public release artifact, version, checksum, and wording.

## Patch 0.1.1 Artifact Refresh Prep

The source tree now prepares `0.1.1` package and CLI version surfaces. The checked-in npm vendor
manifest and vendor binaries must not be refreshed from local builds or unapproved archives. Before
publishing or attaching any `0.1.1` artifact, the operator must:

1. Produce macOS arm64 and Linux x64 draft CLI archives from the release workflow at the reviewed
   source commit.
2. Verify each archive with `smoke_release_cli_artifact.py` and require `ethos 0.1.1` in the smoke
   evidence.
3. Record each archive SHA256 and inventory in a dedicated approval record.
4. Update `packages/npm/ethos-pdf/vendor/manifest.json` only from approved `0.1.1` archive
   checksums.
5. Run `npm run prepare:vendor -- <release-artifact-dir>` only against the approved archives.
6. Treat npm publication as blocked until an approval record binds the refreshed vendor checksums,
   package version, artifact source commit, and exact public wording.

## Local Checks Before Any Future Promotion

```sh
make release-advisory
make third-party-license-manifest
make release-notice-draft
python3 .github/scripts/validate_release_artifact_inventory.py target/release-artifacts/*.inventory.json
```

## Promotion Gate

Before creating or updating any public GitHub Release, package registry entry, or public release
notes for `v0.1.1`, the operator needs an approval record that binds:

- exact source commit;
- artifact names and platform targets;
- SHA256 checksums;
- license/NOTICE bundle;
- PDFium setup or bundling posture;
- exact public wording.

If any item is missing, stop at draft-artifact evidence and do not publish.
