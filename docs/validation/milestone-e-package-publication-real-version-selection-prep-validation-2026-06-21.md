# Milestone E Package Publication Real-Version-Selection Prep Validation - 2026-06-21

## Purpose

Record the package publication prep follow-up for future real-version selection without approving
package publication.

This record defines the future version-selection review boundary that any later dedicated
publication approval must use before real-version cargo publication, package tag creation, or
public installation. It does not select a package publication version, change Cargo manifests,
approve real-version cargo publication, approve public installation, create package tags, publish
binaries, publish wheels, publish npm packages, approve hosted surfaces, approve production
positioning, approve public benchmark reports, approve public benchmark claims, or approve public
result wording. It does not resolve or soften blockers outside this real-version-selection prep
slice.

## Status

Status: **pass for package real-version-selection prep with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `57e3782`
- Lane: package publication real-version-selection prep
- Evidence area: future package version selection review boundary and retained placeholder state

## Evidence Review

- No package publication version is selected by this record.
- The workspace `0.1.0` remains source-tree only.
- The crates.io reserved `0.0.0-reserved.0` placeholders remain placeholders.
- A future real-version selection review must bind an exact SemVer candidate to:
  - candidate crate set and package names;
  - source commit and tree;
  - candidate package manifests;
  - package dependency manifest activation plan;
  - registry-backed dependent assembly evidence;
  - package tag namespace and exact tag name;
  - public-surface posture and claims gates after exact wording changes.
- Package tags must remain separate from the approved source-snapshot tag namespace.
- `ethos-doc` and `ethos-rag` remain reserved placeholders with no in-tree package manifests.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Real package version selection approval remains blocked until a later dedicated publication
  approval.
- Package tag creation remains blocked until a later dedicated publication approval.
- Registry-backed dependent package assembly activation remains blocked until a later dedicated
  publication approval.
- Package dependency manifest activation remains blocked until a later dedicated publication
  approval.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_real_version_selection_prep.py
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
