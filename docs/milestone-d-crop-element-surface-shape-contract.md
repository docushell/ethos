# Milestone D `crop_element_surface_shape` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow `crop_element_surface_shape` contract-prep slice for Milestone D.
It records the source-bound `ethos crop_element` CLI surface and the internal pre-alpha Python
wrapper over that CLI. It does not add a Node binding, MCP method, hosted surface,
sandbox-backed crop behavior, or foreign-adapter crop coordinate interpretation.

The current source-bound carriers are `ethos crop_element` and `ethos_pdf.crop_element`; both
support descriptor-only requests and rendered requests that bind caller-provided source PDF bytes.
`ethos verify --crop-dir` and optional `--crop-source-pdf` remain the verifier evidence-artifact
carrier. The `crop_element_surface_shape` contract names the callable surface shape that must
preserve the existing `crop_element` request and crop descriptor audit bindings before any
Node, MCP, hosted, sandbox-backed, or foreign-adapter surface is added.

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
the surface fields to the existing request and descriptor schemas and records the source-bound
CLI and Python command wrappers.

## Validation Target

- `make milestone-d-crop-element-surface-shape-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs the Python surface tests, schema/example validation, status guards, roadmap
guards, the surface-shape contract guard, and whitespace diff checks. It intentionally does not
guards, the surface-shape contract guard, and whitespace diff checks. It intentionally does not
add Node, MCP, hosted, sandbox-backed, or foreign-adapter surface validation.

## Boundaries Locked By This Slice

- the surface shape uses the existing request and descriptor schemas instead of defining new
  geometry semantics;
- descriptor-only and rendered modes keep the same conditional source-PDF requirements as the
  request and descriptor schemas;
- the current callable CLI boundary is native Ethos document plus explicit element id;
- the current CLI has a source-bound `ethos crop_element` command with descriptor-only and
  rendered modes;
- the current Python scaffold has a source-bound `ethos_pdf.crop_element` method over the
  caller-provided local CLI;
- Node, MCP, and hosted crop surfaces remain explicit blockers.

## Explicit Blockers For This Slice

This first `crop_element_surface_shape` slice does not add:

- additional CLI commands beyond source-bound `ethos crop_element`;
- Node, MCP, or hosted crop surfaces;
- sandbox backend behavior;
- foreign-adapter crop coordinate hardening.

Until those blockers are explicitly handled, public language remains limited to source-only
pre-alpha internal continuation, evidence grounding, diagnostics, fixture-backed validation, and
explicit blockers.
