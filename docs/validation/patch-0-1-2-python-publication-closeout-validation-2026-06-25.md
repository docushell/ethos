# Patch 0.1.2 Python PyPI Publication Closeout Validation - 2026-06-25

Validated source HEAD before this record: `26012eb`.

Patch 0.1.2 Python publication closeout source commit:
`26012ebfaf9a50e02c12515827f63c21e6a69ca6`.

Patch 0.1.2 Python publication closeout source tree:
`a178affbdf5a0f46d52aa80c804b1142688f4a82`.

Status: **patch 0.1.2 Python PyPI wheel published**

This record closes the bounded patch `0.1.2` Python PyPI publication lane for
`ethos-pdf==0.1.2`. It records operator upload evidence and live PyPI registry verification for the
exact approved deterministic wheel. It does not approve Python public installation wording, package
tag creation, hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public
benchmark claims, or broader public wording.

## Published Package

- Package: `ethos-pdf`
- Version: `0.1.2`
- Import package: `ethos_pdf`
- Registry: `https://pypi.org/`
- Project URL: `https://pypi.org/project/ethos-pdf/0.1.2/`
- Distribution: `ethos_pdf-0.1.2-py3-none-any.whl`
- Deterministic build input: `SOURCE_DATE_EPOCH=0`
- SHA256:
  `6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c`

## Operator Upload Evidence

Pre-upload checks:

```text
shasum -a 256 target/python-pypi-0.1.2/ethos_pdf-0.1.2-py3-none-any.whl
6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c  target/python-pypi-0.1.2/ethos_pdf-0.1.2-py3-none-any.whl
python3 .github/scripts/test_patch_0_1_2_python_publication_approval_decision.py
Ran 4 tests in 0.085s
OK
python3 .github/scripts/test_patch_0_1_2_python_publication_approval_request.py
Ran 5 tests in 0.053s
OK
python3 .github/scripts/test_python_public_api_policy.py
Ran 4 tests in 0.001s
OK
PYTHONPATH=python python3 -m unittest discover -s python/tests
Ran 23 tests in 3.912s
OK
make release-candidate-prep PYTHON=python3
git diff --check
```

Upload command:

```text
python3 -m twine upload target/python-pypi-0.1.2/ethos_pdf-0.1.2-py3-none-any.whl
```

Observed upload result:

```text
Uploading distributions to https://upload.pypi.org/legacy/
WARNING This environment is not supported for trusted publishing
Uploading ethos_pdf-0.1.2-py3-none-any.whl
100% 17.0/17.0 kB
View at: https://pypi.org/project/ethos-pdf/0.1.2/
```

The upload used a PyPI-approved credential path. No credential is recorded in this repository.

## Registry Verification

Registry endpoint:

```text
https://pypi.org/pypi/ethos-pdf/0.1.2/json
```

Result:

```text
name: ethos-pdf
version: 0.1.2
requires_python: >=3.8
filename: ethos_pdf-0.1.2-py3-none-any.whl
packagetype: bdist_wheel
python_version: py3
digests.sha256: 6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c
size: 11445
upload_time_iso_8601: 2026-06-25T05:06:17.574879Z
yanked: false
url: https://files.pythonhosted.org/packages/32/0f/06fe9ab696ee596cc88f9b061b5c2b9f443fe7fcdc54ebb02a4189dda129/ethos_pdf-0.1.2-py3-none-any.whl
```

## Approved Candidate Binding

- Approval request record:
  `docs/validation/patch-0-1-2-python-publication-approval-request-validation-2026-06-25.md`
- Approval decision record:
  `docs/validation/patch-0-1-2-python-publication-approval-decision-validation-2026-06-25.md`
- Package source commit: `e431982cca2922d4cc59ddc7cacb9e72538b1cd0`
- Package source tree: `f59ddd018d234eeee0ac77292b417f4acb892b4e`
- Exact deterministic build input: `SOURCE_DATE_EPOCH=0`
- Exact wheel: `ethos_pdf-0.1.2-py3-none-any.whl`
- Exact wheel SHA256:
  `6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c`
- Wheel metadata: `Name: ethos-pdf`, `Version: 0.1.2`, `Requires-Python: >=3.8`,
  `Wheel-Version: 1.0`, `Root-Is-Purelib: true`, `Tag: py3-none-any`.

## Retained Blockers

- Public installation wording may be updated only in a separate bounded docs lane.
- Package tag creation remains blocked until a separate explicit approval or closeout record permits it.
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
SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir target/python-pypi-0.1.2
shasum -a 256 target/python-pypi-0.1.2/ethos_pdf-0.1.2-py3-none-any.whl
python3 .github/scripts/test_patch_0_1_2_python_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_python_publication_approval_request.py
python3 .github/scripts/test_python_public_api_policy.py
PYTHONPATH=python python3 -m unittest discover -s python/tests
make release-candidate-prep PYTHON=python3
python3 -m twine upload target/python-pypi-0.1.2/ethos_pdf-0.1.2-py3-none-any.whl
python3 .github/scripts/test_patch_0_1_2_python_publication_closeout.py
git diff --check
```

## Result

```text
patch 0.1.2 Python PyPI publication closeout recorded
ethos-pdf 0.1.2 is live on PyPI as the approved deterministic py3-none-any wheel
Public installation wording must still be handled in a separate bounded docs lane
```
