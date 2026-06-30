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

The `verify-types` feature exposes verification report/config schema types, stable warning codes,
and the derived `VerificationReport::proof_summary()` helper used by CLI/API wrappers. The helper
does not change the canonical JSON report; it deterministically labels whether a request is
certified, partially reusable, or unverified.

The same feature also exposes `derive_app_answer_release_decision(...)` for applications that have
already labeled question relevance and synthesis. That helper builds the non-canonical app answer
release envelope documented in `docs/app-answer-release-contract.md`; it does not replace
`verification_report.json`, does not judge relevance itself, and rejects duplicate claim IDs before
building release lists.

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
