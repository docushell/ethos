# Patch 0.1.1 Python PyPI Publication Approval Request Validation - 2026-06-24

Validated source HEAD before this record: `16b2c18`.

Patch 0.1.1 Python publication approval request source commit:
`16b2c189e1f23962dced921551cf6b4f9af4ba06`.

Patch 0.1.1 Python publication approval request source tree:
`c76ba8525faaa63c53ac7f037d349a8ab4803fcb`.

Status: **patch 0.1.1 Python PyPI publication approval request recorded; PyPI upload remains blocked**

This record requests decider review for publishing exactly the patch `0.1.1` Ethos Python wheel to
PyPI. It does not approve or perform PyPI upload, create package tags, change public wording,
approve hosted surfaces, approve production positioning, approve Windows packaged artifacts,
approve bundled project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or
approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Python PyPI wheel publication
- Package source commit: `16b2c189e1f23962dced921551cf6b4f9af4ba06`
- Package source tree: `c76ba8525faaa63c53ac7f037d349a8ab4803fcb`
- Candidate package: `ethos-pdf==0.1.1`
- Import package: `ethos_pdf`
- Candidate wheel: `ethos_pdf-0.1.1-py3-none-any.whl`
- Candidate wheel SHA256: `faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14`

## Exact Request Fields

- Decision requested: approve exact patch `0.1.1` Python PyPI wheel publication preparation inputs
  for later operator execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-06-24.
- Exact package requested: `ethos-pdf==0.1.1`.
- Exact distribution requested: `ethos_pdf-0.1.1-py3-none-any.whl` only.
- Exact source commit requested: `16b2c189e1f23962dced921551cf6b4f9af4ba06`.
- Exact source tree requested: `c76ba8525faaa63c53ac7f037d349a8ab4803fcb`.
- Exact wheel SHA256 requested:
  `faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14`.

## Wheel Metadata Bound To This Request

- Name: `ethos-pdf`
- Version: `0.1.1`
- Summary: `Python wrapper for the Ethos document evidence CLI.`
- License-Expression: `Apache-2.0`
- Requires-Python: `>=3.8`
- Wheel-Version: `1.0`
- Root-Is-Purelib: `true`
- Tag: `py3-none-any`
- Build Python: Python `3.9.6`
- Build frontend: build `1.4.4`

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

- `python3 -m build --wheel --outdir <candidate-dir>` built
  `ethos_pdf-0.1.1-py3-none-any.whl` in an isolated build environment.
- Wheel SHA256 verification reported
  `faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14`.
- Wheel metadata inspection reported `Name: ethos-pdf`, `Version: 0.1.1`,
  `License-Expression: Apache-2.0`, `Requires-Python: >=3.8`, and `Tag: py3-none-any`.
- Local install smoke used `python3 -m pip install --no-deps --force-reinstall <candidate-wheel>`.
- Import smoke reported version `0.1.1`.
- Import smoke resolved `EthosCli`.
- Import smoke resolved `EthosCommandError`.

## Manual Decision Gate

Manual action is required before any PyPI upload. A decider must accept or reject this exact request
packet. Only after that decision record passes may an operator upload the exact wheel named above
with the exact SHA256 named above.

This request does not select an sdist, alternate wheel, additional package name, additional Python
module, or broad package-publication class. If any artifact filename, version, hash, source commit,
source tree, metadata, public wording, or blocker set changes, this request must be replaced by a
new evidence record and a new decider review.

## Non-Approvals

- This request record does not approve PyPI upload.
- This request record does not upload any Python distribution.
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
- Public installation wording remains blocked pending explicit decider approval.
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
python3 -m build --wheel --outdir <candidate-dir>
shasum -a 256 <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
python3 .github/scripts/test_patch_0_1_1_python_publication_approval_request.py
python3 .github/scripts/test_python_public_api_policy.py
PYTHONPATH=python python3 -m unittest discover -s python/tests
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.1 Python PyPI publication approval request recorded
Exact wheel, source binding, metadata, SHA256, local install/import smoke, and retained blockers were recorded
PyPI upload remains blocked pending explicit decider approval and later operator action
```
