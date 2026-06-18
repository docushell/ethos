# Milestone D `capability_downgrade` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow `capability_downgrade` contract-prep slice for Milestone D. It does
not add a new public command, binding, Node surface, MCP surface, hosted surface, adapter
hardening, crop API, or sandbox backend. The current executable carrier remains `ethos verify`;
`capability_downgrade` names the existing contract between grounding-source capability
declarations, structured verification-report capability limits, report warnings, and
capability-blocked checks.

## Contract Surface

`capability_downgrade` v1 consumes:

- capability declarations already exposed through `GroundingSource`;
- the active verification config, including claim kinds and evidence options;
- verification reports that surface missing capabilities through `capability_limits`;
- report-level `capability_limited` warnings when any structured capability limit is present;
- per-check `capability_blocked` status only when the missing capability blocks that specific
  check.

The current source-tree inventory for this contract boundary is
`examples/verify/capability_downgrade_v1_contract.json`. It binds existing native and
OpenDataLoader-style verification report goldens to expected capability limits, warnings, and
blocked-check reasons. The inventory also records category invariants for downgrade-free,
report-only downgrade, non-grounded downgrade, and check-blocked downgrade cases.

Focused validation command:

- `make milestone-d-capability-downgrade-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs the current capability-focused verification tests, schema/example validation,
status/roadmap guards, this contract guard, and diff hygiene. It intentionally stays narrower than
adapter or surface work.

## Supported v1 Boundaries

The v1 contract boundary is explicit and fail-closed:

- native Ethos grounding with declared spans, offsets, tables, fingerprint, and coordinate origin
  emits no capability downgrade;
- OpenDataLoader-style grounding without fingerprint, spans, character offsets, or coordinate
  origin emits structured capability limits and a report-level `capability_limited` warning;
- table-cell checks become `capability_blocked` with `missing_table_capability` only when the
  grounding source does not expose tables;
- evidence mismatches and not-found checks retain their specific diagnostics while still carrying
  report-level capability downgrade warnings when the source is limited;
- source-tree fixture validation pins the category invariants for report-level downgrade warnings,
  blocked checks, non-grounded checks, and `all_evidence_grounded`;
- `all_evidence_grounded` remains true only when every supported check is grounded and no stale,
  unsupported, or blocked check is present.

## Explicit Blockers For This Slice

This first `capability_downgrade` slice does not add:

- a new public command or binding surface;
- Python, Node, MCP, or hosted capability surfaces;
- adapter hardening beyond committed fixtures;
- crop API implementation;
- sandbox backend expansion;
- semantic or arithmetic verification.

Public-facing language remains limited to source-only pre-alpha internal continuation, evidence
grounding, diagnostics, fixture-backed validation, and explicit blockers.
