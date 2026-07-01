# App Answer Release Contract Release Prep Validation - 2026-07-01

Validated source HEAD before this record: `d386568`.

app-answer-release contract release prep source commit:
`d386568ef680f36f4a395543b21d34d2b17baccb`.

app-answer-release contract release prep source tree:
`5891ab9c1e2fb4a9094d3d52c59ec57630aa871f`.

Status: **app-answer-release contract release-prep packet recorded; version bump, package
publication, tag creation, artifact publication, installable `0.3.0` wording, npm publication,
and DocuShell integration remain blocked**

This record prepares the next decider review for the app-answer-release contract that landed on
`main`. It does not approve or perform a version bump, create a release-candidate branch, run
`cargo publish`, upload to PyPI, run `npm publish`, create a GitHub Release, upload CLI artifacts,
create release or package tags, change public install wording, approve hosted surfaces, approve
production positioning, approve Windows packaged artifacts, approve bundled project-maintained
PDFium builds, approve `ethos-doc`, approve `ethos-rag`, approve public benchmark reports, or
approve DocuShell integration.

## Subject

- Repository: `docushell/ethos`
- Lane: app-answer-release contract release prep
- Prep source commit: `d386568ef680f36f4a395543b21d34d2b17baccb`
- Prep source tree: `5891ab9c1e2fb4a9094d3d52c59ec57630aa871f`
- Current published baseline: `0.2.0` Rust and Python surfaces, npm
  `@docushell/ethos-pdf@0.2.1`, and GitHub Release `v0.2.0` macOS arm64/Linux x64 CLI artifacts.
- Suggested target version for decider review: `0.3.0`.
- Target version proposal is not an approval.

## Source Surfaces In Scope

The merged source candidate contains the app-answer-release contract path:

- `docs/app-answer-release-contract.md`
- `schemas/ethos-app-answer-release-decision.schema.json`
- `schemas/examples/app-answer-release-decision.example.json`
- `examples/app-answer-release/README.md`
- `examples/app-answer-release/run_python_demo.py`
- `examples/app-answer-release/verification-report.json`
- `examples/app-answer-release/proof-summary.json`
- `examples/app-answer-release/claims.json`
- `examples/app-answer-release/expected-decision.json`
- Rust `derive_app_answer_release_decision(...)` and `VerificationReport::proof_summary()` under
  the `ethos-doc-core` `verify-types` feature.
- Python `proof_summary(...)` and `app_answer_release_decision(...)` exported by `ethos_pdf`.
- CI/source guards: `make app-answer-release-contract PYTHON=python3` and
  `make app-answer-release-demo PYTHON=python3`.

## Package Surface Decisions Requested

- Rust decision requested: decide whether the next public Rust release should carry the app
  helper through `ethos-doc-core`. Because this workspace uses lockstep source versions, a
  proposed `0.3.0` Rust release should explicitly decide whether the public Rust crate set remains
  `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` together.
- Python decision requested: decide whether the Python helper should ship as `ethos-pdf==0.3.0`.
  The package name remains historical; the helper does not add PDF parsing, an LLM demo, or a
  hosted API.
- npm decision requested: keep npm out of scope by default. `@docushell/ethos-pdf` is currently a
  CLI binary distribution package, not a Node API or Node SDK. A CLI alignment release would need a
  separate explicit decision.
- CLI artifact decision requested: keep GitHub Release CLI artifact publication out of scope by
  default unless the decider chooses a full lockstep CLI/artifact release.
- Tag decision requested: keep release tag `v0.3.0` and any package tags blocked until an exact
  approval decision and later evidence records pass.

## Product Boundary Preserved

The contract keeps these ownership lines:

- Ethos owns citation grounding and derived proof summaries.
- Applications own question relevance labels.
- Applications own source-fact, synthesis, and unsupported-claim labels.
- Applications own final, review, and blocked answer-release policy.

The release packet must not describe Ethos as verifying complete answers. Safe wording remains:

```text
Ethos verified citation grounding.
Answer relevance: direct, partial, or off-topic.
```

## Non-Approvals

- This prep record does not approve a version bump.
- This prep record does not create a release-candidate branch.
- This prep record does not approve `cargo publish`.
- This prep record does not publish any crate.
- This prep record does not approve PyPI upload.
- This prep record does not upload any Python distribution.
- This prep record does not approve `npm publish`.
- This prep record does not publish any npm package.
- This prep record does not create a GitHub Release.
- This prep record does not upload CLI artifacts.
- This prep record does not create a release tag.
- This prep record does not create package tags.
- This prep record does not approve installable `0.3.0` public wording.
- This prep record does not approve a Node API, Node SDK, N-API binding, or WASM package.
- This prep record does not approve hosted surfaces.
- This prep record does not approve production positioning.
- This prep record does not approve Windows packaged artifacts.
- This prep record does not approve bundled project-maintained PDFium builds.
- This prep record does not approve public benchmark reports.
- This prep record does not approve public benchmark claims.
- This prep record does not approve `ethos-doc`.
- This prep record does not approve `ethos-rag`.
- This prep record does not approve DocuShell integration.

## Retained Blockers

- Explicit decider approval remains required before any `0.3.0` release-candidate branch.
- Rust workspace/package version bump remains blocked until approval.
- Python metadata and `ethos_pdf.__version__` bump remain blocked until approval and Python scope
  acceptance.
- npm package version bump remains blocked unless a separate npm CLI alignment decision is
  accepted.
- `CHANGELOG.md` final release wording remains blocked until approval.
- `cargo publish` remains blocked until release-candidate dry-runs pass and a separate operator
  action is approved.
- PyPI upload remains blocked until Python scope is accepted and deterministic wheel evidence
  passes.
- `npm publish` remains blocked until npm scope is accepted and package evidence passes.
- GitHub Release CLI artifact publication remains blocked unless the release scope explicitly
  includes CLI artifacts and artifact evidence passes.
- Release tag and package tag creation remain blocked until explicit approval and closeout
  evidence pass.
- Installable `0.3.0` public wording remains blocked until registry/artifact availability and
  smoke closeout records pass.
- DocuShell integration remains blocked until the contract is released or an explicit
  source-dependency decision is recorded.

## Guard Commands

```sh
cargo fmt --check
make app-answer-release-contract PYTHON=python3
python3 .github/scripts/test_app_answer_release_release_prep.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
git diff --check
```

## Result

```text
app-answer-release contract release-prep packet recorded
Suggested target version, source surfaces, package-surface decisions, product boundary,
non-approvals, retained blockers, and guard commands were recorded
version bump, package publication, tag creation, artifact publication, installable wording, npm
publication, and DocuShell integration remain blocked pending explicit approval and later evidence
records
```
