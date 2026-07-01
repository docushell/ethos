# v0.3.0 Publication Approval Decision Validation - 2026-07-01

Validated source HEAD before this record: `1f6ab3c`.

v0.3.0 publication approval decision source commit:
`1f6ab3c7294c390d87f70cde6514a02024cf964c`.

v0.3.0 publication approval decision source tree:
`6541e73b597f39eea91d4d802b08823aa0bfa9a8`.

Status: **v0.3.0 publication approval decision recorded; operator publication remains pending**

Decision: accept exact v0.3.0 Rust crates.io and Python PyPI publication inputs.

This record accepts the exact v0.3.0 package publication approval request for later operator
execution. It also records the decider instruction to start the v0.3.0 CLI/GitHub Release and npm
publication lanes, but those artifact/npm lanes still require exact v0.3.0 artifact evidence and
vendor/package evidence before any GitHub Release artifact upload or `npm publish` action.

This decision record does not run `cargo publish`, upload any Python distribution, run
`npm publish`, upload GitHub Release artifacts, create release tags, create package tags, change
installable `0.3.0` public wording, approve hosted surfaces, approve production positioning,
approve Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve
`ethos-doc`, approve `ethos-rag`, approve public benchmark reports or claims, or approve DocuShell
integration.

## Accepted Inputs

- Repository: `docushell/ethos`
- Decision source commit: `1f6ab3c7294c390d87f70cde6514a02024cf964c`
- Decision source tree: `6541e73b597f39eea91d4d802b08823aa0bfa9a8`
- Approval request record:
  `docs/validation/v0-3-0-package-publication-approval-request-validation-2026-07-01.md`
- Approval request source commit: `39cb548cf6cfe20fbcb47ee605ba51f1ebf71f6b`
- Package evidence record:
  `docs/validation/v0-3-0-package-build-evidence-validation-2026-07-01.md`
- Package evidence source commit: `4b6d219df1757b6e4728c16c8023bee5c8cf8962`
- Approver: `docushell-admin` acting as decider.
- Date accepted: 2026-07-01.

## Rust crates.io Decision

Accepted Rust crate set:

- `ethos-doc-core = 0.3.0`
- `ethos-verify = 0.3.0`
- `ethos-pdf = 0.3.0`

Accepted Rust crate artifacts:

```text
ethos-doc-core-0.3.0.crate
sha256: 7ba41a2ae299a53a4677153beaaec5ed486a07b5da08b2ef13974b9a0be141cb

ethos-verify-0.3.0.crate
sha256: 00f001455ca207e65aaf464551d3ba05945cda0b06e9e1036f49ac587accbb95

ethos-pdf-0.3.0.crate
sha256: c2f4f2ccb6de6e54cd3257597cd28e7f6dec2a6d22befbd230d2c4cf31931cfd
```

After this decision record is merged and validation passes on merged source, an operator may run
only these Rust commands:

```sh
cargo publish --locked -p ethos-doc-core
cargo publish --locked -p ethos-verify
cargo publish --locked -p ethos-pdf
```

The operator must publish `ethos-doc-core` first. The operator must wait for crates.io to report
`ethos-doc-core = 0.3.0` before publishing dependent crates. The operator must stop if any crate
filename, hash, package version, source binding, package list, or retained blocker differs from
this record.

## Python PyPI Decision

Accepted Python package: `ethos-pdf==0.3.0`.

Accepted Python wheel:

```text
ethos_pdf-0.3.0-py3-none-any.whl
sha256: 9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265
```

Accepted deterministic build input: `SOURCE_DATE_EPOCH=0`.

Accepted wheel metadata:

- Name: `ethos-pdf`
- Version: `0.3.0`
- License-Expression: `Apache-2.0`
- Requires-Python: `>=3.8`
- Tag: `py3-none-any`

Accepted Python helper surface:

- `EthosCli`
- `proof_summary`
- `app_answer_release_decision`

After this decision record is merged and validation passes on merged source, an operator may upload
only this Python wheel: `ethos_pdf-0.3.0-py3-none-any.whl` with SHA256
`9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265`.

The operator must build with `SOURCE_DATE_EPOCH=0`. The operator must use a PyPI-approved
authentication path and must not record credentials in the repository. The operator must stop if
the built wheel filename, SHA256, package version, source commit, source tree, deterministic build
input, helper surface, or retained blockers differ from this record.

## CLI, GitHub Release, and npm Direction

CLI/GitHub Release artifact publication is approved only to start the v0.3.0 artifact evidence
lane. No GitHub Release artifact upload is authorized by this decision record.

npm publication is approved only to start the v0.3.0 npm alignment and vendor-refresh evidence
lane. No `npm publish` command is authorized by this decision record.

Required next evidence before GitHub Release artifact upload or npm publication:

- update the draft CLI artifact workflow smoke expectation from `ethos 0.2.0` to `ethos 0.3.0`;
- run the draft CLI artifact workflow for macOS arm64 and Linux x64;
- record exact v0.3.0 CLI artifact, checksum, inventory, and smoke evidence;
- refresh the npm vendor payload from the accepted v0.3.0 CLI artifacts;
- bump npm metadata only after the vendor evidence exists;
- record npm pack/install evidence for the exact v0.3.0 npm package candidate;
- record a separate GitHub Release artifact publication approval decision before upload;
- record a separate npm publication approval decision before `npm publish`.

## Package Tag Set

Accepted package tag name set for later package-tag approval:

- `ethos-package-ethos-doc-core-0.3.0`
- `ethos-package-ethos-verify-0.3.0`
- `ethos-package-ethos-pdf-0.3.0`

This decision record does not create package tags. Package tag creation remains blocked pending a
separate package-tag approval or closeout record.

## Non-Actions

- This decision record does not run `cargo publish`.
- This decision record does not upload any Python distribution.
- This decision record does not run `npm publish`.
- This decision record does not upload GitHub Release artifacts.
- This decision record does not create release tags.
- This decision record does not create package tags.
- This decision record does not approve installable `0.3.0` public wording.
- This decision record does not approve DocuShell integration.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

Publication remains a separate operator action.

## Retained Blockers

- Installable `0.3.0` public wording remains blocked until registry and artifact availability
  closeout passes.
- Rust public installation wording remains blocked until crates.io availability closeout passes.
- Python public installation wording remains blocked until PyPI availability closeout passes.
- GitHub Release artifact publication remains blocked pending exact v0.3.0 artifact evidence and
  a later artifact publication approval decision.
- npm publication remains blocked pending exact v0.3.0 vendor/package evidence and a later npm
  publication approval decision.
- Release tag creation remains blocked pending explicit release-tag approval.
- Package tag creation remains blocked pending explicit package-tag approval.
- DocuShell integration remains blocked pending closeout or explicit source-dependency integration
  approval.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Commands

```sh
python3 .github/scripts/test_v0_3_0_publication_approval_decision.py
python3 .github/scripts/test_v0_3_0_package_publication_approval_request.py
python3 .github/scripts/test_v0_3_0_package_build_evidence.py
make v0-3-release-prep PYTHON=python3
python3 .github/scripts/check_release_boundary_paths.py
python3 .github/scripts/validation_record_integrity.py
git diff --check
```

## Result

```text
v0.3.0 publication approval decision recorded
Exact Rust crates.io and Python PyPI operator inputs were accepted
CLI/GitHub Release and npm lanes are approved to start evidence work, but upload/publish execution remains blocked until exact artifact/npm evidence and later approval records pass
```
