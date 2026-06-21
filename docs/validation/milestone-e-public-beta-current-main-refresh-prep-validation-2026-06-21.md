# Milestone E Public Beta Current-Main Refresh Prep Validation - 2026-06-21

## Purpose

Record source-only public beta current-main refresh preparation without approving a refreshed
reviewed public beta source state.

This record binds current main as a source-only refresh candidate and lists the evidence still
required before a later exact refresh decision. It does not refresh the reviewed public beta source
state, change the approved public beta wording, approve package publication, approve public
installation, approve hosted surfaces, approve production positioning, approve public benchmark
reports, approve public benchmark claims, approve release artifacts, approve binaries, approve
wheels, approve npm packages, approve crate publication, approve project-maintained PDFium builds,
or approve broader public wording.

## Status

Status: **pass for public beta current-main refresh prep validation with refresh approval
blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `9262b28`
- Lane: public beta current-main refresh prep
- Evidence area: exact current-main source candidate and retained refresh blockers

## Refresh Candidate

- surface: GitHub source repository docushell/ethos source-only evaluation
- candidate commit: `9262b281ee2cfb7fb0c9adf9f70afafe624e6878`
- candidate tree: `9f18f9e40c57551aef9b0cb2a53641c87207546b`
- candidate boundary: source-only clone, build, and validation commands only
- candidate state: prepared for later exact source-only public beta refresh review; no refreshed
  source approval is granted by this prep

## Existing Reviewed Public Beta Binding

- reviewed commit: `d755e7c`
- merged main commit: `3f9e1c4`
- reviewed tree: `a9e913b0ba7ecd1567479b2ec773342868cba126`
- boundary: source-only clone, build, and validation commands only

## Prior Readiness Ledger Candidate

- candidate commit: `847e12db42d4519665b1486ccb35c85fe01f00b0`
- candidate tree: `9d3701aa14d98017626583c2a0a0ef45ac0df79f`
- ledger record: `docs/milestone-e-public-facing-readiness-ledger.json`
- boundary: readiness ledger candidate only; not a refreshed reviewed public beta source state

## Required Refresh Evidence

- dedicated source-only public beta refresh decision record
- exact refreshed source commit and tree
- public-surface posture check for exact changed surfaces
- claims gate after exact wording or surface changes
- make milestone-e-prep after the refreshed source binding
- cargo build --locked -p ethos-cli for the source checkout path
- decider signoff on exact refreshed source surface and wording

## Non-Approvals Retained

- this prep does not refresh the reviewed public beta source state
- this prep does not change the approved public beta wording
- this prep does not approve package publication
- this prep does not approve public installation
- this prep does not approve hosted surfaces
- this prep does not approve production positioning
- this prep does not approve public benchmark reports or public benchmark claims
- this prep does not approve release artifacts, binaries, wheels, npm packages, crate publication,
  or project-maintained PDFium builds

## Commands

```sh
python3 .github/scripts/test_milestone_e_public_beta_current_main_refresh_prep.py
python3 .github/scripts/test_milestone_e_public_facing_readiness_ledger.py
python3 .github/scripts/test_milestone_e_public_beta_approval_prep.py
python3 schemas/validate_examples.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
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
- Crate publication remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Project-maintained PDFium builds remain blocked.
- Broader public wording remains blocked.
