# ADR-0007: Trust Layer First

- Status: **Accepted**
- Date: 2026-06-12
- Governs: PRD v3.5 §1.3, §1.5, §5.4, §8, §14; IMPLEMENTATION_PLAN §5.1, §6.5; risk R11

## Context

Ethos has two useful but asymmetric bets:

1. A deterministic PDF parser can produce stable, fingerprinted artifacts.
2. A parser-agnostic grounding and verification layer can make citation evidence auditable across
   Ethos output and foreign parser output.

The parser work is necessary for Gate Zero and for the native Release 1 experience, but it is not
the strategic moat by itself. If the roadmap, public language, or milestone sequencing makes Ethos
look like a parser project first, the project competes directly with mature parser stacks and loses
the differentiated trust story.

This is the existential product risk captured by plan risk R11: the trust wedge arrives too late and
Ethos is dismissed as another parser.

## Decision

Ethos is a verification and grounding layer that includes a deterministic parser, not a parser that
may later add verification.

This principle governs architecture, planning, and public positioning:

- `GroundingSource`, verification schemas, grounding adapters, and `ethos verify` are core
  architecture, not fallback-only features.
- The deterministic parser exists to provide a high-quality native `GroundingSource` and canonical
  artifacts; it must remain swappable behind parser boundaries.
- `ethos-verify` must stay parser-agnostic and must never depend on `ethos-pdf`, PDFium, layout
  internals, or Ethos-only document assumptions.
- Milestone language should lead with grounding, verification, evidence reports, and citations
  whenever describing Ethos' product wedge.
- Parser expansion beyond the minimum needed for Gate Zero should not outrun a working verification
  alpha over at least one foreign parser adapter.

## Consequences

- Milestone A must leave the trust boundary real: `GroundingSource`, verification report/config
  schemas, the OpenDataLoader grounding adapter stub, and the `ethos verify` CLI stub are required
  A-stage artifacts.
- Milestone B should prioritize `ethos verify` alpha behavior before broad parser expansion:
  real quote/presence checks, citation input handling, stale-fingerprint behavior, and explicit
  capability-limited reports over foreign parser output.
- Gate Zero may still evaluate native parser viability, but a passing parser benchmark is not a
  substitute for the trust-layer deliverable.
- Public claims must not imply Ethos is primarily a PDF parser. The acceptable phrasing is that
  Ethos provides verification and grounding for document evidence, with a deterministic parser as
  one supported grounding source.
- If staffing pressure forces scope cuts, optional surfaces and parser breadth are cut before the
  parser-agnostic verification path.
