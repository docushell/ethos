# Milestone E Public-Facing Readiness Ledger Validation - 2026-06-21

## Purpose

Record a current-main public-facing readiness ledger without granting a new source-only public beta
refresh approval or approving any blocked package, hosted, production, public-report, or public
installation surface.

This record binds the current main source state as a refresh candidate and consolidates package
publication pre-approval gaps. It does not refresh the reviewed public beta source state, approve
package publication, approve public installation, select a package publication version, create a
package tag, change Cargo manifests, activate package dependency manifests, create a registry,
approve hosted surfaces, approve production positioning, approve public benchmark reports, approve
public benchmark claims, approve release artifacts, approve binaries, approve wheels, approve npm
packages, approve crate publication, approve project-maintained PDFium builds, or approve broader
public wording.

## Status

Status: **pass for public-facing readiness ledger validation with current-main refresh and package
publication blockers retained**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `847e12d`
- Lane: public-facing readiness current-main ledger
- Evidence area: source-only public beta refresh candidate and package publication resolution gaps

## Current-Main Binding

- current main candidate commit: `847e12db42d4519665b1486ccb35c85fe01f00b0`
- current main candidate tree: `9d3701aa14d98017626583c2a0a0ef45ac0df79f`
- ledger state: `current_main_readiness_recorded_without_new_approval`
- current main is recorded as a refresh candidate only; no new source-only public beta approval is
  granted by this ledger

## Existing Reviewed Source-Only Public Beta Binding

- surface: GitHub source repository docushell/ethos source-only evaluation
- reviewed commit: `d755e7c`
- merged main commit: `3f9e1c4`
- reviewed tree: `a9e913b0ba7ecd1567479b2ec773342868cba126`
- boundary: source-only clone, build, and validation commands only

## Required Source-Only Public Beta Refresh Inputs

- dedicated source-only public beta refresh decision record
- exact refreshed source commit and tree
- public-surface posture check for exact changed surfaces
- claims gate after exact wording or surface changes
- make milestone-e-prep after the refreshed source binding
- decider signoff on exact refreshed source surface and wording

## Package Publication Resolution Criteria

- criteria state: `pre_approval_gaps_remain_unresolved`
- exact package publication approval decision record
- exact candidate crate list
- exact SemVer package version or per-crate version map
- exact package tag name
- exact package_tag_source_commit and package source tree
- exact package-name migration diff for ethos-doc-core
- exact dependency manifest activation diff for ethos-verify and ethos-pdf
- exact registry-backed dependent package assembly evidence
- exact public installation wording and explicit exclusions
- posture and claims gates after exact public installation wording changes

## Blockers Retained

- no package publication version is selected
- no package tag is created
- no package dependency manifest activation is approved
- no registry-backed dependent package assembly activation is approved
- public installation remains blocked
- package publication remains blocked
- real-version cargo publish remains blocked
- hosted surfaces remain blocked
- production positioning remains blocked
- public benchmark reports remain blocked
- public benchmark claims remain blocked
- release artifacts remain blocked
- binaries remain blocked
- wheels remain blocked
- npm packages remain blocked
- crate publication remains blocked
- project-maintained PDFium builds remain blocked
- broader public wording remains blocked

## Commands

```sh
python3 .github/scripts/test_milestone_e_public_facing_readiness_ledger.py
python3 .github/scripts/test_milestone_e_public_beta_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_pre_approval_gap_ledger.py
python3 schemas/validate_examples.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Explicit Boundaries

- Public reports remain blocked.
- Public result wording remains blocked.
- Package publication remains blocked.
- Public installation remains blocked.
- Real-version cargo publish remains blocked.
- Release artifacts remain blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- Npm packages remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Project-maintained PDFium builds remain blocked.
