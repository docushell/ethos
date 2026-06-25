# ethos-doc-core

`ethos-doc-core` is the in-tree Rust package for Ethos document evidence contracts: canonical document
types, deterministic serialization identifiers, fingerprints, stable codes, schema types, and
trait boundaries.

ADR-0006 reserves the public crates.io identifier `ethos-doc-core`. The Rust library name remains
`ethos_core` so existing source imports keep the same crate path.

Parser authors should treat this as the Rust package for `GroundingSource` implementations:

```toml
ethos-doc-core = { version = "0.2", features = ["grounding"] }
```

```rust
use ethos_core::grounding::*;
```

The package name and import name intentionally differ. The package is `ethos-doc-core`; the Rust
library crate is `ethos_core`.

## Publication Boundary

- Public installation from crates.io is available at `0.2.0`.
- The reserved crates.io placeholder remains historical; `0.2.0` is the current public package.
- Source-only pre-alpha crop descriptor APIs are not part of the default public surface. They
  require the explicit Cargo feature `crop-element`, which exists for in-tree CLI contract work.

## Metadata Notes

- License: Apache-2.0 through workspace metadata.
- Notice: see `NOTICE.md` in this crate and the repository root `NOTICE`.
- Source repository: `https://github.com/docushell/ethos`.
- Rust library name: `ethos_core`.
