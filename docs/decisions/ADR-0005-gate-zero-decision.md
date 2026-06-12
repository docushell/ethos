# ADR-0005: Gate Zero Decision

- Status: **Template — filled by the decider in week 4 (days 18–20)**
- Governs: PRD §1.3; IMPLEMENTATION_PLAN §6.4

> Do not edit the decision rule. G2 or G3 failure always means FALLBACK. G1 failure with
> G2/G3 pass means the decider chooses FALLBACK or G1_RETRY (bounded, by week 6, corpus
> unchanged, no speed claims). A failed retry means FALLBACK. No other partial-credit path exists.

```
# ADR-0005: Gate Zero Decision
Date / Decider: <date> / Gate Zero decider (per ADR-0000)
Inputs: benchmarks/results/gate-zero/{g1,g2,g3}.json @ commit <sha>, manifest <sha>

G1 - Throughput: <measured pps> vs max(120 pps p50, 2x <ODL-remeasured pps>)
     on manifest subset `born_digital`, single core, independently on every
     recorded performance host (no averaging, no host substitution) -> PASS|FAIL
G2 - Footprint:  <bytes> vs 30 MB; <ratio> vs 1/10 ODL claim threshold
     (CLI + dynamic libs + PDFium payload + schemas + font assets;
      V8/XFA-enabled build = automatic FAIL; ratio miss blocks only the
      one-tenth-footprint claim per ADR-0008)                        -> PASS|FAIL + CLAIM_SUPPORTED|UNSUPPORTED
G3 - Determinism: <platforms>, <divergence count> on the FULL frozen manifest
     (byte-identical canonical payload + equal fingerprints;
      macOS arm64 + Linux x64 minimum)                              -> PASS|FAIL

Decision: PROCEED (Milestone B)
        | G1_RETRY (bounded retry by week 6; corpus unchanged; no speed claim)
        | FALLBACK (IMPLEMENTATION_PLAN §6.5; parser-core expansion stops)

Reproduction: <one-command repro per gate>
Hardware attestation: <runner strings from benchmarks/gate-zero/manifest.json>
```
