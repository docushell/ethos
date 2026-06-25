# Patch 0.1.2 Package Tag Approval Request Validation - 2026-06-25

Validated source HEAD before this record: `bc14f36`.

Patch 0.1.2 package tag approval request source commit: `bc14f36931ae7453c35fc4ecd1a2a9159f2127d4`.

Patch 0.1.2 package tag approval request source tree: `2b597508e020e8c1090508d5a60fa66af4aa7951`.

Status: **patch 0.1.2 package tag approval request recorded; tag creation remains blocked**

This record requests decider review for creating the exact patch `0.1.2` package tags that were
named in the crates.io publication request and accepted by the crates.io publication decision. It
does not create package tags, approve package tag creation, move any existing tag, change package
contents, change public wording, approve hosted surfaces, approve production positioning, approve
Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`,
approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: patch `0.1.2` package tag creation approval request
- Source request record:
  `docs/validation/patch-0-1-2-crates-publication-approval-request-validation-2026-06-25.md`
- Source decision record:
  `docs/validation/patch-0-1-2-crates-publication-approval-decision-validation-2026-06-25.md`
- Source publication closeout record:
  `docs/validation/patch-0-1-2-crates-publication-closeout-validation-2026-06-25.md`
- Package tag source commit requested: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`
- Package tag source tree requested: `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`

## Exact Request Fields

- Decision requested: approve exact patch `0.1.2` package tag creation for later operator
  execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-06-25.
- Exact package tag name set requested:
  - `ethos-package-ethos-doc-core-0.1.2`
  - `ethos-package-ethos-verify-0.1.2`
  - `ethos-package-ethos-pdf-0.1.2`
- Exact package tag source commit requested: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`.
- Exact package tag source tree requested: `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`.
- Exact later operator commands requested:

```sh
git tag -a ethos-package-ethos-doc-core-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d
git tag -a ethos-package-ethos-verify-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d
git tag -a ethos-package-ethos-pdf-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d
git push origin refs/tags/ethos-package-ethos-doc-core-0.1.2
git push origin refs/tags/ethos-package-ethos-verify-0.1.2
git push origin refs/tags/ethos-package-ethos-pdf-0.1.2
```

The operator must use annotated tags and must stop if any requested tag already exists locally or on
`origin`, if the requested source commit or tree does not match this record, or if any retained
blocker is softened.

## Evidence Bound To This Request

- The crates.io publication approval request recorded the exact package tag name set and source
  binding.
- The crates.io publication approval decision accepted that exact tag name set and source binding.
- The crates.io publication closeout records `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
  published at `0.1.2`.
- The current public README and public package installation wording already point all approved
  evaluation install surfaces to `0.1.2`.
- Public beta evaluation surfaces remain unchanged.

## Non-Actions

- This request record does not create package tags.
- This request record does not approve package tag creation.
- This request record does not move or delete any tag.
- This request record does not change package contents.
- This request record does not change public installation wording.
- This request record does not approve hosted surfaces.
- This request record does not approve production positioning.
- This request record does not approve Windows packaged artifacts.
- This request record does not approve bundled project-maintained PDFium builds.
- This request record does not approve public benchmark reports.
- This request record does not approve public benchmark claims.
- This request record does not approve `ethos-doc`.
- This request record does not approve `ethos-rag`.

## Retained Blockers

- Tag creation remains blocked until a separate explicit approval decision is recorded.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Commands

```sh
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_request.py
python3 .github/scripts/test_patch_0_1_2_crates_publication_closeout.py
python3 .github/scripts/test_patch_0_1_2_python_public_install_wording_closeout.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 package tag approval request recorded
Exact package tag names and source binding were recorded for decider review
Package tag creation remains blocked pending a separate explicit approval decision
```
