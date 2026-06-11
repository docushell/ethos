# Ethos Execution Status

Date: 2026-06-11
Owner: product / decider
Status: Pre-alpha. Week 0 governance is accepted, and commits `de82142` and `8f04bcd` landed the first WS-ENGINE implementation slice. External freeze/pin/name checks still block Gate Zero and all public claims.

## Current Reality

The repository is still pre-alpha, but it is no longer only contract/scaffold code. The committed implementation now includes:

- A real PDFium-backed born-digital PDF extraction path in `ethos-pdf`, loaded only from an explicit `ETHOS_PDFIUM_LIBRARY_PATH`.
- A pinned Phase 1 PDFium profile in `docs/pdfium-profile.md` and `profiles/ethos-deterministic-v1.json`: `chromium/7881`, V8/XFA disabled, platform artifact hashes, runtime library hashes, and provenance are recorded.
- Runtime checks that reject missing or mismatched PDFium versions, release artifacts, and extracted libraries with stable errors before dynamic loading.
- `ethos doc parse` / `ethos fingerprint` PDF execution through a worker process with `max_parse_ms` timeout enforcement, stable error-envelope relay, diagnostics-gated worker stderr, and page-range validation/filtering.
- Quantized page/span extraction at the backend boundary, plus a basic deterministic layout pass that assembles paragraph `text_block` elements and simple column reading order for the current born-digital fixtures.
- Schema/example/profile validation is green through `schemas/validate_examples.py` using `jsonschema` draft 2020-12 validation, including referential-integrity and bbox sanity checks outside JSON Schema.

Still absent or not claimable: frozen Gate Zero corpus/hardware records, reproducible benchmark result JSON, competitor pins/comparisons, public speed/quality/footprint claims, citation-checking verification, OCR/image-only support, table/list/heading semantics, Phase 2 project-maintained PDFium builds, release packaging, and multi-platform determinism evidence.

## Human / External Blockers

| ID | Blocker | Required output | Owner | Blocks |
| --- | --- | --- | --- | --- |
| H1 | Freeze Gate Zero corpus and hardware | `benchmarks/gate-zero/manifest.json` has corpus entries with exact sha256 values, complete hardware CPU/RAM/OS/kernel/runner fields, `frozen=true`, and signed freeze record | Gate Zero decider interim corpus owner / decider | Valid Gate Zero run, public benchmark trust |
| H2 | Pin competitors | `benchmarks/competitors.lock.json` has exact versions, artifact sha256 values, runtime versions, and `pinned=true` for OpenDataLoader, EdgeParse, LiteParse, and PyMuPDF4LLM | Benchmark owner | Harness gating, competitor comparison |
| H3 | Accept package identifier ADR | `docs/decisions/ADR-0006-package-identifiers.md` records registry/trademark checks and moves to Accepted, or records approved renames | Devrel / decider | Any public package, public docs claim, launch announcement |

These are not engineering placeholders. Do not mark them done until the exact external facts are recorded.

## Active Engineering Lane

WS-ENGINE remains the active lane under the reduced-staff plan. The first slice is implemented, but acceptance is limited to simple born-digital fixtures and local PDFium configuration.

| Work item | Current status | Remaining blocker |
| --- | --- | --- |
| PDFium Phase 1 profile | Landed: pinned profile, V8/XFA-disabled state, platform hashes, runtime library hashes, and provenance are recorded | Phase 2 project-maintained builds still block Public Beta |
| PDFium loader/runtime checks | Landed: missing/mismatched version, artifact, and runtime library hashes fail deterministically | Release packaging and operator setup path still need hardening |
| Backend skeleton replacement | Landed for simple born-digital PDFs: page count, quantized spans, worker execution, timeout, page filtering, and fingerprint path exist | Wider corpus coverage, quirk log, and Gate Zero run are still missing |
| Layout groundwork | Landed: basic paragraph text blocks and simple column reading order over quantized spans | Tables, headings, lists, rotation/quirk handling, and confidence policy remain future work |
| Font policy groundwork | Partially landed: substitution table and profile policy are present; fixture output uses deterministic substitution IDs | Bundled fallback asset hashing and broader font/CID validation remain open |
| Schema/example validation | Landed: schemas, examples, deterministic profile, referential integrity, and bbox sanity pass the `jsonschema` validation gate | Contract changes still require explicit versioning and compatibility review |

## PM Rule

Public language stays at "pre-alpha / contracts phase" until all three external blockers are closed and Gate Zero has reproducible result JSON. Internal work can proceed on WS-ENGINE, but no speed, footprint, quality, or competitor claim is allowed before that point.
