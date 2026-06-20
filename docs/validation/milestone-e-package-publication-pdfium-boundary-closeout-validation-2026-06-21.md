# Milestone E Package Publication PDFium Boundary Closeout Validation - 2026-06-21

## Purpose

Record the package publication prep follow-up for the `ethos-pdf` PDFium packaging boundary without
approving package publication.

This record confirms the current source-tree `ethos-pdf` boundary only: no PDFium binary is bundled,
PDFium remains caller-provided, and no raw PDFium FFI types cross the public schema/API boundary.
It does not approve real-version cargo publication, public installation, package tag
creation, binaries, wheels, npm packages, hosted surfaces, production positioning, public benchmark
reports, public benchmark claims, project-maintained PDFium builds, or public result wording. It
does not resolve or soften blockers outside this PDFium boundary slice.

## Status

Status: **pass for PDFium packaging boundary follow-up with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `6ec51e3`
- Lane: package publication PDFium boundary
- Evidence area: `ethos-pdf` package input, caller-provided PDFium loading, and public schema/API
  boundary

## Evidence Review

- `crates/ethos-pdf/Cargo.toml` keeps `publish = false` and
  `publication_status = "blocked"`.
- `crates/ethos-pdf` tracked package inputs are limited to `Cargo.toml`, `README.md`, `NOTICE.md`,
  `assets/README.md`, `assets/font-substitution-table.json`, and `src/lib.rs`.
- No PDFium binary is bundled in `crates/ethos-pdf`.
- `ethos-pdf` keeps PDFium caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.
- The `ethos-core::traits::EthosPdfBackend` boundary returns normalized Ethos core types
  (`BackendManifest`, `Extraction`, `Page`, `Span`, `Region`, and `Warning`) rather than raw
  PDFium FFI types.
- `ethos-verify` remains parser-agnostic and does not depend on `ethos-pdf`.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Project-maintained PDFium builds remain blocked.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Dependent package assembly remains blocked until package dependency naming and ordering are
  resolved.
- Real package version selection and package tag creation remain blocked until a later dedicated
  publication approval.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_pdfium_boundary.py
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
