# Gate Zero G2 macos-arm64 Evidence Summary

- Source result: `benchmarks/results/gate-zero/macos-arm64/g2.json`
- Source result SHA256: `bf218d66123f1e1298337c2b7845e66c1ff26ceb0788f6f48748e00b6a60b770`
- Generated at: `2026-06-12T14:20:14Z`
- Overall status: `fail`
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
- Max Ethos/OpenDataLoader ratio: `0.1`
- Measured Ethos/OpenDataLoader ratio: `0.2520`
- PDFium V8 enabled: `False`
- PDFium XFA enabled: `False`

## Ethos Footprint Items

| Role | Path | Bytes | SHA256 |
| --- | --- | ---: | --- |
| ethos-cli | `target/release/ethos` | 1277392 | `0de71fc5439e` |
| pdfium-library | `/private/tmp/ethos-pdfium/lib/libpdfium.dylib` | 7732336 | `1bc45b15466b` |

## Failures

- ethos install size exceeds OpenDataLoader ratio threshold

## Interpretation Guardrail

G2 is a footprint gate only. It does not measure parser speed, output quality, or cross-platform determinism.
