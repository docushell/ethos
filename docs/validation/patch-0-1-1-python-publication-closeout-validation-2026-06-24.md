# Patch 0.1.1 Python PyPI Publication Closeout Validation - 2026-06-24

Validated source HEAD before this record: `2cab87d`.

Patch 0.1.1 Python publication closeout source commit:
`2cab87df30443cb8e1c32489adc9b3123cac455f`.

Patch 0.1.1 Python publication closeout source tree:
`ae58f8fcdd7a3c60c68e96cb39259a2eb37350bc`.

Status: **patch 0.1.1 Python PyPI wheel published**

This record closes the bounded patch `0.1.1` Python PyPI publication lane for
`ethos-pdf==0.1.1`. It records operator upload evidence and live PyPI registry verification for the
exact approved deterministic wheel. It does not approve hosted surfaces, production positioning,
Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`,
public benchmark reports, public benchmark claims, or broader public wording.

## Published Package

- Package: `ethos-pdf`
- Version: `0.1.1`
- Import package: `ethos_pdf`
- Registry: `https://pypi.org/`
- Project URL: `https://pypi.org/project/ethos-pdf/0.1.1/`
- Distribution: `ethos_pdf-0.1.1-py3-none-any.whl`
- Deterministic build input: `SOURCE_DATE_EPOCH=0`
- SHA256:
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`

## Operator Upload Evidence

Pre-upload check:

```text
python3 -m twine check <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
PASSED
```

Upload command:

```text
python3 -m twine upload <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
```

Observed upload result:

```text
Uploading distributions to https://upload.pypi.org/legacy/
WARNING This environment is not supported for trusted publishing
Uploading ethos_pdf-0.1.1-py3-none-any.whl
View at: https://pypi.org/project/ethos-pdf/0.1.1/
```

The upload used a PyPI-approved credential path. No credential is recorded in this repository.

## Registry Verification

Registry endpoint:

```text
https://pypi.org/pypi/ethos-pdf/0.1.1/json
```

Result:

```text
name: ethos-pdf
version: 0.1.1
requires_python: >=3.8
filename: ethos_pdf-0.1.1-py3-none-any.whl
packagetype: bdist_wheel
python_version: py3
digests.sha256: e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451
size: 11398
upload_time_iso_8601: 2026-06-24T06:15:17.128860Z
yanked: false
url: https://files.pythonhosted.org/packages/3d/c2/406c298e37fca7617c97ff9d74a30ab0a017a22f6025c8f2b74c25b5b39c/ethos_pdf-0.1.1-py3-none-any.whl
```

## Approved Candidate Binding

- Approval request record:
  `docs/validation/patch-0-1-1-python-deterministic-wheel-approval-request-validation-2026-06-24.md`
- Approval decision record:
  `docs/validation/patch-0-1-1-python-deterministic-wheel-approval-decision-validation-2026-06-24.md`
- Exact deterministic source commit:
  `d3e3953b99fbc74669f82ee56b753de7db6e63e4`
- Exact deterministic source tree:
  `8920cbc9bc6ae05ec0c417533513637eda12658d`
- Exact deterministic build input: `SOURCE_DATE_EPOCH=0`
- Exact wheel: `ethos_pdf-0.1.1-py3-none-any.whl`
- Exact wheel SHA256:
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`
- Wheel metadata: `Name: ethos-pdf`, `Version: 0.1.1`, `Requires-Python: >=3.8`,
  `Wheel-Version: 1.0`, `Root-Is-Purelib: true`, `Tag: py3-none-any`.

## Retained Blockers

- Public installation wording may be updated only in a separate bounded docs lane.
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
SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir <candidate-dir>
shasum -a 256 <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
python3 -m twine check <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
python3 -m twine upload <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
python3 .github/scripts/test_patch_0_1_1_python_publication_closeout.py
python3 .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_decision.py
python3 .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_request.py
python3 .github/scripts/test_python_public_api_policy.py
PYTHONPATH=python python3 -m unittest discover -s python/tests
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.1 Python PyPI publication closeout recorded
ethos-pdf 0.1.1 is live on PyPI as the approved deterministic py3-none-any wheel
Public installation wording must still be handled in a separate bounded docs lane
```
