# v0.3.0 Package Tag Approval Request Validation - 2026-07-02

Validated source HEAD before this record: `77e452b`.

v0.3.0 package tag approval request source commit:
`77e452b447c93fd93b3deac72a325cbb2441fa87`.

v0.3.0 package tag approval request source tree:
`76bd5c69c16aee50b7eb7b8736156876598161a2`.

Status: **v0.3.0 package tag approval request recorded; package tag creation remains blocked**

This record requests decider review for creating the exact v0.3.0 package tags named in the
package publication approval request and accepted by the publication approval decision. It does
not create package tags, approve package tag creation, create a release tag, move or replace
GitHub Release tag `v0.3.0`, change package contents, change public wording, approve DocuShell
integration, approve hosted surfaces, approve production positioning, approve Windows packaged
artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`, approve
`ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.3.0 package tag creation approval request
- Source package publication approval request:
  `docs/validation/v0-3-0-package-publication-approval-request-validation-2026-07-01.md`
- Source publication approval decision:
  `docs/validation/v0-3-0-publication-approval-decision-validation-2026-07-01.md`
- Source publication closeout:
  `docs/validation/v0-3-0-publication-closeout-validation-2026-07-01.md`
- GitHub Release artifact closeout:
  `docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md`
- npm publication closeout:
  `docs/validation/v0-3-0-npm-publication-closeout-validation-2026-07-02.md`
- Public install wording closeout:
  `docs/validation/v0-3-0-public-install-wording-closeout-validation-2026-07-02.md`
- Package tag source commit requested: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`
- Package tag source tree requested: `35076461b03ce8476cd8d73077c6f0bcaeae7dc3`

## Exact Request Fields

- Decision requested: approve exact v0.3.0 package tag creation for later operator execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-07-02.
- Exact package tag name set requested:
  - `ethos-package-ethos-doc-core-0.3.0`
  - `ethos-package-ethos-verify-0.3.0`
  - `ethos-package-ethos-pdf-0.3.0`
- Exact package tag source commit requested: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`.
- Exact package tag source tree requested: `35076461b03ce8476cd8d73077c6f0bcaeae7dc3`.
- Exact later operator commands requested:

```sh
git tag -a ethos-package-ethos-doc-core-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b
git tag -a ethos-package-ethos-verify-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b
git tag -a ethos-package-ethos-pdf-0.3.0 39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b
git push origin refs/tags/ethos-package-ethos-doc-core-0.3.0
git push origin refs/tags/ethos-package-ethos-verify-0.3.0
git push origin refs/tags/ethos-package-ethos-pdf-0.3.0
```

The operator must use annotated tags and must stop if any requested tag already exists locally or
on `origin`, if the requested source commit or tree does not match this record, or if any retained
blocker is softened.

## Evidence Bound To This Request

- The v0.3.0 package publication approval request recorded the exact package tag name set and
  source binding.
- The v0.3.0 publication approval decision accepted that package tag name set for later
  package-tag approval.
- The v0.3.0 publication closeout records `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`
  published on crates.io at `0.3.0`, plus `ethos-pdf==0.3.0` published on PyPI.
- The v0.3.0 GitHub Release artifact publication closeout records GitHub Release tag `v0.3.0`
  and the approved macOS arm64/Linux x64 CLI artifacts. This package-tag request does not modify
  that release tag evidence.
- The v0.3.0 npm publication closeout records `@docushell/ethos-pdf@0.3.0` live on npm.
- The v0.3.0 public install wording closeout records the approved public install wording across
  the live Rust, Python, npm, and GitHub Release evaluation surfaces.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Non-Actions

- This request record does not create package tags.
- This request record does not approve package tag creation.
- This request record does not move or delete any tag.
- This request record does not create a release tag.
- This request record does not move or replace GitHub Release tag `v0.3.0`.
- This request record does not create or approve any additional GitHub Release target.
- This request record does not change package contents.
- This request record does not change public installation wording.
- This request record does not approve DocuShell integration.
- This request record does not approve hosted surfaces.
- This request record does not approve production positioning.
- This request record does not approve Windows packaged artifacts.
- This request record does not approve bundled project-maintained PDFium builds.
- This request record does not approve public benchmark reports.
- This request record does not approve public benchmark claims.
- This request record does not approve `ethos-doc`.
- This request record does not approve `ethos-rag`.

## Retained Blockers

- Package tag creation remains blocked until a separate explicit approval decision is recorded.
- No additional release tag or GitHub Release target is approved by this package-tag request.
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
v0.3.0 package tag approval request recorded
Exact package tag names and source binding were recorded for decider review
Package tag creation remains blocked pending a separate explicit approval decision
```
