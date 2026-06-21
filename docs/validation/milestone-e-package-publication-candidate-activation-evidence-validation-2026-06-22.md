# Milestone E Package Publication Candidate Activation Evidence Validation - 2026-06-22

## Purpose

Record repeatable candidate package activation evidence for the package-publication lane after the
current package-publication approval request was rejected.

This record validates a temporary, non-public package activation workspace. It does not change the
source Cargo manifests, select a package publication version, create package tags, approve package
publication, approve public installation, approve public installation wording, or publish any
package.

## Status

Status: **pass for package publication candidate activation evidence with publication blocked**.

Decision: candidate activation evidence recorded; package publication remains blocked.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Package publication remains blocked. Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `6cf211c`
- Candidate activation evidence source commit: `6cf211cfae82c8ba7d6454a71e0922bd95a01f28`
- Candidate activation evidence source tree: `ae76bc588b64dc1e8087d9096d52545a3560c2c0`
- Lane: package publication
- Candidate packages: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
- Candidate package version: `0.1.0`
- Evidence command: `.github/scripts/package_publication_candidate_activation.py --json`

## Candidate Activation Shape Validated

- The temporary workspace changes `crates/ethos-core` package name from `ethos-core` to
  `ethos-doc-core`.
- The temporary workspace sets `[lib] name = "ethos_core"` for the renamed core package so Rust
  imports continue to use `ethos_core`.
- The temporary workspace keeps dependency key `ethos-core` while resolving package
  `ethos-doc-core`.
- `ethos-verify` retains core features `grounding` and `verify-types`.
- `ethos-pdf` retains core feature `full`.
- The temporary workspace assembles `ethos-doc-core-0.1.0.crate`,
  `ethos-verify-0.1.0.crate`, and `ethos-pdf-0.1.0.crate`.
- The temporary workspace packages the candidate core package with Cargo, uses Cargo's package file
  list for dependent candidates, and assembles dependent candidate archives without replacing the
  full crates.io source.
- An unpacked registry-equivalent consumer resolves `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf` and passes `cargo check --locked --offline`.

## Source Packaging Fix

`ethos-pdf` now carries `crates/ethos-pdf/assets/ethos-deterministic-v1.json` and includes that
crate-local profile copy. The crate-local profile is kept byte-identical to
`profiles/ethos-deterministic-v1.json`, which makes the packaged `ethos-pdf` crate self-contained
for this profile include while preserving the canonical source-tree profile path.

## Non-Approvals

- This evidence does not approve package publication.
- This evidence does not approve public installation.
- This evidence does not approve public installation wording.
- This evidence does not select a package publication version.
- This evidence does not create package tags.
- This evidence does not change source Cargo manifests.
- This evidence does not create a source-tree package registry.
- This evidence does not approve real-version cargo publish.
- This evidence does not approve hosted surfaces.
- This evidence does not approve production positioning.
- This evidence does not approve public benchmark reports.
- This evidence does not approve public benchmark claims.

## Retained Blockers

- exact package publication approval remains required
- exact package tag creation remains blocked
- package dependency manifest activation remains blocked for source manifests
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
python3 .github/scripts/test_milestone_e_package_publication_candidate_activation_evidence.py
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Package publication candidate activation evidence validation passed
Temporary candidate workspace assembled ethos-doc-core, ethos-verify, and ethos-pdf package artifacts
Registry-equivalent consumer check passed
Source Cargo manifests remained blocked and unchanged for publication
Package publication and public installation remained blocked
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
