# Milestone E Package Publication Public Installation Wording Review Validation - 2026-06-21

## Purpose

Record the public installation wording review boundary for the package publication approval lane
without approving public installation, package publication, Cargo manifest changes, package
dependency manifest activation, registry-backed dependent package assembly activation, package tag
creation, or package publication version selection.

## Status

Status: **pass for package public installation wording review with publication blocked**.

Decision: record candidate public installation wording for later approval review only.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `8b446e3`
- Public installation wording review source commit: `8b446e3554c9b4b223e43ee46d218c47a7931c76`
- Public installation wording review source tree: `385dd7799cf898fc850555ce13d6d74e8ee15196`
- Lane: package publication
- Reviewed registry assembly evidence record: `docs/validation/milestone-e-package-publication-registry-assembly-evidence-review-validation-2026-06-21.md`

## Candidate Wording Under Review

Candidate public installation wording for later review only:

```text
Ethos Rust crates are proposed for crates.io installation after dedicated package-publication approval. The first candidate crate surface is limited to ethos-doc-core, ethos-verify, and ethos-pdf. Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports, public benchmark claims, release artifacts, project-maintained PDFium builds, ethos-doc, and ethos-rag remain excluded.
```

This candidate wording is not approved public wording and must not be used as installation
instructions until a later dedicated package publication approval decision records exact wording,
exact candidate crates, exact package version, exact package tag source binding, exact manifest
activation diff, exact registry-backed dependent package assembly evidence, and passing
public-surface posture and claims gates after the exact wording change.

## Evidence Review

- No public installation wording is approved by this record.
- Public installation remains blocked.
- Package publication remains blocked.
- The candidate wording limits any later approval review to `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf`.
- `ethos-doc` and `ethos-rag` remain excluded.
- Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark
  reports, public benchmark claims, release artifacts, and project-maintained PDFium builds remain
  excluded.
- The wording review must be followed by public-surface posture and claims gates after any exact
  public installation wording change.

## Approval Inputs Still Required

- exact package publication approval decision record remains required
- decider signoff on the exact candidate version map remains required
- decider signoff on the exact package tag name set and source binding remains required
- package dependency manifest activation approval remains required
- registry-backed dependent package assembly evidence after manifest activation remains required
- exact public installation wording approval remains required
- public-surface posture check after exact public installation wording changes remains required
- claims gate after exact public installation wording changes remains required
- make milestone-e-prep after exact decision record remains required

## Non-Approvals

- this public installation wording review does not select a package publication version
- this public installation wording review does not create a package tag
- this public installation wording review does not change Cargo manifests
- this public installation wording review does not activate package dependency manifests
- this public installation wording review does not create a registry
- this public installation wording review does not activate registry-backed dependent package assembly
- this public installation wording review does not invite public installation
- this public installation wording review does not approve public installation wording
- this public installation wording review does not approve package publication

## Retained Blockers

- candidate package version map is recorded but no package publication version is selected
- candidate package tag names are recorded but no package tag is created
- candidate manifest activation diff is reviewed but no Cargo manifest is changed
- package dependency manifest activation remains blocked
- registry-backed dependent package assembly evidence remains required
- registry-backed dependent package assembly activation remains blocked
- public installation wording approval remains blocked
- public installation remains blocked
- package publication remains blocked
- real-version cargo publish remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_registry_assembly_evidence_review.py
python3 .github/scripts/test_milestone_e_package_publication_public_installation_wording_review.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Package publication public installation wording review validation passed
Candidate public installation wording is recorded for later approval review only
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
