# Milestone E Public Approval Lane Blockers Validation - 2026-06-20

## Purpose

Record internal validation that the current Milestone E prep tree defines blocker lanes for later
public approvals without approving any lane.

This record covers only the source-tree blocker ledger at
`docs/milestone-e-public-approval-lane-blockers.json`. It does not approve public beta, does not
approve package publication, does not approve hosted surfaces, does not approve production
positioning, does not approve public benchmark reports, does not approve public benchmark claims,
and does not approve wording beyond the exact approved pre-alpha sentence. It does not resolve or
soften blockers, does not create release artifacts, does not change the approved source snapshot,
and does not make performance, quality, footprint, table-quality, or parser-quality claims.
ADR-0005 remains an internal continuation decision only.

## Status

Status: **pass for internal Milestone E public approval lane blocker validation**.

Ethos remains source-only pre-alpha. The public approval lane blocker ledger records that all
public approval lanes remain blocked until a later dedicated approval record, owner signoff, gate
script, validation record, and exact wording/surface review exist for that lane.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `9efee7a`
- Ledger: `docs/milestone-e-public-approval-lane-blockers.json`
- Schema: `schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json`
- Guard: `.github/scripts/test_milestone_e_public_approval_lane_blockers.py`
- Validation-record guard:
  `.github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py`
- Gate script recorded per lane:
  `.github/scripts/test_milestone_e_public_approval_lane_blockers.py`
- Validation record recorded per lane:
  `docs/validation/milestone-e-public-approval-lane-blockers-validation-2026-06-20.md`
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
python3 .github/scripts/test_milestone_e_public_approval_lane_blockers.py
python3 .github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py
python3 .github/scripts/test_milestone_e_required_before_alignment_validation_record.py
python3 .github/scripts/test_milestone_e_validation_record_index.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <public-approval-lane-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <public-approval-lane-private-path-expression> -- docs/validation/milestone-e-public-approval-lane-blockers-validation-2026-06-20.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py`; active
non-validation surfaces returned no matches.

## Result

```text
Milestone E public approval lane blocker guard green
Milestone E public approval lane blocker validation-record guard green
Milestone E required-before validation-record guard green
Milestone E validation-record index guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
record private-path grep returned no matches
git diff --check green
```

## Validated Approval Lanes

| Lane | Current status | Required before approval |
| --- | --- | --- |
| Public beta approval | Public beta remains blocked. | Dedicated public beta approval record, release-scope engineering blocker review, public-surface posture check, claims gate, and decider signoff. |
| Package publication | Package publication remains blocked. | Dedicated package publication approval record, artifact-specific license/notice review, package registry metadata review, installation and rollback validation, and decider signoff. |
| Hosted surface | Hosted surfaces remain blocked. | Dedicated hosted surface approval record, surface inventory, security/privacy review, public-surface posture check, and decider signoff. |
| Production positioning | Production positioning remains blocked. | Dedicated production positioning approval record, operator setup and failure-mode review, support boundary review, claim audit, and decider signoff. |
| Public benchmark report | Public benchmark reports remain blocked. | Dedicated public benchmark report approval record, `ethos-bench` publication preflight, benchmark-owner wording acceptance, claim audit, and decider signoff. |

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

- The approval lane ledger lists exactly five public approval lanes.
- Every lane has explicit scope, required evidence, blockers, allowed wording, forbidden wording,
  approval owner, gate script, and validation record.
- The gate script and validation record are the same source-tree guard pair for all five lanes.
- The ledger preserves the approved source-snapshot-only boundary for
  `ethos-source-snapshot-660f268`.
- The ledger preserves the exact approved pre-alpha public sentence and does not expand public
  wording.
- The prep target and CI run the lane blocker guard before the validation-record index.

## Follow-up

Future work that opens any public approval lane must create a lane-specific approval record,
record exact owner approval, update the lane ledger, run the public-surface posture and claims
gates against the exact changed surface, and keep the source-only pre-alpha boundary explicit until
that lane is approved by a dedicated decision.
