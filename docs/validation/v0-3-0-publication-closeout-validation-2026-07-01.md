# v0.3.0 Publication Closeout Validation - 2026-07-01

Validated source HEAD before this record: `681d324`.

v0.3.0 publication closeout source commit:
`681d324653df91a89f6528fbc2a4c685ff0d0114`.

v0.3.0 publication closeout source tree:
`7480149de77f325bbc051f5babadda13a65ef842`.

Status: **v0.3.0 Rust crates and Python wheel published; artifact/npm/tag/install wording lanes remain blocked**

This record closes the bounded v0.3.0 crates.io and PyPI operator publication lane accepted by
`docs/validation/v0-3-0-publication-approval-decision-validation-2026-07-01.md`. It records
operator publish/upload evidence and live registry verification for the exact approved Rust crate
set and deterministic Python wheel. It does not approve GitHub Release artifact upload,
`npm publish`, public install wording, package tags, release tags, DocuShell integration, hosted
surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, or broader
public wording.

## Published Rust Crates

- `ethos-doc-core = 0.3.0`
- `ethos-verify = 0.3.0`
- `ethos-pdf = 0.3.0`

## Rust Operator Publish Evidence

`ethos-doc-core` command:

```text
cargo publish --locked -p ethos-doc-core
```

Observed result:

```text
Uploaded ethos-doc-core v0.3.0 to registry `crates-io`
Published ethos-doc-core v0.3.0 at registry `crates-io`
```

Live registry verification:

```text
crate: ethos-doc-core
version: 0.3.0
created_at: 2026-07-01T14:51:24.877439Z
checksum: 62f179f2dfc07deaae7ee3bca54a8961548b2b6ee33f015ec99b0c5d8423084c
yanked: false
```

`ethos-verify` command:

```text
cargo publish --locked -p ethos-verify
```

Observed result:

```text
Uploaded ethos-verify v0.3.0 to registry `crates-io`
Published ethos-verify v0.3.0 at registry `crates-io`
```

Live registry verification:

```text
crate: ethos-verify
version: 0.3.0
created_at: 2026-07-01T14:55:58.881379Z
checksum: 4b2339f82d0c9e01f20fbe163433efb990ae7d27abd93d9cdfddd258dbead8fb
yanked: false
```

`ethos-pdf` command:

```text
cargo publish --locked -p ethos-pdf
```

Observed result:

```text
Uploaded ethos-pdf v0.3.0 to registry `crates-io`
Published ethos-pdf v0.3.0 at registry `crates-io`
```

Live registry verification:

```text
crate: ethos-pdf
version: 0.3.0
created_at: 2026-07-01T14:57:57.306202Z
checksum: a06a33541df16f630865466ea440bfddc5e4d8304ffe0a4c295a6f74fd033a28
yanked: false
```

## Rust Dependency-Order Evidence

- `ethos-doc-core` was published first.
- `ethos-verify` was published after crates.io reported `ethos-doc-core = 0.3.0`.
- `ethos-pdf` was published after crates.io reported `ethos-verify = 0.3.0`.

## Published Python Package

- Package: `ethos-pdf`
- Version: `0.3.0`
- Import package: `ethos_pdf`
- Registry: `https://pypi.org/`
- Project URL: `https://pypi.org/project/ethos-pdf/0.3.0/`
- Distribution: `ethos_pdf-0.3.0-py3-none-any.whl`
- Deterministic build input: `SOURCE_DATE_EPOCH=0`
- SHA256:
  `9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265`

## Python Operator Upload Evidence

Pre-upload checks:

```text
SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir target/python-pypi-0.3.0
Successfully built ethos_pdf-0.3.0-py3-none-any.whl
shasum -a 256 target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl
9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265  target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl
python3 -m twine check target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl
Checking target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl: PASSED
```

Upload command:

```text
python3 -m twine upload target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl
```

Observed upload result:

```text
Uploading distributions to https://upload.pypi.org/legacy/
WARNING This environment is not supported for trusted publishing
Uploading ethos_pdf-0.3.0-py3-none-any.whl
100% 25.6/25.6 kB
View at: https://pypi.org/project/ethos-pdf/0.3.0/
```

The upload used a PyPI-approved credential path. No credential is recorded in this repository.

## PyPI Registry Verification

Registry endpoint:

```text
https://pypi.org/pypi/ethos-pdf/0.3.0/json
```

Result:

```text
name: ethos-pdf
version: 0.3.0
requires_python: >=3.8
filename: ethos_pdf-0.3.0-py3-none-any.whl
packagetype: bdist_wheel
python_version: py3
digests.sha256: 9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265
size: 16575
upload_time_iso_8601: 2026-07-01T15:03:07.368729Z
yanked: false
url: https://files.pythonhosted.org/packages/31/5c/5aaa1ba4f887f4002593ffe465369cb8c66823ffa9ac540d99e072e4e589/ethos_pdf-0.3.0-py3-none-any.whl
```

## Approved Candidate Binding

- Approval request record:
  `docs/validation/v0-3-0-package-publication-approval-request-validation-2026-07-01.md`
- Approval decision record:
  `docs/validation/v0-3-0-publication-approval-decision-validation-2026-07-01.md`
- Package evidence record:
  `docs/validation/v0-3-0-package-build-evidence-validation-2026-07-01.md`
- Approval decision source commit: `1f6ab3c7294c390d87f70cde6514a02024cf964c`
- Package evidence source commit: `4b6d219df1757b6e4728c16c8023bee5c8cf8962`
- Exact deterministic build input: `SOURCE_DATE_EPOCH=0`
- Exact Python wheel: `ethos_pdf-0.3.0-py3-none-any.whl`
- Exact Python wheel SHA256:
  `9eb106deafcd1d9717e5e7b67dc9413180421aba25a5257266352d09540b3265`
- Accepted Rust crate artifact SHA256 values:
  - `ethos-doc-core-0.3.0.crate`:
    `7ba41a2ae299a53a4677153beaaec5ed486a07b5da08b2ef13974b9a0be141cb`
  - `ethos-verify-0.3.0.crate`:
    `00f001455ca207e65aaf464551d3ba05945cda0b06e9e1036f49ac587accbb95`
  - `ethos-pdf-0.3.0.crate`:
    `c2f4f2ccb6de6e54cd3257597cd28e7f6dec2a6d22befbd230d2c4cf31931cfd`

## Retained Blockers

- Public installation wording may be updated only in a separate bounded docs lane.
- GitHub Release artifact publication remains blocked pending exact v0.3.0 artifact evidence and
  a later artifact publication approval decision.
- npm publication remains blocked pending exact v0.3.0 vendor/package evidence and a later npm
  publication approval decision.
- npm package metadata remains at `@docushell/ethos-pdf@0.2.1` until the approved vendor refresh
  and npm package evidence lane passes.
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
cargo publish --locked -p ethos-doc-core
cargo publish --locked -p ethos-verify
cargo publish --locked -p ethos-pdf
SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir target/python-pypi-0.3.0
shasum -a 256 target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl
python3 -m twine check target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl
python3 -m twine upload target/python-pypi-0.3.0/ethos_pdf-0.3.0-py3-none-any.whl
python3 .github/scripts/test_v0_3_0_publication_closeout.py
python3 .github/scripts/test_v0_3_0_publication_approval_decision.py
python3 .github/scripts/test_v0_3_0_package_publication_approval_request.py
make v0-3-release-prep PYTHON=python3
python3 .github/scripts/check_release_boundary_paths.py
python3 .github/scripts/validation_record_integrity.py
git diff --check
```

## Result

```text
v0.3.0 Rust crates.io and Python PyPI publication closeout recorded
ethos-doc-core, ethos-verify, and ethos-pdf 0.3.0 are live on crates.io
ethos-pdf 0.3.0 is live on PyPI as the approved deterministic py3-none-any wheel
GitHub Release artifacts, npm publication, tags, install wording, and DocuShell integration remain blocked
```
