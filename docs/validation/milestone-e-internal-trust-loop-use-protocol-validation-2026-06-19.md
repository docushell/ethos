# Milestone E Internal Trust-Loop Use Protocol Validation - 2026-06-19

## Purpose

Record internal validation for the source-only internal trust-loop use protocol added during
Milestone E prep.

This record covers protocol guard wiring only. It does not promote any fixture, approve public
reports, approve release artifacts, approve package publication, approve production positioning,
approve hosted surfaces, or approve public result wording. It also does not make performance,
quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an internal
continuation decision only.

## Status

Status: **pass for internal Milestone E trust-loop use protocol validation**.

Ethos remains source-only pre-alpha. The protocol defines source-checkout rules for internal
walkthrough use over the current fixture-candidate inventory; it does not move any fixture beyond
internal planning. The record is limited to evidence grounding, diagnostics, fixture validation,
and explicit blockers.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `8946185`
- Fixture-candidate inventory: `docs/milestone-e-fixture-candidates.json`
- Fixture-promotion criteria: `docs/milestone-e-fixture-promotion-criteria.json`
- Internal trust-loop walkthrough plan: `docs/milestone-e-internal-trust-loop-walkthrough.json`
- Internal trust-loop use protocol: `docs/milestone-e-internal-trust-loop-use-protocol.json`
- Use protocol schema:
  `schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json`
- Guard: `.github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py`
- Status: `source-only-pre-alpha-internal-milestone-e-prep`
- Scope: tracked source tree, protocol-to-walkthrough consistency, walkthrough-to-criteria
  consistency, path-backed fixtures, allowlisted validation commands, explicit diagnostic
  boundaries, explicit blockers, schema validation, public posture exclusions, CI/static guard
  wiring, and diff hygiene
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Commands

```sh
python3 -m json.tool docs/milestone-e-internal-trust-loop-use-protocol.json
python3 -m json.tool schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json
<jsonschema-venv>/bin/python schemas/validate_examples.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol_validation_record.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough_validation_record.py
python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <protocol-forbidden-wording-expression> -- README.md docs examples fixtures schemas
git grep <protocol-record-private-path-expression> -- docs/validation/milestone-e-internal-trust-loop-use-protocol-validation-2026-06-19.md
git diff --check
```

The grep command used the forbidden protocol wording covered by
`.github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py`; active non-validation
surfaces returned no matches.

## Result

```text
internal trust-loop use protocol guard green
protocol steps exactly matched the current walkthrough steps
protocol steps exactly matched current fixture-promotion criteria
schema/example validation green
Milestone E prep scope guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
git diff --check green
```

## Validated Protocol Boundary

- The protocol stays source-only, internal, and non-public.
- The protocol scope remains `internal_trust_loop_use_protocol`.
- The protocol boundary remains `internal_source_only_walkthrough_use`.
- The protocol promotion status remains `not_promoted_beyond_internal_fixture_planning`.
- The protocol references `docs/milestone-e-fixture-candidates.json`.
- The protocol references `docs/milestone-e-fixture-promotion-criteria.json`.
- The protocol references `docs/milestone-e-internal-trust-loop-walkthrough.json`.
- The protocol references only current walkthrough step ids and candidate ids.
- Each protocol step exactly matches its walkthrough step for validation command, input fixtures,
  diagnostic boundary, blocker wording, and promotion status.
- Each protocol step exactly matches its criteria entry for validation command, input fixtures,
  diagnostic boundary, blocker wording, and promotion status.
- Required input fixtures are relative, tracked, and path-backed.
- Validation commands are existing allowlisted Make targets.
- Schema validation covers the protocol plan and schema.
- Public boundaries remain explicit and blocked.

## Validated Protocol Steps

- `native-grounding-baseline` uses `native-verification-trust-loop` and `make verify-alpha`.
  Inputs are `examples/verify/cases.json` and
  `examples/verify/goldens/native_grounded_report.json`. Its diagnostic boundary is:
  `Native quote, table-cell, and presence evidence checks over checked-in document JSON.` The
  `public result wording` and `public-report blockers` blockers remain explicit.
- `diagnostic-boundary-check` uses `split-quote-unsupported-claim-diagnostics` and
  `make verify-alpha`.
  Inputs are `examples/verify/native_split_quote_citations.json` and
  `examples/verify/native_non_v1_claims_citations.json`. Its diagnostic boundary is:
  `Adjacent native text evidence matching and explicit unsupported non-v1 claim diagnostics.`
  The `future claim-kind expansion` blocker remains explicit.
- `capability-downgrade-boundary` uses `capability-downgrade-diagnostics` and
  `make milestone-d-capability-downgrade-contract`.
  Inputs are `examples/verify/capability_downgrade_v1_contract.json` and
  `examples/verify/goldens/opendataloader_capability_limited_report.json`. Its diagnostic
  boundary is: `Grounding-source capability limits surface as warnings and capability-blocked
  checks.` The `missing source capabilities` blocker remains explicit.
- `opendataloader-adapter-grounding` uses `opendataloader-style-adapter-grounding` and
  `make milestone-d-opendataloader-adapter-shape-contract`.
  Inputs are `examples/verify/opendataloader_adapter_shape_v1_contract.json` and
  `examples/verify/opendataloader.json`. Its diagnostic boundary is: `OpenDataLoader-style input
  shape maps to parser-neutral grounding metadata with deterministic adapter diagnostics.` The
  `broader foreign-adapter hardening` blocker remains explicit.
- `pinned-opendataloader-fixture-path` uses `pinned-real-opendataloader-fixture-path` and
  `make verify-alpha`.
  Inputs are `fixtures/foreign/opendataloader/real/manifest.json`,
  `fixtures/foreign/opendataloader/real/expected.verification_report.json`, and
  `fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json`. Its
  diagnostic boundary is: `Pinned foreign output exercises grounded and ungrounded verification
  paths without public comparison wording.` The `public comparison reports` and `claim wording`
  blockers remain explicit.
- `crop-descriptor-source-bound-shape` uses `crop-descriptor-source-bound-crop-shape` and
  `make milestone-d-internal-contracts`.
  Inputs are `examples/crop/crop_element_v1_contract.json` and
  `examples/crop/crop_element_surface_shape_v1_contract.json`. Its diagnostic boundary is:
  `Source-bound crop descriptor identity and callable CLI/Python surface shape remain tied to
  current request and descriptor schemas.` The `Node crop surfaces`, `MCP crop surfaces`,
  `hosted crop surfaces`, `sandbox-backed crop surfaces`, and `foreign-adapter crop surfaces`
  blockers remain explicit.
- `rag-chunk-artifact-loop` uses `rag-chunk-artifact-loop` and `make rag-chunk-alpha`.
  Input is `schemas/examples/chunks.example.jsonl`. Its diagnostic boundary is:
  `RAG chunk output stays fixture-backed with stale-reference and warning-reference validation.`
  The `broader provenance integration`, `broader citation integration`, `parser integration`, and
  `table integration` blockers remain explicit.
- `security-report-artifact-loop` uses `security-report-artifact-loop` and
  `make security-report-alpha`.
  Input is `schemas/examples/security-report.example.json`. Its diagnostic boundary is:
  `Security-report output stays source-grounded with locator, warning-lane, and summary
  diagnostics.` The `broader security-report generation semantics` and `artifact UX` blockers
  remain explicit.
- `demo-narrative-index` uses `demo-narrative-index` and `make verify-alpha`.
  Input is `docs/demos/verify-alpha.md`. Its diagnostic boundary is: `Existing narrative index
  remains tied to checked-in alpha verification fixtures and posture guards.` The
  `broad demo-generation` and `public result wording` blockers remain explicit.

## Remaining Boundaries

- Public reports remain blocked.
- Public result wording remains blocked.
- Hosted surfaces remain blocked.
- Release artifacts remain blocked.
- Package publication remains blocked.
- Production positioning remains blocked.
- Broad demo-generation workflows remain blocked.
- Performance claims remain blocked.
- Quality claims remain blocked.
- Footprint claims remain blocked.
- Table-quality claims remain blocked.
- Parser-quality claims remain blocked.

## Follow-up

Future protocol changes require this guard to stay green and require either a new validation record
or an explicit superseding record. Internal walkthrough use remains limited to source-checkout
validation over the existing fixture candidates until blockers are explicitly resolved in a later
source-only slice.
