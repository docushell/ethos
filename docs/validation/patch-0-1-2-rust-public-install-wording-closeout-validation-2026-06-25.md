# Patch 0.1.2 Rust Public Install Wording Closeout Validation - 2026-06-25

Validated source HEAD before this record: `5ca6e23`.

Patch 0.1.2 Rust public install wording closeout source commit: `5ca6e237bd12656f894c7a1d70fe57c7385a7c95`.

Patch 0.1.2 Rust public install wording closeout source tree: `9d0f629bdfb89ae191d971ee4ec9f323a61fba84`.

Status: **patch 0.1.2 Rust public install wording recorded**

This record closes only the bounded patch `0.1.2` Rust public install wording lane after crates.io
publication closeout for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`. It does not approve
Python PyPI `0.1.2` publication, hosted surfaces, production positioning, Windows packaged
artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark
reports, public benchmark claims, or broader public wording.

## Public README Install Wording

Rust crate installation now points to the published `0.1.2` crates:

```sh
cargo add ethos-doc-core@0.1.2
cargo add ethos-verify@0.1.2
cargo add ethos-pdf@0.1.2
```

The current public README sentence is:

```text
Ethos is a deterministic document evidence layer for source-grounded verification and citation checking across native Ethos JSON and supported foreign parser outputs. The current beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`, the Python `ethos-pdf` wheel at `0.1.1`, the npm `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS arm64/Linux x64 CLI artifacts. PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.
```

## Retained Blockers

- Python installation remains at `ethos-pdf==0.1.1` until separate PyPI `0.1.2` publication
  records pass.
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
python3 .github/scripts/test_patch_0_1_2_rust_public_install_wording_closeout.py
python3 .github/scripts/test_patch_0_1_2_public_install_wording_closeout.py
python3 .github/scripts/test_patch_0_1_2_crates_publication_closeout.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/public_boundary_claims_gate.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 Rust public install wording closeout recorded
README and public boundary claims now point Rust crate installation to 0.1.2
Python PyPI, hosted, production, Windows, bundled PDFium, benchmark, ethos-doc, and ethos-rag surfaces remain blocked
```
