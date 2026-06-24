# Patch 0.1.2 Artifact Publication Approval Decision Validation - 2026-06-24

Validated source HEAD before this record: `94c2ea4`.

Patch 0.1.2 artifact publication approval decision source commit:
`94c2ea490883a042ee026c9c3565e92121f16c3f`.

Patch 0.1.2 artifact publication approval decision source tree:
`6016ad317aae4efe01eadcd1d643f9c2f0be2ee5`.

Status: **patch 0.1.2 artifact publication approval decision recorded; operator upload remains pending**

This record accepts the exact patch `0.1.2` GitHub Release artifact publication request after
decider approval. It approves only attaching the exact evidenced macOS arm64 and Linux x64 CLI
artifact assets below to GitHub Release tag `v0.1.2` for public beta evaluation. It does not upload
artifacts, publish registries, refresh npm vendor binaries, publish npm, change public installation
wording, change PDFium posture, approve hosted surfaces, approve production positioning, approve
Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`,
approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: patch `0.1.2` GitHub Release artifact publication
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/patch-0-1-2-artifact-publication-approval-request-validation-2026-06-24.md`
- Artifact evidence record:
  `docs/validation/patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md`
- Release workflow run: `https://github.com/docushell/ethos/actions/runs/28102259869`

## Exact Decision Fields

- Decision: accept the exact patch `0.1.2` artifact publication request.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-24.
- Exact GitHub Release tag accepted by this decision: `v0.1.2`.
- Exact artifact source commit accepted by this decision:
  `09750a81cb72cbc91f9e0c35e52ae2711c2ee7b7`.
- Exact artifact source tree accepted by this decision:
  `7a7eeb7b3b258facd4f171ce00ed4df5533259b1`.
- Exact workflow run accepted by this decision:
  `https://github.com/docushell/ethos/actions/runs/28102259869`.
- Exact workflow head SHA accepted by this decision:
  `2cb092b403eefe937e30c902fcebf7bb5754d590`.

macOS arm64 assets accepted by this decision:

- `ethos-macos-arm64.tar.gz`
- `ethos-macos-arm64.tar.gz.sha256`
- `ethos-macos-arm64.inventory.json`
- `ethos-macos-arm64.smoke.json`
- archive SHA256:

```text
7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c
```

Linux x64 assets accepted by this decision:

- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`
- archive SHA256:

```text
4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456
```

Exact CLI smoke accepted by this decision: `ethos 0.1.2` for both accepted platform artifacts.

Exact PDFium boundary accepted by this decision: caller-provided PDFium only through
`ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or project-maintained PDFium build is approved.

## Approved Operator Action

After this decision record is merged and the validation commands below pass on the merged source,
an operator may attach only the exact accepted asset names above to GitHub Release tag `v0.1.2`.

This decision does not itself upload artifacts. Publication remains an explicit later operator
action.

## Approved Public Wording

After the exact assets above are attached to GitHub Release tag `v0.1.2`, the bounded public
release wording may remain:

> Ethos patch `0.1.2` CLI artifacts for macOS arm64 and Linux x64 are requested for public beta
> evaluation with caller-provided PDFium. Rust crates, the Python wheel, npm package install
> instructions, and public README installation examples remain on the published `0.1.1` baseline
> until separate registry, npm vendor refresh, and public wording closeout records pass. Hosted
> surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
> builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, and speed,
> footprint, parser-quality, table-quality, or production claims remain blocked.

Any broader public wording requires a separate decider record. The public install baseline remains
`0.1.1`, and README installation examples remain unchanged.

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
python3 .github/scripts/test_patch_0_1_2_artifact_publication_approval_decision.py
make release-candidate-prep PYTHON=python3
git diff --check
```

The operator must stop if artifact names, checksums, version output, inventory publication status,
PDFium posture, license and NOTICE inclusion, public install baseline, or approved public wording
differ from this decision record.

## Retained Blockers

- `packages/npm/ethos-pdf/vendor/manifest.json` must not be refreshed until after the approved
  GitHub Release assets are attached and publication closeout evidence is recorded.
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

## Evidence Bound To This Decision

- Decider decision supplied: Approved.
- Exact approval supplied by operator:
  `Approve exact patch 0.1.2 GitHub Release artifact publication request for the listed macOS arm64
  and Linux x64 CLI artifacts, checksums, source binding, and bounded public wording.`
- `python3 .github/scripts/test_patch_0_1_2_artifact_publication_approval_request.py` passed on
  merged `main`.
- `python3 .github/scripts/test_release_candidate_prep.py` passed on merged `main`.
- `make light-check PYTHON=python3` passed on merged `main`.
- `make release-candidate-prep PYTHON=python3` passed on merged `main`.

## Non-Actions

- This decision record does not upload GitHub Release assets.
- This decision record does not publish registries.
- This decision record does not refresh npm vendor binaries.
- This decision record does not publish npm.
- This decision record does not change public installation wording.
- This decision record does not change PDFium posture.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Result

The exact patch `0.1.2` GitHub Release artifact publication decision is accepted. Actual asset
upload remains a separate operator action requiring the exact bounded assets approved here, final
pre-upload checks, and post-upload closeout evidence.
