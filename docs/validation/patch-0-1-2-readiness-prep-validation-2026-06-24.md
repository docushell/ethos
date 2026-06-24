# Patch 0.1.2 Readiness Prep Validation - 2026-06-24

## Purpose

Record the immediate candidate boundary for a possible patch `0.1.2` review after the
`ethos evidence anchor` command and the `evidence_anchor` v1 guard landed on `main`.

Validated source HEAD before this record: `8926217`.
Patch-prep source commit: `89262171ee9fdd342c5bcc808d8c12d40a126337`.
Patch-prep source tree: `3e41ef063d7746de2a59486a2bacc2fdecb187f2`.

## Candidate Contents

The candidate patch contents are limited to a narrow beta patch:

- `ethos evidence anchor` as a deterministic source-bound evidence-ref checking command.
- The `evidence_anchor` v1 guard, including schema/example validation and CI-enforced drift checks.
- Professional public README status wording that keeps `Status: public beta evaluation.` while
  presenting Ethos as a source-grounded verification layer instead of a blocker ledger.
- Retained caller-provided PDFium boundary for PDFium-backed paths.

## Boundary

This prep record does not approve a release, does not approve a tag, does not approve package
publish, does not approve npm publish, does not approve PyPI publish, does not approve crates.io
publish, does not approve a GitHub Release artifact, does not approve hosted surfaces, does not
approve production positioning, does not approve Windows packaged artifacts, does not approve
bundled project-maintained PDFium builds, does not approve public benchmark reports, does not
approve public benchmark claims, does not approve speed, footprint, parser-quality, table-quality,
or production claims, does not approve `ethos-doc`, and does not approve `ethos-rag`.

The current public install baseline remains `0.1.1` until a separate release decision, version
update, artifact build, smoke evidence, registry/GitHub Release evidence, and operator action are
completed.

PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`. The setup checks only whether
the configured PDFium is usable by Ethos; they do not vet untrusted dynamic libraries.

## Required Before Any Patch Release Action

- Decide the exact `0.1.2` package and artifact surfaces in a separate decider step.
- Update package and CLI versions only after that decision.
- Build and smoke any proposed artifacts from the exact candidate commit.
- Re-run public posture, claims, source snapshot, license/NOTICE, and private-path checks after
  any version or public-facing wording changes.
- Record manual operator evidence for any credentialed publish or GitHub Release action.

## Validation Commands

The prep lane should pass at least:

```sh
python3 .github/scripts/test_patch_0_1_2_readiness_prep.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/test_public_prealpha_wording_approval.py
python3 .github/scripts/test_release_candidate_prep.py
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
make light-check PYTHON=python3
git diff --check
```
