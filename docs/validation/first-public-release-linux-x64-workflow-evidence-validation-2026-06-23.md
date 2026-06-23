# First Public Release Linux x64 Workflow Evidence Validation - 2026-06-23

- Validated source HEAD before this record: `5be8104`

Workflow-evidence source commit: `5be8104223bcff633ac58e24280b40309029807a`

Workflow-evidence source tree: `01bf96c5abd223acc269c4470d9acdb7cdf1fe7a`

Status: **Linux x64 release workflow passed; artifact byte evidence still blocked**

This record captures the first Linux x64 draft artifact workflow run after adding release artifact
runtime smoke evidence. It does not approve Linux x64 publication, does not approve uploading any
new GitHub Release asset, and does not change the approved public launch wording.

## Workflow Run

Workflow:

```text
.github/workflows/release.yml
```

Run:

```text
https://github.com/docushell/ethos/actions/runs/28004938177
```

Ref:

```text
codex/linux-x64-first-public-release
```

Observed result from `gh run watch 28004938177 --exit-status --interval 10`: **pass**.

Observed jobs:

- `preflight`: passed.
- `cli-draft-artifacts (macos-arm64, macos-14, tar.gz)`: passed.
- `cli-draft-artifacts (linux-x64, ubuntu-latest, tar.gz)`: passed.

The Linux x64 job passed these workflow steps:

- checkout;
- `rustup show`;
- `cargo build --locked --release -p ethos-cli`;
- draft artifact assembly;
- release artifact runtime smoke;
- draft artifact inventory validation;
- artifact upload.

## Artifact Retrieval Blocker

The local environment attempted to download the completed workflow artifacts with:

```sh
GH_PROMPT_DISABLED=1 gh run download 28004938177 --dir <artifact-download-dir>
```

Result: **blocked by GitHub API timeout**.

The local environment also attempted to fetch the Linux job log with:

```sh
GH_PROMPT_DISABLED=1 gh run view 28004938177 --job 82884823792 --log
```

Result: **blocked by GitHub API timeout**.

Because the Linux artifact bytes and sidecars were not retrievable in this environment, this record
does not name a Linux x64 SHA256 and does not approve publication.

## Required Before Linux x64 Publication

Before attaching Linux x64 assets to the existing `v0.1.0` GitHub Release, retrieve the uploaded
workflow artifact `ethos-cli-draft-linux-x64` from run `28004938177` or a later equivalent green
run on this branch, then record:

- `ethos-linux-x64.tar.gz`;
- `ethos-linux-x64.tar.gz.sha256`;
- `ethos-linux-x64.inventory.json`;
- `ethos-linux-x64.smoke.json`;
- recomputed archive SHA256;
- inventory `sha256`;
- smoke evidence showing `ethos 0.1.0`, expected help command groups, and missing-PDFium exit
  code `12`;
- operator-verified current macOS arm64 published checksum sidecars from `v0.1.0`.

If any artifact, checksum, inventory, smoke sidecar, version output, or missing-PDFium behavior
differs from the approved evaluation boundary, publication must stop until a new evidence record
and decider record pass.

## Retained Blockers

- Linux x64 CLI artifact publication remains blocked until artifact byte evidence and checksum
  sidecars are recorded.
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

The Linux x64 workflow path is green, but Ethos has not yet reached complete first public release
artifact coverage. The next release step is artifact retrieval from the green workflow run, followed
by a Linux x64 artifact evidence record and final decider update.
