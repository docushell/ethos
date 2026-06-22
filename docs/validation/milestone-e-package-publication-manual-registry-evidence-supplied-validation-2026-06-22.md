# Milestone E Package Publication Manual Registry Evidence Supplied Validation - 2026-06-22

- Validated source HEAD before this record: `5950b74`

Manual registry evidence supplied record source commit: `5950b7442f248c45d8efb6dab29d2f112181c4aa`

Manual registry evidence supplied record source tree: `674264c1f34a84bb9c309f645cf58d1c488469cb`

Reviewed package source commit: `7d9329a0f26e5335e32b6351711e8718729a3a43`

Reviewed package source tree: `d11dafbe47a75953ff2173be6515a727745b2d05`

Status: **pass for manual registry evidence supplied with registry action blocked**

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Scope

This record captures the non-secret manual registry evidence requested by
`docs/validation/milestone-e-package-publication-manual-registry-evidence-request-validation-2026-06-22.md`.

It does not create package tags, run `cargo publish`, approve public installation wording, or
approve any surface outside the bounded `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
candidate set.

## Manual Evidence Supplied

Lane: Package publication manual registry evidence

Decision: evidence supplied

Source commit reviewed: `7d9329a0f26e5335e32b6351711e8718729a3a43`

Source tree reviewed: `d11dafbe47a75953ff2173be6515a727745b2d05`

crates.io account name or owner identity:

`docushell-admin` governance/decider role

crates.io publishing owner of record:

`docushell-dev` docushell team

reserved name owner outputs:

```text
$ cargo owner --list ethos-doc-core
docushell-dev (docushell)

$ cargo owner --list ethos-verify
docushell-dev (docushell)

$ cargo owner --list ethos-pdf
docushell-dev (docushell)
```

first dry-run output for `ethos-doc-core`:

```text
$ cargo publish --dry-run --locked -p ethos-doc-core
Packaging ethos-doc-core v0.1.0 (crates/ethos-core)
Packaged 19 files, 150.6KiB (35.5KiB compressed)
Verifying ethos-doc-core v0.1.0
Compiling ethos-doc-core v0.1.0 (target/package/ethos-doc-core-0.1.0)
Finished `dev` profile in 31.12s
Uploading ethos-doc-core v0.1.0
warning: aborting upload due to dry run
RESULT: PASS (dry-run)
```

dependent dry-run outputs after `ethos-doc-core` is visible:

```text
$ cargo publish --dry-run --locked -p ethos-verify
error: failed to select a version for the requirement `ethos-doc-core = "^0.1.0"`
  candidate versions found which didn't match: 0.0.0-reserved.0
RESULT: EXPECTED BLOCKED until ethos-doc-core 0.1.0 is available on crates.io

$ cargo publish --dry-run --locked -p ethos-pdf
error: failed to select a version for the requirement `ethos-doc-core = "^0.1.0"`
  candidate versions found which didn't match: 0.0.0-reserved.0
RESULT: EXPECTED BLOCKED until ethos-doc-core 0.1.0 is available on crates.io
```

Package tag names acknowledged:

- `ethos-package-ethos-doc-core-0.1.0`
- `ethos-package-ethos-verify-0.1.0`
- `ethos-package-ethos-pdf-0.1.0`

Explicit exclusions retained:

Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports,
public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag` remain
blocked.

Approver: `docushell-admin`

Date: `2026-06-22`

## Retained Blockers

- No package tag is created by this record:
  `ethos-package-ethos-doc-core-0.1.0`, `ethos-package-ethos-verify-0.1.0`, and
  `ethos-package-ethos-pdf-0.1.0` remain absent.
- `cargo publish` remains blocked.
- Manual registry evidence is supplied, but registry action remains blocked.
- Public installation instructions remain blocked until package availability and wording are
  explicitly revalidated.
- The dependent dry-runs for `ethos-verify` and `ethos-pdf` remain expected blocked until
  `ethos-doc-core 0.1.0` is available on crates.io.
- Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark
  reports, public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag`
  remain excluded.
- Public reports remain blocked.
- Public result wording remains blocked.
- No local registry config is created: `.cargo/config.toml` remains absent.
- No local package registry directory is retained: `target/package-registry` remains absent.

## Result

The manual registry evidence is supplied and recorded. Package tag creation remains blocked, public
installation remains blocked, and registry publication remains blocked.
