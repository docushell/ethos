# Milestone E Crop Descriptor Source-Bound Shape Rehearsal Validation - 2026-06-20

## Purpose

Record internal validation for the sixth source-only Milestone E trust-loop rehearsal row:
`crop-descriptor-source-bound-shape`.

This record covers only the existing sixth row from the internal rehearsal/evidence matrix. It does
not execute the full walkthrough, resolve or soften blockers, promote any fixture, approve public
reports, approve release artifacts, approve package publication, approve production positioning,
approve hosted surfaces, or approve public result wording. It also does not make performance,
quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an internal
continuation decision only.

## Status

Status: **pass for internal Milestone E crop-descriptor-source-bound-shape rehearsal validation**.

Ethos remains source-only pre-alpha. The row validation used the existing
`make milestone-d-internal-contracts` source-checkout command and stayed limited to evidence
grounding, diagnostics, fixture/evaluator validation, and explicit blockers. The internal
rehearsal/evidence matrix and blocker ledger remain source-only planning artifacts; this record does
not change their promotion or blocker status.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `25e10cc`
- Rehearsed step: `crop-descriptor-source-bound-shape`
- Candidate: `crop-descriptor-source-bound-crop-shape`
- Validation command: `make milestone-d-internal-contracts`
- Required input fixtures:
  - `examples/crop/crop_element_v1_contract.json`
  - `examples/crop/crop_element_surface_shape_v1_contract.json`
- Diagnostic boundary:
  `Source-bound crop descriptor identity and callable CLI/Python surface shape remain tied to current request and descriptor schemas.`
- Evidence lanes: evidence grounding, diagnostics, fixture/evaluator validation, explicit blockers
- Explicit blockers: `Node crop surfaces`, `MCP crop surfaces`, `hosted crop surfaces`,
  `sandbox-backed crop surfaces`, `foreign-adapter crop surfaces`
- Promotion status: `not_promoted_beyond_internal_fixture_planning`
- Matrix source: `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`
- Blocker ledger source: `docs/milestone-e-internal-trust-loop-blocker-ledger.json`
- Guard:
  `.github/scripts/test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py`
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Commands

```sh
make milestone-d-internal-contracts PYTHON=<jsonschema-venv>/bin/python
python3 .github/scripts/test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <crop-descriptor-source-bound-shape-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <crop-descriptor-source-bound-shape-record-private-path-expression> -- docs/validation/milestone-e-crop-descriptor-source-bound-shape-rehearsal-validation-2026-06-20.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py`;
active non-validation surfaces returned no matches.

## Result

```text
milestone-d-internal-contracts green
crop-descriptor-source-bound-shape row remained aligned with the rehearsal/evidence matrix
crop-descriptor-source-bound-shape row remained aligned with the blocker ledger
Milestone E prep scope guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
git diff --check green
```

## Validated Rehearsal Boundary

- Only `crop-descriptor-source-bound-shape` is covered by this record.
- The candidate remains `crop-descriptor-source-bound-crop-shape`.
- The validation command remains `make milestone-d-internal-contracts`.
- Required input fixtures remain `examples/crop/crop_element_v1_contract.json` and
  `examples/crop/crop_element_surface_shape_v1_contract.json`.
- The diagnostic boundary remains
  `Source-bound crop descriptor identity and callable CLI/Python surface shape remain tied to current request and descriptor schemas.`
- Evidence lanes remain evidence grounding, diagnostics, fixture/evaluator validation, and
  explicit blockers.
- Explicit blockers remain `Node crop surfaces`, `MCP crop surfaces`, `hosted crop surfaces`,
  `sandbox-backed crop surfaces`, and `foreign-adapter crop surfaces`.
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
