# ethos-pdf

`ethos-pdf` is the in-tree Rust crate for the PDFium-backed PDF source path behind Ethos parser
traits. It normalizes parser output before data crosses the crate boundary.

ADR-0006 reserves the public crates.io identifier `ethos-pdf`.

For v0.2.0, this crate is a continuity crate for the lockstep Rust workspace. The release headline
is JSON verification and evidence anchoring over caller-provided source evidence. `ethos-pdf`
remains the parser/PDFium-facing crate.

## Publication Boundary

- Public installation from crates.io is available at `0.2.0`.
- The reserved crates.io placeholder remains historical; `0.2.0` is the current public package.

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
