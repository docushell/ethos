# Patch 0.1.2 Python PyPI Publication Approval Decision Validation - 2026-06-25

Validated source HEAD before this record: `a35ff66`.

Patch 0.1.2 Python publication approval decision source commit:
`a35ff66cbb7d04f4df4d7ac478edcd1f11ecbcdc`.

Patch 0.1.2 Python publication approval decision source tree:
`2deb30a01223fd9afc4291460cfd5578a3c3242c`.

Status: **patch 0.1.2 Python PyPI publication approval decision recorded; operator upload remains pending**

This record accepts the exact deterministic patch `0.1.2` Python PyPI publication request packet
after decider approval. It approves only the bounded later operator action for the
`ethos-pdf==0.1.2` wheel. It does not upload any Python distribution, create package tags, change
Python public installation wording, approve hosted surfaces, approve production positioning, approve
Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`,
approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Python PyPI deterministic wheel publication
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/patch-0-1-2-python-publication-approval-request-validation-2026-06-25.md`
- Package source commit accepted by this decision: `e431982cca2922d4cc59ddc7cacb9e72538b1cd0`
- Package source tree accepted by this decision: `f59ddd018d234eeee0ac77292b417f4acb892b4e`

## Exact Decision Fields

- Decision: accept exact deterministic patch `0.1.2` Python PyPI wheel publication decision packet.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-25.
- Exact package accepted by this decision: `ethos-pdf==0.1.2`.
- Exact distribution accepted by this decision: `ethos_pdf-0.1.2-py3-none-any.whl` only.
- Exact deterministic build input accepted by this decision: `SOURCE_DATE_EPOCH=0`.
- Exact source commit accepted by this decision: `e431982cca2922d4cc59ddc7cacb9e72538b1cd0`.
- Exact source tree accepted by this decision: `f59ddd018d234eeee0ac77292b417f4acb892b4e`.
- Exact deterministic wheel SHA256 accepted by this decision:
  `6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c`.

## Wheel Metadata Accepted By This Decision

- Name: `ethos-pdf`
- Version: `0.1.2`
- Summary: `Python wrapper for the Ethos document evidence CLI.`
- License-Expression: `Apache-2.0`
- Requires-Python: `>=3.8`
- Wheel-Version: `1.0`
- Root-Is-Purelib: `true`
- Tag: `py3-none-any`
- Build input: `SOURCE_DATE_EPOCH=0`
- Wheel member timestamps: `1980-01-01 00:00:00`
- Import smoke accepted by this decision: version `0.1.2`, `EthosCli`, and `EthosCommandError`.
- PDFium boundary accepted by this decision: PDFium remains caller-provided through
  `ETHOS_PDFIUM_LIBRARY_PATH`.

## Approved Operator Action

After this decision record is merged and validation passes on merged source, an operator may upload
only this wheel:

```text
ethos_pdf-0.1.2-py3-none-any.whl
```

The operator must build with `SOURCE_DATE_EPOCH=0`. The operator must use a PyPI-approved
authentication path and must not record credentials in the repository. The operator must stop if the
built wheel filename, SHA256, package version, source commit, source tree, deterministic build input,
or retained blockers differ.

PyPI upload remains a separate operator action. This decision record does not upload any Python
distribution.

## Required Operator Pre-Upload Checks

Before uploading, the operator must run:

```sh
SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir <candidate-dir>
shasum -a 256 <candidate-dir>/ethos_pdf-0.1.2-py3-none-any.whl
python3 .github/scripts/test_patch_0_1_2_python_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_python_publication_approval_request.py
python3 .github/scripts/test_python_public_api_policy.py
PYTHONPATH=python python3 -m unittest discover -s python/tests
make release-candidate-prep PYTHON=python3
git diff --check
```

## Explicit Exclusions

- Source distributions remain excluded.
- Alternate wheels remain excluded.
- Alternate Python package names remain excluded.
- Package tag creation remains blocked until a separate explicit approval or closeout record permits it.
- Python public installation wording remains blocked until PyPI availability is closed out.
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

- Decider decision supplied: Approved; exact deterministic patch `0.1.2` Python PyPI publication
  request accepted.
- `python3 .github/scripts/test_patch_0_1_2_python_publication_approval_request.py` passed.
- `python3 .github/scripts/test_release_candidate_prep.py` passed.
- `python3 .github/scripts/public_boundary_claims_gate.py` passed.
- `make light-check PYTHON=python3` passed on merged `main` before this decision branch.
- `make milestone-e-prep PYTHON=python3` passed on merged `main` before this decision branch.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this decision branch.

## Non-Actions

- This decision record does not upload any Python distribution.
- This decision record does not approve an sdist.
- This decision record does not approve another wheel.
- This decision record does not approve package tags.
- This decision record does not approve Python public installation wording.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Retained Blockers

- Actual PyPI upload remains pending operator action.
- Python public installation wording remains blocked until PyPI availability is closed out.
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

## Result

The exact deterministic patch `0.1.2` Python PyPI wheel publication decision packet for
`ethos-pdf==0.1.2` is accepted. Actual PyPI upload remains a separate operator action requiring
final pre-upload checks, PyPI-approved authentication, exact deterministic wheel hash verification,
and later registry closeout evidence.
