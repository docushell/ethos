# First Public Release Final Decider Validation - 2026-06-23

- Validated source HEAD before this record: `858bf0f`

Final-decider source commit: `858bf0fbcac38040ee68f714c302672a72fb27d9`

Final-decider source tree: `86b7cc44e28a1308af3c29632c7d9e90a0270bfb`

Status: **bounded artifact-evaluation publication decision recorded**

This record is the final decider for the current first public artifact evaluation lane. It is
intentionally narrow: it approves only the exact evidenced surfaces below for public artifact
evaluation and keeps all unevidenced or higher-risk surfaces blocked.

## Approved Artifact Evaluation Surfaces

- GitHub Release artifact evaluation for `ethos-macos-arm64.tar.gz`.
- Python package artifact evaluation for `ethos-pdf` / `ethos_pdf` at `0.1.0`.
- Caller-provided PDFium only, through `ETHOS_PDFIUM_LIBRARY_PATH`.
- SHA256 checksum and inventory evidence for the macOS arm64 CLI artifact.
- License and NOTICE inclusion for the approved artifact evaluation surfaces.

## Required Publication Boundaries

- GitHub artifact notes must include the macOS arm64 SHA256
  `35c7cc19ea51231edb1a0cfb6d160d3a2e620ba9357d116ef071f66ebc5e236f`.
- The macOS arm64 CLI artifact must continue to report `ethos 0.1.0`.
- Python `ethos-pdf` must continue to report `0.1.0` and expose the documented public API.
- PDFium must remain caller-provided; no project-maintained PDFium build is approved.
- Publication instructions must not describe hosted surfaces, production positioning, public
  benchmark reports, public benchmark claims, speed, footprint, table-quality, parser-quality, or
  general quality claims.

## Exact Approved Launch Wording

The following wording is approved for the bounded artifact evaluation lane:

> Ethos is public beta for source, Rust crate, macOS arm64 CLI artifact, and Python wheel evaluation.
> It verifies whether AI citations are grounded in document evidence across native Ethos JSON and
> supported foreign parser outputs. Rust library crates `ethos-doc-core`, `ethos-verify`, and
> `ethos-pdf` are available on crates.io at `0.1.0` for evaluation. The macOS arm64 CLI artifact and
> Python `ethos-pdf` wheel are available for evaluation with caller-provided PDFium. Hosted surfaces,
> production positioning, npm publication, Windows packaged artifacts, bundled project-maintained
> PDFium builds, `ethos-doc`, `ethos-rag`, and public benchmark claims remain blocked.

Any broader public wording requires a new decider record.

## Retained Blockers

- Linux x64 CLI artifact publication remains blocked until artifact evidence is recorded.
- npm publication remains blocked until `vendor/` binary payload inclusion is implemented and
  validated, or a later decider explicitly approves a different npm strategy.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows x64 packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Required Operator Checks Before Publication

Before publishing the approved artifact evaluation surfaces, the operator must rerun:

```sh
make release-candidate-prep PYTHON=<jsonschema-venv>/bin/python
cargo build --locked --release -p ethos-cli
python3 -m build --wheel
```

If any output changes artifact names, checksums, version output, license/NOTICE inclusion, or the
approved launch wording, publication must stop until a new evidence record and decider record pass.

## Result

The current lane may proceed only with the exact approved artifact evaluation surfaces and exact
approved launch wording above. All retained blockers remain in force.
