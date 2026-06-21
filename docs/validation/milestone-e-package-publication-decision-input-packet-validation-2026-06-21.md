# Milestone E Package Publication Decision Input Packet Validation - 2026-06-21

## Purpose

Record the package publication decision input packet for later review without selecting a package
publication version, creating package tags, changing Cargo manifests, activating dependency
manifests, creating a registry, activating registry-backed dependent package assembly, inviting
public installation, or approving package publication.

## Status

Status: **pass for package publication decision-input packet validation with publication blocked**.

Decision: record exact candidate inputs for later review only.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `54bf70f`
- Candidate source commit: `54bf70f57b8c357ec76059e31d203b80ade7c0e4`
- Candidate source tree: `5a197bee718e3b31399563340169e9efd4f1317c`
- Lane: package publication
- Packet state: `decision_input_packet_recorded_publication_blocked`

## Candidate Crates

- ethos-doc-core mapped from crates/ethos-core; package-name migration remains pending
- ethos-verify mapped from crates/ethos-verify; dependency manifest activation remains pending
- ethos-pdf mapped from crates/ethos-pdf; dependency manifest activation and PDFium boundary confirmation must remain current

## Candidate Version Map

- ethos-doc-core candidate package version for later approval: 0.1.0; not selected or approved
- ethos-verify candidate package version for later approval: 0.1.0; not selected or approved
- ethos-pdf candidate package version for later approval: 0.1.0; not selected or approved

## Candidate Package Tags

- ethos-doc-core candidate package tag for later approval: ethos-package-ethos-doc-core-0.1.0; tag is not created
- ethos-verify candidate package tag for later approval: ethos-package-ethos-verify-0.1.0; tag is not created
- ethos-pdf candidate package tag for later approval: ethos-package-ethos-pdf-0.1.0; tag is not created

## Candidate Manifest Activation Diff

- crates/ethos-core/Cargo.toml candidate package-name migration: package.name ethos-core -> ethos-doc-core; current manifest remains unchanged
- crates/ethos-verify/Cargo.toml candidate dependency activation: ethos_core package alias points at ethos-doc-core; current manifest remains unchanged
- crates/ethos-pdf/Cargo.toml candidate dependency activation: ethos_core package alias points at ethos-doc-core; current manifest remains unchanged
- included candidate crates require later publish-flag activation only after dedicated approval; current manifests remain publish=false

## Registry-Backed Assembly Input

registry-backed dependent package assembly evidence remains required after manifest activation; no
registry is created and no assembly is activated

## Candidate Public Installation Wording

Candidate public installation wording for later review only: Ethos Rust crates are proposed for
crates.io installation after dedicated package-publication approval; public installation remains
blocked.

## Explicit Exclusions

- wheels
- npm packages
- binaries
- hosted surfaces
- production positioning
- public benchmark reports
- public benchmark claims
- release artifacts
- project-maintained PDFium builds

## Required Before Approval

- exact package publication approval decision record
- decider signoff on the exact candidate version map
- decider signoff on the exact package tag name set and source binding
- dedicated manifest activation diff review for ethos-doc-core, ethos-verify, and ethos-pdf
- registry-backed dependent package assembly evidence after manifest activation
- public-surface posture check after exact public installation wording changes
- claims gate after exact public installation wording changes
- make milestone-e-prep after exact decision record

## Non-Approvals

- this exact decision input packet does not select a package publication version
- this exact decision input packet does not create a package tag
- this exact decision input packet does not change Cargo manifests
- this exact decision input packet does not activate package dependency manifests
- this exact decision input packet does not create a registry
- this exact decision input packet does not activate registry-backed dependent package assembly
- this exact decision input packet does not invite public installation
- this exact decision input packet does not approve package publication

## Retained Blockers

- candidate package version map is recorded but no package publication version is selected
- candidate package tag names are recorded but no package tag is created
- candidate manifest activation diff is recorded but no Cargo manifest is changed
- registry-backed dependent package assembly evidence remains required
- public installation remains blocked
- package publication remains blocked
- real-version cargo publish remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_approval_resolution_plan.py
python3 .github/scripts/test_milestone_e_package_publication_decision_input_packet.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Package publication decision-input packet validation passed
Candidate version, tag, source, manifest, assembly, and wording inputs were recorded for later review
No package version was selected
No package tag was created
No Cargo manifest was changed
No registry-backed assembly was activated
Package publication and public installation remained blocked
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
