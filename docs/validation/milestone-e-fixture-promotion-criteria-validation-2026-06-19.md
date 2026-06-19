# Milestone E Fixture Promotion Criteria Validation - 2026-06-19

## Purpose

Record internal validation for the source-only fixture-promotion criteria added during Milestone E
prep.

This record covers criteria guard wiring only. It does not promote any fixture, approve public
reports, approve release artifacts, approve package publication, approve production positioning,
approve hosted surfaces, or approve public result wording. It also does not make performance,
quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an internal
continuation decision only.

## Status

Status: **pass for internal Milestone E fixture-promotion criteria validation**.

Ethos remains source-only pre-alpha. The criteria define conditions for internal demo-plan
candidate review only; they do not move any fixture beyond internal planning.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `24e1bbd`
- Fixture-candidate inventory: `docs/milestone-e-fixture-candidates.json`
- Fixture-promotion criteria: `docs/milestone-e-fixture-promotion-criteria.json`
- Guard: `.github/scripts/test_milestone_e_fixture_promotion_criteria.py`
- Scope: tracked source tree, criteria-to-candidate consistency, path-backed fixtures,
  allowlisted validation commands, explicit diagnostic boundaries, explicit blockers, public
  posture exclusions, CI/static guard wiring, and diff hygiene
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Commands

```sh
python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_milestone_e_prep_validation_record.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
python3 -m json.tool docs/milestone-e-fixture-candidates.json
python3 -m json.tool docs/milestone-e-fixture-promotion-criteria.json
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <fixture-promotion-forbidden-wording-expression> -- README.md docs examples fixtures schemas
git grep <criteria-record-private-path-expression> -- docs/validation/milestone-e-fixture-promotion-criteria-validation-2026-06-19.md
git diff --check
```

The grep command used the forbidden promotion wording covered by
`.github/scripts/test_milestone_e_fixture_promotion_criteria.py`; active non-validation surfaces
returned no matches.

## Result

```text
Fixture-promotion criteria guard green
Milestone E prep scope guard green
Milestone E prep validation-record guard green
CI workflow static guard green
public-surface posture and claims gates green
fixture-candidate JSON parses cleanly
fixture-promotion criteria JSON parses cleanly
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
git diff --check green
```

## Validated Criteria Boundary

- Criteria entries exactly match `docs/milestone-e-fixture-candidates.json` candidate ids.
- Every criteria entry keeps `promotion_status` at
  `not_promoted_beyond_internal_fixture_planning`.
- Every criteria entry requires the same validation command, input fixtures, and diagnostic
  boundary as its source candidate.
- Required input fixtures are relative, tracked, and path-backed.
- Validation commands are existing allowlisted Make targets.
- Blocker status remains explicit for every candidate.
- Criteria wording stays source-only, internal, and non-public.
- Criteria status remains `source-only-pre-alpha-internal-milestone-e-prep`.
- Criteria scope remains `internal_fixture_promotion_criteria`.
- Criteria promotion boundary remains `internal_demo_plan_candidate_review_only`.
- Future criteria changes require a validation record or explicit superseding record.

## Validated Criteria Cases

- `native-verification-trust-loop` uses `make verify-alpha`.
- `split-quote-unsupported-claim-diagnostics` uses `make verify-alpha`.
- `capability-downgrade-diagnostics` uses `make milestone-d-capability-downgrade-contract`.
- `opendataloader-style-adapter-grounding` uses
  `make milestone-d-opendataloader-adapter-shape-contract`.
- `pinned-real-opendataloader-fixture-path` uses `make verify-alpha`.
- `crop-descriptor-source-bound-crop-shape` uses `make milestone-d-internal-contracts`.
- `rag-chunk-artifact-loop` uses `make rag-chunk-alpha`.
- `security-report-artifact-loop` uses `make security-report-alpha`.
- `demo-narrative-index` uses `make verify-alpha`.

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

Future criteria changes require this guard to stay green and require either a new validation record
or an explicit superseding record. Internal demo-plan work remains blocked until a later source-only
slice defines it without creating public claims or public-facing result wording.
