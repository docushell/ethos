# Gate Zero G3 cross-platform Evidence Summary

- Source result: `benchmarks/results/gate-zero/g3.json`
- Source result SHA256: `748d4bf9d7366bcb1f5aa9326bead9cd284f0abd39c360e9db114a9d5cabe2c1`
- Generated at: `2026-06-13T15:45:51Z`
- Overall status: `pass`
- Platforms: `macos-arm64, linux-x64`
- Corpus: `gate-zero-v1`
- Corpus files compared: `10`
- Definition: `benchmarks/gate-zero/gates.json`
- Reproduction command: `reproduction-command.txt`
- Reproduction env: `reproduction-env.json` (`complete`)
- Host attestation: `host-attestation.json`

## Determinism Result

| Check | Divergences |
| --- | ---: |
| Stable payload projection hash | 0 |
| Document fingerprint | 0 |
| Warning IDs | 0 |
| Corpus binding | 0 |

## Platform Inputs

| Platform | Result | Status | Ethos Status | Runs | SHA256 |
| --- | --- | --- | --- | ---: | --- |
| linux-x64 | `benchmarks/results/gate-zero/linux-x64/g1.json` | `fail` | `pass` | 10 | `c86d29fa531d` |
| macos-arm64 | `benchmarks/results/gate-zero/macos-arm64/g1.json` | `fail` | `pass` | 10 | `e495801af9f0` |

## Interpretation Guardrail

G3 compares existing G1 Ethos stable payload projection hashes, document fingerprints, warning IDs, and corpus bindings across required platforms. It does not run parsers or measure extraction quality.
