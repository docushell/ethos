# Patch 0.1.1 npm Publication Approval Decision Validation - 2026-06-23

Validated source HEAD before this record: `25d52b9`.

npm publication final approval decision source commit: `25d52b9dc0119aaa39e66d3886583a95bb852128`.

npm publication final approval decision source tree: `26e6faa2d0171589efc4d18a7ce6593f36583d32`.

Status: **patch 0.1.1 npm publication approval decision recorded; operator publish remains pending**

This record accepts the exact patch `0.1.1` npm publication request packet after decider approval.
It approves only the bounded npm publication decision for `@docushell/ethos-pdf@0.1.1` using the
exact package contents and provenance bindings below. It does not run `npm publish`, does not
publish any package, and does not approve hosted surfaces, production positioning, Windows packaged
artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark
reports, or public benchmark claims.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Approval owner: `docushell-admin`
- Final approval request record:
  `docs/validation/patch-0-1-1-npm-publication-approval-request-validation-2026-06-23.md`
- Candidate evidence record:
  `docs/validation/patch-0-1-1-npm-vendor-refresh-validation-2026-06-23.md`
- Vendor strategy record:
  `docs/validation/npm-vendor-binary-payload-strategy-validation-2026-06-23.md`

## Exact Decision Fields

- Decision: accept exact patch `0.1.1` npm publication decision packet for the bounded npm
  candidate.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-23.
- Exact package accepted by this decision: `@docushell/ethos-pdf@0.1.1`.
- Exact npm tarball filename accepted by this decision: `docushell-ethos-pdf-0.1.1.tgz`.
- Exact npm shasum accepted by this decision: a150d08395724aa186d077074782413249a48689.
- Exact npm tarball SHA256 accepted by this decision:
  `4b227d37bd125c6db1ffe40534f6cb5223a60073f26e3c4dbf60709561671d3d`.
- Exact npm integrity accepted by this decision:
  `sha512-wVF4Ew6836sRncPZkvVieyQuo8FFbbBsIQ/vdupleUQZVX4YHgXb+lFZzZNcVB54Hh7srbbY17El4Z5sV7odhA==`.
- Exact npm pack toolchain accepted for reproducing those tarball hashes and for operator publish:
  - Node.js: `v23.11.1`
  - npm: `10.9.2`
- Exact npm tarball hash interpretation accepted by this decision: npm shasum, tarball SHA256,
  and integrity are qualified by Node.js `v23.11.1` and npm `10.9.2`; per-file vendor SHA256
  values are the durable cross-toolchain provenance binding.
- Exact vendor binary payload accepted by this decision:
  - `vendor/ethos-darwin-arm64`
    - SHA256: `a3d0d4be596da25313659a89de8fbff0e13f4b355462381e1bbedd05078c09f2`
  - `vendor/ethos-linux-x64`
    - SHA256: `ee14be020fb79e326686fc77bcf781503f4759d2e3b7bcb6a641b2311608a354`
  - `vendor/manifest.json`
    - SHA256: `7be6e6c02c0086de7c10594a6f0443c8535d5782a4ffc0bc0eed3f8ebb13bda8`
- Exact supported npm platforms accepted by this decision:
  - macOS arm64
  - Linux x64
- Exact installed CLI smoke accepted by this decision: `ethos 0.1.1`.
- Exact missing-PDFium behavior accepted by this decision: exit code `12` with
  `PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path`.
- Exact PDFium boundary accepted by this decision: caller-provided PDFium only through
  `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build.

## Approved Operator Action

After this decision record is merged and the validation commands below pass on the merged source,
an operator may run `npm publish` for the exact `@docushell/ethos-pdf@0.1.1` candidate only if all
of the following are true:

- the operator uses Node.js `v23.11.1` and npm `10.9.2`;
- the operator has npm credentials authorized for the `@docushell` scope;
- the package contents still match the accepted packed file list and durable vendor SHA256 values;
- `npm publish` targets only `@docushell/ethos-pdf@0.1.1`;
- the package version remains `0.1.1`.

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

- Decider decision supplied: Approved; exact patch `0.1.1` npm publication approval request
  accepted.
- `python3 .github/scripts/test_npm_tarball_candidate_evidence.py` passed.
- `python3 .github/scripts/test_npm_publication_final_approval_request.py` passed.
- `python3 .github/scripts/test_npm_publication_final_approval_decision.py` passed.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this decision branch.

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

The exact npm publication decision packet for `@docushell/ethos-pdf@0.1.1` is accepted. Actual
publication remains a separate operator action requiring the accepted Node/npm toolchain, npm
credentials, final pre-publish checks, and the exact bounded package contents approved here.
