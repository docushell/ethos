# Milestone E Package Publication Dry-Run Smoke Plan Validation - 2026-06-20

## Purpose

Record the dry-run and smoke-build plan for the package publication prep lane without running or
approving package publication.

This is an evidence record only. It documents the future command shape that a later publication
approval lane must run after per-crate metadata and manifest readiness are complete. It does not
approve crate publication, real-version `cargo publish`, public installation, release artifacts,
binaries, wheels, npm packages, hosted surfaces, production positioning, public benchmark reports,
public benchmark claims, or public result wording. It does not resolve or soften blockers.

## Status

Status: **pass for package dry-run smoke plan evidence with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `e792f03`
- Lane: package publication evidence records
- Evidence area: dry-run and smoke-build plan

## Current Source Build Evidence

The current source-tree build path remains:

```sh
cargo build --locked -p ethos-cli
```

That command is a source checkout build path, not a package publication dry-run and not a registry
installation smoke test.

## Future Dry-Run Plan

A later publication approval lane must define and run per-candidate commands only after candidate
metadata is ready and `publish = false` is intentionally changed in that same approval scope.
Expected future command shapes:

```sh
cargo publish --dry-run -p ethos-verify
cargo package -p ethos-verify
cargo install --path crates/ethos-verify --locked
```

These commands are not approved as current publication evidence. They are recorded as the required
future smoke path shape.

## Blockers Retained

- Candidate crates currently keep `publish = false`.
- No registry-install smoke test has been run for a real crate surface.
- No real-version cargo publish is approved.
- No package publication rollback path is approved.

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

