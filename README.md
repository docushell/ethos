# Ethos

[![ci](https://github.com/docushell/ethos/actions/workflows/ci.yml/badge.svg)](https://github.com/docushell/ethos/actions/workflows/ci.yml)
[![determinism](https://github.com/docushell/ethos/actions/workflows/determinism.yml/badge.svg)](https://github.com/docushell/ethos/actions/workflows/determinism.yml)
[![bench](https://github.com/docushell/ethos/actions/workflows/bench.yml/badge.svg)](https://github.com/docushell/ethos/actions/workflows/bench.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
![Rust: 1.87+](https://img.shields.io/badge/rust-1.87%2B-orange)
![status: public beta](https://img.shields.io/badge/status-public--beta-blue)

> **Status: source-only public beta evaluation.**
> Ethos is public beta for source-only evaluation. It verifies whether AI citations are grounded in document evidence across native Ethos JSON and supported foreign parser outputs. Package publication, hosted surfaces, production positioning, and public benchmark claims remain blocked.
> The approved public beta surface is this GitHub source repository only, pinned to reviewed commit
> `d755e7c` and merged main commit `3f9e1c4`, which have matching source trees. Excluded surfaces
> include published crates, wheels, npm packages, binaries, release artifacts, hosted demos or APIs,
> project-maintained PDFium builds, public benchmark reports, and performance, footprint, quality,
> table-quality, or parser-quality claims.
> Current execution status and blockers live in `docs/execution-status.md`; public-release
> hygiene gates live in `docs/public-release-checklist.md`.

Ethos is a verification and grounding system for document evidence. It includes a deterministic
PDF parser that turns born-digital PDFs into auditable grounding artifacts: JSON, Markdown, text,
chunks, citations, coordinates, crops, and security warnings.

Ethos can verify citation evidence against the parsed source and return the source crop for
inspection.

One native parser. No JVM. No Python ML stack. No GPU. No OCR model in the base install.
Same input, same pinned profile, same stable payload projection and fingerprint.

## Install / Build from source

Ethos is public beta for source-only evaluation. There are no published crates, wheels, npm
packages, binaries, or GitHub release artifacts yet.

Prerequisites:

- Rust via `rustup`; this checkout pins Rust `1.87.0` in `rust-toolchain.toml`
- `make`
- Python 3 for demo and schema-validation targets
- `jsonschema>=4.18` in the Python environment used for `make verify-alpha`
- caller-provided local PDFium through `ETHOS_PDFIUM_LIBRARY_PATH` only for PDFium-backed paths

From a source checkout:

```bash
git clone https://github.com/docushell/ethos.git
cd ethos
rustup show
cargo build --locked -p ethos-cli
./target/debug/ethos --help
```

To install the source-built CLI from the checkout into your local Cargo bin:

```bash
cargo install --locked --path crates/ethos-cli
ethos --help
```

## Minimal end-to-end example

This verifies three citation claims against checked-in native Ethos document JSON: a quote, a
table cell, and page-level presence evidence.

```bash
cargo build --locked -p ethos-cli

./target/debug/ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --fail-on-ungrounded \
  --out /tmp/ethos-native-verification-report.json
```

The command exits `0` and writes a verification report shaped like this:

```json
{
  "all_evidence_grounded": true,
  "fingerprint_stale": false,
  "grounding": {
    "parser": {
      "name": "ethos",
      "version": "0.1.0"
    }
  },
  "checks": [
    {
      "id": "v0001",
      "status": "grounded",
      "match_method": "normalized_text_contains"
    }
  ],
  "warnings": []
}
```

## Try the alpha verification loop

The source-only public beta path has no release artifacts or package installs. From a source
checkout, the current verification loop is:

```bash
make verify-alpha
```

That command builds the CLI and checks the alpha grounding loop across:

- native Ethos document JSON
- synthetic OpenDataLoader-style JSON
- pinned real OpenDataLoader 2.4.7 JSON fixtures
- grounded, ungrounded, not-found, stale-fingerprint, and capability-limited citation cases
- malformed citation inputs and malformed OpenDataLoader-style inputs that must fail with usage
  diagnostics
- byte-identical repeated verification reports for the checked-in fixtures
- deterministic native crop descriptor JSON artifacts

A foreign-parser verification command looks like this:

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

## Expected output snippet

A healthy `make verify-alpha` run includes ordinary Cargo test output plus the demo checks:

```text
running 17 tests
...
test result: ok. 17 passed; 0 failed

running 40 tests
...
test result: ok. 40 passed; 0 failed

ok    native-grounded matches examples/verify/goldens/native_grounded_report.json
ok    opendataloader-grounded matches examples/verify/goldens/opendataloader_grounded_report.json
ok    native-ungrounded matches examples/verify/goldens/native_ungrounded_report.json
ok    opendataloader-not-found matches examples/verify/goldens/opendataloader_not_found_report.json
ok    native-stale matches examples/verify/goldens/native_stale_report.json
ok    opendataloader-capability-limited matches examples/verify/goldens/opendataloader_capability_limited_report.json
ok    real-opendataloader-grounded matches fixtures/foreign/opendataloader/real/expected.verification_report.json
ok    real-opendataloader-ungrounded matches fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json
ok    invalid-table-cell-citation exits 2 with expected usage diagnostic
ok    invalid-bbox-citation exits 2 with expected usage diagnostic
ok    opendataloader-malformed-bbox-input exits 2 with expected usage diagnostic
ok    opendataloader-unknown-page-input exits 2 with expected usage diagnostic
ok    native-ungrounded-summary summary includes expected diagnostics
ok    native-grounded-crops crop descriptors validate against schemas/ethos-crop-descriptor.schema.json

verify-alpha demo checks passed
```

Generated reports and crop descriptors are written under `target/verify-alpha/`.

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
| Born-digital PDF parsing | Narrow parser path exists | Public benchmark approval and parser quality claims are blocked |
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

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `ModuleNotFoundError: No module named 'jsonschema'` during `make verify-alpha` | Install `jsonschema>=4.18` in the Python environment used by `python3`, then rerun the target. |
| `cargo build --locked` fails before compiling Ethos | Run from the repository root and keep the committed `Cargo.lock`; dependency or lockfile changes should happen in their own PR. |
| Rust version errors or unexpected compiler behavior | Run `rustup show`; this repo pins Rust `1.87.0` through `rust-toolchain.toml`. |
| `ethos verify --fail-on-ungrounded` exits `1` | The command wrote a report, but at least one requested evidence check was stale, missing, mismatched, unsupported, or capability-blocked. Inspect `all_evidence_grounded`, `checks[].status`, `warnings`, and `capability_limits`. |
| Scanned or image-only PDFs do not parse | Base Ethos does not include OCR. These inputs should fail with `ocr_required` until OCR support is explicitly added. |
| Rendered crop PNGs are missing or skipped | Logical crop descriptor JSON works in the alpha path; rendered PNG crop artifacts require the source PDF path and a configured PDFium runtime. |
| Release/tag workflow fails | Public releases, binaries, wheels, npm packages, and crates are blocked until they have separate approval. |

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

The source-built CLI supports `--fail-on-ungrounded`, which exits `1` when verification completes
but evidence is not fully grounded. Treat the current repo as source-only public beta evaluation,
not a stable package or release artifact.

### Where are benchmark results?

Public benchmark reports are not approved. Generated public-safe Gate Zero evidence belongs in the
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
