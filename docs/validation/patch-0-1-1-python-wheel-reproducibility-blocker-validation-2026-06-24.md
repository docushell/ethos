# Patch 0.1.1 Python Wheel Reproducibility Blocker Validation - 2026-06-24

Validated source HEAD before this record: `5be31dd`.

Patch 0.1.1 Python wheel reproducibility blocker source commit:
`5be31dd292a0551caea457fd23db98045e110c00`.

Patch 0.1.1 Python wheel reproducibility blocker source tree:
`590dc80d27beaa9950a21f7f188650d2f24dd036`.

Status: **patch 0.1.1 Python PyPI upload remains blocked by wheel reproducibility evidence**

This record captures a pre-upload blocker discovered after the patch `0.1.1` Python PyPI
publication approval decision merged. The exact approved wheel filename was rebuilt before upload,
but the fresh wheel SHA256 did not match the approved candidate SHA256. PyPI upload remains blocked.

## Subject

- Repository: `docushell/ethos`
- Lane: Python PyPI wheel publication
- Approved decision record:
  `docs/validation/patch-0-1-1-python-publication-approval-decision-validation-2026-06-24.md`
- Approved request record:
  `docs/validation/patch-0-1-1-python-publication-approval-request-validation-2026-06-24.md`
- Candidate wheel: `ethos_pdf-0.1.1-py3-none-any.whl`

## Observed Hashes

- Approved wheel SHA256:
  `faa6c4751341b603b986ad3cf65d3c0c2f574e5df1d7232f76c3afd0221dac14`
- Fresh standard pre-upload rebuild SHA256:
  `52cc738637a84aa084b776db8be866e7af7438d580f3d564801a2ce94492a950`
- Rebuild with the original generated timestamp pinned SHA256:
  `ab84782cd7b7e7db2628f36e5d34e636afcddb9798196305203380a49b36b964`
- Deterministic rebuild SHA256 using `SOURCE_DATE_EPOCH=0`, first run:
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`
- Deterministic rebuild SHA256 using `SOURCE_DATE_EPOCH=0`, second run:
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`

## Root Cause Classification

- The approved wheel and the fresh standard pre-upload rebuild had the same filename and file size.
- The wheel member byte content was identical for every member.
- The generated `dist-info` ZIP member timestamps differed.
- The timestamp difference alone changed the whole-wheel SHA256.
- Setting `SOURCE_DATE_EPOCH=0` produced the same wheel SHA256 twice.

This is a packaging reproducibility blocker, not a Python API or wrapper behavior change.

## Required Follow-Up

- A new deterministic wheel approval request and approval decision are required before any PyPI
  upload.
- The next candidate should be built with `SOURCE_DATE_EPOCH=0`.
- The next approval request should bind the deterministic wheel SHA256:
  `e0292276e711e75d4f7e1bb8c2c6137c6e89d4c343dd308943eb9b22094ea451`.
- The prior merged approval decision remains useful as historical evidence but is not sufficient for
  upload because the required pre-upload rebuild produced a different wheel SHA256.

## Non-Actions

- This record does not approve PyPI upload.
- This record does not upload any Python distribution.
- This record does not approve the deterministic wheel hash.
- This record does not approve an sdist.
- This record does not approve another wheel.
- This record does not approve public installation wording.
- This record does not approve hosted surfaces.
- This record does not approve production positioning.
- This record does not approve Windows packaged artifacts.
- This record does not approve bundled project-maintained PDFium builds.
- This record does not approve public benchmark reports.
- This record does not approve public benchmark claims.
- This record does not approve `ethos-doc`.
- This record does not approve `ethos-rag`.

## Retained Blockers

- Actual PyPI upload remains blocked.
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

## Commands

```sh
python3 -m build --wheel --outdir <candidate-dir>
shasum -a 256 <candidate-dir>/ethos_pdf-0.1.1-py3-none-any.whl
env SOURCE_DATE_EPOCH=0 python3 -m build --wheel --outdir <candidate-dir>
python3 .github/scripts/test_patch_0_1_1_python_wheel_reproducibility_blocker.py
python3 .github/scripts/test_patch_0_1_1_python_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_1_python_publication_approval_request.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.1 Python wheel reproducibility blocker recorded
Pre-upload PyPI upload is stopped because the fresh standard wheel rebuild did not match the approved SHA256
Deterministic SOURCE_DATE_EPOCH=0 rebuild evidence is available for a new approval request
```
