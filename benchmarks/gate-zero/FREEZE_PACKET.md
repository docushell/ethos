# Gate Zero Freeze Packet

Date: 2026-06-12
Owner: product / decider
Status: Blocked pending corpus freeze and competitor pins

This packet is the product checklist for turning Gate Zero from an engineering placeholder into a
valid benchmark decision input. Do not mark `benchmarks/gate-zero/manifest.json` frozen and do not
publish benchmark claims until every required fact below is recorded.

## Product Decision

Ethos remains pre-alpha. Gate Zero is not ready to run.

The engineering harness now fails closed when the corpus/hardware manifest or competitor lock is
incomplete. The remaining work is product/benchmark-owner evidence gathering, not parser
implementation.

## Required External Outputs

| Output | Required file | Product acceptance |
| --- | --- | --- |
| Frozen corpus and hardware | `benchmarks/gate-zero/manifest.json` | `frozen=true`, status `FROZEN-SIGNED`, freeze timestamp, signed-by value, nonempty corpus entries |
| Competitor pins | `benchmarks/competitors.lock.json` | Exact versions, runtime versions where applicable, artifact SHA256 values, and `pinned=true` for all Gate Zero competitors |
| Public naming acceptance | `docs/decisions/ADR-0006-package-identifiers.md` | Status `Accepted`; registry/trademark checks complete before public package/docs claims |

## Candidate Corpus Seed

The existing CC0 synthetic fixtures are valid engineering seed material, but they are not sufficient
by themselves for a representative public benchmark. The decider must either accept these as a
small Gate Zero seed or add broader redistributable born-digital PDFs before freezing.

| Candidate ID | Source fixture | SHA256 | Pages | Subsets | Product note |
| --- | --- | --- | ---: | --- | --- |
| failure-corrupt-header-valid | `fixtures/failure/corrupt-header-valid/document.pdf` | `0716f9264c9fe19f5d7455276107f3ddcc1d3497f63d60689a73558ae8a1bf5e` | 0 | failure | Stable corrupt-PDF error fixture |
| failure-image-only-or-blank-page | `fixtures/failure/image-only-or-blank-page/document.pdf` | `df69a01c6c61fb04fb4a4be2a53e920dccbd8956c32eb7ab53bf0f19b50f3e21` | 1 | failure | Stable OCR-required failure fixture |
| failure-invalid-header | `fixtures/failure/invalid-header/document.pdf` | `c52fa72b5f4be9a86cd7bf69559025bae760a974e1c9d998e33d6981993df412` | 0 | failure | Stable non-PDF byte fixture |
| synthetic-hyphenated-line-break | `fixtures/synthetic/hyphenated-line-break/document.pdf` | `7f079977e8438cea4f4b876b3f67380f047218133b3193d7bae8130ac327eeeb` | 1 | born_digital, hyphenation, fonts | Hyphenation/font quirk seed |
| synthetic-ligature-fi-embedded-font | `fixtures/synthetic/ligature-fi-embedded-font/document.pdf` | `7f99a763d765ea0d880fcd871171ac4811e23b9fc7c3912a391276fcbdf6431e` | 1 | born_digital, fonts, ligatures | Embedded-font ligature seed |
| synthetic-rotation-90 | `fixtures/synthetic/rotation-90/document.pdf` | `1400858e1c0fa0255a037463b4e44df6f9d740ac33583cc590c4ac5cfd2fcc9d` | 1 | born_digital, rotation | Rotation seed |
| simple-text | `fixtures/synthetic/simple-text/document.pdf` | `f2f6ab91c696a4dffd96512456184451634fda22e19face9f636f3b69c6286f3` | 1 | born_digital | Parser smoke seed |
| synthetic-two-columns | `fixtures/synthetic/two-columns/document.pdf` | `de50aafb08219aa7fefdcb13ef8975ebf362f52f4d558c2d274ca711ce9d9d79` | 1 | born_digital, multi_column | Multi-column seed |
| synthetic-two-lines | `fixtures/synthetic/two-lines/document.pdf` | `28d9c089bced8c913e6e0440a937f36581ed0b951384787930ba5c52f47a5359` | 1 | born_digital | Paragraph grouping seed |

## Hardware Evidence Recorded

The benchmark host hardware fields are now recorded in `benchmarks/gate-zero/manifest.json`.

| Host | Recorded evidence |
| --- | --- |
| `mac-m4pro-arm64` | MacBook Pro `Mac16,8`; Apple M4 Pro, 12 cores (8 performance, 4 efficiency); 48 GB RAM; macOS 26.5 (25F71); Darwin 25.5.0; local manual runner `<private-host-pattern>-Pro.local` |
| `linux-x64-1` | KVM virtualized enterprise Linux 8.8 x86_64 host; AMD EPYC 7742 64-Core Processor, 2 vCPU; `32565968 kB` MemTotal; Linux 5.15.0 enterprise x86_64 kernel; manual runner `linux-x64-1` |

Remaining manifest blockers are corpus freeze/signature fields, not hardware fields.

## Competitor Pin Checklist

Every Gate Zero competitor must be recorded as the exact artifact measured by the harness.

| Competitor | Required fields |
| --- | --- |
| OpenDataLoader PDF | `version`, `artifact_sha256`, `jvm_version`, `pinned=true` |
| EdgeParse | `version`, `artifact_sha256`, `pinned=true` |
| LiteParse | `version`, `artifact_sha256`, `pinned=true` |
| PyMuPDF4LLM | `version`, `artifact_sha256`, `python_version`, `pinned=true` |

Artifact hashes must be lowercase SHA256 of the downloaded package, binary, jar, wheel, or pinned
source archive actually used by the benchmark runner. Do not use a repository commit hash as a
substitute unless the benchmark artifact is the source archive itself.

## Execution Commands

Use these commands after the manifest and lockfile are updated:

```sh
python3 .github/scripts/readiness_gate.py gate-zero
make -C benchmarks/harness bench
```

Expected state today:

```text
gate-zero readiness: BLOCKED
```

Expected state after all required facts are recorded:

```text
gate-zero readiness: green
```

The G1/G2/G3 measurement runner is still a separate implementation step after readiness turns
green.

## Public-Claim Rule

Until Gate Zero produces `benchmarks/results/gate-zero/{g1,g2,g3}.json` from the frozen manifest
and pinned competitors, product language must stay at:

```text
Ethos is pre-alpha. Current results are engineering fixtures, not public benchmark claims.
```
