# Milestone E Package Publication Manifest-Migration Prep Validation - 2026-06-21

## Purpose

Record the package publication prep follow-up for future Cargo manifest migration without approving
package publication.

This record defines the future manifest shape that any later dedicated publication approval must
review before registry-backed dependent candidate assembly. It does not change Cargo manifests,
approve real-version cargo publication, approve public installation, create package tags, publish
binaries, publish wheels, publish npm packages, approve hosted surfaces, approve production
positioning, approve public benchmark reports, approve public benchmark claims, or approve public
result wording. It does not resolve or soften blockers outside this manifest-migration prep slice.

## Status

Status: **pass for package manifest-migration prep with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `421fddd`
- Lane: package publication manifest-migration prep
- Evidence area: future public package name migration, workspace dependency alias shape, and
  dependent candidate source-tree dependency keys

## Evidence Review

- Current Cargo manifests remain source-tree manifests. No Cargo manifest is changed by this
  record.
- The current in-tree core package remains `name = "ethos-core"` and `publish = false`.
- A later dedicated publication approval must review a future core package-name migration to
  `name = "ethos-doc-core"` before any real-version cargo publication can proceed.
- A later dedicated publication approval must review a workspace dependency alias shaped as:

```toml
ethos-core = { package = "ethos-doc-core", path = "crates/ethos-core", version = "<approved-version>", default-features = false }
```

- The dependent candidate crates should keep stable source dependency keys after that future
  alias is reviewed:

```toml
ethos-core = { workspace = true, features = ["grounding", "verify-types"] }
ethos-core = { workspace = true, features = ["full"] }
```

- The first dependent line is the future `ethos-verify` dependency shape.
- The second dependent line is the future `ethos-pdf` dependency shape.
- The `ethos-doc-core` package-name migration must happen before `ethos-verify` or `ethos-pdf`
  registry-backed dependent candidate assembly.
- `ethos-doc` and `ethos-rag` remain reserved placeholders with no in-tree package manifests.

## Blockers Retained

- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Public installation from crates.io remains blocked.
- Registry-backed dependent package assembly remains blocked until a later dedicated publication
  approval.
- Package dependency manifest activation remains blocked until a later dedicated publication
  approval.
- Real package version selection and package tag creation remain blocked until a later dedicated
  publication approval.
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_manifest_migration_prep.py
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
