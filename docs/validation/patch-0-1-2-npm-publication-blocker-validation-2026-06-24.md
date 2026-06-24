# Patch 0.1.2 npm Publication Blocker Validation - 2026-06-24

Validated source HEAD before this record: `5d04c71`.

Patch 0.1.2 npm publication blocker source commit:
`5d04c71b3f229fc08f3cae3e094cb315da286ffd`.

Patch 0.1.2 npm publication blocker source tree:
`828a57c1c4448f2dbb9e44c0c4afb9418d775567`.

Status: **patch 0.1.2 npm publication remains blocked after registry publish failure**

This record captures a failed operator publication attempt after the patch `0.1.2` npm publication
approval decision merged. The attempted tarball metadata matched the approved
`@docushell/ethos-pdf@0.1.2` candidate, but npm rejected the `PUT` with `E404`. Registry checks
after the attempt confirmed that `@docushell/ethos-pdf@0.1.2` is not published.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication
- Approved decision record:
  `docs/validation/patch-0-1-2-npm-publication-approval-decision-validation-2026-06-24.md`
- Approved request record:
  `docs/validation/patch-0-1-2-npm-publication-approval-request-validation-2026-06-24.md`
- Candidate evidence record:
  `docs/validation/patch-0-1-2-npm-vendor-refresh-validation-2026-06-24.md`
- Candidate package: `@docushell/ethos-pdf@0.1.2`

## Attempted Publish Evidence

Operator command:

```sh
cd packages/npm/ethos-pdf && npm publish --access public
```

Observed npm notice metadata:

- name: `@docushell/ethos-pdf`
- version: `0.1.2`
- filename: `docushell-ethos-pdf-0.1.2.tgz`
- npm shasum: 39b85d74f588666bfbf69e423a189c2039743de4
- approved tarball SHA256:
  `77cbc9c79dd60cc16073690a186e149ecbaabacce035fb0bd3603b267ce64112`
- integrity:
  `sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg==`
- total files: 11

Observed warning:

```text
npm auto-corrected some errors in your package.json when publishing
"bin[ethos]" script name was cleaned
```

Observed failure:

```text
npm error code E404
npm error 404 Not Found - PUT https://registry.npmjs.org/@docushell%2fethos-pdf - Not found
npm error 404 '@docushell/ethos-pdf@0.1.2' is not in this registry.
```

The local npm debug-log path from the operator machine is intentionally omitted.

## Registry Verification After Failure

Command:

```sh
npm view @docushell/ethos-pdf versions --json
npm view @docushell/ethos-pdf version
npm view @docushell/ethos-pdf@0.1.2 version
```

Observed versions:

- `0.0.0-reserved.0`
- `0.1.0`
- `0.1.1`

The latest registry version remains `0.1.1`.

Lookup for `@docushell/ethos-pdf@0.1.2` returned E404 with no matching published version.

## Blocker Classification

- The approved package candidate was the one attempted.
- The publish failure occurred at npm registry publication time.
- Registry state confirms the candidate was not published.
- The failure is consistent with npm account, authentication, package ownership, or `@docushell`
  scope permission state that must be resolved outside the repository.
- This is not a package-content approval failure and not a public wording closeout.

## Required Follow-Up

- Retrying `npm publish` remains blocked.
- Resolve npm account, authentication, or `@docushell` scope permission before any retry.
- Record a new approval or unblocker lane before retrying publication.
- Registry closeout remains blocked until `@docushell/ethos-pdf@0.1.2` is visible on npm.
- Public installation wording remains blocked.

## Non-Actions

- This record does not approve another `npm publish` attempt.
- This record does not publish the npm package.
- This record does not change package contents.
- This record does not change public installation wording.
- This record does not approve hosted surfaces.
- This record does not approve production positioning.
- This record does not approve Windows packaged artifacts.
- This record does not approve bundled project-maintained PDFium builds.
- This record does not approve public benchmark reports.
- This record does not approve public benchmark claims.
- This record does not approve `ethos-doc`.
- This record does not approve `ethos-rag`.

## Retained Blockers

- Actual npm publication remains blocked.
- Public installation wording remains blocked.
- Registry closeout remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Commands

```sh
npm view @docushell/ethos-pdf versions --json
npm view @docushell/ethos-pdf version
npm view @docushell/ethos-pdf@0.1.2 version
python3 .github/scripts/test_patch_0_1_2_npm_publication_blocker.py
python3 .github/scripts/test_patch_0_1_2_npm_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_npm_publication_approval_request.py
python3 .github/scripts/test_npm_tarball_candidate_evidence.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 npm publication blocker recorded
The attempted @docushell/ethos-pdf@0.1.2 publish failed with npm E404
Registry verification confirms @docushell/ethos-pdf@0.1.2 is not published
Retry remains blocked until npm account/scope access is resolved and a new unblocker or approval lane passes
```
