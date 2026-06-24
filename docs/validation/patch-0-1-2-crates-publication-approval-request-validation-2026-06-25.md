# Patch 0.1.2 crates.io Publication Approval Request Validation - 2026-06-25

Validated source HEAD before this record: `3bc3564`.

Patch 0.1.2 crates publication approval request source commit: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`.

Patch 0.1.2 crates publication approval request source tree: `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`.

Status: **patch 0.1.2 crates.io publication approval request recorded; cargo publish remains blocked**

This record requests decider review for publishing exactly the patch `0.1.2` Ethos Rust library
crate set to crates.io. It does not approve or perform `cargo publish`, create package tags, change
Rust crate public installation wording, approve PyPI upload, approve hosted surfaces, approve
production positioning, approve Windows packaged artifacts, approve bundled project-maintained
PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or
claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Rust crates publication
- Package source commit: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`
- Package source tree: `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`
- Candidate crates:
  - `ethos-doc-core = 0.1.2`
  - `ethos-verify = 0.1.2`
  - `ethos-pdf = 0.1.2`
- Excluded workspace packages:
  - `ethos-cli`
  - `ethos-layout`
  - `ethos-tables`
  - `ethos-grounding-opendataloader-json`
  - reserved `ethos-doc`
  - reserved `ethos-rag`

## Exact Request Fields

- Decision requested: approve exact patch `0.1.2` crates.io publication preparation inputs for
  later operator execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-06-25.
- Exact candidate crate list requested: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` only.
- Exact package version map requested: `ethos-doc-core = 0.1.2`, `ethos-verify = 0.1.2`, and
  `ethos-pdf = 0.1.2`.
- Exact package tag name set requested: `ethos-package-ethos-doc-core-0.1.2`,
  `ethos-package-ethos-verify-0.1.2`, and `ethos-package-ethos-pdf-0.1.2`.
- Exact package tag source commit requested: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`.
- Exact package tag source tree requested: `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`.
- Exact candidate package artifacts requested:
  - `ethos-doc-core-0.1.2.crate`
    - SHA256: `471956cac567f2d328ab2538291462a0bf57e082ef40dd86d877ffaa363bb632`
  - `ethos-verify-0.1.2.crate`
    - SHA256: `cc4356aa24b304d2f18187d5c3a0c02f847031c1d74e2f6a902a742711d65bf4`
  - `ethos-pdf-0.1.2.crate`
    - SHA256: `9245cf03c71802c385d65ac8539e678e513114fdbb359543ad0d1373af02b900`
- Exact operator commands requested for later approval:
  - `cargo publish --locked -p ethos-doc-core`
  - `cargo publish --locked -p ethos-verify`
  - `cargo publish --locked -p ethos-pdf`

## Requested Publication Order

1. Publish `ethos-doc-core` first.
2. Publish `ethos-verify` after crates.io reports `ethos-doc-core = 0.1.2`.
3. Publish `ethos-pdf` after crates.io reports `ethos-doc-core = 0.1.2`.

`ethos-verify` and `ethos-pdf` both depend on `ethos-doc-core`; no dependent crate publish should
be attempted until the base crate is visible from crates.io.

## Evidence Bound To This Request

- Candidate activation produced crate artifacts for exactly `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf`.
- Candidate activation reported version `0.1.2`.
- Candidate activation reported registry-equivalent consumer check status `pass`.
- Candidate activation reported source manifest activation applied.
- Candidate activation reported package publication approval `false`.
- Candidate activation reported public installation approval `false`.
- `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` manifests do not contain `publish = false`.
- The `ethos-cli` package remains `publish = false`.
- The `ethos-layout` package remains `publish = false`.
- The `ethos-tables` package remains `publish = false`.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Non-Approvals

- This request record does not approve `cargo publish`.
- This request record does not publish any crate.
- This request record does not create package tags.
- This request record does not approve Rust crate public installation wording.
- This request record does not approve PyPI upload.
- This request record does not approve the `ethos-cli` crate for publication.
- This request record does not approve hosted surfaces.
- This request record does not approve production positioning.
- This request record does not approve Windows packaged artifacts.
- This request record does not approve bundled project-maintained PDFium builds.
- This request record does not approve public benchmark reports.
- This request record does not approve public benchmark claims.
- This request record does not approve `ethos-doc`.
- This request record does not approve `ethos-rag`.

## Retained Blockers

- Actual crates.io publication remains blocked pending explicit decider approval.
- Rust crate public installation wording remains blocked pending explicit decider approval, operator
  publication, and registry closeout.
- Package tag creation remains blocked pending explicit decider approval.
- Python installation remains at `ethos-pdf==0.1.1` until separate PyPI `0.1.2` approval,
  operator publication, and closeout records pass.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Commands

```sh
python3 .github/scripts/test_patch_0_1_2_crates_publication_approval_request.py
python3 .github/scripts/package_publication_candidate_activation.py --json
python3 .github/scripts/test_patch_0_1_2_artifact_package_evidence.py
python3 .github/scripts/test_patch_0_1_2_public_install_wording_closeout.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 crates.io publication approval request recorded
Exact crate set, version map, package tag names, source binding, local crate artifact hashes, publish order, and retained blockers were recorded
cargo publish remains blocked pending explicit decider approval and later operator action
```
