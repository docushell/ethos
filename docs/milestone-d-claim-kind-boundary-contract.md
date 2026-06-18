# Milestone D `claim_kind_boundary` v1 Contract

Status: source-only pre-alpha contract work for internal Milestone D continuation.

This note defines the narrow `claim_kind_boundary` contract-prep slice for Milestone D. It does
not add new claim-kind support, a new command, a binding surface, Node surface, MCP surface, hosted
surface, crop behavior, or sandbox behavior. The current executable carrier remains `ethos verify`.

`claim_kind_boundary` names the v1 boundary between supported literal claim kinds and explicit
non-v1 claim diagnostics. This keeps future claim-kind expansion from silently changing the
current trust loop.

## Contract Surface

`claim_kind_boundary` v1 is defined by the current schemas and fixtures:

- `schemas/ethos-citations.schema.json` admits `quote`, `value`, `presence`, `table_cell`,
  `region`, and `other` citation input kinds so non-v1 claims can be reported explicitly;
- `schemas/ethos-verification-config.schema.json` accepts only `quote`, `value`, `presence`, and
  `table_cell` in `claim_kinds`;
- `schemas/ethos-verification-report.schema.json` reports non-v1 claim checks with
  `unsupported_claim_kind`, `match_method: none`, no evidence, and `all_evidence_grounded: false`;
- `examples/verify/native_non_v1_claims_citations.json` and
  `examples/verify/goldens/native_non_v1_claims_report.json` are the current fixture pair.

The executable inventory is `examples/verify/claim_kind_boundary_v1_contract.json`. It binds the
supported and unsupported claim-kind sets to the existing schemas and the committed fixture pair.

## Validation Target

- `make milestone-d-claim-kind-boundary-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs the focused current verifier tests for claim-kind boundaries, schema/example
validation, status guards, roadmap guards, this contract guard, and whitespace diff checks. It
does not add or broaden verification behavior.

## Boundaries Locked By This Slice

- supported v1 claim kinds remain `quote`, `value`, `presence`, and `table_cell`;
- `region` and `other` remain accepted citation input kinds only so they can fail closed with
  explicit diagnostics;
- verification configs cannot enable `region` or `other`;
- unsupported non-v1 checks carry no evidence and do not become semantic checks;
- unsupported non-v1 checks keep `all_evidence_grounded` false even when other checks ground.

## Explicit Blockers For This Slice

This first `claim_kind_boundary` slice does not add:

- new claim-kind support;
- semantic, visual, arithmetic, or cross-region verification;
- a new command or binding surface;
- crop API changes;
- sandbox backend changes;
- foreign-adapter broadening beyond committed fixtures.

Until those blockers are explicitly handled, public language remains limited to source-only
pre-alpha internal continuation, evidence grounding, diagnostics, fixture-backed validation, and
explicit blockers.
