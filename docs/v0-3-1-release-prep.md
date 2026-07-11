# Ethos v0.3.1 Release Preparation

Status: patch-release preparation tracker for a docs, tooling, and decision-record release.
No crate, wheel, npm, or CLI behavior changes are included. This document does not approve
version activation, publication, additional release tags or release targets, DocuShell
integration, hosted surfaces, or production positioning.

Canonical preparation sentence:

> v0.3.1 prepares adoption-focused docs, the pinned PDFium fetch helper, and the caller-provided
> PDFium decision record, with no change to Ethos verification semantics or public claims scope.

The release promise being prepared is narrow:

> Ethos v0.3.1 makes the existing v0.3.0 evaluation surfaces easier to try and records the
> distribution posture they already ship with. It adds no new capability, claim, or surface.

## Included Preparation Scope

- README lead demo: "catch a fabricated citation in 60 seconds" over checked-in JSON fixtures
  (`schemas/examples/document.example.json` + `examples/verify/native_ungrounded_citations.json`
  and `examples/verify/native_grounded_citations.json`), no PDFium required. All existing
  `docs/public-boundary-claims.json` readme claim strings are preserved verbatim.
- `scripts/fetch-pdfium.sh`: optional operator helper mirroring the exact
  `docs/pdfium-profile.md` Phase 1 pins (release `chromium/7881`, archive sha256, runtime
  library sha256), fail-closed on any mismatch. README prerequisites, quickstart, and
  troubleshooting reference it.
- ADR-0013 (caller-provided PDFium beta posture): records the shipped v0.3.0 no-distribution
  posture, re-scopes ADR-0002's Phase 2 blocker to bundled / Windows-with-PDFium / hosted
  surfaces, and classifies the fetch helper as operator tooling, not distribution.
- ADR-0002 status amendment line pointing to ADR-0013.
- ADR-0001 addendum (2026-07-10): schedule confirmation one month after kickoff; clarification
  that npm `@docushell/ethos-pdf` is a binary distribution package, not the gated "Node beta."
- CHANGELOG entries for the above.

## Explicit Non-Scope

- version activation (`0.3.0` → `0.3.1` source metadata) — separate lane with its own guard,
  following the existing version-activation pattern;
- crates.io, PyPI, npm, or GitHub Release publication — separate approval and closeout lanes;
- any `ethos` CLI, crate, wheel, or npm behavior change;
- any change to verification semantics, report schemas, goldens, or fixtures;
- ADR-0014 / readiness-report work — explicitly deferred, tracked separately;
- OSS-Fuzz enrollment — external application, tracked outside this release;
- DocuShell integration, hosted surfaces, production positioning;
- Windows packaged artifacts, bundled project-maintained PDFium builds;
- public benchmark reports and speed/footprint/parser-quality/table-quality claims;
- `ethos-doc` / `ethos-rag` public GA.

## Release Sequence

### 1. Land this preparation packet

Merge the README rework, fetch helper, ADR-0013, ADR-0002 amendment, ADR-0001 addendum,
CHANGELOG entries, and this document on `dev/v0-3-1-Fixes` after:

- `make …` public-boundary claims gate passes (`.github/scripts/public_boundary_claims_gate.py`);
- `bash -n scripts/fetch-pdfium.sh` (and shellcheck where available) passes;
- schema-validation and verify-alpha targets are unaffected (no fixture/golden changes expected);
- decider review of ADR-0013 (Proposed → Accepted) and the ADR-0001 addendum.

### 2. Version activation (separate lane)

Bump workspace/package versions `0.3.0` → `0.3.1` with the version-activation guard pattern used
for v0.3.0. Public install wording (`README.md`, `docs/public-boundary-claims.json`) keeps `0.3.0`
strings until the corresponding artifacts are actually published and their wording packet is
approved.

### 3. Publication and closeout (separate lanes)

Follow the v0.3.0 lane pattern: publication approval request → decision → operator action →
closeout record per surface. Nothing in this document pre-approves those steps.

## Product Boundary

v0.3.1 is an adoption and decision-hygiene patch. It changes how quickly an evaluator reaches the
existing verification loop and where the caller-provided PDFium decision is recorded. It does not
change what Ethos claims, proves, parses, or supports.
