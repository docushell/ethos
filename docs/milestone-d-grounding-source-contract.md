# Milestone D `grounding_source` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow `grounding_source` contract-prep slice for Milestone D. It does
not add a new public command, binding surface, adapter behavior, crop surface, or sandbox
behavior.

The current executable carrier remains the `GroundingSource` trait in `ethos-core`, plus the
existing `ethos verify` reports that embed parser identity and declared capabilities.
`grounding_source` names the parser-neutral evidence boundary between native Ethos document
JSON, foreign adapter output, and the verifier.

## Contract Surface

`grounding_source` v1 covers:

- parser identity through `ParserIdentity`;
- capability declarations through `Capabilities`;
- optional document fingerprint exposure;
- deterministic page, element, span, and table evidence ordering;
- optional crop references that remain opaque audit pointers;
- report grounding metadata under `verification_report.grounding`.

The executable inventory is `examples/verify/grounding_source_v1_contract.json`. It binds the
current trait surface to native Ethos and OpenDataLoader-style report goldens plus the trait
default-safety test.

## Validation Target

- `make milestone-d-grounding-source-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs the focused core grounding test, native and OpenDataLoader-style CLI verifier
checks, schema/example validation, status guards, roadmap guards, the contract guard, and
whitespace diff checks.

## Boundaries Locked By This Slice

- native Ethos document JSON remains a `GroundingSource` with parser name `ethos`, a declared
  fingerprint, top-left coordinate origin, spans, char offsets, and tables;
- OpenDataLoader-style JSON remains a foreign `GroundingSource` through the `opendataloader-json`
  adapter, with explicit missing fingerprint/span/char-offset/crop capabilities and unknown
  coordinate origin;
- `ethos verify` reports echo only parser identity and capabilities under `grounding`;
- default optional trait methods remain safe: empty spans, empty tables, no crop reference, and
  linear element lookup.

## Explicit Blockers For This Slice

This first `grounding_source` slice does not add:

- a new command or binding surface;
- a new foreign parser adapter;
- adapter behavior beyond committed fixtures;
- first-class crop API behavior;
- sandbox backend behavior;
- claim-kind expansion or semantic verification.

Until those blockers are explicitly handled, public language remains limited to source-only
pre-alpha internal continuation, evidence grounding, diagnostics, fixture-backed validation, and
explicit blockers.
