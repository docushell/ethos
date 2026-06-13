# Gate Zero G1 linux-x64 Evidence Summary

- Source result: `benchmarks/results/gate-zero/linux-x64/g1.json`
- Source result SHA256: `c86d29fa531d0d34805509859a1692491d048ade22e5b8d00965e6dca80ac18b`
- Generated at: `2026-06-13T15:41:39Z`
- Overall status: `fail`
- Ethos status: `pass`
- Host: `linux-x64-1`
- Corpus: `gate-zero-v1`
- Reproduction command: `reproduction-command.txt`
- Reproduction env: `reproduction-env.json` (`complete`)
- Host attestation: `host-attestation.json`

## Parser Results

| Parser | Status | Failed Runs | Iterations | p50 ms | p95 ms | p99 ms | Peak RSS MiB | Install MiB | Output SHA256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Ethos | `pass` | 0/10 | 10 | 275.05 | 18491.41 | 18538.50 | 656.4 | 1.6 | `842d78cec62a` |
| OpenDataLoader | `pass` | 0/10 | 10 | 1841.70 | 68372.12 | 68575.15 | 5826.1 | 122.4 | `cbe52e73d230` |
| EdgeParse | `fail` | 3/10 | 10 | 240.77 | 22701.80 | 22853.63 | 1400.5 | 109.7 | n/a |
| LiteParse | `pass` | 0/10 | 10 | 243.72 | 5532.23 | 5602.29 | 113.5 | 119.8 | `bfe9e103d863` |
| PyMuPDF4LLM | `fail` | 1/10 | 10 | 3355.51 | 120194.49 | 120196.64 | 513.7 | 319.5 | n/a |

## EdgeParse Determinism Note

EdgeParse is recorded as a context/non-gating competitor row and failed G1 determinism because `output_sha256 changed across iterations`.

- `cfpb-home-loan-toolkit`
- `nist-sp-800-53r5`
- `nist-sp-800-63b`

Ethos passed all top-level G1 determinism checks in this result. The overall benchmark status is `fail` because competitor failures are preserved as benchmark data.

## Interpretation Guardrail

This summary supports claims about recorded determinism, footprint, measured latency, and RSS when available for this pinned corpus and host. It does not claim Ethos is the fastest parser overall.
