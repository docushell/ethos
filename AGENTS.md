# Agent instructions

**Implementing anything in this repository? Read `NEXT_IMPLEMENTATION_PLAN.md` first.**
It is the canonical "what to build next" document: pick the highest-priority unblocked task from
its Progress Ledger (§7), follow its operating rules (§2), and update the ledger row when you
finish. Do not start new workstreams that are not in that plan without a decider note.

Other authoritative context, in reading order:

1. `NEXT_IMPLEMENTATION_PLAN.md` — active plan, task ledger, guardrails.
2. `docs/execution-status.md` — current release state and explicit blockers.
3. `README.md` + `docs/public-boundary-claims.json` — approved public wording; never edit claim
   strings without the approval lane.
4. `SPEC.md`, `docs/determinism-contract.md`, `docs/decisions/` (ADRs) — contracts and decisions.
5. `IMPLEMENTATION_PLAN.md`, `docs/roadmap.md` — historical milestone plan and closeout record.

Hard rules that apply to every change: determinism is a contract (byte-identical output under a
pinned profile — add double-run tests for new artifacts); fail closed on missing capability;
claims gate must stay green; no AGPL dependencies; PDFium stays caller-provided unless an
accepted ADR says otherwise; every landed change adds a `CHANGELOG.md` entry under Unreleased.

## Imported Claude Cowork project instructions
