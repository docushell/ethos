# Patch 0.1.1 npm Publication Approval Request Validation - 2026-06-23

Validated source HEAD before this record: `af1851c`.

npm publication approval request source commit: `af1851c88b2b7c17f706a902ca64987c2af082be`.

npm publication approval request source tree: `7d501ab7fa5a585352918f65fbd2de1756a184b9`.

Status: **patch 0.1.1 npm publication approval request packet recorded; npm publish remains blocked**

This record requests decider review for publishing exactly `@docushell/ethos-pdf@0.1.1` to npm
using the refreshed and locally validated vendor payload evidence. It does not approve or perform
`npm publish`, change public wording, approve hosted surfaces, approve production positioning,
approve Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve
`ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Package: `@docushell/ethos-pdf`
- Version: `0.1.1`
- Candidate evidence record:
  `docs/validation/patch-0-1-1-npm-vendor-refresh-validation-2026-06-23.md`
- Vendor strategy record:
  `docs/validation/npm-vendor-binary-payload-strategy-validation-2026-06-23.md`
- Approved release artifacts used by candidate:
  - `ethos-macos-arm64.tar.gz`
  - `ethos-linux-x64.tar.gz`

## Exact Request Fields

- Decision requested: approve exact npm publication preparation inputs for later operator
  execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-06-23.
- Exact package requested: `@docushell/ethos-pdf@0.1.1`.
- Exact npm tarball filename requested: `docushell-ethos-pdf-0.1.1.tgz`.
- Exact npm shasum requested: a150d08395724aa186d077074782413249a48689.
- Exact npm tarball SHA256 requested:
  `4b227d37bd125c6db1ffe40534f6cb5223a60073f26e3c4dbf60709561671d3d`.
- Exact npm integrity requested:
  `sha512-wVF4Ew6836sRncPZkvVieyQuo8FFbbBsIQ/vdupleUQZVX4YHgXb+lFZzZNcVB54Hh7srbbY17El4Z5sV7odhA==`.
- Exact npm pack toolchain requested for reproducing those tarball hashes:
  - Node.js: `v23.11.1`
  - npm: `10.9.2`
- Exact npm tarball hash interpretation requested: npm shasum, tarball SHA256, and integrity are
  qualified by Node.js `v23.11.1` and npm `10.9.2`; per-file vendor SHA256 values are the durable
  cross-toolchain provenance binding.
- Exact vendor binary payload requested:
  - `vendor/ethos-darwin-arm64`
    - SHA256: `a3d0d4be596da25313659a89de8fbff0e13f4b355462381e1bbedd05078c09f2`
  - `vendor/ethos-linux-x64`
    - SHA256: `ee14be020fb79e326686fc77bcf781503f4759d2e3b7bcb6a641b2311608a354`
  - `vendor/manifest.json`
    - SHA256: `7be6e6c02c0086de7c10594a6f0443c8535d5782a4ffc0bc0eed3f8ebb13bda8`
- Exact supported npm platforms requested:
  - macOS arm64
  - Linux x64
- Exact installed CLI smoke accepted for request: `ethos 0.1.1`.
- Exact missing-PDFium behavior accepted for request: exit code `12` with
  `PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path`.
- Exact PDFium boundary requested: caller-provided PDFium only through
  `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build.

## Requested Publication Boundaries

- Only `@docushell/ethos-pdf@0.1.1` is in scope.
- Publication must use the exact candidate tarball bound above.
- Publication must use Node.js `v23.11.1` and npm `10.9.2` when reproducing npm pack hashes or
  running `npm publish`.
- Publication must not change the package version.
- Publication must not add Windows packaged artifacts.
- Publication must not add hosted surfaces.
- Publication must not add production positioning.
- Publication must not add public benchmark reports or claims.
- Publication must not bundle PDFium or claim a project-maintained PDFium build.
- Publication must not approve `ethos-doc` or `ethos-rag`.

## Required Manual Decider Step

Manual action is required before any publish operation:

1. A decider must accept or reject this exact request packet.
2. If accepted, a separate approval decision record must bind the exact npm candidate and retained
   blockers.
3. Only after that decision record passes may an operator run `npm publish` with npm credentials.

No `npm publish` command is approved by this request record.

## Evidence Bound To This Request

- `python3 .github/scripts/test_npm_tarball_candidate_evidence.py` passed.
- `npm test --prefix packages/npm/ethos-pdf` passed.
- `python3 .github/scripts/test_npm_binary_package_scaffold.py` passed.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this request branch.
- Provenance chain confirmed: approved GitHub Release `v0.1.1` archives are bound by archive
  SHA256, the extracted npm vendor payload is bound by per-file SHA256, and npm tarball hashes are
  toolchain-qualified under Node.js `v23.11.1` and npm `10.9.2`.

## Non-Approvals

- This request packet does not approve `npm publish`.
- This request packet does not publish the npm package.
- This request packet does not approve public wording changes.
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
python3 .github/scripts/test_npm_publication_final_approval_request.py
python3 .github/scripts/test_npm_tarball_candidate_evidence.py
python3 .github/scripts/test_npm_binary_package_scaffold.py
python3 .github/scripts/test_npm_vendor_binary_payload_strategy.py
npm test --prefix packages/npm/ethos-pdf
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.1 npm publication approval request packet recorded
Exact package, version, toolchain-qualified npm shasum, toolchain-qualified tarball SHA256, toolchain-qualified integrity, durable vendor payload checksums, installed CLI smoke, and PDFium boundary were recorded
npm publish remains blocked pending explicit decider approval and later operator action
```
