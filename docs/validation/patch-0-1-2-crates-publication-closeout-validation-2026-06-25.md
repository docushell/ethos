# Patch 0.1.2 crates.io Publication Closeout Validation - 2026-06-25

Validated source HEAD before this record: `35d0cca`.

Patch 0.1.2 crates publication closeout source commit: `35d0cca87669217f079793ce0553c9ac1121884b`.

Patch 0.1.2 crates publication closeout source tree: `3fcad87f2fc67c59c2f102f4f2c73d9e5c382724`.

Status: **patch 0.1.2 Rust crates published to crates.io**

This record closes the bounded patch `0.1.2` crates.io publication lane for `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf`. It records operator publish evidence and live crates.io
verification. It does not approve Rust crate public installation wording, PyPI publication, hosted
surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, or broader
public wording.

## Published Crates

- `ethos-doc-core = 0.1.2`
- `ethos-verify = 0.1.2`
- `ethos-pdf = 0.1.2`

## Operator Publish Evidence

`ethos-doc-core` command:

```text
cargo publish --locked -p ethos-doc-core
```

Observed result:

```text
Uploaded ethos-doc-core v0.1.2 to registry `crates-io`
Published ethos-doc-core v0.1.2 at registry `crates-io`
```

Registry visibility check:

```text
ethos-doc-core = "0.1.2"
```

`ethos-verify` command:

```text
cargo publish --locked -p ethos-verify
```

Observed result:

```text
Uploaded ethos-verify v0.1.2 to registry `crates-io`
Published ethos-verify v0.1.2 at registry `crates-io`
```

Registry visibility check:

```text
ethos-verify = "0.1.2"
```

`ethos-pdf` command:

```text
cargo publish --locked -p ethos-pdf
```

Observed result:

```text
Uploaded ethos-pdf v0.1.2 to registry `crates-io`
Published ethos-pdf v0.1.2 at registry `crates-io`
```

Registry visibility check:

```text
ethos-pdf = "0.1.2"
```

## Dependency-Order Evidence

- `ethos-doc-core` was published before dependent crates.
- `ethos-verify` was published after ethos-doc-core was visible on crates.io.
- `ethos-pdf` was published after ethos-verify was visible on crates.io.

## Retained Blockers

- Rust crate public installation wording remains blocked until a separate wording and availability record.
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
python3 .github/scripts/test_patch_0_1_2_crates_publication_closeout.py
python3 .github/scripts/test_patch_0_1_2_crates_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_crates_publication_approval_request.py
cargo search ethos-doc-core --limit 1
cargo search ethos-verify --limit 1
cargo search ethos-pdf --limit 1
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.2 Rust crates.io publication closeout recorded
ethos-doc-core, ethos-verify, and ethos-pdf 0.1.2 are live on crates.io
Rust crate public installation wording, PyPI, and unrelated public/support surfaces remain blocked
```
