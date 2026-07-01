# v0.3.0 CLI Artifact Evidence Prep Validation - 2026-07-01

Validated source HEAD before this record: `3ae36b9`.

v0.3.0 CLI artifact evidence prep source commit:
`3ae36b95f9fe7c1f74f58075eacbbaaa7c469bea`.

v0.3.0 CLI artifact evidence prep source tree:
`d9d6313cd28b647eba89e02b29adcba54349c190`.

Status: **CLI artifact evidence prep recorded; artifact publication remains blocked**

This record starts the v0.3.0 CLI/GitHub Release artifact evidence lane after the v0.3.0 Rust
crates.io and Python PyPI publication closeout. It aligns the draft CLI artifact workflow to the
current source version so a later workflow-dispatch run can produce macOS arm64 and Linux x64
draft artifact evidence for review.

No workflow run is recorded by this prep record. No artifact bytes, checksums, release assets, npm
vendor payloads, release tags, package tags, or public install wording are changed by this record.

## Workflow Prep

Workflow:

```text
.github/workflows/release.yml
```

The workflow now passes `--expected-version "ethos 0.3.0"` to
`.github/scripts/smoke_release_cli_artifact.py` for both draft artifact targets:

- `macos-arm64` on `macos-14`
- `linux-x64` on `ubuntu-latest`

The workflow remains a draft-artifact workflow. It runs public-surface posture checks, claims
gates, package-surface guards, and PDFium manual setup contract tests before building artifacts.
It uploads CI artifacts containing:

- `ethos-<target>.tar.gz`
- `ethos-<target>.tar.gz.sha256`
- `ethos-<target>.inventory.json`
- `ethos-<target>.smoke.json`

The workflow still does not create a GitHub Release, upload release assets, publish npm packages,
publish PyPI distributions, publish Rust crates, create tags, or approve launch wording.

## Required Later Evidence

The next record must capture the workflow run URL and run id. It must bind the run to the reviewed
source commit and record `status: completed` and `conclusion: success`.

The next record must capture macOS arm64 and Linux x64 archive SHA256 values, checksum sidecar
matches, inventory sidecars, smoke sidecars, and archive inventories. The smoke sidecars must show:

```json
{
  "version_stdout": "ethos 0.3.0",
  "missing_pdfium_exit_code": 12,
  "pdfium_policy": "caller-provided"
}
```

The next record must keep artifact publication, npm vendor refresh, npm publication, release tags,
package tags, public install wording, and DocuShell integration blocked unless separate approval
and closeout records explicitly open those boundaries.

## Operator Commands For Later Evidence

After this prep branch is reviewed and pushed, collect draft artifact evidence with:

```sh
git push origin dev/v0-3-cli-artifact-evidence-prep
GH_PROMPT_DISABLED=1 gh workflow run release.yml --repo docushell/ethos --ref dev/v0-3-cli-artifact-evidence-prep
GH_PROMPT_DISABLED=1 gh run watch <run-id> --repo docushell/ethos --exit-status --interval 10
GH_PROMPT_DISABLED=1 gh run view <run-id> --repo docushell/ethos --json url,status,conclusion,event,headBranch,headSha,createdAt,updatedAt,jobs
GH_PROMPT_DISABLED=1 gh run download <run-id> --repo docushell/ethos --dir <artifact-download-dir>
python3 .github/scripts/validate_release_artifact_inventory.py <artifact-download-dir>/*/*.inventory.json
shasum -a 256 <artifact-download-dir>/*/*.tar.gz
tar -tzf <artifact-download-dir>/ethos-cli-draft-linux-x64/ethos-linux-x64.tar.gz
tar -tzf <artifact-download-dir>/ethos-cli-draft-macos-arm64/ethos-macos-arm64.tar.gz
```

Do not upload GitHub Release assets from this prep record. Use the downloaded evidence to create a
separate v0.3.0 draft artifact evidence record first.

## Boundary

- This record does not approve GitHub Release artifact publication.
- This record does not approve GitHub Release creation.
- This record does not approve release tag creation.
- This record does not approve package tag creation.
- This record does not approve npm vendor refresh.
- This record does not approve npm publication.
- This record does not approve public installation wording for `0.3.0`.
- This record does not approve DocuShell integration.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

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

## Verification Commands

```sh
python3 .github/scripts/test_v0_3_0_cli_artifact_evidence_prep.py
python3 .github/scripts/test_release_artifact_workflow_prep.py
python3 .github/scripts/test_v0_3_0_version_activation.py
python3 .github/scripts/test_v0_2_0_package_build_evidence.py
make v0-3-release-prep PYTHON=python3
python3 .github/scripts/check_release_boundary_paths.py
python3 .github/scripts/validation_record_integrity.py
git diff --check
```

## Result

```text
v0.3.0 CLI artifact evidence prep: PASS
release.yml draft artifact smoke expectation: ethos 0.3.0
workflow run evidence, artifact checksums, GitHub Release upload, npm alignment, tags, install wording, and DocuShell integration: BLOCKED
```
