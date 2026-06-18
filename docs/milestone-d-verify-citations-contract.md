# Milestone D `verify_citations` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow first Milestone D slice for `verify_citations` v1. It does not
create a new public command, binding, or hosted surface. The current executable carrier remains
`ethos verify`; `verify_citations` names the contract between citation input, grounding source,
verification config, and verification report.

## Contract Surface

`verify_citations` v1 consumes:

- a grounding source: canonical Ethos document JSON, or a declared foreign adapter such as
  `opendataloader-json`;
- citation input governed by `schemas/ethos-citations.schema.json`;
- the pinned default verification config, or an explicit config governed by
  `schemas/ethos-verification-config.schema.json`.

It emits `verification_report.json`, governed by
`schemas/ethos-verification-report.schema.json`.

The example pair `schemas/examples/citations.example.json` and
`schemas/examples/verification-report.example.json` is the minimal source-tree fixture for this
contract. Schema validation now checks that the example report echoes the example claims in input
order and keeps the grounded gate coherent.

`examples/verify/verify_citations_v1_contract.json` classifies the existing executable verifier
cases as the current v1 contract inventory. Schema validation checks the inventory shape and
vocabulary; the guard checks that this inventory stays aligned with `examples/verify/cases.json`
and each referenced report golden.

Focused validation command:

- `make milestone-d-verify-citations-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs verifier contract tests, schema/example validation, status/roadmap guards, this
contract guard, and diff hygiene. It intentionally stays narrower than prior milestone composite
checks.

## Supported v1 Checks

The v1 supported claim kinds are:

- `quote`
- `value`
- `presence`
- `table_cell`

`region` and `other` remain explicit unsupported non-v1 inputs. They must be reported as
unsupported instead of approximated.

Evidence grounding is literal and diagnostic:

- quote checks use exact or normalized containment;
- value and table-cell checks use exact or normalized equality / table-cell lookup;
- presence checks only confirm the cited target exists;
- stale fingerprints, missing locators, missing source capabilities, and missing targets fail
  closed with stable check reasons;
- `all_evidence_grounded` is true only under the invariant documented in
  `schemas/ethos-verification-report.schema.json` and implemented by
  `compute_all_evidence_grounded`.

`semantic_unverified` stays false for current literal checks. Work that needs paraphrase,
arithmetic, cross-region synthesis, or unmodeled evidence must not be silently treated as
grounded.

## Capability And Crop Boundaries

Grounding sources declare capabilities in the verification report. Missing spans, char offsets,
tables, fingerprints, coordinate origins, or crop support surface as capability limits and
diagnostics.

Crop evidence remains bounded to existing verifier plumbing:

- `crop_ref` can appear only when the active config requests crops and the grounding source
  declares crop support;
- native crop descriptors and rendered crop artifacts remain verifier evidence artifacts;
- the broader first-class crop API is separate Milestone D work and is not part of this contract
  slice.

## Explicit Blockers For This Slice

This first D slice does not add:

- a new `verify_citations` CLI alias;
- Python, Node, MCP, or hosted API surfaces;
- broad foreign-adapter hardening beyond existing fixtures;
- crop API implementation;
- sandbox/subprocess backend expansion;
- semantic or arithmetic verification.

Public-facing language remains limited to source-only pre-alpha internal continuation, evidence
grounding, diagnostics, fixture-backed validation, and explicit blockers.
