# Patch 0.1.1 Python Deterministic Wheel Approval Decision Validation - 2026-06-24

Validated source HEAD before this record: `0c8ffe7`.

Patch 0.1.1 Python deterministic wheel approval decision source commit:
`0c8ffe7db3b83896ab0be1c106bd1ec7de3cb278`.

Patch 0.1.1 Python deterministic wheel approval decision source tree:
`44376507f98789401efae7b9cf0ab97ca3b78980`.

Status: **patch 0.1.1 Python deterministic wheel approval decision recorded; operator upload remains pending**

This record accepts the exact patch `0.1.1` deterministic Python PyPI publication request packet
after decider approval. It approves only the bounded later operator action for the
`SOURCE_DATE_EPOCH=0` `ethos-pdf==0.1.1` wheel. It does not upload any Python distribution, create
package tags, change public wording, approve hosted surfaces, approve production positioning,
approve Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve
`ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Python PyPI deterministic wheel publication
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/patch-0-1-1-python-deterministic-wheel-approval-request-validation-2026-06-24.md`
- Deterministic package source commit accepted by this decision:
  `d3e3953b99fbc74669f82ee56b753de7db6e63e4`
- Deterministic package source tree accepted by this decision:
  `8920cbc9bc6ae05ec0c417533513637eda12658d`

## Exact Decision Fields

- Decision: accept exact patch `0.1.1` deterministic Python PyPI wheel publication decision packet.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-24.
- Exact package accepted by this decision: `ethos-pdf==0.1.1`.
- Exact distribution accepted by this decision: `ethos_pdf-0.1.1-py3-none-any.whl` only.
- Exact deterministic build input accepted by this decision: `SOURCE_DATE_EPOCH=0`.
- Exact source commit accepted by this decision: `d3e3953b99fbc74669f82ee56b753de7db6e63e4`.
- Exact source tree accepted by this decision: `8920cbc9bc6ae05ec0c417533513637eda12658d`.
- Exact deterministic wheel SHA256 accepted by this decision:
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`.

## Superseded Hash Context

- Prior timestamp-sensitive approved wheel SHA256:
  `faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14`
- Fresh standard pre-upload rebuild SHA256:
  `52cc738637a84aa084b776db8be866e7af7438d580f3d564801a2ce94492a950`
- The approved deterministic request packet classified the difference as generated ZIP timestamp
  drift with identical wheel member bytes.

## Wheel Metadata Accepted By This Decision

- Name: `ethos-pdf`
- Version: `0.1.1`
- Summary: `Python wrapper for the Ethos document evidence CLI.`
- License-Expression: `Apache-2.0`
- Requires-Python: `>=3.8`
- Wheel-Version: `1.0`
- Root-Is-Purelib: `true`
- Tag: `py3-none-any`
- Wheel member timestamps: `1980-01-01 00:00:00`
- Import smoke accepted by this decision: version `0.1.1`, `EthosCli`, and `EthosCommandError`.
- PDFium boundary accepted by this decision: PDFium remains caller-provided through
  `ETHOS_PDFIUM_LIBRARY_PATH`.

## Approved Operator Action

After this decision record is merged and validation passes on merged source, an operator may upload
only this deterministic wheel:

```text
ethos_pdf-0.1.1-py3-none-any.whl
```

The operator must set `SOURCE_DATE_EPOCH=0` before building the wheel for upload. The operator must
use a PyPI-approved authentication path and must not record credentials in the repository. The
operator must stop if the built wheel filename, SHA256, package version, source commit, source
tree, deterministic build input, or retained blockers differ.

PyPI upload remains a separate operator action. This decision record does not upload any Python
distribution.

## Required Operator Pre-Upload Checks

Before uploading, the operator must run:

```sh
SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir <candidate-dir>
shasum -a 256 <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
python3 .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_decision.py
python3 .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_request.py
python3 .github/scripts/test_patch_0_1_1_python_wheel_reproducibility_blocker.py
python3 .github/scripts/test_python_public_api_policy.py
PYTHONPATH=python python3 -m unittest discover -s python/tests
make release-candidate-prep PYTHON=python3
git diff --check
```

## Explicit Exclusions

- Source distributions remain excluded.
- Alternate wheels remain excluded.
- Alternate Python package names remain excluded.
- Package tags remain excluded.
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

- Decider decision supplied: Approved; create the patch `0.1.1` Python PyPI publication approval
  decision record for the exact deterministic `ethos-pdf==0.1.1` wheel candidate in the merged
  approval-request record.
- `python3 .github/scripts/test_patch_0_1_1_python_deterministic_wheel_approval_request.py`
  passed on merged `main`.
- `python3 .github/scripts/test_patch_0_1_1_python_wheel_reproducibility_blocker.py` passed on
  merged `main`.
- `python3 .github/scripts/test_python_public_api_policy.py` passed on merged `main`.
- `PYTHONPATH=python python3 -m unittest discover -s python/tests` passed on merged `main`.
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

The exact patch `0.1.1` deterministic Python PyPI wheel publication decision packet for
`ethos-pdf==0.1.1` is accepted. Actual PyPI upload remains a separate operator action requiring
final pre-upload checks, PyPI-approved authentication, exact deterministic wheel hash verification,
and later registry closeout evidence.
