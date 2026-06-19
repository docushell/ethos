# Milestone D `crop_element` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow `crop_element` contract-prep slice for Milestone D. It includes an
internal Rust resolver in `ethos-core::crop_element` that validates request identity, resolves one
native document element, builds descriptor-only crop descriptors, and exposes that descriptor
path through the source-only pre-alpha `ethos crop_element` CLI command. It does not create a
Python binding, Node binding, MCP server method, hosted surface, rendered-crop backend change, or
sandbox behavior. The existing `ethos verify --crop-dir` and optional `--crop-source-pdf` carrier
remain the verifier evidence-artifact path; `crop_element` names the first-class descriptor
contract between a parsed Ethos document, an explicit element locator, and a crop descriptor.

## Contract Surface

`crop_element` v1 will consume:

- a `schemas/ethos-crop-element-request.schema.json` request envelope carrying the document
  fingerprint, `element_id`, requested rendering mode, and stable `request_ref`;
- a canonical Ethos document JSON grounding source with explicit element ids, page ids, integer
  bboxes, and a matching document fingerprint;
- an `element_id` locator that resolves through that request to one element with one page and one
  bbox;
- optional source PDF bytes whose fingerprint matches the document source fingerprint when
  rendered output is requested.

It emits a crop descriptor governed by `schemas/ethos-crop-descriptor.schema.json`. When rendering
is requested and a matching source PDF is available, the descriptor also binds the rendered PNG
filename, byte hash, dimensions, and source PDF fingerprint.

The current source-tree fixture for this contract boundary is
`examples/crop/crop_element_v1_contract.json`. That inventory binds
`schemas/examples/crop-element-request.example.json`,
`schemas/examples/document.example.json` element `e000002`, and
`schemas/examples/crop-descriptor.example.json`.

Focused validation command:

- `cargo test --locked -p ethos-core crop_element`
- `cargo test --locked -p ethos-cli --test verify crop_element_cli`
- `make milestone-d-crop-element-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs the internal Rust resolver fixture tests, current verifier crop coverage,
the descriptor-only CLI fixture tests, schema/example validation, status/roadmap guards, this
contract guard, and diff hygiene. It intentionally stays narrower than Python, Node, MCP, hosted,
rendered-backend, or sandbox implementation work.

## Supported v1 Boundaries

The v1 contract boundary is native, explicit, and source-bound:

- crop locators resolve through one `element_id`;
- the resolved element must carry one page id and one integer bbox with positive area inside the
  resolved page bounds;
- source-tree fixture validation binds crop element request identity to `document_fingerprint`,
  `element_id`, rendering mode, optional source PDF fingerprint, and
  `ethos.crop_element_request_ref.v1`;
- descriptor `crop_ref` values remain opaque artifact filenames for callers;
- source-tree fixture validation binds descriptor filenames to the logical evidence identity tuple
  of `document_fingerprint`, check id, page id, and `ethos.logical_crop_ref.v1`;
- source-tree fixture validation binds descriptor `text_sha256` values to verification evidence
  text when textual evidence is present;
- descriptor JSON remains the canonical crop audit artifact;
- rendered PNG output is optional and must be bound to a matching source PDF fingerprint;
- missing elements, missing pages, missing bboxes, malformed bboxes, non-positive bboxes,
  out-of-page bboxes, missing document fingerprints, unsafe crop artifact filenames, crop reference
  collisions, and source fingerprint mismatch fail closed.

The contract does not infer missing geometry, synthesize evidence, or reinterpret foreign adapter
coordinates. Cross-platform rendered crop byte identity is not part of this contract boundary.

## Relationship To Existing Verifier Artifacts

`ethos verify --crop-dir` can already emit crop descriptors for grounded evidence checks. That path
is evidence-artifact plumbing for verification reports. The `ethos crop_element` command is the
source-only descriptor carrier for one explicit native element request. Both paths delegate logical
crop descriptor identity and descriptor JSON shape to `ethos-core::crop_element` so verifier
artifacts and the descriptor-only command share source-only identity and descriptor types. Any
future non-CLI surface or rendered backend must preserve the same audit bindings before it can
wrap this descriptor contract:

- document fingerprint;
- element id;
- page id;
- bbox;
- crop descriptor filename;
- crop element request identity (`request_ref`);
- optional rendered PNG metadata and source PDF fingerprint.

## Explicit Blockers For This Slice

This first `crop_element` slice does not add:

- additional CLI commands beyond descriptor-only `ethos crop_element`;
- Python, Node, MCP, or hosted crop API surfaces;
- sandbox/subprocess backend expansion;
- rendered-crop backend changes;
- foreign-adapter crop coordinate hardening;
- cross-platform rendered-crop byte identity claims.

Public-facing language remains limited to source-only pre-alpha internal continuation, evidence
grounding, diagnostics, fixture-backed validation, and explicit blockers.
