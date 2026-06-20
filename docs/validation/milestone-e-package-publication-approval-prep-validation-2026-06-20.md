# Milestone E Package Publication Approval Prep Validation - 2026-06-20

## Purpose

Record internal validation that the package publication approval prep lane has started without
approving package publication.

This record covers only the source-tree approval prep artifact at
`docs/milestone-e-package-publication-approval-prep.json`. It does not approve package
publication, does not approve binaries, does not approve wheels, does not approve npm packages,
does not approve crate publication, does not approve public beta, does not approve hosted surfaces,
does not approve production positioning, does not approve public benchmark reports, does not approve
public benchmark claims, and does not approve wording beyond the exact approved pre-alpha sentence.
It does not change the approved source snapshot, does not create release artifacts, does not resolve
or soften blockers, and does not make performance, quality, footprint, table-quality, or
parser-quality claims. ADR-0005 remains an internal continuation decision only.

## Status

Status: **pass for internal Milestone E package publication approval prep validation**.

Ethos remains source-only pre-alpha. Package publication approval prep has started, but package
publication remains blocked pending a dedicated approval decision, required evidence,
public-surface posture check, claims gate, and devrel / decider signoff on exact artifact names and
surfaces.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `04411ec`
- Prep artifact: `docs/milestone-e-package-publication-approval-prep.json`
- Schema: `schemas/ethos-milestone-e-package-publication-approval-prep.schema.json`
- Guard: `.github/scripts/test_milestone_e_package_publication_approval_prep.py`
- Validation-record guard:
  `.github/scripts/test_milestone_e_package_publication_approval_prep_validation_record.py`
- Lane blocker guard:
  `.github/scripts/test_milestone_e_public_approval_lane_blockers.py`
- Approved source snapshot boundary: source HEAD `660f268df400351347d5185ad36584faa0481c7f`,
  tag `ethos-source-snapshot-660f268`, archive `ethos-source-snapshot-660f268.tar.gz`,
  SHA256 `58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87`
- Exact approved public sentence:
  "Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
  native Ethos JSON and supported foreign parser outputs."
- Excluded approvals: package publication, binaries, wheels, npm packages, crate publication,
  public beta, hosted surfaces, production positioning, public benchmark reports, public benchmark
  claims, release artifacts, public result wording, and wording beyond the exact approved
  pre-alpha sentence

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_approval_prep_validation_record.py
python3 .github/scripts/test_milestone_e_public_approval_lane_blockers.py
python3 .github/scripts/test_milestone_e_validation_record_index.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <package-publication-approval-prep-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <package-publication-approval-prep-private-path-expression> -- docs/validation/milestone-e-package-publication-approval-prep-validation-2026-06-20.md
git diff --check
```

The grep command used the forbidden wording covered by
`.github/scripts/test_milestone_e_package_publication_approval_prep_validation_record.py`; active
non-validation surfaces returned no matches.

## Result

```text
Milestone E package publication approval prep guard green
Milestone E package publication approval prep validation-record guard green
Milestone E public approval lane blocker guard green
Milestone E validation-record index guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
record private-path grep returned no matches
git diff --check green
```

## Required Evidence Before Package Publication Approval

- Dedicated package publication approval decision record.
- Artifact-specific license and notice bundle review.
- Package registry metadata review.
- Source-to-artifact provenance review.
- Installation and rollback validation for each artifact family.
- Public-surface posture check for exact changed surfaces.
- Decider signoff on exact artifact names and surfaces.

## Validated Public Boundary

- Public reports remain blocked.
- Release artifacts remain blocked.
- Package publication remains blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- Npm packages remain blocked.
- Crate publication remains blocked.
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

- Package publication approval prep is started and remains `not_approved`.
- The approved source snapshot remains source-snapshot-only and does not approve package
  publication.
- The exact approved pre-alpha sentence remains the only approved public wording.
- Package publication requires a later dedicated approval record and devrel / decider signoff.
- The prep target and CI run the package publication approval prep guard before the
  validation-record index.

## Follow-up

Future work that advances package publication must update the package publication prep artifact,
add the dedicated approval decision record, run public-surface posture and claims gates against
exact changed surfaces, and keep package publication blocked until devrel and the decider approve
the exact artifact names, wording, and surface.
