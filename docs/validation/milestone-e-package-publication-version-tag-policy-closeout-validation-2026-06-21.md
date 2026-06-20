# Milestone E Package Publication Version Tag Policy Closeout Validation - 2026-06-21

## Purpose

Record the package publication prep follow-up for version and tag policy without approving package
publication.

This record separates source-tree workspace versions, crates.io reservation placeholders, source
snapshot tags, and any later package tag namespace. It does not approve real-version cargo
publication, public installation, package tag creation, binaries, wheels, npm packages, hosted
surfaces, production positioning, public benchmark reports, public benchmark claims, or public
result wording. It does not resolve or soften blockers outside this version/tag policy slice.

## Status

Status: **pass for version/tag policy follow-up with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `fb869c6`
- Lane: package publication version/tag policy
- Evidence area: source-tree version, reserved placeholder version, source snapshot tag, and future
  package tag namespace separation

## Evidence Review

- Workspace package version `0.1.0` remains a source-tree version. It is not a public installation
  claim and does not approve registry publication.
- ADR-0006 crates.io reservations remain `0.0.0-reserved.0` placeholders. Placeholder
  reservations are not installable packages and carry no public API.
- The approved source snapshot tag remains `ethos-source-snapshot-660f268`.
- Future package tags must use a distinct namespace from source snapshot tags. The candidate
  namespace for any later package publication review is `ethos-package-<crate-name>-<version>`.
- A later package publication approval must name the exact crate set, exact package version, exact
  tag, exact source HEAD, and dry-run/install smoke evidence before any real-version publication.
- No package tag is created by this record.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Real package version selection remains blocked until a later dedicated publication approval.
- Package tag creation remains blocked until a later dedicated publication approval.
- Dependent package assembly remains blocked until package dependency naming and ordering are
  resolved.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_version_tag_policy.py
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
