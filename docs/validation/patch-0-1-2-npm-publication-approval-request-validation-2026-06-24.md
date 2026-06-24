# Patch 0.1.2 npm Publication Approval Request Validation - 2026-06-24

Validated source HEAD before this record: `8ee8e8c`.

npm publication approval request source commit: `8ee8e8c5b6f4fb228f896b7e3e336f17b560490c`.

npm publication approval request source tree: `959115a414e334a42f0078b2070e9790eb5b752f`.

Status: **patch 0.1.2 npm publication approval request packet recorded; npm publish remains blocked**

This record requests decider review for publishing exactly `@docushell/ethos-pdf@0.1.2` to npm
using the refreshed and locally validated vendor payload evidence. It does not approve or perform
`npm publish`, change public installation wording, approve hosted surfaces, approve production
positioning, approve Windows packaged artifacts, approve bundled project-maintained PDFium builds,
approve `ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Package: `@docushell/ethos-pdf`
- Version: `0.1.2`
- Candidate evidence record:
  `docs/validation/patch-0-1-2-npm-vendor-refresh-validation-2026-06-24.md`
- GitHub Release artifact closeout record:
  `docs/validation/patch-0-1-2-artifact-publication-closeout-validation-2026-06-24.md`
- Approved release artifacts used by candidate:
  - `ethos-macos-arm64.tar.gz`
  - `ethos-linux-x64.tar.gz`

## Exact Request Fields

- Decision requested: approve exact npm publication preparation inputs for later operator
  execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-06-24.
- Exact package requested: `@docushell/ethos-pdf@0.1.2`.
- Exact npm tarball filename requested: `docushell-ethos-pdf-0.1.2.tgz`.
- Exact npm shasum requested: 39b85d74f588666bfbf69e423a189c2039743de4.
- Exact npm tarball SHA256 requested:
  `77cbc9c79dd60cc16073690a186e149ecbaabacce035fb0bd3603b267ce64112`.
- Exact npm integrity requested:
  `sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg==`.
- Exact npm pack toolchain requested for reproducing those tarball hashes:
  - Node.js: `v23.11.1`
  - npm: `10.9.2`
- Exact npm tarball hash interpretation requested: npm shasum, tarball SHA256, and integrity are
  qualified by Node.js `v23.11.1` and npm `10.9.2`; per-file vendor SHA256 values are the durable
  cross-toolchain provenance binding.
- Exact vendor binary payload requested:
  - `vendor/ethos-darwin-arm64`
    - SHA256: `47c2f4aaac6cb6a1ca5cf1d9a0cc1f897ef00c48cdd8549455de70f0fbc6bcc1`
  - `vendor/ethos-linux-x64`
    - SHA256: `e75122f2954efbde6b8c07a98601b8d4a3b7a06647891a9e60d6aef4046649c3`
  - `vendor/manifest.json`
    - SHA256: `d557e081b946be0f839b17b8593027e31267b668498e202372026020f68a97a1`
- Exact supported npm platforms requested:
  - macOS arm64
  - Linux x64
- Exact installed CLI smoke accepted for request: `ethos 0.1.2`.
- Exact missing-PDFium behavior accepted for request: exit code `12` with
  `PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path`.
- Exact PDFium boundary requested: caller-provided PDFium only through
  `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build.

## Requested Publication Boundaries

- Only `@docushell/ethos-pdf@0.1.2` is in scope.
- Publication must use the exact candidate tarball bound above.
- Publication must use Node.js `v23.11.1` and npm `10.9.2` when reproducing npm pack hashes or
  running `npm publish`.
- Publication must not change the package version.
- Publication must not change public installation wording.
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
- `python3 .github/scripts/test_patch_0_1_2_npm_vendor_refresh.py` passed.
- `npm test --prefix packages/npm/ethos-pdf` passed.
- `python3 .github/scripts/test_npm_binary_package_scaffold.py` passed.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this request branch.
- Provenance chain confirmed: approved GitHub Release `v0.1.2` archives are bound by archive
  SHA256, the extracted npm vendor payload is bound by per-file SHA256, and npm tarball hashes are
  toolchain-qualified under Node.js `v23.11.1` and npm `10.9.2`.

## Non-Approvals

- This request packet does not approve `npm publish`.
- This request packet does not publish the npm package.
- This request packet does not approve public installation wording changes.
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
- Public installation wording remains blocked.
- Registry publication remains blocked.
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
python3 .github/scripts/test_patch_0_1_2_npm_publication_approval_request.py
python3 .github/scripts/test_npm_tarball_candidate_evidence.py
python3 .github/scripts/test_patch_0_1_2_npm_vendor_refresh.py
python3 .github/scripts/test_npm_binary_package_scaffold.py
npm test --prefix packages/npm/ethos-pdf
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 npm publication approval request packet recorded
Exact package, version, toolchain-qualified npm shasum, toolchain-qualified tarball SHA256, toolchain-qualified integrity, durable vendor payload checksums, installed CLI smoke, and PDFium boundary were recorded
npm publish remains blocked pending explicit decider approval and later operator action
```
