# Milestone E Package Publication Registry Action Authorization Request Validation - 2026-06-22

- Validated source HEAD before this record: `ee8d2f6`

Registry action authorization request source commit: `ee8d2f6ded15c09ec3f47a8505d0b63468749bb8`

Registry action authorization request source tree: `e7afe973e4b688302d84baaf5b95bc34a8365f83`

Accepted package tag source commit: `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`

Accepted package tag source tree: `aa0d5d31d879540fd0044052dfeb747f12b64204`

Status: **pass for registry action authorization request with registry action blocked**

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Scope

This record requests the final manual authorization needed after
`docs/validation/milestone-e-package-publication-manual-registry-evidence-supplied-validation-2026-06-22.md`.

It does not create package tags, run `cargo publish`, approve public installation wording, or
approve any surface outside the bounded `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
candidate set.

## Authorization Output Packet

Do not paste tokens, passwords, or secret registry credentials.

Provide the following exact output in a later approval response:

```text
Lane: Package publication registry action authorization

Decision: approve

Exact authorized tag operations:
create annotated package tags at source commit 421bed8c6e04fa3d2299c6a1d9c99ccfd508122e:
- ethos-package-ethos-doc-core-0.1.0
- ethos-package-ethos-verify-0.1.0
- ethos-package-ethos-pdf-0.1.0

Exact authorized first registry action:
cargo publish --locked -p ethos-doc-core

Exact deferred registry actions:
cargo publish --dry-run --locked -p ethos-verify after ethos-doc-core 0.1.0 is available on crates.io
cargo publish --dry-run --locked -p ethos-pdf after ethos-doc-core 0.1.0 is available on crates.io
cargo publish --locked -p ethos-verify only after the refreshed ethos-verify dry-run passes
cargo publish --locked -p ethos-pdf only after the refreshed ethos-pdf dry-run passes

Exact source binding acknowledged:
421bed8c6e04fa3d2299c6a1d9c99ccfd508122e

Exact source tree acknowledged:
aa0d5d31d879540fd0044052dfeb747f12b64204

crates.io publishing owner acknowledged:
docushell-dev (docushell team)

Explicit exclusions retained:
wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports,
public benchmark claims, project-maintained PDFium builds, ethos-doc, and ethos-rag remain blocked.

Approver:
docushell-admin

Date:
2026-06-22
```

## Manual Command Order After Authorization

The later operator command order must be:

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
  `ethos-package-ethos-pdf-0.1.0` remain absent.
- `cargo publish` remains blocked until the later exact authorization response is recorded.
- Registry publication remains blocked.
- Public installation instructions remain blocked until package availability and wording are
  explicitly revalidated.
- Dependent registry actions for `ethos-verify` and `ethos-pdf` remain blocked until
  `ethos-doc-core 0.1.0` is available on crates.io and fresh dependent dry-runs pass.
- Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark
  reports, public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag`
  remain excluded.
- Public reports remain blocked.
- Public result wording remains blocked.
- No local registry config is created: `.cargo/config.toml` remains absent.
- No local package registry directory is retained: `target/package-registry` remains absent.

## Result

The registry action authorization request is recorded. Package tag creation remains blocked, public
installation remains blocked, and registry publication remains blocked.
