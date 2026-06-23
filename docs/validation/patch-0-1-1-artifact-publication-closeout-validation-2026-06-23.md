# Patch 0.1.1 Artifact Publication Closeout Validation - 2026-06-23

Validated source HEAD before this record: `5231b56`.

Patch 0.1.1 artifact publication closeout source commit:
`5231b56383afbc08c874325a7f47d6ae90e60a24`.

Patch 0.1.1 artifact publication closeout source tree:
`b0e5d2e5ac534facf9bd78a580366aab1995f0e1`.

Status: **patch 0.1.1 GitHub Release artifact publication complete**

This record closes the bounded GitHub Release artifact publication action for patch `0.1.1`. It
records that GitHub Release tag `v0.1.1` exists at the approved source commit, contains the exact
approved macOS arm64 and Linux x64 CLI artifact assets, and preserves the approved public-beta
wording. It does not refresh npm vendor binaries, publish npm, change PDFium posture, approve hosted
surfaces, approve production positioning, approve Windows packaged artifacts, approve bundled
project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or approve public
benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- GitHub Release tag: `v0.1.1`
- GitHub Release URL: `https://github.com/docushell/ethos/releases/tag/v0.1.1`
- Approval decision record:
  `docs/validation/patch-0-1-1-artifact-publication-approval-decision-validation-2026-06-23.md`
- Approval request record:
  `docs/validation/patch-0-1-1-artifact-publication-approval-request-validation-2026-06-23.md`
- Artifact evidence record:
  `docs/validation/patch-0-1-1-release-artifact-evidence-validation-2026-06-23.md`

## Release Metadata Verified

- Release tag: `v0.1.1`
- Release name: `Release v0.1.1`
- Release draft status: `false`
- Release prerelease status: `false`
- Tag target: `5231b56383afbc08c874325a7f47d6ae90e60a24`

## Published Assets Verified

The published release asset list contains exactly these approved assets:

- `ethos-macos-arm64.tar.gz`
- `ethos-macos-arm64.tar.gz.sha256`
- `ethos-macos-arm64.inventory.json`
- `ethos-macos-arm64.smoke.json`
- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`

The published archive SHA256 values match the approval decision:

```text
eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88  ethos-macos-arm64.tar.gz
842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0  ethos-linux-x64.tar.gz
```

The GitHub Release asset API also reported matching archive digests:

```text
sha256:eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88  ethos-macos-arm64.tar.gz
sha256:842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0  ethos-linux-x64.tar.gz
```

The downloaded published sidecars verified as follows:

- `ethos-macos-arm64.inventory.json`: schema `ethos.release_artifact_inventory.v1`, target
  `macos-arm64`, status `draft_not_release_ready`, publication `blocked`.
- `ethos-macos-arm64.smoke.json`: schema `ethos.release_artifact_smoke.v1`, target
  `macos-arm64`, version `ethos 0.1.1`.
- `ethos-linux-x64.inventory.json`: schema `ethos.release_artifact_inventory.v1`, target
  `linux-x64`, status `draft_not_release_ready`, publication `blocked`.
- `ethos-linux-x64.smoke.json`: schema `ethos.release_artifact_smoke.v1`, target `linux-x64`,
  version `ethos 0.1.1`.

Both published archives contain the expected payload:

- `LICENSE`
- `NOTICE`
- `ethos`
- `pdfium-manual-setup.md`

The published macOS arm64 CLI smoke run reported:

```text
ethos 0.1.1
```

`ethos doctor` preserved the caller-provided PDFium setup-warning posture when
`ETHOS_PDFIUM_LIBRARY_PATH` was unset.

## Published Release Wording Verified

The GitHub Release body contains the approved bounded public-beta wording:

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

The release body includes the approved archive SHA256 values shown above.

## Verification Commands

Operator verification completed:

```sh
gh release view v0.1.1 --repo docushell/ethos --json tagName,name,isDraft,isPrerelease,url,assets
git ls-remote --tags origin v0.1.1
gh release view v0.1.1 --repo docushell/ethos --json targetCommitish,tagName,url
gh release view v0.1.1 --repo docushell/ethos --json body --jq .body
gh release download v0.1.1 --repo docushell/ethos --dir /tmp/ethos-v0.1.1-published-assets
python3 .github/scripts/validate_release_artifact_inventory.py \
  /tmp/ethos-v0.1.1-published-assets/ethos-macos-arm64.inventory.json \
  /tmp/ethos-v0.1.1-published-assets/ethos-linux-x64.inventory.json
```

## Retained Blockers

- `packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed until after this closeout
  record is merged and a dedicated npm vendor refresh lane starts.
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

Patch `0.1.1` GitHub Release artifact publication is complete for the exact approved macOS arm64
and Linux x64 CLI artifacts. The next release lane may prepare npm vendor refresh from these
published assets, but only after this closeout record is merged and the dedicated vendor-refresh
guards pass.
