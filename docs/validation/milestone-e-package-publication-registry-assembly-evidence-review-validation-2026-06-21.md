# Milestone E Package Publication Registry-Assembly Evidence Review Validation - 2026-06-21

## Purpose

Record the registry-backed dependent package assembly evidence review boundary for the package
publication approval lane without creating a registry, activating registry-backed assembly,
changing Cargo manifests, selecting a package publication version, creating package tags, inviting
public installation, or approving package publication.

## Status

Status: **pass for package registry-assembly evidence review with publication blocked**.

Decision: record registry-backed dependent package assembly evidence requirements only.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `3f0f3ed`
- Registry assembly evidence review source commit: `3f0f3ed7939b7b55d8f5eb86938fa10447dd58c9`
- Registry assembly evidence review source tree: `6c748cd6f4a8de7789e42666697d1f25aa99f6f9`
- Lane: package publication
- Reviewed manifest diff record: `docs/validation/milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md`

## Evidence Requirements

- Registry-backed dependent package assembly evidence after manifest activation remains required.
- Any future evidence must bind reviewed candidate package artifacts for `ethos-doc-core`,
  `ethos-verify`, and `ethos-pdf`.
- The future `ethos-doc-core` candidate must be assembled before dependent candidates.
- The future `ethos-verify` dependent candidate must resolve dependency key `ethos-core` to
  candidate package `ethos-doc-core` and retain `features = ["grounding", "verify-types"]`.
- The future `ethos-pdf` dependent candidate must resolve dependency key `ethos-core` to
  candidate package `ethos-doc-core`, retain `features = ["full"]`, and keep the PDFium boundary
  confirmed.
- Any future assembly evidence must bind the exact source commit, source tree, candidate package
  manifests, selected SemVer package version, exact package tag name set, and public-surface
  posture and claims gates after exact wording changes.
- No registry-backed dependent package assembly evidence is activated by this record.

## Current Source State

- No Cargo manifest is changed by this record.
- No registry is created by this record.
- No registry-backed assembly is activated by this record.
- The current `crates/ethos-core/Cargo.toml` package name remains `ethos-core`.
- The current `crates/ethos-core/Cargo.toml`, `crates/ethos-verify/Cargo.toml`, and
  `crates/ethos-pdf/Cargo.toml` manifests remain `publish = false`.
- The current `crates/ethos-verify/Cargo.toml` and `crates/ethos-pdf/Cargo.toml` manifests do not
  reference `package = "ethos-doc-core"`.
- No candidate package tag is created for `ethos-doc-core`, `ethos-verify`, or `ethos-pdf`.

## Approval Inputs Still Required

- exact package publication approval decision record remains required
- decider signoff on the exact candidate version map remains required
- decider signoff on the exact package tag name set and source binding remains required
- package dependency manifest activation approval remains required
- registry-backed dependent package assembly evidence after manifest activation remains required
- public-surface posture check after exact public installation wording changes remains required
- claims gate after exact public installation wording changes remains required
- make milestone-e-prep after exact decision record remains required

## Non-Approvals

- this registry assembly evidence review does not select a package publication version
- this registry assembly evidence review does not create a package tag
- this registry assembly evidence review does not change Cargo manifests
- this registry assembly evidence review does not activate package dependency manifests
- this registry assembly evidence review does not create a registry
- this registry assembly evidence review does not activate registry-backed dependent package assembly
- this registry assembly evidence review does not invite public installation
- this registry assembly evidence review does not approve package publication

## Retained Blockers

- candidate package version map is recorded but no package publication version is selected
- candidate package tag names are recorded but no package tag is created
- candidate manifest activation diff is reviewed but no Cargo manifest is changed
- package dependency manifest activation remains blocked
- registry-backed dependent package assembly evidence remains required
- registry-backed dependent package assembly activation remains blocked
- public installation remains blocked
- package publication remains blocked
- real-version cargo publish remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_manifest_activation_diff_review.py
python3 .github/scripts/test_milestone_e_package_publication_registry_assembly_evidence_review.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Package publication registry-assembly evidence review validation passed
Registry-backed dependent package assembly evidence requirements are recorded
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
