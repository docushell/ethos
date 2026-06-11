# ADR-0001: Staffing Confirmation vs Plan Schedule

- Status: **Proposed — requires decider confirmation before the week-1 clock starts**
- Date: 2026-06-11
- Governs: IMPLEMENTATION_PLAN §1.2, §2 row 0.2 (plan-level assumption, not a PRD requirement)

## Context

The plan's schedule (week-4 Gate Zero, week-13 and week-26 checkpoints) assumes: 2 senior Rust engineers + 1 bindings/infra engineer + 0.5 benchmark/devrel, dedicated. Lanes are work lanes, not headcount; review capacity caps parallelism at ~3 concurrent lanes.

## Decision (to be confirmed)

- [ ] Staffing matches the assumption → schedule stands as written.
- [ ] Staffing differs → record actual staffing here and recompute the schedule in the same PR that accepts this ADR. Release-2-horizon scope sheds first (plan §5.4).

Actual staffing at kickoff: _______________ (decider fills in)

## Consequences

Week 0 is not exited until this ADR is Accepted. A lane idle >1 week triggers re-scope at the check-in (risk R6).
