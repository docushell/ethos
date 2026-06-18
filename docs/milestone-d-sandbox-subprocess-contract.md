# Milestone D `sandbox_subprocess` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow `sandbox_subprocess` contract-prep slice for Milestone D. It does not
add a hardened OS sandbox, new public command, binding, Node surface, MCP surface, or hosted
surface. The current executable carrier remains the PDF worker process behind `ethos doc parse`
and `ethos fingerprint`; `sandbox_subprocess` names the future backend contract between hostile
PDF input, bounded worker execution, normalized document output, and stable error envelopes.

## Contract Surface

`sandbox_subprocess` v1 will consume:

- a `schemas/ethos-sandbox-subprocess-request.schema.json` request envelope carrying operation,
  PDF-byte input kind, limits, diagnostics intent, and failure-output policy;
- PDF input already accepted by the current parse/fingerprint paths;
- parse configuration, including page selection for document parsing and `max_parse_ms`;
- a worker boundary that returns either normalized graph data or a stable error envelope;
- optional diagnostics that may expose worker stderr only when explicitly requested.

The current source-tree inventory for this contract boundary is
`examples/sandbox/sandbox_subprocess_v1_contract.json`. It classifies existing worker tests that
exercise timeout handling, memory-limit error reporting, stable error relay, and diagnostics-gated
stderr behavior. Each inventory case binds to a request envelope under
`schemas/examples/sandbox-subprocess-*.example.json`.

Focused validation command:

- `make milestone-d-sandbox-subprocess-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs the current worker-boundary test slice, schema/example validation,
status/roadmap guards, this contract guard, and diff hygiene. It intentionally stays narrower than
backend hardening work.

## Supported v1 Boundaries

The v1 contract boundary is fail-closed and error-envelope-first:

- `max_parse_ms` timeout exits through the stable `parse_timeout` error code;
- worker memory-limit failures exit through the stable `memory_limit_exceeded` error code;
- stable worker error envelopes are relayed without converting them to generic failures;
- non-envelope worker stderr is hidden by default;
- non-envelope worker stderr is exposed only under explicit diagnostics;
- request envelopes bind each failure case to the intended operation, timeout limit, diagnostics
  mode, and failure-output policy;
- stdout remains empty on worker failures covered by this contract inventory.

## Explicit Blockers For This Slice

This first `sandbox_subprocess` slice does not add:

- hardened OS sandbox rules;
- network-denying runtime proof;
- file-descriptor or child-process enforcement;
- arbitrary filesystem allowlist enforcement;
- a new public command or binding surface;
- Python, Node, MCP, or hosted sandbox surfaces;
- crop or verification API changes.

Public-facing language remains limited to source-only pre-alpha internal continuation, evidence
grounding, diagnostics, fixture-backed validation, and explicit blockers.
