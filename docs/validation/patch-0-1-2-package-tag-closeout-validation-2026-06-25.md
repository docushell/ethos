# Patch 0.1.2 Package Tag Closeout Validation - 2026-06-25

Validated source HEAD before this record: `8ab9e18`.

Patch 0.1.2 package tag closeout source commit: `8ab9e180cfb96a1e6659dff97db7fb7a4288817b`.

Patch 0.1.2 package tag closeout source tree: `1a40205d4d87614e14278ab7d0107fa58bbeeb46`.

Status: **patch 0.1.2 package tags created and pushed**

This record closes the bounded patch `0.1.2` package tag creation lane for the three package tags
approved in `docs/validation/patch-0-1-2-package-tag-approval-decision-validation-2026-06-25.md`.
It records only the completed annotated package tag operator action and remote tag evidence. It does
not change package contents, change public wording, approve hosted surfaces, approve production
positioning, approve Windows packaged artifacts, approve bundled project-maintained PDFium builds,
approve `ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: patch `0.1.2` package tag closeout
- Approval decision record:
  `docs/validation/patch-0-1-2-package-tag-approval-decision-validation-2026-06-25.md`
- Package tag source commit: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`
- Package tag source tree: `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`

## Completed Package Tags

- `ethos-package-ethos-doc-core-0.1.2`
  - local tag object prefix: `4ced-3275-6502`
  - remote tag object prefix: `4ced-3275-6502`
  - dereferenced commit: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`
- `ethos-package-ethos-verify-0.1.2`
  - local tag object prefix: `57dd-49a6-b8a6`
  - remote tag object prefix: `57dd-49a6-b8a6`
  - dereferenced commit: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`
- `ethos-package-ethos-pdf-0.1.2`
  - local tag object prefix: `0243-15d5-a973`
  - remote tag object prefix: `0243-15d5-a973`
  - dereferenced commit: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`

## Operator Evidence

Pre-tag checks passed:

```sh
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_request.py
python3 .github/scripts/test_patch_0_1_2_python_public_install_wording_closeout.py
make release-candidate-prep PYTHON=python3
git diff --check
```

Pre-tag existence checks returned no existing patch `0.1.2` package tags locally or on `origin`.

Approved local tag creation commands executed:

```sh
git tag -a ethos-package-ethos-doc-core-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d -m "Package tag ethos-doc-core 0.1.2"
git tag -a ethos-package-ethos-verify-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d -m "Package tag ethos-verify 0.1.2"
git tag -a ethos-package-ethos-pdf-0.1.2 3bc3564e38c1168b2db72f38863d324b6b57bd4d -m "Package tag ethos-pdf 0.1.2"
```

Approved remote push command executed:

```sh
git push origin refs/tags/ethos-package-ethos-doc-core-0.1.2 refs/tags/ethos-package-ethos-verify-0.1.2 refs/tags/ethos-package-ethos-pdf-0.1.2
```

Observed push result:

```text
* [new tag]         ethos-package-ethos-doc-core-0.1.2 -> ethos-package-ethos-doc-core-0.1.2
* [new tag]         ethos-package-ethos-verify-0.1.2 -> ethos-package-ethos-verify-0.1.2
* [new tag]         ethos-package-ethos-pdf-0.1.2 -> ethos-package-ethos-pdf-0.1.2
```

Remote verification:

```text
4ced-3275-6502... refs/tags/ethos-package-ethos-doc-core-0.1.2
3bc3564e38c1168b2db72f38863d324b6b57bd4d refs/tags/ethos-package-ethos-doc-core-0.1.2^{}
0243-15d5-a973... refs/tags/ethos-package-ethos-pdf-0.1.2
3bc3564e38c1168b2db72f38863d324b6b57bd4d refs/tags/ethos-package-ethos-pdf-0.1.2^{}
57dd-49a6-b8a6... refs/tags/ethos-package-ethos-verify-0.1.2
3bc3564e38c1168b2db72f38863d324b6b57bd4d refs/tags/ethos-package-ethos-verify-0.1.2^{}
```

## Retained Blockers

- Package tag creation closeout is complete for the three patch `0.1.2` package tags.
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
python3 .github/scripts/test_patch_0_1_2_package_tag_closeout.py
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_package_tag_approval_request.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 package tag closeout recorded
The three approved annotated package tags exist on origin and dereference to the approved source commit
Hosted, production, Windows, bundled PDFium, benchmark, ethos-doc, and ethos-rag surfaces remain blocked
```
