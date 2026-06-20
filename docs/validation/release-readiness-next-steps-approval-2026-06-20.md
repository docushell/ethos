# Release-Readiness Next-Step Approval - 2026-06-20

## Purpose

Record product approval for the ordered next-step sequence from H1 through release-candidate
validation gates. This is an execution-sequence approval only.

It does not close H1 or H2, does not approve public beta, does not approve public benchmark
reports, does not approve release artifacts, does not approve package publication, does not approve
production positioning, does not approve hosted surfaces, and does not approve wording beyond the
exact approved pre-alpha sentence.

## Status

Status: **approved next-step sequence for release-readiness work**.

Ethos remains source-only pre-alpha. Milestone E remains closed only for the current internal
source-only prep boundary. First-release, public-beta, public benchmark-report, package, hosted, and
production-positioning decisions remain blocked until their own gates and approvals close.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `42840eb`
- Approved by: product / decider manual review
- Approved sequence scope: next execution steps 1 through 5 only
- Excluded approvals: public benchmark reports, public comparison reports, release artifacts,
  package publication, production positioning, hosted surfaces, public beta, and wording beyond the
  exact approved pre-alpha sentence

## Approved Sequence

1. Close H1: execute and review the public-safe competitor comparison flow in `ethos-bench`, then
   record reviewable comparison rows without unsupported wording.
2. Close H2: complete `docs/public-release-checklist.md`, including explicit release/package
   artifact approval and passing claim-language gates.
3. Approve any wording beyond the exact pre-alpha sentence: benchmark owner maps each exact
   sentence to accepted evidence, and the decider approves the exact wording and surface.
4. Harden release-scope engineering blockers: release packaging/operator setup, stable CLI/Python
   docs, public setup path, Phase 2 project-maintained PDFium builds, broader corpus/failure
   fixtures, and cross-platform runtime provisioning.
5. Run release-candidate validation gates: source gates plus `ethos-bench` publication preflight,
   readiness, smoke, and test gates, then rerun posture and claims gates after any public-facing
   text changes.

## Required Before Status Change

- H1 closes with accepted, public-safe competitor comparison evidence and no unsupported wording.
- H2 closes with an explicitly approved public release/package checklist.
- Any wording beyond the exact approved pre-alpha sentence has exact evidence mapping and exact
  surface approval.
- Release-scope engineering blockers are either closed or explicitly accepted by a release-scope
  decision record.
- Release-candidate validation gates pass after all public-facing text and generated evidence are
  in their proposed final state.
