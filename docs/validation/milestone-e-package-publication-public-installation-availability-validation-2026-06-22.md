# Milestone E Package Publication Public Installation Availability Validation - 2026-06-22

- Validated source HEAD before this record: `25073a1`

Availability source commit: `25073a1b9cf1d691e8b2496b3622cb6349e96a98`

Availability source tree: `46a0e8a7bf11c3b30ee5c32512fb57a1f3677aeb`

Accepted package tag source commit: `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`

Accepted package tag source tree: `aa0d5d31d879540fd0044052dfeb747f12b64204`

Status: **pass for crates.io availability and bounded Rust crate installation wording**

Ethos remains source-only pre-alpha outside the exact approved source and Rust crate evaluation
surfaces. Public reports remain blocked. Public result wording remains blocked outside the exact
bounded wording below.

## Scope

This record captures crates.io availability evidence after
`docs/validation/milestone-e-package-publication-dependent-registry-action-evidence-validation-2026-06-22.md`.

It records:

- `ethos-doc-core 0.1.0` availability on crates.io;
- `ethos-verify 0.1.0` availability on crates.io;
- `ethos-pdf 0.1.0` availability on crates.io;
- exact public wording for Rust crate installation limited to those three crates.

It does not approve the Ethos CLI, wheels, npm packages, binaries, hosted surfaces, production
positioning, public benchmark reports, public benchmark claims, project-maintained PDFium builds,
`ethos-doc`, or `ethos-rag`.

## Availability Evidence

Crates.io search output:

```text
ethos-doc-core = "0.1.0"
ethos-verify = "0.1.0"
ethos-pdf = "0.1.0"
```

Crates.io API evidence:

```text
ethos-doc-core: num=0.1.0; yanked=false; license=Apache-2.0; rust_version=1.87; published_by=docushell-dev; checksum=97a1c7b508988d2aa20d386dc29985a2db2308dca337fce9ba2b8ee219953a4d
ethos-verify: num=0.1.0; yanked=false; license=Apache-2.0; rust_version=1.87; published_by=docushell-dev; checksum=101629eb2cd67f6ced6efab766c3c4c83e2e33f1adddc57937e84b18c78a113c
ethos-pdf: num=0.1.0; yanked=false; license=Apache-2.0; rust_version=1.87; published_by=docushell-dev; checksum=54194a3e90defb78aadbb03cc17e7ab817338c57c2fc9a5d47795e6365b741b9
```

## Exact Public Wording

```text
Ethos is public beta for source and Rust crate evaluation. It verifies whether AI citations are grounded in document evidence across native Ethos JSON and supported foreign parser outputs. Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available on crates.io at `0.1.0` for evaluation. Hosted surfaces, production positioning, and public benchmark claims remain blocked.
```

Additional bounded README installation wording:

```text
Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available on crates.io at `0.1.0` for evaluation. The Ethos CLI, wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports, public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag` remain blocked.
```

Approved Rust crate installation commands:

```text
cargo add ethos-doc-core@0.1.0
cargo add ethos-verify@0.1.0
cargo add ethos-pdf@0.1.0
```

## Retained Blockers

- The Ethos CLI remains source-checkout only.
- Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark
  reports, public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag`
  remain excluded.
- Public reports remain blocked.
- Public result wording outside the exact wording in this record remains blocked.
- No local registry config is created: `.cargo/config.toml` remains absent.
- No local package registry directory is retained: `target/package-registry` remains absent.

## Result

Crates.io availability for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.0` is
recorded. Public wording is bounded to source and Rust crate evaluation for those three library
crates, with all retained exclusions explicit.
