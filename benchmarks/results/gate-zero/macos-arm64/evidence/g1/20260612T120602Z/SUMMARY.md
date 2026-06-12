# Gate Zero G1 macos-arm64 Evidence Summary

- Source result: `benchmarks/results/gate-zero/macos-arm64/g1.json`
- Source result SHA256: `d35516c5d10e02cc3c581cf518252df7350351dc7c071e03ca2f51d9694e870f`
- Generated at: `2026-06-12T12:06:02Z`
- Overall status: `fail`
- Ethos status: `pass`
- Host: `mac-m4pro-arm64`
- Corpus: `gate-zero-v1`
- Reproduction command: `reproduction-command.txt`
- Reproduction env: `reproduction-env.json` (`incomplete`)
- Host attestation: `host-attestation.json`

## Parser Results

| Parser | Status | Failed Runs | Iterations | p50 ms | p95 ms | p99 ms | Peak RSS MiB | Install MiB | Output SHA256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Ethos | `pass` | 0/10 | 3 | 128.85 | 4141.90 | 4150.79 | 525.7 | 1.2 | `4b7b1225544f` |
| OpenDataLoader | `pass` | 0/10 | 3 | 435.87 | 20825.55 | 20833.04 | 3590.8 | 34.1 | `9e6c611e5c3c` |
| EdgeParse | `fail` | 3/10 | 3 | 110.80 | 6730.54 | 6736.27 | 1509.7 | 19.4 | n/a |
| LiteParse | `pass` | 0/10 | 3 | 93.85 | 1679.48 | 1683.61 | 129.8 | 26.8 | `be99bd1fef79` |
| PyMuPDF4LLM | `pass` | 0/10 | 3 | 547.65 | 85757.61 | 85802.10 | 8701.8 | 204.9 | `0f694929c21d` |

## EdgeParse Determinism Note

EdgeParse is recorded as a context/non-gating competitor row and failed G1 determinism because `output_sha256 changed across iterations`.

- `cfpb-home-loan-toolkit`
- `nist-sp-800-53r5`
- `nist-sp-800-63b`

Ethos passed all top-level G1 determinism checks in this result. The overall benchmark status is `fail` because competitor failures are preserved as benchmark data.

## Interpretation Guardrail

This summary supports claims about recorded determinism, footprint, and measured latency/RSS for this pinned corpus and host. It does not claim Ethos is the fastest parser overall.
