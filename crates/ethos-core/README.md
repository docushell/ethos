# ethos-doc-core

`ethos-doc-core` is the in-tree Rust package for Ethos document evidence contracts: canonical document
types, deterministic serialization identifiers, fingerprints, stable codes, schema types, and
trait boundaries.

ADR-0006 reserves the public crates.io identifier `ethos-doc-core` at
`0.0.0-reserved.0`. The Rust library name remains `ethos_core` so existing source imports keep the
same crate path while registry action remains blocked.

For the v0.2.0 preparation lane, parser authors should treat this as the Rust package for
`GroundingSource` implementations:

```toml
ethos-doc-core = { version = "0.2", features = ["grounding"] }
```

```rust
use ethos_core::grounding::*;
```

The package name and import name intentionally differ. The package is `ethos-doc-core`; the Rust
library crate is `ethos_core`.

## Publication Boundary

- Publication metadata is activated for the approved crates.io candidate surface.
- Public installation from crates.io remains blocked until refreshed tag/source binding and
  operator evidence are recorded.
- The reserved crates.io placeholder remains `0.0.0-reserved.0` until registry action is
  explicitly recorded.
- This README supports package-publication activation review only.
- Source-only pre-alpha crop descriptor APIs are not part of the default public surface. They
  require the explicit Cargo feature `crop-element`, which exists for in-tree CLI contract work.
- v0.2.0 registry install wording remains in preparation status until publication approval,
  registry availability, and clean smoke tests are recorded.

## Metadata Notes

- License: Apache-2.0 through workspace metadata.
- Notice: see `NOTICE.md` in this crate and the repository root `NOTICE`.
- Source repository: `https://github.com/docushell/ethos`.
- Rust library name: `ethos_core`.
