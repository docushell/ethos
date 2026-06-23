# Patch 0.1.1 Readiness Prep Validation - 2026-06-23

## Purpose

Record the candidate contents and remaining gates for a possible patch `0.1.1` review after the
post-`0.1.0` onboarding fixes landed on `main`.

Validated source HEAD before this record: `dd155e4`.
Patch-prep source commit: `dd155e4f5e999da82043e2f53fa1ac8e84929118`.
Patch-prep source tree: `ba0291a1c084f19d04935dc4af16fb7603388a19`.

## Candidate Contents

The candidate patch contents are limited to user-facing setup and onboarding improvements:

- `ethos doctor` PDFium diagnostics.
- Synthetic fixture golden-change rationale guard.
- Bounded 2-minute PDF parse quickstart using `fixtures/synthetic/simple-text/document.pdf`.
- Missing or unusable PDFium setup guidance that points to `ethos doctor`,
  `ethos doctor --require-pdfium`, and `docs/pdfium-manual-setup.md`.

## Boundary

This prep record does not approve a release, tag, package publish, GitHub Release artifact,
version bump, npm publish, PyPI publish, crates.io publish, hosted surface, production positioning,
Windows packaged artifact, bundled project-maintained PDFium build, public benchmark report, public
benchmark claim, `ethos-doc`, or `ethos-rag`.

The current public baseline remains `v0.1.0` until a separate release decision, version update,
artifact build, smoke evidence, and operator action are completed.

PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`. The setup checks only whether
the configured PDFium is usable by Ethos; they do not vet untrusted dynamic libraries.

## Required Before Any Patch Release Action

- Decide the exact patch version and surfaces in a separate decider step.
- Update package and CLI versions only after that decision.
- Run the release-candidate prep gates from the exact candidate commit.
- Build and smoke any proposed artifacts from the exact candidate commit.
- Re-run public posture, claims, source snapshot, license/NOTICE, and private-path checks after
  any version or public-facing wording changes.
- Record manual operator evidence for any credentialed publish or GitHub Release action.

## Validation Commands

The prep lane should pass at least:

```sh
cargo fmt --check
cargo test --locked -p ethos-cli --test doctor
cargo test --locked -p ethos-pdf
PYTHONPATH=python python3 python/tests/test_cli_surface.py
python3 .github/scripts/test_pdfium_manual_setup_contract.py
python3 .github/scripts/test_release_artifact_workflow_prep.py
python3 .github/scripts/test_patch_0_1_1_readiness_prep.py
make light-check PYTHON=python3
```

Manual successful PDF parse smoke remains optional unless a trusted caller-provided PDFium dynamic
library is available locally.
