# First Public Release Scope Decision Validation - 2026-06-22

- Validated source HEAD before this record: `d3bba4c`

Release-prep source commit: `d3bba4c521ed1837977049bc6f687e795f40cca0`

Release-prep source tree: `f62c1407658a3f7e67b217eeaebf4b5031c80d84`

Status: **release preparation approved; public artifact publication remains blocked**

Ethos remains public beta for source and Rust crate evaluation only until the later release-candidate
and final approval records pass. This record starts a bounded first public release preparation lane;
it does not publish artifacts, approve production positioning, approve hosted surfaces, or approve
public benchmark reports or claims.

## In Scope For Release Preparation

- GitHub Release draft CLI artifacts for macOS arm64 and Linux x64.
- Python package preparation for `ethos-pdf` / `ethos_pdf`.
- npm package preparation for `@docushell/ethos-pdf`.
- Caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.
- Artifact inventories, SHA256 checksums, license files, NOTICE files, and release-candidate guards.
- Draft launch copy for later claim audit and final decider approval.

## Out Of Scope Until A Later Decision

- Public artifact publication.
- Hosted surfaces.
- Production positioning.
- Public benchmark reports.
- Public benchmark claims.
- Windows x64 packaged artifacts.
- Bundled project-maintained PDFium builds.
- `ethos-doc`.
- `ethos-rag`.
- Broader public wording outside the exact approved public beta evaluation wording.

## Release Preparation Defaults

- CLI binary version follows the Rust workspace version and must report `ethos 0.1.0` for this
  release train.
- GitHub Release artifacts use SHA256 checksums in release notes only; detached signatures are
  deferred until a key-management policy is approved.
- PyPI publication, if later approved, must use trusted publishing rather than manual long-lived
  keys.
- npm publication, if later approved, must use a CI-held service account token.
- Python support starts at Python `>=3.8`.
- npm support starts with macOS arm64 and Linux x64 package selection only.

## Required Follow-Up Records

- Python public API policy.
- npm binary package policy.
- PDFium manual setup contract.
- Release artifact workflow and inventory validation.
- Release-candidate validation target.
- Launch-copy claim audit.
- Final release approval binding source, artifacts, checksums, wording, and retained blockers.

## Result

The first public release preparation lane may begin. Public release artifacts, public launch wording,
hosted surfaces, production positioning, and public benchmark reports or claims remain blocked until
the required follow-up records pass.
