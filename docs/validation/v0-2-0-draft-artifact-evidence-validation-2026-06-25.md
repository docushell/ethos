# v0.2.0 Draft Artifact Evidence Validation - 2026-06-25

Validated source HEAD before this record: `36955ca`.

v0.2.0 draft artifact evidence source commit:
`36955cac69dc4eed624feb22b1a8c5e8a811d3bd`.

v0.2.0 draft artifact evidence source tree:
`7ca47e76dfa2d23d40768dbcb88e2b97fba619b2`.

Status: **draft CLI artifact evidence recorded; publication and installable wording remain blocked**

This record captures a green v0.2.0 draft CLI artifact workflow run on the
`dev/v0-2-approval-packet` release-candidate branch. It records downloaded macOS arm64 and Linux
x64 draft artifact sidecars, archive checksums, and runtime smoke outputs. It satisfies the
two-platform draft CLI artifact evidence prerequisite for later artifact-publication and npm-vendor
decisions. It does not publish those artifacts, create a GitHub Release, update npm vendor
payloads, publish registries, create tags, or change public installation wording.

## Workflow Run

Workflow:

```text
.github/workflows/release.yml
```

Run:

```text
https://github.com/docushell/ethos/actions/runs/28175143857
```

Observed run metadata:

- status: `completed`
- conclusion: `success`
- event: `workflow_dispatch`
- branch: `dev/v0-2-approval-packet`
- head SHA: `36955cac69dc4eed624feb22b1a8c5e8a811d3bd`
- created at: `2026-06-25T13:52:38Z`
- updated at: `2026-06-25T13:53:52Z`

Observed jobs:

- `preflight`: passed.
- `cli-draft-artifacts (macos-arm64, macos-14, tar.gz)`: passed.
- `cli-draft-artifacts (linux-x64, ubuntu-latest, tar.gz)`: passed.

Both artifact jobs passed build, draft artifact assembly, draft artifact runtime smoke, draft
artifact inventory validation, and artifact upload.

## Downloaded Artifact Set

The operator downloaded these workflow artifacts from run `28175143857`:

- `ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz`
- `ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz.sha256`
- `ethos-cli-draft-macos-arm64/ethos-macos-arm64.inventory.json`
- `ethos-cli-draft-macos-arm64/ethos-macos-arm64.smoke.json`
- `ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz`
- `ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz.sha256`
- `ethos-cli-draft-linux-x64/ethos-linux-x64.inventory.json`
- `ethos-cli-draft-linux-x64/ethos-linux-x64.smoke.json`

## Artifact Evidence

macOS arm64:

- archive: `ethos-macos-arm64.tar.gz`
- SHA256: `c588ee77bbaf99a7d933673e6cd9db190f5992e47d40955def803435a9f9fc5a`
- checksum sidecar matched the recomputed archive SHA256
- archive members: `ethos-macos-arm64/`, `LICENSE`, `NOTICE`, `ethos`, `pdfium-manual-setup.md`
- inventory:

```json
{
  "artifact": "ethos-macos-arm64.tar.gz",
  "artifact_class": "github-release-binary",
  "pdfium_policy": "caller-provided",
  "publication": "blocked",
  "required_notices": [
    "LICENSE",
    "NOTICE",
    "docs/pdfium-manual-setup.md"
  ],
  "schema": "ethos.release_artifact_inventory.v1",
  "sha256": "c588ee77bbaf99a7d933673e6cd9db190f5992e47d40955def803435a9f9fc5a",
  "status": "draft_not_release_ready",
  "target": "macos-arm64"
}
```

- smoke:

```json
{
  "artifact_dir": "ethos-macos-arm64",
  "help_command_groups": [
    "doc",
    "rag",
    "security",
    "verify",
    "fingerprint"
  ],
  "missing_pdfium_exit_code": 12,
  "missing_pdfium_message": "PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path. Run ethos doctor for setup diagnostics, run ethos doctor --require-pdfium after setting it, and see docs/pdfium-manual-setup.md.",
  "required_files": [
    "ethos",
    "LICENSE",
    "NOTICE",
    "pdfium-manual-setup.md"
  ],
  "schema": "ethos.release_artifact_smoke.v1",
  "target": "macos-arm64",
  "version_stdout": "ethos 0.2.0"
}
```

Linux x64:

- archive: `ethos-linux-x64.tar.gz`
- SHA256: `00137b20ca2c2a2d2089df1d135920b021b0905d779b1347d134e8a2fb7bfa23`
- checksum sidecar matched the recomputed archive SHA256
- archive members: `ethos-linux-x64/`, `LICENSE`, `ethos`, `NOTICE`, `pdfium-manual-setup.md`
- inventory:

```json
{
  "artifact": "ethos-linux-x64.tar.gz",
  "artifact_class": "github-release-binary",
  "pdfium_policy": "caller-provided",
  "publication": "blocked",
  "required_notices": [
    "LICENSE",
    "NOTICE",
    "docs/pdfium-manual-setup.md"
  ],
  "schema": "ethos.release_artifact_inventory.v1",
  "sha256": "00137b20ca2c2a2d2089df1d135920b021b0905d779b1347d134e8a2fb7bfa23",
  "status": "draft_not_release_ready",
  "target": "linux-x64"
}
```

- smoke:

```json
{
  "artifact_dir": "ethos-linux-x64",
  "help_command_groups": [
    "doc",
    "rag",
    "security",
    "verify",
    "fingerprint"
  ],
  "missing_pdfium_exit_code": 12,
  "missing_pdfium_message": "PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path. Run ethos doctor for setup diagnostics, run ethos doctor --require-pdfium after setting it, and see docs/pdfium-manual-setup.md.",
  "required_files": [
    "ethos",
    "LICENSE",
    "NOTICE",
    "pdfium-manual-setup.md"
  ],
  "schema": "ethos.release_artifact_smoke.v1",
  "target": "linux-x64",
  "version_stdout": "ethos 0.2.0"
}
```

## Boundary

This record does not approve GitHub Release artifact publication. This record does not approve
registry publication. This record does not approve PyPI upload. This record does not approve npm
publication. This record does not approve npm vendor refresh. This record does not create or
approve release tags or package tags. This record does not approve public installation wording for
`0.2.0`.

The public install baseline remains `0.1.2` until separate registry/GitHub Release publication
decisions, operator actions, npm vendor refresh, and public wording closeout records pass.

## Retained Blockers

- GitHub Release artifact publication remains blocked.
- Registry publication remains blocked.
- PyPI upload remains blocked.
- npm vendor refresh remains blocked pending a separate refresh record.
- npm publication remains blocked.
- Release tag creation remains blocked.
- Package tag creation remains blocked.
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

## Verification Commands

```sh
make v0-2-release-prep PYTHON=python3
git push origin dev/v0-2-approval-packet
GH_PROMPT_DISABLED=1 gh workflow run release.yml --repo docushell/ethos --ref dev/v0-2-approval-packet
GH_PROMPT_DISABLED=1 gh run watch 28175143857 --repo docushell/ethos --exit-status --interval 10
GH_PROMPT_DISABLED=1 gh run view 28175143857 --repo docushell/ethos --json url,status,conclusion,event,headBranch,headSha,createdAt,updatedAt,jobs
GH_PROMPT_DISABLED=1 gh run download 28175143857 --repo docushell/ethos --dir <artifact-download-dir>
python3 .github/scripts/validate_release_artifact_inventory.py <artifact-download-dir>/*/*.inventory.json
shasum -a 256 <artifact-download-dir>/*/*.tar.gz
tar -tzf <artifact-download-dir>/ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz
tar -tzf <artifact-download-dir>/ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz
python3 .github/scripts/test_v0_2_0_draft_artifact_evidence.py
make v0-2-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.2.0 draft CLI artifact evidence recorded
macOS arm64 and Linux x64 draft artifacts smoke as ethos 0.2.0
public install baseline remains 0.1.2
publication, npm vendor refresh, tags, and installable wording remain blocked pending separate approvals and evidence
```
