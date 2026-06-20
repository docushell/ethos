# Milestone E Package Publication Version Tag Policy Validation - 2026-06-20

## Purpose

Record draft version and tag policy evidence for the package publication prep lane without
approving package publication.

This is an evidence record only. It documents the current version conflict that must be resolved
before any future crate publication approval. It does not approve crate publication, real-version
`cargo publish`, public installation, release artifacts, binaries, wheels, npm packages, hosted
surfaces, production positioning, public benchmark reports, public benchmark claims, or public
result wording. It does not resolve or soften blockers.

## Status

Status: **pass for package version and tag policy evidence with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `e792f03`
- Lane: package publication evidence records
- Evidence area: version and tag policy

## Current Version Facts

- Workspace package version is `0.1.0`.
- ADR-0006 crates.io reservations remain `0.0.0-reserved.0` placeholders.
- The approved source snapshot tag remains `ethos-source-snapshot-660f268`.
- No package release tag policy exists for a real crate surface.

## Draft Policy Constraints

- The first future crate surface must choose an explicit package version separate from the reserved
  placeholder version.
- A future package tag must identify the exact source tree used for that package surface.
- Package tags must not be reused for source snapshot tags.
- Placeholder reservations must not be described as public installable APIs.
- A future crate surface must complete dry-run, metadata, README, license, NOTICE, and rollback
  evidence before publication approval.

## Blockers Retained

- Workspace `0.1.0` and crates.io `0.0.0-reserved.0` reservations are not reconciled for
  publication.
- No real package tag format is approved.
- No package publication approval is recorded.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_evidence_records.py
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
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Release artifacts remain blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- npm packages remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Project-maintained PDFium builds remain blocked.

