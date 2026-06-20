# Milestone E Package Publication Metadata Readiness Closeout Validation - 2026-06-21

## Purpose

Record the package publication prep follow-up for metadata, license, NOTICE, and README readiness
across the current in-tree priority candidate crates without approving package publication.

This record covers `crates/ethos-core`, `crates/ethos-verify`, and `crates/ethos-pdf`. It does not
cover real-version cargo publication, registry installation, binaries, wheels, npm packages, hosted
surfaces, production positioning, public benchmark reports, public benchmark claims, or public result
wording. It does not resolve or soften blockers outside this metadata-readiness slice.

## Status

Status: **pass for in-tree package metadata readiness with blockers retained**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `5e216ff`
- Lane: package publication metadata readiness
- Evidence area: in-tree priority candidate crate README, NOTICE, manifest metadata, and include list

## Evidence Review

- `crates/ethos-core` now has `README.md`, `NOTICE.md`, manifest `readme`, package keywords, an
  explicit package include list, and `package.metadata.ethos_publication` mapping its future
  reviewed public identifier to `ethos-doc-core`.
- `crates/ethos-verify` now has `README.md`, `NOTICE.md`, manifest `readme`, package keywords, an
  explicit package include list, and `package.metadata.ethos_publication` mapping its future
  reviewed public identifier to `ethos-verify`.
- `crates/ethos-pdf` now has `README.md`, `NOTICE.md`, manifest `readme`, package keywords, an
  explicit package include list, and `package.metadata.ethos_publication` mapping its future
  reviewed public identifier to `ethos-pdf`.
- All three in-tree candidate manifests keep `publish = false`.
- All three in-tree candidate manifests keep Apache-2.0 license, repository, authors, version,
  edition, and Rust version inherited from workspace metadata.
- The `ethos-pdf` README and NOTICE keep the PDFium boundary explicit: no PDFium binary is bundled,
  PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`, and public schemas/APIs expose
  no PDFium types.
- `ethos-doc` and `ethos-rag` remain reserved placeholders with no in-tree package manifests.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- `cargo publish --dry-run` and registry-install smoke tests remain unrun blockers.
- Version/tag policy reconciliation remains incomplete.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_metadata_readiness.py
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
