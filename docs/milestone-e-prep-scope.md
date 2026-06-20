# Milestone E Prep Scope

Status: source-only pre-alpha prep for internal Milestone E continuation.

This note defines the first narrow Milestone E prep slice. It does not approve public benchmark
reports, release artifacts, package publication, production positioning, public result wording, or
performance, quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an
internal continuation decision only.

## Purpose

Milestone D closed the current source-only contract boundary. Milestone E prep starts by preserving
that boundary while selecting already-validated trust-loop artifacts that can support internal demo
fixture planning.

The prep slice is allowed to:

- document the source-only pre-alpha E prep boundary;
- identify existing D and C trust-loop artifacts that are candidates for internal E demo fixtures;
- keep claim language tied to evidence grounding, diagnostics, fixture/evaluator validation, and
  explicit blockers;
- add static guards that prevent this prep note from becoming public launch or result wording.

The prep slice is not allowed to:

- create public report wording or public result summaries;
- add hosted surfaces, package/distribution work, or release artifacts;
- expand Node, MCP, sandbox-backed, or foreign-adapter crop surfaces;
- claim speed, footprint, quality, table-quality, parser-quality, or production readiness;
- treat the E prep fixture list as a finished demo plan.

## Internal Demo Fixture Candidates

The current E prep candidate set is restricted to tracked source-tree artifacts already covered by
existing guards. The machine-readable inventory is
`docs/milestone-e-fixture-candidates.json` and is schema-bound by
`schemas/ethos-milestone-e-fixture-candidates.schema.json`. Internal fixture-promotion criteria
live in `docs/milestone-e-fixture-promotion-criteria.json` and are schema-bound by
`schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json`; they define what must be
rechecked before a candidate can enter an internal demo plan, not public demo approval. Each
candidate row must keep a structured `blockers_must_remain_explicit` list that matches the
promotion criteria row before any internal fixture-planning use.
The internal trust-loop walkthrough plan lives in
`docs/milestone-e-internal-trust-loop-walkthrough.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json`. It sequences the current
fixture-candidate inventory for internal source-only planning, not public result wording.
The internal trust-loop use protocol lives in
`docs/milestone-e-internal-trust-loop-use-protocol.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json`. It defines only the
required source-checkout validation and blocker-preservation rules for internal walkthrough use,
not public result wording.
The internal trust-loop rehearsal/evidence matrix lives in
`docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json`. It maps
the existing use-protocol steps to evidence grounding, diagnostics, fixture/evaluator validation,
and explicit blockers for internal source-only rehearsal planning, not public result wording.
The internal trust-loop blocker ledger lives in
`docs/milestone-e-internal-trust-loop-blocker-ledger.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json`. It derives explicit
blockers from the rehearsal/evidence matrix and keeps them visible for internal source-only
planning; it does not resolve or soften blockers and is not public result wording.

| Candidate | Existing artifact | Current guard |
| --- | --- | --- |
| Native verification trust loop | `examples/verify/cases.json` and `examples/verify/goldens/native_grounded_report.json` | `make verify-alpha` |
| Split-quote and unsupported-claim diagnostics | `examples/verify/native_split_quote_citations.json` and `examples/verify/native_non_v1_claims_citations.json` | `make verify-alpha` |
| Capability downgrade diagnostics | `examples/verify/capability_downgrade_v1_contract.json` and `examples/verify/goldens/opendataloader_capability_limited_report.json` | `make milestone-d-capability-downgrade-contract` |
| OpenDataLoader-style adapter grounding | `examples/verify/opendataloader_adapter_shape_v1_contract.json` and `examples/verify/opendataloader.json` | `make milestone-d-opendataloader-adapter-shape-contract` |
| Pinned real OpenDataLoader fixture path | `fixtures/foreign/opendataloader/real/manifest.json`, `fixtures/foreign/opendataloader/real/expected.verification_report.json`, and `fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json` | `make verify-alpha` |
| Crop descriptor and source-bound crop shape | `examples/crop/crop_element_v1_contract.json` and `examples/crop/crop_element_surface_shape_v1_contract.json` | `make milestone-d-internal-contracts` |
| RAG chunk artifact loop | `schemas/examples/chunks.example.jsonl` | `make rag-chunk-alpha` |
| Security-report artifact loop | `schemas/examples/security-report.example.json` | `make security-report-alpha` |
| Demo narrative index | `docs/demos/verify-alpha.md` | `make verify-alpha` |

These are internal fixture candidates, not public proof points. Any future demo plan must still
state the validated command, input fixture, expected diagnostic boundary, blocker status, and every
structured blocker before the fixture can be promoted beyond source-only pre-alpha planning.

## Prep Guard

Focused validation command:

- `make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python`

The target runs status/roadmap posture checks, public-surface posture checks, the claims gate,
schema/example validation, schema-registry alignment for the E prep JSON artifacts,
public-boundary alignment, this prep-scope guard, fixture-candidate blocker-alignment validation,
the internal trust-loop walkthrough, use-protocol, rehearsal/evidence matrix, and blocker-ledger
guards, validation-command index checks, validation-record index checks, the prep guard-sequence
index, validation-record guards, and diff hygiene. It intentionally does not run public-report,
release, package, hosted, benchmark-report, or broad demo-generation workflows.

## Exit Criteria For This Prep Slice

- `docs/roadmap.md` and `docs/execution-status.md` point to this prep boundary.
- The source-tree guard keeps the fixture-candidate list explicit and path-backed.
- The source-tree guard keeps internal fixture-promotion criteria aligned with the candidate
  inventory.
- The schema validation gate keeps the fixture-candidate inventory and fixture-promotion criteria
  closed to unreviewed fields.
- The schema-registry alignment guard keeps the six E prep JSON artifacts and their six schemas in
  one-to-one sync across schema validation and source-tree status docs.
- Fixture-candidate blocker lists remain structured, nonempty, and visible before any internal
  fixture-planning use.
- The internal trust-loop walkthrough plan remains limited to existing candidates and criteria.
- The internal trust-loop use protocol remains limited to existing walkthrough steps and explicit
  blockers.
- The internal trust-loop rehearsal/evidence matrix remains limited to existing protocol steps,
  evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
- The internal trust-loop blocker ledger remains limited to existing matrix rows and does not
  resolve or soften blockers.
- Public language remains source-only pre-alpha and internal-continuation scoped.
- External blockers remain visible before any public-facing Milestone E work starts.
