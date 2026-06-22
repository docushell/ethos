# Milestone E Package Publication Registry Action Approval Validation - 2026-06-22

- Validated source HEAD before this record: `f6865bc`

Registry action approval source commit: `f6865bcecda6f42277527e299718461e080782d9`

Registry action approval source tree: `df33221c7299a18440ac70361e73b19e88a722f6`

Accepted package tag source commit: `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`

Accepted package tag source tree: `aa0d5d31d879540fd0044052dfeb747f12b64204`

Status: **pass for bounded registry action approval with registry action not yet executed**

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Scope

This record captures the exact authorization response requested by
`docs/validation/milestone-e-package-publication-registry-action-authorization-request-validation-2026-06-22.md`.

It authorizes only:

- annotated package tag creation for the three accepted package tag names at
  `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`;
- the first registry action: `cargo publish --locked -p ethos-doc-core`.

It does not authorize public installation wording, dependent package registry actions without fresh
dependent dry-runs, or any surface outside the bounded `ethos-doc-core`, `ethos-verify`, and
`ethos-pdf` candidate set.

## Authorization Supplied

Lane: Package publication registry action authorization

Decision: approve

Exact authorized tag operations:

Create annotated package tags at source commit
`421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`:

- `ethos-package-ethos-doc-core-0.1.0`
- `ethos-package-ethos-verify-0.1.0`
- `ethos-package-ethos-pdf-0.1.0`

Exact authorized first registry action:

`cargo publish --locked -p ethos-doc-core`

Exact deferred registry actions:

- `cargo publish --dry-run --locked -p ethos-verify` after `ethos-doc-core 0.1.0` is available on crates.io
- `cargo publish --dry-run --locked -p ethos-pdf` after `ethos-doc-core 0.1.0` is available on crates.io
- `cargo publish --locked -p ethos-verify` only after the refreshed `ethos-verify` dry-run passes
- `cargo publish --locked -p ethos-pdf` only after the refreshed `ethos-pdf` dry-run passes

Exact source binding acknowledged:

`421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`

Exact source tree acknowledged:

`aa0d5d31d879540fd0044052dfeb747f12b64204`

crates.io publishing owner acknowledged:

`docushell-dev` docushell team

Explicit exclusions retained:

Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports,
public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag` remain
blocked.

Approver: `docushell-admin`

Date: `2026-06-22`

## Authorized Manual Command Order

The authorized operator command order is:

```text
git tag -a ethos-package-ethos-doc-core-0.1.0 421bed8c6e04fa3d2299c6a1d9c99ccfd508122e
git tag -a ethos-package-ethos-verify-0.1.0 421bed8c6e04fa3d2299c6a1d9c99ccfd508122e
git tag -a ethos-package-ethos-pdf-0.1.0 421bed8c6e04fa3d2299c6a1d9c99ccfd508122e
git push origin ethos-package-ethos-doc-core-0.1.0
git push origin ethos-package-ethos-verify-0.1.0
git push origin ethos-package-ethos-pdf-0.1.0
cargo publish --locked -p ethos-doc-core
```

The dependent packages stay blocked until `ethos-doc-core 0.1.0` is visible on crates.io and fresh
dependent dry-runs pass.

## Retained Blockers

- No package tag is created by this record:
  `ethos-package-ethos-doc-core-0.1.0`, `ethos-package-ethos-verify-0.1.0`, and
  `ethos-package-ethos-pdf-0.1.0` remain absent until the later operator step executes.
- `cargo publish --locked -p ethos-doc-core` is authorized by this record but not executed by this
  record.
- Registry publication for `ethos-verify` and `ethos-pdf` remains blocked until fresh dependent
  dry-runs pass after `ethos-doc-core 0.1.0` is available on crates.io.
- Public installation instructions remain blocked until package availability and wording are
  explicitly revalidated.
- Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark
  reports, public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag`
  remain excluded.
- Public reports remain blocked.
- Public result wording remains blocked.
- No local registry config is created: `.cargo/config.toml` remains absent.
- No local package registry directory is retained: `target/package-registry` remains absent.

## Result

The bounded tag and first registry action authorization is recorded. Dependent registry actions and
public installation remain blocked.
