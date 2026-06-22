# Milestone E Package Publication Current Registry-Equivalent Assembly Validation - 2026-06-22

## Purpose

Refresh registry-equivalent dependent package assembly evidence after source manifest activation
and the current dry-run smoke evidence refresh.

This record validates the current non-public assembly rehearsal for `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf`. It does not approve package publication, public installation,
public installation wording, package tag creation, removing `publish = false`, or real-version
cargo publish.

## Status

Status: **pass for current registry-equivalent assembly evidence with publication blocked**.

Decision: current registry-equivalent assembly evidence is recorded; package publication remains
blocked.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `b48e2f2`
- Current registry-equivalent assembly source commit:
  `b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875`
- Current registry-equivalent assembly source tree:
  `4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3`
- Lane: package publication
- Candidate packages: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
- Candidate package version: `0.1.0`
- Evidence command: `.github/scripts/package_publication_candidate_activation.py --json`
- Current dry-run smoke record:
  `docs/validation/milestone-e-package-publication-current-dry-run-smoke-validation-2026-06-22.md`
- Manifest activation applied record:
  `docs/validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md`

## Evidence Review

- The current source tree already uses package name `ethos-doc-core` for `crates/ethos-core` and
  keeps Rust library name `ethos_core`.
- The current source tree keeps workspace dependency key `ethos-core` while resolving package
  `ethos-doc-core`.
- `ethos-verify` retains core features `grounding` and `verify-types`.
- `ethos-pdf` retains core feature `full`.
- The non-public assembly command assembles `ethos-doc-core-0.1.0.crate`,
  `ethos-verify-0.1.0.crate`, and `ethos-pdf-0.1.0.crate`.
- The unpacked registry-equivalent consumer resolves `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf` and passes `cargo check --locked --offline`.
- Source manifests retain `publish = false` and `publication_status = "blocked"`.
- No package tag exists for `ethos-package-ethos-doc-core-0.1.0`,
  `ethos-package-ethos-verify-0.1.0`, or `ethos-package-ethos-pdf-0.1.0`.

## Non-Approvals

- This evidence does not approve package publication.
- This evidence does not approve public installation.
- This evidence does not approve public installation wording.
- This evidence does not select a package publication version.
- This evidence does not create package tags.
- This evidence does not remove `publish = false`.
- This evidence does not create a source-tree package registry.
- This evidence does not approve real-version cargo publish.
- This evidence does not approve hosted surfaces.
- This evidence does not approve production positioning.
- This evidence does not approve public benchmark reports.
- This evidence does not approve public benchmark claims.

## Retained Blockers

- exact package publication approval remains required
- exact package version selection remains blocked
- exact package tag creation remains blocked
- publish-flag activation remains blocked
- public installation wording approval remains blocked
- public installation remains blocked
- package publication remains blocked
- real-version cargo publish remains blocked
- hosted surfaces remain blocked
- production positioning remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Commands

```sh
python3 .github/scripts/package_publication_candidate_activation.py --json
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
Current registry-equivalent assembly validation passed
Temporary package artifacts assembled for ethos-doc-core, ethos-verify, and ethos-pdf
Registry-equivalent consumer check passed
Source manifests retained publish=false and publication_status=blocked
Package publication and public installation remained blocked
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
