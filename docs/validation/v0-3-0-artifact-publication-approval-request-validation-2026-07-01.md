# v0.3.0 Artifact Publication Approval Request Validation - 2026-07-01

## Purpose

Record the exact v0.3.0 GitHub Release artifact publication approval request for decider review.
This record does not publish artifacts, create a GitHub Release, create tags, refresh npm vendor
binaries, publish npm, change public installation wording, change PDFium posture, or open any new
public surface.

Validated source HEAD before this record: `d6496e8`.

v0.3.0 artifact publication approval request source commit:
`d6496e82e613e653edc197db4cf4153271d131dc`.

v0.3.0 artifact publication approval request source tree:
`2594c63071c512f2c61e78b223a74406440a8516`.

## Evidence Inputs

- Release workflow: `.github/workflows/release.yml`
- Workflow run: `https://github.com/docushell/ethos/actions/runs/28531102130`
- Evidence record:
  `docs/validation/v0-3-0-draft-artifact-evidence-validation-2026-07-01.md`
- Run status: `completed`
- Run conclusion: `success`
- Run event: `workflow_dispatch`
- Run branch: `main`
- Run head SHA: `7287358475a96e827d536f0d2d250a1c2961ba84`

## Requested Artifact Evaluation Surface

The decider is asked to accept or reject only attaching these exact draft CLI artifacts and sidecars
to GitHub Release `v0.3.0` for release evaluation if and when the release target is authorized.
This request does not create the release, create the tag, upload release assets, or approve public
installation wording.

macOS arm64:

- `ethos-macos-arm64.tar.gz`
- `ethos-macos-arm64.tar.gz.sha256`
- `ethos-macos-arm64.inventory.json`
- `ethos-macos-arm64.smoke.json`
- archive SHA256:

```text
efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96
```

Linux x64:

- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`
- archive SHA256:

```text
b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405
```

Both smoke sidecars report `ethos 0.3.0`. Both inventory sidecars report
`draft_not_release_ready` and `publication: blocked`; those sidecars are evidence inputs for
decider review and are not themselves publication approvals.

## Requested Public Wording

If the decider accepts the exact artifacts above, the bounded GitHub Release wording may remain:

> Ethos v0.3.0 CLI artifacts for macOS arm64 and Linux x64 are requested for GitHub Release
> evaluation with caller-provided PDFium. Rust crates `ethos-doc-core`, `ethos-verify`, and
> `ethos-pdf` at `0.3.0`, plus the Python `ethos-pdf` wheel at `0.3.0`, are already live. npm
> alignment/publication, public `0.3.0` install wording, release/package tags, DocuShell
> integration, hosted surfaces, production positioning, Windows packaged artifacts, bundled
> project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public
> benchmark claims, and speed, footprint, parser-quality, table-quality, or production claims
> remain blocked.

Any broader public wording requires a separate decision record. The public install baseline remains
current published `0.2.0` Rust/Python and `0.2.1` npm, and README installation examples remain
unchanged.

## Retained Blockers

- GitHub Release artifact publication remains blocked until the decider explicitly accepts the
  exact artifact names, checksums, source binding, workflow evidence, and bounded public wording in
  this request.
- GitHub Release artifact upload remains blocked until an explicit approval decision, operator
  action, and closeout record pass.
- npm vendor refresh remains blocked.
- npm publication remains blocked.
- Release tag creation remains blocked.
- Package tag creation remains blocked.
- Public installation wording remains blocked.
- DocuShell integration remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

Upload remains blocked until explicit approval is recorded.

## Required Operator Checks Before Decision

Before acceptance, the operator should verify the downloaded workflow artifacts:

```sh
shasum -a 256 ethos-macos-arm64.tar.gz
cat ethos-macos-arm64.tar.gz.sha256
cat ethos-macos-arm64.inventory.json
cat ethos-macos-arm64.smoke.json
shasum -a 256 ethos-linux-x64.tar.gz
cat ethos-linux-x64.tar.gz.sha256
cat ethos-linux-x64.inventory.json
cat ethos-linux-x64.smoke.json
```

If any output changes artifact names, checksums, version output, inventory publication status,
PDFium posture, license and NOTICE inclusion, public install baseline, or requested public wording,
publication must stop until a refreshed evidence record and approval request pass.

## Validation Commands

```sh
python3 .github/scripts/test_v0_3_0_artifact_publication_approval_request.py
python3 .github/scripts/test_v0_3_0_draft_artifact_evidence.py
python3 .github/scripts/public_boundary_claims_gate.py
make v0-3-release-prep PYTHON=python3
python3 .github/scripts/check_release_boundary_paths.py
python3 .github/scripts/validation_record_integrity.py
git diff --check
```

## Result

The v0.3.0 artifact publication approval request is ready for decider review. Upload remains
blocked until explicit approval is recorded.
