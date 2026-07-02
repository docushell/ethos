# v0.3.0 Package Tag Closeout Validation - 2026-07-02

Validated source HEAD before this record: `068d843`.

v0.3.0 package tag closeout source commit:
`068d843e28ff1ce4e45182665245e08e222d8f17`.

v0.3.0 package tag closeout source tree:
`7e50368c8d59756b467a4e257b23ecf64cab2eca`.

Status: **v0.3.0 package tags created and pushed**

This record closes the bounded v0.3.0 package tag creation lane for the three package tags
approved in `docs/validation/v0-3-0-package-tag-approval-decision-validation-2026-07-02.md`. It
records only the completed annotated package tag operator action and remote tag evidence. It does
not change package contents, change public wording, approve DocuShell integration, approve hosted
surfaces, approve production positioning, approve Windows packaged artifacts, approve bundled
project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or approve public
benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.3.0 package tag closeout
- Approval request record:
  `docs/validation/v0-3-0-package-tag-approval-request-validation-2026-07-02.md`
- Approval decision record:
  `docs/validation/v0-3-0-package-tag-approval-decision-validation-2026-07-02.md`
- Package tag source commit: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`
- Package tag source tree: `35076461b03ce8476cd8d73077c6f0bcaeae7dc3`

## Completed Package Tags

- `ethos-package-ethos-doc-core-0.3.0`
  - local tag object prefix: `c772-f2ca-0c57`
  - remote tag object prefix: `c772-f2ca-0c57`
  - dereferenced commit: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`
- `ethos-package-ethos-verify-0.3.0`
  - local tag object prefix: `a9cf-6df0-a7a7`
  - remote tag object prefix: `a9cf-6df0-a7a7`
  - dereferenced commit: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`
- `ethos-package-ethos-pdf-0.3.0`
  - local tag object prefix: `6489-829d-5f7d`
  - remote tag object prefix: `6489-829d-5f7d`
  - dereferenced commit: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`

## Operator Evidence

Pre-tag checks passed:

```sh
python3 .github/scripts/test_v0_3_0_package_tag_approval_decision.py
python3 .github/scripts/test_v0_3_0_package_tag_approval_request.py
python3 .github/scripts/test_v0_3_0_public_install_wording_closeout.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
python3 .github/scripts/validation_record_integrity.py
make v0-3-release-prep PYTHON=python3
git diff --check
```

Pre-tag existence checks returned no existing v0.3.0 package tags locally or on `origin`.

Approved local tag creation commands executed:

```sh
git tag -a ethos-package-ethos-doc-core-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b -m "ethos-package-ethos-doc-core-0.3.0"
git tag -a ethos-package-ethos-verify-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b -m "ethos-package-ethos-verify-0.3.0"
git tag -a ethos-package-ethos-pdf-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b -m "ethos-package-ethos-pdf-0.3.0"
```

Approved remote push commands executed:

```sh
git push origin refs/tags/ethos-package-ethos-doc-core-0.3.0
git push origin refs/tags/ethos-package-ethos-verify-0.3.0
git push origin refs/tags/ethos-package-ethos-pdf-0.3.0
```

Observed push result:

```text
* [new tag]         ethos-package-ethos-doc-core-0.3.0 -> ethos-package-ethos-doc-core-0.3.0
* [new tag]         ethos-package-ethos-verify-0.3.0 -> ethos-package-ethos-verify-0.3.0
* [new tag]         ethos-package-ethos-pdf-0.3.0 -> ethos-package-ethos-pdf-0.3.0
```

Remote verification:

```text
c772-f2ca-0c57... refs/tags/ethos-package-ethos-doc-core-0.3.0
39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b refs/tags/ethos-package-ethos-doc-core-0.3.0^{}
a9cf-6df0-a7a7... refs/tags/ethos-package-ethos-verify-0.3.0
39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b refs/tags/ethos-package-ethos-verify-0.3.0^{}
6489-829d-5f7d... refs/tags/ethos-package-ethos-pdf-0.3.0
39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b refs/tags/ethos-package-ethos-pdf-0.3.0^{}
```

## Retained Blockers

- Package tag creation closeout is complete for the three v0.3.0 package tags.
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

## Commands

```sh
python3 .github/scripts/test_v0_3_0_package_tag_closeout.py
python3 .github/scripts/test_v0_3_0_package_tag_approval_decision.py
python3 .github/scripts/test_v0_3_0_package_tag_approval_request.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
python3 .github/scripts/validation_record_integrity.py
make v0-3-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.3.0 package tag closeout recorded
The three approved annotated package tags exist on origin and dereference to the approved source commit
DocuShell integration, hosted, production, Windows, bundled PDFium, benchmark, ethos-doc, and ethos-rag surfaces remain blocked
```
