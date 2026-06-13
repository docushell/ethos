# Gate Zero G2 linux-x64 Evidence Summary

- Source result: `benchmarks/results/gate-zero/linux-x64/g2.json`
- Source result SHA256: `351202a378beec450ad34515fbeee999fd7c452123de52a09b612f7cf812685e`
- Generated at: `2026-06-13T12:22:49Z`
- Overall status: `pass`
- Host: `linux-x64-1`
- Corpus: `gate-zero-v1`
- Definition: `benchmarks/gate-zero/gates.json`
- Reproduction command: `reproduction-command.txt`
- Reproduction env: `reproduction-env.json` (`complete`)
- Host attestation: `host-attestation.json`

## Footprint Result

| Subject | Bytes | MiB |
| --- | ---: | ---: |
| Ethos base parser footprint | 9233208 | 8.8 |
| OpenDataLoader install footprint | 128392275 | 122.4 |

## Thresholds

- Max Ethos footprint: `30000000` bytes
- Ethos/OpenDataLoader claim ratio threshold: `0.1`
- Measured Ethos/OpenDataLoader ratio: `0.0719`
- One-tenth OpenDataLoader footprint claim supported: `True`
- PDFium V8 enabled: `False`
- PDFium XFA enabled: `False`

## Ethos Footprint Items

| Role | Path | Bytes | SHA256 |
| --- | --- | ---: | --- |
| ethos-cli | `target/release/ethos` | 1588024 | `684a45479b3e` |
| pdfium-library | `/home/<private-user-pattern>/ethos-bench/pdfium/lib/libpdfium.so` | 7645184 | `f728930966f5` |

## Interpretation Guardrail

G2 is a footprint gate only. It does not measure parser speed, output quality, or cross-platform determinism.
