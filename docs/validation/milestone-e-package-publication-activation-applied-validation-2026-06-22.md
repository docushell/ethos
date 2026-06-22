# Milestone E Package Publication Activation Applied Validation - 2026-06-22

- Validated source HEAD before this record: `f50f294`

Activation applied source commit: `f50f2948b0536b3c75fe369558c94ce1155b73d1`

Activation applied source tree: `00c3e4df7a7b3b368659650601a2df76b63a2ce8`

Status: **pass for publish-flag and package metadata activation with registry action blocked**

## Scope

This record validates the source change requested by
`docs/validation/milestone-e-package-publication-publish-flag-activation-request-validation-2026-06-22.md`
after the decider accepted the bounded candidate surface in
`docs/validation/milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md`.

The applied source change is limited to the three accepted crates.io candidate manifests:

- `crates/ethos-core/Cargo.toml` for package `ethos-doc-core`
- `crates/ethos-verify/Cargo.toml` for package `ethos-verify`
- `crates/ethos-pdf/Cargo.toml` for package `ethos-pdf`

## Applied Manifest State

- `publish = false` is absent from the three accepted candidate manifests.
- `publication_status = "approved_for_crates_io_publication"` is present in the three accepted
  candidate manifests.
- `reserved_crates_io_version = "0.0.0-reserved.0"` remains present in the three accepted
  candidate manifests as reservation provenance.
- Non-candidate workspace crates remain unchanged and retain `publish = false`:
  `ethos-cli`, `ethos-layout`, and `ethos-tables`.
- The package name split remains intact: source path `crates/ethos-core`, package name
  `ethos-doc-core`, Rust library name `ethos_core`, and workspace dependency key `ethos-core`.
- `ethos-verify` still depends only on the workspace `ethos-core` key with `grounding` and
  `verify-types`; it does not depend on parser internals.
- `ethos-pdf` keeps PDFium caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH` and bundles no
  PDFium binary.

## Retained Blockers

- Ethos remains source-only pre-alpha for this source-tree approval boundary.
- Public reports remain blocked.
- Public result wording remains blocked.
- Package tag source binding must be refreshed to this activated source commit or a later reviewed
  source commit before package tags are created.
- No package tags are created by this record:
  `ethos-package-ethos-doc-core-0.1.0`, `ethos-package-ethos-verify-0.1.0`, and
  `ethos-package-ethos-pdf-0.1.0` remain absent.
- `cargo publish` remains blocked until refreshed binding, dry-run evidence, and operator evidence
  are recorded.
- Public installation instructions remain blocked until package availability and wording are
  explicitly revalidated.
- Wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark reports,
  public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag` remain
  excluded.
- No local registry config is created: `.cargo/config.toml` remains absent.
- No local package registry directory is retained: `target/package-registry` remains absent.

## Validation Commands

- `python3 .github/scripts/test_milestone_e_package_publication_activation_applied.py`
- `python3 .github/scripts/test_milestone_e_package_publication_candidate_activation_evidence.py`
- `python3 .github/scripts/test_milestone_e_package_publication_current_registry_assembly.py`
- `python3 .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py`
- `python3 .github/scripts/test_public_surface_posture.py`
- `python3 .github/scripts/claims_gate.py`
- `make package-publication-dry-run-smoke PYTHON=<python>`
- `make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python`
- `cargo build --locked -p ethos-cli`
- `cargo test --locked --workspace --all-features`
- `git diff --check`
