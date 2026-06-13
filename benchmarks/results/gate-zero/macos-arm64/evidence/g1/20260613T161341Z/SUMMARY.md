# Gate Zero G1 macos-arm64 Evidence Summary

- Source result: `benchmarks/results/gate-zero/macos-arm64/g1.json`
- Source result SHA256: `b2fa4d8873915c88be3d1cc92079eaf2e1c5b9926fcf3be8e69eccb8d5f551e4`
- Generated at: `2026-06-13T16:13:41Z`
- Overall status: `fail`
- Ethos status: `pass`
- Host: `mac-m4pro-arm64`
- Corpus: `gate-zero-v1`
- Reproduction command: `reproduction-command.txt`
- Reproduction env: `reproduction-env.json` (`complete`)
- Host attestation: `host-attestation.json`

## Parser Results

| Parser | Status | Failed Runs | Iterations | p50 ms | p95 ms | p99 ms | Peak RSS MiB | Install MiB | Output SHA256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Ethos | `pass` | 0/10 | 10 | 110.03 | 3799.10 | 3803.98 | 974.1 | 1.2 | `f85e5e507921` |
| OpenDataLoader | `pass` | 0/10 | 10 | 297.48 | 14291.39 | 14362.11 | 3604.2 | 34.1 | `cbe52e73d230` |
| EdgeParse | `fail` | 3/10 | 10 | 75.21 | 4479.73 | 4490.91 | 1476.6 | 19.4 | n/a |
| LiteParse | `pass` | 0/10 | 10 | 82.01 | 1089.06 | 1094.85 | 141.6 | 26.8 | `821c63acaefa` |
| PyMuPDF4LLM | `pass` | 0/10 | 10 | 333.54 | 58492.31 | 58500.19 | 8196.9 | 204.9 | `43b0eaecd27a` |

## EdgeParse Determinism Note

EdgeParse is recorded as a context/non-gating competitor row and failed G1 determinism because `output_sha256 changed across iterations`.

- `cfpb-home-loan-toolkit`
- `nist-sp-800-53r5`
- `nist-sp-800-63b`

Ethos passed all top-level G1 determinism checks in this result. The overall benchmark status is `fail` because competitor failures are preserved as benchmark data.

## Interpretation Guardrail

This summary supports claims about recorded determinism, footprint, measured latency, and RSS when available for this pinned corpus and host. It does not claim Ethos is the fastest parser overall.
