# Milestone E Public Beta Approval Prep Validation - 2026-06-20

## Purpose

Record internal validation that the public beta approval prep lane has started without approving
public beta.

This record covers only the source-tree approval prep artifact at
`docs/milestone-e-public-beta-approval-prep.json`. It does not approve public beta, does not
approve package publication, does not approve hosted surfaces, does not approve production
positioning, does not approve public benchmark reports, does not approve public benchmark claims,
and does not approve wording beyond the exact approved pre-alpha sentence. It does not change the
approved source snapshot, does not create release artifacts, does not resolve or soften blockers,
and does not make performance, quality, footprint, table-quality, or parser-quality claims.
ADR-0005 remains an internal continuation decision only.

## Status

Status: **pass for internal Milestone E public beta approval prep validation**.

Ethos remains source-only pre-alpha. Public beta approval prep has started, but public beta remains
blocked pending a dedicated approval decision, required evidence, public-surface posture check,
claims gate, and decider signoff on exact wording and surface.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `d6f081a`
- Prep artifact: `docs/milestone-e-public-beta-approval-prep.json`
- Schema: `schemas/ethos-milestone-e-public-beta-approval-prep.schema.json`
- Guard: `.github/scripts/test_milestone_e_public_beta_approval_prep.py`
- Validation-record guard:
  `.github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py`
- Lane blocker guard:
  `.github/scripts/test_milestone_e_public_approval_lane_blockers.py`
- Approved source snapshot boundary: source HEAD `660f268df400351347d5185ad36584faa0481c7f`,
  tag `ethos-source-snapshot-660f268`, archive `ethos-source-snapshot-660f268.tar.gz`,
  SHA256 `58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87`
- Exact approved public sentence:
  "Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
  native Ethos JSON and supported foreign parser outputs."
- Excluded approvals: public beta, package publication, hosted surfaces, production positioning,
  public benchmark reports, public benchmark claims, release artifacts, package artifacts, hosted
  operation, public result wording, and wording beyond the exact approved pre-alpha sentence

## Commands

```sh
python3 .github/scripts/test_milestone_e_public_beta_approval_prep.py
python3 .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py
python3 .github/scripts/test_milestone_e_public_approval_lane_blockers.py
python3 .github/scripts/test_milestone_e_validation_record_index.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <public-beta-approval-prep-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <public-beta-approval-prep-private-path-expression> -- docs/validation/milestone-e-public-beta-approval-prep-validation-2026-06-20.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py`; active
non-validation surfaces returned no matches.

## Result

```text
Milestone E public beta approval prep guard green
Milestone E public beta approval prep validation-record guard green
Milestone E public approval lane blocker guard green
Milestone E validation-record index guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
record private-path grep returned no matches
git diff --check green
```

## Required Evidence Before Public Beta Approval

- Dedicated public beta approval decision record.
- Release-scope engineering blocker review.
- Public setup path review.
- Phase 2 project-maintained PDFium build-path decision or explicit rescope.
- Public-surface posture check for exact changed surfaces.
- Claims gate run after exact wording changes.
- Decider signoff on exact wording and surface.

## Validated Public Boundary

- Public reports remain blocked.
- Release artifacts remain blocked.
- Package publication remains blocked.
- Hosted surfaces remain blocked.
- Public result wording remains blocked.
- Production positioning remains blocked.
- Public benchmark claims remain blocked.
- Performance claims remain blocked.
- Quality claims remain blocked.
- Footprint claims remain blocked.
- Table-quality claims remain blocked.
- Parser-quality claims remain blocked.

## Validated Alignment Boundary

- Public beta approval prep is started and remains `not_approved`.
- The approved source snapshot remains source-snapshot-only and does not approve public beta.
- The exact approved pre-alpha sentence remains the only approved public wording.
- Public beta requires a later dedicated approval record and decider signoff.
- The prep target and CI run the public beta approval prep guard before the validation-record
  index.

## Follow-up

Future work that advances public beta must update the public beta prep artifact, add the dedicated
approval decision record, run public-surface posture and claims gates against exact changed
surfaces, and keep public beta blocked until the decider approves the exact wording and surface.
