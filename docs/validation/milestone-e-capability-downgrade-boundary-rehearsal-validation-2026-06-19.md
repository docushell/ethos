# Milestone E Capability Downgrade Boundary Rehearsal Validation - 2026-06-19

## Purpose

Record internal validation for the third source-only Milestone E trust-loop rehearsal row:
`capability-downgrade-boundary`.

This record covers only the existing third row from the internal rehearsal/evidence matrix. It does
not execute the full walkthrough, resolve or soften blockers, promote any fixture, approve public
reports, approve release artifacts, approve package publication, approve production positioning,
approve hosted surfaces, or approve public result wording. It also does not make performance,
quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an internal
continuation decision only.

## Status

Status: **pass for internal Milestone E capability-downgrade-boundary rehearsal validation**.

Ethos remains source-only pre-alpha. The row validation used the existing
`make milestone-d-capability-downgrade-contract` source-checkout command and stayed limited to
evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers. The internal
rehearsal/evidence matrix and blocker ledger remain source-only planning artifacts; this record does
not change their promotion or blocker status.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `6e586f7`
- Rehearsed step: `capability-downgrade-boundary`
- Candidate: `capability-downgrade-diagnostics`
- Validation command: `make milestone-d-capability-downgrade-contract`
- Required input fixtures:
  - `examples/verify/capability_downgrade_v1_contract.json`
  - `examples/verify/goldens/opendataloader_capability_limited_report.json`
- Diagnostic boundary:
  `Grounding-source capability limits surface as warnings and capability-blocked checks.`
- Evidence lanes: evidence grounding, diagnostics, fixture/evaluator validation, explicit blockers
- Explicit blockers: `missing source capabilities`
- Promotion status: `not_promoted_beyond_internal_fixture_planning`
- Matrix source: `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`
- Blocker ledger source: `docs/milestone-e-internal-trust-loop-blocker-ledger.json`
- Guard:
  `.github/scripts/test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py`
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Commands

```sh
make milestone-d-capability-downgrade-contract PYTHON=<jsonschema-venv>/bin/python
python3 .github/scripts/test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <capability-downgrade-boundary-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <capability-downgrade-boundary-record-private-path-expression> -- docs/validation/milestone-e-capability-downgrade-boundary-rehearsal-validation-2026-06-19.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py`;
active non-validation surfaces returned no matches.

## Result

```text
milestone-d-capability-downgrade-contract green
capability-downgrade-boundary row remained aligned with the rehearsal/evidence matrix
capability-downgrade-boundary row remained aligned with the blocker ledger
Milestone E prep scope guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
git diff --check green
```

## Validated Rehearsal Boundary

- Only `capability-downgrade-boundary` is covered by this record.
- The candidate remains `capability-downgrade-diagnostics`.
- The validation command remains `make milestone-d-capability-downgrade-contract`.
- Required input fixtures remain `examples/verify/capability_downgrade_v1_contract.json` and
  `examples/verify/goldens/opendataloader_capability_limited_report.json`.
- The diagnostic boundary remains
  `Grounding-source capability limits surface as warnings and capability-blocked checks.`
- Evidence lanes remain evidence grounding, diagnostics, fixture/evaluator validation, and
  explicit blockers.
- Explicit blockers remain `missing source capabilities`.
- Promotion status remains `not_promoted_beyond_internal_fixture_planning`.
- The row remains source-only, internal, and non-public.
- The record does not execute the full walkthrough.
- The record does not resolve or soften blockers.
- Public boundaries remain explicit and blocked.

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

Future row-rehearsal records must stay one-row scoped unless a later source-only decision expands
the internal rehearsal boundary. This record does not change public-facing blockers, fixture
promotion status, or the source-only pre-alpha posture.
