# Ethos

> **Status: pre-alpha — contracts phase.** Nothing here is released, benchmarked, or ready for
> use. Gate Zero (the go/no-go measurement for the parser core) has not run. No performance,
> footprint, or quality claims are made until the published, reproducible benchmark report
> exists (Milestone E).
> Current execution status and blockers live in `docs/execution-status.md`; public-release
> hygiene gates live in `docs/public-release-checklist.md`.

Ethos is a verification and grounding system for document evidence. It includes a fast,
deterministic, runtime-light PDF parser that turns born-digital PDFs into auditable grounding
artifacts: JSON, Markdown, text, chunks, tables, citations, coordinates, crops, and security
warnings.

Ethos can verify citation evidence against the parsed source and return the source crop for
inspection.

One small native parser. No JVM. No Python ML stack. No GPU. No OCR model in the base install.
Same input, same pinned profile, same canonical output.

## What Ethos is not (honest scope)

- Ethos is **not an OCR engine** yet, and it does not claim to beat VLM parsers on complex
  scanned layouts. Scanned/image-only pages fail with a stable `ocr_required` error.
- Release 1 targets **born-digital PDFs**: text spans, reading order, headings, lists, simple
  and bordered tables, non-text region coordinates, security report, chunks, citations,
  verification. Complex table semantics, formula/LaTeX, and chart classification are Release 2
  enrichment.
- Verification checks **evidence grounding** (the cited region exists, the text matches, the
  fingerprint is fresh). It is not a semantic correctness judgment of an answer.
- Non-embedded CJK font fallback is out of Release 1 and warns explicitly.

It is built for teams that need trustworthy local document grounding, deterministic native parsing
when they want it, and citation evidence that can be inspected instead of trusted blindly.

## Public architecture

```text
Ethos
├── ethos-doc      Document parsing, structure, and canonical document graph
├── ethos-rag      Chunking, citation references, and retrieval-ready artifacts
└── ethos-verify   Evidence, grounding, fingerprint, and citation verification
```

CLI follows the same shape: `ethos doc …`, `ethos rag …`, `ethos verify …`
(plus `ethos fingerprint`, `ethos inspect`, `ethos debug`, `ethos audit`).

`ethos-verify` is parser-agnostic by design: it consumes any parser's output through the
`GroundingSource` trait. OpenDataLoader JSON is the first grounding adapter.

## Determinism, in one paragraph

Under a pinned deterministic profile (`profiles/ethos-deterministic-v1.json`), the same input
bytes and the same configuration produce a byte-identical canonical payload and equal
fingerprints on every supported platform. Geometry is quantized at extraction, fonts resolve
through a bundled deterministic profile (never system fonts), canonical JSON has one
serialization, and runtime diagnostics live outside canonical equality. A flaky fingerprint is
a bug, never a retry. See `docs/determinism-contract.md`.

## Repository map

| Path | What it is |
| --- | --- |
| `schemas/` | The product contract: document, chunks, security-report, verification-report, verification-config |
| `profiles/` | Deterministic profile artifacts |
| `crates/` | Rust workspace (internal `ethos-core`, public core package planned as `ethos-doc-core`, plus `ethos-pdf`, `ethos-verify`, `ethos-cli`, …) |
| `adapters/grounding/` | Foreign-parser adapters into `GroundingSource` |
| `fixtures/` | Public/synthetic test corpus — see the contribution guide |
| `benchmarks/` | Internal Gate Zero corpus, evidence, schemas, and parser harness; public run orchestration lives in `ethos-bench` |
| `docs/` | PRD, implementation plan, architecture, determinism contract, ADRs, public-release checklist |

## License

Apache-2.0 (`LICENSE`). Contributions require DCO sign-off (`CONTRIBUTING.md`). Base
dependencies are restricted to a permissive-license allowlist enforced in CI (`deny.toml`,
ADR-0004).
