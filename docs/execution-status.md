# Ethos Execution Status

Date: 2026-06-16
Owner: product / decider
Status: Pre-alpha / Milestone A implementation. Week 0 governance is accepted, WS-ENGINE Phase 1 has a real narrow PDFium path, WS-VERIFY-ALPHA has real deterministic evidence checks over native Ethos JSON and pinned OpenDataLoader output, WS-HARNESS has fail-closed readiness scaffolding, the Gate Zero corpus/hardware manifest and direct competitor lock are frozen/signed, ADR-0006 closes package identifier/trademark validation, ADR-0007 locks the product direction, and the public-source preflight is green for a source-only pre-alpha GitHub push. Signed host result generation still blocks Gate Zero, public benchmark reports, releases, packages, and all performance/quality claims. The next controlled-run handoff is `docs/gate-zero-evidence-runbook.md`.

## Current Reality

The repository is still pre-alpha, but it is no longer only contract/scaffold code. Real parsing and real alpha verification exist. They are narrow, fixture-backed, and not yet Gate Zero-proven.

The committed implementation now includes:

- A real PDFium-backed born-digital PDF extraction path in `ethos-pdf`, loaded only from an explicit `ETHOS_PDFIUM_LIBRARY_PATH`.
- A pinned Phase 1 PDFium profile in `docs/pdfium-profile.md` and `profiles/ethos-deterministic-v1.json`: `chromium/7881`, V8/XFA disabled, platform artifact hashes, runtime library hashes, and provenance are recorded.
- Runtime checks that reject missing or mismatched PDFium versions, release artifacts, and extracted libraries with stable errors before dynamic loading.
- `ethos doc parse` / `ethos fingerprint` PDF execution through a worker process with `max_parse_ms` timeout enforcement, stable error-envelope relay, diagnostics-gated worker stderr, and page-range validation/filtering.
- Quantized page/span extraction at the backend boundary, plus a basic deterministic layout pass that assembles paragraph `text_block` elements and simple column reading order for the current born-digital fixtures.
- Schema/example/profile validation is green through `schemas/validate_examples.py` using `jsonschema` draft 2020-12 validation, including the crop descriptor artifact contract plus referential-integrity and bbox sanity checks outside JSON Schema.
- `ethos verify` now produces non-empty quote, value, presence, and table-cell verification checks over native Ethos document JSON and synthetic OpenDataLoader-style JSON through `--grounding opendataloader-json`; it also verifies quote/value/presence citations over pinned real OpenDataLoader 2.4.7 JSON, including grounded and ungrounded cases. Citation/config inputs are rejected when they drift outside the closed schemas. The public demo harness covers grounded, ungrounded, not-found, stale-fingerprint, capability-limited, malformed-citation, malformed OpenDataLoader-style input, and summary-format reject paths.
- Verification semantics are now trust-honest at alpha scope: quote containment is explicitly labeled, value/table-cell checks require normalized equality, fingerprint-pinned citations fail closed when source fingerprints are unavailable, and structured capability limits explain why a run is downgraded.
- `make verify-alpha` is the current alpha trust-loop command: it checks native examples, synthetic OpenDataLoader-style examples, pinned real OpenDataLoader grounded/ungrounded examples, schema validation, usage diagnostics for malformed citations and malformed OpenDataLoader-style inputs, byte-identical repeated verification reports, byte-identical native crop descriptors, summary diagnostics for an ungrounded native case, and foreign fixture manifest hash binding.
- Native Ethos verification can emit deterministic, schema-backed crop descriptor JSON artifacts through `--crop-dir`; these bind `document_fingerprint`, page, bbox, and check ids. Native `crop_ref` filenames are logical evidence references derived from document fingerprint, check id, and page, while descriptors still record the exact observed bbox. When `--crop-source-pdf` is supplied, the CLI validates source-PDF fingerprint binding and emits PNG crop artifacts whose filenames, byte hashes, dimensions, and source fingerprint are bound from the descriptor. `make verify-rendered-crops` checks same-host repeated-run stability for the rendered artifact path, and `make compare-rendered-crops` classifies two rendered-crop runs by separating logical evidence identity from rendered artifact byte equality. Cross-platform rendered image determinism is not claimed; the 2026-06-14 macOS arm64 vs Linux x64 validation record in `docs/validation/rendered-crops-2026-06-14.md` preserved document fingerprint and `payload_sha256` but failed rendered artifact byte equality because the evidence bbox differed slightly across platforms.

Still absent or not claimable: reproducible benchmark result JSON, executed competitor comparisons, public speed/quality/footprint claims, OCR/image-only support, real table extraction, mature list/heading/layout semantics, semantic/arithmetic verification beyond deterministic evidence lookup, Phase 2 project-maintained PDFium builds, release packaging, and full frozen-corpus multi-platform determinism evidence.

## Human / External Blockers

PM execution packet: `benchmarks/gate-zero/FREEZE_PACKET.md`.

| ID | Blocker | Required output | Owner | Blocks |
| --- | --- | --- | --- | --- |
| H1 | Generate signed Gate Zero host results | `../ethos-bench/benchmarks/results/gate-zero/{macos-arm64,linux-x64}/g1.json` plus G2/G3 result files are produced from the frozen manifest and pinned lock | Benchmark owner / decider | Valid Gate Zero run, public benchmark trust |
| H2 | Execute pinned competitor comparisons | Harness executes the pinned OpenDataLoader, EdgeParse, LiteParse, and PyMuPDF4LLM artifacts and records signed comparison rows where applicable in `ethos-bench` | Benchmark owner | Public competitor comparison |
| H3 | Accept package identifier ADR | Closed by ADR-0006 acceptance on 2026-06-15 | Devrel / decider | Unblocked package identifier/trademark gate; broader public-release checklist still applies |

The corpus/hardware freeze and direct competitor pins are recorded in `benchmarks/gate-zero/manifest.json` and `benchmarks/competitors.lock.json`. The remaining blockers are result production and signed evidence, not manifest/pin placeholders.

## Current Milestone Posture

Milestone A is partially implemented, not complete. The product can demonstrate a narrow parser-backed grounding loop today, but cannot yet claim Gate Zero readiness or public benchmark credibility.

| Work item | Current status | Remaining blocker |
| --- | --- | --- |
| PDFium Phase 1 profile | Landed: pinned profile, V8/XFA-disabled state, platform hashes, runtime library hashes, and provenance are recorded | Phase 2 project-maintained builds still block Public Beta |
| PDFium loader/runtime checks | Landed: missing/mismatched version, artifact, and runtime library hashes fail deterministically | Release packaging and operator setup path still need hardening |
| Real PDF backend | Landed for simple born-digital PDFs: page count, quantized spans, worker execution, timeout, page filtering, and fingerprint path exist | Wider corpus coverage, failure fixtures, memory-limit behavior, quirk log, and Gate Zero run are still missing |
| Layout groundwork | Landed: basic paragraph text blocks and simple column reading order over quantized spans | Tables, headings, lists, rotation/quirk handling, and confidence policy remain future work |
| Font policy groundwork | Partially landed: substitution table and profile policy are present; fixture output uses deterministic substitution IDs | Bundled fallback asset hashing and broader font/CID validation remain open |
| Schema/example validation | Landed: schemas, examples, deterministic profile, referential integrity, and bbox sanity pass the `jsonschema` validation gate | Contract changes still require explicit versioning and compatibility review |
| Trust-layer implementation | Landed: `ethos verify` quote/value/presence/table-cell checks, explicit quote-containment labeling, normalized equality for value/table-cell checks, stale and unverifiable fingerprint handling, unsupported claim reporting, structured capability limits, native Ethos JSON path, ODL-style adapter path with synthetic table/cell mapping, pinned real OpenDataLoader 2.4.7 grounded/ungrounded fixtures, foreign fixture manifest hash validation, crop-ref evidence plumbing, stable logical native crop refs, native crop descriptor artifacts, raw BGRA crop rendering in `ethos-pdf`, CLI PNG crop artifact production for bound native source PDFs, same-host rendered crop repeatability check, rendered-crop run comparison helper, strict citation/config input validation, citation input schema, and demo fixtures | Still needed: evidence matching against richer source structures, semantic/arithmetic claim handling by explicit non-v1 design, real OpenDataLoader table-cell grounding, broader adapter hardening against real output, and a decision on whether cross-platform rendered crop artifact equality is worth pursuing after the current macOS/Linux bbox drift finding |
| WS-HARNESS readiness | Partially landed: readiness path is green for frozen corpus/hardware and pinned competitors, and fails closed if those records regress | Actual benchmark runner outputs, install-size/RSS/timing collection, competitor execution, and cross-host determinism evidence are still missing |

## PM Rule

Public language stays at "pre-alpha / Milestone A implementation" until the remaining external blockers are closed and Gate Zero has reproducible result JSON. Do not describe Ethos as benchmark-validated, release-ready, or broadly parser-complete. Internal parser work should proceed only when it supports Gate Zero evidence or the trust layer; the product-differentiating path remains verification and grounding first, with parser expansion serving that path.
