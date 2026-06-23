# npm Publication Final Approval Decision Validation - 2026-06-23

- Validated source HEAD before this record: `aab7a97`

npm publication final approval decision source commit: `aab7a97dabc17fa1f90e085e8934e1582827dcda`

npm publication final approval decision source tree: `b842f2aaedf51275cebf25c9ecadc37f56120106`

Status: **npm publication approval decision recorded; operator publish remains pending**

This record accepts the exact npm publication request packet after the provenance blocker was
resolved. It approves only the bounded npm publication decision for `@docushell/ethos-pdf@0.1.0`
using the exact package contents and provenance bindings below. It does not run `npm publish`, does
not publish any package, and does not approve hosted surfaces, production positioning, Windows
packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public
benchmark reports, or public benchmark claims.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Approval owner: `docushell-admin`
- Final approval request record:
  `docs/validation/npm-publication-final-approval-request-validation-2026-06-23.md`
- Candidate evidence record:
  `docs/validation/npm-tarball-candidate-evidence-validation-2026-06-23.md`
- Vendor strategy record:
  `docs/validation/npm-vendor-binary-payload-strategy-validation-2026-06-23.md`

## Exact Decision Fields

- Decision: accept exact npm publication decision packet for the bounded npm candidate.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-23.
- Exact package accepted by this decision: `@docushell/ethos-pdf@0.1.0`.
- Exact npm tarball filename accepted by this decision: `docushell-ethos-pdf-0.1.0.tgz`.
- Exact npm shasum accepted by this decision: `17a053c5ccb802bca2a295e1b1d0e6106c6a3ca6`.
- Exact npm tarball SHA256 accepted by this decision:
  `8d0483d69a6de471dee52c8ef06d46712c06861682a0d7319ca573fdb1fe6376`.
- Exact npm integrity accepted by this decision:
  `sha512-uWTHYd9Hfkm3nkahK2UchCMOVvYWe82z03jffZnX6aYPqYGd6LkuiEoTH5DjrXl+oA817EjlE88fIKBxZbhjMw==`.
- Exact npm pack toolchain accepted for reproducing those tarball hashes and for operator publish:
  - Node.js: `v23.11.1`
  - npm: `10.9.2`
- Exact npm tarball hash interpretation accepted by this decision: npm shasum, tarball SHA256,
  and integrity are qualified by Node.js `v23.11.1` and npm `10.9.2`; per-file SHA256 values are
  the durable cross-toolchain provenance binding.
- Exact vendor binary payload accepted by this decision:
  - `vendor/ethos-darwin-arm64`
    - SHA256: `f1b0c9e47dace78b7e8b3639b9445afe9a01f0db5d5b7b0bd81858def4df2cf5`
  - `vendor/ethos-linux-x64`
    - SHA256: `7ef796a6d1c86b7c3b5b1afe58dd9cc348b706cec441602833540d8a0c9260ac`
  - `vendor/manifest.json`
    - SHA256: `0d03124957255dca55b7374e3318707da488f4b6648bfcec5e6e598079353b1f`
- Exact supported npm platforms accepted by this decision:
  - macOS arm64
  - Linux x64
- Exact installed CLI smoke accepted by this decision: `ethos 0.1.0`.
- Exact missing-PDFium behavior accepted by this decision: exit code `12` with
  `PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path`.
- Exact PDFium boundary accepted by this decision: caller-provided PDFium only through
  `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build.

## Approved Operator Action

After this decision record is merged and the validation commands below pass on the merged source,
an operator may run `npm publish` for the exact `@docushell/ethos-pdf@0.1.0` candidate only if all
of the following are true:

- the operator uses Node.js `v23.11.1` and npm `10.9.2`;
- the operator has npm credentials authorized for the `@docushell` scope;
- the package contents still match the accepted packed file list and durable vendor SHA256 values;
- `npm publish` targets only `@docushell/ethos-pdf@0.1.0`;
- the package version remains `0.1.0`.

This decision does not itself execute `npm publish`; publication remains an explicit later
operator action.

## Required Operator Pre-Publish Checks

Before publishing, the operator must run:

```sh
node --version
npm --version
python3 .github/scripts/test_npm_publication_final_approval_decision.py
python3 .github/scripts/test_npm_tarball_candidate_evidence.py
npm test --prefix packages/npm/ethos-pdf
make release-candidate-prep PYTHON=python3
git diff --check
```

The operator must stop if Node.js is not `v23.11.1`, npm is not `10.9.2`, candidate contents differ,
the durable vendor SHA256 values differ, the missing-PDFium behavior changes, or any retained
blocker is softened.

## Explicit Exclusions

- hosted surfaces remain blocked;
- production positioning remains blocked;
- public benchmark reports remain blocked;
- public benchmark claims remain blocked;
- Windows packaged artifacts remain blocked;
- bundled project-maintained PDFium builds remain blocked;
- `ethos-doc` remains blocked;
- `ethos-rag` remains blocked;
- broader public wording remains blocked.

## Evidence Bound To This Decision

- Decider decision supplied: Approved; provenance blocker resolved.
- `python3 .github/scripts/test_npm_tarball_candidate_evidence.py` passed.
- `python3 .github/scripts/test_npm_publication_final_approval_request.py` passed.
- `python3 .github/scripts/test_milestone_e_source_snapshot_candidate_audit.py` passed.
- `make release-candidate-prep PYTHON=python3` passed before this decision branch.

## Non-Actions

- This decision record does not run `npm publish`.
- This decision record does not publish the npm package.
- This decision record does not change the package version.
- This decision record does not approve public wording changes.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Result

The exact npm publication decision packet for `@docushell/ethos-pdf@0.1.0` is accepted. Actual
publication remains a separate operator action requiring the accepted Node/npm toolchain, npm
credentials, final pre-publish checks, and the exact bounded package contents approved here.
