# Milestone E Package Publication Dry-Run Smoke Closeout Validation - 2026-06-21

## Purpose

Record the package publication prep follow-up for local dry-run smoke evidence without approving
package publication.

This record covers the current source-tree smoke path for `ethos-core`, `ethos-verify`, and
`ethos-pdf`. It does not cover real-version cargo publication, public installation from crates.io,
binaries, wheels, npm packages, hosted surfaces, production positioning, public benchmark reports,
public benchmark claims, or public result wording. It does not resolve or soften blockers outside
this dry-run smoke slice.

## Status

Status: **pass for local dry-run smoke evidence with blockers retained**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `d1c9384`
- Lane: package publication dry-run smoke
- Evidence area: local package assembly and source-tree candidate smoke path

## Evidence Review

- `cargo package --locked --offline -p ethos-core --allow-dirty --no-verify` passes for the current
  in-tree core candidate while `publish = false` remains set.
- `cargo package --list --locked --offline -p ethos-core --allow-dirty` lists the expected local
  package inputs, including README, NOTICE, manifest, lockfile, and source files.
- `cargo check --locked --offline -p ethos-verify` passes for the current source-tree candidate
  while `publish = false` remains set.
- `cargo check --locked --offline -p ethos-pdf` passes for the current source-tree candidate while
  `publish = false` remains set and PDFium remains caller-provided.
- Direct local package assembly for `ethos-verify` and `ethos-pdf` remains blocked because Cargo
  resolves their in-tree `ethos-core` dependency as a registry dependency during package
  preparation, and no matching package named `ethos-core` is available for this future public
  dependency path.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Dependent package assembly remains blocked until package dependency naming and ordering are
  resolved.
- `ethos-doc-core` is the reserved public identifier for the current in-tree `ethos-core` package
  candidate; the package dependency path still needs a future reviewed migration.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Version/tag policy reconciliation remains incomplete.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
make package-publication-dry-run-smoke PYTHON=<python>
python3 .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py
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
