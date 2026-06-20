# Milestone E Public Beta Source-Only Approval Validation - 2026-06-20

## Purpose

Record the dedicated approval decision for the narrowly scoped Public beta approval lane.

This record approves only source-only public beta evaluation for the GitHub source repository. It
does not approve package publication, hosted surfaces, production positioning, public benchmark
reports, public benchmark claims, release artifacts, binaries, wheels, npm packages, crate
publication, project-maintained PDFium builds, or public result wording. It does not make
performance, quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an
internal continuation decision only.

## Status

Status: **pass for source-only public beta approval validation**.

Decision: approve source-only public beta evaluation.

Ethos remains source-only pre-alpha outside this approved source-only public beta surface.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `3f9e1c4`
- Lane: public beta approval
- Surface: GitHub source repository `docushell/ethos`
- Reviewed commit: `d755e7c`
- Merged main commit: `3f9e1c4`
- Tree: `a9e913b0ba7ecd1567479b2ec773342868cba126`
- Approval owner: docushell-admin acting as decider

## Exact Approved Wording

Ethos is public beta for source-only evaluation. It verifies whether AI citations are grounded in
document evidence across native Ethos JSON and supported foreign parser outputs. Package
publication, hosted surfaces, production positioning, and public benchmark claims remain blocked.

## Exact Approved Surface

The approved surface is limited to source-only evaluation through the GitHub source repository.
Users may clone the source, read source-tree docs, build the CLI locally, and run source-tree
validation or setup commands.

Approved source-tree commands for this surface:

```sh
rustup show
cargo build --locked -p ethos-cli
./target/debug/ethos --help
make verify-alpha
./target/debug/ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --fail-on-ungrounded \
  --out /tmp/ethos-native-verification-report.json
```

## Rescoped Blockers

- Release-scope engineering blocker: rescoped because the approved surface excludes package
  publication, hosted operation, project-maintained PDFium builds, broad-corpus claims, public
  benchmark reports, and public benchmark claims.
- Public setup path: resolved for source checkout build and validation commands. No package,
  hosted, or production setup path is approved.
- PDFium build path: rescoped and excluded. PDFium-backed paths require caller-provided local
  PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`; project-maintained PDFium builds remain blocked.

## Explicit Exclusions

- Package publication remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public reports remain blocked.
- Public result wording remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Release artifacts remain blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- npm packages remain blocked.
- Crate publication remains blocked.
- Project-maintained PDFium builds remain blocked.
- Performance claims remain blocked.
- Quality claims remain blocked.
- Footprint claims remain blocked.
- Table-quality claims remain blocked.
- Parser-quality claims remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_public_beta_source_only_approval.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Source-only public beta approval validation passed
Reviewed commit and merged main commit have the same tree
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
