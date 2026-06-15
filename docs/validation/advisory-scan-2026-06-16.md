# Advisory Scan - 2026-06-16

## Purpose

Record the release-readiness advisory scan that was previously blocked by the Rust 1.87 pinned
toolchain and older `cargo-deny` RustSec parser support.

This closes the current advisory-scan blocker only. It does not make Ethos ready for package
publication, GitHub release artifacts, binaries, wheels, npm updates, public benchmark reports,
or production-grade claims.

## Status

Status: **completed for the current source tree**.

The full `cargo-deny check` run passed with advisories, bans, licenses, and sources enabled by
using a newer sidecar Rust toolchain and a current `cargo-deny`. The repository remains pinned to
Rust 1.87 for normal deterministic development unless and until a separate toolchain-change ADR or
release decision updates that contract.

## Scope

Checked source state:

- Repository: `docushell/ethos`
- HEAD: `ed53d0cafda43e812eb9a66234c1fc78081b8e60`
- Cargo lockfile: current checked-in `Cargo.lock`
- Policy: current checked-in `deny.toml`

Tooling:

- Sidecar Rust toolchain: `rustc 1.94.0 (4a4ef493e 2026-03-02)`
- Sidecar Cargo: `cargo 1.94.0 (85eff7c80 2026-01-15)`
- `cargo-deny 0.19.9`

## Verification Commands

```sh
cargo +stable --version
rustc +stable --version
cargo +stable install cargo-deny --locked --root <tmp-tools-stable>
RUSTUP_TOOLCHAIN=stable CARGO_HOME=<tmp-cargo-home> <tmp-tools-stable>/bin/cargo-deny check
```

Equivalent durable target added after this run:

```sh
make release-advisory \
  ADVISORY_RUSTUP_TOOLCHAIN=stable \
  CARGO_DENY_ADVISORY=<tmp-tools-stable>/bin/cargo-deny
```

## Result

```text
advisories ok, bans ok, licenses ok, sources ok
```

Warnings only:

- unused license allowances in `deny.toml` for licenses not currently encountered in the
  dependency graph;
- duplicate transitive `wit-bindgen` versions through dev dependencies.

Neither warning changes the current release boundary.

## Remaining Release Work

- Generate third-party license/NOTICE manifests for any future release artifacts.
- Keep release artifact workflows blocked until generated license manifests, artifact provenance,
  and package-specific readiness checks exist.
- Keep public benchmark reports blocked until public-safe Gate Zero evidence is owned by
  `ethos-bench` and signed or otherwise integrity-bound.
- Re-run `make release-advisory` before any release candidate or package publication decision.
