# Milestone E Package Publication Dependency Ordering Closeout Validation - 2026-06-21

## Purpose

Record the package publication prep follow-up for dependency naming and ordering without approving
package publication.

This record defines the future package dependency order that any later dedicated publication
approval must use. It does not change Cargo manifests, approve real-version cargo publication,
approve public installation, create package tags, publish binaries, publish wheels, publish npm
packages, approve hosted surfaces, approve production positioning, approve public benchmark
reports, approve public benchmark claims, or approve public result wording. It does not resolve or
soften blockers outside this dependency-ordering slice.

## Status

Status: **pass for dependency naming and ordering follow-up with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `d99b396`
- Lane: package publication dependency ordering
- Evidence area: reserved public package name, current in-tree workspace dependency name, and
  future dependent-candidate staging order

## Evidence Review

- The current in-tree core package remains `ethos-core`.
- The reserved public package identifier for that in-tree core package remains `ethos-doc-core`.
- Current dependent candidates `ethos-verify` and `ethos-pdf` depend on the in-tree workspace
  dependency key `ethos-core`.
- A later dedicated publication approval must stage package evidence in this order:

1. `ethos-doc-core` sourced from `crates/ethos-core`.
2. `ethos-verify` only after the reviewed dependency manifest can use dependency key `ethos-core`
   with `package = "ethos-doc-core"` and the approved version.
3. `ethos-pdf` only after the reviewed dependency manifest can use dependency key `ethos-core` with
   `package = "ethos-doc-core"`, the approved version, and the PDFium boundary remains confirmed.

- `ethos-doc` and `ethos-rag` remain reserved placeholders with no in-tree package manifests.
- No manifest migration is performed by this record.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Registry-backed dependent package assembly remains blocked until a later dedicated publication
  approval.
- Package dependency manifest migration remains blocked until a later dedicated publication
  approval.
- Real package version selection and package tag creation remain blocked until a later dedicated
  publication approval.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_dependency_ordering.py
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
