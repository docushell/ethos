# v0.3.0 Public Install Wording Closeout Validation - 2026-07-02

Validated source HEAD before this record: `7502658`.

v0.3.0 public install wording closeout source commit:
`750265856f352b32378ab62c72a74dd6ca72646f`.

v0.3.0 public install wording closeout source tree:
`0c458a91f49267aadc4240e2981305338d4793ca`.

Status: **v0.3.0 public install wording closeout recorded**

This record closes the approved public `0.3.0` install wording lane for `README.md` and
`docs/public-boundary-claims.json`. It is based on the approval request and decision records:

- `docs/validation/v0-3-0-public-install-wording-approval-request-validation-2026-07-02.md`
- `docs/validation/v0-3-0-public-install-wording-approval-decision-validation-2026-07-02.md`

## Public Status Sentence Applied

```text
Ethos is a deterministic document evidence layer for source-grounded verification and citation checking across native Ethos JSON and supported foreign parser outputs. The current beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.3.0`, the Python `ethos-pdf` wheel at `0.3.0`, the npm `@docushell/ethos-pdf@0.3.0` package, and GitHub Release `v0.3.0` macOS arm64/Linux x64 CLI artifacts. PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.
```

## Install Wording Applied

Rust library crates:

```bash
cargo add ethos-doc-core@0.3.0
cargo add ethos-verify@0.3.0
cargo add ethos-pdf@0.3.0
```

Python wrapper:

```bash
python3 -m pip install ethos-pdf==0.3.0
```

npm CLI package:

```bash
npm install -g @docushell/ethos-pdf@0.3.0
ethos --version
```

GitHub Release CLI artifact wording:

```text
GitHub Release `v0.3.0` also provides evaluation CLI archives for macOS arm64 and Linux x64.
```

Python wrapper wording:

```text
The v0.3.0 Python wrapper includes JSON verification and evidence anchoring through that caller-provided CLI.
```

## Files Updated

- `README.md`
- `docs/public-boundary-claims.json`
- `docs/execution-status.md`
- `docs/public-release-checklist.md`
- `docs/v0-3-0-release-prep.md`
- `docs/validation/README.md`
- `CHANGELOG.md`

## Retained Boundaries

- PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.
- The Python wheel remains a thin wrapper around a caller-provided local `ethos` CLI binary.
- The Python wheel does not bundle the CLI or PDFium.
- The npm package vendors only the approved macOS arm64 and Linux x64 CLI binaries.
- Unsupported npm platforms fail before invoking a binary.
- Windows packaged artifacts remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Parser-quality, table-quality, speed, footprint, and production claims remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- DocuShell integration remains blocked.
- Package tag creation remains blocked.
- Release tag creation remains blocked.

## Non-Actions

- This closeout does not create package tags.
- This closeout does not create release tags.
- This closeout does not approve DocuShell integration.
- This closeout does not approve hosted surfaces.
- This closeout does not approve production positioning.
- This closeout does not approve Windows packaged artifacts.
- This closeout does not approve bundled project-maintained PDFium builds.
- This closeout does not approve public benchmark reports.
- This closeout does not approve public benchmark claims.
- This closeout does not approve `ethos-doc`.
- This closeout does not approve `ethos-rag`.

## Result

Public `0.3.0` install wording is closed out only for the exact accepted README and
public-boundary claims packet. Package tag creation, release tag creation, DocuShell integration,
hosted surfaces, production positioning, Windows packaged artifacts, bundled project-maintained
PDFium builds, public benchmark reports, public benchmark claims, speed, footprint,
parser-quality, table-quality, `ethos-doc`, and `ethos-rag` remain blocked pending separate
lanes.
