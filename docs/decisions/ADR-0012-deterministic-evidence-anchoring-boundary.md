# ADR-0012: Deterministic Evidence Anchoring Boundary

- Status: **Accepted**
- Date: 2026-06-24
- Decider: Gate Zero decider
- Governs: `ethos evidence anchor`, evidence-anchor request/report schemas, and parser-agnostic source binding.

## Context

`ethos verify --citations` checks AI-style citation claims against source evidence. That remains
useful, but document pipelines also need a lower-level primitive: check whether caller-provided
evidence refs bind to source evidence before any semantic answer workflow exists.

The boundary must remain parser- and app-agnostic. Native Ethos JSON and supported foreign parser
outputs enter through `GroundingSource`; callers own what they do with the resulting anchor report.

## Decision

Add `ethos evidence anchor <SOURCE> --evidence-refs <PATH>` as a narrow deterministic source-tracing
command.

The command:

- consumes one source document representation per invocation;
- consumes caller-provided evidence refs;
- emits a deterministic evidence-anchor report;
- reuses `GroundingSource`, `ParserIdentity`, `Capabilities`, `CoordinateOrigin`, and
  `CapabilityLimit`;
- supports native Ethos JSON and OpenDataLoader-style JSON in v1;
- reports stale fingerprints, missing evidence, mismatches, unsupported v1 kinds, and source
  capability limits explicitly.

The command does not perform semantic support checks, AI answer verification, RAG workflow,
source-map validation, evidence export, crop rendering, batch document-set processing, or
production-readiness gating.

## Consequences

- Evidence anchoring becomes a first-class source-bound primitive rather than being squeezed through
  citation-claim input.
- Existing `ethos verify` report semantics and goldens must remain unchanged.
- Public docs must describe evidence anchoring generically and preserve the public beta evaluation
  posture.
- Future parser adapters can participate when they expose the required data through
  `GroundingSource`; missing capabilities must remain explicit diagnostics.
