# v0.2.0 Version Activation Validation - 2026-06-25

Validated source HEAD before this record: `523e114`.

v0.2.0 version activation source commit:
`523e1143bec52e16e596593f5dd649df741b4971`.

v0.2.0 version activation source tree:
`8f13de3588a36927635a967cf120fba8f73a39f6`.

Status: **v0.2.0 release-candidate source versions activated; package publication, tag creation,
artifact publication, and installable wording remain blocked**

This record activates source/package metadata for the approved `v0.2.0` release-candidate lane
after `docs/validation/v0-2-0-release-approval-decision-validation-2026-06-25.md` landed on
`dev/v0-2-approval-packet`.

## Activated Source Versions

Rust, Python, and npm source/package metadata move to `0.2.0`:

- Rust workspace package version and internal Rust path-dependency version pins.
- `Cargo.lock` workspace package entries.
- Python `pyproject.toml` metadata.
- Python `ethos_pdf.__version__`.
- npm `packages/npm/ethos-pdf/package.json` metadata.

## Release-Candidate Wording

Version-pinned public install commands remain on the approved `0.1.2` evaluation baseline until
publication, registry/artifact availability, smoke evidence, and wording closeout records pass.

The allowed v0.2.0 wording is release-candidate wording only:

> v0.2.0 release-candidate source versions are activated for JSON verification and evidence
> anchoring.

No `0.2.0` registry install wording is approved until publication, registry availability, artifact
availability, and clean smoke tests are recorded.

## Boundary

This record does not approve a release, does not approve a tag, does not approve package publish,
does not approve npm publish, does not approve PyPI publish, does not approve crates.io publish,
does not approve a GitHub Release artifact, does not approve public installation wording for
`0.2.0`, does not approve hosted surfaces, does not approve production positioning, does not
approve Windows packaged artifacts, does not approve bundled project-maintained PDFium builds,
does not approve public benchmark reports, does not approve public benchmark claims, does not
approve speed, footprint, parser-quality, table-quality, or production claims, does not approve
`ethos-doc`, and does not approve `ethos-rag`.

## Required Before Any Public 0.2.0 Install Wording

- Build and smoke exact `0.2.0` CLI artifacts from the version-activated source commit.
- Record exact Rust crate package artifacts and dependency ordering for `0.2.0`.
- Record exact Python wheel artifacts for `0.2.0`.
- Record exact npm package artifact evidence for `@docushell/ethos-pdf@0.2.0`.
- Re-run public posture, claims, license/NOTICE, private-path, and source-binding checks after any
  public-facing install wording changes.
- Record manual operator evidence for any credentialed publish or GitHub Release action.

## Validation Commands

```sh
python3 .github/scripts/test_v0_2_0_version_activation.py
python3 .github/scripts/test_v0_2_0_release_approval_decision.py
python3 .github/scripts/test_v0_2_0_release_approval_request.py
python3 .github/scripts/test_python_public_api_policy.py
python3 .github/scripts/test_npm_binary_package_scaffold.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
make v0-2-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.2.0 release-candidate source versions activated
Rust, Python, and npm metadata now point to 0.2.0 for candidate validation
Public install commands and installable wording remain on approved 0.1.2 evaluation surfaces until
separate publication, smoke, and closeout records pass
```
