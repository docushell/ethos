# Milestone E Validation-Record Source-Head Alignment Validation - 2026-06-20

## Purpose

Record internal validation that current Milestone E validation records keep a source-bound
`Validated source HEAD before this record` line.

This record covers only validation-record source-head alignment for current Milestone E prep. It
does not change any fixture JSON artifact, does not change any schema, does not resolve or soften
blockers, does not promote any fixture, approve public reports, approve release artifacts, approve
package publication, approve production positioning, approve hosted surfaces, or approve public
result wording. It also does not make performance, quality, footprint, table-quality, or
parser-quality claims. ADR-0005 remains an internal continuation decision only.

## Status

Status: **pass for internal Milestone E validation-record source-head alignment validation**.

Ethos remains source-only pre-alpha. Milestone E prep remains an internal continuation checkpoint
over tracked trust-loop fixture candidates, guarded source-tree validation records, and explicit
blockers. Internal fixture candidates remain non-public planning inputs.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `67f1af2`
- Prep scope: `docs/milestone-e-prep-scope.md`
- Validation records: `docs/validation/milestone-e-*-validation-*.md`
- Scope: source-only validation-record provenance alignment across Milestone E validation records,
  CI/static guard wiring, validation-record indexing, guard-sequence indexing, and diff hygiene
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Current Source-Head Rule

Each current Milestone E validation record must include exactly one
`Validated source HEAD before this record` line. For committed records, that source HEAD must
resolve to the parent commit of the commit that first introduced the validation record. For an
in-progress record that has not yet been committed, that source HEAD must resolve to the current
source checkout HEAD.

## Commands

```sh
python3 .github/scripts/test_milestone_e_validation_source_head_alignment.py
python3 .github/scripts/test_milestone_e_validation_source_head_alignment_validation_record.py
python3 .github/scripts/test_milestone_e_validation_record_index.py
python3 .github/scripts/test_milestone_e_prep_guard_sequence_index.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <validation-source-head-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <validation-source-head-private-path-expression> -- docs/validation/milestone-e-validation-source-head-alignment-validation-2026-06-20.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_validation_source_head_alignment_validation_record.py`; active
non-validation surfaces returned no matches.

## Result

```text
Milestone E validation-record source-head alignment guard green
Milestone E validation-record source-head alignment validation-record guard green
Milestone E validation-record index guard green
Milestone E prep guard-sequence index guard green
CI workflow guard green
Milestone E prep scope guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
record private-path grep returned no matches
git diff --check green
```

## Validated Current Prep Guard State

- Every current Milestone E validation record has exactly one source-head line.
- Every source-head value resolves to a commit in the current git history.
- Committed validation records name the parent of the commit that introduced the record.
- In-progress validation records name the current source checkout HEAD until committed.
- The source-head guard runs after validation-record indexing and before guard-sequence indexing.
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

Future Milestone E validation records must keep the source-head line aligned with the source commit
that was validated before the record was added.
