# Patch 0.1.1 Release Artifact Evidence Validation - 2026-06-23

## Purpose

Record the green release workflow run and downloaded draft CLI artifact evidence for patch `0.1.1`.
This record is evidence only. It does not approve attaching GitHub Release assets, publishing npm,
refreshing checked-in npm vendor binaries, changing PDFium posture, or opening any new public
surface.

Validated source HEAD before this record: `3cbbb8f`.
Artifact-evidence source commit: `3cbbb8f8b8195fe0f964ab4e5d2bf0458770ad11`.
Artifact-evidence source tree: `2791caca23354bd11974f391fa94c5de02df91a4`.

## Workflow Run

Workflow:

```text
.github/workflows/release.yml
```

Run:

```text
https://github.com/docushell/ethos/actions/runs/28040466463
```

Observed run metadata:

- status: `completed`
- conclusion: `success`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `3cbbb8f8b8195fe0f964ab4e5d2bf0458770ad11`
- created at: `2026-06-23T16:23:14Z`
- updated at: `2026-06-23T16:24:57Z`

## Downloaded Artifact Set

The operator downloaded these workflow artifacts from run `28040466463`:

- `ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz`
- `ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz.sha256`
- `ethos-cli-draft-macos-arm64/ethos-macos-arm64.inventory.json`
- `ethos-cli-draft-macos-arm64/ethos-macos-arm64.smoke.json`
- `ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz`
- `ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz.sha256`
- `ethos-cli-draft-linux-x64/ethos-linux-x64.inventory.json`
- `ethos-cli-draft-linux-x64/ethos-linux-x64.smoke.json`

## Artifact Evidence

macOS arm64:

- archive: `ethos-macos-arm64.tar.gz`
- SHA256: `eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88`
- inventory schema: `ethos.release_artifact_inventory.v1`
- inventory target: `macos-arm64`
- inventory status: `draft_not_release_ready`
- inventory publication: `blocked`
- smoke schema: `ethos.release_artifact_smoke.v1`
- smoke target: `macos-arm64`
- smoke version stdout: `ethos 0.1.1`

Linux x64:

- archive: `ethos-linux-x64.tar.gz`
- SHA256: `842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0`
- inventory schema: `ethos.release_artifact_inventory.v1`
- inventory target: `linux-x64`
- inventory status: `draft_not_release_ready`
- inventory publication: `blocked`
- smoke schema: `ethos.release_artifact_smoke.v1`
- smoke target: `linux-x64`
- smoke version stdout: `ethos 0.1.1`

The downloaded checksum sidecars matched the recomputed archive SHA256 values above. The inventory
sidecars passed `validate_release_artifact_inventory.py`.

## Retained Blockers

- GitHub Release publication remains blocked until a dedicated decider record approves exact
  artifact names, checksums, source commit, and public wording.
- `packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed until a decider approves the
  exact `0.1.1` artifact checksums.
- npm publication remains blocked until the checked-in vendor payload is refreshed from approved
  artifacts and a dedicated npm approval record passes.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The patch `0.1.1` release workflow produced smoke-validated macOS arm64 and Linux x64 draft CLI
artifacts from `main`. This is sufficient evidence for decider review of the artifact/vendor
refresh lane, but it is not itself a publish approval.
