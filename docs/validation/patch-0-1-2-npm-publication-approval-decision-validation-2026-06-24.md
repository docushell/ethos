# Patch 0.1.2 npm Publication Approval Decision Validation - 2026-06-24

Validated source HEAD before this record: `ef63161`.

npm publication approval decision source commit: `ef631614f8c36b6ef080e968d8daac937a63a533`.

npm publication approval decision source tree: `fc514355314347619e07122700b7d1b035302653`.

Status: **patch 0.1.2 npm publication approval decision recorded; operator publish remains pending**

This record accepts the exact patch `0.1.2` npm publication request packet after decider approval.
It approves only the bounded npm publication decision for `@docushell/ethos-pdf@0.1.2` using the
exact package contents and provenance bindings below. It does not run `npm publish`, does not
publish any package, does not change public installation wording, and does not approve hosted
surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or public benchmark claims.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Approval owner: `docushell-admin`
- Final approval request record:
  `docs/validation/patch-0-1-2-npm-publication-approval-request-validation-2026-06-24.md`
- Candidate evidence record:
  `docs/validation/patch-0-1-2-npm-vendor-refresh-validation-2026-06-24.md`
- GitHub Release artifact closeout record:
  `docs/validation/patch-0-1-2-artifact-publication-closeout-validation-2026-06-24.md`

## Exact Decision Fields

- Decision: accept exact patch `0.1.2` npm publication decision packet for the bounded npm
  candidate.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-24.
- Exact package accepted by this decision: `@docushell/ethos-pdf@0.1.2`.
- Exact npm tarball filename accepted by this decision: `docushell-ethos-pdf-0.1.2.tgz`.
- Exact npm shasum accepted by this decision: 39b85d74f588666bfbf69e423a189c2039743de4.
- Exact npm tarball SHA256 accepted by this decision:
  `77cbc9c79dd60cc16073690a186e149ecbaabacce035fb0bd3603b267ce64112`.
- Exact npm integrity accepted by this decision:
  `sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg==`.
- Exact npm pack toolchain accepted for reproducing those tarball hashes and for operator publish:
  - Node.js: `v23.11.1`
  - npm: `10.9.2`
- Exact npm tarball hash interpretation accepted by this decision: npm shasum, tarball SHA256,
  and integrity are qualified by Node.js `v23.11.1` and npm `10.9.2`; per-file vendor SHA256
  values are the durable cross-toolchain provenance binding.
- Exact vendor binary payload accepted by this decision:
  - `vendor/ethos-darwin-arm64`
    - SHA256: `47c2f4aaac6cb6a1ca5cf1d9a0cc1f897ef00c48cdd8549455de70f0fbc6bcc1`
  - `vendor/ethos-linux-x64`
    - SHA256: `e75122f2954efbde6b8c07a98601b8d4a3b7a06647891a9e60d6aef4046649c3`
  - `vendor/manifest.json`
    - SHA256: `d557e081b946be0f839b17b8593027e31267b668498e202372026020f68a97a1`
- Exact supported npm platforms accepted by this decision:
  - macOS arm64
  - Linux x64
- Exact installed CLI smoke accepted by this decision: `ethos 0.1.2`.
- Exact missing-PDFium behavior accepted by this decision: exit code `12` with
  `PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path`.
- Exact PDFium boundary accepted by this decision: caller-provided PDFium only through
  `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build.

## Approved Operator Action

After this decision record is merged and the validation commands below pass on the merged source,
an operator may run `npm publish` for the exact `@docushell/ethos-pdf@0.1.2` candidate only if all
of the following are true:

- the operator uses Node.js `v23.11.1` and npm `10.9.2`;
- the operator has npm credentials authorized for the `@docushell` scope;
- the package contents still match the accepted packed file list and durable vendor SHA256 values;
- `npm publish` targets only `@docushell/ethos-pdf@0.1.2`;
- the package version remains `0.1.2`.

This decision does not itself execute `npm publish`; publication remains an explicit later
operator action.

## Required Operator Pre-Publish Checks

Before publishing, the operator must run:

```sh
node --version
npm --version
python3 .github/scripts/test_patch_0_1_2_npm_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_npm_publication_approval_request.py
python3 .github/scripts/test_npm_tarball_candidate_evidence.py
npm test --prefix packages/npm/ethos-pdf
make release-candidate-prep PYTHON=python3
git diff --check
```

The operator must stop if Node.js is not `v23.11.1`, npm is not `10.9.2`, candidate contents differ,
the durable vendor SHA256 values differ, the missing-PDFium behavior changes, or any retained
blocker is softened.

## Explicit Exclusions

- Public installation wording remains blocked;
- registry closeout remains blocked until registry evidence is recorded after publication;
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

- Decider decision supplied: Approved; exact patch `0.1.2` npm publication approval request
  accepted.
- `python3 .github/scripts/test_patch_0_1_2_npm_publication_approval_request.py` passed.
- `python3 .github/scripts/test_npm_tarball_candidate_evidence.py` passed.
- `python3 .github/scripts/test_patch_0_1_2_npm_vendor_refresh.py` passed.
- `npm test --prefix packages/npm/ethos-pdf` passed.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this decision branch.

## Non-Actions

- This decision record does not run `npm publish`.
- This decision record does not publish the npm package.
- This decision record does not change the package version.
- This decision record does not approve public installation wording changes.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Result

The exact npm publication decision packet for `@docushell/ethos-pdf@0.1.2` is accepted. Actual
publication remains a separate operator action requiring the accepted Node/npm toolchain, npm
credentials, final pre-publish checks, and the exact bounded package contents approved here.
