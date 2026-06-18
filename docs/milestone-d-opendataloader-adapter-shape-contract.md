# Milestone D `opendataloader_adapter_shape` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow `opendataloader_adapter_shape` contract-prep slice for
Milestone D. It does not add a new public command, binding surface, adapter behavior, or
verification policy.

The current executable carrier remains the `ethos-grounding-opendataloader-json` adapter
crate and `ethos verify --grounding opendataloader-json`.
`opendataloader_adapter_shape` names the current contract between OpenDataLoader-style JSON
shapes and the parser-neutral `GroundingSource` boundary used by `ethos verify`.

## Contract Inputs

`opendataloader_adapter_shape` v1 consumes:

- the documented synthetic OpenDataLoader-style subset with `tool`, `pages`, `elements`, and
  optional `tables`;
- the pinned real OpenDataLoader 2.4.x tree shape with `kids`, `children`, `list items`,
  `list_items`, `rows`, and `cells`;
- deterministic malformed-input diagnostics for adapter shapes that cannot be mapped without
  silent approximation.

The executable inventory is `examples/verify/opendataloader_adapter_shape_v1_contract.json`.
It binds accepted and rejected adapter shapes to existing adapter crate tests, CLI grounding
tests, report goldens, usage diagnostics, and explicit blockers.

## Validation Target

- `make milestone-d-opendataloader-adapter-shape-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs the current adapter crate tests, OpenDataLoader-focused CLI verifier tests,
schema/example validation, status guards, roadmap guards, the contract guard, and whitespace
diff checks.

## Boundaries Locked By This Slice

- documented subset inputs retain parser identity, page geometry, elements, optional
  tables/cells, centipoint bbox quantization, and explicit capability downgrades;
- real OpenDataLoader-style tree inputs retain parser name, unknown parser version, adapter
  identity, derived page extents, deterministic element ids, text/child alias handling, and
  explicit capability downgrades;
- real OpenDataLoader-style table nodes map only when row/cell page, bbox, and text fields are
  explicit enough to produce deterministic cells;
- malformed bbox, unknown page references, malformed child containers, malformed table cells,
  and unrecognized roots fail closed with deterministic diagnostics.

## Explicit Blockers For This Slice

This first `opendataloader_adapter_shape` slice does not add:

- a new command or binding surface;
- a new foreign parser adapter;
- adapter behavior beyond committed fixtures;
- coordinate-origin inference;
- fingerprint, span, char-offset, or crop support;
- claim-kind expansion or semantic verification.

Until those blockers are explicitly handled, public language remains limited to source-only
pre-alpha internal continuation, evidence grounding, diagnostics, fixture-backed validation, and
explicit blockers.
