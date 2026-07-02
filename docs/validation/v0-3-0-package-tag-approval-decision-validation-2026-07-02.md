# v0.3.0 Package Tag Approval Decision Validation - 2026-07-02

Validated source HEAD before this record: `81dfe10`.

v0.3.0 package tag approval decision source commit:
`81dfe102b0b21ec62e9952d844b4cfc2e177cdc4`.

v0.3.0 package tag approval decision source tree:
`4e3dd1f119cc274d6c31b59bfac49415cc0ec857`.

Status: **v0.3.0 package tag approval decision recorded; operator tag creation remains pending**

This record accepts the exact v0.3.0 package tag creation request after decider approval. It
approves only bounded later operator creation and push of the three exact annotated package tags
listed below. It does not create package tags, push package tags, move any existing tag, create or
move GitHub Release tag `v0.3.0`, change package contents, change public wording, approve
DocuShell integration, approve hosted surfaces, approve production positioning, approve Windows
packaged artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`,
approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.3.0 package tag creation approval decision
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/v0-3-0-package-tag-approval-request-validation-2026-07-02.md`
- Package tag source commit accepted by this decision: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`
- Package tag source tree accepted by this decision: `35076461b03ce8476cd8d73077c6f0bcaeae7dc3`

## Exact Decision Fields

- Decision: accept exact v0.3.0 package tag creation decision packet.
- Decider approval supplied: Approve exact v0.3.0 package tag creation request for
  ethos-package-ethos-doc-core-0.3.0, ethos-package-ethos-verify-0.3.0, and
  ethos-package-ethos-pdf-0.3.0, bound to package tag source commit
  39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b and source tree
  35076461b03ce8476cd8d73077c6f0bcaeae7dc3. Keep DocuShell integration, hosted surfaces,
  production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds,
  public benchmark claims, ethos-doc, and ethos-rag blocked.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-07-02.
- Exact package tag name set accepted by this decision:
  - `ethos-package-ethos-doc-core-0.3.0`
  - `ethos-package-ethos-verify-0.3.0`
  - `ethos-package-ethos-pdf-0.3.0`
- Exact package tag source commit accepted by this decision:
  `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`.
- Exact package tag source tree accepted by this decision:
  `35076461b03ce8476cd8d73077c6f0bcaeae7dc3`.

## Approved Later Operator Action

After this decision record is merged and validation passes on merged source, an operator may run
only these tag commands:

```sh
git tag -a ethos-package-ethos-doc-core-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b
git tag -a ethos-package-ethos-verify-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b
git tag -a ethos-package-ethos-pdf-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b
git push origin refs/tags/ethos-package-ethos-doc-core-0.3.0
git push origin refs/tags/ethos-package-ethos-verify-0.3.0
git push origin refs/tags/ethos-package-ethos-pdf-0.3.0
```

The operator must use annotated tags. The operator must stop if any requested tag already exists
locally or on `origin`, if the requested source commit or tree does not match this record, or if
any retained blocker is softened.

Package tag creation remains a separate operator action after this decision is merged and
validation passes on merged source. This decision record does not create or push any tag.

## Required Operator Pre-Tag Checks

Before creating tags, the operator must run:

```sh
python3 .github/scripts/test_v0_3_0_package_tag_approval_decision.py
python3 .github/scripts/test_v0_3_0_package_tag_approval_request.py
python3 .github/scripts/test_v0_3_0_public_install_wording_closeout.py
make v0-3-release-prep PYTHON=python3
git diff --check
```

## Evidence Bound To This Decision

- Decider decision supplied:
  `Approve exact v0.3.0 package tag creation request for ethos-package-ethos-doc-core-0.3.0,
  ethos-package-ethos-verify-0.3.0, and ethos-package-ethos-pdf-0.3.0, bound to package tag
  source commit 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b and source tree
  35076461b03ce8476cd8d73077c6f0bcaeae7dc3. Keep DocuShell integration, hosted surfaces,
  production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds,
  public benchmark claims, ethos-doc, and ethos-rag blocked.`
- The package tag approval request recorded the exact tag names and source binding.
- The requested source commit resolves to the requested source tree.
- The v0.3.0 publication closeout records `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
  published at `0.3.0`.
- The v0.3.0 public install wording closeout records the approved public `0.3.0` install wording
  across the live Rust, Python, npm, and GitHub Release evaluation surfaces.
- DocuShell integration remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Non-Actions

- This decision record does not create package tags.
- This decision record does not push package tags.
- This decision record does not move or delete any package tag.
- This decision record does not create or move GitHub Release tag `v0.3.0`.
- This decision record does not create or approve any additional GitHub Release target.
- This decision record does not change package contents.
- This decision record does not change public installation wording.
- This decision record does not approve DocuShell integration.
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
python3 .github/scripts/test_v0_3_0_package_tag_approval_decision.py
python3 .github/scripts/test_v0_3_0_package_tag_approval_request.py
python3 .github/scripts/test_v0_3_0_public_install_wording_closeout.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
python3 .github/scripts/validation_record_integrity.py
make v0-3-release-prep PYTHON=python3
git diff --check
```

## Result

```text
v0.3.0 package tag approval decision recorded
Exact package tag names and source binding are accepted for later operator action
No package tags are created or pushed by this record
```
