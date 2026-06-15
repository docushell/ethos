# ADR-0000: Gate Zero Decider

- Status: Accepted
- Date: 2026-06-11
- Governs: PRD v3.5 §1.3, §15; IMPLEMENTATION_PLAN §2 row 0.1

## Context

Gate Zero (week 4) is a single, named-decider evaluation of G1 throughput, G2 footprint, and G3 determinism against a frozen corpus manifest. The PRD requires the decider to be recorded before the clock starts; an unowned gate invites partial-credit drift.

## Decision

The Gate Zero decider is the **project lead role**.

- Sole inputs to the decision: `benchmarks/results/gate-zero/{g1,g2,g3}.json` plus reproduction commands and hardware attestation (handoff contract §5.2.4).
- The decision is recorded as ADR-0005 using the template in `ADR-0005-gate-zero-decision.md`.
- Decision space is fixed by PRD §1.3: PROCEED, G1_RETRY (only when G1 alone fails and G2/G3 pass; bounded, by week 6), or FALLBACK (§6.5 trust-layer pivot). G2 or G3 failure always means FALLBACK.
- The decider also signs off the corpus/hardware freeze (row 0.3) and any plan-level changes to gates or the week-4 bound.

## Consequences

- No Gate Zero measurement is valid until this ADR and the frozen manifest exist; corpus changes after kickoff void the measurement (PRD §1.3).
- No public speed claims unless G1 passes, including any approved retry (PRD §14).
