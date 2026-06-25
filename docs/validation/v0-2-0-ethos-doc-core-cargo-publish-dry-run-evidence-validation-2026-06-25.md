# v0.2.0 ethos-doc-core Cargo Publish Dry-Run Evidence Validation - 2026-06-25

Validated source HEAD before this record: `9ca0147`.

v0.2.0 ethos-doc-core dry-run source commit:
`9ca01477a14b9addd542e7aa9c5217a1b1df6831`.

v0.2.0 ethos-doc-core dry-run source tree:
`095ce634fa0a90e81fbc4805574d75fa4d06bb71`.

Status: **ethos-doc-core 0.2.0 cargo publish dry-run evidence recorded; cargo publish remains blocked**

This record captures the first required Rust registry dry-run after `v0.2.0` version activation.
It does not approve or perform `cargo publish`, create tags, publish dependent crates, change
installable public wording, upload artifacts, publish Python or npm packages, approve hosted
surfaces, approve production positioning, approve Windows packaged artifacts, approve bundled
project-maintained PDFium builds, approve `ethos-doc`, approve `ethos-rag`, or approve public
benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: v0.2.0 first Rust dry-run gate
- Package: `ethos-doc-core`
- Version: `0.2.0`
- Source commit: `9ca01477a14b9addd542e7aa9c5217a1b1df6831`
- Source tree: `095ce634fa0a90e81fbc4805574d75fa4d06bb71`
- Generated crate artifact: `ethos-doc-core-0.2.0.crate`
- Generated crate SHA256:
  `de86ce74dd791b50d0722cddc878756cceabae2162f747e9e24902b88e5c7de1`

## Command Evidence

Command:

```sh
cargo publish --dry-run --locked -p ethos-doc-core
```

Result:

```text
Packaging ethos-doc-core v0.2.0
Packaged 20 files, 162.1KiB (37.6KiB compressed)
Verifying ethos-doc-core v0.2.0
Compiling ethos-doc-core v0.2.0
Finished `dev` profile
Uploading ethos-doc-core v0.2.0
warning: aborting upload due to dry run
RESULT: PASS (dry-run)
```

The dry run exited `0`.

## Package File List

```text
.cargo_vcs_info.json
Cargo.lock
Cargo.toml
Cargo.toml.orig
NOTICE.md
README.md
src/c14n.rs
src/codes.rs
src/config.rs
src/crop_element.rs
src/error.rs
src/evidence_anchor.rs
src/fingerprint.rs
src/geom.rs
src/grounding.rs
src/ids.rs
src/lib.rs
src/model.rs
src/traits.rs
src/verify_types.rs
```

## Boundary

- `cargo publish` remains blocked until an explicit operator publication decision is recorded.
- `ethos-verify` and `ethos-pdf` dry-runs remain blocked until the required dependency-order lane
  reaches them after `ethos-doc-core 0.2.0` is visible in the crates.io index.
- PyPI upload remains blocked.
- `npm publish` remains blocked.
- GitHub Release `v0.2.0` artifact upload remains blocked.
- Release tag creation remains blocked.
- Package tag creation remains blocked.
- Installable `0.2.0` public wording remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Commands

```sh
cargo publish --dry-run --locked -p ethos-doc-core
shasum -a 256 target/package/ethos-doc-core-0.2.0.crate
cargo package --list --locked -p ethos-doc-core
python3 .github/scripts/test_v0_2_0_ethos_doc_core_cargo_publish_dry_run_evidence.py
make v0-2-release-prep PYTHON=python3
git diff --check
```

## Result

```text
ethos-doc-core 0.2.0 dry-run evidence recorded
The generated crate artifact and package file list are bound to source commit 9ca0147
No publication, tag, artifact upload, or installable wording is approved by this record
```
