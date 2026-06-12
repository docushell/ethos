# Gate Zero Freeze Packet

Date: 2026-06-12
Owner: product / decider
Status: Blocked pending corpus sign-off and competitor pins

This packet is the product checklist for turning Gate Zero from an engineering placeholder into a
valid benchmark decision input. Do not mark `benchmarks/gate-zero/manifest.json` frozen and do not
publish benchmark claims until every required fact below is recorded.

## Product Decision

Ethos remains pre-alpha. Gate Zero is not ready to run.

The engineering harness now fails closed when the corpus/hardware manifest or competitor lock is
incomplete. A small CC0 seed corpus has been staged in `benchmarks/gate-zero/corpus/`, but it is
not a frozen benchmark corpus until the decider signs it. The remaining work is
product/benchmark-owner evidence gathering, not parser implementation.

## Required External Outputs

| Output | Required file | Product acceptance |
| --- | --- | --- |
| Frozen corpus and hardware | `benchmarks/gate-zero/manifest.json` | staged corpus accepted, `frozen=true`, status `FROZEN-SIGNED`, freeze timestamp, signed-by value |
| Competitor pins | `benchmarks/competitors.lock.json` | Exact versions, runtime versions where applicable, artifact SHA256 values, and `pinned=true` for all Gate Zero competitors |
| Public naming acceptance | `docs/decisions/ADR-0006-package-identifiers.md` | Status `Accepted`; registry/trademark checks complete before public package/docs claims |

## Staged Corpus Seed

The existing CC0 synthetic fixtures have been copied into `benchmarks/gate-zero/corpus/` as a
staged Gate Zero seed. They are valid engineering seed material, but they are not sufficient by
themselves for a representative public benchmark. The decider must either accept these as a small
Gate Zero seed or add broader redistributable born-digital PDFs before freezing.

| Candidate ID | Corpus file | SHA256 | Pages | Subsets | Product note |
| --- | --- | --- | ---: | --- | --- |
| simple-text | `benchmarks/gate-zero/corpus/simple-text.pdf` | `f2f6ab91c696a4dffd96512456184451634fda22e19face9f636f3b69c6286f3` | 1 | born_digital | Parser smoke seed |
| two-lines | `benchmarks/gate-zero/corpus/two-lines.pdf` | `28d9c089bced8c913e6e0440a937f36581ed0b951384787930ba5c52f47a5359` | 1 | born_digital | Paragraph grouping seed |
| two-columns | `benchmarks/gate-zero/corpus/two-columns.pdf` | `de50aafb08219aa7fefdcb13ef8975ebf362f52f4d558c2d274ca711ce9d9d79` | 1 | born_digital, multi_column | Multi-column seed |
| rotation-90 | `benchmarks/gate-zero/corpus/rotation-90.pdf` | `1400858e1c0fa0255a037463b4e44df6f9d740ac33583cc590c4ac5cfd2fcc9d` | 1 | born_digital, rotation | Rotation seed |
| hyphenated-line-break | `benchmarks/gate-zero/corpus/hyphenated-line-break.pdf` | `7f079977e8438cea4f4b876b3f67380f047218133b3193d7bae8130ac327eeeb` | 1 | born_digital, hyphenation, fonts | Hyphenation/font quirk seed |
| ligature-fi-embedded-font | `benchmarks/gate-zero/corpus/ligature-fi-embedded-font.pdf` | `7f99a763d765ea0d880fcd871171ac4811e23b9fc7c3912a391276fcbdf6431e` | 1 | born_digital, fonts, ligatures | Embedded-font ligature seed |

## Hardware Evidence Recorded

The benchmark host hardware fields are now recorded in `benchmarks/gate-zero/manifest.json`.

| Host | Recorded evidence |
| --- | --- |
| `mac-m4pro-arm64` | MacBook Pro `Mac16,8`; Apple M4 Pro, 12 cores (8 performance, 4 efficiency); 48 GB RAM; macOS 26.5 (25F71); Darwin 25.5.0; manual runner `mac-m4pro-arm64` |
| `linux-x64-1` | KVM virtualized EL-compatible 8.8 x86_64 host; AMD EPYC 7742 64-Core Processor, 2 vCPU; `32565968 kB` MemTotal; Linux 5.15.0-316.196.4.1.el8uek.x86_64 kernel; manual runner `linux-x64-1` |

Remaining manifest blockers are corpus freeze/signature fields, not hardware fields or staged
corpus hashes.

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

The current runner can produce an Ethos-only Gate Zero result file after readiness turns green.
Competitor execution adapters and G2/G3 comparison rows remain separate implementation steps.

## Public-Claim Rule

Until Gate Zero produces `benchmarks/results/gate-zero/{g1,g2,g3}.json` from the frozen manifest
and pinned competitors, product language must stay at:

```text
Ethos is pre-alpha. Current results are engineering fixtures, not public benchmark claims.
```
