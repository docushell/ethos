# Milestone E Package Publication Manual Registry Evidence Request Validation - 2026-06-22

- Validated source HEAD before this record: `7d9329a`

Manual registry evidence request source commit: `7d9329a0f26e5335e32b6351711e8718729a3a43`

Manual registry evidence request source tree: `d11dafbe47a75953ff2173be6515a727745b2d05`

Status: **pass for manual registry evidence request with registry action blocked**

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Scope

This record requests the manual registry evidence required after the operator preflight in
`docs/validation/milestone-e-package-publication-operator-preflight-validation-2026-06-22.md`.

It does not create package tags, run `cargo publish`, update public installation instructions, or
approve any surface outside the bounded `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
candidate set.

## Manual Evidence Output Packet

Do not paste tokens, passwords, or secret registry credentials.

Provide the following output in a later approval response:

```text
Lane: Package publication manual registry evidence
Decision: evidence supplied

Source commit reviewed:
7d9329a0f26e5335e32b6351711e8718729a3a43

Source tree reviewed:
d11dafbe47a75953ff2173be6515a727745b2d05

crates.io account name or owner identity:
[provide non-secret account or owner identity]

reserved name owner outputs:
cargo owner --list ethos-doc-core
[paste output]

cargo owner --list ethos-verify
[paste output]

cargo owner --list ethos-pdf
[paste output]

first dry-run output for `ethos-doc-core`:
cargo publish --dry-run --locked -p ethos-doc-core
[paste output]

dependent dry-run outputs after `ethos-doc-core` is visible:
cargo publish --dry-run --locked -p ethos-verify
[paste output]

cargo publish --dry-run --locked -p ethos-pdf
[paste output]

Package tag names acknowledged:
ethos-package-ethos-doc-core-0.1.0
ethos-package-ethos-verify-0.1.0
ethos-package-ethos-pdf-0.1.0

Explicit exclusions retained:
wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports,
public benchmark claims, project-maintained PDFium builds, ethos-doc, and ethos-rag remain blocked.

Approver:
docushell-admin

Date:
2026-06-22
```

## Retained Blockers

- No package tag is created by this record:
  `ethos-package-ethos-doc-core-0.1.0`, `ethos-package-ethos-verify-0.1.0`, and
  `ethos-package-ethos-pdf-0.1.0` remain absent.
- `cargo publish` remains blocked.
- Manual registry evidence remains required.
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

The manual evidence request is recorded. Manual registry evidence remains required, package tag
creation remains blocked, public installation remains blocked, and registry publication remains
blocked.
