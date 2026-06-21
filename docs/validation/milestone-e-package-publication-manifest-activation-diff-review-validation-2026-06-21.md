# Milestone E Package Publication Manifest-Activation Diff Review Validation - 2026-06-21

## Purpose

Record the candidate package manifest activation diff review for the package publication approval
lane without changing Cargo manifests, selecting a package publication version, creating package
tags, creating a registry, activating registry-backed dependent package assembly, inviting public
installation, or approving package publication.

## Status

Status: **pass for package manifest-activation diff review with publication blocked**.

Decision: record candidate manifest activation diff review only.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `89d24c8`
- Manifest activation diff review source commit: `89d24c84614a7c961dcecdccf85a9e9eca235046`
- Manifest activation diff review source tree: `21b263dca908ef7cc977e7669e40206096eef93e`
- Lane: package publication
- Reviewed readiness record: `docs/validation/milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md`

## Candidate Manifest Activation Diff

- crates/ethos-core/Cargo.toml candidate package-name migration: package.name ethos-core ->
  ethos-doc-core; current manifest remains unchanged
- crates/ethos-verify/Cargo.toml candidate dependency activation: ethos_core package alias points
  at ethos-doc-core; current manifest remains unchanged
- crates/ethos-pdf/Cargo.toml candidate dependency activation: ethos_core package alias points at
  ethos-doc-core; current manifest remains unchanged
- included candidate crates require later publish-flag activation only after dedicated approval;
  current manifests remain publish=false

## Evidence Review

- The current `crates/ethos-core/Cargo.toml` package name remains `ethos-core`.
- The current `crates/ethos-core/Cargo.toml` package metadata retains
  `reserved_crates_io_name = "ethos-doc-core"`.
- The current `crates/ethos-verify/Cargo.toml` manifest does not reference
  `package = "ethos-doc-core"`.
- The current `crates/ethos-pdf/Cargo.toml` manifest does not reference
  `package = "ethos-doc-core"`.
- The current `crates/ethos-core/Cargo.toml`, `crates/ethos-verify/Cargo.toml`, and
  `crates/ethos-pdf/Cargo.toml` manifests remain `publish = false`.
- No candidate package tag is created for `ethos-doc-core`, `ethos-verify`, or `ethos-pdf`.
- Registry-backed dependent package assembly remains required after any later exact manifest
  activation approval.

## Approval Inputs Still Required

- exact package publication approval decision record remains required
- decider signoff on the exact candidate version map remains required
- decider signoff on the exact package tag name set and source binding remains required
- registry-backed dependent package assembly evidence remains required
- public-surface posture check after exact public installation wording changes remains required
- claims gate after exact public installation wording changes remains required
- make milestone-e-prep after exact decision record remains required

## Non-Approvals

- this manifest activation diff review does not select a package publication version
- this manifest activation diff review does not create a package tag
- this manifest activation diff review does not change Cargo manifests
- this manifest activation diff review does not activate package dependency manifests
- this manifest activation diff review does not create a registry
- this manifest activation diff review does not activate registry-backed dependent package assembly
- this manifest activation diff review does not invite public installation
- this manifest activation diff review does not approve package publication

## Retained Blockers

- candidate package version map is recorded but no package publication version is selected
- candidate package tag names are recorded but no package tag is created
- candidate manifest activation diff is reviewed but no Cargo manifest is changed
- package dependency manifest activation remains blocked
- registry-backed dependent package assembly evidence remains required
- public installation remains blocked
- package publication remains blocked
- real-version cargo publish remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_approval_readiness_review.py
python3 .github/scripts/test_milestone_e_package_publication_manifest_activation_diff_review.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Package publication manifest-activation diff review validation passed
Candidate manifest activation diff is recorded for ethos-doc-core, ethos-verify, and ethos-pdf
No package version was selected
No package tag was created
No Cargo manifest was changed
No registry-backed assembly was activated
Package publication and public installation remained blocked
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
