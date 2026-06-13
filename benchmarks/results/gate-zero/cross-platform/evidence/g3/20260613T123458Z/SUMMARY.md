# Gate Zero G3 cross-platform Evidence Summary

- Source result: `benchmarks/results/gate-zero/g3.json`
- Source result SHA256: `9051afa565b3128c251603137c59930da502298cdde4780c65ce2e78a7d53a4e`
- Generated at: `2026-06-13T12:34:58Z`
- Overall status: `fail`
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
| Canonical payload hash | 5 |
| Document fingerprint | 5 |
| Warning IDs | 0 |
| Corpus binding | 0 |

## Platform Inputs

| Platform | Result | Status | Ethos Status | Runs | SHA256 |
| --- | --- | --- | --- | ---: | --- |
| linux-x64 | `benchmarks/results/gate-zero/linux-x64/g1.json` | `fail` | `pass` | 10 | `d3e8009d85c4` |
| macos-arm64 | `benchmarks/results/gate-zero/macos-arm64/g1.json` | `fail` | `pass` | 10 | `d35516c5d10e` |

## Failures

- simple-text canonical payload differs on linux-x64
- simple-text document fingerprint differs on linux-x64
- two-lines canonical payload differs on linux-x64
- two-lines document fingerprint differs on linux-x64
- two-columns canonical payload differs on linux-x64
- two-columns document fingerprint differs on linux-x64
- rotation-90 canonical payload differs on linux-x64
- rotation-90 document fingerprint differs on linux-x64
- hyphenated-line-break canonical payload differs on linux-x64
- hyphenated-line-break document fingerprint differs on linux-x64

## Interpretation Guardrail

G3 compares existing G1 Ethos canonical payload hashes, document fingerprints, warning IDs, and corpus bindings across required platforms. It does not run parsers or measure extraction quality.
