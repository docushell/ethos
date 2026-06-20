# Milestone E Public Beta Approval Decision Validation - 2026-06-20

## Purpose

Record the dedicated public beta approval decision review requested for the public beta approval
lane.

This is a decision record, but it does not approve public beta. It records that public beta remains
blocked because required release-scope, setup-path, and PDFium build-path evidence still leaves
blockers open. It does not approve package publication, hosted surfaces, production positioning,
public benchmark reports, public benchmark claims, release artifacts, binaries, wheels, npm
packages, crate publication, or wording beyond the exact approved pre-alpha sentence. It does not
change the approved source snapshot, does not resolve or soften blockers, and does not make
performance, quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an
internal continuation decision only.

## Status

Status: **pass for internal Milestone E public beta approval decision validation**.

Ethos remains source-only pre-alpha. Public beta remains blocked. The only approved public wording
continues to be:

"Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
native Ethos JSON and supported foreign parser outputs."

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `3a104a2`
- Lane: public beta approval
- Decision: not approved
- Decision owner: docushell-admin acting as decider
- Prep artifact: `docs/milestone-e-public-beta-approval-prep.json`
- Evidence records:
  - `docs/validation/milestone-e-public-beta-release-scope-engineering-blocker-review-validation-2026-06-20.md`
  - `docs/validation/milestone-e-public-beta-public-setup-path-review-validation-2026-06-20.md`
  - `docs/validation/milestone-e-public-beta-pdfium-build-path-review-validation-2026-06-20.md`
- Approved source snapshot boundary: source HEAD `660f268df400351347d5185ad36584faa0481c7f`,
  tag `ethos-source-snapshot-660f268`, archive `ethos-source-snapshot-660f268.tar.gz`,
  SHA256 `58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87`

## Commands

```sh
python3 .github/scripts/test_milestone_e_public_beta_required_evidence_records.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Public beta approval decision review completed
Public beta remains blocked
Public beta required-evidence record guard green
public-surface posture and claims gates green
Milestone E prep target green
git diff --check green
```

## Required Evidence Status

- Dedicated public beta approval decision record: present in this record, with a not-approved
  decision.
- Release-scope engineering blocker review: present, and it does not clear public beta.
- Public setup path review: present, and the public beta setup path remains unresolved.
- Phase 2 project-maintained PDFium build-path decision or explicit rescope: present as a review,
  and no public beta rescope is accepted.
- Public-surface posture check for exact changed surfaces: required after any surface change.
- Claims gate run after exact wording changes: required after any wording change.
- Decider signoff on exact wording and surface: not granted for public beta in this record.

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

## Follow-up

Public beta can be reconsidered only after the blocker evidence changes, the exact public surface
and wording are specified, posture and claims gates pass for that exact change, and the decider
records a new approval decision.
