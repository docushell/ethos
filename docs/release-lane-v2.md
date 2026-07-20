# Release Lane v2 (NIP-7.1)

Status: **Accepted** (2026-07-19, decider direction: keep the process smooth end-to-end).
Created: 2026-07-19. Owner: product / decider. Plan reference: `NEXT_IMPLEMENTATION_PLAN.md` §NIP-7.

**Smoothness rule:** a routine release train never waits on ceremony. When the prep doc's gate
checklist is green, the train ships. The only human moments in the pipeline are PR review, the
registry publish itself, and public-wording changes — everything else is automated CI.

## Problem

The v0.1.x–v0.3.0 release lanes produced per-artifact chains of request → decision → operator
action → closeout records (30+ validation documents for three crate publications). That pattern
was correct for first-time surface classes: it forced explicit decisions while the project
established what "publishing" means here. For routine releases it now costs more maintainer
capacity than the product work it gates, and the capacity model (ADR-0001: one implementation
lane) cannot afford it.

## Rule

From acceptance of this document:

**A routine release train produces exactly two governance documents:**

1. **One release prep doc** — `docs/v<version>-release-prep.md` (current pilot:
   `docs/v0-4-0-release-prep.md`): included scope, explicit non-scope, canonical release
   sentence, and the gate checklist that must pass before publication.
2. **One closeout record** — `docs/validation/v<version>-release-closeout-<date>.md`: versions
   published per surface (crates.io / PyPI / npm / GitHub Release), artifact sha256 values,
   command evidence, wording confirmation (approved claim strings unchanged or the approved new
   packet applied verbatim), and any deviations.

Everything previously spread across per-artifact request/decision/evidence/closeout chains is a
**section inside those two documents**, not a separate file.

## What is retained, unchanged

- The public-boundary claims gate (`.github/scripts/public_boundary_claims_gate.py`) on every PR.
- Decider approval for any change to public wording (`README.md`,
  `docs/public-boundary-claims.json`). Wording packets are approved inside the prep doc.
- Operator actions remain manual and human-executed (registry publishes, tag pushes, GitHub
  Release edits). AI agents prepare evidence and commands; a human runs registry-facing actions.
- Version-activation guard pattern (source metadata bump as its own reviewed change).
- CHANGELOG discipline.

## What still requires the full (v1) multi-record lane

First-of-class surfaces only — the first occurrence of a surface class the project has never
shipped:

- first hosted or network-served surface (including any decision on the WASM playground);
- first bundled/project-distributed PDFium artifact (ADR-0015 outcome);
- first Windows packaged artifact;
- first paid/commercial or trademark-relevant surface;
- any release that changes verification-report semantics in a backward-incompatible way.

After a surface class ships once under v1, subsequent releases of that class ride the routine
two-document lane.

## Release train definition

A release train is one version number across all surfaces shipped together (source tag, crates,
wheel, npm, CLI artifacts). Trains ship when their prep-doc gate checklist is green — no fixed
cadence. Surfaces may be skipped in a train (recorded in the closeout) but never published
outside one.

## Pilot

The next release train (carrying NIP-5 install-friction work and any landed NIP-1/NIP-4
deliverables) is the pilot (NIP-7.2). Success criteria: exactly two governance documents, no
loss of evidence quality (closeout contains per-surface versions, hashes, and commands), decider
review time reduced.

## Decider sign-off

- [x] Accepted: 2026-07-19, per decider direction recorded in NIP-1 revision v1.2 (process must
  stay smooth from idea to release; no ceremony blockers).
- [ ] Amendments required: —
