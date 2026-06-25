# Patch 0.1.2 Package Tag Approval Decision Validation - 2026-06-25

Validated source HEAD before this record: `070a5c5`.

Patch 0.1.2 package tag approval decision source commit: `070a5c54afe780f95fc6fbe4598558107949695c`.

Patch 0.1.2 package tag approval decision source tree: `93e025c44993c18a42203b7b999d9dd5af94e709`.

Status: **patch 0.1.2 package tag approval decision recorded; operator tag creation remains pending**

This record accepts the exact patch `0.1.2` package tag creation request after decider approval. It
approves only bounded later operator creation and push of the three exact annotated package tags
listed below. It does not create package tags, push package tags, move any existing tag, change
package contents, change public wording, approve hosted surfaces, approve production positioning,
approve Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve
`ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: patch `0.1.2` package tag creation approval decision
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/patch-0-1-2-package-tag-approval-request-validation-2026-06-25.md`
- Package tag source commit accepted by this decision: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`
- Package tag source tree accepted by this decision: `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`

## Exact Decision Fields

- Decision: accept exact patch `0.1.2` package tag creation decision packet.
- Decider approval supplied: Yes, I Approve exact patch 0.1.2.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-25.
- Exact package tag name set accepted by this decision:
  - `ethos-package-ethos-doc-core-0.1.2`
  - `ethos-package-ethos-verify-0.1.2`
  - `ethos-package-ethos-pdf-0.1.2`
- Exact package tag source commit accepted by this decision:
  `3bc3564e38c1168b2db72f38863d324b6b57bd4d`.
- Exact package tag source tree accepted by this decision:
  `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`.

## Approved Later Operator Action

After this decision record is merged and validation passes on merged source, an operator may run
only these tag commands:

```sh
git tag -a ethos-package-ethos-doc-core-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d
git tag -a ethos-package-ethos-verify-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d
git tag -a ethos-package-ethos-pdf-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d
git push origin refs/tags/ethos-package-ethos-doc-core-0.1.2
git push origin refs/tags/ethos-package-ethos-verify-0.1.2
git push origin refs/tags/ethos-package-ethos-pdf-0.1.2
```

The operator must use annotated tags. The operator must stop if any requested tag already exists
locally or on `origin`, if the requested source commit or tree does not match this record, or if
any retained blocker is softened.

Package tag creation remains a separate operator action after this decision is merged and validation
passes on merged source. This decision record does not create or push any tag.

## Required Operator Pre-Tag Checks

Before creating tags, the operator must run:

```sh
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_request.py
python3 .github/scripts/test_patch_0_1_2_python_public_install_wording_closeout.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Evidence Bound To This Decision

- Decider decision supplied: Yes, I Approve exact patch 0.1.2.
- The package tag approval request recorded the exact tag names and source binding.
- The requested source commit resolves to the requested source tree.
- The crates.io publication closeout records `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
  published at `0.1.2`.
- The current public README and public package installation wording already point all approved
  evaluation install surfaces to `0.1.2`.
- Public beta evaluation surfaces remain unchanged.

## Non-Actions

- This decision record does not create package tags.
- This decision record does not push package tags.
- This decision record does not move or delete any tag.
- This decision record does not change package contents.
- This decision record does not change public installation wording.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Retained Blockers

- Package tag creation remains a separate operator action after this decision is merged and
  validation passes on merged source.
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
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_request.py
python3 .github/scripts/test_patch_0_1_2_crates_publication_closeout.py
python3 .github/scripts/test_patch_0_1_2_python_public_install_wording_closeout.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 package tag approval decision recorded
Exact package tag names and source binding are accepted for later operator action
No package tags are created or pushed by this record
```
