# Gate Zero G2 macos-arm64 Evidence Summary

- Source result: `benchmarks/results/gate-zero/macos-arm64/g2.json`
- Source result SHA256: `7c66ef9e7b51628d0986feaed276ffc2d3528d011d3ee0e83f5164035c3c9dc4`
- Generated at: `2026-06-12T14:20:14Z`
- Overall status: `pass`
- Host: `mac-m4pro-arm64`
- Corpus: `gate-zero-v1`
- Definition: `benchmarks/gate-zero/gates.json`
- Reproduction command: `reproduction-command.txt`
- Reproduction env: `reproduction-env.json` (`complete`)
- Host attestation: `host-attestation.json`

## Footprint Result

| Subject | Bytes | MiB |
| --- | ---: | ---: |
| Ethos base parser footprint | 9009728 | 8.6 |
| OpenDataLoader install footprint | 35753427 | 34.1 |

## Thresholds

- Max Ethos footprint: `30000000` bytes
- Ethos/OpenDataLoader claim ratio threshold: `0.1`
- Measured Ethos/OpenDataLoader ratio: `0.2520`
- One-tenth OpenDataLoader footprint claim supported: `False`
- PDFium V8 enabled: `False`
- PDFium XFA enabled: `False`

## Ethos Footprint Items

| Role | Path | Bytes | SHA256 |
| --- | --- | ---: | --- |
| ethos-cli | `target/release/ethos` | 1277392 | `0de71fc5439e` |
| pdfium-library | `/private/tmp/ethos-pdfium/lib/libpdfium.dylib` | 7732336 | `1bc45b15466b` |

## Interpretation Guardrail

G2 is a footprint gate only. It does not measure parser speed, output quality, or cross-platform determinism.
