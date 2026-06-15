# Ethos Governance

## Maintainer ladder

| Role | Earned by | Responsibilities |
| --- | --- | --- |
| Contributor | Any accepted DCO-signed PR | — |
| Reviewer | Sustained quality contributions; nominated by a maintainer | Reviews PRs in their area; enforces fixtures-first, claims discipline, contract-change labeling |
| Maintainer | Sustained reviewership; lazy consensus of maintainers | Merge rights; triage; owns one or more lanes; can propose ADRs |
| Release owner | Appointed per release by maintainers | Owns release checklist, claim audit, footprint gate, NOTICE/license manifests |

Current maintainers are listed in this file's history until a `MAINTAINERS.md` split is
warranted. The project lead role owns the Gate Zero decider responsibility (ADR-0000).

## Decision making

- Day-to-day: lazy consensus on PRs.
- Architecture and contract decisions: ADR in `docs/decisions/`, merged by PR.
- Contract changes (`schemas/`, c14n spec, error/warning codes, deterministic profile):
  PR labeled `contract-change` + version bump + downstream lane sign-off.
- Plan-level changes (gates, week-4 bound, Release 1 scope): require decider sign-off.

## Cadence and transparency

- Public roadmap: `docs/roadmap.md`, updated at every milestone boundary.
- Landscape refresh: before each milestone and at least every 90 days (`docs/landscape-log.md`).
- Discussion channel: GitHub Discussions for design questions and user feedback.
- Issue templates exist for bugs, parser failures, benchmark questions, and adapter requests;
  security reports go through private vulnerability reporting (`SECURITY.md`).

## Service-level objectives (from public launch)

- Median first maintainer response on issues: **< 48 hours**, measured monthly.
- OpenSSF Scorecard tracked monthly; security regressions are release blockers.
- `good-first-issue` funnel and fixture-contribution path reviewed monthly.
- Trust-loop activation tracked from documented examples/download telemetry where privacy-safe.

## Claims discipline

CI blocks "#1"-style superlative claims and unearned benchmark/failure-corpus claims in
README/docs/announcements. Published numbers come only from one-command-reproducible harness
JSON with pinned competitor versions and labeled tiers. No public speed claims unless Gate
Zero G1 passed (including an approved retry).
