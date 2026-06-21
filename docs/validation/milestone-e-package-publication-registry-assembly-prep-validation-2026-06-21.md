# Milestone E Package Publication Registry-Assembly Prep Validation - 2026-06-21

## Purpose

Record the package publication prep follow-up for future registry-backed dependent candidate
assembly without approving package publication.

This record defines the future non-public assembly rehearsal boundary that any later dedicated
publication approval must review before dependent candidate assembly. It does not create a registry,
change Cargo manifests, approve real-version cargo publication, approve public installation, create
package tags, publish binaries, publish wheels, publish npm packages, approve hosted surfaces,
approve production positioning, approve public benchmark reports, approve public benchmark claims,
or approve public result wording. It does not resolve or soften blockers outside this
registry-assembly prep slice.

## Status

Status: **pass for package registry-assembly prep with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `bc94861`
- Lane: package publication registry-assembly prep
- Evidence area: future non-public dependent candidate assembly rehearsal boundary

## Evidence Review

- Current Cargo manifests remain source-tree manifests. No Cargo manifest is changed by this
  record.
- No registry is created by this record.
- A later dedicated publication approval must review registry-backed dependent assembly only after
  package dependency manifest activation and real package version selection are explicitly
  approved.
- Any future rehearsal must use a non-public local registry or registry-equivalent source override
  assembled from reviewed candidate artifacts only.
- The future `ethos-doc-core` candidate must be assembled first from the reviewed `crates/ethos-core`
  source path and approved package version.
- The future `ethos-verify` dependent candidate must resolve dependency key `ethos-core` to
  candidate package `ethos-doc-core` and retain `features = ["grounding", "verify-types"]`.
- The future `ethos-pdf` dependent candidate must resolve dependency key `ethos-core` to candidate
  package `ethos-doc-core`, retain `features = ["full"]`, and keep the PDFium boundary confirmed.
- `ethos-doc` and `ethos-rag` remain reserved placeholders with no in-tree package manifests.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Registry-backed dependent package assembly activation remains blocked until a later dedicated
  publication approval.
- Package dependency manifest activation remains blocked until a later dedicated publication
  approval.
- Real package version selection and package tag creation remain blocked until a later dedicated
  publication approval.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_registry_assembly_prep.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Explicit Boundaries

- Public reports remain blocked.
- Public result wording remains blocked.
- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Release artifacts remain blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- npm packages remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Project-maintained PDFium builds remain blocked.
