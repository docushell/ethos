# ethos-pdf

`ethos-pdf` is the in-tree Rust crate for the PDFium-backed PDF source path behind Ethos parser
traits. It normalizes parser output before data crosses the crate boundary.

ADR-0006 reserves the public crates.io identifier `ethos-pdf` at `0.0.0-reserved.0`.

## Publication Boundary

- `publish = false` remains set.
- Package publication remains blocked.
- Public installation from crates.io remains blocked.
- The reserved crates.io placeholder remains `0.0.0-reserved.0` with no public API.
- This README supports internal metadata readiness review only.

## PDFium Boundary

- No PDFium binary is bundled in this crate.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.
- Public schemas and APIs expose no PDFium types.
- If that boundary cannot be guaranteed in a later review, `ethos-pdf` remains held out of any
  future crate surface.

## Metadata Notes

- License: Apache-2.0 through workspace metadata.
- Notice: see `NOTICE.md` in this crate and the repository root `NOTICE`.
- Source repository: `https://github.com/docushell/ethos`.
- Public package name for future review: `ethos-pdf`.
