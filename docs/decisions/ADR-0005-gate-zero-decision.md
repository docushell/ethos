# ADR-0005: Gate Zero Decision

- Status: **Accepted - PROCEED**
- Date: 2026-06-16
- Decider: project lead role, per ADR-0000
- Governs: PRD section 1.3; IMPLEMENTATION_PLAN section 6.4

This record indexes the committed Gate Zero evidence now available in the sibling
`ethos-bench` repository and records the decider's internal Gate Zero decision. It is not a
public benchmark report, release approval, package approval, production approval, or launch
approval.

## Decision Rule

Do not edit this decision rule.

- If G1, G2, and G3 are accepted by the decider, parser-core expansion may continue to
  Milestone B.
- If G1 is not accepted while G2 and G3 are accepted, the decider chooses either fallback or one
  bounded G1 remediation retry; the corpus remains unchanged and no public claim is allowed from
  the failed run.
- If G2 or G3 is not accepted, parser-core expansion stops and Ethos continues as a
  parser-agnostic trust layer over foreign parser output.
- No partial-credit path exists.

## Evidence Repositories

| Repository | Commit | Role |
| --- | --- | --- |
| `ethos` | `b128e93b6f8fc04b4160274935c1f7b289e955c8` | Source, frozen manifests, gate definitions, and decision record |
| `ethos-bench` | `9b8092f4f0706b632736b2d2dfb86d495887796c` | Generated result JSON and evidence bundles |

## Shared Inputs

| Input | SHA256 |
| --- | --- |
| `benchmarks/gate-zero/manifest.json` | `33f30da39cea31a92a80c25de48a88ff3861a625843e9dccca1ee3c87889f729` |
| `benchmarks/competitors.lock.json` | `35becebfbf2b4b10b14213ae4a986efc9805ed6b0cf7f5dc5878f7ba79b13afa` |
| current `benchmarks/gate-zero/gates.json` | `7c85a0c60a0e0c71de3860a75c6f545cabaa5c6a23fa88bd3aff602e11d18e65` |

## Source Result Files

The following status values are copied from the committed source result JSON files. They are
decision inputs only.

| Gate | Platform | Source result | Source SHA256 | Source JSON status |
| --- | --- | --- | --- | --- |
| G1 | `macos-arm64` | `benchmarks/results/gate-zero/macos-arm64/g1.json` | `d47d66d2be67bbd17af427da4d8f40fd39606c7dd737c8e997e512de247ac728` | `pass` |
| G1 | `linux-x64` | `benchmarks/results/gate-zero/linux-x64/g1.json` | `9f46794a7bf3c47902536057a240c42aa94258a062e19ab341cc9ceadce11337` | `pass` |
| G2 | `macos-arm64` | `benchmarks/results/gate-zero/macos-arm64/g2.json` | `5d32d8b36aa5b82a467e4614ff02e782630a1f4e13347b73a580bff26e58682c` | `pass` |
| G2 | `linux-x64` | `benchmarks/results/gate-zero/linux-x64/g2.json` | `351202a378beec450ad34515fbeee999fd7c452123de52a09b612f7cf812685e` | `pass` |
| G3 | `cross-platform` | `benchmarks/results/gate-zero/g3.json` | `7aa3e2033fbc33838eb0ddfd8556880e425863bf2314fed4215285cc4e386c12` | `pass` |

## Evidence Bundles

Each listed bundle has `reproduction-env.json` status `complete`; its `evidence-manifest.json`
source result hash matches the source result file above.

| Gate | Platform | Evidence bundle | Checksum manifest SHA256 |
| --- | --- | --- | --- |
| G1 | `macos-arm64` | `benchmarks/results/gate-zero/macos-arm64/evidence/g1/20260616T082540Z/` | `6749dc2ea8bc26ccff3b07ae645ce2775709d2d90ee3902e945ea647cb780c11` |
| G1 | `linux-x64` | `benchmarks/results/gate-zero/linux-x64/evidence/g1/20260616T082542Z/` | `1b9ae3886f5d0a12588091b4ee610f12c2529d704201a60edeb71018c660a2c3` |
| G2 | `macos-arm64` | `benchmarks/results/gate-zero/macos-arm64/evidence/g2/20260616T082541Z/` | `d9a7db140432b9524b1517aa47d885a2171aa7deb90fb6f8e0f8329d171f9be4` |
| G2 | `linux-x64` | `benchmarks/results/gate-zero/linux-x64/evidence/g2/20260613T122249Z/` | `07e6afa4dbf7f19cb8c90da3956946d9670ec8281b7422f96fc6dc59d3a1622b` |
| G3 | `cross-platform` | `benchmarks/results/gate-zero/cross-platform/evidence/g3/20260616T082543Z/` | `ea91b9cdbe2c60bbbbf30ba52390bbe6f598ac527019b8173bd86da1107eeab2` |

## Reproduction Pointers

The exact commands are preserved in each bundle as `reproduction-command.txt`; the resolved
environment sidecars are preserved as `reproduction-env.json`.

| Gate | Platform | Command sidecar | Environment sidecar |
| --- | --- | --- | --- |
| G1 | `macos-arm64` | `macos-arm64/evidence/g1/20260616T082540Z/reproduction-command.txt` | `macos-arm64/evidence/g1/20260616T082540Z/reproduction-env.json` |
| G1 | `linux-x64` | `linux-x64/evidence/g1/20260616T082542Z/reproduction-command.txt` | `linux-x64/evidence/g1/20260616T082542Z/reproduction-env.json` |
| G2 | `macos-arm64` | `macos-arm64/evidence/g2/20260616T082541Z/reproduction-command.txt` | `macos-arm64/evidence/g2/20260616T082541Z/reproduction-env.json` |
| G2 | `linux-x64` | `linux-x64/evidence/g2/20260613T122249Z/reproduction-command.txt` | `linux-x64/evidence/g2/20260613T122249Z/reproduction-env.json` |
| G3 | `cross-platform` | `cross-platform/evidence/g3/20260616T082543Z/reproduction-command.txt` | `cross-platform/evidence/g3/20260616T082543Z/reproduction-env.json` |

## Hardware Attestation Pointers

Hardware and observed host metadata are preserved in each bundle as `host-attestation.json`.

| Platform | Host attestation |
| --- | --- |
| `macos-arm64` G1 | `benchmarks/results/gate-zero/macos-arm64/evidence/g1/20260616T082540Z/host-attestation.json` |
| `macos-arm64` G2 | `benchmarks/results/gate-zero/macos-arm64/evidence/g2/20260616T082541Z/host-attestation.json` |
| `linux-x64` G1 | `benchmarks/results/gate-zero/linux-x64/evidence/g1/20260616T082542Z/host-attestation.json` |
| `linux-x64` G2 | `benchmarks/results/gate-zero/linux-x64/evidence/g2/20260613T122249Z/host-attestation.json` |
| `cross-platform` G3 | `benchmarks/results/gate-zero/cross-platform/evidence/g3/20260616T082543Z/host-attestation.json` |

## Review Caveat

`linux-x64` G2 cites `benchmarks/gate-zero/gates.json` SHA256
`602f82e3141e9826a893de509f3a1137430539a0166fd045d8c5f458d26efbb6`, while the current
gate-definition file is
`7c85a0c60a0e0c71de3860a75c6f545cabaa5c6a23fa88bd3aff602e11d18e65`.

The current hash was introduced by commit `b382d67f2ba9c1a3ad0363944bffaaba1c5ca86a`, which changed
the G3 wording and added ADR-0009 as a G3 source reference. The G2 section was not changed by that
commit.

Decider resolution: accepted for this decision. The `linux-x64` G2 result remains indexed exactly
as produced, with its recorded input hash, and the hash difference is not treated as a blocker for
the internal Gate Zero decision.

## Required Decision Check

The decision check was run before accepting this ADR:

```bash
python3 .github/scripts/gate_zero_evidence_preflight.py decision --ethos-bench ../ethos-bench
python3 .github/scripts/claims_gate.py
python3 .github/scripts/readiness_gate.py public
```

The first command reported `gate-zero evidence decision: green`.

## Decision

Decision: `PROCEED`.

Parser-core expansion may continue to Milestone B under the existing roadmap. This decision does
not authorize public benchmark language, release artifacts, package publication, production
positioning, or claims beyond the committed internal Gate Zero evidence.
