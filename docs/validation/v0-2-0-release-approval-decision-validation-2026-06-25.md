# v0.2.0 Release Approval Decision Validation - 2026-06-25

Validated source HEAD before this record: `bebc3b0`.

v0.2.0 release approval decision source commit:
`bebc3b0a2a20fd762ad70351291222c162631eb6`.

v0.2.0 release approval decision source tree:
`90b19b657df2df50a957a991dcde7b9474e1f758`.

Status: **v0.2.0 release approval decision recorded; release-candidate version activation may
begin on the current branch; package publication, tag creation, artifact publication, and
installable wording remain blocked**

This record accepts the exact `v0.2.0` release approval request packet after decider approval. It
authorizes release-candidate version activation on the current branch only. It does not run
`cargo publish`, publish any crate, upload to PyPI, run `npm publish`, create a GitHub Release,
upload CLI artifacts, create release tags, create package tags, change installable public wording,
approve hosted surfaces, approve production positioning, approve Windows packaged artifacts,
approve bundled project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or
approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.2.0 release-candidate approval decision
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/v0-2-0-release-approval-request-validation-2026-06-25.md`
- Approval request source commit accepted by this decision:
  `fa15fa6f60993e30aa90540526903e4eb72c8252`
- Approval request source tree accepted by this decision:
  `983f484ff1249ee3ea88da79ebafa9d2cd2410f5`
- Approval decision source commit:
  `bebc3b0a2a20fd762ad70351291222c162631eb6`
- Approval decision source tree:
  `90b19b657df2df50a957a991dcde7b9474e1f758`

## Exact Decision Fields

- Decision: accept the exact `v0.2.0` release approval request packet.
- Approver: `docushell-admin` acting as decider.
- Operator: `docushell-admin`.
- Closeout owner: `docushell-admin`.
- Date: 2026-06-25.
- Branch decision: continue on `dev/v0-2-approval-packet` as the release-candidate working branch
  per operator instruction; do not create a separate branch for this lane unless a later explicit
  instruction changes that.
- Exact target version accepted by this decision: `0.2.0`.
- Exact Rust crate set accepted by this decision:
  - `ethos-doc-core = 0.2.0`;
  - `ethos-verify = 0.2.0`;
  - `ethos-pdf = 0.2.0`.
- Exact `ethos-pdf` continuity decision accepted by this decision: keep `ethos-pdf` as the
  continuity crate for `v0.2.0`; JSON verify and evidence-anchor paths remain PDFium-free, while
  parser, crop, and render paths continue to use caller-provided PDFium.
- Exact Python decision accepted by this decision: Python is public in `v0.2.0` only as
  `ethos-pdf==0.2.0` with all of these required together:
  - PyPI wheel;
  - `v0.2.0` macOS arm64 and Linux x64 CLI artifacts usable by the Python wrapper;
  - docs explaining that `ethos-pdf` is historical package naming and that JSON verify/anchor
    methods call a caller-provided `ethos` CLI binary.
- Exact npm decision accepted by this decision: `@docushell/ethos-pdf@0.2.0` may remain in scope
  only as a CLI binary distribution package. This decision does not approve a Node API, Node SDK,
  N-API binding, or WASM package.
- Exact CLI artifact decision accepted by this decision: prepare macOS arm64 and Linux x64 GitHub
  Release CLI artifacts for `v0.2.0`; Windows packaged artifacts remain blocked.
- Exact tag and package-tag decision accepted by this decision:
  - release tag candidate: `v0.2.0`;
  - package tag candidates: `ethos-package-ethos-doc-core-0.2.0`,
    `ethos-package-ethos-verify-0.2.0`, and `ethos-package-ethos-pdf-0.2.0`;
  - actual tag creation remains blocked until publication/smoke evidence and closeout records pass.
- ADR-0006/name ownership accepted by this decision: retain `docushell/ethos` as the canonical
  source repository, `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` as the requested priority
  crates, `ethos-pdf` as the PyPI package/import surface `ethos_pdf`, and
  `@docushell/ethos-pdf` as the npm CLI package identity.
- `reserved_crates_io_version` handling accepted by this decision: keep
  `reserved_crates_io_version = "0.0.0-reserved.0"` as historical reservation metadata in the
  crate manifests. The real package version comes from the workspace/package version and may be
  bumped to `0.2.0` during release-candidate version activation.
- crates.io append-only risk accepted by this decision: once `0.2.0` is published to crates.io,
  the exact version cannot be deleted or overwritten. A bad publish can only be yanked, so the
  operator must stop on any version, source, artifact, README, license, dependency, or index
  mismatch.

## Approved Release-Candidate Work

After this decision record is merged and validation passes, release-candidate work may begin on
`dev/v0-2-approval-packet` with only these changes:

- bump Rust workspace/package dependency versions from `0.1.2` to `0.2.0`;
- bump Python metadata and `ethos_pdf.__version__` from `0.1.2` to `0.2.0`;
- bump npm `@docushell/ethos-pdf` from `0.1.2` to `0.2.0`;
- finalize `CHANGELOG.md`;
- update version-pinned docs to release-candidate wording, not installable wording.

## Required Checks Before Publication Decisions

The release-candidate tree must pass:

```sh
make v0-2-release-prep PYTHON=python3
cargo publish --dry-run -p ethos-doc-core
```

Python, npm, and CLI package/build checks must pass before those surfaces move to any separate
operator publication decision. `ethos-verify` and `ethos-pdf` dry-runs belong after
`ethos-doc-core 0.2.0` is visible in the crates.io index.

## DocuShell Pilot Boundary

The DocuShell wedge remains an internal/design-partner "Evidence-Checked Answers" pilot, not a
public launch.

The accepted pilot learning goals are:

- claim extraction quality;
- non-PDF ingestion.

This decision does not approve hosted DocuShell surfaces, public SaaS positioning, or production
positioning.

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
- This decision record does not approve installable `0.2.0` public wording.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Retained Blockers

- `cargo publish` remains blocked until release-candidate dry-runs pass and a separate operator
  publication decision is recorded.
- PyPI upload remains blocked until deterministic wheel evidence and a separate operator
  publication decision pass.
- `npm publish` remains blocked until package evidence and a separate operator publication decision
  pass.
- GitHub Release `v0.2.0` CLI artifact publication remains blocked until artifact evidence and a
  separate operator publication decision pass.
- Release tag and package tag creation remain blocked until explicit closeout evidence passes.
- Installable `0.2.0` public wording remains blocked until registry/artifact availability and
  smoke closeout records pass.
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
python3 .github/scripts/test_v0_2_0_release_approval_decision.py
python3 .github/scripts/test_v0_2_0_release_approval_request.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
make v0-2-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.2.0 release approval decision recorded
Release-candidate version activation may begin on dev/v0-2-approval-packet for Rust, Python, npm,
CHANGELOG, and release-candidate wording only
Package publication, tag creation, artifact publication, and installable wording remain blocked
pending separate evidence records and operator decisions
```
