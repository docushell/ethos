# Milestone E Package Publication Approval Decision Template Validation - 2026-06-21

## Purpose

Record the exact package publication approval decision template for the package publication lane
without approving package publication, public installation, Cargo manifest changes, package
dependency manifest activation, registry-backed dependent package assembly activation, package tag
creation, or package publication version selection.

## Status

Status: **pass for package publication approval decision template with publication blocked**.

Decision: **not approved pending exact decider input**.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `66979cc`
- Approval decision template source commit: `66979ccce3585c6e99ace484350ea6f84816d046`
- Approval decision template source tree: `58ef15e1cac8ce7df35a7e88da2044e57eb66c10`
- Lane: package publication
- Reviewed wording record: `docs/validation/milestone-e-package-publication-public-installation-wording-review-validation-2026-06-21.md`

## Exact Decision Fields Required Later

A later approval decision must provide all of these fields exactly:

- Decision: approve or reject.
- Approver: named decider.
- Date.
- Exact candidate crate list.
- Exact SemVer package version or exact per-crate version map.
- Exact package tag name set.
- Exact package tag source commit and source tree.
- Exact package-name migration diff for `ethos-doc-core`.
- Exact dependency manifest activation diff for `ethos-verify` and `ethos-pdf`.
- Exact registry-backed dependent package assembly evidence after manifest activation.
- Exact public installation wording.
- Explicit exclusions for wheels, npm packages, binaries, hosted surfaces, production positioning,
  public benchmark reports, public benchmark claims, release artifacts, project-maintained PDFium
  builds, `ethos-doc`, and `ethos-rag`.
- Public-surface posture check result after exact wording changes.
- Claims gate result after exact wording changes.
- Milestone E prep result after the exact decision record.

## Candidate Inputs Available For Later Review

- Candidate crate surface: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`.
- Candidate version map: `0.1.0` for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`, not
  selected or approved.
- Candidate package tag names: `ethos-package-ethos-doc-core-0.1.0`,
  `ethos-package-ethos-verify-0.1.0`, and `ethos-package-ethos-pdf-0.1.0`, not created.
- Candidate manifest activation diff: reviewed, while current Cargo manifests remain unchanged.
- Registry-backed dependent package assembly evidence requirements: reviewed, while no registry is
  created and no registry-backed assembly is activated.
- Candidate public installation wording: reviewed for later approval only, not approved.

## Non-Approvals

- this approval decision template does not approve package publication
- this approval decision template does not approve public installation
- this approval decision template does not approve public installation wording
- this approval decision template does not select a package publication version
- this approval decision template does not create a package tag
- this approval decision template does not change Cargo manifests
- this approval decision template does not activate package dependency manifests
- this approval decision template does not create a registry
- this approval decision template does not activate registry-backed dependent package assembly

## Retained Blockers

- exact decider approval remains required
- no package publication version is selected
- no package tag is created
- no package dependency manifest activation is approved
- no registry-backed dependent package assembly activation is approved
- public installation wording approval remains blocked
- public installation remains blocked
- package publication remains blocked
- real-version cargo publish remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_public_installation_wording_review.py
python3 .github/scripts/test_milestone_e_package_publication_approval_decision_template.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Package publication approval decision template validation passed
Decision remains not approved pending exact decider input
No public installation wording was approved
No package version was selected
No package tag was created
No Cargo manifest was changed
No registry was created
No registry-backed assembly was activated
Package publication and public installation remained blocked
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
