# Milestone E Package Publication Prep Approval Validation - 2026-06-20

## Purpose

Record the dedicated decision to approve internal package publication preparation for a narrow Rust
crate surface while keeping real-version package publication and public installation blocked.

This record approves preparation work only. It does not approve crate publication, real-version
`cargo publish`, public installation from crates.io, binaries, wheels, npm packages, release
artifacts, hosted surfaces, production positioning, public benchmark reports, public benchmark
claims, project-maintained PDFium builds, or any public performance, quality, footprint,
table-quality, or parser-quality claims. ADR-0005 remains an internal continuation decision only.

## Status

Status: **pass for package publication prep approval validation**.

Decision: approve package publication prep only.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and this
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `f93508e`
- Lane: package publication approval
- Prep surface: Rust crate publication preparation only
- Registry: crates.io
- Reserved version: `0.0.0-reserved.0`
- Approval owner: docushell-admin
- Decision date: 2026-06-20

## Exact Approved Public Wording

Ethos crate publication is in internal preparation only and remains blocked for public installation.
No Ethos crates are published; the reserved crates.io names remain 0.0.0-reserved.0 placeholders
with no public API. Wheels, npm packages, binaries, hosted surfaces, production positioning, and
public benchmark claims remain blocked.

## Exact Approved Prep Surface

The approved prep surface is limited to the five ADR-0006 reserved priority crates.io identifiers:

- `ethos-doc-core`
- `ethos-doc`
- `ethos-verify`
- `ethos-rag`
- `ethos-pdf`

Prep covers package inventory reconciliation, per-crate metadata/license/NOTICE/README readiness,
`cargo publish --dry-run` and smoke build path definition, publish version and tag policy, and the
PDFium packaging boundary decision. No real-version cargo publish is approved, and reservations
remain placeholder versions.

## Package Inventory Boundary

- `ethos-doc-core` maps to the in-tree `ethos-core` crate before any future publish prep can
  advance.
- `ethos-doc` has no in-tree workspace member yet and remains a reserved placeholder until a
  package owner, README, and metadata are prepared.
- `ethos-verify` maps to `crates/ethos-verify` and currently remains `publish = false`.
- `ethos-rag` has no in-tree workspace member yet and remains a reserved placeholder until a
  package owner, README, and metadata are prepared.
- `ethos-pdf` maps to `crates/ethos-pdf` and currently remains `publish = false`.

## Evidence Review Status

- Package inventory: reviewed; reserved-to-in-tree reconciliation remains a prep task.
- Package metadata/license/README review: not reviewed; prep deliverable.
- Install/build smoke path: not reviewed for packaged publication; source `cargo build --locked`
  is green, but `cargo publish --dry-run` and registry-install smoke remain prep deliverables.
- Version/tag policy: not ratified; prep must reconcile workspace `0.1.0` with
  `0.0.0-reserved.0` reservations.
- PDFium packaging boundary: reviewed as caller-provided PDFium only.
- Public-surface posture check: required after exact wording changes.
- Claims gate after exact wording changes: required after exact wording changes.
- Decider signoff: docushell-admin approved the exact prep wording and prep surface.

## PDFium Boundary

- `ethos-pdf` prep must bundle no PDFium binary.
- `ethos-pdf` prep must expose no PDFium types in public API.
- PDFium must remain caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.
- If the boundary cannot be guaranteed, `ethos-pdf` remains held out of the first crate surface.

## Explicit Exclusions

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Release artifacts remain blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- npm packages remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public reports remain blocked.
- Public result wording remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_prep_approval_validation_record.py
python3 .github/scripts/test_milestone_e_public_approval_lane_blockers.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Package publication prep approval validation passed
Package publication remains blocked
Public-surface posture and claims gates passed
Source CLI build path passed
Milestone E prep target passed
git diff --check passed
```
