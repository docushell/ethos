# v0.3.0 Public Install Wording Approval Decision Validation - 2026-07-02

Validated source HEAD before this record: `7502658`.

v0.3.0 public install wording approval decision source commit:
`750265856f352b32378ab62c72a74dd6ca72646f`.

v0.3.0 public install wording approval decision source tree:
`0c458a91f49267aadc4240e2981305338d4793ca`.

Status: **v0.3.0 public install wording approval decision recorded; wording closeout authorized**

This record captures the decider approval for the exact public `0.3.0` install wording packet
requested in
`docs/validation/v0-3-0-public-install-wording-approval-request-validation-2026-07-02.md`.

Decider decision supplied: **Approved**. The exact public `0.3.0` install wording packet below is
accepted for a bounded README and public-boundary claims closeout.

## Accepted Public Status Sentence

```text
Ethos is a deterministic document evidence layer for source-grounded verification and citation checking across native Ethos JSON and supported foreign parser outputs. The current beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.3.0`, the Python `ethos-pdf` wheel at `0.3.0`, the npm `@docushell/ethos-pdf@0.3.0` package, and GitHub Release `v0.3.0` macOS arm64/Linux x64 CLI artifacts. PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.
```

## Accepted Install Commands

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

## Scope Accepted By This Decision

- Update `README.md` to the exact accepted public `0.3.0` status sentence and install wording.
- Update `docs/public-boundary-claims.json` so the public-boundary claims gate protects the exact
  accepted `0.3.0` README wording.
- Keep PDFium-backed commands scoped to caller-provided PDFium through
  `ETHOS_PDFIUM_LIBRARY_PATH`.
- Keep the Python wheel scoped to a thin wrapper around a caller-provided local `ethos` CLI binary.
- Keep the npm package scoped to the approved macOS arm64 and Linux x64 CLI binaries.

## Non-Actions

- This decision does not create package tags.
- This decision does not create release tags.
- This decision does not approve DocuShell integration.
- This decision does not approve hosted surfaces.
- This decision does not approve production positioning.
- This decision does not approve Windows packaged artifacts.
- This decision does not approve bundled project-maintained PDFium builds.
- This decision does not approve public benchmark reports.
- This decision does not approve public benchmark claims.
- This decision does not approve speed, footprint, parser-quality, table-quality, or production
  claims.
- This decision does not approve `ethos-doc`.
- This decision does not approve `ethos-rag`.

## Result

The exact public `0.3.0` install wording packet is approved for a bounded README and
public-boundary claims closeout. Package tag creation, release tag creation, DocuShell
integration, hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, public benchmark reports, public benchmark claims, speed,
footprint, parser-quality, table-quality, `ethos-doc`, and `ethos-rag` remain blocked pending
separate lanes.
