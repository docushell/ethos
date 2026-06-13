# Gate Zero G1 linux-x64 Evidence Summary

- Source result: `benchmarks/results/gate-zero/linux-x64/g1.json`
- Source result SHA256: `d3e8009d85c40073fe687f1fd2ea2e329fd960aaad244027082bc0fc3abb4e0a`
- Generated at: `2026-06-13T12:14:39Z`
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
| Ethos | `pass` | 0/10 | 10 | 154.47 | 14614.56 | 14621.82 | 426.4 | 1.5 | `726db15df564` |
| OpenDataLoader | `pass` | 0/10 | 10 | 1821.51 | 74316.60 | 76546.70 | 6051.9 | 122.4 | `9e6c611e5c3c` |
| EdgeParse | `fail` | 3/10 | 10 | 234.77 | 31262.58 | 34779.34 | 1394.7 | 109.7 | n/a |
| LiteParse | `pass` | 0/10 | 10 | 242.31 | 5602.32 | 5769.06 | 124.4 | 119.8 | `88d2a46aebaa` |
| PyMuPDF4LLM | `fail` | 1/10 | 10 | 2491.87 | 120230.10 | 120271.63 | 513.8 | 319.5 | n/a |

## EdgeParse Determinism Note

EdgeParse is recorded as a context/non-gating competitor row and failed G1 determinism because `output_sha256 changed across iterations`.

- `cfpb-home-loan-toolkit`
- `nist-sp-800-53r5`
- `nist-sp-800-63b`

Ethos passed all top-level G1 determinism checks in this result. The overall benchmark status is `fail` because competitor failures are preserved as benchmark data.

## Interpretation Guardrail

This summary supports claims about recorded determinism, footprint, and measured latency/RSS for this pinned corpus and host. It does not claim Ethos is the fastest parser overall.
