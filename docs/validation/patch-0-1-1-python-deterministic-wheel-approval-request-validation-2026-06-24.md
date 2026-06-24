# Patch 0.1.1 Python Deterministic Wheel Approval Request Validation - 2026-06-24

Validated source HEAD before this record: `d3e3953`.

Patch 0.1.1 Python deterministic wheel approval request source commit:
`d3e3953b99fbc74669f82ee56b753de7db6e63e4`.

Patch 0.1.1 Python deterministic wheel approval request source tree:
`8920cbc9bc6ae05ec0c417533513637eda12658d`.

Status: **patch 0.1.1 Python deterministic wheel approval request recorded; PyPI upload remains blocked**

This record requests decider review for publishing exactly the deterministic patch `0.1.1` Ethos
Python wheel to PyPI. It replaces the timestamp-sensitive wheel hash from the prior request with a
wheel built using `SOURCE_DATE_EPOCH=0`. It does not approve or perform PyPI upload, create package
tags, change public wording, approve hosted surfaces, approve production positioning, approve
Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`,
approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Python PyPI deterministic wheel publication
- Prior blocker record:
  `docs/validation/patch-0-1-1-python-wheel-reproducibility-blocker-validation-2026-06-24.md`
- Candidate package: `ethos-pdf==0.1.1`
- Import package: `ethos_pdf`
- Candidate wheel: `ethos_pdf-0.1.1-py3-none-any.whl`
- Deterministic build input: `SOURCE_DATE_EPOCH=0`
- Deterministic candidate wheel SHA256:
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`

## Superseded Hash Context

- Prior timestamp-sensitive approved wheel SHA256:
  `faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14`
- Fresh standard pre-upload rebuild SHA256:
  `52cc738637a84aa084b776db8be866e7af7438d580f3d564801a2ce94492a950`
- The blocker record classified the difference as generated ZIP timestamp drift with identical
  wheel member bytes.

## Exact Request Fields

- Decision requested: approve exact deterministic patch `0.1.1` Python PyPI wheel publication
  preparation inputs for later operator execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-06-24.
- Exact package requested: `ethos-pdf==0.1.1`.
- Exact distribution requested: `ethos_pdf-0.1.1-py3-none-any.whl` only.
- Exact deterministic build input requested: `SOURCE_DATE_EPOCH=0`.
- Exact source commit requested: `d3e3953b99fbc74669f82ee56b753de7db6e63e4`.
- Exact source tree requested: `8920cbc9bc6ae05ec0c417533513637eda12658d`.
- Exact deterministic wheel SHA256 requested:
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`.

## Wheel Metadata Bound To This Request

- Name: `ethos-pdf`
- Version: `0.1.1`
- Summary: `Python wrapper for the Ethos document evidence CLI.`
- License-Expression: `Apache-2.0`
- Requires-Python: `>=3.8`
- Wheel-Version: `1.0`
- Root-Is-Purelib: `true`
- Tag: `py3-none-any`
- Wheel member timestamps: `1980-01-01 00:00:00`

Wheel file list:

- `ethos_pdf/__init__.py`
- `ethos_pdf/_cli.py`
- `ethos_pdf-0.1.1.dist-info/METADATA`
- `ethos_pdf-0.1.1.dist-info/RECORD`
- `ethos_pdf-0.1.1.dist-info/WHEEL`
- `ethos_pdf-0.1.1.dist-info/licenses/LICENSE`
- `ethos_pdf-0.1.1.dist-info/licenses/NOTICE`
- `ethos_pdf-0.1.1.dist-info/top_level.txt`

## Local Evidence Bound To This Request

- `SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir <candidate-dir>` built
  `ethos_pdf-0.1.1-py3-none-any.whl` twice in isolated build environments.
- Both deterministic builds produced SHA256
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`.
- Wheel metadata inspection reported `Name: ethos-pdf`, `Version: 0.1.1`,
  `License-Expression: Apache-2.0`, `Requires-Python: >=3.8`, and `Tag: py3-none-any`.
- Wheel ZIP member timestamp inspection reported `1980-01-01 00:00:00` for every member.
- Local install smoke used `python3 -m pip install --no-deps --force-reinstall <candidate-wheel>`.
- Import smoke reported version `0.1.1`.
- Import smoke resolved `EthosCli`.
- Import smoke resolved `EthosCommandError`.

## Manual Decision Gate

Manual action is required before any PyPI upload. A decider must accept or reject this exact
deterministic request packet. Only after that decision record passes may an operator upload the
exact deterministic wheel named above with the exact SHA256 named above.

This request does not select an sdist, alternate wheel, additional package name, additional Python
module, or broad package-publication class. If any artifact filename, version, hash, source commit,
source tree, metadata, build input, public wording, or blocker set changes, this request must be
replaced by a new evidence record and a new decider review.

## Non-Approvals

- This request record does not approve PyPI upload.
- This request record does not upload any Python distribution.
- This request record does not approve the deterministic wheel hash.
- This request record does not approve an sdist.
- This request record does not approve another wheel.
- This request record does not approve package tags.
- This request record does not approve public installation wording.
- This request record does not approve hosted surfaces.
- This request record does not approve production positioning.
- This request record does not approve Windows packaged artifacts.
- This request record does not approve bundled project-maintained PDFium builds.
- This request record does not approve public benchmark reports.
- This request record does not approve public benchmark claims.
- This request record does not approve `ethos-doc`.
- This request record does not approve `ethos-rag`.

## Retained Blockers

- Actual PyPI upload remains blocked pending explicit decider approval.
- Public installation wording remains blocked pending PyPI availability closeout.
- Package tag creation remains blocked pending explicit decider approval.
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
python3 .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_request.py
python3 .github/scripts/test_patch_0_1_1_python_wheel_reproducibility_blocker.py
python3 .github/scripts/test_python_public_api_policy.py
PYTHONPATH=python python3 -m unittest discover -s python/tests
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.1 Python deterministic wheel approval request recorded
Exact deterministic wheel, build input, source binding, metadata, SHA256, local install/import smoke, and retained blockers were recorded
PyPI upload remains blocked pending explicit decider approval and later operator action
```
