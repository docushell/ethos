# Ethos OSS Product And Engineering Requirements (v3.5 OSS-Only)

Status: Revised standalone OSS specification
Date: 2026-06-10
Audience: Ethos maintainers, contributors, AI agents, parser engineers, RAG engineers, and benchmark reviewers

This document describes Ethos as a standalone open-source document parser. It intentionally excludes product-specific hosted integration, commercial packaging, and platform rollout plans. Platform adoption should be documented outside this OSS product requirements file.

---

## 1. Decision Summary

Ethos is an open-source, PDF-first document parser for RAG and AI-agent systems. It starts with born-digital PDFs and a deterministic Rust-native core, then grows toward OCR/VLM, multi-format conversion, and production platforms through optional modules.

The first public promise is intentionally narrow:

> Citation evidence you can prove. A deterministic, runtime-light PDF parser for RAG and agents.

Ethos must not launch as a universal document AI system. It must launch as a reliable parsing primitive with stable artifacts, source coordinates, verifiable citation evidence, and reproducible benchmarks.

### 1.1 Strategic Thesis

The open-source parser market is crowded, but the trust layer remains under-served:

- MarkItDown is excellent for broad lightweight conversion, but not high-fidelity structure, coordinates, or citation verification.
- OpenDataLoader PDF provides strong AI-ready parsing, bboxes, reading order, tables, accessibility/tagging, and hybrid enrichment, but requires a JVM and does not publish a formal deterministic fingerprint contract or parser-level citation verification loop.
- Docling and MinerU are strong on breadth, layout models, OCR/VLM, formulas, charts, and integrations, but they are heavier and model-dependent.
- LiteParse, Kreuzberg, EdgeParse, PyMuPDF, and PyMuPDF4LLM compete on speed and local extraction, but do not own the full parse -> chunk -> cite -> verify -> crop trust loop.

Ethos competes by making trust and repeatability the core product contract:

- same input + same deterministic profile = same canonical output
- every chunk cites stable page/element/bbox references
- citation evidence can be verified deterministically against parsed source regions
- hidden, off-page, low-contrast, annotation, attachment, and action risks are surfaced explicitly
- benchmarks are reproducible, pinned, and honest about tier differences

### 1.2 Build vs Fork Decision Record

OpenDataLoader is Apache-2.0, so the obvious alternative is to fork or pin it. Ethos still builds a new core because the first-order goals require deeper control than a fork gives:

- A fork keeps the JVM runtime tax.
- A fork inherits upstream architecture, schema, and merge-surface constraints.
- Deterministic canonical output and fingerprinting are easier to design into the engine than retrofit.
- Parser-level citation verification needs stable element identities, spans, and coordinate rules from the start.
- Rust gives a better long-term base for small native binaries, bindings, WASM, and security hardening.

Gate Zero keeps this decision honest. If Ethos cannot prove the base parser is meaningfully faster, smaller, and deterministic early, the project must pivot away from parser-core expansion instead of continuing a weak parser-core bet. The parser-agnostic trust layer is not only a fallback: `ethos-verify` must ship as an early alpha over foreign parser output so Ethos can earn adoption even while the native parser matures.

### 1.3 Gate Zero

Gate Zero is a binding pass/fail checkpoint no later than week 4 after implementation kickoff.

The single Gate Zero corpus and hardware profile are frozen before kickoff in `benchmarks/gate-zero/manifest.json`. No document may be added, removed, reweighted, renamed into another corpus, or excluded after kickoff except by an ADR from the named Gate Zero decider before measurements begin.

Gate Zero ownership and hardware profile are no longer open questions:

- Decider: Gate Zero decider, project lead. Gate Zero is a build-vs-pivot business decision, not a committee vote.
- Corpus owner: Gate Zero decider on an interim basis, transferring to the benchmark/devrel owner when staffed.
- Known Gate Zero benchmark hardware: local Mac M4 Pro arm64 and Linux x64 machines recorded in the manifest with exact CPU, RAM, OS, kernel, and runner details. Literal host strings belong in `benchmarks/gate-zero/manifest.json`, not in this PRD.
- Windows x64 joins the nightly determinism matrix no later than Milestone B exit, week 8. Windows failures before Public Beta are tracked as release-blockers-in-waiting; unresolved Windows determinism failure blocks or re-scopes Public Beta.

Gate Zero metrics:

- G1 - Throughput: at least `max(120 pages/sec p50, 2x in-harness remeasured OpenDataLoader pages/sec)` on the manifest's born-digital subset, single CPU core per host. G1 must pass independently on every recorded Gate Zero performance host in `benchmarks/gate-zero/manifest.json`; averaging or substituting results across hosts is not allowed. EdgeParse and LiteParse results are recorded as context, not as gating thresholds.
- G2 - Footprint: base distributable install footprint no more than 30 MB, with PDFium V8 and XFA disabled. The measurement includes CLI, native dynamic libraries, PDFium sidecar/static payload, default schemas, bundled deterministic font assets, and all assets required to run the base parser without network access. The Ethos/OpenDataLoader installed-footprint ratio is still measured; the "no more than one tenth of OpenDataLoader" statement is a public claim threshold, not a hard parser-core decision threshold (ADR-0008).
- G3 - Determinism: byte-identical canonical document payload across the Gate Zero supported platforms, at minimum macOS arm64 and Linux x64 under the deterministic profile on the full frozen manifest. Windows x64 determinism is a public-beta release blocker even if it is not part of the first local Gate Zero hardware set.

Decision rule:

- All G1/G2/G3 pass: continue to Milestone B.
- G2 or G3 fail: stop the parser-core expansion track and continue with `ethos-verify` plus chunk/citation tooling as a standalone parser-agnostic OSS layer over foreign parser output.
- G1 fails while G2 and G3 pass: the named Gate Zero decider records an ADR choosing either immediate parser-core fallback or one bounded performance-remediation retry. A retry must finish no later than week 6, may not change the frozen corpus, and cannot be used to make public speed claims until G1 passes.
- G1 fails again after the bounded retry: stop the parser-core expansion track and continue the parser-agnostic trust layer.

There is no documented-gap escape for G2 or G3. G1 may receive only the single explicit retry path above.

### 1.4 Product Wedge

Ethos' wedge ranking:

1. Citation evidence verification: parse -> chunk-with-bbox-citations -> verify -> crop as one deterministic loop.
2. Determinism as a contract: versioned canonicalization, profile fingerprinting, cross-platform CI, and semver treatment for output drift.
3. Runtime weight: no JVM, no Python ML stack, no GPU, no OCR model downloads in the base parser.
4. Public failure corpus: designed but not earned. It becomes a claimable advantage only after legal/consent rules, public fixture process, and published robustness delta exist.

Ethos does not claim pixel-level proof, semantic entailment, arithmetic truth, OCR quality, VLM-level chart understanding, or universal format support in the first release.

### 1.5 Trust Layer Alpha

`ethos-verify` is an early product surface, not fallback-only salvage.

The first alpha must prove that Ethos can verify citation evidence over at least one foreign parser output before the full native parser reaches public beta. The alpha scope is:

- `GroundingSource` trait and verification schemas.
- `ethos verify` CLI command.
- OpenDataLoader JSON grounding adapter as the first foreign adapter.
- Capability-driven downgrade warnings for missing spans, fingerprints, crop support, or coordinate metadata.
- A parser-agnostic demo that verifies citations over foreign parser output and, where possible, returns source-region crops for inspection.

This alpha is allowed to carry an experimental label. It must not be blocked by native parser table quality, Node bindings, MCP, OCR, VLM, or multi-format support.

---

## 2. Competitive Landscape

Validated: 2026-06-10. The landscape must be refreshed before each major milestone and at least every 90 days.

| Project | License / Community Signal | Strengths | Gaps Ethos Targets | Ethos Posture |
| --- | --- | --- | --- | --- |
| OpenDataLoader PDF | Apache-2.0; approx. 24.3k stars in June 2026 snapshot | Bboxes, reading order, tables, hidden text handling, Markdown/JSON/HTML, accessibility/tagging, hybrid enrichment | JVM runtime, no formal canonical determinism contract, no local parser-level citation verification loop | Reference competitor. Match non-OCR fundamentals; win on runtime, determinism, verification, and benchmarks. Record its local deterministic mode as G1 context, not as a replacement for Ethos' gate. |
| LiteParse | Apache-2.0; approx. 9.8k stars in June 2026 snapshot | Lightweight PDFium-based spatial extraction, local execution, Python/Node/WASM orientation | Narrower trust/security/verification story | Closest Release 1 overlap. Compete on full RAG artifact model and verification. |
| Docling | MIT; LF AI & Data project; approx. 61.3k stars in June 2026 snapshot | Broad formats, DoclingDocument provenance, OCR/layout models, tables, formulas, integrations | Heavier Python/ML stack, model components, larger runtime | Interoperate. Do not clone breadth in Release 1. |
| MinerU | Custom/source-available model constraints; approx. 67.1k stars in June 2026 snapshot | Strong OCR/VLM/document-understanding quality, formulas/charts/tables, CJK strength | Heavy model path, non-deterministic VLM tier, license complexity for default OSS dependencies | Concede VLM accuracy initially; add optional enrichment later outside the base install. |
| MarkItDown | MIT; approx. 150k stars in June 2026 snapshot | Simple broad conversion for LLM workflows | Not high-fidelity structure, coordinates, tables, or verification | Beat on PDF RAG trust, not breadth. |
| Marker | GPL-3.0 plus model/weight considerations; approx. 36k stars in June 2026 snapshot | Strong Markdown conversion and optional LLM quality boost | Python/ML runtime, weaker deterministic trust contract, restrictive default-license posture | Beat on provenance, security report, verification, and permissive base licensing. |
| EdgeParse | Approx. 117 stars in June 2026 snapshot | Pure Rust, deterministic positioning, bboxes, Markdown/JSON/HTML/text, fast local runtime, WASM surface | Early community signal, self-reported benchmark, no published verification loop or formal fingerprint contract | Track, but do not over-rank as a near-term adoption threat unless community or feature velocity materially changes. |
| Kreuzberg | Tracked in `docs/landscape-log.md` | Rust-oriented document processing, MCP-friendly direction, broad developer ergonomics | License/adoption questions, less specialized PDF trust contract | Track and benchmark; interoperate where useful. |
| Unstructured | Tracked in `docs/landscape-log.md` | Enterprise ETL, partitioning, connectors | Heavy local path, broad ETL rather than deterministic PDF engine | Provide compatibility adapters later. |
| PyMuPDF/PyMuPDF4LLM | AGPL/commercial licensing considerations | Fast local extraction and mature PDF primitives | Less opinionated about canonical schema, verification, security report | Benchmark and use as baseline; do not make it a default Apache-2.0 dependency. |
| Hosted parsers | Commercial | Scale, UI, managed APIs, commercial support | Not local-first, not pinnable, data leaves boundary | Demand evidence, future adapter targets. |

Community and license numbers are a June 2026 snapshot. Exact counts must be refreshed in `docs/landscape-log.md`, not treated as permanent PRD facts.

### 2.1 LiteParse Overlap And Differentiation

LiteParse is the closest overlap for Ethos' Release 1 parser-core surface. It already covers fast local PDF parsing, PDFium-based spatial text extraction, bounding boxes, JSON/text output, screenshots, OCR options, Rust/Node/Python/WASM surfaces, and multi-platform distribution.

Ethos must therefore not position itself as merely a fast local parser with bounding boxes. That would be a weak and already occupied lane.

Ethos' required differentiation against LiteParse:

- Canonical deterministic document graph, not just structured extraction output.
- Versioned output fingerprint and deterministic profile that can be pinned in CI.
- RAG-first artifacts from day one: canonical JSON, Markdown, text, chunks, security report, verification report, and debug overlay.
- Citation evidence verification as a first-class product surface: parse -> chunk -> cite -> verify -> crop.
- Parser-agnostic `GroundingSource` adapters so Ethos can verify foreign parser output, including future LiteParse adapters if useful.
- Security report semantics: hidden, off-page, low-contrast, annotation, action, attachment, and external-link handling with default exclusion from chunks.
- Reproducible benchmark discipline with LiteParse included as a pinned reference competitor.

If Ethos cannot beat or match LiteParse on raw speed and footprint, Ethos can still justify itself only if the deterministic graph, citation verification, security report, and benchmark credibility are clearly stronger. If those trust-layer features slip, Ethos risks becoming a redundant parser.

Explicit non-moats:

- Bounding boxes alone.
- Markdown export alone.
- Hidden-text filtering alone.
- Local execution alone.
- Pure "deterministic" marketing language without a versioned contract.

---

## 3. Product Brief

### 3.1 Naming

Project rename decision: the project name is Ethos.

Package identifiers to validate before public publishing:

- Repository: `ethos`
- CLI binary: `ethos`
- Public architecture modules: `ethos-doc`, `ethos-rag`, `ethos-verify`
- Reserved public package/module names: `ethos-doc`, `ethos-rag`, `ethos-verify`, even if `ethos-doc` and `ethos-rag` remain facade modules rather than published crates.
- Public Rust package identifiers: `ethos-doc-core`, `ethos-pdf`, `ethos-layout`, `ethos-rag`, `ethos-verify`
- Internal Rust namespace: `ethos_core` and sibling crates
- Python package: `ethos-pdf`
- Python import: `ethos_pdf`
- Node package: `@ethos-pdf/core`
- MCP package: `ethos-mcp`

The name decision is closed, but registry availability, trademark risk, and discoverability must still be validated before public package publication. If a specific package identifier is unavailable, rename that package identifier by ADR before any public package, benchmark artifact, or launch announcement.

### 3.2 Primary Users

- RAG engineers parsing PDF-heavy corpora who need verifiable citations.
- AI-agent developers who need local tools for parse, search, crop, and cite verification.
- Eval and CI engineers who need stable parser output and diffable fingerprints.
- Data engineers processing high-volume born-digital PDFs on CPU.
- Security-conscious teams that need hidden-content and suspicious-feature reporting.
- OSS maintainers who want reproducible parser benchmarks instead of unverifiable leaderboard claims.

### 3.3 North-Star Metrics

| Metric | Target |
| --- | --- |
| Base install footprint | <= 30 MB hard gate; <= 1/10 measured OpenDataLoader install footprint is a claim threshold (ADR-0008) |
| Born-digital throughput | Gate Zero G1: >= `max(120 pages/sec p50, 2x remeasured OpenDataLoader pages/sec)` unless the one-time G1-only remediation ADR is active; no public speed claim until G1 passes |
| Determinism | Byte-identical canonical payload across macOS arm64, Linux x64, Windows x64 under profile |
| Citation evidence verification | Deterministic match report for supported citation modes |
| Trust-loop activation | Users can run parse -> chunk -> verify -> crop in one documented workflow, including at least one foreign-parser verification path |
| Time to first parse | New user can install, parse a local born-digital PDF, and inspect chunks/citations from the quickstart without custom build steps |
| Public reproducibility | One-command benchmark reproduction with pinned competitor versions |
| RAG usefulness | Chunks include stable source references and page/bbox provenance |
| Security | Hidden/off-page/low-contrast text excluded from default chunks |
| OSS health | OpenSSF Scorecard tracked, median public issue first response target under 48 hours after public launch |

---

## 4. Product Scope

### 4.1 Release 1 - Digital PDF Core

Release 1 must support born-digital PDFs without OCR. The stable Release 1 surfaces are the CLI and Python package. Node is a functional beta surface, and MCP is an experimental agent surface during the Release 1 window with GA eligibility in Release 2.

Required capabilities:

- Rust parser core.
- Stable CLI.
- Stable Python package.
- Functional Node package labeled beta.
- Experimental MCP server labeled experimental in the Release 1 window.
- Canonical JSON document graph.
- Deterministic Markdown export.
- Plain text export.
- RAG chunks with page/element/bbox citations.
- Page selection.
- Rotation and coordinate normalization.
- Password, corrupt, encrypted, and scanned/image-only detection.
- Text spans with stable source references where backend support allows.
- Heading, paragraph, list, and basic reading-order inference.
- Simple/bordered table detection and structured table output.
- Non-text region detection with stable coordinates. Type labels such as image, chart, or formula are optional and must be marked experimental unless they satisfy deterministic Release 1 quality gates.
- Security report for hidden/off-page/low-contrast text, annotations, actions, attachments, scripts, and external links.
- Verification report for supported citation evidence checks.
- Parser-agnostic verification over at least one foreign parser output through `GroundingSource`.
- Debug HTML overlay for visual inspection.
- Benchmark harness against OpenDataLoader, EdgeParse, LiteParse, PyMuPDF4LLM, and other feasible baselines.
- Launch examples for RAG citation verification and lightweight LangChain/LlamaIndex ingestion through the Python API.

Release 1 must not claim support for:

- OCR.
- Handwriting.
- VLM image understanding.
- Stable chart/formula/image semantic classification.
- Chart semantic descriptions.
- Complex/borderless table reconstruction.
- Full LaTeX formula extraction.
- Multi-format Office/email/archive conversion.
- PDF mutation or PDF/UA compliance.

### 4.2 Release 2 - Structure Enrichment

Release 2 should move toward non-OCR feature parity with the strongest local parser capabilities:

- Complex and borderless table reconstruction.
- Multi-row/multi-column header handling.
- Merged-cell inference.
- Cross-page table continuation detection.
- Formula region classification.
- LaTeX extraction where a deterministic or bounded optional model path exists.
- Chart region classification.
- Image/chart/formula region classification when backed by fixtures and quality metrics.
- Image extraction and stable image references.
- Optional image/chart description hooks through a non-base enrichment module.
- Better hierarchy inference for annual reports, scientific PDFs, policies, and financial documents.

Release 2 may introduce `ethos-layout-ml` as an optional module. It must not increase the base parser footprint or make the base output nondeterministic.

### 4.3 Release 3 - OCR/VLM Extensions

OCR and VLM support are optional extension tracks, not base-parser requirements.

Potential adapters:

- Tesseract.
- PaddleOCR.
- Surya.
- DocTR.
- Cloud OCR clients.
- VLM captioning/description providers.
- Layout and table models through ONNX CPU execution.

Rules:

- OCR/VLM modules are disabled by default.
- OCR/VLM modules and their transitive dependencies must not enter the default install path.
- Copyleft, AGPL, source-available, or custom-condition dependencies are not allowed in the base install path. Optional adapters that require such dependencies must live in separate packages or features, be disabled by default, and publish explicit license manifests.
- OCR/VLM outputs are labeled as enrichment tier, not deterministic base tier.
- OCR/VLM benchmark results are separated from born-digital deterministic results.
- Model versions, weights, providers, prompts, and hardware must be recorded in output metadata.

### 4.4 Release 4 - Multi-Format And Platform

After PDF core credibility is established, Ethos can broaden into:

- DOCX.
- PPTX.
- XLSX.
- HTML.
- EPUB.
- Emails.
- Images.
- Archives of documents.
- Hosted API wrappers.
- Batch processing.
- Desktop or web review tools.
- Compliance workflows.

This breadth must not dilute the PDF trust contract. PDF remains the reference implementation for deterministic schema, citation verification, and benchmark discipline.

---

## 5. Architecture Requirements

### 5.1 Principles

- JSON graph is canonical; all exports are derived from it.
- Markdown is a user artifact, not the source of truth.
- Determinism is a release contract, not a best-effort note.
- PDFs are hostile input.
- No network calls in the base parser.
- Base parser has no JVM, no Python ML stack, no GPU, no OCR models, no runtime downloads.
- Every public output shape is schema-versioned.
- Output-changing heuristics require a version bump and changelog entry.
- Parser backends are hidden behind explicit traits.
- Verification must remain parser-agnostic through `GroundingSource`.

### 5.2 Public Architecture

Ethos should present a simple three-part public architecture:

```text
Ethos
├── ethos-doc
│   Document parsing, structure, and canonical document graph
│
├── ethos-rag
│   Chunking, citation references, and retrieval-ready artifacts
│
└── ethos-verify
    Evidence, grounding, fingerprint, and citation verification
```

Public module responsibilities:

| Public module | Release 1 responsibility | Not a Release 1 claim |
| --- | --- | --- |
| `ethos-doc` | Parse born-digital PDFs into a stable canonical document graph with pages, elements, spans, tables, non-text regions, warnings, and deterministic fingerprints. | OCR, VLM understanding, semantic chart interpretation, handwriting, or universal format conversion. |
| `ethos-rag` | Turn the document graph into deterministic Markdown, text, chunks, source refs, page refs, element refs, and bbox-backed citation artifacts for RAG systems. | Retrieval engine hosting, vector database ownership, answer generation, or semantic truth scoring. |
| `ethos-verify` | Verify whether supported citations and evidence references are grounded in source document regions, table/cell/text evidence, fingerprints, and adapter capabilities. | Proving answer truth, semantic entailment, arithmetic correctness, or pixel-level proof. |

`ethos-doc` may be described as the long-term document-understanding layer, but Release 1 public wording must prefer "document parsing and structure" or "canonical document graph" to avoid implying OCR/VLM-quality understanding.

The public architecture is a product/API boundary. Internally, Ethos may keep finer-grained crates such as `ethos-core`, `ethos-pdf`, `ethos-layout`, `ethos-tables`, `ethos-security`, and `ethos-render`. Per ADR-0006, the public crates.io package name for the internal core crate is planned as `ethos-doc-core`, not `ethos-core`.

### 5.3 Repository Layout

Target layout:

```text
ethos/
  crates/
    ethos-core/          # canonical document model, IDs, errors, schema types
    ethos-pdf/           # physical PDF backend abstraction and implementations
    ethos-layout/        # reading order, blocks, headings, lists
    ethos-layout-ml/     # optional ONNX/model tier, not base
    ethos-tables/        # table detection and structure
    ethos-rag/           # chunking, citation model, exporters
    ethos-security/      # hidden/off-page/annotation/action report
    ethos-verify/        # parser-agnostic citation evidence verification
    ethos-render/        # crops, overlays, optional rendering
    ethos-cli/           # CLI
    ethos-mcp/           # experimental Release 1 agent surface; GA candidate in Release 2
  bindings/
    python/
    node/
    wasm/
  adapters/
    grounding/
    docling/
    unstructured/
    eval/
    langchain/          # Release 1 examples first; maintained adapter later if adoption warrants
    llamaindex/         # Release 1 examples first; maintained adapter later if adoption warrants
  schemas/
  fixtures/
  benchmarks/
  docs/
  examples/
```

### 5.4 Core Pipeline

Pipeline stages:

1. Ingest: validate file, page count, encryption, corruption, scan/image-only signals.
2. Extract: text spans, glyph geometry, images, paths, annotations, metadata.
3. Normalize: coordinates, rotation, fonts, page boxes, deterministic quantization.
4. Layout: lines, blocks, reading order, headings, lists.
5. Tables: detect tables, cells, headers, merged cells, confidence and warnings.
6. Regions: detect non-text regions with stable coordinates; optional image/chart/formula labels move to enrichment unless deterministic quality gates are met.
7. RAG: chunk graph into citation-bearing chunks.
8. Security: hidden/off-page/low-contrast text, annotations, actions, attachments, scripts, links.
9. Verify: evidence checks against text/table/cell regions and source fingerprint.
10. Render: crops and debug overlays.
11. Export: JSON, Markdown, text, chunks, reports, overlays.

Deterministic geometry quantization happens before layout/table/chunk/reading-order heuristics consume coordinates.

### 5.5 GroundingSource Trait

`ethos-verify` consumes parser output through a `GroundingSource` trait, not Ethos-internal structs.

Required trait data:

- parser identity: name, version, adapter version
- document fingerprint if available
- page geometry: width, height, rotation, coordinate system, origin
- elements: id, page, bbox, text, type
- optional spans with char offsets
- capabilities declaration: spans, char offsets, fingerprint, coordinate origin, crop support

Capability-driven downgrades are explicit. Missing spans, missing fingerprints, or foreign coordinate systems must appear as `capability_limited` warnings in the verification report.

---

## 6. PDF Engine Policy

### 6.1 PDFium Candidate Backend

PDFium remains the Release 1 candidate backend, but only through the canonical upstream source and only behind `EthosPdfBackend`.

Important constraint: the archived `chromium/pdfium` GitHub repository is a mirror. The canonical source is the active PDFium repository at `pdfium.googlesource.com`. Ethos must not treat the archived GitHub mirror as the source of truth.

ADR-0002 decision: PDFium uses a two-phase distribution path.

- Phase 1, Milestone A / Gate Zero: use pinned `bblanchon/pdfium-binaries` artifacts with V8 and XFA disabled, by exact release/version and per-platform hash. Gate Zero may run on this Phase 1 path.
- Phase 2, by Milestone E / Public Beta: move to project-maintained PDFium builds from `pdfium.googlesource.com`, with pinned source revision, recorded build flags, toolchain, patches, and per-platform hashes.
- Public Beta must not ship on Phase 1 binaries. If project-maintained builds are not ready by Milestone E, Public Beta is blocked or re-scoped.

Base PDFium requirements:

- V8 disabled.
- XFA disabled.
- Source revision pinned.
- Build flags recorded.
- Toolchain recorded.
- Platform binary hash recorded.
- Patches recorded.
- Distribution method recorded.
- Deterministic font profile recorded.
- Geometry quantization recorded.

Base PDFium builds with V8 or XFA enabled fail the security review and Gate Zero footprint/security profile.

### 6.1.1 Deterministic Font Policy

ADR-0003 decision:

- Embedded PDF fonts are always preferred.
- Missing-font handling goes through a versioned `font-substitution-table.json`.
- The Release 1 fallback bundle is the Liberation family under SIL OFL 1.1, expected footprint about 4 MB, chosen for metric compatibility with the standard-14 PDF font territory.
- PDFium font mapping must be overridden to use the bundled deterministic font profile instead of system font fallback.
- Glyph misses emit deterministic `.notdef` output plus a stable warning code.
- Non-embedded CJK font fallback is out of Release 1; it must warn clearly instead of silently using system fonts.

The deterministic font profile is part of the parser profile manifest and Gate Zero determinism evidence.

### 6.2 Alternatives And Fallbacks

Alternatives to evaluate:

- pdf.js: strong Apache-2.0/browser/WASM story, likely weaker native performance and extraction ergonomics.
- Poppler: mature but GPL licensing makes it unsuitable as the default Apache-2.0 core dependency.
- MuPDF/PyMuPDF: excellent technically, but AGPL/commercial licensing is not suitable as the default Apache-2.0 core dependency.
- Pure Rust physical parser: best long-term safety/control, too large for Release 1 unless Gate Zero forces a reset.
- Existing wrappers: useful for spike learning, not enough for final build provenance and deterministic profile control.

Ethos must keep the backend swappable. Public schemas and APIs must not expose PDFium-specific types.

### 6.3 Sandbox Policy

PDFium is C++ parsing hostile input. Hosted or service deployments must run it through sandbox/subprocess mode with:

- CPU limit.
- Memory limit.
- Wall-time limit.
- File-descriptor limit.
- Output-size limit.
- Page-count limit.
- No network.
- No child process spawning.
- No shell execution.
- No arbitrary filesystem access.
- Narrow IPC returning only normalized graph data or stable errors.

In-process PDFium is allowed only for local/offline CLI usage with an explicit threat model.

---

## 7. Artifact Contract

Release 1 must emit more than JSON. JSON is canonical, but users need practical RAG artifacts from day one.

Required artifacts:

| Artifact | Purpose | Source of Truth |
| --- | --- | --- |
| `ethos.json` | Canonical document graph | Primary |
| `document.md` | Deterministic Markdown for RAG/humans | Derived from JSON |
| `document.txt` | Plain text for search and simple indexing | Derived from JSON |
| `chunks.jsonl` | RAG chunks with source refs | Derived from JSON |
| `security_report.json` | Hidden/off-page/annotation/action/attachment report | Derived from JSON/security pass |
| `verification_report.json` | Citation evidence checks | Derived from JSON + citation input |
| `debug.html` | Visual overlay for inspection | Derived from JSON + render/crop layer |

Rule: every derived artifact must be reproducible from the canonical JSON plus versioned config.

---

## 8. Canonical Data Model

The canonical document graph must include:

- schema version
- parser version
- deterministic profile
- source fingerprint
- canonical document payload fingerprint
- pages
- elements
- spans
- tables
- chunks
- non-text regions with stable coordinates and optional image/figure/formula/chart labels
- security warnings
- parser warnings
- runtime diagnostics outside canonical equality

Element fields:

- stable id
- type
- page
- bbox
- normalized coordinate system
- text when applicable
- confidence where applicable
- source span refs where available
- warning refs

Table fields:

- stable id
- page refs
- bbox
- cells
- rows/columns
- header rows/columns
- row span / col span
- confidence
- structure warnings
- optional CSV/Markdown derived exports

Chunk fields:

- stable id
- text
- source element refs
- page refs
- bbox refs
- token estimate with pinned estimator or explicit approximate flag
- warnings inherited from source regions

Verification report fields:

- document fingerprint
- verification config hash
- all evidence grounded boolean
- staleness check
- capability warnings
- per-check status
- per-check match method
- per-check `semantic_unverified` boolean
- unsupported claim kind handling
- stable warning codes

`all_evidence_grounded` is true only when at least one supported check exists, every supported check is grounded, no check is semantically unverified, no unsupported claim kind is present, and the fingerprint is not stale.

---

## 9. CLI And API Requirements

### 9.1 CLI

```bash
# ethos-doc: document parsing and canonical graph
ethos doc parse report.pdf --format json --out report.ethos.json
ethos doc parse report.pdf --format markdown --out report.md
ethos doc parse report.pdf --format text --out report.txt

# ethos-rag: chunks and retrieval-ready artifacts
ethos rag chunk report.ethos.json --out chunks.jsonl

# Multiple derived artifacts
ethos doc parse report.pdf --formats json,markdown,text,chunks,security_report --out out/

# Page selection
ethos doc parse report.pdf --pages 1-5,9 --format json --out out/

# Debug overlay
ethos debug report.pdf --out debug/

# Security report
ethos inspect report.pdf --security --out security_report.json

# Citation evidence verification
ethos verify report.ethos.json --citations answer_citations.json --out verification_report.json

# Foreign parser output through adapter
ethos verify foreign_output.json --grounding opendataloader-json --citations answer_citations.json

# Determinism check
ethos fingerprint report.pdf

# Batch audit
ethos audit ./pdfs --out audit.json
```

`ethos parse` may exist as a convenience alias, but public documentation should prefer the module-shaped commands: `ethos doc`, `ethos rag`, and `ethos verify`.

### 9.2 Python

```python
from ethos_pdf import parse_pdf

result = parse_pdf("report.pdf", formats=["json", "markdown", "chunks"])
print(result.document.fingerprint)
```

```python
from ethos_pdf.verify import verify_citations

report = verify_citations("report.ethos.json", "answer_citations.json")
assert report.all_evidence_grounded
```

### 9.3 Node

Node is a functional beta surface in Release 1. It must be usable for local parse and verification workflows, but it is not a GA blocker for the stable CLI/Python Release 1 surface.

```ts
import { parsePdf, verifyCitations } from "@ethos-pdf/core";

const result = await parsePdf("report.pdf", { formats: ["json", "markdown", "chunks"] });
const verification = await verifyCitations(result.document, citations);
```

### 9.4 MCP

MCP is experimental in the Release 1 window and a GA candidate for Release 2. Release 1 MCP work exists to prove the agent workflow, not to expand the stable API surface beyond CLI and Python.

Experimental Release 1 MCP tools:

- `parse_pdf`
- `get_document`
- `get_page`
- `get_element`
- `get_table`
- `get_chunk`
- `crop_element`
- `search_text`
- `verify_citations`
- `get_security_report`
- `get_fingerprint`

MCP security rules:

- Only parse files under allowlisted roots or MCP-provided file handles.
- Reject `~`, symlink escape, URL paths, network paths, parent traversal, and globs by default.
- Use opaque document ids.
- Use short TTL memory-backed document stores by default.
- Enforce size, page, time, crop, search, and concurrency limits.
- Search parsed graph only.
- Crop only already parsed documents.
- Exclude suspicious hidden/off-page/low-contrast content from default search and chunks unless explicitly requested.

---

## 10. Security Requirements

Ethos treats PDFs as hostile input.

Base requirements:

- max file size
- max page count
- max parse time
- memory budget where possible
- stable corrupt/encrypted/password/image-only errors
- no embedded JavaScript execution
- no XFA in base build
- no external link following
- no external resource fetches
- annotations/actions/attachments/scripts surfaced in report
- hidden/off-page/low-contrast text detected and excluded from default chunks
- stable failure codes
- sandbox/subprocess mode for service deployments

Stable error codes:

- `invalid_pdf`
- `corrupt_pdf`
- `password_protected`
- `page_limit_exceeded`
- `file_too_large`
- `ocr_required`
- `unsupported_pdf_feature`
- `parse_timeout`
- `memory_limit_exceeded`
- `internal_error`

Stable warning codes:

- `low_confidence_reading_order`
- `low_confidence_table_structure`
- `hidden_text_detected`
- `off_page_text_detected`
- `low_contrast_text_detected`
- `annotations_present`
- `external_links_present`
- `image_only_page`
- `unsupported_annotation`
- `partial_parse`
- `capability_limited`

---

## 11. Benchmark Plan

Benchmark credibility is part of the product.

### 11.1 Categories

Performance:

- pages/sec
- docs/sec
- cold start
- warm start
- peak memory
- install size
- p50/p95/p99 latency

Quality:

- text fidelity
- reading order
- heading hierarchy
- table detection F1
- table structure accuracy
- cell text accuracy
- bbox IoU
- chunk usefulness

Trust:

- citation evidence verification accuracy
- hidden text exclusion
- deterministic fingerprint stability
- stable failure behavior
- warning precision/recall on security fixtures

### 11.2 Competitors And Suites

Run where licensing and setup allow:

- OpenDataLoader PDF
- EdgeParse
- LiteParse
- Kreuzberg
- Docling
- MinerU
- Marker
- MarkItDown
- Unstructured
- PyMuPDF
- PyMuPDF4LLM

Suite policy:

- OmniDocBench is neutral/community.
- ParseBench is publisher-owned by LlamaIndex/run-llama and must be labeled as such.
- Competitor-owned suites may be run but must be labeled as publisher-owned.
- Ethos' own fixtures must not be presented as neutral.

### 11.3 Rules

- No ranking claims.
- No superlative claims.
- Publish commands, environment, hardware, versions, and failures.
- Separate born-digital deterministic results from OCR/VLM results.
- Label model tier vs deterministic tier in every table.
- Use one-command reproduction for published tables.
- Pin competitor versions and dates.
- Re-run reference competitors after major releases.

### 11.4 Launch Demos

Release 1 must include proof-of-trust demos, not only parser examples:

- RAG demo: parse -> chunks -> answer citation refs -> deterministic verification report.
- Agent demo: parse -> retrieve chunk -> verify citation -> crop source region for inspection.
- Foreign parser demo: verify citations over OpenDataLoader JSON through the `GroundingSource` adapter.
- Ecosystem examples: lightweight LangChain and LlamaIndex examples over the Python API. Full maintained loaders are Release 2 or later unless adoption justifies earlier ownership.

These demos are part of the launch package and must use pinned fixtures, not private cherry-picked PDFs.

---

## 12. Open-Source Governance And License

License: Apache-2.0 for Ethos Core.

Contribution governance: Developer Certificate of Origin, not CLA. CI must enforce signed-off commits.

Rationale:

- Apache-2.0 maximizes enterprise and OSS adoption.
- DCO keeps inbound and outbound contribution posture simple.
- Restrictive licenses such as AGPL or source-available licenses may reduce cloud-clone risk but would also reduce adoption and ecosystem trust.
- Optional OCR/VLM model weights, hosted services, enterprise workflows, or managed platforms can use separate terms without weakening Ethos Core adoption.

Required repository documents:

- `LICENSE`
- `README.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `GOVERNANCE.md`
- `MAINTAINERS.md` or an equivalent maintainer-ladder section in `GOVERNANCE.md`
- `CODE_OF_CONDUCT.md`
- `docs/architecture.md`
- `docs/determinism-contract.md`
- `docs/pdfium-profile.md`
- `docs/benchmark-plan.md`
- `docs/landscape-log.md`
- schema documentation
- fixture contribution guide

Governance requirements:

- Public maintainer ladder with reviewer, maintainer, and release-owner responsibilities.
- Public roadmap cadence tied to milestones and 90-day landscape refreshes.
- Public discussion channel for design questions and user feedback.
- Issue templates for bugs, parser failures, benchmark questions, security reports, and adapter requests.
- Triage target: median first maintainer response under 48 hours after public launch, measured monthly.
- Good-first-issue labels and fixture-contribution path for community onboarding.
- OpenSSF Scorecard tracked after public launch, with security regressions treated as release blockers.

Dependency and license boundary:

- Base install dependencies must be compatible with the approved ADR-0004 allowlist: Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, Zlib, Unicode-DFS, CC0, and MPL-2.0.
- GPL, AGPL, LGPL, source-available, custom-condition, or model-license-restricted dependencies are denied in the base dependency tree, including through optional modules' default features.
- Optional OCR/VLM/layout-ML integrations that need restricted dependencies must live behind explicit non-default features or separate packages and publish license manifests.
- Exceptions require an ADR before merge.
- CI must enforce the base dependency policy through `cargo-deny` or equivalent tooling plus review of generated third-party notices.
- `NOTICE` must be maintained and include at minimum PDFium BSD-3 notices and Liberation font SIL OFL 1.1 notices.

README positioning:

```text
Ethos is a fast, deterministic, runtime-light PDF parser for RAG and AI
agents. It turns born-digital PDFs into an auditable document graph:
JSON, Markdown, text, chunks, tables, citations, coordinates, crops,
and security warnings.

Ethos can verify citation evidence against the parsed source and return
the source crop for inspection.

One small native parser. No JVM. No Python ML stack. No GPU. No OCR model
in the base install. Same input, same pinned profile, same canonical
output.

Ethos is not an OCR engine yet, and it does not claim to beat VLM parsers
on complex scanned layouts. It is built for teams that need trustworthy,
fast, local PDF parsing with verifiable source grounding.
```

---

## 13. Release Plan

### Milestone A - Gate Zero

Deliverables:

- Ethos package-name registry and trademark validation before A exit.
- Initial governance files: `GOVERNANCE.md`, public roadmap, discussion-channel plan, issue templates, and triage SLO.
- PDFium Phase 1 integration using pinned `bblanchon/pdfium-binaries` V8/XFA-disabled artifacts by exact version and per-platform hash.
- PDFium Phase 2 plan for project-maintained `pdfium.googlesource.com` builds by Milestone E.
- License sign-off recorded in ADR-0004 with DCO CI enforcement, cargo-deny allowlist, denied-license policy, and NOTICE obligations.
- Deterministic font bundle and font mapper override using embedded fonts, `font-substitution-table.json`, and bundled Liberation fallback.
- Pre-layout geometry quantization.
- Sandbox/subprocess feasibility report.
- Frozen Gate Zero corpus and hardware manifest.
- JSON schema drafts.
- Verification report schema draft.
- Rust workspace.
- CLI skeleton.
- Basic text/span extraction.
- Determinism fingerprint and canonicalization profile.
- Benchmark harness with G1/G2/G3 measurements.

Exit:

- Gate Zero pass/fail ADR recorded.
- G2/G3 failure stops parser-core expansion and continues parser-agnostic verification/chunker work.
- G1-only failure records either immediate fallback or the single bounded remediation retry.

### Milestone B - Layout And Exports

Deliverables:

- Reading order.
- Block grouping.
- Heading/list inference.
- Markdown exporter.
- Text exporter.
- Python binding.
- `ethos-verify` alpha over `GroundingSource`.
- OpenDataLoader JSON grounding adapter alpha.
- Parser-agnostic verification demo over foreign parser output.

Exit:

- Multi-column fixtures read correctly.
- Markdown and text artifacts are useful for RAG.
- Python package parses local PDFs.
- `ethos verify` can produce a capability-aware verification report over at least one foreign parser output.

### Milestone C - Tables, Chunks, Debug Overlay

Deliverables:

- Simple table detection.
- Cell model.
- RAG chunker.
- Citation model.
- Non-text region detection with stable coordinates.
- Debug HTML overlay with click-to-highlight.
- Security report.

Exit:

- Common tables retain structure.
- Chunks cite source bboxes.
- Non-text regions carry stable coordinates without claiming semantic chart/formula/image understanding.
- Hidden/off-page text is excluded from default chunks.

### Milestone D - Agents And Verification

Deliverables:

- Functional Node binding labeled beta.
- MCP server labeled experimental.
- Crop API.
- `verify_citations` v1 hardening from the Milestone B alpha.
- `GroundingSource` trait.
- OpenDataLoader JSON grounding adapter.
- Capability downgrade warnings.

Exit:

- Agent can parse, chunk, cite, verify, and crop.
- Verification works over at least one foreign parser output.
- Node and MCP have smoke-tested beta/experimental docs, but neither is a stable Release 1 blocker.

### Milestone E - Public Beta

Deliverables:

- Public benchmark report, pairing known Gate Zero host results with cloud-runner numbers reproducible by third parties. Laptop-only or local-host-only numbers must never be marketed alone.
- Honest-scope README.
- Stable CLI and Python docs.
- Node beta docs.
- MCP experimental docs.
- Proof-of-trust launch demos: RAG citation verification, agent verify+crop, and foreign-parser verification.
- Lightweight LangChain/LlamaIndex examples over the Python API.
- Schema compatibility tests.
- Determinism CI.
- Windows x64 determinism matrix green, or Public Beta explicitly re-scoped before launch.
- Project-maintained PDFium Phase 2 builds from `pdfium.googlesource.com`, with pinned source revision, flags, toolchain, patches, and per-platform hashes.
- Release artifacts for target platforms.

Exit:

- Reproducible benchmark methodology.
- Public benchmark tables include third-party reproducible cloud-runner numbers next to recorded Gate Zero host numbers.
- Users can install the stable CLI/Python surfaces, parse, inspect, chunk, and verify born-digital PDFs.
- Public Beta does not ship on Phase 1 `bblanchon/pdfium-binaries`; Phase 2 PDFium builds are present or the release is blocked/re-scoped.
- Windows x64 determinism is green in the nightly matrix or the release is blocked/re-scoped.
- Node beta and MCP experimental workflows are clearly labeled and do not expand the stable API promise.

### Milestone F - Release 2 Enrichment

Deliverables:

- Complex table workstream.
- Formula region and LaTeX workstream.
- Image/chart region workstream.
- Optional enrichment module strategy.
- Multi-format feasibility report.

Exit:

- Release 2 scope is backed by fixtures, benchmarks, and module boundaries.

---

## 14. Agent Instructions For Future Implementers

- Keep Ethos OSS-only in this document.
- Do not add platform-specific hosted integration plans here.
- Do not introduce OCR/VLM dependencies into the base package.
- Do not introduce copyleft, AGPL, source-available, custom-condition, or model-license-restricted dependencies into the base install path.
- Treat the canonical graph schema as the core product contract.
- Keep all exports derived from the graph.
- Keep Markdown secondary.
- Keep security warnings explicit.
- Never blend hidden/off-page/low-contrast text into default chunks.
- Keep every public API versioned.
- Add fixtures before heuristics.
- Benchmark before speed or accuracy claims.
- Do not make public speed claims until Gate Zero G1 passes, including any approved G1 retry.
- Prefer deterministic heuristics over hidden model behavior in the base tier.
- Never compare deterministic-tier output against OCR/VLM parsers without labeling the tier.
- If a PDF cannot be parsed safely, fail with a stable code.
- Track OpenDataLoader, EdgeParse, LiteParse, Kreuzberg, Docling, MinerU, Marker, MarkItDown, Unstructured, PyMuPDF, and PyMuPDF4LLM releases.
- Keep exact community/license landscape figures in `docs/landscape-log.md`; refresh before major milestones and at least every 90 days.
- Never publish ranking or superlative claims.
- Keep `ethos-verify` free of Ethos-internal type dependencies.
- Never describe verification as pixel-level proof, semantic proof, or arithmetic proof.
- Treat canonical-payload output differences across supported platforms as release-blocking bugs under the deterministic profile.

---

## 15. Open Questions

Closed decisions now recorded in this PRD:

- Project name: Ethos.
- Gate Zero decider: Gate Zero decider.
- Interim corpus owner: Gate Zero decider until the benchmark/devrel role is staffed.
- Gate Zero benchmark hardware: local Mac M4 Pro arm64 and Linux x64 machines recorded in `benchmarks/gate-zero/manifest.json` with exact CPU, RAM, OS, kernel, and runner details.
- PDFium distribution: Phase 1 pinned `bblanchon/pdfium-binaries`; Phase 2 project-maintained `pdfium.googlesource.com` builds before Public Beta.
- Font policy: embedded fonts first, versioned substitution table, bundled Liberation fallback, deterministic `.notdef` on glyph miss, non-embedded CJK warned and out of Release 1.
- Licensing: Apache-2.0 core, DCO with CI sign-off enforcement, approved license allowlist, denied GPL/AGPL/LGPL/custom-condition base dependencies, exceptions only by ADR, NOTICE maintained.
- Priority lock: `ethos-verify` alpha plus OpenDataLoader grounding adapter are launch-critical in the Milestone B window.

Remaining open questions:

- Whether the base footprint gate applies independently to CLI, Python wheel, and Node package or only to the smallest first-class install surface.
- How much debug overlay functionality is public by default.
- Whether WASM is Release 2 or later.
- Which optional OCR/VLM adapters are acceptable by license, footprint, privacy posture, and CPU cost.
- Which Release 2 table/formula/chart capabilities are deterministic enough for base tier versus enrichment tier.

---

## 16. Recommended Next Step

Before parser implementation expands, produce the design package:

- `schemas/ethos-document.schema.json`
- `schemas/ethos-chunks.schema.json`
- `schemas/ethos-security-report.schema.json`
- `schemas/ethos-verification-report.schema.json`
- `schemas/ethos-verification-config.schema.json`
- `profiles/ethos-deterministic-v1.json`
- `adapters/grounding/opendataloader-json/README.md`
- `fixtures/README.md`
- `docs/architecture.md`
- `docs/benchmark-plan.md`
- `docs/determinism-contract.md`
- `docs/pdfium-profile.md`
- `docs/landscape-log.md`
- `GOVERNANCE.md`
- `docs/roadmap.md`
- `benchmarks/gate-zero/manifest.json`

Approved contract package scope for the first implementation task:

- Five schemas: document, chunks, security report, verification report, and verification config.
- `docs/determinism-contract.md` with c14n v1, canonical exclusion table, and deterministic profile manifest.
- Versioned deterministic profile artifact: `profiles/ethos-deterministic-v1.json`.
- Internal `ethos-core` trait skeleton: `GroundingSource`, backend trait, and layout trait. If published, this contract package uses the public crates.io package name `ethos-doc-core` per ADR-0006.
- Tiny OpenDataLoader grounding adapter stub: `adapters/grounding/opendataloader-json`, enough to prove foreign parser output can enter the `GroundingSource` interface.
- CI proof that `ethos-verify` compiles against the trait module alone.

Acceptance:

- Schemas validate the examples and field requirements in section 8.
- `profiles/ethos-deterministic-v1.json` records deterministic-profile version, c14n version, canonical exclusion table reference, quantization policy, font policy reference, PDFium profile placeholder, warning policy, config-hash inputs, and runtime fields excluded from canonical equality.
- c14n idempotence property tests are green.
- No-network base check is green for base crates and CLI skeleton.
- `ethos-verify` has no dependency on Ethos parser internals.
- `adapters/grounding/opendataloader-json` compiles or validates as a stub against `GroundingSource`, even if it only maps parser identity, pages, elements, bbox, text, and capabilities.

The first implementation plan must also include the `ethos-verify` alpha, OpenDataLoader grounding adapter, and proof-of-trust demos as launch-critical work, not fallback-only work.

Then implement a thin Rust prototype that parses simple born-digital PDFs into the draft schema, fingerprints the canonical document payload under the deterministic profile, and runs inside the benchmark harness next to OpenDataLoader, EdgeParse, LiteParse, and PyMuPDF4LLM.

---

## Appendix A: Research References

Competitors and tools:

- OpenDataLoader PDF: https://github.com/opendataloader-project/opendataloader-pdf
- OpenDataLoader license history: https://opendataloader.org/docs/license
- EdgeParse: https://github.com/raphaelmansuy/edgeparse
- LiteParse: https://github.com/run-llama/liteparse
- Kreuzberg: https://github.com/kreuzberg-dev/kreuzberg
- Docling: https://github.com/docling-project/docling
- MinerU: https://github.com/opendatalab/MinerU
- MarkItDown: https://github.com/microsoft/markitdown
- Unstructured: https://github.com/Unstructured-IO/unstructured
- PyMuPDF4LLM: https://github.com/pymupdf/RAG

PDF engines and dependencies:

- PDFium canonical repository: https://pdfium.googlesource.com/pdfium/
- Archived PDFium GitHub mirror: https://github.com/chromium/pdfium
- PDFium binaries: https://github.com/bblanchon/pdfium-binaries
- pdfium-render wrapper: https://github.com/ajrcarey/pdfium-render
- pdf.js: https://github.com/mozilla/pdf.js
- MuPDF licensing: https://mupdf.com/licensing/index.html
- Poppler: https://poppler.freedesktop.org/

Benchmarks and evaluation:

- OmniDocBench: https://github.com/opendatalab/OmniDocBench
- ParseBench: https://github.com/run-llama/ParseBench
- RAGAS: https://github.com/explodinggradients/ragas
- DeepEval: https://github.com/confident-ai/deepeval
- TruLens: https://github.com/truera/trulens
