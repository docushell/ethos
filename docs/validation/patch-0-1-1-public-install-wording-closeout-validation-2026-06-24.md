# Patch 0.1.1 Public Installation Wording Closeout Validation - 2026-06-24

Validated source HEAD before this record: `4a573dc`.

Patch 0.1.1 public install wording closeout source commit:
`4a573dc96175cf10b90b8e6928e2c2408cb763e3`.

Patch 0.1.1 public install wording closeout source tree:
`71c874291b17d92d641470f01d2dedaf8a48d8ea`.

Status: **patch 0.1.1 public installation wording recorded for published evaluation surfaces**

This record closes the bounded patch `0.1.1` public installation wording lane after CLI artifact,
Rust crates.io, npm, and Python PyPI publication closeout records were merged. It updates install
wording for the already-published evaluation surfaces only. It does not approve hosted surfaces,
production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds,
`ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, speed claims,
footprint claims, parser-quality claims, table-quality claims, or production claims.

## Approved Install Wording

README install wording now includes:

```text
cargo add ethos-doc-core@0.1.1
cargo add ethos-verify@0.1.1
cargo add ethos-pdf@0.1.1
python3 -m pip install ethos-pdf==0.1.1
npm install -g @docushell/ethos-pdf@0.1.1
GitHub Release v0.1.1 evaluation CLI archives for macOS arm64 and Linux x64
```

The Python wording is explicitly bounded:

```text
The Python wheel is a thin wrapper around a caller-provided local ethos CLI binary.
It does not bundle the CLI or PDFium.
PDFium-backed commands still require ETHOS_PDFIUM_LIBRARY_PATH.
```

## Files In Scope

- `README.md`
- `python/README.md`
- `python/QUICKSTART.md`
- `docs/public-boundary-claims.json`
- `docs/validation/README.md`
- `CHANGELOG.md`

## Non-Approvals

- This record does not approve hosted surfaces.
- This record does not approve production positioning.
- This record does not approve Windows packaged artifacts.
- This record does not approve bundled project-maintained PDFium builds.
- This record does not approve public benchmark reports.
- This record does not approve public benchmark claims.
- This record does not approve speed claims.
- This record does not approve footprint claims.
- This record does not approve parser-quality claims.
- This record does not approve table-quality claims.
- This record does not approve `ethos-doc`.
- This record does not approve `ethos-rag`.

## Retained Boundaries

- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.
- The Python wheel remains a wrapper around a caller-provided local `ethos` CLI binary.

## Commands

```sh
python3 .github/scripts/test_patch_0_1_1_public_install_wording_closeout.py
python3 .github/scripts/public_boundary_claims_gate.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/test_public_surface_posture.py
make light-check PYTHON=python3
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.1 public installation wording closeout recorded
published evaluation install paths are documented without changing retained support boundaries
```
