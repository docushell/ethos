# Ethos

[![ci](https://github.com/docushell/ethos/actions/workflows/ci.yml/badge.svg)](https://github.com/docushell/ethos/actions/workflows/ci.yml)
[![determinism](https://github.com/docushell/ethos/actions/workflows/determinism.yml/badge.svg)](https://github.com/docushell/ethos/actions/workflows/determinism.yml)
[![bench](https://github.com/docushell/ethos/actions/workflows/bench.yml/badge.svg)](https://github.com/docushell/ethos/actions/workflows/bench.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
![Rust: 1.87+](https://img.shields.io/badge/rust-1.87%2B-orange)

**Ethos checks whether an AI's claims about a document are actually in the document.**

Models reword. They cite page 4 on one run and page 7 on the next. Ethos doesn't move: same
source, same claim, same config, same answer, byte for byte. So when a verdict changes, you
know it was the model that changed and not the checker.

Point it at your own parser's output or let it parse a born-digital PDF itself. It reports
what matched, what didn't, whether the evidence went stale, and — the part most tools skip —
**what it could not establish**. A missing capability produces an explicit limitation, never
a silent guess.

It does not decide whether an answer is true, relevant, or complete. That boundary is
deliberate and permanent.

Apache-2.0. Runs locally. No account, no API key, no network.

## Start here

- [Verify a checked-in example](#catch-a-fabricated-citation-in-60-seconds)
- [Install or build Ethos](#install-or-build)
- [Parse a born-digital PDF](#2-minute-pdf-parse-quickstart)
- [Use another parser](#bring-your-own-parser)
- [See what works today](#supported-today--not-yet)
- [See what comes out](#what-comes-out)
- [Read the limits](docs/CLAIMS.md) — what a verdict proves, and what it does not
- [Read the v0.6.0 format plan](docs/proof-statement-v1.md) — the major release in progress
- [Pick up a v0.6.0 task](docs/proof-statement-v1-implementation-plan.md) — task board and acceptance criteria

## Catch a fabricated citation in 60 seconds

Conversion tools stop at output. Ethos checks whether cited evidence actually exists in the
source. This works on checked-in JSON fixtures and does not require PDFium:

```bash
cargo build --locked -p ethos-cli

# One fabricated quote, one citation to a missing element - both get caught:
./target/debug/ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_ungrounded_citations.json \
  --fail-on-ungrounded
# exit 1: "Operating margin was 99%" is not supported by the source evidence

# Correct citations against the same source verify cleanly:
./target/debug/ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --fail-on-ungrounded
# exit 0: all requested evidence is grounded
```

Exit `1` means verification ran but at least one check failed. Ethos still writes the report so
you can see the reason. This example checks document evidence; it does not judge whether an answer
is factually correct.

## What comes out

Every verdict is a self-describing record. It says what kind of result it is, which artifact
it is about, and what produced it:

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    { "name": "invoice.pdf", "digest": { "sha256": "1a3106…" } }
  ],
  "predicateType": "https://docushell.com/ethos/grounding/v1",
  "predicate": {
    "all_evidence_grounded": true,
    "checks": [ { "id": "v0001", "status": "grounded", "evidence_tier": "element_scoped" } ],
    "attestation": {
      "verifier": { "name": "ethos-verify", "version": "0.6.0" },
      "config_version": "default-v1",
      "claims_sha256": "65e9f8…"
    }
  }
}
```

`subject` names the artifact by digest, so anyone holding the same file can confirm the
verdict is about their copy. `attestation` names the verifier, config, and exact claims, so
the verdict can be re-run and compared byte for byte. `evidence_tier` says how precisely each
claim was bound rather than leaving you to work it out.

The [in-toto Statement](https://github.com/in-toto/attestation) shape is borrowed from the
supply-chain world, so existing tooling already reads it.

**Upgrading from 0.5:** the report you already parse is now the `predicate`. `jq .predicate`
gives back the previous shape byte for byte. Nothing inside it changed except two added
fields, `attestation` and `evidence_tier`.

Read [what a verdict proves and what it does not](docs/CLAIMS.md) before building on it.

## Why Ethos?

Document parsers turn files into text and structure. Ethos handles the next step: checking whether
a citation points back to the recorded document evidence.

## What Ethos produces

Depending on the command and available source data, Ethos can produce:

- structured JSON, Markdown, and text;
- chunks and citation references;
- verification reports;
- page coordinates and crop descriptions;
- rendered evidence crops when PDFium is configured; and
- document security warnings.

## Where Ethos fits

Use Ethos when a pipeline needs to answer:

- Does this quote, value, page, or table cell exist in the recorded source?
- Is the citation for the current document representation?
- Was a required source capability missing?
- Can a reviewer inspect the cited evidence?

Ethos is a local evidence-checking tool. It is not an OCR service, hosted parsing API, or semantic
truth system.

## Supported today / not yet

| Area | What works |
| --- | --- |
| Citation verification | Native Ethos JSON and foreign parser output, no PDFium needed |
| Foreign parser grounding | OpenDataLoader-style JSON adapter, or write your own |
| Born-digital PDF parsing | Yes, with caller-provided PDFium |
| Output formats | JSON, Markdown, text, chunks, verification reports, crop descriptors |
| Install | Rust crates, Python wheel, npm package, macOS arm64 and Linux x64 CLI, or build from source |
| Where it runs | Your machine. No network calls anywhere in the base flows. |

| Area | Not supported |
| --- | --- |
| Scanned or image-only PDFs | No OCR. Fails with `ocr_required` rather than guessing. |
| Windows CLI artifact | Build from source on Windows; no packaged binary yet |
| Bundled PDFium | Supply your own via `ETHOS_PDFIUM_LIBRARY_PATH` |
| Hosted API | None. Ethos is a local tool by design. |
| Semantic judgement | Ethos checks whether cited evidence exists, not whether an answer is correct |

We publish no speed, footprint, or parser-quality comparisons, because we have not run a
benchmark whose numbers we would be willing to defend. When that changes the numbers will
arrive with the harness that produced them.

## Install or build

Verification needs nothing but the CLI. PDF parsing additionally needs caller-provided PDFium
through `ETHOS_PDFIUM_LIBRARY_PATH`.

Choose the smallest path that fits your work:

- Use the npm package for a packaged CLI on supported platforms.
- Build from source when working in this repository.
- Use the Rust crates when embedding Ethos in Rust.
- Use the Python wrapper with a separately installed `ethos` CLI.

Source-checkout prerequisites:

- Rust via `rustup`; this checkout pins Rust `1.87.0` in `rust-toolchain.toml`
- `make`
- Python 3 for demo and schema-validation targets
- `jsonschema>=4.18` in the Python environment used for `make verify-alpha`
- caller-provided local PDFium through `ETHOS_PDFIUM_LIBRARY_PATH` only for PDFium-backed paths
  (`scripts/fetch-pdfium.sh` can fetch the exact pinned archive; see the quickstart)

From a source checkout:

```bash
git clone https://github.com/docushell/ethos.git
cd ethos
rustup show
cargo build --locked -p ethos-cli
./target/debug/ethos --help
./target/debug/ethos doctor
```

To install the source-built CLI from the checkout into your local Cargo bin:

```bash
cargo install --locked --path crates/ethos-cli
ethos --help
```

To add the currently approved Rust library crates to another Rust project:

```bash
cargo add ethos-doc-core@0.5.0
cargo add ethos-verify@0.5.0
cargo add ethos-pdf@0.5.0
```

To install the Python wrapper from PyPI:

```bash
python3 -m pip install ethos-pdf==0.5.0
```

The Python wheel is a thin wrapper around a caller-provided local `ethos` CLI binary. It does not
bundle the CLI or PDFium. Install or provide `ethos` separately, and keep
`ETHOS_PDFIUM_LIBRARY_PATH` set for PDFium-backed commands.

The v0.5.0 Python wrapper includes JSON verification and evidence anchoring through that
caller-provided CLI:

```python
from ethos_pdf import EthosCli

ethos = EthosCli(binary="/path/to/ethos")
report = ethos.verify(
    source="source.ethos.json",
    citations="citations.json",
    fail_on_ungrounded=False,
)
anchor_report = ethos.anchor(
    source="source.ethos.json",
    evidence_refs="evidence_refs.json",
)
```

The JSON verification and evidence-anchor wrapper calls use the caller-provided CLI and do not
require PDFium unless the chosen command path invokes PDFium-backed parser, crop, or render
behavior.

To install the npm CLI package on a supported first-release platform:

```bash
npm install -g @docushell/ethos-pdf@0.5.0
ethos --version
```

The npm package vendors only the approved macOS arm64 and Linux x64 CLI binaries. Unsupported
platforms fail before invoking a binary. PDFium-backed commands fail until
`ETHOS_PDFIUM_LIBRARY_PATH` points to a caller-provided PDFium dynamic library.

Run `ethos doctor` for local setup diagnostics. Run `ethos doctor --require-pdfium` after setting
`ETHOS_PDFIUM_LIBRARY_PATH` to check whether the configured PDFium is usable by Ethos.

GitHub Release `v0.5.0` also provides CLI archives for macOS arm64 and Linux x64.

## 2-minute PDF parse quickstart

This source-checkout example uses a generated born-digital PDF. PDFium remains caller-provided
through `ETHOS_PDFIUM_LIBRARY_PATH`. Ethos checks the library you configure; it does not download,
install, repair, or vet untrusted dynamic libraries.

`scripts/fetch-pdfium.sh` downloads the exact pinned PDFium archive named in
`docs/pdfium-profile.md`. It checks the archive and library hashes, stops on a mismatch, and prints
the `ETHOS_PDFIUM_LIBRARY_PATH` value to use.

```bash
scripts/fetch-pdfium.sh   # optional: fetch + verify the pinned PDFium
```

```bash
cargo build --locked -p ethos-cli
export ETHOS_PDFIUM_LIBRARY_PATH=/absolute/path/to/libpdfium.dylib

./target/debug/ethos doctor --require-pdfium
./target/debug/ethos doc parse fixtures/synthetic/simple-text/document.pdf --format json
./target/debug/ethos doc parse fixtures/synthetic/simple-text/document.pdf --format text
```

The fixture is synthetic and born-digital. This is a smoke path, not a benchmark or a
claim about broader PDF, OCR, table, production, hosted, or bundled-PDFium support.

## Minimal end-to-end example

This checks three citations against a saved Ethos JSON document: a quote, a table cell, and a
page. It does not require PDFium.

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
      "version": "0.2.0"
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

Use `--format summary` for a shorter, human-readable result. The JSON report remains the audit
record. A result is `verified` only when all requested evidence is grounded. A
`partially_verified` result lists the checks that can be reused; `unverified` means none can be
reused. Apps that also decide whether an answer is relevant or safe to release need the separate
[`app answer release contract`](docs/app-answer-release-contract.md).

## Evidence anchoring

Ethos can also check whether a list of evidence references points to evidence in a saved document.
It checks source links, not whether an answer is correct. This JSON-only command does not require
PDFium.

```bash
./target/debug/ethos evidence anchor schemas/examples/document.example.json \
  --evidence-refs schemas/examples/evidence-anchor-request.example.json \
  --out /tmp/ethos-evidence-anchor-report.json
```

## Try the verification loop

From a source checkout, the current verification loop is:

```bash
make verify-alpha
```

That command builds the CLI and checks:

- native Ethos document JSON
- synthetic and pinned OpenDataLoader-style JSON
- successful, failed, stale, and capability-limited citation cases
- malformed inputs
- repeated verification reports and crop descriptions

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

Exit `2` means Ethos could not create a verification report.

See `docs/demos/verify-alpha.md` for the full demo matrix.

Successful runs end with `verify-alpha demo checks passed`. Generated files are written under
`target/verify-alpha/`.

## Scope and boundaries

- Ethos supports a narrow born-digital PDF path. Scanned or image-only pages fail with
  `ocr_required` because the base install has no OCR.
- Complex tables, formulas, charts, and difficult layouts are outside the current base scope.
- Verification checks whether evidence exists, matches, and belongs to the expected document
  representation. It does not decide whether an answer is true, relevant, or complete.
- Windows packaged artifacts, bundled project-maintained PDFium builds, hosted surfaces, public
  benchmark reports, and launch announcements are tracked as separate release-scope work.

## Verification flow

```text
citations + document evidence
             |
             v
       grounding source
             |
             v
        ethos verify
             |
             +--> verification report
             +--> optional crop description or image
```

Ethos can use its own document JSON or a supported parser adapter. If the source cannot prove a
requested check, Ethos reports the missing capability instead of treating the check as grounded.

## Bring your own parser

### Available today

Rust developers can implement the `GroundingSource` trait. The CLI can verify native Ethos JSON
and supported OpenDataLoader-style JSON:

```text
your parser output -> small adapter -> GroundingSource -> ethos verify -> report
```

The adapter maps the parser's pages, text, tables, regions, fingerprints, and declared
capabilities. It must report missing information honestly. It must not invent evidence.

Start with the [`GroundingSource` adapter guide](docs/bring-your-own-parser.md). The existing
OpenDataLoader adapter is the larger working example.

### Proposed for v0.6.0

The draft v0.6.0 plan proposes one strict, language-neutral Grounding JSON format:

```text
your parser output -> one mapper -> Grounding JSON -> ethos check/verify -> report
```

This would let JavaScript, Python, Java, Go, and other pipelines use Ethos without implementing a
Rust trait. “Plug and play” still requires one deterministic mapper because parsers use different
field names and meanings. Ethos will reject unknown or incomplete input instead of guessing.

Grounding JSON is a proposal, not a current feature. It must pass a real second-parser mapping
proof before its schema is frozen. This does not change DocuShell's current OpenDataLoader parsing
of normal born-digital PDFs; DocuShell would add a mapper only where it wants Ethos verification.

Ethos would remain the open verification engine. DocuShell could sell hosted mapping,
compatibility testing, support, and audit workflows around it. Billing and hosted-service code do
not belong in the Ethos core.

Relevant sections in the [Grounding JSON plan](docs/v0-6-0-release-prep.md), which covers the
merged parser-integration half of v0.6.0:

- §1 — Release decision
- §5 — Success criteria and non-goals
- §6 — Architecture contract
- §8 — Developer and pipeline surfaces
- §9 — DocuShell and monetization boundary
- §13 — Tradeoffs and deliberate decisions

## Supported grounding sources

| Source | How to use it |
| --- | --- |
| Native Ethos document JSON | `ethos verify document.ethos.json --citations citations.json` |
| OpenDataLoader-style JSON | Add `--grounding opendataloader-json` |

Other adapters must expose only what their source can prove and report missing capabilities.

## Determinism

With the same input, configuration, and pinned profile, Ethos should produce the same stable
fingerprint data on supported platforms. Exact page boxes and rendered images may differ between
platforms and are not part of that guarantee. Unexpected fingerprint changes are bugs. See the
[determinism contract](docs/determinism-contract.md).

## Security and local execution

Ethos treats PDFs as untrusted input. Base features run locally and do not call network APIs.
PDFium is loaded only from the path you provide. Services that process untrusted documents must
isolate the process and limit its CPU, memory, time, files, output, and network access.

Report vulnerabilities through GitHub private vulnerability reporting. See `SECURITY.md`.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `ModuleNotFoundError: No module named 'jsonschema'` during `make verify-alpha` | Install `jsonschema>=4.18` in the Python environment used by `python3`, then rerun the target. |
| `cargo build --locked` fails before compiling Ethos | Run from the repository root and keep the committed `Cargo.lock`; dependency or lockfile changes should happen in their own PR. |
| Rust version errors or unexpected compiler behavior | Run `rustup show`; this repo pins Rust `1.87.0` through `rust-toolchain.toml`. |
| `ethos verify --fail-on-ungrounded` exits `1` | Verification finished and wrote a report, but at least one check failed. Start with `checks[].status` and `warnings`. |
| Scanned or image-only PDFs do not parse | Base Ethos does not include OCR. These inputs should fail with `ocr_required` until OCR support is explicitly added. |
| Need a PDFium library | Run `scripts/fetch-pdfium.sh`. It downloads the exact pinned archive recorded in `docs/pdfium-profile.md`, verifies both recorded sha256 values, and prints the `ETHOS_PDFIUM_LIBRARY_PATH` export line. |
| Rendered crop PNGs are missing or skipped | Crop descriptor JSON works without PDFium; rendered PNG crops need the source PDF path and a configured PDFium runtime. |

## FAQ

### Is Ethos a PDF parser?

Yes, for a narrow set of born-digital PDFs. Its main job is broader: checking citations against
document evidence, including evidence produced by supported external parsers.

### Is Ethos a semantic truth system?

No. Ethos checks whether evidence exists, matches, is current, and can support the requested type
of check. It does not decide whether an answer is correct or good.

### Can Ethos verify output from other parsers?

Today, Rust developers can implement `GroundingSource`, and the CLI supports the
OpenDataLoader-style adapter. The v0.6.0 plan proposes Grounding JSON for other languages and
pipeline tools. See [Bring your own parser](#bring-your-own-parser).

### Does Ethos support scanned PDFs?

Not in the base install. Scanned or image-only pages fail with `ocr_required`.

### Can I use Ethos in CI?

Yes. Use `--fail-on-ungrounded`; it exits `1` when verification finishes but a check fails. Exit `2`
means malformed input or a usage error, which is a process failure rather than a verification
result — do not retry on it.

### Where are benchmark results?

There are none to publish yet. Generated public-safe Gate Zero evidence belongs in the
separate `docushell/ethos-bench` repository, not in this main source repo.

## Repository map

| Path | What it is |
| --- | --- |
| `schemas/` | JSON formats accepted or produced by Ethos |
| `profiles/` | Pinned settings for repeatable output |
| `crates/` | Rust libraries and CLI |
| `adapters/grounding/` | Adapters for external parser output |
| `fixtures/` | Sample documents and expected test results |
| `benchmarks/` | Internal benchmark tools and data |
| `docs/` | Plans, contracts, decisions, and guides |

## License

Apache-2.0 (`LICENSE`). Contributions require DCO sign-off (`CONTRIBUTING.md`). Base
dependencies are restricted to a permissive-license allowlist enforced in CI (`deny.toml`,
ADR-0004).
