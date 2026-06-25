# ethos-pdf

`ethos-pdf` is the in-tree Rust crate for the PDFium-backed PDF source path behind Ethos parser
traits. It normalizes parser output before data crosses the crate boundary.

ADR-0006 reserves the public crates.io identifier `ethos-pdf` at `0.0.0-reserved.0`.

For the v0.2.0 release-candidate lane, this crate is a continuity crate for the lockstep Rust workspace.
The release headline remains JSON verification and evidence anchoring over caller-provided source
evidence. `ethos-pdf` remains the parser/PDFium-facing crate.

## Publication Boundary

- Publication metadata is activated for the approved crates.io candidate surface.
- Public installation from crates.io remains blocked until refreshed tag/source binding and
  operator evidence are recorded.
- The reserved crates.io placeholder remains `0.0.0-reserved.0` until registry action is
  explicitly recorded.
- This README supports package-publication activation review only.
- v0.2.0 registry install wording remains in release-candidate status until publication, registry
  availability, and clean smoke tests are recorded.

## PDFium Boundary

- No PDFium binary is bundled in this crate.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.
- If `ETHOS_PDFIUM_LIBRARY_PATH` is missing, PDFium-backed paths fail with a setup error naming the
  environment variable.
- Public schemas and APIs expose no PDFium types.
- v0.2.0's no-PDFium claim applies to JSON verify and evidence-anchor workflows. Parser, crop, and
  render paths may still require caller-provided PDFium.
- If that boundary cannot be guaranteed in a later review, `ethos-pdf` remains held out of any
  future crate surface.

## Metadata Notes

- License: Apache-2.0 through workspace metadata.
- Notice: see `NOTICE.md` in this crate and the repository root `NOTICE`.
- Source repository: `https://github.com/docushell/ethos`.
- Public package name for future review: `ethos-pdf`.
