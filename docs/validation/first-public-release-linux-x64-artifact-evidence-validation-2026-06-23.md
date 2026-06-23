# First Public Release Linux x64 Artifact Evidence Validation - 2026-06-23

- Validated source HEAD before this record: `38a92f3`

Linux-artifact evidence source commit: `38a92f390c9578194467eceaacdd297a132d49c9`

Linux-artifact evidence source tree: `66a8d69a9e94c891621a77cb3b4719a9a7ffd8cd`

Status: **Linux x64 artifact evidence recorded; publication awaits final decider**

This record captures Linux x64 CLI artifact evidence from the green release workflow run. It does
not publish the artifact, does not change public launch wording, and does not approve npm, Windows
packaged artifacts, hosted surfaces, production positioning, bundled project-maintained PDFium
builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or public benchmark claims.

## Source and Workflow Binding

Workflow:

```text
.github/workflows/release.yml
```

Run:

```text
https://github.com/docushell/ethos/actions/runs/28004938177
```

Branch:

```text
codex/linux-x64-first-public-release
```

Observed workflow status: **pass**.

Observed Linux job: `cli-draft-artifacts (linux-x64, ubuntu-latest, tar.gz)` passed.

## macOS Published Artifact Reconciliation

The operator verified the already-published macOS arm64 GitHub Release artifact sidecars from
`v0.1.0`.

Published macOS artifact: `ethos-macos-arm64.tar.gz`

Published macOS SHA256:

```text
9cb66dac20f93c55f574357dd0494e0cad711e1e5969cdfb29ae4c64ddf7c95d
```

The recomputed archive SHA256, `.sha256` sidecar, and inventory `sha256` all matched. The inventory
validated with:

```sh
python3 .github/scripts/validate_release_artifact_inventory.py /tmp/ethos-v0.1.0-macos/ethos-macos-arm64.inventory.json
```

## Linux x64 CLI Artifact Evidence

Artifact bundle downloaded from workflow artifact `ethos-cli-draft-linux-x64`.

Artifact: `ethos-linux-x64.tar.gz`

Checksum sidecar: `ethos-linux-x64.tar.gz.sha256`

Inventory sidecar: `ethos-linux-x64.inventory.json`

Smoke sidecar: `ethos-linux-x64.smoke.json`

SHA256:

```text
59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2
```

Checksum sidecar:

```text
59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2  target/release-artifacts/ethos-linux-x64.tar.gz
```

Inventory:

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
  "sha256": "59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2",
  "status": "draft_not_release_ready",
  "target": "linux-x64"
}
```

Smoke evidence:

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
  "missing_pdfium_message": "PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path",
  "required_files": [
    "ethos",
    "LICENSE",
    "NOTICE",
    "pdfium-manual-setup.md"
  ],
  "schema": "ethos.release_artifact_smoke.v1",
  "target": "linux-x64",
  "version_stdout": "ethos 0.1.0"
}
```

Archive contents:

```text
ethos-linux-x64/
ethos-linux-x64/LICENSE
ethos-linux-x64/ethos
ethos-linux-x64/NOTICE
ethos-linux-x64/pdfium-manual-setup.md
```

Validation command:

```sh
python3 .github/scripts/validate_release_artifact_inventory.py /tmp/ethos-release-run-28004938177/ethos-linux-x64.inventory.json
```

Result: **pass**.

## Retained Blockers

- Linux x64 CLI artifact publication remains blocked until the final Linux x64 decider record
  approves attaching the evidenced assets to `v0.1.0`.
- npm publication remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows x64 packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

Linux x64 artifact evidence is sufficient to proceed to a final Linux x64 decider record for the
existing GitHub Release `v0.1.0`.
