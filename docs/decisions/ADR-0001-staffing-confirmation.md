# ADR-0001: Staffing Confirmation vs Plan Schedule

- Status: **Accepted**
- Date: 2026-06-11
- Governs: IMPLEMENTATION_PLAN §1.2, §2 row 0.2 (plan-level assumption, not a PRD requirement)

## Context

The plan's schedule (week-4 Gate Zero, week-13 and week-26 checkpoints) assumes: 2 senior Rust engineers + 1 bindings/infra engineer + 0.5 benchmark/devrel, dedicated. Lanes are work lanes, not headcount; review capacity caps parallelism at ~3 concurrent lanes.

## Decision (to be confirmed)

- [ ] Staffing matches the assumption → schedule stands as written.
- [x] Staffing differs → record actual staffing here and recompute the schedule in the same PR that accepts this ADR. Release-2-horizon scope sheds first (plan §5.4).

Actual staffing at kickoff: 1 senior Rust engineer + 0.25 benchmark/devrel, part-time

## Consequences

Week 0 is not exited until this ADR is Accepted and the schedule is recomputed in the same PR. A lane idle >1 week triggers re-scope at the check-in (risk R6).

Accepted outcome: `IMPLEMENTATION_PLAN.md` v2.2 and `docs/roadmap.md` use a reduced-staff schedule with one active implementation lane plus 0.25 benchmark/devrel support. Gate Zero moves to week 8, the first A-C checkpoint moves to week 22, and the public-beta checkpoint moves to week 40.

Release-2-horizon scope sheds first. Node beta and MCP experimental work require either a staffed bindings/infra owner or an explicit release-scope ADR before any public claim includes those surfaces.
