# First Public Release Linux x64 Final Decider Validation - 2026-06-23

- Validated source HEAD before this record: `38a92f3`

Linux-final-decider source commit: `38a92f390c9578194467eceaacdd297a132d49c9`

Linux-final-decider source tree: `66a8d69a9e94c891621a77cb3b4719a9a7ffd8cd`

Status: **bounded Linux x64 artifact-evaluation publication decision recorded**

This record is the final decider for adding the Linux x64 CLI artifact to the existing first public
evaluation release. It approves only the exact evidenced Linux x64 GitHub Release assets below and
keeps all unevidenced or higher-risk surfaces blocked.

## Approved Artifact Evaluation Surface

- GitHub Release artifact evaluation for `ethos-linux-x64.tar.gz`.
- SHA256 checksum, inventory, and smoke evidence for the Linux x64 CLI artifact.
- Caller-provided PDFium only, through `ETHOS_PDFIUM_LIBRARY_PATH`.
- Publication to the existing GitHub Release tag `v0.1.0`.

## Required Publication Boundaries

- The Linux x64 GitHub Release assets must be:
  - `ethos-linux-x64.tar.gz`
  - `ethos-linux-x64.tar.gz.sha256`
  - `ethos-linux-x64.inventory.json`
  - `ethos-linux-x64.smoke.json`
- The Linux x64 artifact SHA256 must be:

```text
59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2
```

- The Linux x64 CLI artifact must continue to report `ethos 0.1.0`.
- Missing PDFium behavior must continue to exit `12` and report:

```text
PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path
```

- PDFium must remain caller-provided; no project-maintained PDFium build is approved.
- Publication instructions must not describe hosted surfaces, production positioning, public
  benchmark reports, public benchmark claims, speed, footprint, table-quality, parser-quality, or
  general quality claims.

## Exact Approved Launch Wording

The following wording is approved for the bounded artifact evaluation lane after Linux x64 assets
are attached:

> Ethos is public beta for source, Rust crate, macOS arm64 CLI artifact, Linux x64 CLI artifact,
> and Python wheel evaluation. It verifies whether AI citations are grounded in document evidence
> across native Ethos JSON and supported foreign parser outputs. Rust library crates
> `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are available on crates.io at `0.1.0` for
> evaluation. The macOS arm64 and Linux x64 CLI artifacts and Python `ethos-pdf` wheel are
> available for evaluation with caller-provided PDFium. Hosted surfaces, production positioning,
> npm publication, Windows packaged artifacts, bundled project-maintained PDFium builds,
> `ethos-doc`, `ethos-rag`, and public benchmark claims remain blocked.

Any broader public wording requires a new decider record.

## Retained Blockers

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

Before attaching the approved Linux x64 assets to `v0.1.0`, the operator must verify:

```sh
shasum -a 256 ethos-linux-x64.tar.gz
cat ethos-linux-x64.tar.gz.sha256
cat ethos-linux-x64.inventory.json
cat ethos-linux-x64.smoke.json
```

If any output changes artifact names, checksums, version output, missing-PDFium behavior, license
and NOTICE inclusion, or approved launch wording, publication must stop until a new evidence record
and decider record pass.

## Result

The current lane may proceed only by attaching the exact approved Linux x64 artifact evaluation
assets to the existing GitHub Release `v0.1.0` and updating release notes with the exact approved
bounded wording above. All retained blockers remain in force.
