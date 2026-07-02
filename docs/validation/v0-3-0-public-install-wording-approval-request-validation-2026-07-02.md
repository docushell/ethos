# v0.3.0 Public Install Wording Approval Request Validation - 2026-07-02

Validated source HEAD before this record: `7ad3521`.

v0.3.0 public install wording approval request source commit:
`7ad3521623764557edccbb563ef3bd279d046cc5`.

v0.3.0 public install wording approval request source tree:
`1471f4c7ecfc0aa84439042994be161bd97e1f4e`.

Status: **v0.3.0 public install wording approval request recorded; wording remains blocked**

This record requests decider review for the exact public `0.3.0` install wording packet below. It
does not change `README.md`, does not change `docs/public-boundary-claims.json`, does not publish
or republish any package, does not create package tags or release tags, does not approve DocuShell
integration, hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or public
benchmark claims.

## Source Inputs

- Rust and PyPI publication closeout:
  `docs/validation/v0-3-0-publication-closeout-validation-2026-07-01.md`
- GitHub Release CLI artifact closeout:
  `docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md`
- npm publication closeout:
  `docs/validation/v0-3-0-npm-publication-closeout-validation-2026-07-02.md`
- Rust crate versions requested for public install wording:
  - `ethos-doc-core@0.3.0`
  - `ethos-verify@0.3.0`
  - `ethos-pdf@0.3.0`
- Python wheel requested for public install wording:
  - `ethos-pdf==0.3.0`
- npm package requested for public install wording:
  - `@docushell/ethos-pdf@0.3.0`
- GitHub Release requested for public install wording:
  - `v0.3.0` macOS arm64 and Linux x64 CLI artifacts

## Exact Public Status Sentence Requested

```text
Ethos is a deterministic document evidence layer for source-grounded verification and citation checking across native Ethos JSON and supported foreign parser outputs. The current beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.3.0`, the Python `ethos-pdf` wheel at `0.3.0`, the npm `@docushell/ethos-pdf@0.3.0` package, and GitHub Release `v0.3.0` macOS arm64/Linux x64 CLI artifacts. PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.
```

## Exact Install Commands Requested

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

Python wrapper wording requested:

```text
The v0.3.0 Python wrapper includes JSON verification and evidence anchoring through that caller-provided CLI.
```

## Required Boundaries For The Requested Wording

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

## Current Public Wording State

Current `README.md` and `docs/public-boundary-claims.json` remain on the already-approved public
install baseline while this request is under review:

- Rust install commands remain `0.2.0`.
- Python install command remains `ethos-pdf==0.2.0`.
- npm install command remains `@docushell/ethos-pdf@0.2.1`.
- GitHub Release CLI artifact reference remains `v0.2.0`.

Public `0.3.0` install wording remains blocked until a separate approval decision and closeout
pass.

## Required Manual Decider Step

A decider must accept or reject this exact wording packet before any public docs or public-boundary
claims file is changed to `0.3.0` install wording.

If accepted, a later decision record must bind this exact wording and retained blockers. Only after
that decision record passes may a follow-up branch update `README.md`,
`docs/public-boundary-claims.json`, and any other public install surfaces to the exact accepted
wording.

## Non-Actions

- This request does not change `README.md`.
- This request does not change `docs/public-boundary-claims.json`.
- This request does not change public install commands.
- This request does not create package tags.
- This request does not create release tags.
- This request does not approve DocuShell integration.
- This request does not approve hosted surfaces.
- This request does not approve production positioning.
- This request does not approve Windows packaged artifacts.
- This request does not approve bundled project-maintained PDFium builds.
- This request does not approve public benchmark reports.
- This request does not approve public benchmark claims.
- This request does not approve `ethos-doc`.
- This request does not approve `ethos-rag`.

## Result

The exact public `0.3.0` install wording packet is ready for decider review. Public `0.3.0` install
wording remains blocked until a separate approval decision and closeout pass.
