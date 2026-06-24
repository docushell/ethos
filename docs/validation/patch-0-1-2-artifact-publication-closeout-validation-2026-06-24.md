# Patch 0.1.2 Artifact Publication Closeout Validation - 2026-06-24

Validated source HEAD before this record: `6cc9a93`.

Patch 0.1.2 artifact publication closeout source commit:
`6cc9a933a7eb2684f8f2ccc78039ed5440e6af08`.

Patch 0.1.2 artifact publication closeout source tree:
`84712214e430977f857a7f5d0c4440523c86a2a4`.

Status: **patch 0.1.2 GitHub Release artifact publication complete**

This record closes the bounded GitHub Release artifact publication action for patch `0.1.2`. It
records that GitHub Release tag `v0.1.2` exists at the approved source commit, contains the exact
approved macOS arm64 and Linux x64 CLI artifact assets, and preserves the approved bounded public
wording. It does not publish registries, refresh npm vendor binaries, publish npm, change public
installation wording, change PDFium posture, approve hosted surfaces, approve production
positioning, approve Windows packaged artifacts, approve bundled project-maintained PDFium builds,
approve `ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- GitHub Release tag: `v0.1.2`
- GitHub Release URL: `https://github.com/docushell/ethos/releases/tag/v0.1.2`
- Approval decision record:
  `docs/validation/patch-0-1-2-artifact-publication-approval-decision-validation-2026-06-24.md`
- Approval request record:
  `docs/validation/patch-0-1-2-artifact-publication-approval-request-validation-2026-06-24.md`
- Artifact evidence record:
  `docs/validation/patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md`

## Release Metadata Verified

- Release tag: `v0.1.2`
- Release name: `Release v0.1.2`
- Release draft status: `false`
- Release prerelease status: `false`
- Release targetCommitish display value: `main`
- Tag target: `6cc9a933a7eb2684f8f2ccc78039ed5440e6af08`

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
7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c  ethos-macos-arm64.tar.gz
4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456  ethos-linux-x64.tar.gz
```

The GitHub Release asset API also reported matching archive digests:

```text
sha256:7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c  ethos-macos-arm64.tar.gz
sha256:4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456  ethos-linux-x64.tar.gz
```

The published sidecar asset API digests matched the downloaded sidecars:

```text
sha256:c349a9fa6e6312b36cceeca6d0c9463ab1683123c52d41936a4da32dcadf3a9b  ethos-macos-arm64.tar.gz.sha256
sha256:4cea4d57838681886aa9108d2292b0ae310f71947c130b985020f53272a20cd5  ethos-macos-arm64.inventory.json
sha256:9474a5412082dd4cecefe60843e3fb796c2ae0d79952e85e53400430d362dfd2  ethos-macos-arm64.smoke.json
sha256:652c421a035d231e8f009b8b84cca03b90b5ebbb51beca193b2f002ade565596  ethos-linux-x64.tar.gz.sha256
sha256:86c80e97bce5c51f0b7249c3aed383afd6e1d8bdb35dc4a2e8d32b355f1fadea  ethos-linux-x64.inventory.json
sha256:71a92d59f24e31ee653933adf71e43de3a833e0933fc07d6a865ba07bbc5e8a1  ethos-linux-x64.smoke.json
```

The downloaded published sidecars verified as follows:

- `ethos-macos-arm64.inventory.json`: schema `ethos.release_artifact_inventory.v1`, target
  `macos-arm64`, status `draft_not_release_ready`, publication `blocked`.
- `ethos-macos-arm64.smoke.json`: schema `ethos.release_artifact_smoke.v1`, target
  `macos-arm64`, version `ethos 0.1.2`.
- `ethos-linux-x64.inventory.json`: schema `ethos.release_artifact_inventory.v1`, target
  `linux-x64`, status `draft_not_release_ready`, publication `blocked`.
- `ethos-linux-x64.smoke.json`: schema `ethos.release_artifact_smoke.v1`, target `linux-x64`,
  version `ethos 0.1.2`.

Both published archives contain the expected payload:

- `LICENSE`
- `NOTICE`
- `ethos`
- `pdfium-manual-setup.md`

The published sidecars show missing-PDFium guidance preserved the caller-provided PDFium posture
through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Published Release Wording Verified

The GitHub Release body contains the approved bounded public-beta wording:

> Ethos patch `0.1.2` CLI artifacts for macOS arm64 and Linux x64 are requested for public beta
> evaluation with caller-provided PDFium. Rust crates, the Python wheel, npm package install
> instructions, and public README installation examples remain on the published `0.1.1` baseline
> until separate registry, npm vendor refresh, and public wording closeout records pass. Hosted
> surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
> builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, and speed,
> footprint, parser-quality, table-quality, or production claims remain blocked.

The release body includes the approved archive SHA256 values shown above.

## Verification Commands

Operator verification completed:

```sh
gh release view v0.1.2 --repo docushell/ethos --json tagName,name,isDraft,isPrerelease,url,assets
git ls-remote --tags origin refs/tags/v0.1.2
gh release view v0.1.2 --repo docushell/ethos --json targetCommitish,tagName,url
gh release view v0.1.2 --repo docushell/ethos --json body --jq .body
gh release download v0.1.2 --repo docushell/ethos --dir /tmp/ethos-v0.1.2-published-assets
python3 .github/scripts/validate_release_artifact_inventory.py \
  /tmp/ethos-v0.1.2-published-assets/ethos-macos-arm64.inventory.json \
  /tmp/ethos-v0.1.2-published-assets/ethos-linux-x64.inventory.json
shasum -a 256 /tmp/ethos-v0.1.2-published-assets/ethos-macos-arm64.tar.gz
cat /tmp/ethos-v0.1.2-published-assets/ethos-macos-arm64.tar.gz.sha256
cat /tmp/ethos-v0.1.2-published-assets/ethos-macos-arm64.inventory.json
cat /tmp/ethos-v0.1.2-published-assets/ethos-macos-arm64.smoke.json
shasum -a 256 /tmp/ethos-v0.1.2-published-assets/ethos-linux-x64.tar.gz
cat /tmp/ethos-v0.1.2-published-assets/ethos-linux-x64.tar.gz.sha256
cat /tmp/ethos-v0.1.2-published-assets/ethos-linux-x64.inventory.json
cat /tmp/ethos-v0.1.2-published-assets/ethos-linux-x64.smoke.json
```

## Retained Blockers

- `packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed until after this closeout
  record is merged and a dedicated npm vendor refresh lane starts.
- The public install baseline remains `0.1.1`.
- README installation examples remain unchanged.
- Registry publication remains blocked.
- npm vendor refresh remains blocked.
- npm publication remains blocked.
- Public installation wording remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Result

Patch `0.1.2` GitHub Release artifact publication is complete for the exact approved macOS arm64
and Linux x64 CLI artifacts. The public install baseline remains `0.1.1`, and the next release lane
may prepare npm vendor refresh from these published assets only after this closeout record is merged
and dedicated vendor-refresh guards pass.
