# Ethos

> **Status: pre-alpha — contracts phase.** Nothing here is released, benchmarked, or ready for
> use. Gate Zero (the go/no-go measurement for the parser core) has not run. No performance,
> footprint, or quality claims are made until the published, reproducible benchmark report
> exists (Milestone E).
> Current execution status and blockers live in `docs/execution-status.md`; public-release
> hygiene gates live in `docs/public-release-checklist.md`.

Ethos is a verification and grounding system for document evidence. It includes a deterministic
PDF parser that turns born-digital PDFs into auditable grounding artifacts: JSON, Markdown, text,
chunks, citations, coordinates, crops, and security warnings.

Ethos can verify citation evidence against the parsed source and return the source crop for
inspection.

One native parser. No JVM. No Python ML stack. No GPU. No OCR model in the base install.
Same input, same pinned profile, same stable payload projection and fingerprint.

## Try the alpha verification loop

Ethos is source-only pre-alpha. There are no release artifacts or package installs yet. From a
source checkout, the current product-proof command is:

```bash
make verify-alpha
```

That command builds the CLI and checks the alpha grounding loop across:

- native Ethos document JSON
- synthetic OpenDataLoader-style JSON
- pinned real OpenDataLoader 2.4.7 JSON fixtures
- grounded, ungrounded, stale-fingerprint, and capability-limited citation cases
- byte-identical repeated verification reports for the checked-in fixtures
- deterministic native crop descriptor JSON artifacts

A single verification command looks like this:

```bash
ethos verify examples/verify/opendataloader.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_grounded_citations.json \
  --fail-on-ungrounded \
  --out /tmp/ethos-verification-report.json
```

Exit behavior:

- `0`: verification completed and all requested evidence is grounded
- `1`: verification completed, but at least one requested evidence check is stale, missing,
  mismatched, unsupported, or capability-blocked
- `2`: invalid input, malformed citations, adapter failure, or another usage error

See `docs/demos/verify-alpha.md` for the full demo matrix.

## What Ethos is not (honest scope)

- Ethos is **not an OCR engine** yet, and it does not claim to beat VLM parsers on complex
  scanned layouts. Scanned/image-only pages fail with a stable `ocr_required` error.
- Release 1 targets **born-digital PDFs**: text spans, reading order, conservative structure,
  non-text region coordinates, security report, chunks, citations, and verification. Complex
  table semantics, formula/LaTeX, and chart classification are Release 2 enrichment.
- Verification checks **evidence grounding** (the cited region exists, the text matches, the
  fingerprint is fresh). It is not a semantic correctness judgment of an answer.
- Non-embedded CJK font fallback is out of Release 1 and warns explicitly.
- Public benchmark reports, package publication, GitHub releases, binaries, wheels, npm updates,
  and launch announcements are blocked until the release checklist is complete.

It is built for teams that need trustworthy local document grounding, deterministic native parsing
when they want it, and citation evidence that can be inspected instead of trusted blindly.

## Verification flow

```text
AI answer citations
        +
document evidence source
        |
        v
GroundingSource adapter
        |
        v
ethos verify
        |
        +--> verification_report.json
        +--> optional crop descriptor JSON
        +--> optional source-bound rendered crop artifact
```

The deterministic Ethos parser is one grounding source. Foreign parser output can be another
grounding source when an adapter can expose text, pages, regions, fingerprints, and capabilities
through the `GroundingSource` trait. When a source lacks required evidence metadata, Ethos reports
that limitation instead of silently upgrading the claim.

## Current capability status

| Capability | Current status | Claim boundary |
| --- | --- | --- |
| Native Ethos JSON citation verification | Alpha path exists | Grounding checks over checked-in fixtures |
| OpenDataLoader JSON grounding adapter | Alpha path exists | Quote, value, and presence checks over pinned fixtures |
| Stale fingerprint handling | Alpha path exists | Fails closed when citation fingerprints drift |
| Capability-limited reports | Alpha path exists | Reports missing source capabilities explicitly |
| Crop descriptor JSON | Alpha path exists for native Ethos JSON | Descriptor identity is logical evidence identity |
| Rendered crop PNG artifacts | Same-host repeatability path exists | Cross-platform PNG byte identity is not claimed |
| Born-digital PDF parsing | Narrow parser path exists | Not benchmark-validated; parser quality claims are blocked |
| OCR / scanned PDFs | Not supported in base install | Stable `ocr_required` failure |
| Complex table semantics | Alpha-only | Release 2 enrichment work |
| Heading/list/layout quality | Alpha-only | Still fixture- and Gate-Zero-dependent |
| Public benchmarks | Not ready | Public evidence belongs in `ethos-bench` |

## Supported grounding sources

Ethos verification is parser-agnostic by design. The current source adapters are:

| Source | How to use it | Notes |
| --- | --- | --- |
| Native Ethos document JSON | `ethos verify document.ethos.json --citations citations.json` | Fullest alpha evidence path |
| OpenDataLoader-style JSON | `--grounding opendataloader-json` | Capability warnings describe missing metadata |
| Real pinned OpenDataLoader 2.4.7 JSON fixtures | `fixtures/foreign/opendataloader/real/` | Used by `make verify-alpha` |

Additional adapters should preserve the same contract: expose what the source can prove, report
what it cannot, and never pretend parser output is stronger than its evidence.

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
bytes and the same configuration are intended to produce a byte-identical stable payload
projection and equal fingerprints across supported Gate Zero platforms. Precise emitted geometry
such as `bbox` values can remain platform-sensitive and is excluded from the fingerprint basis;
full emitted document JSON and rendered crops are not claimed to be cross-platform byte-identical.
Geometry is quantized at extraction, fonts resolve through a bundled deterministic profile
(never system fonts), canonical JSON has one serialization, and runtime diagnostics live outside
canonical equality. A flaky fingerprint is a bug, never a retry. See
`docs/determinism-contract.md`.

## Security and local execution

Ethos treats PDFs as hostile input. The base build is designed for local/offline execution with no
network APIs in base crates. PDFium is loaded only from an explicit operator-provided path, and
hosted or service deployments must use sandbox/subprocess isolation with CPU, memory, wall-time,
file-descriptor, output, and network limits.

Report vulnerabilities through GitHub private vulnerability reporting. See `SECURITY.md`.

## FAQ

### Is Ethos a PDF parser?

Partly. Ethos includes a deterministic born-digital PDF parser, but the product goal is citation
grounding: checking whether cited AI claims are supported by document evidence. Parser work serves
that verification loop.

### Is Ethos a semantic truth system?

No. Ethos checks evidence grounding, freshness, and source capabilities. It does not claim semantic
entailment, computed-number correctness, factual correctness, or answer quality.

### Can Ethos verify output from other parsers?

Yes, when that parser's output can be adapted into `GroundingSource`. OpenDataLoader JSON is the
first adapter path.

### Does Ethos support scanned PDFs?

Not in the base install. Scanned or image-only pages fail with `ocr_required`.

### Can I use Ethos in CI?

The alpha CLI supports `--fail-on-ungrounded`, which exits `1` when verification completes but
evidence is not fully grounded. Treat the current repo as source-only pre-alpha, not a stable
package or release artifact.

### Where are benchmark results?

Public benchmark reports are not ready. Generated public-safe Gate Zero evidence belongs in the
separate `docushell/ethos-bench` repository, not in this main source repo.

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
