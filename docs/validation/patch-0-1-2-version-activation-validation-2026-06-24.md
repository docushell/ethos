# Patch 0.1.2 Version Activation Validation - 2026-06-24

## Purpose

Record source/package version activation for the narrow patch `0.1.2` beta candidate after
`docs/validation/patch-0-1-2-readiness-prep-validation-2026-06-24.md` landed on `main`.

Validated source HEAD before this record: `0252cc7`.
Version-activation source commit: `0252cc7800d51cb1ec673698be5646b4fb945066`.
Version-activation source tree: `ec9e4481ab237192d10942e9ce8d0b4a908c15b8`.

## Activated Source Versions

Rust workspace and Python source/package metadata move to `0.1.2`:

- Workspace package version and internal Rust path-dependency version pins.
- `Cargo.lock` workspace package entries.
- Python `pyproject.toml` metadata.
- Python `ethos_pdf.__version__`.

npm remains at `0.1.1` until matching `0.1.2` CLI artifacts exist and a separate npm vendor-refresh
or publication lane records exact artifact evidence.

## Boundary

This record does not approve a release, does not approve a tag, does not approve package publish,
does not approve npm publish, does not approve PyPI publish, does not approve crates.io publish,
does not approve a GitHub Release artifact, does not approve public installation wording for
`0.1.2`, does not approve hosted surfaces, does not approve production positioning, does not
approve Windows packaged artifacts, does not approve bundled project-maintained PDFium builds,
does not approve public benchmark reports, does not approve public benchmark claims, does not
approve speed, footprint, parser-quality, table-quality, or production claims, does not approve
`ethos-doc`, and does not approve `ethos-rag`.

The current public install baseline remains `0.1.1` until separate package publication,
artifact-publication, registry/GitHub Release evidence, and operator action are completed.

## Required Before Any Public 0.1.2 Install Wording

- Build and smoke exact `0.1.2` CLI artifacts from the version-activated source commit.
- Record exact Rust crate package artifacts and dependency ordering for `0.1.2`.
- Record exact Python wheel artifacts for `0.1.2`.
- Refresh npm vendor payload only after matching `0.1.2` CLI artifacts exist.
- Re-run public posture, claims, source snapshot, license/NOTICE, and private-path checks after
  any public-facing install wording changes.
- Record manual operator evidence for any credentialed publish or GitHub Release action.

## Validation Commands

The version-activation lane should pass at least:

```sh
cargo check --locked -p ethos-cli
python3 .github/scripts/test_patch_0_1_2_version_activation.py
python3 .github/scripts/test_patch_0_1_2_readiness_prep.py
python3 .github/scripts/test_python_public_api_policy.py
python3 .github/scripts/test_npm_binary_package_scaffold.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/public_boundary_claims_gate.py
python3 .github/scripts/claims_gate.py
make light-check PYTHON=python3
git diff --check
```
