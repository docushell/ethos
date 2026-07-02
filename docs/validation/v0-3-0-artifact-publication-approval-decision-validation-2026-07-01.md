# v0.3.0 Artifact Publication Approval Decision Validation - 2026-07-01

Validated source HEAD before this record: `a20b42a`.

v0.3.0 artifact publication approval decision source commit:
`a20b42a7927052f727fcaaa585a7a050aec02abe`.

v0.3.0 artifact publication approval decision source tree:
`ed4f624ad29a8c8c457b045b2519b5aadb2c4f40`.

Status: **v0.3.0 artifact publication approval decision recorded; operator upload remains
pending**

This record accepts the exact v0.3.0 GitHub Release artifact publication request after decider
approval. It approves only later attaching the exact evidenced macOS arm64 and Linux x64 CLI
artifact assets below to GitHub Release target `v0.3.0` for release evaluation. It does not upload
artifacts, refresh npm vendor binaries, publish npm, change public installation wording, change
PDFium posture, approve DocuShell integration, approve hosted surfaces, approve production
positioning, approve Windows packaged artifacts, approve bundled project-maintained PDFium builds,
approve `ethos-doc`, approve `ethos-rag`, approve public benchmark reports or claims, or approve
package tags.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.3.0 GitHub Release artifact publication
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/v0-3-0-artifact-publication-approval-request-validation-2026-07-01.md`
- Artifact evidence record:
  `docs/validation/v0-3-0-draft-artifact-evidence-validation-2026-07-01.md`
- Release workflow run: `https://github.com/docushell/ethos/actions/runs/28531102130`

## Exact Decision Fields

- Decision: accept the exact v0.3.0 artifact publication request.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-07-01.
- Exact GitHub Release target accepted by this decision: `v0.3.0`.
- Exact request source commit accepted by this decision:
  `d6496e82e613e653edc197db4cf4153271d131dc`.
- Exact request source tree accepted by this decision:
  `2594c63071c512f2c61e78b223a74406440a8516`.
- Exact artifact source commit accepted by this decision:
  `7287358475a96e827d536f0d2d250a1c2961ba84`.
- Exact artifact source tree accepted by this decision:
  `84d7908f91f3bb2024acb6bad4c71b6c75d4f357`.
- Exact workflow run accepted by this decision:
  `https://github.com/docushell/ethos/actions/runs/28531102130`.
- Exact workflow head SHA accepted by this decision:
  `7287358475a96e827d536f0d2d250a1c2961ba84`.

macOS arm64 assets accepted by this decision:

- `ethos-macos-arm64.tar.gz`
- `ethos-macos-arm64.tar.gz.sha256`
- `ethos-macos-arm64.inventory.json`
- `ethos-macos-arm64.smoke.json`
- archive SHA256:

```text
efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96
```

Linux x64 assets accepted by this decision:

- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`
- archive SHA256:

```text
b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405
```

Exact CLI smoke accepted by this decision: `ethos 0.3.0` for both accepted platform artifacts.

Exact PDFium boundary accepted by this decision: caller-provided PDFium only through
`ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build is approved.

## Approved Operator Action

After this decision record is merged and the validation commands below pass on the merged source,
an operator may attach only the exact accepted asset names above to GitHub Release target `v0.3.0`.
If the target does not already exist, the operator may create or use only that exact target for the
accepted assets and bounded wording in this record. The operator must not create or use any other
release target.

This decision does not itself upload artifacts. Publication remains an explicit later operator
action.

## Approved Public Wording

After the exact assets above are attached to GitHub Release target `v0.3.0`, the bounded public
release wording may remain:

> Ethos v0.3.0 CLI artifacts for macOS arm64 and Linux x64 are requested for GitHub Release
> evaluation with caller-provided PDFium. Rust crates `ethos-doc-core`, `ethos-verify`, and
> `ethos-pdf` at `0.3.0`, plus the Python `ethos-pdf` wheel at `0.3.0`, are already live. npm
> alignment/publication, public `0.3.0` install wording, release/package tags, DocuShell
> integration, hosted surfaces, production positioning, Windows packaged artifacts, bundled
> project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public
> benchmark claims, and speed, footprint, parser-quality, table-quality, or production claims
> remain blocked.

Any broader public wording requires a separate decider record. The public install baseline remains
current published `0.2.0` Rust/Python and `0.2.1` npm, and README installation examples remain
unchanged.

## Required Operator Pre-Upload Checks

Before uploading, the operator must verify the downloaded workflow artifacts:

```sh
shasum -a 256 ethos-macos-arm64.tar.gz
cat ethos-macos-arm64.tar.gz.sha256
cat ethos-macos-arm64.inventory.json
cat ethos-macos-arm64.smoke.json
shasum -a 256 ethos-linux-x64.tar.gz
cat ethos-linux-x64.tar.gz.sha256
cat ethos-linux-x64.inventory.json
cat ethos-linux-x64.smoke.json
python3 .github/scripts/test_v0_3_0_artifact_publication_approval_decision.py
make v0-3-release-prep PYTHON=python3
git diff --check
```

The operator must stop if artifact names, checksums, version output, inventory publication status,
PDFium posture, license and NOTICE inclusion, public install baseline, or approved public wording
differ from this decision record.

## Retained Blockers

- `packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed until after the approved
  GitHub Release assets are attached and publication closeout evidence is recorded.
- npm vendor refresh remains blocked.
- npm publication remains blocked.
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

## Evidence Bound To This Decision

- Decider decision supplied: Approved.
- Exact approval supplied by operator:
  `Approve exact v0.3.0 GitHub Release artifact publication request for the listed macOS arm64
  and Linux x64 CLI artifacts, checksums, source binding, workflow evidence, and bounded public
  wording.`
- `python3 .github/scripts/test_v0_3_0_artifact_publication_approval_request.py` passed on
  merged `main`.
- `python3 .github/scripts/test_v0_3_0_draft_artifact_evidence.py` passed on merged `main`.
- `make v0-3-release-prep PYTHON=python3` passed on merged `main`.

## Non-Actions

- This decision record does not upload GitHub Release assets.
- This decision record does not refresh npm vendor binaries.
- This decision record does not publish npm.
- This decision record does not change public installation wording.
- This decision record does not change PDFium posture.
- This decision record does not approve DocuShell integration.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.
- This decision record does not approve package tags.

## Result

The exact v0.3.0 GitHub Release artifact publication decision is accepted. Actual asset upload
remains a separate operator action requiring the exact bounded assets approved here, final
pre-upload checks, and post-upload closeout evidence.
