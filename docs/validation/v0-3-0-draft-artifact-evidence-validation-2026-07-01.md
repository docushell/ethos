# v0.3.0 Draft Artifact Evidence Validation - 2026-07-01

Validated source HEAD before this record: `7287358`.

v0.3.0 draft CLI artifact evidence source commit:
`7287358475a96e827d536f0d2d250a1c2961ba84`.

v0.3.0 draft CLI artifact evidence source tree:
`84d7908f91f3bb2024acb6bad4c71b6c75d4f357`.

Status: **draft CLI artifact evidence recorded; publication and installable wording remain blocked**

This record captures a green v0.3.0 draft CLI artifact workflow-dispatch run on `main` after the
CLI artifact evidence prep and release workflow preflight fix landed. It records downloaded macOS
arm64 and Linux x64 draft artifact sidecars, archive checksums, archive inventories, and runtime
smoke outputs. It satisfies the two-platform draft CLI artifact evidence prerequisite for later
artifact-publication and npm-vendor decisions. It does not publish those artifacts, create a GitHub
Release, update npm vendor payloads, publish npm, create tags, change public installation wording,
or approve DocuShell integration.

## Workflow Run

Workflow:

```text
.github/workflows/release.yml
```

Run:

```text
https://github.com/docushell/ethos/actions/runs/28531102130
```

Observed run metadata:

- status: `completed`
- conclusion: `success`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `7287358475a96e827d536f0d2d250a1c2961ba84`
- created at: `2026-07-01T16:06:05Z`
- updated at: `2026-07-01T16:07:15Z`

Observed jobs:

- `preflight`: passed.
- `cli-draft-artifacts (macos-arm64, macos-14, tar.gz)`: passed.
- `cli-draft-artifacts (linux-x64, ubuntu-latest, tar.gz)`: passed.

Both artifact jobs passed build, draft artifact assembly, draft artifact runtime smoke, draft
artifact inventory validation, and artifact upload.

## Downloaded Artifact Set

The operator downloaded these workflow artifacts from run `28531102130`:

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
- SHA256: `efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96`
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
  "sha256": "efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96",
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
  "version_stdout": "ethos 0.3.0"
}
```

Linux x64:

- archive: `ethos-linux-x64.tar.gz`
- SHA256: `b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405`
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
  "sha256": "b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405",
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
  "version_stdout": "ethos 0.3.0"
}
```

## Boundary

This record does not approve GitHub Release artifact publication. This record does not approve npm
vendor refresh. This record does not approve npm publication. This record does not create or
approve release tags or package tags. This record does not approve public installation wording for
`0.3.0`. This record does not approve DocuShell integration.

The public install baseline remains current published `0.2.0` Rust/Python and `0.2.1` npm until
separate GitHub Release artifact publication, npm vendor refresh, npm publication, tag creation,
public wording, and closeout records pass.

## Retained Blockers

- GitHub Release artifact publication remains blocked.
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

## Verification Commands

```sh
git checkout main
git pull --ff-only origin main
GH_PROMPT_DISABLED=1 gh workflow run release.yml --repo docushell/ethos --ref main
GH_PROMPT_DISABLED=1 gh run watch 28531102130 --repo docushell/ethos --exit-status --interval 10
GH_PROMPT_DISABLED=1 gh run view 28531102130 --repo docushell/ethos --json url,status,conclusion,event,headBranch,headSha,createdAt,updatedAt,jobs
GH_PROMPT_DISABLED=1 gh run download 28531102130 --repo docushell/ethos --dir <artifact-download-dir>
python3 .github/scripts/validate_release_artifact_inventory.py <artifact-download-dir>/*/*.inventory.json
shasum -a 256 <artifact-download-dir>/*/*.tar.gz
tar -tzf <artifact-download-dir>/ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz
tar -tzf <artifact-download-dir>/ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz
python3 .github/scripts/test_v0_3_0_draft_artifact_evidence.py
make v0-3-release-prep PYTHON=python3
python3 .github/scripts/check_release_boundary_paths.py
python3 .github/scripts/validation_record_integrity.py
git diff --check
```

## Result

```text
v0.3.0 draft CLI artifact evidence recorded
macOS arm64 and Linux x64 draft artifacts smoke as ethos 0.3.0
public install baseline remains current published 0.2.0 Rust/Python and 0.2.1 npm
publication, npm vendor refresh, tags, install wording, and DocuShell integration remain blocked pending separate approvals and evidence
```
