# v0.3.0 Package Publication Approval Request Validation - 2026-07-01

Validated source HEAD before this record: `39cb548`.

v0.3.0 package publication approval request source commit:
`39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`.

v0.3.0 package publication approval request source tree:
`35076461b03ce8476cd8d73077c6f0bcaeae7dc3`.

Status: **v0.3.0 package publication approval request recorded; crates.io and PyPI publication remain blocked**

This record requests decider review for publishing exactly the v0.3.0 Rust library crate set to
crates.io and exactly the deterministic v0.3.0 Python wheel to PyPI. It does not approve or perform
`cargo publish`, PyPI upload, `npm publish`, GitHub Release artifact publication, release tag
creation, package tag creation, installable `0.3.0` public wording, DocuShell integration, hosted
surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
builds, `ethos-doc`, `ethos-rag`, or public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.3.0 package publication approval request
- Request source commit: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`
- Request source tree: `35076461b03ce8476cd8d73077c6f0bcaeae7dc3`
- Package evidence record:
  `docs/validation/v0-3-0-package-build-evidence-validation-2026-07-01.md`
- Package evidence source commit: `4b6d219df1757b6e4728c16c8023bee5c8cf8962`
- Rust candidate packages:
  - `ethos-doc-core = 0.3.0`
  - `ethos-verify = 0.3.0`
  - `ethos-pdf = 0.3.0`
- Python candidate package: `ethos-pdf==0.3.0`
- Python candidate wheel: `ethos_pdf-0.3.0-py3-none-any.whl`
- npm package metadata remains `@docushell/ethos-pdf@0.2.1`

## Exact Request Fields

- Decision requested: approve exact v0.3.0 crates.io publication inputs and exact deterministic
  v0.3.0 PyPI wheel publication inputs for later operator execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-07-01.
- Exact Rust crate list requested: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` only.
- Exact Rust package version map requested: `ethos-doc-core = 0.3.0`, `ethos-verify = 0.3.0`, and
  `ethos-pdf = 0.3.0`.
- Exact package tag name set requested for later package-tag approval: `ethos-package-ethos-doc-core-0.3.0`,
  `ethos-package-ethos-verify-0.3.0`, and `ethos-package-ethos-pdf-0.3.0`.
- Exact package tag source commit requested: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`.
- Exact package tag source tree requested: `35076461b03ce8476cd8d73077c6f0bcaeae7dc3`.
- Exact Python package requested: `ethos-pdf==0.3.0`.
- Exact Python distribution requested: `ethos_pdf-0.3.0-py3-none-any.whl` only.
- Exact Python deterministic build input requested: `SOURCE_DATE_EPOCH=0`.
- Exact Python public helper surface requested: `EthosCli`, `proof_summary`, and
  `app_answer_release_decision`.

## Candidate Artifacts Requested

Rust crate artifacts:

```text
ethos-doc-core-0.3.0.crate
sha256: 7ba41a2ae299a53a4677153beaaec5ed486a07b5da08b2ef13974b9a0be141cb

ethos-verify-0.3.0.crate
sha256: 00f001455ca207e65aaf464551d3ba05945cda0b06e9e1036f49ac587accbb95

ethos-pdf-0.3.0.crate
sha256: c2f4f2ccb6de6e54cd3257597cd28e7f6dec2a6d22befbd230d2c4cf31931cfd
```

Python wheel artifact:

```text
ethos_pdf-0.3.0-py3-none-any.whl
sha256: 9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265
```

## Requested Rust Publication Order

1. Publish `ethos-doc-core` first.
2. Publish `ethos-verify` after crates.io reports `ethos-doc-core = 0.3.0`.
3. Publish `ethos-pdf` after crates.io reports `ethos-doc-core = 0.3.0`.

`ethos-verify` and `ethos-pdf` both depend on `ethos-doc-core`; no dependent crate publish should
be attempted until the base crate is visible from crates.io.

Exact Rust operator commands requested for later approval:

```sh
cargo publish --locked -p ethos-doc-core
cargo publish --locked -p ethos-verify
cargo publish --locked -p ethos-pdf
```

## Evidence Bound To This Request

- `docs/validation/v0-3-0-package-build-evidence-validation-2026-07-01.md` records local Rust
  candidate package assembly for exactly `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`.
- The evidence record reports candidate version `0.3.0`.
- The evidence record reports registry-equivalent Rust consumer check status `pass`.
- The evidence record reports `package_publication_approved: false`.
- The evidence record reports `public_installation_approved: false`.
- The evidence record reports local Python wheel build, install, and helper smoke status `pass`.
- The Python helper smoke imported `EthosCli`, `proof_summary`, and
  `app_answer_release_decision` from the installed candidate wheel.
- `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` source manifests carry the current
  publication-prep metadata.
- The `ethos-cli`, `ethos-layout`, and `ethos-tables` source packages remain `publish = false`.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Manual Decision Gate

Manual action is required before any crates.io publication or PyPI upload. A decider must accept or
reject this exact request packet. Only after a separate approval decision record is merged and its
validation passes may an operator publish the exact Rust crate set and the exact Python wheel named
above.

This request does not select an sdist, alternate wheel, additional crate, npm package, CLI artifact,
release artifact, public wording change, DocuShell integration path, or broad package-publication
class. If any artifact filename, version, hash, source commit, source tree, package list, helper
surface, public wording, or blocker set changes, this request must be replaced by a new evidence
record and a new decider review.

## Non-Approvals

- This request record does not approve `cargo publish`.
- This request record does not publish any crate.
- This request record does not approve PyPI upload.
- This request record does not upload any Python distribution.
- This request record does not approve the deterministic wheel hash.
- This request record does not approve an sdist.
- This request record does not approve another wheel.
- This request record does not approve `npm publish`.
- This request record does not approve GitHub Release artifact publication.
- This request record does not create a release tag.
- This request record does not create package tags.
- This request record does not approve installable `0.3.0` public wording.
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

- Actual crates.io publication remains blocked pending explicit decider approval.
- Actual PyPI upload remains blocked pending explicit decider approval.
- Rust crate public installation wording remains blocked pending operator publication, registry
  availability, smoke evidence, and wording closeout.
- Python public installation wording remains blocked pending PyPI availability, smoke evidence, and
  wording closeout.
- Package tag creation remains blocked pending explicit package-tag approval.
- Release tag creation remains blocked pending explicit release-tag approval.
- npm alignment remains blocked.
- `npm publish` remains blocked.
- GitHub Release artifact publication remains blocked.
- CLI artifact evidence remains blocked for v0.3.0.
- DocuShell integration remains blocked.
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
python3 .github/scripts/test_v0_3_0_package_publication_approval_request.py
python3 .github/scripts/test_v0_3_0_package_build_evidence.py
make v0-3-release-prep PYTHON=python3
python3 .github/scripts/check_release_boundary_paths.py
python3 .github/scripts/validation_record_integrity.py
git diff --check
```

## Result

```text
v0.3.0 package publication approval request recorded
Exact Rust crate set, Rust crate hashes, Python wheel hash, helper surface, source binding, publish order, and retained blockers were recorded
crates.io publication and PyPI upload remain blocked pending explicit decider approval and later operator action
```
