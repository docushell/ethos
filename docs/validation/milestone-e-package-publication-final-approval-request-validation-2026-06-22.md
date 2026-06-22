# Milestone E Package Publication Final Approval Request Validation - 2026-06-22

## Purpose

Record the exact package-publication approval request packet for decider review after current
source manifest activation, current dry-run smoke evidence, and current registry-equivalent
assembly evidence are present.

This record does not approve package publication, public installation, public installation wording,
package tag creation, removing `publish = false`, metadata activation, or real-version cargo
publish. It records the exact fields that must be accepted or rejected by the decider.

## Status

Status: **pass for exact package-publication approval request packet with publication blocked**.

Decision: exact approval request packet recorded for decider review.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `b48e2f2`
- Final approval request source commit:
  `b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875`
- Final approval request source tree:
  `4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3`
- Lane: package publication
- Current dry-run smoke record:
  `docs/validation/milestone-e-package-publication-current-dry-run-smoke-validation-2026-06-22.md`
- Current registry-equivalent assembly record:
  `docs/validation/milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md`
- Manifest activation applied record:
  `docs/validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md`

## Exact Request Fields

- Decision requested: approve exact crates.io publication preparation inputs for later decider
  signoff.
- Approver requested: docushell-admin acting as decider.
- Date requested: 2026-06-22.
- Exact candidate crate list requested: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` only.
- Exact package version map requested: `ethos-doc-core = 0.1.0`, `ethos-verify = 0.1.0`, and
  `ethos-pdf = 0.1.0`.
- Exact package tag name set requested: `ethos-package-ethos-doc-core-0.1.0`,
  `ethos-package-ethos-verify-0.1.0`, and `ethos-package-ethos-pdf-0.1.0`.
- Exact package tag source commit requested: `b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875`.
- Exact package tag source tree requested: `4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3`.
- Exact manifest activation reviewed: `ethos-doc-core` package name is active in source, Rust
  library name remains `ethos_core`, and workspace dependency key `ethos-core` resolves package
  `ethos-doc-core`.
- Exact publish-flag activation requested later: remove `publish = false` from the three candidate
  crate manifests only after decider approval.
- Exact metadata activation requested later: change `publication_status = "blocked"` only after
  decider approval.
- Exact public installation wording requested later: Ethos Rust crates ethos-doc-core,
  ethos-verify, and ethos-pdf version 0.1.0 are proposed for crates.io installation only after
  explicit package-publication approval and package-tag creation. ethos-pdf requires
  caller-provided PDFium through ETHOS_PDFIUM_LIBRARY_PATH. Wheels, npm packages, binaries, hosted
  surfaces, production positioning, public benchmark reports, public benchmark claims,
  project-maintained PDFium builds, ethos-doc, and ethos-rag remain blocked.

## Explicit Exclusions

- wheels remain blocked
- npm packages remain blocked
- binaries remain blocked
- hosted surfaces remain blocked
- production positioning remains blocked
- public benchmark reports remain blocked
- public benchmark claims remain blocked
- project-maintained PDFium builds remain blocked
- `ethos-doc` remains excluded
- `ethos-rag` remains excluded
- broader public wording remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Evidence Bound To This Request

- Source binding: `b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875` /
  `4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3`.
- Current dry-run smoke: `ethos-doc-core` local package assembly passes; `ethos-verify` and
  `ethos-pdf` source-tree checks pass.
- Current registry-equivalent assembly: temporary candidate artifacts assemble and the unpacked
  consumer passes `cargo check --locked --offline`.
- PDFium boundary: `ethos-pdf` remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`; no
  project-maintained PDFium build is part of this request.
- Public-surface posture and claims gates must pass again after any later exact wording change.
- Milestone E prep must pass again after any later exact approval record.

## Non-Approvals

- This request packet does not approve package publication.
- This request packet does not approve public installation.
- This request packet does not approve public installation wording.
- This request packet does not create package tags.
- This request packet does not remove `publish = false`.
- This request packet does not activate package metadata.
- This request packet does not approve real-version cargo publish.
- This request packet does not approve hosted surfaces.
- This request packet does not approve production positioning.
- This request packet does not approve public benchmark reports.
- This request packet does not approve public benchmark claims.

## Retained Blockers

- Package publication remains blocked pending explicit decider approval.
- Public installation remains blocked pending explicit decider approval.
- Package tag creation remains blocked pending explicit decider approval.
- Publish-flag activation remains blocked pending explicit decider approval.
- Metadata activation remains blocked pending explicit decider approval.
- Real-version cargo publish remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public reports remain blocked.
- Public result wording remains blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_final_approval_request.py
python3 .github/scripts/test_milestone_e_package_publication_current_registry_assembly.py
python3 .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Final approval request packet validation passed
Exact candidate crate list, version map, tag names, source binding, and wording were recorded
Current dry-run smoke and registry-equivalent assembly evidence were recorded
Package publication and public installation remained blocked
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
