# Patch 0.1.1 Artifact Publication Approval Request Validation - 2026-06-23

## Purpose

Record the exact patch `0.1.1` GitHub Release artifact publication approval request for decider
review. This record does not publish artifacts, refresh npm vendor binaries, publish npm, change
PDFium posture, or open any new public surface.

Validated source HEAD before this record: `bfc6dc1`.
Artifact-publication-request source commit: `bfc6dc11801af4416b6760c1bbd216c5a1a22809`.
Artifact-publication-request source tree: `41680dbd9d506df280a5ca246c4225db6a047be7`.

## Evidence Inputs

- Release workflow: `.github/workflows/release.yml`
- Workflow run: `https://github.com/docushell/ethos/actions/runs/28040466463`
- Evidence record:
  `docs/validation/patch-0-1-1-release-artifact-evidence-validation-2026-06-23.md`
- Run status: `completed`
- Run conclusion: `success`
- Run event: `workflow_dispatch`
- Run branch: `main`
- Run head SHA: `3cbbb8f8b8195fe0f964ab4e5d2bf0458770ad11`

## Requested Artifact Evaluation Surface

The decider is asked to approve only attaching these exact draft CLI artifacts and sidecars to
GitHub Release tag `v0.1.1` for public beta evaluation:

macOS arm64:

- `ethos-macos-arm64.tar.gz`
- `ethos-macos-arm64.tar.gz.sha256`
- `ethos-macos-arm64.inventory.json`
- `ethos-macos-arm64.smoke.json`
- archive SHA256:

```text
eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88
```

Linux x64:

- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`
- archive SHA256:

```text
842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0
```

Both smoke sidecars report `ethos 0.1.1`. Both inventory sidecars report
`draft_not_release_ready` and `publication: blocked`; those sidecars are evidence inputs for
decider review and are not themselves publication approvals.

## Requested Public Wording

If the decider approves the exact artifacts above, the bounded public release wording may remain:

> Ethos is public beta for source, Rust crate, Python wheel, macOS arm64 CLI artifact, Linux x64
> CLI artifact, and npm `@docushell/ethos-pdf` evaluation. It verifies whether AI citations are
> grounded in document evidence across native Ethos JSON and supported foreign parser outputs.
> Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available on crates.io
> at `0.1.1` for evaluation. The Python `ethos-pdf` wheel, npm `@docushell/ethos-pdf@0.1.1`
> package, and macOS arm64/Linux x64 CLI artifacts are available for evaluation with
> caller-provided PDFium. Hosted surfaces, production positioning, Windows packaged artifacts,
> bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports,
> public benchmark claims, and speed, footprint, parser-quality, table-quality, or production
> claims remain blocked.

Any broader public wording requires a separate decider record.

## Retained Blockers

- GitHub Release artifact publication remains blocked until the decider explicitly approves the
  exact artifact names, checksums, source binding, and public wording in this request.
- `packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed until after artifact
  publication is explicitly approved and completed.
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

## Required Operator Checks Before Approval

Before approval, the operator should verify the downloaded workflow artifacts:

```sh
shasum -a 256 ethos-macos-arm64.tar.gz
cat ethos-macos-arm64.tar.gz.sha256
cat ethos-macos-arm64.inventory.json
cat ethos-macos-arm64.smoke.json
shasum -a 256 ethos-linux-x64.tar.gz
cat ethos-linux-x64.tar.gz.sha256
cat ethos-linux-x64.inventory.json
cat ethos-linux-x64.smoke.json
```

If any output changes artifact names, checksums, version output, inventory publication status,
PDFium posture, license and NOTICE inclusion, or approved public wording, publication must stop
until a refreshed evidence record and approval request pass.

## Result

The patch `0.1.1` artifact publication approval request is ready for decider review. Publication
remains blocked until explicit approval is recorded.
