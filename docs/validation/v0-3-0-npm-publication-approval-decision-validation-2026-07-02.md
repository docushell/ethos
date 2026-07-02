# v0.3.0 npm Publication Approval Decision Validation - 2026-07-02

Validated source HEAD before this record: `5262d4f`.

v0.3.0 npm publication approval decision source commit:
`5262d4f736f5fa52fd14990c11b535768085ede6`.

v0.3.0 npm publication approval decision source tree:
`f942e215a6aa35cec96d8ff3958958d07b77b41f`.

Status: **v0.3.0 npm publication approval decision recorded; operator publish remains pending**

This record accepts the exact v0.3.0 npm publication approval request packet after decider
approval. It approves only the bounded later npm publication operator action for
`@docushell/ethos-pdf@0.3.0` using the exact package contents and provenance bindings below. It
does not run `npm publish`, does not publish any package, does not change public `0.3.0`
installation wording, does not create package tags or release tags, and does not approve
DocuShell integration, hosted surfaces, production positioning, Windows packaged artifacts,
bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or
public benchmark claims.

The current published npm package observed before the approval request remains
`@docushell/ethos-pdf@0.2.1`.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Approval owner: `docushell-admin`
- Final approval request record:
  `docs/validation/v0-3-0-npm-publication-approval-request-validation-2026-07-02.md`
- Candidate evidence record:
  `docs/validation/v0-3-0-npm-vendor-refresh-validation-2026-07-02.md`
- GitHub Release artifact closeout record:
  `docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md`

## Exact Decision Fields

- Decision: accept exact v0.3.0 npm publication decision packet for the bounded npm candidate.
- Decider decision supplied: Approved; exact v0.3.0 npm publication approval request accepted.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-07-02.
- Exact package accepted by this decision: `@docushell/ethos-pdf@0.3.0`.
- Exact current published npm baseline observed before request: `@docushell/ethos-pdf@0.2.1`.
- Exact npm tarball filename accepted by this decision: `docushell-ethos-pdf-0.3.0.tgz`.
- Exact npm shasum accepted by this decision: 1a90cebd8d52011ea5c41629becdfb37dec73ee7.
- Exact npm tarball SHA256 accepted by this decision:
  `1b72ef2fd9415f9edff93319ee2763e8f67cd6168ea00cd64d89a3760101c5fa`.
- Exact npm integrity accepted by this decision:
  `sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ==`.
- Exact npm pack toolchain accepted for reproducing those tarball hashes and for operator publish:
  - Node.js: `v23.11.1`
  - npm: `10.9.2`
- Exact npm tarball hash interpretation accepted by this decision: npm shasum, tarball SHA256,
  and integrity are qualified by Node.js `v23.11.1` and npm `10.9.2`; per-file vendor SHA256
  values are the durable cross-toolchain provenance binding.
- Exact GitHub Release artifact inputs accepted by this decision:
  - `ethos-macos-arm64.tar.gz`
    - SHA256: `efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96`
  - `ethos-linux-x64.tar.gz`
    - SHA256: `b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405`
- Exact vendor binary payload accepted by this decision:
  - `vendor/ethos-darwin-arm64`
    - SHA256: `777e1fb243425a46b83b63ed92fbf7cb810f59cfedd81cfe671cf791410c20dc`
  - `vendor/ethos-linux-x64`
    - SHA256: `b416993fc38e6f794611b8b71789ed85af18eb6aa63fef380d9ae7738661f154`
  - `vendor/manifest.json`
    - SHA256: `e313b42e49b258171611935455fd9e70bad7ce61c409df63ab90aaa2732a46af`
- Exact supported npm platforms accepted by this decision:
  - macOS arm64
  - Linux x64
- Exact installed CLI smoke accepted by this decision: `ethos 0.3.0`.
- Exact missing-PDFium behavior accepted by this decision: exit code `12` with caller-provided
  PDFium guidance through `ETHOS_PDFIUM_LIBRARY_PATH`.
- Exact PDFium boundary accepted by this decision: caller-provided PDFium only through
  `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build.

## Approved Operator Action

After this decision record is merged and the validation commands below pass on the merged source,
an operator may run `npm publish` for the exact `@docushell/ethos-pdf@0.3.0` candidate only if all
of the following are true:

- the operator uses Node.js `v23.11.1` and npm `10.9.2`;
- the operator has npm credentials authorized for the `@docushell` scope;
- `npm view @docushell/ethos-pdf version` does not already report `0.3.0`;
- the package contents still match the accepted packed file list and durable vendor SHA256 values;
- `npm publish` targets only `@docushell/ethos-pdf@0.3.0`;
- the package version remains `0.3.0`;
- the missing-PDFium behavior remains exit code `12` with caller-provided PDFium guidance.

This decision does not itself execute `npm publish`; publication remains an explicit later
operator action.

## Required Operator Pre-Publish Checks

Before publishing, the operator must run:

```sh
node --version
npm --version
npm view @docushell/ethos-pdf version
python3 .github/scripts/test_v0_3_0_npm_publication_approval_decision.py
python3 .github/scripts/test_v0_3_0_npm_publication_approval_request.py
python3 .github/scripts/test_v0_3_0_npm_vendor_refresh.py
python3 .github/scripts/test_npm_tarball_candidate_evidence.py
python3 .github/scripts/test_npm_binary_package_scaffold.py
npm test --prefix packages/npm/ethos-pdf
make v0-3-release-prep PYTHON=python3
git diff --check
```

The operator must stop if Node.js is not `v23.11.1`, npm is not `10.9.2`, candidate contents
differ, durable vendor SHA256 values differ, missing-PDFium behavior changes, the registry already
reports `0.3.0` before publish, or any retained blocker is softened.

## Explicit Exclusions

- Public `0.3.0` installation wording remains blocked;
- registry closeout remains blocked until registry evidence is recorded after publication;
- package tag creation remains blocked;
- release tag creation remains blocked;
- DocuShell integration remains blocked;
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

- Decider decision supplied: Approved; exact v0.3.0 npm publication approval request accepted.
- `python3 .github/scripts/test_v0_3_0_npm_publication_approval_request.py` passed.
- `python3 .github/scripts/test_v0_3_0_npm_vendor_refresh.py` passed.
- `python3 .github/scripts/test_npm_tarball_candidate_evidence.py` passed.
- `python3 .github/scripts/test_npm_binary_package_scaffold.py` passed.
- `npm test --prefix packages/npm/ethos-pdf` passed.
- `make v0-3-release-prep PYTHON=python3` passed on merged `main` after the approval-request merge.
- `npm view @docushell/ethos-pdf version` returned `0.2.1` before the approval request, confirming
  that `@docushell/ethos-pdf@0.3.0` was not already live.

## Non-Actions

- This decision record does not run `npm publish`.
- This decision record does not publish the npm package.
- This decision record does not change the package version.
- This decision record does not approve public `0.3.0` installation wording changes.
- This decision record does not approve package tag creation.
- This decision record does not approve release tag creation.
- This decision record does not approve DocuShell integration.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Result

The exact npm publication decision packet for `@docushell/ethos-pdf@0.3.0` is accepted. Actual
publication remains a separate operator action requiring the accepted Node/npm toolchain, npm
credentials, final pre-publish checks, and the exact bounded package contents approved here.
