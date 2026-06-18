# Milestone D `crop_element_surface_shape` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow `crop_element_surface_shape` contract-prep slice for Milestone D.
It does not add a first-class CLI command, Python method, Node binding, MCP method, hosted
surface, crop renderer, or sandbox behavior.

The current executable crop carrier remains `ethos verify --crop-dir` and optional
`--crop-source-pdf`. `crop_element_surface_shape` names the future callable surface shape that
must preserve the existing `crop_element` request and crop descriptor audit bindings before any
first-class surface is added.

## Surface Shape

`crop_element_surface_shape` v1 is a shape contract over existing artifacts:

- document identity maps to `document_fingerprint` in
  `schemas/ethos-crop-element-request.schema.json`;
- the explicit element locator maps to `element_id`;
- rendering mode maps to `rendering`;
- optional source PDF identity maps to `source_pdf_fingerprint` when rendering is requested;
- descriptor output maps to `schemas/ethos-crop-descriptor.schema.json`;
- rendered artifact metadata remains descriptor-owned when rendered output exists.

The executable inventory is `examples/crop/crop_element_surface_shape_v1_contract.json`. It binds
the future surface fields to the existing request and descriptor schemas, and records that the
current CLI and Python surfaces intentionally do not expose a first-class crop call.

## Validation Target

- `make milestone-d-crop-element-surface-shape-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs schema/example validation, status guards, roadmap guards, the surface-shape
contract guard, and whitespace diff checks. It intentionally does not run rendered crop comparison
or Python surface tests because this slice does not implement that surface.

## Boundaries Locked By This Slice

- the surface shape uses the existing request and descriptor schemas instead of defining new
  geometry semantics;
- descriptor-only and rendered modes keep the same conditional source-PDF requirements as the
  request and descriptor schemas;
- the future callable boundary remains native Ethos document plus explicit element id;
- the current CLI still has no first-class `crop_element` command;
- the current Python scaffold still has no crop method;
- Node, MCP, and hosted crop surfaces remain explicit blockers.

## Explicit Blockers For This Slice

This first `crop_element_surface_shape` slice does not add:

- a first-class `crop_element` CLI command;
- a Python crop method;
- Node, MCP, or hosted crop surfaces;
- rendered-crop backend changes;
- sandbox backend behavior;
- foreign-adapter crop coordinate hardening.

Until those blockers are explicitly handled, public language remains limited to source-only
pre-alpha internal continuation, evidence grounding, diagnostics, fixture-backed validation, and
explicit blockers.
