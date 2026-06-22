# Milestone E Package Publication Dependent Registry Action Evidence Validation - 2026-06-22

- Validated source HEAD before this record: `2a6ba4a`

Evidence source commit: `2a6ba4a8dc3f109acb62f572cce1efa3b37a9590`

Evidence source tree: `d1bc7657709204d70e338c8e97ad3493c326ec5e`

Accepted package tag source commit: `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`

Accepted package tag source tree: `aa0d5d31d879540fd0044052dfeb747f12b64204`

Status: **pass for completed dependent registry action evidence with public installation wording blocked**

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Scope

This record captures the operator evidence after
`docs/validation/milestone-e-package-publication-dependent-registry-action-approval-validation-2026-06-22.md`.

It records:

- completion of the authorized `ethos-verify` registry action;
- completion of the authorized `ethos-pdf` registry action;
- retained public-installation wording and surface exclusions.

It does not approve public installation wording or any surface outside the bounded
`ethos-doc-core`, `ethos-verify`, and `ethos-pdf` crate set.

## Dependent Registry Action Evidence

`ethos-verify` authorized command:

```text
cargo publish --locked -p ethos-verify
```

Observed result:

```text
Uploaded ethos-verify v0.1.0 to registry `crates-io`
Published ethos-verify v0.1.0 at registry `crates-io`
```

`ethos-pdf` authorized command:

```text
cargo publish --locked -p ethos-pdf
```

Observed result:

```text
Uploaded ethos-pdf v0.1.0 to registry `crates-io`
Published ethos-pdf v0.1.0 at registry `crates-io`
```

## Retained Blockers

- Public installation wording remains blocked until package availability and wording are
  explicitly revalidated in a separate record.
- Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark
  reports, public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag`
  remain excluded.
- Public reports remain blocked.
- Public result wording remains blocked.
- No local registry config is created: `.cargo/config.toml` remains absent.
- No local package registry directory is retained: `target/package-registry` remains absent.

## Result

The authorized `ethos-verify` and `ethos-pdf` registry action evidence is recorded.
Public installation wording remains blocked pending separate wording and availability validation.
