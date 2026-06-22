# Milestone E Package Publication Publish-Flag Activation Request Validation - 2026-06-22

## Purpose

Record the exact publish-flag and package metadata activation request after the final
package-publication approval decision.

This record does not remove `publish = false`, change package metadata, create package tags, run
`cargo publish`, or invite public installation. It records the exact source activation diff that
requires decider review before package tag source binding can move forward.

## Status

Status: **pass for publish-flag activation request with activation blocked**.

Decision: exact publish-flag activation request recorded for decider review.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `cea2018`
- Activation request source commit: `cea20182e11271bf83675c12de43498df9c42c18`
- Activation request source tree: `8c7076b0997fe925827bb81f859b74790a4d8b16`
- Lane: package publication
- Final approval decision record:
  `docs/validation/milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md`
- Approval owner requested: `docushell-admin`

## Exact Request Fields

- Decision requested: approve exact publish-flag and package metadata activation diff.
- Approver requested: docushell-admin acting as decider.
- Date requested: 2026-06-22.
- Exact activation crate list requested: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` only.
- Exact activation diff requested: remove `publish = false` from the three accepted candidate
  manifests only.
- Exact metadata diff requested: change `publication_status = "blocked"` to
  `publication_status = "approved_for_crates_io_publication"` in the three accepted candidate
  manifests only.
- Exact crate manifests requested for activation:
  `crates/ethos-core/Cargo.toml`, `crates/ethos-verify/Cargo.toml`, and
  `crates/ethos-pdf/Cargo.toml`.
- Exact crate READMEs requested for activation: update only the candidate package status language
  so it no longer says `publish = false` remains set.
- Non-candidate workspace crates remain unchanged and retain `publish = false`.
- Package tag source binding impact: the previous accepted source binding keeps `publish = false`;
  package tag source binding must be refreshed after the activation diff is applied and reviewed.
- Exact package tag names retained as candidates: `ethos-package-ethos-doc-core-0.1.0`,
  `ethos-package-ethos-verify-0.1.0`, and `ethos-package-ethos-pdf-0.1.0`.
- Exact package version map retained as candidates: `ethos-doc-core = 0.1.0`,
  `ethos-verify = 0.1.0`, and `ethos-pdf = 0.1.0`.

## Explicit Exclusions

- package tag creation remains blocked
- real-version cargo publish remains blocked
- public installation instructions remain blocked
- wheels remain blocked
- npm packages remain blocked
- binaries remain blocked
- hosted surfaces remain blocked
- production positioning remains blocked
- public benchmark reports remain blocked
- public benchmark claims remain blocked
- project-maintained PDFium builds remain blocked
- `ethos-doc` remains excluded
- `ethos-rag` remains excluded
- broader public wording remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Retained Blockers

- activation remains blocked until the exact diff is reviewed and accepted
- package tag source binding must be refreshed after activation is applied
- package tag creation remains blocked until the refreshed source binding is accepted
- real-version cargo publish remains blocked until activated source evidence and operator evidence
  are present
- public installation instructions remain blocked until registry availability is verified

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_publish_flag_activation_request.py
python3 .github/scripts/test_milestone_e_package_publication_final_approval_decision.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Publish-flag activation request validation passed
Exact activation diff was recorded for decider review
Current source manifests retained publish=false and publication_status=blocked
No package tag was created
No package was published
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
