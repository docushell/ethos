# Milestone E Package Publication Current Dry-Run Smoke Validation - 2026-06-22

## Purpose

Refresh the package-publication dry-run smoke evidence after source manifest activation changed the
current package selector from `ethos-core` to `ethos-doc-core`.

This record supersedes the current approval-precondition pointer for dry-run smoke evidence. It
does not rewrite the historical 2026-06-21 dry-run smoke record, approve package publication,
approve public installation, approve public installation wording, create package tags, remove
`publish = false`, or approve real-version cargo publish.

## Status

Status: **pass for current source-tree dry-run smoke evidence with blockers retained**.

Decision: current dry-run smoke evidence is refreshed for the source tree after manifest
activation; package publication remains blocked.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `4d337b4`
- Current dry-run smoke source commit:
  `4d337b4ceffef2c3ace4e76500d3a10c10068e97`
- Current dry-run smoke source tree:
  `cc003907fd59e94cd93eb864e34c4d08ded766af`
- Lane: package publication
- Candidate packages: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
- Candidate package version: `0.1.0`
- Prior dry-run smoke record:
  `docs/validation/milestone-e-package-publication-dry-run-smoke-closeout-validation-2026-06-21.md`
- Manifest activation applied record:
  `docs/validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md`

## Evidence Review

- `cargo package --locked --offline -p ethos-doc-core --allow-dirty --no-verify` passes for the
  current in-tree core candidate while `publish = false` remains set.
- `cargo package --list --locked --offline -p ethos-doc-core --allow-dirty` lists the expected
  local package inputs, including README, NOTICE, manifest, lockfile, and source files.
- `cargo check --locked --offline -p ethos-verify` passes for the current source-tree candidate
  while `publish = false` remains set.
- `cargo check --locked --offline -p ethos-pdf` passes for the current source-tree candidate while
  `publish = false` remains set and PDFium remains caller-provided.
- Registry-equivalent dependent package assembly evidence is tracked separately by
  `docs/validation/milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md`.
- Source manifest activation is tracked separately by
  `docs/validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md`.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Public installation wording remains blocked.
- Package tag creation remains blocked.
- Removing `publish = false` remains blocked.
- Registry-backed dependent package assembly activation remains blocked until exact approval.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests,
  README files, metadata, and support expectations are prepared.
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
