# Patch 0.1.2 Draft Artifact Evidence Validation - 2026-06-24

Validated source HEAD before this record: `2cb092b`.

Patch 0.1.2 draft artifact evidence source commit:
`2cb092b403eefe937e30c902fcebf7bb5754d590`.

Patch 0.1.2 draft artifact evidence source tree:
`9e23207526591813c4aaf311ec8788b94e6a95ab`.

Status: **patch 0.1.2 draft CLI artifact evidence recorded; publication remains blocked**

This record captures a green draft CLI artifact workflow run for patch `0.1.2` after the
artifact/package evidence prep lane landed on `main`. It records downloaded macOS arm64 and Linux
x64 draft artifact sidecars and checksums. It does not publish those artifacts, create a GitHub
Release, update npm vendor payloads, publish registries, or change public installation wording.

## Workflow Run

Workflow:

```text
.github/workflows/release.yml
```

Run:

```text
https://github.com/docushell/ethos/actions/runs/28102259869
```

Observed run metadata:

- status: `completed`
- conclusion: `success`
- event: `workflow_dispatch`
- branch: `main`
- head SHA: `2cb092b403eefe937e30c902fcebf7bb5754d590`
- created at: `2026-06-24T13:32:01Z`
- updated at: `2026-06-24T13:33:06Z`

Observed jobs:

- `preflight`: passed.
- `cli-draft-artifacts (macos-arm64, macos-14, tar.gz)`: passed.
- `cli-draft-artifacts (linux-x64, ubuntu-latest, tar.gz)`: passed.

Both artifact jobs passed build, draft artifact assembly, release artifact runtime smoke, draft
artifact inventory validation, and artifact upload.

## Downloaded Artifact Set

The operator downloaded these workflow artifacts from run `28102259869`:

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
- SHA256: `7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c`
- checksum sidecar matched the recomputed archive SHA256
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
  "sha256": "7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c",
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
  "schema": "ethos.release_artifact_smoke.v1",
  "target": "macos-arm64",
  "version_stdout": "ethos 0.1.2"
}
```

Linux x64:

- archive: `ethos-linux-x64.tar.gz`
- SHA256: `4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456`
- checksum sidecar matched the recomputed archive SHA256
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
  "sha256": "4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456",
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
  "schema": "ethos.release_artifact_smoke.v1",
  "target": "linux-x64",
  "version_stdout": "ethos 0.1.2"
}
```

The smoke sidecars also recorded the expected missing-PDFium guidance text for caller-provided
`ETHOS_PDFIUM_LIBRARY_PATH` setup.

## Boundary

This record does not approve GitHub Release artifact publication. This record does not approve
registry publication. This record does not approve PyPI upload. This record does not approve npm
publication. This record does not refresh the checked-in npm vendor payload. This record does not
approve public installation wording for `0.1.2`.

The public install baseline remains `0.1.1` until separate registry/GitHub Release publication
decisions, operator actions, npm vendor refresh, and public wording closeout records pass.

## Retained Blockers

- GitHub Release artifact publication remains blocked.
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

## Verification Commands

```sh
GH_PROMPT_DISABLED=1 gh workflow run release.yml --repo docushell/ethos --ref main
GH_PROMPT_DISABLED=1 gh run watch 28102259869 --repo docushell/ethos --exit-status --interval 10
GH_PROMPT_DISABLED=1 gh run download 28102259869 --repo docushell/ethos --dir <artifact-download-dir>
python3 .github/scripts/validate_release_artifact_inventory.py <artifact-download-dir>/*/*.inventory.json
shasum -a 256 <artifact-download-dir>/*/*.tar.gz
python3 .github/scripts/test_patch_0_1_2_draft_artifact_evidence.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 draft CLI artifact evidence recorded
macOS arm64 and Linux x64 draft artifacts smoke as ethos 0.1.2
public install baseline remains 0.1.1
publication and npm vendor refresh remain blocked pending separate approval and operator evidence
```
