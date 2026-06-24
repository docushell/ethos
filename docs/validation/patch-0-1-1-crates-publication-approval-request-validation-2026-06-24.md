# Patch 0.1.1 crates.io Publication Approval Request Validation - 2026-06-24

Validated source HEAD before this record: `a085103`.

Patch 0.1.1 crates publication approval request source commit: `a0851030e28c155c12f5f966af8fa0739a536ea9`.

Patch 0.1.1 crates publication approval request source tree: `0238c3f6bfd264f8803708e4a828d8352320f08f`.

Status: **patch 0.1.1 crates.io publication approval request recorded; cargo publish remains blocked**

This record requests decider review for publishing exactly the patch `0.1.1` Ethos Rust library
crate set to crates.io. It does not approve or perform `cargo publish`, create package tags, change
public wording, approve hosted surfaces, approve production positioning, approve Windows packaged
artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`, approve
`ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Rust crates publication
- Package source commit: `a0851030e28c155c12f5f966af8fa0739a536ea9`
- Package source tree: `0238c3f6bfd264f8803708e4a828d8352320f08f`
- Candidate crates:
  - `ethos-doc-core = 0.1.1`
  - `ethos-verify = 0.1.1`
  - `ethos-pdf = 0.1.1`
- Excluded workspace packages:
  - `ethos-cli`
  - `ethos-layout`
  - `ethos-tables`
  - `ethos-grounding-opendataloader-json`
  - reserved `ethos-doc`
  - reserved `ethos-rag`

## Exact Request Fields

- Decision requested: approve exact patch `0.1.1` crates.io publication preparation inputs for
  later operator execution.
- Approver requested: `docushell-admin` acting as decider.
- Date requested: 2026-06-24.
- Exact candidate crate list requested: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` only.
- Exact package version map requested: `ethos-doc-core = 0.1.1`, `ethos-verify = 0.1.1`, and
  `ethos-pdf = 0.1.1`.
- Exact package tag name set requested: `ethos-package-ethos-doc-core-0.1.1`,
  `ethos-package-ethos-verify-0.1.1`, and `ethos-package-ethos-pdf-0.1.1`.
- Exact package tag source commit requested: `a0851030e28c155c12f5f966af8fa0739a536ea9`.
- Exact package tag source tree requested: `0238c3f6bfd264f8803708e4a828d8352320f08f`.
- Exact candidate package artifacts requested:
  - `ethos-doc-core-0.1.1.crate`
    - SHA256: `d845042c391d584a26dc3aa7ff367f118cfd94e8290a3caec81642186ed0de51`
  - `ethos-verify-0.1.1.crate`
    - SHA256: `27313b8decab66a3ea1b9e4c3e82dc47088e5c2f9d289a1450203cff1b9a7070`
  - `ethos-pdf-0.1.1.crate`
    - SHA256: `a07e6436cceb64dddce1d5468fb25c44b745a26e4d044858b72bd570dcb84529`
- Exact operator commands requested for later approval:
  - `cargo publish --locked -p ethos-doc-core`
  - `cargo publish --locked -p ethos-verify`
  - `cargo publish --locked -p ethos-pdf`

## Requested Publication Order

1. Publish `ethos-doc-core` first.
2. Publish `ethos-verify` after crates.io reports `ethos-doc-core = 0.1.1`.
3. Publish `ethos-pdf` after crates.io reports `ethos-doc-core = 0.1.1`.

`ethos-verify` and `ethos-pdf` both depend on `ethos-doc-core`; no dependent crate publish should
be attempted until the base crate is visible from crates.io.

## Evidence Bound To This Request

- Candidate activation produced crate artifacts for exactly `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf`.
- Candidate activation reported version `0.1.1`.
- Candidate activation reported registry-equivalent consumer check status `pass`.
- Candidate activation reported source manifest activation applied.
- Candidate activation reported package publication approval `false`.
- Candidate activation reported public installation approval `false`.
- `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` manifests do not contain `publish = false`.
- The `ethos-cli` package remains `publish = false`.
- The `ethos-layout` package remains `publish = false`.
- The `ethos-tables` package remains `publish = false`.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Non-Approvals

- This request record does not approve `cargo publish`.
- This request record does not publish any crate.
- This request record does not create package tags.
- This request record does not approve public installation wording.
- This request record does not approve the `ethos-cli` crate for publication.
- This request record does not approve hosted surfaces.
- This request record does not approve production positioning.
- This request record does not approve Windows packaged artifacts.
- This request record does not approve bundled project-maintained PDFium builds.
- This request record does not approve public benchmark reports.
- This request record does not approve public benchmark claims.
- This request record does not approve `ethos-doc`.
- This request record does not approve `ethos-rag`.

## Retained Blockers

- Actual crates.io publication remains blocked pending explicit decider approval.
- Public installation wording remains blocked pending explicit decider approval.
- Package tag creation remains blocked pending explicit decider approval.
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
python3 .github/scripts/test_patch_0_1_1_crates_publication_approval_request.py
python3 .github/scripts/test_milestone_e_package_publication_current_registry_assembly.py
python3 .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py
cargo package --locked --offline -p ethos-doc-core --allow-dirty --no-verify
cargo check --locked --offline -p ethos-verify
cargo check --locked --offline -p ethos-pdf
make release-candidate-prep PYTHON=python3
git diff --check
```

## Result

```text
patch 0.1.1 crates.io publication approval request recorded
Exact crate set, version map, package tag names, source binding, local crate artifact hashes, publish order, and retained blockers were recorded
cargo publish remains blocked pending explicit decider approval and later operator action
```
