# Patch 0.1.2 Artifact Publication Approval Request Validation - 2026-06-24

## Purpose

Record the exact patch `0.1.2` GitHub Release artifact publication approval request for decider
review. This record does not publish artifacts, create a GitHub Release, refresh npm vendor
binaries, publish npm, publish registries, change public installation wording, change PDFium
posture, or open any new public surface.

Validated source HEAD before this record: `09750a8`.
Patch 0.1.2 artifact publication approval request source commit:
`09750a81cb72cbc91f9e0c35e52ae2711c2ee7b7`.
Patch 0.1.2 artifact publication approval request source tree:
`7a7eeb7b3b258facd4f171ce00ed4df5533259b1`.

## Evidence Inputs

- Release workflow: `.github/workflows/release.yml`
- Workflow run: `https://github.com/docushell/ethos/actions/runs/28102259869`
- Evidence record:
  `docs/validation/patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md`
- Run status: `completed`
- Run conclusion: `success`
- Run event: `workflow_dispatch`
- Run branch: `main`
- Run head SHA: `2cb092b403eefe937e30c902fcebf7bb5754d590`

## Requested Artifact Evaluation Surface

The decider is asked to accept or reject only attaching these exact draft CLI artifacts and sidecars
to GitHub Release `v0.1.2` for public beta evaluation:

macOS arm64:

- `ethos-macos-arm64.tar.gz`
- `ethos-macos-arm64.tar.gz.sha256`
- `ethos-macos-arm64.inventory.json`
- `ethos-macos-arm64.smoke.json`
- archive SHA256:

```text
7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c
```

Linux x64:

- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`
- archive SHA256:

```text
4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456
```

Both smoke sidecars report `ethos 0.1.2`. Both inventory sidecars report
`draft_not_release_ready` and `publication: blocked`; those sidecars are evidence inputs for
decider review and are not themselves publication approvals.

## Requested Public Wording

If the decider accepts the exact artifacts above, the bounded GitHub Release wording may remain:

> Ethos patch `0.1.2` CLI artifacts for macOS arm64 and Linux x64 are requested for public beta
> evaluation with caller-provided PDFium. Rust crates, the Python wheel, npm package install
> instructions, and public README installation examples remain on the published `0.1.1` baseline
> until separate registry, npm vendor refresh, and public wording closeout records pass. Hosted
> surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
> builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, and speed,
> footprint, parser-quality, table-quality, or production claims remain blocked.

Any broader public wording requires a separate decision record. The public install baseline remains
`0.1.1`, and README installation examples remain unchanged.

## Retained Blockers

- GitHub Release artifact publication remains blocked until the decider explicitly accepts the
  exact artifact names, checksums, source binding, and public wording in this request.
- Registry publication remains blocked.
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

Publication remains blocked until explicit approval is recorded.

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
python3 .github/scripts/test_patch_0_1_2_artifact_publication_approval_request.py
python3 .github/scripts/test_patch_0_1_2_draft_artifact_evidence.py
python3 .github/scripts/public_boundary_claims_gate.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

The patch `0.1.2` artifact publication approval request is ready for decider review. Publication
remains blocked until explicit approval is recorded.
