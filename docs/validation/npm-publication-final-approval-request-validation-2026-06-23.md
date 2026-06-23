# npm Publication Final Approval Request Validation - 2026-06-23

- Validated source HEAD before this record: `73f673c`

npm publication final approval request source commit: `73f673cd4e6afcac6c96baffd743b339a89de96c`

npm publication final approval request source tree: `942087f3d45f8d62e46f116b3f576b1713e17f37`

Status: **npm publication approval request packet recorded; npm publish remains blocked**

This record requests decider review for publishing exactly `@docushell/ethos-pdf@0.1.0` to npm
using the already assembled and locally validated candidate tarball evidence. It does not approve
or perform `npm publish`, change public wording, approve hosted surfaces, approve production
positioning, approve Windows packaged artifacts, approve bundled project-maintained PDFium builds,
approve `ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Package: `@docushell/ethos-pdf`
- Version: `0.1.0`
- Candidate evidence record:
  `docs/validation/npm-tarball-candidate-evidence-validation-2026-06-23.md`
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
- Exact package requested: `@docushell/ethos-pdf@0.1.0`.
- Exact npm tarball filename requested: `docushell-ethos-pdf-0.1.0.tgz`.
- Exact npm shasum requested: `17a053c5ccb802bca2a295e1b1d0e6106c6a3ca6`.
- Exact npm tarball SHA256 requested:
  `8d0483d69a6de471dee52c8ef06d46712c06861682a0d7319ca573fdb1fe6376`.
- Exact npm integrity requested:
  `sha512-uWTHYd9Hfkm3nkahK2UchCMOVvYWe82z03jffZnX6aYPqYGd6LkuiEoTH5DjrXl+oA817EjlE88fIKBxZbhjMw==`.
- Exact npm pack toolchain requested for reproducing those tarball hashes:
  - Node.js: `v23.11.1`
  - npm: `10.9.2`
- Exact npm tarball hash interpretation requested: npm shasum, tarball SHA256, and integrity are
  qualified by Node.js `v23.11.1` and npm `10.9.2`; per-file SHA256 values are the durable
  cross-toolchain provenance binding.
- Exact vendor binary payload requested:
  - `vendor/ethos-darwin-arm64`
    - SHA256: `f1b0c9e47dace78b7e8b3639b9445afe9a01f0db5d5b7b0bd81858def4df2cf5`
  - `vendor/ethos-linux-x64`
    - SHA256: `7ef796a6d1c86b7c3b5b1afe58dd9cc348b706cec441602833540d8a0c9260ac`
  - `vendor/manifest.json`
    - SHA256: `0d03124957255dca55b7374e3318707da488f4b6648bfcec5e6e598079353b1f`
- Exact supported npm platforms requested:
  - macOS arm64
  - Linux x64
- Exact installed CLI smoke accepted for request: `ethos 0.1.0`.
- Exact missing-PDFium behavior accepted for request: exit code `12` with
  `PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path`.
- Exact PDFium boundary requested: caller-provided PDFium only through
  `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build.

## Requested Publication Boundaries

- Only `@docushell/ethos-pdf@0.1.0` is in scope.
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
- `python3 .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py` passed.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this request branch.
- Provenance chain confirmed: approved GitHub Release archives are bound by archive SHA256, the
  extracted npm vendor payload is bound by per-file SHA256, and npm tarball hashes are
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
python3 .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
npm publication final approval request packet recorded
Exact package, version, toolchain-qualified npm shasum, toolchain-qualified tarball SHA256, toolchain-qualified integrity, durable vendor payload checksums, installed CLI smoke, and PDFium boundary were recorded
npm publish remains blocked pending explicit decider approval and later operator action
```
