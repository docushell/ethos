# Ethos Execution Status

Date: 2026-06-11
Owner: product / decider
Status: Week 0 governance accepted; external freeze/pin/name checks still block public claims. Engineering may begin WS-ENGINE work, but Gate Zero cannot run until the blockers below are closed.

## Current Reality

The repository is still pre-alpha contract/scaffold code. It does not yet have real PDF parsing, a real PDFium backend, layout extraction, benchmark results, competitor comparisons, or citation-checking verification. Those items remain implementation work.

## Human / External Blockers

| ID | Blocker | Required output | Owner | Blocks |
| --- | --- | --- | --- | --- |
| H1 | Freeze Gate Zero corpus and hardware | `benchmarks/gate-zero/manifest.json` has corpus entries with exact sha256 values, complete hardware CPU/RAM/OS/kernel/runner fields, `frozen=true`, and signed freeze record | Gate Zero decider interim corpus owner / decider | Valid Gate Zero run, public benchmark trust |
| H2 | Pin competitors | `benchmarks/competitors.lock.json` has exact versions, artifact sha256 values, runtime versions, and `pinned=true` for OpenDataLoader, EdgeParse, LiteParse, and PyMuPDF4LLM | Benchmark owner | Harness gating, competitor comparison |
| H3 | Accept package identifier ADR | `docs/decisions/ADR-0006-package-identifiers.md` records registry/trademark checks and moves to Accepted, or records approved renames | Devrel / decider | Any public package, public docs claim, launch announcement |

These are not engineering placeholders. Do not mark them done until the exact external facts are recorded.

## Active Engineering Lane

WS-ENGINE is the next active lane under the reduced-staff plan.

| Work item | Required output | Acceptance |
| --- | --- | --- |
| PDFium Phase 1 profile | `docs/pdfium-profile.md` and `profiles/ethos-deterministic-v1.json` record pinned Phase 1 identity | Version, V8/XFA disabled state, platform hashes, and provenance are present |
| PDFium loader/build checks | `ethos-pdf` build/runtime path rejects missing or mismatched PDFium payloads deterministically | Loader validates hashes and emits stable errors |
| Backend skeleton replacement | `PdfiumBackend` opens born-digital PDFs and returns page count plus quantized spans | `ethos doc parse` no longer returns the not-implemented backend error for simple PDFs |
| Font policy groundwork | Substitution table and deterministic fallback path are present | System font fallback is disabled or explicitly unreachable in the base profile |
| Quantized extraction groundwork | Extraction emits `QuantizedGeom` at the backend boundary | Raw PDFium geometry does not cross into layout/contract layers |

## PM Rule

Public language stays at "pre-alpha / contracts phase" until all three external blockers are closed and Gate Zero has reproducible result JSON. Internal work can proceed on WS-ENGINE, but no speed, footprint, quality, or competitor claim is allowed before that point.
