# ethos-core

`ethos-core` is the in-tree Rust crate for Ethos document evidence contracts: canonical document
types, deterministic serialization identifiers, fingerprints, stable codes, schema types, crop
descriptor support, and trait boundaries.

ADR-0006 reserves the public crates.io identifier `ethos-doc-core` at
`0.0.0-reserved.0`. The in-tree crate name remains `ethos-core` until a later reviewed publishing
migration.

## Publication Boundary

- `publish = false` remains set.
- Package publication remains blocked.
- Public installation from crates.io remains blocked.
- The reserved crates.io placeholder remains `0.0.0-reserved.0` with no public API.
- This README supports internal metadata readiness review only.

## Metadata Notes

- License: Apache-2.0 through workspace metadata.
- Notice: see `NOTICE.md` in this crate and the repository root `NOTICE`.
- Source repository: `https://github.com/docushell/ethos`.
- Public package name for future review: `ethos-doc-core`.
