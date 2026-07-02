# v0.3.0 npm Publication Approval Request Validation - 2026-07-02

Validated source HEAD before this record: `161645d`.

v0.3.0 npm publication approval request source commit:
`161645d7d3b5564cc4fafff411de07631616acca`.

v0.3.0 npm publication approval request source tree:
`3f872c9ff0685bcf6f95e8e05f9530f852b0bd98`.

Status: **v0.3.0 npm publication approval request packet recorded; npm publish remains blocked**

This record requests decider review for publishing exactly `@docushell/ethos-pdf@0.3.0` to npm
using the refreshed and locally validated vendor payload evidence. It does not approve or perform
`npm publish`, change public `0.3.0` installation wording, approve package tags, approve release
tags, approve hosted surfaces, approve production positioning, approve Windows packaged artifacts,
approve bundled project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or
approve public benchmark reports or claims.

The current published npm package observed for this request lane remains
`@docushell/ethos-pdf@0.2.1`.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Package: `@docushell/ethos-pdf`
- Version: `0.3.0`
- Candidate evidence record:
  `docs/validation/v0-3-0-npm-vendor-refresh-validation-2026-07-02.md`
- GitHub Release artifact closeout record:
  `docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md`
- Published GitHub Release artifacts used by candidate:
  - `ethos-macos-arm64.tar.gz`
    - SHA256: `efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96`
  - `ethos-linux-x64.tar.gz`
    - SHA256: `b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405`

## Exact Request Fields

- Decision requested: approve exact npm publication preparation inputs for later operator
  execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-07-02.
- Exact package requested: `@docushell/ethos-pdf@0.3.0`.
- Exact current published npm baseline observed before request: `@docushell/ethos-pdf@0.2.1`.
- Exact npm tarball filename requested: `docushell-ethos-pdf-0.3.0.tgz`.
- Exact npm shasum requested: 1a90cebd8d52011ea5c41629becdfb37dec73ee7.
- Exact npm tarball SHA256 requested:
  `1b72ef2fd9415f9edff93319ee2763e8f67cd6168ea00cd64d89a3760101c5fa`.
- Exact npm integrity requested:
  `sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ==`.
- Exact npm pack toolchain requested for reproducing those tarball hashes:
  - Node.js: `v23.11.1`
  - npm: `10.9.2`
- Exact npm tarball hash interpretation requested: npm shasum, tarball SHA256, and integrity are
  qualified by Node.js `v23.11.1` and npm `10.9.2`; per-file vendor SHA256 values are the durable
  cross-toolchain provenance binding.
- Exact vendor binary payload requested:
  - `vendor/ethos-darwin-arm64`
    - SHA256: `777e1fb243425a46b83b63ed92fbf7cb810f59cfedd81cfe671cf791410c20dc`
  - `vendor/ethos-linux-x64`
    - SHA256: `b416993fc38e6f794611b8b71789ed85af18eb6aa63fef380d9ae7738661f154`
  - `vendor/manifest.json`
    - SHA256: `e313b42e49b258171611935455fd9e70bad7ce61c409df63ab90aaa2732a46af`
- Exact supported npm platforms requested:
  - macOS arm64
  - Linux x64
- Exact installed CLI smoke accepted for request: `ethos 0.3.0`.
- Exact missing-PDFium behavior accepted for request: exit code `12` with caller-provided PDFium
  guidance through `ETHOS_PDFIUM_LIBRARY_PATH`.
- Exact PDFium boundary requested: caller-provided PDFium only through
  `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build.

## Requested Publication Boundaries

- Only `@docushell/ethos-pdf@0.3.0` is in scope.
- Publication must use the exact candidate tarball bound above.
- Publication must use Node.js `v23.11.1` and npm `10.9.2` when reproducing npm pack hashes or
  running `npm publish`.
- Publication must not change the package version.
- Publication must not change public `0.3.0` installation wording.
- Publication must not create package tags.
- Publication must not create release tags.
- Publication must not add Windows packaged artifacts.
- Publication must not add hosted surfaces.
- Publication must not add production positioning.
- Publication must not add public benchmark reports or claims.
- Publication must not bundle PDFium or claim a project-maintained PDFium build.
- Publication must not approve `ethos-doc` or `ethos-rag`.
- Publication must not approve DocuShell integration.

## Required Manual Decider Step

Manual action is required before any publish operation:

1. A decider must accept or reject this exact request packet.
2. If accepted, a separate approval decision record must bind the exact npm candidate and retained
   blockers.
3. Only after that decision record passes may an operator run `npm publish` with npm credentials.

No `npm publish` command is approved by this request record.

## Evidence Bound To This Request

- `python3 .github/scripts/test_v0_3_0_npm_vendor_refresh.py` passed.
- `python3 .github/scripts/test_npm_tarball_candidate_evidence.py` passed.
- `python3 .github/scripts/test_npm_binary_package_scaffold.py` passed.
- `npm test --prefix packages/npm/ethos-pdf` passed.
- `python3 .github/scripts/test_public_surface_posture.py` passed.
- `python3 .github/scripts/claims_gate.py` passed.
- `python3 .github/scripts/public_boundary_claims_gate.py` passed.
- `make v0-3-release-prep PYTHON=python3` passed on merged `main` after the v0.3.0 npm vendor
  refresh merge.
- `npm view @docushell/ethos-pdf version` returned `0.2.1` before this request, confirming that
  `@docushell/ethos-pdf@0.3.0` was not already live.
- Provenance chain confirmed: published GitHub Release `v0.3.0` archives are bound by archive
  SHA256, the extracted npm vendor payload is bound by per-file SHA256, and npm tarball hashes are
  toolchain-qualified under Node.js `v23.11.1` and npm `10.9.2`.

## Non-Approvals

- This request packet does not approve `npm publish`.
- This request packet does not publish the npm package.
- This request packet does not approve public `0.3.0` installation wording changes.
- This request packet does not approve package tag creation.
- This request packet does not approve release tag creation.
- This request packet does not approve DocuShell integration.
- This request packet does not approve hosted surfaces.
- This request packet does not approve production positioning.
- This request packet does not approve public benchmark reports.
- This request packet does not approve public benchmark claims.
- This request packet does not approve Windows packaged artifacts.
- This request packet does not approve bundled project-maintained PDFium builds.
- This request packet does not approve `ethos-doc`.
- This request packet does not approve `ethos-rag`.

## Retained Blockers

- npm publication remains blocked pending explicit decider approval.
- Actual npm publish remains blocked pending explicit operator action with npm credentials.
- Public `0.3.0` installation wording remains blocked.
- Registry publication remains blocked.
- Package tag creation remains blocked.
- Release tag creation remains blocked.
- DocuShell integration remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Commands

```sh
python3 .github/scripts/test_v0_3_0_npm_publication_approval_request.py
python3 .github/scripts/test_v0_3_0_npm_vendor_refresh.py
python3 .github/scripts/test_npm_tarball_candidate_evidence.py
python3 .github/scripts/test_npm_binary_package_scaffold.py
npm test --prefix packages/npm/ethos-pdf
python3 .github/scripts/validation_record_integrity.py
make v0-3-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.3.0 npm publication approval request packet recorded
Exact package, version, toolchain-qualified npm shasum, toolchain-qualified tarball SHA256,
toolchain-qualified integrity, durable vendor payload checksums, installed CLI smoke, and PDFium
boundary were recorded
npm publish remains blocked pending explicit decider approval and later operator action
```
