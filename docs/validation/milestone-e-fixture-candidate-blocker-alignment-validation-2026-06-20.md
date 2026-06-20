# Milestone E Fixture-Candidate Blocker Alignment Validation - 2026-06-20

## Purpose

Record internal validation for aligning the source-only fixture-candidate inventory with the
structured blocker lists used by downstream Milestone E prep artifacts.

This record covers only the blocker-alignment boundary between
`docs/milestone-e-fixture-candidates.json` and
`docs/milestone-e-fixture-promotion-criteria.json`. It does not change fixture inventory
membership, does not resolve or soften blockers, does not promote any fixture, approve public
reports, approve release artifacts, approve package publication, approve production positioning,
approve hosted surfaces, or approve public result wording. It also does not make performance,
quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an internal
continuation decision only.

## Status

Status: **pass for internal Milestone E fixture-candidate blocker alignment validation**.

Ethos remains source-only pre-alpha. The inventory now carries
`blockers_must_remain_explicit` for each current fixture candidate, and those lists exactly match
the fixture-promotion criteria rows. The change is a source-only blocker-alignment boundary and
keeps promotion status at `not_promoted_beyond_internal_fixture_planning`.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `4c8f17f`
- Fixture-candidate inventory: `docs/milestone-e-fixture-candidates.json`
- Fixture-candidate schema: `schemas/ethos-milestone-e-fixture-candidates.schema.json`
- Fixture-promotion criteria: `docs/milestone-e-fixture-promotion-criteria.json`
- Guard: `.github/scripts/test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py`
- Promotion status: `not_promoted_beyond_internal_fixture_planning`
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Commands

```sh
python3 -m json.tool docs/milestone-e-fixture-candidates.json
python3 -m json.tool schemas/ethos-milestone-e-fixture-candidates.schema.json
<jsonschema-venv>/bin/python schemas/validate_examples.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py
python3 .github/scripts/test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <fixture-candidate-blocker-alignment-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <fixture-candidate-blocker-alignment-record-private-path-expression> -- docs/validation/milestone-e-fixture-candidate-blocker-alignment-validation-2026-06-20.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py`;
active non-validation surfaces returned no matches.

## Result

```text
fixture-candidate blocker alignment guard green
fixture-candidate JSON parses cleanly
fixture-candidate schema parses cleanly
schema/example validation green
fixture-promotion criteria guard green
Milestone E prep scope guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
git diff --check green
```

## Validated Blocker Alignment

- Every fixture candidate has a structured `blockers_must_remain_explicit` list.
- Every fixture-candidate blocker list exactly matches the corresponding criteria row.
- The fixture-candidate schema requires structured blocker lists.
- Fixture inventory membership is unchanged.
- Blockers remain explicit and unresolved.
- The alignment remains source-only, internal, and non-public.
- Public boundaries remain explicit and blocked.

## Candidate Blockers

- `native-verification-trust-loop`: `public result wording`, `public-report blockers`
- `split-quote-unsupported-claim-diagnostics`: `future claim-kind expansion`
- `capability-downgrade-diagnostics`: `missing source capabilities`
- `opendataloader-style-adapter-grounding`: `broader foreign-adapter hardening`
- `pinned-real-opendataloader-fixture-path`: `public comparison reports`, `claim wording`
- `crop-descriptor-source-bound-crop-shape`: `Node crop surfaces`, `MCP crop surfaces`,
  `hosted crop surfaces`, `sandbox-backed crop surfaces`, `foreign-adapter crop surfaces`
- `rag-chunk-artifact-loop`: `broader provenance integration`, `broader citation integration`,
  `parser integration`, `table integration`
- `security-report-artifact-loop`: `broader security-report generation semantics`, `artifact UX`
- `demo-narrative-index`: `broad demo-generation`, `public result wording`

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

Future fixture-candidate changes must keep structured blockers aligned with the criteria boundary.
This record does not change public-facing blockers, fixture promotion status, or the source-only
pre-alpha posture.
