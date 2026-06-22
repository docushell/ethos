# Milestone E Package Publication Manifest Activation Applied Validation - 2026-06-22

## Purpose

Record that the package-publication candidate manifest activation has been applied to source for
review while retaining the package-publication blockers.

This record does not approve package publication, public installation, public installation wording,
package tag creation, removing `publish = false`, or real-version cargo publish.

## Status

Status: **pass for source manifest activation applied with publication blocked**.

Decision: source manifest activation is applied for review only; manual exact approval remains
required before any publication action.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `e517d76`
- Manifest activation source commit before this record:
  `e517d76c7c5f34984f62181769809637e7123bbc`
- Manifest activation source tree before this record:
  `b0cdeca1387f2080a1f9dca4f075e3a4bd7a92ec`
- Lane: package publication
- Prior approval decision refresh record:
  `docs/validation/milestone-e-package-publication-approval-decision-refresh-validation-2026-06-22.md`
- Candidate activation evidence record:
  `docs/validation/milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md`
- Approval owner: `docushell-admin`

## Activation Applied

- Root workspace dependency key remains `ethos-core`, with `package = "ethos-doc-core"` and
  path `crates/ethos-core`.
- `crates/ethos-core/Cargo.toml` uses package name `ethos-doc-core`.
- `crates/ethos-core/Cargo.toml` sets `[lib] name = "ethos_core"` so Rust imports remain
  `ethos_core`.
- `crates/ethos-verify/Cargo.toml` keeps the workspace dependency key `ethos-core` with
  `grounding` and `verify-types`.
- `crates/ethos-pdf/Cargo.toml` keeps the workspace dependency key `ethos-core` with `full`.
- `Cargo.lock` resolves the source package as `ethos-doc-core`.

## Blockers Retained

- `publish = false` remains in `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`.
- `publication_status = "blocked"` remains in the candidate crate metadata.
- No package publication version is selected.
- No package tag is created.
- No source-tree package registry is created.
- Public installation wording remains blocked.
- Public installation remains blocked.
- Package publication remains blocked.
- Real-version cargo publish remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public reports remain blocked.
- Public result wording remains blocked.

## Required Before Later Approval

Before any later package-publication approval can be recorded, `docushell-admin` must manually
approve or reject:

- exact candidate crate list for the first package-publication surface
- exact package version map
- exact package tag names and source binding
- exact registry-equivalent dependent package assembly evidence after this source activation
- exact public installation wording and explicit exclusions
- posture, claims, and Milestone E prep gate results after the exact wording and approval record
- whether any `publish = false` change is approved

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_manifest_activation_applied.py
python3 .github/scripts/test_milestone_e_package_publication_candidate_activation_evidence.py
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make package-publication-dry-run-smoke PYTHON=<python>
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Source manifest activation applied for review
ethos-doc-core package name and ethos_core library name confirmed
ethos-verify and ethos-pdf dependency keys remain workspace-scoped
publish=false and publication_status=blocked retained
Package publication and public installation remained blocked
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
