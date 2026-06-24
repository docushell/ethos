# Patch 0.1.1 Python PyPI Publication Approval Decision Validation - 2026-06-24

Validated source HEAD before this record: `d3c7db2`.

Patch 0.1.1 Python publication approval decision source commit:
`d3c7db24c8fac6cd9da627df76bde6df54dd46f9`.

Patch 0.1.1 Python publication approval decision source tree:
`90253df1cb04ef7c587138b3439bb1825d13a395`.

Status: **patch 0.1.1 Python PyPI publication approval decision recorded; operator upload remains pending**

This record accepts the exact patch `0.1.1` Python PyPI publication request packet after decider
approval. It approves only the bounded later operator action for the `ethos-pdf==0.1.1` wheel. It
does not upload any Python distribution, create package tags, change public wording, approve hosted
surfaces, approve production positioning, approve Windows packaged artifacts, approve bundled
project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or approve public
benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Python PyPI wheel publication
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/patch-0-1-1-python-publication-approval-request-validation-2026-06-24.md`
- Package source commit accepted by this decision: `16b2c189e1f23962dced921551cf6b4f9af4ba06`
- Package source tree accepted by this decision: `c76ba8525faaa63c53ac7f037d349a8ab4803fcb`

## Exact Decision Fields

- Decision: accept exact patch `0.1.1` Python PyPI wheel publication decision packet.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-24.
- Exact package accepted by this decision: `ethos-pdf==0.1.1`.
- Exact distribution accepted by this decision: `ethos_pdf-0.1.1-py3-none-any.whl` only.
- Exact source commit accepted by this decision: `16b2c189e1f23962dced921551cf6b4f9af4ba06`.
- Exact source tree accepted by this decision: `c76ba8525faaa63c53ac7f037d349a8ab4803fcb`.
- Exact wheel SHA256 accepted by this decision:
  `faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14`.

## Wheel Metadata Accepted By This Decision

- Name: `ethos-pdf`
- Version: `0.1.1`
- Summary: `Python wrapper for the Ethos document evidence CLI.`
- License-Expression: `Apache-2.0`
- Requires-Python: `>=3.8`
- Wheel-Version: `1.0`
- Root-Is-Purelib: `true`
- Tag: `py3-none-any`
- Import smoke accepted by this decision: version `0.1.1`, `EthosCli`, and `EthosCommandError`.
- PDFium boundary accepted by this decision: PDFium remains caller-provided through
  `ETHOS_PDFIUM_LIBRARY_PATH`.

## Approved Operator Action

After this decision record is merged and validation passes on merged source, an operator may upload
only this wheel:

```text
ethos_pdf-0.1.1-py3-none-any.whl
```

The operator must use a PyPI-approved authentication path and must not record credentials in the
repository. The operator must stop if the built wheel filename, SHA256, package version, source
commit, source tree, or retained blockers differ.

PyPI upload remains a separate operator action. This decision record does not upload any Python
distribution.

## Required Operator Pre-Upload Checks

Before uploading, the operator must run:

```sh
python3 -m build --wheel --outdir <candidate-dir>
shasum -a 256 <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
python3 .github/scripts/test_patch_0_1_1_python_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_1_python_publication_approval_request.py
python3 .github/scripts/test_python_public_api_policy.py
PYTHONPATH=python python3 -m unittest discover -s python/tests
make release-candidate-prep PYTHON=python3
git diff --check
```

## Explicit Exclusions

- Source distributions remain excluded.
- Alternate wheels remain excluded.
- Alternate Python package names remain excluded.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- Broader public wording remains blocked.

## Evidence Bound To This Decision

- Decider decision supplied: Approved; exact patch `0.1.1` Python PyPI publication request
  accepted.
- `python3 .github/scripts/test_patch_0_1_1_python_publication_approval_request.py` passed.
- `python3 .github/scripts/test_python_public_api_policy.py` passed.
- `PYTHONPATH=python python3 -m unittest discover -s python/tests` passed.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this decision branch.

## Non-Actions

- This decision record does not upload any Python distribution.
- This decision record does not approve an sdist.
- This decision record does not approve another wheel.
- This decision record does not approve package tags.
- This decision record does not approve public installation wording.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Retained Blockers

- Public installation wording remains blocked until PyPI availability is closed out.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Result

The exact patch `0.1.1` Python PyPI wheel publication decision packet for `ethos-pdf==0.1.1` is
accepted. Actual PyPI upload remains a separate operator action requiring final pre-upload checks,
PyPI-approved authentication, exact wheel hash verification, and later registry closeout evidence.
