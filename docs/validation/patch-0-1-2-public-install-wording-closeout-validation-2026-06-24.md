# Patch 0.1.2 Public Install Wording Closeout Validation - 2026-06-24

Validated source HEAD before this record: `37c294a`.

Patch 0.1.2 public install wording closeout source commit:
`37c294a2175bd4713df6a93464b90e6372a176d9`.

Patch 0.1.2 public install wording closeout source tree:
`648cd0cca2f04461fb3d6e04db6004590b75ede4`.

Status: **patch 0.1.2 public install wording recorded for published npm and CLI artifact surfaces**

This record closes only the bounded patch `0.1.2` public install wording lane after GitHub Release
artifact publication, npm vendor refresh, and npm publication closeout records were merged. It
updates public README and public claim-inventory wording for the surfaces that have `0.1.2`
publication evidence:

```sh
npm install -g @docushell/ethos-pdf@0.1.2
```

GitHub Release `v0.1.2` evaluation CLI archives for macOS arm64 and Linux x64 are also the current
public CLI artifact references.

Rust crate install commands remain on the published `0.1.1` crates.io baseline:

```sh
cargo add ethos-doc-core@0.1.1
cargo add ethos-verify@0.1.1
cargo add ethos-pdf@0.1.1
```

Python install commands remain on the published `0.1.1` PyPI baseline:

```sh
python3 -m pip install ethos-pdf==0.1.1
```

Rust crate and Python wheel `0.1.2` install wording require separate crates.io/PyPI `0.1.2`
publication closeout records before they can move.

## Public Wording

The current public README status sentence is:

> Ethos is a deterministic document evidence layer for source-grounded verification and citation
> checking across native Ethos JSON and supported foreign parser outputs. The current beta includes
> the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and
> `ethos-pdf` at `0.1.1`, the Python `ethos-pdf` wheel at `0.1.1`, the npm
> `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS arm64/Linux x64 CLI
> artifacts. PDFium-backed commands use caller-provided PDFium through
> `ETHOS_PDFIUM_LIBRARY_PATH`.

## Retained Blockers

- Rust crate `0.1.2` public install wording remains blocked until crates.io `0.1.2` publication
  closeout records pass.
- Python wheel `0.1.2` public install wording remains blocked until PyPI `0.1.2` publication
  closeout records pass.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Speed, footprint, parser-quality, table-quality, and production claims remain blocked.

## Verification Commands

```sh
python3 .github/scripts/test_patch_0_1_2_public_install_wording_closeout.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/public_boundary_claims_gate.py
python3 .github/scripts/claims_gate.py
make light-check PYTHON=python3
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

patch 0.1.2 public install wording closeout recorded
