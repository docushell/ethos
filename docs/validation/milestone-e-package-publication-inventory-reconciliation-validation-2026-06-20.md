# Milestone E Package Publication Inventory Reconciliation Validation - 2026-06-20

## Purpose

Record package-inventory evidence for the package publication prep lane without approving package
publication.

This record reconciles the five ADR-0006 reserved priority crates.io identifiers with the current
source-tree workspace. It is an evidence record only. It does not approve crate publication,
real-version `cargo publish`, public installation from crates.io, binaries, wheels, npm packages,
release artifacts, hosted surfaces, production positioning, public benchmark reports, public
benchmark claims, project-maintained PDFium builds, or public result wording. It does not resolve or
soften blockers.

## Status

Status: **pass for package publication inventory reconciliation evidence**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `e792f03`
- Lane: package publication evidence records
- Evidence area: package inventory reconciliation
- Registry: crates.io
- Reserved placeholder version: `0.0.0-reserved.0`

## Reconciled Inventory

| Reserved identifier | Current source-tree mapping | Evidence status |
| --- | --- | --- |
| `ethos-doc-core` | Maps to in-tree `crates/ethos-core`; public package name differs from internal crate name | Needs package-name reconciliation before any future crate surface can advance |
| `ethos-doc` | No in-tree workspace member or package manifest | Held as reserved placeholder |
| `ethos-verify` | Maps to in-tree `crates/ethos-verify` | Best first candidate for future crate-surface evidence; still `publish = false` |
| `ethos-rag` | Placeholder README only; no in-tree package manifest | Held as reserved placeholder |
| `ethos-pdf` | Maps to in-tree `crates/ethos-pdf` | Held until PDFium boundary evidence is complete and still `publish = false` |

## Verified Source Facts

- ADR-0006 records all five priority crates.io placeholders at `0.0.0-reserved.0`.
- `Cargo.toml` workspace members include `crates/ethos-core`, `crates/ethos-verify`, and
  `crates/ethos-pdf`.
- `Cargo.toml` workspace members do not include `crates/ethos-doc` or `crates/ethos-rag`.
- `crates/ethos-core/Cargo.toml`, `crates/ethos-verify/Cargo.toml`, and
  `crates/ethos-pdf/Cargo.toml` all retain `publish = false`.

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

