# ethos-verify

`ethos-verify` is the in-tree Rust crate for parser-agnostic citation evidence verification over
the `GroundingSource` boundary. It depends on `ethos-core` without parser internals and keeps
verification limited to the current source-tree evidence-grounding contract.

ADR-0006 reserves the public crates.io identifier `ethos-verify`.

Verification consumers should treat this as the Rust package for running checks over
caller-provided `GroundingSource` evidence:

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

- Public installation from crates.io is available at `0.2.0`.
- The reserved crates.io placeholder remains historical; `0.2.0` is the current public package.

## Metadata Notes

- License: Apache-2.0 through workspace metadata.
- Notice: see `NOTICE.md` in this crate and the repository root `NOTICE`.
- Source repository: `https://github.com/docushell/ethos`.
- Public package name for future review: `ethos-verify`.
