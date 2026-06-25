# ethos-verify

`ethos-verify` is the in-tree Rust crate for parser-agnostic citation evidence verification over
the `GroundingSource` boundary. It depends on `ethos-core` without parser internals and keeps
verification limited to the current source-tree evidence-grounding contract.

ADR-0006 reserves the public crates.io identifier `ethos-verify` at `0.0.0-reserved.0`.

For the v0.2.0 preparation lane, verification consumers should treat this as the Rust package for
running checks over caller-provided `GroundingSource` evidence:

```toml
ethos-doc-core = { version = "0.2", features = ["grounding"] }
ethos-verify = "0.2"
```

`ethos-verify` returns structured reports. Grounded, ungrounded, stale, unsupported, and
capability-limited outcomes are report data. They are not infrastructure failures unless a caller
uses a CLI enforcement flag such as `ethos verify --fail-on-ungrounded`.

Default fingerprint matching is security-relevant: when citations are fingerprint-pinned, stale or
unverifiable source fingerprints fail closed in the report.

## Publication Boundary

- Publication metadata is activated for the approved crates.io candidate surface.
- Public installation from crates.io remains blocked until refreshed tag/source binding and
  operator evidence are recorded.
- The reserved crates.io placeholder remains `0.0.0-reserved.0` until registry action is
  explicitly recorded.
- This README supports package-publication activation review only.
- v0.2.0 registry install wording remains in preparation status until publication approval,
  registry availability, and clean smoke tests are recorded.

## Metadata Notes

- License: Apache-2.0 through workspace metadata.
- Notice: see `NOTICE.md` in this crate and the repository root `NOTICE`.
- Source repository: `https://github.com/docushell/ethos`.
- Public package name for future review: `ethos-verify`.
