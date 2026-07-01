# v0.3.0 Version Activation Validation - 2026-07-01

Validated source HEAD before this record: `57e3821`.

v0.3.0 version activation source commit:
`57e3821b63b119ee6ca8e52322ddde2fb05dde66`.

v0.3.0 version activation source tree:
`7fd3dd7bcd4d8b503483a06752fdc5e5cb587695`.

Status: **v0.3.0 release-candidate source versions activated; package publication, tag creation,
artifact publication, npm alignment, installable wording, and DocuShell integration remain
blocked**

This record activates source/package metadata for the approved `v0.3.0` app-answer-release
release-candidate lane after
`docs/validation/v0-3-0-release-approval-decision-validation-2026-07-01.md` accepted source
activation on `dev/v0-3-approval-packet`.

## Activated Source Versions

Rust and Python source/package metadata move to `0.3.0`:

- Rust workspace package version and internal Rust path-dependency version pins.
- `Cargo.lock` workspace package entries.
- Python `pyproject.toml` metadata.
- Python `ethos_pdf.__version__`.

npm remains at `0.2.1`. The npm package is still a CLI binary distribution package, not a Node API
or Node SDK, and no npm CLI alignment release is approved by this record.

## Release-Candidate Wording

Version-pinned public install commands remain on the current published `0.2.0` Rust/Python and
`0.2.1` npm evaluation surfaces until publication, registry/artifact availability, smoke evidence,
and wording closeout records pass.

The allowed v0.3.0 wording is release-candidate wording only:

> v0.3.0 source versions are activated for app-answer-release contract validation.

No `0.3.0` registry install wording is approved until publication, registry availability, artifact
availability, and clean smoke tests are recorded.

## Boundary

This record does not approve a release, does not approve a tag, does not approve package publish,
does not approve npm publish, does not approve PyPI publish, does not approve crates.io publish,
does not approve a GitHub Release artifact, does not approve public installation wording for
`0.3.0`, does not approve npm CLI alignment, does not approve a Node API, Node SDK, N-API binding,
or WASM package, does not approve hosted surfaces, does not approve production positioning, does
not approve Windows packaged artifacts, does not approve bundled project-maintained PDFium builds,
does not approve public benchmark reports, does not approve public benchmark claims, does not
approve speed, footprint, parser-quality, table-quality, or production claims, does not approve
`ethos-doc`, does not approve `ethos-rag`, and does not approve DocuShell integration.

## Required Before Any Public 0.3.0 Install Wording

- Build and smoke exact `0.3.0` source/package candidates from the version-activated source commit.
- Record exact Rust crate package artifacts and dependency ordering for `0.3.0`.
- Record exact Python wheel artifacts and helper smoke evidence for `ethos-pdf==0.3.0`.
- Record CLI artifact evidence only if a later decision includes CLI artifacts.
- Record npm evidence only if a later decision explicitly includes npm CLI alignment.
- Re-run public posture, claims, license/NOTICE, private-path, and source-binding checks after any
  public-facing install wording changes.
- Record manual operator evidence for any credentialed publish or GitHub Release action.

## Validation Commands

```sh
cargo test --locked --workspace
make app-answer-release-contract PYTHON=python3
python3 .github/scripts/test_v0_3_0_version_activation.py
python3 .github/scripts/test_v0_3_0_release_approval_decision.py
python3 .github/scripts/test_app_answer_release_release_prep.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
make v0-3-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.3.0 release-candidate source versions activated
Rust and Python metadata now point to 0.3.0 for app-answer-release candidate validation
npm remains at 0.2.1 and public install commands remain on the current published baseline until
separate publication, smoke, and closeout records pass
```
