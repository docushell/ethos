# Patch 0.1.2 Python Public Install Wording Closeout Validation - 2026-06-25

Validated source HEAD before this record: `67b499b`.

Patch 0.1.2 Python public install wording closeout source commit:
`67b499bd68e1c060fb52e2b41f221c2895d16847`.

Patch 0.1.2 Python public install wording closeout source tree:
`79e8bf0a145ee3e7bc7021c90fd0f1e1eb91880f`.

Status: **patch 0.1.2 Python public install wording recorded**

This record closes only the bounded patch `0.1.2` Python public install wording lane after PyPI
publication closeout for `ethos-pdf==0.1.2`. It updates public README, Python package docs, and
public claim-inventory wording for the published Python wheel. It does not approve package tag
creation, hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public
benchmark claims, or broader public wording.

## Public Install Wording

Python package installation now points to the published `0.1.2` PyPI wheel:

```sh
python3 -m pip install ethos-pdf==0.1.2
```

The current public README sentence is:

```text
Ethos is a deterministic document evidence layer for source-grounded verification and citation checking across native Ethos JSON and supported foreign parser outputs. The current beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`, the Python `ethos-pdf` wheel at `0.1.2`, the npm `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS arm64/Linux x64 CLI artifacts. PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.
```

## Published Surface Binding

- PyPI closeout record:
  `docs/validation/patch-0-1-2-python-publication-closeout-validation-2026-06-25.md`
- Exact package: `ethos-pdf==0.1.2`
- Exact wheel: `ethos_pdf-0.1.2-py3-none-any.whl`
- Exact wheel SHA256:
  `6f17240954f1257ece3c762c820ad771ccb114353bfb699fe87f418a5ceb663c`
- Python docs remain explicit that the package is a thin wrapper around a caller-provided local
  `ethos` CLI binary and does not bundle the CLI or PDFium.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Retained Blockers

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
python3 .github/scripts/test_patch_0_1_2_python_public_install_wording_closeout.py
python3 .github/scripts/test_patch_0_1_2_python_publication_closeout.py
python3 .github/scripts/test_public_prealpha_wording_approval.py
python3 .github/scripts/test_execution_status.py
python3 .github/scripts/public_boundary_claims_gate.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 Python public install wording closeout recorded
Public README, Python package docs, and public claim inventory now point Python install wording to ethos-pdf==0.1.2
Remaining blocked surfaces stay blocked
```
