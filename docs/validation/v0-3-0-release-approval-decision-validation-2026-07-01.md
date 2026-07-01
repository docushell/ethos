# v0.3.0 Release Approval Decision Validation - 2026-07-01

Validated source HEAD before this record: `57e3821`.

v0.3.0 release approval decision source commit:
`57e3821b63b119ee6ca8e52322ddde2fb05dde66`.

v0.3.0 release approval decision source tree:
`7fd3dd7bcd4d8b503483a06752fdc5e5cb587695`.

Status: **v0.3.0 release approval decision recorded; release-candidate source activation may
begin on `dev/v0-3-approval-packet`; package publication, tag creation, artifact publication,
npm alignment, installable wording, and DocuShell integration remain blocked**

This record accepts the exact app-answer-release contract release-prep packet after decider
instruction on 2026-07-01 to prepare `0.3.0` and start release-candidate work. It authorizes
release-candidate source metadata activation on `dev/v0-3-approval-packet` only. It does not run
`cargo publish`, publish any crate, upload to PyPI, run `npm publish`, create a GitHub Release,
upload CLI artifacts, create release tags, create package tags, change installable public wording,
approve hosted surfaces, approve production positioning, approve Windows packaged artifacts,
approve bundled project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`,
approve public benchmark reports or claims, or approve DocuShell integration.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.3.0 app-answer-release release-candidate approval decision
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/app-answer-release-contract-release-prep-validation-2026-07-01.md`
- Approval request source commit accepted by this decision:
  `d386568ef680f36f4a395543b21d34d2b17baccb`
- Approval request source tree accepted by this decision:
  `5891ab9c1e2fb4a9094d3d52c59ec57630aa871f`
- Approval decision source commit:
  `57e3821b63b119ee6ca8e52322ddde2fb05dde66`
- Approval decision source tree:
  `7fd3dd7bcd4d8b503483a06752fdc5e5cb587695`

## Exact Decision Fields

- Decision: accept the exact app-answer-release contract release-prep packet for `0.3.0`
  release-candidate source activation.
- Approver: `docushell-admin` acting as decider.
- Operator: `docushell-admin`.
- Closeout owner: `docushell-admin`.
- Date: 2026-07-01.
- Branch decision: continue on `dev/v0-3-approval-packet` as the release-candidate source
  activation branch.
- Exact target version accepted by this decision: `0.3.0`.
- Exact Rust crate set accepted by this decision:
  - `ethos-doc-core = 0.3.0`;
  - `ethos-verify = 0.3.0`;
  - `ethos-pdf = 0.3.0`.
- Exact Rust app-release decision accepted by this decision: ship
  `VerificationReport::proof_summary()` and `derive_app_answer_release_decision(...)` through the
  `ethos-doc-core` `verify-types` feature as the deterministic reference path for the public Rust
  helper.
- Exact Python decision accepted by this decision: activate Python source metadata for
  `ethos-pdf==0.3.0` so the package can carry `proof_summary(...)` and
  `app_answer_release_decision(...)`. The package name remains historical; this decision does not
  add a parser-quality claim, a hosted API, or a pure-Python document parser.
- Exact npm decision accepted by this decision: keep npm out of scope by default.
  `@docushell/ethos-pdf@0.2.1` remains the current public CLI binary distribution package. This
  decision does not approve a Node API, Node SDK, N-API binding, WASM package, npm metadata bump,
  npm vendor refresh, or `npm publish`.
- Exact CLI artifact decision accepted by this decision: keep GitHub Release CLI artifact
  publication out of scope by default. A full lockstep CLI artifact release requires a later
  explicit decision and artifact evidence.
- Exact tag decision accepted by this decision: release tag `v0.3.0` and package tags remain
  blocked until separate publication/smoke evidence and closeout records pass.

## Approved Release-Candidate Work

After this decision record is recorded, release-candidate work may begin on
`dev/v0-3-approval-packet` with only these changes:

- bump Rust workspace/package dependency versions from `0.2.0` to `0.3.0`;
- bump Python metadata and `ethos_pdf.__version__` from `0.2.0` to `0.3.0`;
- leave npm `@docushell/ethos-pdf` metadata at `0.2.1`;
- add `docs/v0-3-0-release-prep.md`;
- finalize `CHANGELOG.md` release-candidate entries;
- update validation indexes for approval and source activation records;
- keep public install commands on the current published `0.2.0` Rust/Python and `0.2.1` npm
  surfaces.

## Product Boundary

The accepted app-answer-release lane keeps these ownership lines:

- Ethos owns citation grounding and derived proof summaries.
- Applications own question relevance labels.
- Applications own source-fact, synthesis, and unsupported-claim labels.
- Applications own final, review, and blocked answer-release policy.

Safe product wording remains:

```text
Ethos verified citation grounding.
Answer relevance: direct, partial, or off-topic.
```

This decision does not approve complete-answer verification wording.

## Required Checks Before Publication Decisions

The release-candidate tree must pass:

```sh
make v0-3-release-prep PYTHON=python3
```

Rust package dry-runs, Python wheel evidence, CLI artifact evidence, npm artifact evidence, release
tag creation, package tag creation, and public install wording each require separate records before
any operator publication action.

## Non-Actions

- This decision record does not run `cargo publish`.
- This decision record does not publish any crate.
- This decision record does not upload to PyPI.
- This decision record does not publish any Python distribution.
- This decision record does not run `npm publish`.
- This decision record does not publish any npm package.
- This decision record does not create a GitHub Release.
- This decision record does not upload CLI artifacts.
- This decision record does not create a release tag.
- This decision record does not create package tags.
- This decision record does not approve installable `0.3.0` public wording.
- This decision record does not approve a Node API, Node SDK, N-API binding, or WASM package.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.
- This decision record does not approve DocuShell integration.

## Retained Blockers

- `cargo publish` remains blocked until release-candidate dry-runs pass and a separate operator
  publication decision is recorded.
- PyPI upload remains blocked until deterministic wheel evidence and a separate operator
  publication decision pass.
- npm metadata bump, npm vendor refresh, and `npm publish` remain blocked until a separate npm
  scope decision and package evidence pass.
- GitHub Release `v0.3.0` CLI artifact publication remains blocked until a separate CLI/artifact
  scope decision, artifact evidence, and operator decision pass.
- Release tag and package tag creation remain blocked until explicit closeout evidence passes.
- Installable `0.3.0` public wording remains blocked until registry/artifact availability and
  smoke closeout records pass.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- DocuShell integration remains blocked until `0.3.0` closeout or an explicit source-dependency
  decision is recorded.

## Commands

```sh
python3 .github/scripts/test_v0_3_0_release_approval_decision.py
python3 .github/scripts/test_app_answer_release_release_prep.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
make v0-3-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.3.0 release approval decision recorded
Release-candidate source activation may begin on dev/v0-3-approval-packet for Rust and Python
source metadata only
Package publication, tag creation, artifact publication, npm alignment, installable wording, and
DocuShell integration remain blocked pending separate evidence records and operator decisions
```
