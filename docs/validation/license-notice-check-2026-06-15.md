# License and NOTICE Check - 2026-06-15

## Purpose

Record the public-release checklist check for source-tree license metadata, NOTICE boundaries,
and release-artifact license obligations.

This is not a legal opinion and not a final release artifact license manifest. It is a source
readiness check for the current pre-alpha tree.

## Status

Status: **completed for current source tree with release-artifact and advisory follow-up required**.

The source tree has coherent Apache-2.0 project licensing, records the known PDFium and
Liberation notice boundaries, and passes the non-advisory `cargo-deny` policy checks that enforce
licenses, banned crates, and source registries. Final public release artifacts still need a
generated third-party license manifest and an advisory scan with a compatible `cargo-deny`/Rust
toolchain.

## Scope

Checked paths:

- `LICENSE`
- `NOTICE`
- `Cargo.toml`
- crate and adapter `Cargo.toml` files under `crates/` and `adapters/`
- `Cargo.lock`
- `deny.toml`
- `docs/decisions/ADR-0004-licensing-and-dependency-policy.md`
- `profiles/ethos-deterministic-v1.json`
- `benchmarks/competitors.lock.json`

## Findings

- The repository root carries the Apache License 2.0 text in `LICENSE`.
- The workspace package metadata declares `license = "Apache-2.0"`.
- All current workspace crates and the OpenDataLoader grounding adapter inherit workspace
  `license`, `repository`, and `authors` metadata.
- The workspace repository URL now points at `https://github.com/docushell/ethos`.
- `deny.toml` implements the ADR-0004 allowlist and denies common network/runtime dependency
  families for the base tree.
- `NOTICE` now records the known PDFium BSD-3-Clause and Liberation SIL OFL 1.1 boundaries
  without claiming those artifacts are vendored in the source tree.
- `profiles/ethos-deterministic-v1.json` records pinned PDFium and Liberation policy metadata.
- `benchmarks/competitors.lock.json` records PyMuPDF/PyMuPDF4LLM as an AGPL run-only comparison,
  not a project dependency.

## Verification Commands

```sh
cargo metadata --locked --offline --format-version 1 --no-deps
cargo deny --version
cargo install cargo-deny --locked --root /private/tmp/ethos-cargo-tools
cargo install cargo-deny --version 0.18.3 --locked --root /private/tmp/ethos-cargo-tools
/private/tmp/ethos-cargo-tools/bin/cargo-deny check
/private/tmp/ethos-cargo-tools/bin/cargo-deny check licenses bans sources
make release-hygiene CARGO_DENY=/private/tmp/ethos-cargo-tools/bin/cargo-deny
git diff --check
```

Results:

```text
cargo metadata --locked --offline --format-version 1 --no-deps
success; workspace package metadata was readable offline and reported Apache-2.0 for workspace members

cargo deny --version
error: no such command: `deny`

cargo install cargo-deny --locked --root /private/tmp/ethos-cargo-tools
error: cargo-deny 0.19.8 requires rustc 1.88.0 or newer; active rustc is 1.87.0

cargo install cargo-deny --version 0.18.3 --locked --root /private/tmp/ethos-cargo-tools
success

/private/tmp/ethos-cargo-tools/bin/cargo-deny check
error: cargo-deny 0.18.3 could not parse a current RustSec CVSS 4.0 advisory

/private/tmp/ethos-cargo-tools/bin/cargo-deny check licenses bans sources
bans ok, licenses ok, sources ok
warnings only: unused allowed-license entries in `deny.toml`, plus duplicate transitive
`wit-bindgen` versions through dev dependencies

make release-hygiene CARGO_DENY=/private/tmp/ethos-cargo-tools/bin/cargo-deny
pass

git diff --check
pass
```

## Remaining Release Work

- Run the advisory portion of `cargo-deny` before any public release artifact is cut. On the
  current Rust 1.87 toolchain, `cargo-deny 0.18.3` is the newest compatible version, but it
  cannot parse current RustSec CVSS 4.0 advisory metadata. Use Rust 1.88+ with a newer
  `cargo-deny`, or a CI runner that provides that pairing.
- Generate and publish a third-party license/NOTICE manifest with release artifacts.
- If PDFium binaries or Liberation fonts are bundled in an artifact, include the upstream license
  and notice material in that artifact.
- Keep AGPL/GPL comparison tools out of the base dependency tree; benchmark-only execution remains
  acceptable when recorded as run-only comparison evidence.

## Result

The current source tree passes the license/NOTICE source-readiness check and non-advisory
`cargo-deny` policy checks for pre-alpha publication. Public release artifacts remain blocked on
generated third-party license manifests and a successful advisory scan.
