# Milestone E Package Publication Approval Decision Validation - 2026-06-21

## Purpose

Record the package publication approval decision for the current package-publication request after
the approval decision template.

This decision record rejects package publication approval for the current source state because the
required activation evidence is still absent. It does not approve package publication, public
installation, package dependency manifest activation, registry-backed dependent package assembly
activation, package tag creation, or package publication version selection.

## Status

Status: **pass for package publication approval decision with publication blocked**.

Decision: **reject current package publication approval request**.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `fdbd5b7`
- Approval decision source commit: `fdbd5b7e1817ab73d459f25faadc2132263d88ff`
- Approval decision source tree: `4a7bf5cda2c779e41a04c3feb691a12fec1e5c8d`
- Lane: package publication
- Template record:
  `docs/validation/milestone-e-package-publication-approval-decision-template-validation-2026-06-21.md`
- Approval owner: docushell-admin acting as decider

## Exact Decision Fields

- Decision: reject current package publication approval request.
- Approver: docushell-admin acting as decider.
- Date: 2026-06-21.
- Exact candidate crate list reviewed for this decision: `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf` only.
- Exact package version map approved by this decision: none; candidate `0.1.0` remains unapproved.
- Exact package tag name set approved by this decision: none; candidate package tags remain
  uncreated and unapproved.
- Exact package tag source commit and source tree approved by this decision: none.
- Exact package-name migration diff for `ethos-doc-core` approved by this decision: none; current
  Cargo manifests remain unchanged.
- Exact dependency manifest activation diff for `ethos-verify` and `ethos-pdf` approved by this
  decision: none; current Cargo manifests remain unchanged.
- Exact registry-backed dependent package assembly evidence after manifest activation: absent; no
  registry is created and no registry-backed assembly is activated.
- Exact public installation wording approved by this decision: none; public installation wording
  remains blocked.
- Public-surface posture check result after this decision: passed with no public installation
  wording approval.
- Claims gate result after this decision: passed with package publication blocked.
- Milestone E prep result after this decision record: required for this record branch.

## Reviewed Candidate Inputs

- Candidate crate surface reviewed: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`.
- `ethos-doc` and `ethos-rag` remain excluded.
- Candidate version map reviewed: `0.1.0` for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`;
  not selected or approved.
- Candidate package tag names reviewed: `ethos-package-ethos-doc-core-0.1.0`,
  `ethos-package-ethos-verify-0.1.0`, and `ethos-package-ethos-pdf-0.1.0`; not created or
  approved.
- Candidate manifest activation diff reviewed; current Cargo manifests remain unchanged.
- Registry-backed dependent package assembly evidence requirements reviewed; no registry is
  created and no assembly is activated.
- Candidate public installation wording reviewed; no wording is approved.

## Explicit Exclusions

- Package publication remains blocked.
- Public installation remains blocked.
- Real-version cargo publish remains blocked.
- Package tag creation remains blocked.
- Package dependency manifest activation remains blocked.
- Registry-backed dependent package assembly activation remains blocked.
- Release artifacts remain blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- npm packages remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Project-maintained PDFium builds remain blocked.
- `ethos-doc` remains excluded.
- `ethos-rag` remains excluded.
- Broader public wording remains blocked.
- Public reports remain blocked.
- Public result wording remains blocked.
- Performance claims remain blocked.
- Quality claims remain blocked.
- Footprint claims remain blocked.
- Table-quality claims remain blocked.
- Parser-quality claims remain blocked.

## Required Before A Future Approval Request

- Select an exact package version map for the candidate crates.
- Select exact package tag names and source binding.
- Prepare and review exact package-name migration and dependency manifest activation diffs.
- Produce registry-backed dependent package assembly evidence after manifest activation.
- Approve exact public installation wording and explicit exclusions.
- Run public-surface posture and claims gates after exact wording changes.
- Run Milestone E prep after the exact decision record.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_decision_record.py
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_approval_decision_template.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Package publication approval decision validation passed
Current package publication approval request was rejected for this source state
No package publication version was selected
No package tag was created
No Cargo manifest was changed
No registry was created
No registry-backed assembly was activated
No public installation wording was approved
Package publication and public installation remained blocked
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
