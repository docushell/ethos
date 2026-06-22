# Milestone E Package Publication Registry Action Evidence Validation - 2026-06-22

- Validated source HEAD before this record: `38e0158`

Registry action evidence source commit: `38e0158d7df5fddeded942926f2dfcdff02dbd92`

Registry action evidence source tree: `15c973f51515745dfc8e879609208279b8661fee`

Accepted package tag source commit: `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`

Accepted package tag source tree: `aa0d5d31d879540fd0044052dfeb747f12b64204`

Status: **pass for bounded registry action evidence with dependent registry actions blocked**

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Scope

This record captures the operator evidence after
`docs/validation/milestone-e-package-publication-registry-action-approval-validation-2026-06-22.md`.

It records:

- the three annotated package tags pushed to `origin`;
- the peeled tag commit verification for the approved source binding;
- completion of the authorized first registry action for `ethos-doc-core`;
- passing refreshed dry-runs for `ethos-verify` and `ethos-pdf`.

It does not authorize or execute dependent registry actions for `ethos-verify` or `ethos-pdf`.
It does not approve public installation wording or any surface outside the bounded
`ethos-doc-core`, `ethos-verify`, and `ethos-pdf` candidate set.

## Tag Evidence

Remote annotated tag objects:

```text
16f260a8f635f3250e2583bd4f7e10cca5dabcb2 refs/tags/ethos-package-ethos-doc-core-0.1.0
bc9876f5682d5f670b6357bd0206a467d76ac850 refs/tags/ethos-package-ethos-verify-0.1.0
95613c035a128644998af5c9432729cf0024ed3e refs/tags/ethos-package-ethos-pdf-0.1.0
```

Remote peeled tag commits:

```text
421bed8c6e04fa3d2299c6a1d9c99ccfd508122e refs/tags/ethos-package-ethos-doc-core-0.1.0^{}
421bed8c6e04fa3d2299c6a1d9c99ccfd508122e refs/tags/ethos-package-ethos-verify-0.1.0^{}
421bed8c6e04fa3d2299c6a1d9c99ccfd508122e refs/tags/ethos-package-ethos-pdf-0.1.0^{}
```

## Registry Action Evidence

Authorized command:

```text
cargo publish --locked -p ethos-doc-core
```

Observed result:

```text
Uploaded ethos-doc-core v0.1.0 to registry `crates-io`
Published ethos-doc-core v0.1.0 at registry `crates-io`
```

## Refreshed Dependent Dry-Run Evidence

`ethos-verify` command:

```text
cargo publish --dry-run --locked -p ethos-verify
```

Observed result:

```text
Downloaded ethos-doc-core v0.1.0
Finished `dev` profile
warning: aborting upload due to dry run
```

`ethos-pdf` command:

```text
cargo publish --dry-run --locked -p ethos-pdf
```

Observed result:

```text
Compiling ethos-doc-core v0.1.0
Finished `dev` profile
warning: aborting upload due to dry run
```

## Retained Blockers

- Registry actions for `ethos-verify` and `ethos-pdf` remain blocked until a separate exact
  approval record authorizes them.
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

The tag and first registry action evidence is recorded. The refreshed dependent dry-runs are
recorded. Dependent registry actions and public installation remain blocked.
