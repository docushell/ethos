# Patch 0.1.2 Artifact/Package Evidence Validation - 2026-06-24

Validated source HEAD before this record: `6f81938`.

Patch 0.1.2 artifact/package evidence source commit:
`6f819381e189e98f5aa3177deb52901c89447ab4`.

Patch 0.1.2 artifact/package evidence source tree:
`7cae3956d5d01aac1005b675332c97451df3cbb8`.

Status: **patch 0.1.2 artifact/package evidence prep recorded; publication remains blocked**

This record captures the first source-bound artifact/package evidence gate after patch `0.1.2`
source version activation. It validates that the current source can assemble candidate Rust crate
artifacts and a candidate Python wheel for `0.1.2` without publishing anything and without changing
public install wording.

## Subject

- Repository: `docushell/ethos`
- Lane: patch `0.1.2` artifact/package evidence prep
- Source commit: `6f819381e189e98f5aa3177deb52901c89447ab4`
- Source tree: `7cae3956d5d01aac1005b675332c97451df3cbb8`
- Rust candidate packages: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
- Python candidate package: `ethos-pdf==0.1.2`
- Python candidate wheel: `ethos_pdf-0.1.2-py3-none-any.whl`
- npm package metadata remains `@docushell/ethos-pdf@0.1.1`

## Local Evidence Gate

The guard `python3 .github/scripts/test_patch_0_1_2_artifact_package_evidence.py` dynamically
checks the following in temporary workspaces:

- `python3 .github/scripts/package_publication_candidate_activation.py --json` reports
  candidate version `0.1.2`.
- Candidate crate files are assembled for:
  - `ethos-doc-core-0.1.2.crate`
  - `ethos-verify-0.1.2.crate`
  - `ethos-pdf-0.1.2.crate`
- Each candidate crate artifact reports a SHA256-shaped digest.
- The registry-equivalent consumer check passes offline.
- The candidate activation report keeps `package_publication_approved` false.
- The candidate activation report keeps `public_installation_approved` false.
- `python3 -m build --wheel --outdir <candidate-dir>` builds
  `ethos_pdf-0.1.2-py3-none-any.whl`.
- The wheel reports `Name: ethos-pdf`, `Version: 0.1.2`,
  `License-Expression: Apache-2.0`, `Requires-Python: >=3.8`, and `Tag: py3-none-any`.
- Local install/import smoke resolves version `0.1.2`, `EthosCli`, and `EthosCommandError`.

## Release Workflow Prep

The draft CLI artifact workflow now passes `--expected-version "ethos 0.1.2"` to
`smoke_release_cli_artifact.py`. This lane records only workflow preparedness for the version
activated source; it does not record downloaded `0.1.2` GitHub Actions artifacts or approve
publishing those artifacts to a GitHub Release.

## Boundary

This record does not approve publishing any package. This record does not approve PyPI upload. This
record does not approve crates.io publication. This record does not approve npm publication. This
record does not approve GitHub Release artifact publication. This record does not approve creating
or moving a tag. This record does not refresh the checked-in npm vendor payload. This record does
not approve public installation wording for `0.1.2`.

The public install baseline remains `0.1.1` until separate registry/GitHub Release evidence,
operator actions, npm vendor refresh, and public wording closeout records pass.

## Retained Blockers

- Actual registry publication remains blocked.
- GitHub Release artifact publication remains blocked.
- npm vendor refresh remains blocked.
- npm publication remains blocked.
- Public installation wording remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Commands

```sh
python3 .github/scripts/test_patch_0_1_2_artifact_package_evidence.py
python3 .github/scripts/test_patch_0_1_2_version_activation.py
python3 .github/scripts/test_release_artifact_workflow_prep.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/public_boundary_claims_gate.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 artifact/package evidence prep recorded
0.1.2 crate candidates and Python wheel candidate are locally evidence-checked
public install baseline remains 0.1.1
publication and GitHub Release artifact actions remain blocked pending separate approval and operator evidence
```
