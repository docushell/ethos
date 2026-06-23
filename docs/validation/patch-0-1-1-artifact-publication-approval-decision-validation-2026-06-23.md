# Patch 0.1.1 Artifact Publication Approval Decision Validation - 2026-06-23

Validated source HEAD before this record: `7df928c`.

Patch 0.1.1 artifact publication approval decision source commit:
`7df928cd453decd273a5e83fc2b2191a0edf654e`.

Patch 0.1.1 artifact publication approval decision source tree:
`6b9ebbb7087604367f53022406c50a4ec8509992`.

Status: **patch 0.1.1 artifact publication approval decision recorded; operator upload remains pending**

This record accepts the exact patch `0.1.1` GitHub Release artifact publication request after
decider approval. It approves only attaching the exact evidenced macOS arm64 and Linux x64 CLI
artifact assets below to GitHub Release tag `v0.1.1` for public beta evaluation. It does not upload
artifacts, refresh npm vendor binaries, publish npm, change PDFium posture, approve hosted
surfaces, approve production positioning, approve Windows packaged artifacts, approve bundled
project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or approve public
benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: patch `0.1.1` GitHub Release artifact publication
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/patch-0-1-1-artifact-publication-approval-request-validation-2026-06-23.md`
- Artifact evidence record:
  `docs/validation/patch-0-1-1-release-artifact-evidence-validation-2026-06-23.md`
- Release workflow run: `https://github.com/docushell/ethos/actions/runs/28040466463`

## Exact Decision Fields

- Decision: accept the exact patch `0.1.1` artifact publication request.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-23.
- Exact GitHub Release tag accepted by this decision: `v0.1.1`.
- Exact workflow run accepted by this decision:
  `https://github.com/docushell/ethos/actions/runs/28040466463`.
- Exact workflow head SHA accepted by this decision:
  `3cbbb8f8b8195fe0f964ab4e5d2bf0458770ad11`.

macOS arm64 assets accepted by this decision:

- `ethos-macos-arm64.tar.gz`
- `ethos-macos-arm64.tar.gz.sha256`
- `ethos-macos-arm64.inventory.json`
- `ethos-macos-arm64.smoke.json`
- archive SHA256:

```text
eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88
```

Linux x64 assets accepted by this decision:

- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`
- archive SHA256:

```text
842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0
```

Exact CLI smoke accepted by this decision: `ethos 0.1.1` for both accepted platform artifacts.

Exact PDFium boundary accepted by this decision: caller-provided PDFium only through
`ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build is approved.

## Approved Operator Action

After this decision record is merged and the validation commands below pass on the merged source,
an operator may attach only the exact accepted asset names above to GitHub Release tag `v0.1.1`.

This decision does not itself upload artifacts. Publication remains an explicit later operator
action.

## Approved Public Wording

After the exact assets above are attached to GitHub Release tag `v0.1.1`, the bounded public
release wording may remain:

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

## Required Operator Pre-Upload Checks

Before uploading, the operator must verify the downloaded workflow artifacts:

```sh
shasum -a 256 ethos-macos-arm64.tar.gz
cat ethos-macos-arm64.tar.gz.sha256
cat ethos-macos-arm64.inventory.json
cat ethos-macos-arm64.smoke.json
shasum -a 256 ethos-linux-x64.tar.gz
cat ethos-linux-x64.tar.gz.sha256
cat ethos-linux-x64.inventory.json
cat ethos-linux-x64.smoke.json
python3 .github/scripts/test_patch_0_1_1_artifact_publication_approval_decision.py
make release-candidate-prep PYTHON=python3
git diff --check
```

The operator must stop if artifact names, checksums, version output, PDFium posture, license and
NOTICE inclusion, or approved public wording differ from this decision record.

## Retained Blockers

- `packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed until after the approved
  GitHub Release assets are attached and publication closeout evidence is recorded.
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

## Evidence Bound To This Decision

- Decider decision supplied: Approved.
- Exact approval supplied by operator:
  `Yes, I approve publishing the exact v0.1.1 macOS arm64 and Linux x64 CLI artifacts named and
  checksummed in the merged approval-request record.`
- `python3 .github/scripts/test_patch_0_1_1_artifact_publication_approval_request.py` passed on
  merged `main`.
- `python3 .github/scripts/test_release_candidate_prep.py` passed on merged `main`.
- `make light-check PYTHON=python3` passed on merged `main`.
- `make release-candidate-prep PYTHON=python3` passed on merged `main`.

## Non-Actions

- This decision record does not upload GitHub Release assets.
- This decision record does not refresh npm vendor binaries.
- This decision record does not publish npm.
- This decision record does not change PDFium posture.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Result

The exact patch `0.1.1` GitHub Release artifact publication decision is accepted. Actual asset
upload remains a separate operator action requiring the exact bounded assets approved here, final
pre-upload checks, and post-upload closeout evidence.
