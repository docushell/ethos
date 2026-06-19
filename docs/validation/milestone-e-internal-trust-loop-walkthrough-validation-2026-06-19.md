# Milestone E Internal Trust-Loop Walkthrough Validation - 2026-06-19

## Purpose

Record internal validation for the source-only internal trust-loop walkthrough plan added during
Milestone E prep.

This record covers walkthrough-plan guard wiring only. It does not promote any fixture, approve
public reports, approve release artifacts, approve package publication, approve production
positioning, approve hosted surfaces, or approve public result wording. It also does not make
performance, quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an
internal continuation decision only.

## Status

Status: **pass for internal Milestone E trust-loop walkthrough validation**.

Ethos remains source-only pre-alpha. The walkthrough plan sequences two existing trust-loop
fixture candidates for internal Milestone E prep continuation and internal source-only planning
only; it does not move any fixture beyond internal planning. The record is limited to evidence
grounding, diagnostics, fixture validation, and explicit blockers.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `5be2a2c`
- Fixture-candidate inventory: `docs/milestone-e-fixture-candidates.json`
- Fixture-promotion criteria: `docs/milestone-e-fixture-promotion-criteria.json`
- Internal trust-loop walkthrough plan: `docs/milestone-e-internal-trust-loop-walkthrough.json`
- Walkthrough schema:
  `schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json`
- Guard: `.github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py`
- Status: `source-only-pre-alpha-internal-milestone-e-prep`
- Scope: tracked source tree, walkthrough-to-criteria consistency, path-backed fixtures,
  allowlisted validation commands, explicit diagnostic boundaries, explicit blockers, schema
  validation, public posture exclusions, CI/static guard wiring, and diff hygiene
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Commands

```sh
python3 -m json.tool docs/milestone-e-internal-trust-loop-walkthrough.json
python3 -m json.tool docs/milestone-e-fixture-candidates.json
python3 -m json.tool docs/milestone-e-fixture-promotion-criteria.json
python3 -m json.tool schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json
<jsonschema-venv>/bin/python schemas/validate_examples.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py
python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py
python3 .github/scripts/test_milestone_e_fixture_promotion_criteria_validation_record.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make verify-alpha PYTHON=<jsonschema-venv>/bin/python
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <walkthrough-forbidden-wording-expression> -- README.md docs examples fixtures schemas
git grep <walkthrough-record-private-path-expression> -- docs/validation/milestone-e-internal-trust-loop-walkthrough-validation-2026-06-19.md
git diff --check
```

The grep command used the forbidden walkthrough wording covered by
`.github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py`; active non-validation
surfaces returned no matches.

## Result

```text
internal trust-loop walkthrough guard green
fixture-promotion criteria guard green
Milestone E prep scope guard green
CI workflow static guard green
public-surface posture and claims gates green
walkthrough JSON parses cleanly
walkthrough schema parses cleanly
schema/example validation green
verify-alpha target green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
git diff --check green
```

## Validated Walkthrough Boundary

- The walkthrough stays source-only, internal, and non-public.
- The walkthrough scope remains `internal_trust_loop_walkthrough_plan`.
- The walkthrough boundary remains `internal_source_only_walkthrough_planning`.
- The walkthrough promotion status remains `not_promoted_beyond_internal_fixture_planning`.
- The walkthrough references `docs/milestone-e-fixture-candidates.json`.
- The walkthrough references `docs/milestone-e-fixture-promotion-criteria.json`.
- The walkthrough references only existing candidate ids.
- Each walkthrough step exactly matches its criteria entry for validation command, input fixtures,
  diagnostic boundary, blocker wording, and promotion status.
- Required input fixtures are relative, tracked, and path-backed.
- Validation commands are existing allowlisted Make targets.
- Schema validation covers the walkthrough plan and schema.
- Public boundaries remain explicit and blocked.

## Validated Walkthrough Steps

- `native-grounding-baseline` uses `native-verification-trust-loop` and `make verify-alpha`.
  Inputs are `examples/verify/cases.json` and
  `examples/verify/goldens/native_grounded_report.json`. Its diagnostic boundary is:
  `Native quote, table-cell, and presence evidence checks over checked-in document JSON.` Public
  result wording and public-report blockers remain explicit.
- `diagnostic-boundary-check` uses `split-quote-unsupported-claim-diagnostics` and
  `make verify-alpha`.
  Inputs are `examples/verify/native_split_quote_citations.json` and
  `examples/verify/native_non_v1_claims_citations.json`. Its diagnostic boundary is:
  `Adjacent native text evidence matching and explicit unsupported non-v1 claim diagnostics.`
  The `future claim-kind expansion` blocker remains explicit.

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

Future walkthrough changes require this guard to stay green and require either a new validation
record or an explicit superseding record. Broader internal walkthrough sequencing remains blocked
until a later source-only slice defines it without creating public claims or public-facing result
wording.
