# Agent instructions

**Implementing anything in this repository? Start from an explicitly scoped issue, PR, or decider
request.** For release-specific work, read the current `docs/v<version>-release-prep.md` before
writing code. Do not infer a new public surface or workstream from historical planning records.

Other authoritative context, in reading order:

1. The scoped issue, PR, or decider request; for a release train, its
   `docs/v<version>-release-prep.md`.
2. `docs/execution-status.md` — current release state and explicit blockers.
3. `README.md` + `docs/public-boundary-claims.json` — approved public wording; never edit claim
   strings without the approval lane.
4. `SPEC.md`, `docs/determinism-contract.md`, `docs/decisions/` (ADRs) — contracts and decisions.
5. `docs/roadmap.md`, `IMPLEMENTATION_PLAN.md` — public direction and historical milestones.

Hard rules that apply to every change: determinism is a contract (byte-identical output under a
pinned profile — add double-run tests for new artifacts); fail closed on missing capability;
claims gate must stay green; no AGPL dependencies; PDFium stays caller-provided unless an
accepted ADR says otherwise; every landed change adds a `CHANGELOG.md` entry under Unreleased.

## Imported Claude Cowork project instructions
