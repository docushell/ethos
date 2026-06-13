# Gate Zero G1 macos-arm64 Evidence Summary

- Source result: `benchmarks/results/gate-zero/macos-arm64/g1.json`
- Source result SHA256: `e495801af9f07825292f70c6fe5e00aa8230dfd08ea09aaa3a316412a2d60524`
- Generated at: `2026-06-13T14:24:05Z`
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
| Ethos | `pass` | 0/10 | 10 | 102.16 | 3732.95 | 3763.26 | n/a | 1.2 | `f85e5e507921` |
| OpenDataLoader | `pass` | 0/10 | 10 | 314.05 | 14372.36 | 14444.61 | n/a | 34.1 | `cbe52e73d230` |
| EdgeParse | `fail` | 3/10 | 10 | 49.25 | 4392.19 | 4393.42 | n/a | 19.4 | n/a |
| LiteParse | `pass` | 0/10 | 10 | 75.38 | 1126.22 | 1144.13 | n/a | 26.8 | `821c63acaefa` |
| PyMuPDF4LLM | `pass` | 0/10 | 10 | 322.80 | 58497.01 | 58513.76 | n/a | 204.9 | `43b0eaecd27a` |

## EdgeParse Determinism Note

EdgeParse is recorded as a context/non-gating competitor row and failed G1 determinism because `output_sha256 changed across iterations`.

- `cfpb-home-loan-toolkit`
- `nist-sp-800-53r5`
- `nist-sp-800-63b`

Ethos passed all top-level G1 determinism checks in this result. The overall benchmark status is `fail` because competitor failures are preserved as benchmark data.

## Interpretation Guardrail

This summary supports claims about recorded determinism, footprint, measured latency, and RSS when available for this pinned corpus and host. It does not claim Ethos is the fastest parser overall.
