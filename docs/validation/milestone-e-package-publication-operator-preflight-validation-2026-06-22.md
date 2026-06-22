# Milestone E Package Publication Operator Preflight Validation - 2026-06-22

- Validated source HEAD before this record: `421bed8`

Operator preflight source commit: `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`

Operator preflight source tree: `aa0d5d31d879540fd0044052dfeb747f12b64204`

Status: **pass for operator preflight packet with registry action blocked**

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Scope

This record defines the manual operator evidence required after the refreshed package tag binding
in
`docs/validation/milestone-e-package-publication-tag-binding-refresh-validation-2026-06-22.md`.

It does not create package tags, run `cargo publish`, update public installation instructions, or
approve any surface outside the bounded `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
candidate set.

## Manual Evidence Required

- crates.io owner/account confirmation remains manual evidence.
- reserved name ownership for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` must be confirmed
  before any registry action.
- The operator must confirm the working source is the refreshed source commit
  `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e` or a later reviewed source commit with an updated
  binding record.
- dependency order: `ethos-doc-core`, then `ethos-verify`, then `ethos-pdf`.
- Package tags must be created only after manual confirmation:
  `ethos-package-ethos-doc-core-0.1.0`, `ethos-package-ethos-verify-0.1.0`, and
  `ethos-package-ethos-pdf-0.1.0`.

## Operator Command Packet

No command in this record has been executed against crates.io.

The exact publish command order, after manual evidence is recorded separately, is:

```sh
cargo publish --locked -p ethos-doc-core
cargo publish --locked -p ethos-verify
cargo publish --locked -p ethos-pdf
```

The exact pre-command verification set is:

```sh
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/test_milestone_e_package_publication_tag_binding_refresh.py
python3 .github/scripts/test_milestone_e_package_publication_operator_preflight.py
make package-publication-dry-run-smoke PYTHON=<jsonschema-venv>/bin/python
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
cargo test --locked --workspace --all-features
git diff --check
```

## Retained Blockers

- No package tag is created by this record.
- `cargo publish` remains blocked until manual registry evidence is supplied and recorded.
- Public installation instructions remain blocked until package availability and wording are
  explicitly revalidated.
- wheels, npm packages, binaries, hosted surfaces, production positioning, public benchmark
  reports, public benchmark claims, project-maintained PDFium builds, `ethos-doc`, and `ethos-rag`
  remain excluded.
- Public reports remain blocked.
- Public result wording remains blocked.
- No local registry config is created: `.cargo/config.toml` remains absent.
- No local package registry directory is retained: `target/package-registry` remains absent.

## Result

The operator preflight packet is recorded. Manual registry evidence remains required, package tag
creation remains blocked, public installation remains blocked, and registry publication remains
blocked.
