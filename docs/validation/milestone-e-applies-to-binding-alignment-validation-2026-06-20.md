# Milestone E Applies-To Binding Alignment Validation - 2026-06-20

## Purpose

Record internal validation that the current Milestone E prep artifacts and schemas keep the same
`applies_to_*` source-artifact binding chain.

This record covers only source-tree applies-to binding alignment for current Milestone E prep. It
does not change any fixture JSON artifact, does not change any schema, does not resolve or soften
blockers, does not promote any fixture, approve public reports, approve release artifacts, approve
package publication, approve production positioning, approve hosted surfaces, or approve public
result wording. It also does not make performance, quality, footprint, table-quality, or
parser-quality claims. ADR-0005 remains an internal continuation decision only.

## Status

Status: **pass for internal Milestone E applies-to binding alignment validation**.

Ethos remains source-only pre-alpha. Milestone E prep remains an internal continuation checkpoint
over tracked trust-loop fixture candidates, guarded source-tree validation records, and explicit
blockers. Internal fixture candidates remain non-public planning inputs.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `cf78e15`
- Prep scope: `docs/milestone-e-prep-scope.md`
- Fixture candidates: `docs/milestone-e-fixture-candidates.json`
- Fixture-promotion criteria: `docs/milestone-e-fixture-promotion-criteria.json`
- Internal trust-loop walkthrough: `docs/milestone-e-internal-trust-loop-walkthrough.json`
- Internal trust-loop use protocol: `docs/milestone-e-internal-trust-loop-use-protocol.json`
- Rehearsal/evidence matrix: `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`
- Blocker ledger: `docs/milestone-e-internal-trust-loop-blocker-ledger.json`
- Scope: source-only applies-to binding alignment across current Milestone E trust-loop planning
  artifacts, matching schema consts, CI/static guard wiring, validation-record indexing, and diff
  hygiene
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Current Applies-To Binding Set

- `applies_to_inventory` -> `docs/milestone-e-fixture-candidates.json`
- `applies_to_criteria` -> `docs/milestone-e-fixture-promotion-criteria.json`
- `applies_to_walkthrough` -> `docs/milestone-e-internal-trust-loop-walkthrough.json`
- `applies_to_protocol` -> `docs/milestone-e-internal-trust-loop-use-protocol.json`
- `applies_to_matrix` -> `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`

## Commands

```sh
python3 .github/scripts/test_milestone_e_applies_to_binding_alignment.py
python3 .github/scripts/test_milestone_e_applies_to_binding_alignment_validation_record.py
python3 .github/scripts/test_milestone_e_source_status_alignment.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_milestone_e_validation_record_index.py
python3 .github/scripts/test_milestone_e_prep_guard_sequence_index.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <applies-to-binding-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <applies-to-binding-private-path-expression> -- docs/validation/milestone-e-applies-to-binding-alignment-validation-2026-06-20.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_applies_to_binding_alignment_validation_record.py`; active
non-validation surfaces returned no matches.

## Result

```text
Milestone E applies-to binding alignment guard green
Milestone E applies-to binding alignment validation-record guard green
Milestone E source-status alignment guard green
Milestone E prep scope guard green
Milestone E validation-record index guard green
Milestone E prep guard-sequence index guard green
CI workflow guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
record private-path grep returned no matches
git diff --check green
```

## Validated Current Prep Guard State

- Fixture-promotion criteria remain bound to the fixture-candidate inventory.
- The internal trust-loop walkthrough remains bound to the fixture-candidate inventory and
  fixture-promotion criteria.
- The internal trust-loop use protocol remains bound to the fixture-candidate inventory,
  fixture-promotion criteria, and walkthrough.
- The rehearsal/evidence matrix remains bound to the fixture-candidate inventory,
  fixture-promotion criteria, walkthrough, and use protocol.
- The blocker ledger remains bound to the fixture-candidate inventory, fixture-promotion criteria,
  walkthrough, use protocol, and rehearsal/evidence matrix.
- Matching schemas keep the same required `applies_to_*` consts as the current artifacts.
- The applies-to binding chain only references current Milestone E source artifacts.
- The record does not change fixture JSON artifacts.
- The record does not change schemas.
- The record does not promote any fixture.
- The record does not resolve or soften blockers.

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

Future Milestone E prep changes that add, remove, or rename `applies_to_*` bindings must update
the artifacts, schemas, guard sequence, and validation records together before
`make milestone-e-prep` can stay green.
