# Milestone E Validation-Command Index Validation - 2026-06-20

## Purpose

Record internal validation that current Milestone E fixture candidates, trust-loop artifacts,
prep-scope rows, schemas, and row validation records agree on the same source-checkout validation
commands.

This record covers only validation-command alignment for current Milestone E prep. It does not
change any fixture JSON artifact, does not change any schema, does not resolve or soften blockers,
does not promote any fixture, approve public reports, approve release artifacts, approve package
publication, approve production positioning, approve hosted surfaces, or approve public result
wording. It also does not make performance, quality, footprint, table-quality, or parser-quality
claims. ADR-0005 remains an internal continuation decision only.

## Status

Status: **pass for internal Milestone E validation-command index validation**.

Ethos remains source-only pre-alpha. The current Milestone E command index stays limited to plain
source-checkout make targets that already exist in the source tree. Promotion status remains
`not_promoted_beyond_internal_fixture_planning`.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `ddd9673`
- Guard: `.github/scripts/test_milestone_e_validation_command_index.py`
- Validation-record guard:
  `.github/scripts/test_milestone_e_validation_command_index_validation_record.py`
- Promotion status: `not_promoted_beyond_internal_fixture_planning`
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, public report publication,
  and any performance, quality, footprint, table-quality, or parser-quality claims

## Commands

```sh
python3 .github/scripts/test_milestone_e_validation_command_index.py
python3 .github/scripts/test_milestone_e_validation_command_index_validation_record.py
python3 .github/scripts/test_milestone_e_rehearsal_row_record_coverage_validation.py
python3 .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <validation-command-index-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <validation-command-index-private-path-expression> -- docs/validation/milestone-e-validation-command-index-validation-2026-06-20.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_validation_command_index_validation_record.py`; active
non-validation surfaces returned no matches.

## Result

```text
Milestone E validation-command index guard green
Milestone E validation-command index validation-record guard green
Milestone E row-record coverage guard green
Milestone E public-boundary validation-record guard green
Milestone E prep scope guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
record private-path grep returned no matches
git diff --check green
```

## Validated Command Set

- `make verify-alpha`
- `make milestone-d-capability-downgrade-contract`
- `make milestone-d-opendataloader-adapter-shape-contract`
- `make milestone-d-internal-contracts`
- `make rag-chunk-alpha`
- `make security-report-alpha`

## Validated Alignment Boundary

- The six current Milestone E schemas carry the same validation-command enum.
- Fixture-candidate `validated_command` values match fixture-promotion criteria commands.
- Walkthrough, protocol, rehearsal/evidence matrix, and blocker-ledger row commands match.
- Prep-scope table rows carry the same plain source-checkout make targets.
- Row validation records name the same command as their matrix and ledger row.
- The command strings do not add shell operators, absolute local paths, private paths, or external
  workflow commands.
- The prep target and CI run the validation-command index guards.
- The command index remains source-only, internal, and non-public.

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

Future Milestone E fixture, walkthrough, matrix, ledger, prep-scope, schema, or row-record changes
must keep their validation commands aligned before any internal fixture-planning use. This record
does not change public-facing blockers, fixture promotion status, or the source-only pre-alpha
posture.
