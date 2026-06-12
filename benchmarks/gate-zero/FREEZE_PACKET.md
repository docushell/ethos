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
incomplete. A staged corpus now exists in `benchmarks/gate-zero/corpus/` with synthetic CC0 PDFs
and real redistributable official PDFs, but it is not a frozen benchmark corpus until the decider
signs it. The remaining work is product/benchmark-owner evidence gathering, not parser
implementation.

## Required External Outputs

| Output | Required file | Product acceptance |
| --- | --- | --- |
| Frozen corpus and hardware | `benchmarks/gate-zero/manifest.json` | staged corpus accepted, `frozen=true`, status `FROZEN-SIGNED`, freeze timestamp, signed-by value |
| Competitor pins | `benchmarks/competitors.lock.json` | Exact versions, runtime versions where applicable, artifact SHA256 values, and `pinned=true` for all Gate Zero competitors |
| Public naming acceptance | `docs/decisions/ADR-0006-package-identifiers.md` | Status `Accepted`; registry/trademark checks complete before public package/docs claims |

## Staged Corpus Seed

The existing CC0 synthetic fixtures have been copied into `benchmarks/gate-zero/corpus/` as a
staged Gate Zero seed. Four real official PDFs have also been added to exercise harder document
classes: forms, worksheets, long technical reports, tables, and dense requirements text. The
decider must still accept or amend this corpus before freezing.

| Candidate ID | Corpus file | SHA256 | Pages | Subsets | Product note |
| --- | --- | --- | ---: | --- | --- |
| simple-text | `benchmarks/gate-zero/corpus/simple-text.pdf` | `f2f6ab91c696a4dffd96512456184451634fda22e19face9f636f3b69c6286f3` | 1 | born_digital | Parser smoke seed |
| two-lines | `benchmarks/gate-zero/corpus/two-lines.pdf` | `28d9c089bced8c913e6e0440a937f36581ed0b951384787930ba5c52f47a5359` | 1 | born_digital | Paragraph grouping seed |
| two-columns | `benchmarks/gate-zero/corpus/two-columns.pdf` | `de50aafb08219aa7fefdcb13ef8975ebf362f52f4d558c2d274ca711ce9d9d79` | 1 | born_digital, multi_column | Multi-column seed |
| rotation-90 | `benchmarks/gate-zero/corpus/rotation-90.pdf` | `1400858e1c0fa0255a037463b4e44df6f9d740ac33583cc590c4ac5cfd2fcc9d` | 1 | born_digital, rotation | Rotation seed |
| hyphenated-line-break | `benchmarks/gate-zero/corpus/hyphenated-line-break.pdf` | `7f079977e8438cea4f4b876b3f67380f047218133b3193d7bae8130ac327eeeb` | 1 | born_digital, hyphenation, fonts | Hyphenation/font quirk seed |
| ligature-fi-embedded-font | `benchmarks/gate-zero/corpus/ligature-fi-embedded-font.pdf` | `7f99a763d765ea0d880fcd871171ac4811e23b9fc7c3912a391276fcbdf6431e` | 1 | born_digital, fonts, ligatures | Embedded-font ligature seed |
| irs-form-1040-2025 | `benchmarks/gate-zero/corpus/irs-form-1040-2025.pdf` | `3d31c226df0d189ced80e039d01cf0f8820c1019681a0f0ca6264de277b7e982` | 2 | born_digital, forms, tables, real_world | Dense government form with boxes, line items, labels, and two-page form layout |
| cfpb-home-loan-toolkit | `benchmarks/gate-zero/corpus/cfpb-home-loan-toolkit.pdf` | `eae4ec62ec46a96d1ac9157912f3fbaffa8f0c723da1407038257b2234c122e9` | 28 | born_digital, guide, worksheets, tables, real_world | Guide-style layout with worksheets, icons, bullets, sidebars, and table-like forms |
| nist-sp-800-53r5 | `benchmarks/gate-zero/corpus/nist-sp-800-53r5.pdf` | `fc63bcd61715d0181dd8e85998b1e6201ae3515fc6626102101cab1841e11ec6` | 492 | born_digital, technical_report, long_document, tables, real_world | Large technical control catalog with dense controls, appendices, references, and table-like structure |
| nist-sp-800-63b | `benchmarks/gate-zero/corpus/nist-sp-800-63b.pdf` | `ccfce7510a1267933f912d023306c6e7d485f21be63d271108b61aad6139127e` | 80 | born_digital, technical_report, tables, real_world | Technical guideline with structured requirements, tables, and references |

## Redistribution Notes

| Corpus file | Source | Redistribution note |
| --- | --- | --- |
| `irs-form-1040-2025.pdf` | `https://www.irs.gov/pub/irs-pdf/f1040.pdf` | Official Treasury/IRS form; treated as a U.S. federal government work for benchmark redistribution unless third-party material is separately marked |
| `cfpb-home-loan-toolkit.pdf` | `https://files.consumerfinance.gov/f/201503_cfpb_your-home-loan-toolkit-web.pdf` | Official Consumer Financial Protection Bureau guide; treated as a U.S. federal government work for benchmark redistribution unless third-party material is separately marked |
| `nist-sp-800-53r5.pdf` | `https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf` | The NIST PDF states it is not subject to copyright in the United States and that attribution is appreciated |
| `nist-sp-800-63b.pdf` | `https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63b.pdf` | Official NIST publication from the NVL Publications endpoint; public-domain-compatible federal technical publication unless third-party material is separately marked |

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
