# ethos-verify

`ethos-verify` is the in-tree Rust crate for parser-agnostic citation evidence verification over
the `GroundingSource` boundary. It depends on `ethos-core` without parser internals and keeps
verification limited to the current source-tree evidence-grounding contract.

ADR-0006 reserves the public crates.io identifier `ethos-verify` at `0.0.0-reserved.0`.

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
- Public package name for future review: `ethos-verify`.
