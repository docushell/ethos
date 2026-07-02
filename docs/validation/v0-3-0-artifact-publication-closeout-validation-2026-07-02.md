# v0.3.0 Artifact Publication Closeout Validation - 2026-07-02

Validated source HEAD before this record: `4aa8b8b`.

v0.3.0 artifact publication closeout source commit:
`4aa8b8bf25685f9cd6691669ea791a38ecc1a84a`.

v0.3.0 artifact publication closeout source tree:
`150a7262277e810c5b6253a9b7f403c0d286a191`.

Status: **v0.3.0 GitHub Release artifact publication complete**

This record closes the bounded GitHub Release artifact publication action for `v0.3.0`. It records
that GitHub Release tag `v0.3.0` exists at the approved source commit, contains the exact approved
macOS arm64 and Linux x64 CLI artifact assets, and preserves the approved bounded release wording.
It does not refresh npm vendor binaries, publish npm, change public installation wording, change
PDFium posture, approve package tags, approve hosted surfaces, approve production positioning,
approve Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve
DocuShell integration, approve `ethos-doc`, approve `ethos-rag`, or approve public benchmark
reports or claims.

## Subject

- Repository: `docushell/ethos`
- GitHub Release tag: `v0.3.0`
- GitHub Release URL: `https://github.com/docushell/ethos/releases/tag/v0.3.0`
- Approval decision record:
  `docs/validation/v0-3-0-artifact-publication-approval-decision-validation-2026-07-01.md`
- Approval request record:
  `docs/validation/v0-3-0-artifact-publication-approval-request-validation-2026-07-01.md`
- Artifact evidence record:
  `docs/validation/v0-3-0-draft-artifact-evidence-validation-2026-07-01.md`
- Artifact workflow run: `https://github.com/docushell/ethos/actions/runs/28531102130`
- Approval decision source commit accepted before publication:
  `a20b42a7927052f727fcaaa585a7a050aec02abe`
- Approval request source commit accepted before publication:
  `d6496e82e613e653edc197db4cf4153271d131dc`
- Artifact workflow source commit accepted before publication:
  `7287358475a96e827d536f0d2d250a1c2961ba84`

## Release Metadata Verified

- Release tag: `v0.3.0`
- Release name: `Release v0.3.0`
- Release draft status: `false`
- Release prerelease status: `false`
- Release targetCommitish display value: `4aa8b8bf25685f9cd6691669ea791a38ecc1a84a`
- Tag target: `4aa8b8bf25685f9cd6691669ea791a38ecc1a84a`

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
efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96  ethos-macos-arm64.tar.gz
b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405  ethos-linux-x64.tar.gz
```

The GitHub Release asset API also reported matching archive digests:

```text
sha256:efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96  ethos-macos-arm64.tar.gz
sha256:b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405  ethos-linux-x64.tar.gz
```

The published sidecar asset API digests matched the downloaded sidecars:

```text
sha256:f86a3d1b556e4e0f601c4e9cf06917b522f900717ab1d2e33eb46faf46bf81e9  ethos-macos-arm64.tar.gz.sha256
sha256:13e944876ad34ecbb07dc66ff8887135472f17f2baf72864a5edbae21a335845  ethos-macos-arm64.inventory.json
sha256:78ad54e090e661ff1e192dd471ac49190a1afb94c33405d7b74312d8724a3608  ethos-macos-arm64.smoke.json
sha256:ecd6785bc8a8c952df31ef99d4e2f612c4a28590f9bdaa67c22eae09775411ed  ethos-linux-x64.tar.gz.sha256
sha256:cbfe3c0494043f3a4fa3b0d300f6bd8cec222dd24a93a7282b8c0cabf42eec2a  ethos-linux-x64.inventory.json
sha256:1198fde1293ae32eb1b016b789e191d0ef93a86e3e9bc0c91cf3719fe1917e34  ethos-linux-x64.smoke.json
```

The downloaded published sidecars verified as follows:

- `ethos-macos-arm64.inventory.json`: schema `ethos.release_artifact_inventory.v1`, target
  `macos-arm64`, status `draft_not_release_ready`, publication `blocked`.
- `ethos-macos-arm64.smoke.json`: schema `ethos.release_artifact_smoke.v1`, target
  `macos-arm64`, version `ethos 0.3.0`.
- `ethos-linux-x64.inventory.json`: schema `ethos.release_artifact_inventory.v1`, target
  `linux-x64`, status `draft_not_release_ready`, publication `blocked`.
- `ethos-linux-x64.smoke.json`: schema `ethos.release_artifact_smoke.v1`, target `linux-x64`,
  version `ethos 0.3.0`.

Both published archives contain the expected payload:

- `LICENSE`
- `NOTICE`
- `ethos`
- `pdfium-manual-setup.md`

The published sidecars show missing-PDFium guidance preserved the caller-provided PDFium posture
through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Published Release Wording Verified

The GitHub Release body contains the approved bounded wording:

> Ethos v0.3.0 CLI artifacts for macOS arm64 and Linux x64 are requested for GitHub Release
> evaluation with caller-provided PDFium. Rust crates `ethos-doc-core`, `ethos-verify`, and
> `ethos-pdf` at `0.3.0`, plus the Python `ethos-pdf` wheel at `0.3.0`, are already live. npm
> alignment/publication, public `0.3.0` install wording, release/package tags, DocuShell
> integration, hosted surfaces, production positioning, Windows packaged artifacts, bundled
> project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public
> benchmark claims, and speed, footprint, parser-quality, table-quality, or production claims
> remain blocked.

The release body includes the approved archive SHA256 values shown above and preserves:

```text
PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.
```

## Verification Commands

Operator and local verification completed:

```sh
gh release view v0.3.0 --repo docushell/ethos --json tagName,name,isDraft,isPrerelease,url,targetCommitish
gh release view v0.3.0 --repo docushell/ethos --json tagName,name,isDraft,isPrerelease,url,targetCommitish,assets,body
git ls-remote --tags origin refs/tags/v0.3.0
gh release download v0.3.0 --repo docushell/ethos --dir target/v0-3-published-assets-check
python3 .github/scripts/validate_release_artifact_inventory.py \
  target/v0-3-published-assets-check/ethos-macos-arm64.inventory.json \
  target/v0-3-published-assets-check/ethos-linux-x64.inventory.json
shasum -a 256 target/v0-3-published-assets-check/ethos-macos-arm64.tar.gz
cat target/v0-3-published-assets-check/ethos-macos-arm64.tar.gz.sha256
cat target/v0-3-published-assets-check/ethos-macos-arm64.inventory.json
cat target/v0-3-published-assets-check/ethos-macos-arm64.smoke.json
tar -tzf target/v0-3-published-assets-check/ethos-macos-arm64.tar.gz
shasum -a 256 target/v0-3-published-assets-check/ethos-linux-x64.tar.gz
cat target/v0-3-published-assets-check/ethos-linux-x64.tar.gz.sha256
cat target/v0-3-published-assets-check/ethos-linux-x64.inventory.json
cat target/v0-3-published-assets-check/ethos-linux-x64.smoke.json
tar -tzf target/v0-3-published-assets-check/ethos-linux-x64.tar.gz
```

## Retained Blockers

- `packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed until after this closeout
  record is merged and a dedicated npm vendor refresh lane starts.
- The public install baseline remains current published `0.2.0` Rust/Python and `0.2.1` npm.
- README installation examples remain unchanged.
- npm vendor refresh remains blocked.
- npm publication remains blocked.
- Package tag creation remains blocked.
- Public installation wording remains blocked.
- DocuShell integration remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.
- No additional GitHub Release targets are approved by this closeout.

## Result

GitHub Release `v0.3.0` artifact publication is complete for the exact approved macOS arm64 and
Linux x64 CLI artifacts. The public install baseline remains current published `0.2.0`
Rust/Python and `0.2.1` npm. The next release lane may prepare npm vendor refresh from these
published assets only after this closeout record is merged and dedicated vendor-refresh guards pass.
