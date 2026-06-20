# Milestone E Package Publication PDFium Boundary Validation - 2026-06-20

## Purpose

Record PDFium packaging-boundary evidence for the package publication prep lane without approving
package publication.

This is an evidence record only. It records that `ethos-pdf` cannot enter a first crate publication
surface unless the PDFium boundary remains caller-provided and the public API does not expose PDFium
types. It does not approve crate publication, real-version `cargo publish`, public installation,
release artifacts, binaries, wheels, npm packages, hosted surfaces, production positioning, public
benchmark reports, public benchmark claims, project-maintained PDFium builds, or public result
wording. It does not resolve or soften blockers.

## Status

Status: **pass for package PDFium boundary evidence with ethos-pdf held unless confirmed**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `e792f03`
- Lane: package publication evidence records
- Evidence area: `ethos-pdf` PDFium packaging boundary

## Boundary Evidence

- `ethos-pdf` currently keeps `publish = false`.
- `ethos-pdf` must bundle no PDFium binary in any first crate surface.
- `ethos-pdf` must expose no PDFium types in public API.
- PDFium must remain caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.
- ADR-0002 still blocks project-maintained PDFium build distribution outside a dedicated future
  approval scope.

## Holdout Rule

If the no-bundled-PDFium and no-public-PDFium-types boundary cannot be guaranteed, `ethos-pdf` is
held out of the first crate surface. `ethos-verify` remains the recommended first candidate for any
later crate-publication evidence lane because it is parser-agnostic and must not depend on
`ethos-pdf`.

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

