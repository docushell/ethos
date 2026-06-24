# Patch 0.1.1 crates.io Publication Closeout Validation - 2026-06-24

Validated source HEAD before this record: `7bc50f0`.

Patch 0.1.1 crates publication closeout source commit: `7bc50f09f6ce0385737e9b978dcb249f161195b0`.

Patch 0.1.1 crates publication closeout source tree: `88bc7969652d56c534c5a101824926a8e9bbb4d0`.

Status: **patch 0.1.1 Rust crates published to crates.io**

This record closes the bounded patch `0.1.1` crates.io publication lane for `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf`. It records operator publish evidence and live crates.io
verification. It does not approve hosted surfaces, production positioning, Windows packaged
artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark
reports, public benchmark claims, or broader public wording.

## Published Crates

- `ethos-doc-core = 0.1.1`
- `ethos-verify = 0.1.1`
- `ethos-pdf = 0.1.1`

## Operator Publish Evidence

`ethos-doc-core` command:

```text
cargo publish --locked -p ethos-doc-core
```

Observed result:

```text
Uploaded ethos-doc-core v0.1.1 to registry `crates-io`
Published ethos-doc-core v0.1.1 at registry `crates-io`
```

Registry visibility check:

```text
ethos-doc-core = "0.1.1"
```

`ethos-verify` command:

```text
cargo publish --locked -p ethos-verify
```

Observed result:

```text
Uploaded ethos-verify v0.1.1 to registry `crates-io`
Published ethos-verify v0.1.1 at registry `crates-io`
```

Registry visibility check:

```text
ethos-verify = "0.1.1"
```

`ethos-pdf` command:

```text
cargo publish --locked -p ethos-pdf
```

Observed result:

```text
Uploaded ethos-pdf v0.1.1 to registry `crates-io`
Published ethos-pdf v0.1.1 at registry `crates-io`
```

Registry visibility check:

```text
ethos-pdf = "0.1.1"
```

## Dependency-Order Evidence

- `ethos-doc-core` was published before dependent crates.
- `ethos-verify` was published after ethos-doc-core was visible on crates.io.
- `ethos-pdf` was published after ethos-doc-core was visible on crates.io.

## Retained Blockers

- Public installation wording remains blocked until a separate wording and availability record.
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
python3 .github/scripts/test_patch_0_1_1_crates_publication_closeout.py
python3 .github/scripts/test_patch_0_1_1_crates_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_1_crates_publication_approval_request.py
cargo search ethos-doc-core --limit 1
cargo search ethos-verify --limit 1
cargo search ethos-pdf --limit 1
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.1 Rust crates.io publication closeout recorded
ethos-doc-core, ethos-verify, and ethos-pdf 0.1.1 are live on crates.io
Public installation wording and unrelated public/support surfaces remain blocked
```
