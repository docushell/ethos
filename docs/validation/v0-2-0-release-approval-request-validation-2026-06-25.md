# v0.2.0 Release Approval Request Validation - 2026-06-25

Validated source HEAD before this record: `fa15fa6`.

v0.2.0 release approval request source commit:
`fa15fa6f60993e30aa90540526903e4eb72c8252`.

v0.2.0 release approval request source tree:
`983f484ff1249ee3ea88da79ebafa9d2cd2410f5`.

Status: **v0.2.0 release approval request recorded; version bump, package publication, tag
creation, artifact publication, and installable wording remain blocked**

This record requests decider review for the exact `v0.2.0` release-candidate scope. It does not
approve or perform a version bump, create a release-candidate branch, run `cargo publish`, upload
to PyPI, run `npm publish`, create a GitHub Release, upload CLI artifacts, create package tags,
change public install wording, approve hosted surfaces, approve production positioning, approve
Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`,
approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.2.0 release-candidate approval packet
- Approval source commit: `fa15fa6f60993e30aa90540526903e4eb72c8252`
- Approval source tree: `983f484ff1249ee3ea88da79ebafa9d2cd2410f5`
- Current source version baseline before approval: `0.1.2`
- Requested target version after approval: `0.2.0`
- Prepared release promise:
  - JSON verification over caller-provided sources.
  - JSON evidence anchoring over caller-provided sources.
  - PDFium-free verify and evidence-anchor paths.
  - PDFium remains caller-provided for parser, crop, and render paths that need PDF parsing.

## Exact Request Fields

- Decision requested: approve creation of a release-candidate branch for exact `v0.2.0` version
  activation and artifact preparation.
- Approver requested: `docushell-admin` acting as decider.
- Operator requested: `docushell-admin`, or a named replacement explicitly accepted in the
  approval decision.
- Closeout owner requested: `docushell-admin`, or a named replacement explicitly accepted in the
  approval decision.
- Date requested: 2026-06-25.
- Exact source commit requested: `fa15fa6f60993e30aa90540526903e4eb72c8252`.
- Exact source tree requested: `983f484ff1249ee3ea88da79ebafa9d2cd2410f5`.
- Version-bump plan requested:
  - bump Rust workspace/package dependency versions from `0.1.2` to `0.2.0`;
  - bump Python metadata and `ethos_pdf.__version__` from `0.1.2` to `0.2.0` if Python is
    accepted in scope;
  - bump npm `@docushell/ethos-pdf` from `0.1.2` to `0.2.0` if npm is accepted in scope;
  - finalize `CHANGELOG.md`;
  - update version-pinned docs to release-candidate wording, not installable wording, until
    registry/artifact smoke and closeout records pass.
- Exact Rust crate set requested:
  - `ethos-doc-core = 0.2.0`;
  - `ethos-verify = 0.2.0`;
  - `ethos-pdf = 0.2.0`.
- Explicit `ethos-pdf` continuity decision requested: keep `ethos-pdf` in the `v0.2.0` crate set
  as the continuity crate. The JSON verify and evidence-anchor promise does not require PDFium,
  while PDF parser/crop/render paths continue to use caller-provided PDFium.
- Python decision requested: include Python `ethos-pdf==0.2.0` in public `v0.2.0` only if the
  release includes all of these together:
  - PyPI wheel for `ethos-pdf==0.2.0`;
  - `v0.2.0` macOS arm64 and Linux x64 CLI artifacts usable by the Python wrapper;
  - docs explaining that `ethos-pdf` is historical package naming and that JSON verify/anchor
    methods call a caller-provided `ethos` CLI binary.
- npm `@docushell/ethos-pdf` fate requested: include `@docushell/ethos-pdf@0.2.0` only as a CLI
  binary distribution package if `v0.2.0` CLI artifacts are approved. This request does not approve
  a Node API, Node SDK, N-API binding, or WASM package.
- CLI artifact decision requested: prepare macOS arm64 and Linux x64 GitHub Release CLI artifacts
  for `v0.2.0`; Windows packaged artifacts remain blocked.
- Tag and package-tag approval requested:
  - release tag candidate: `v0.2.0`;
  - package tag candidates: `ethos-package-ethos-doc-core-0.2.0`,
    `ethos-package-ethos-verify-0.2.0`, and `ethos-package-ethos-pdf-0.2.0`;
  - tag creation remains blocked until explicit decision, publication/smoke evidence, and closeout
    records pass.
- ADR-0006/name ownership confirmation requested: retain `docushell/ethos` as the canonical
  source repository, `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` as the requested priority
  crates, `ethos-pdf` as the PyPI package/import surface `ethos_pdf`, and
  `@docushell/ethos-pdf` as the npm CLI package identity.
- `reserved_crates_io_version` handling requested: keep
  `reserved_crates_io_version = "0.0.0-reserved.0"` as historical reservation metadata in the
  crate manifests. The real package version comes from the workspace/package version and must be
  bumped to `0.2.0` only on the release-candidate branch after approval.
- crates.io append-only risk accepted for review: once `0.2.0` is published to crates.io, the
  exact version cannot be deleted or overwritten. A bad publish can only be yanked, so the operator
  must stop on any version, source, artifact, README, license, dependency, or index mismatch.

## Approval Sequence Requested

1. Accept or reject this exact approval packet.
2. After acceptance, create a release-candidate branch.
3. Apply only release-candidate version and wording changes on that branch.
4. Run:

```sh
make v0-2-release-prep PYTHON=python3
cargo publish --dry-run -p ethos-doc-core
```

5. Run Python, npm, and CLI package/build checks only for accepted surfaces.
6. Publish Rust crates in dependency order:
   - `ethos-doc-core`;
   - wait for crates.io index availability;
   - dry-run and publish `ethos-verify`;
   - dry-run and publish `ethos-pdf`.
7. Publish Python, npm, and CLI artifacts only if accepted in scope.
8. Smoke:
   - Rust bring-your-own-parser API;
   - CLI JSON verify;
   - CLI evidence anchor;
   - Python wrapper against the published CLI artifact if Python is accepted in scope.
9. Only after publication and smoke evidence, flip docs to installable `0.2.0` wording and rerun
   the claims gates.

## DocuShell Pilot Boundary

The DocuShell wedge remains an internal/design-partner "Evidence-Checked Answers" pilot, not a
public launch.

The pilot learning goals are:

- claim extraction quality;
- non-PDF ingestion.

Those learning goals decide whether the deterministic trust layer is easy to apply outside Ethos'
own parser path. This request does not approve hosted DocuShell surfaces, public SaaS positioning,
or production positioning.

## Non-Approvals

- This request record does not approve a version bump.
- This request record does not create a release-candidate branch.
- This request record does not approve `cargo publish`.
- This request record does not publish any crate.
- This request record does not approve PyPI upload.
- This request record does not upload any Python distribution.
- This request record does not approve `npm publish`.
- This request record does not publish any npm package.
- This request record does not create a GitHub Release.
- This request record does not upload CLI artifacts.
- This request record does not create a release tag.
- This request record does not create package tags.
- This request record does not approve installable `0.2.0` public wording.
- This request record does not approve hosted surfaces.
- This request record does not approve production positioning.
- This request record does not approve Windows packaged artifacts.
- This request record does not approve bundled project-maintained PDFium builds.
- This request record does not approve public benchmark reports.
- This request record does not approve public benchmark claims.
- This request record does not approve `ethos-doc`.
- This request record does not approve `ethos-rag`.

## Retained Blockers

- Explicit decider approval remains required before a release-candidate branch.
- Rust workspace/package dependency version bump remains blocked until approval.
- Python metadata and `__version__` bump remain blocked until approval and Python scope acceptance.
- npm package version bump remains blocked until approval and npm scope acceptance.
- `CHANGELOG.md` final release wording remains blocked until approval.
- `cargo publish` remains blocked until release-candidate dry-runs pass and a separate operator
  action is approved.
- PyPI upload remains blocked until Python scope is accepted and deterministic wheel evidence
  passes.
- `npm publish` remains blocked until npm scope is accepted and package evidence passes.
- GitHub Release `v0.2.0` CLI artifact publication remains blocked until artifact evidence and
  explicit approval pass.
- Release tag and package tag creation remain blocked until explicit approval and closeout evidence
  pass.
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
python3 .github/scripts/test_v0_2_0_release_approval_request.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
make v0-2-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.2.0 release approval request recorded
Exact source commit, version-bump plan, Rust crate set, ethos-pdf continuity, Python decision,
npm fate, CLI artifact decision, tag/package-tag request, ADR-0006 ownership, reserved crates.io
metadata handling, crates.io append-only risk, operator and closeout owner, DocuShell pilot
boundary, and retained blockers were recorded
version bump, package publication, tag creation, artifact publication, and installable wording
remain blocked pending explicit approval and later evidence records
```
