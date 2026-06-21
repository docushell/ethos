# Milestone E Public Beta Current-Main Source-Only Approval Validation - 2026-06-21

## Purpose

Record the dedicated approval decision for refreshing the Public beta approval lane to the current
main source state.

This record approves only source-only public beta evaluation for the GitHub source repository at
the reviewed branch commit and squash-merged main commit named below. It does not approve package
publication, public installation, hosted surfaces, production positioning, public benchmark reports,
public benchmark claims, release artifacts, binaries, wheels, npm packages, crate publication,
project-maintained PDFium builds, public reports, public result wording, or wording beyond the
exact approved public beta sentence. ADR-0005 remains an internal continuation decision only.

## Status

Status: **pass for current-main source-only public beta approval validation**.

Decision: approve current-main source-only public beta evaluation.

Ethos remains source-only pre-alpha outside this approved source-only public beta surface.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `6019a97`
- Lane: public beta approval
- Surface: GitHub source repository `docushell/ethos`
- Reviewed commit: `902c423`
- Merged main commit: `6019a97`
- Tree: `f56fde854f6f6e4c4070209329f8c7b12310aa51`
- Approval owner: docushell-admin acting as decider

## Exact Approved Wording

Ethos is public beta for source-only evaluation. It verifies whether AI citations are grounded in
document evidence across native Ethos JSON and supported foreign parser outputs. Package
publication, hosted surfaces, production positioning, and public benchmark claims remain blocked.

## Exact Approved Surface

The approved surface remains limited to source-only evaluation through the GitHub source
repository. Users may clone the source, read source-tree docs, build the CLI locally, and run
source-tree validation or setup commands.

Approved source-tree commands for this surface:

```sh
rustup show
cargo build --locked -p ethos-cli
./target/debug/ethos --help
make verify-alpha
./target/debug/ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --fail-on-ungrounded \
  --out /tmp/ethos-native-verification-report.json
```

## Refresh Basis

- `docs/milestone-e-public-beta-current-main-refresh-prep.json` recorded the required refresh prep
  boundary before approval.
- The reviewed branch commit `902c423` and merged main commit `6019a97` have the same source tree:
  `f56fde854f6f6e4c4070209329f8c7b12310aa51`.
- Public-surface posture, claims, Milestone E prep, and source-checkout build gates passed before
  this decision record.
- The exact approved public beta wording is unchanged.

## Explicit Exclusions

- Package publication remains blocked.
- Public installation remains blocked.
- Real-version cargo publish remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Release artifacts remain blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- npm packages remain blocked.
- Crate publication remains blocked.
- Project-maintained PDFium builds remain blocked.
- Broader public wording remains blocked.
- Public reports remain blocked.
- Public result wording remains blocked.
- Performance claims remain blocked.
- Quality claims remain blocked.
- Footprint claims remain blocked.
- Table-quality claims remain blocked.
- Parser-quality claims remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_public_facing_readiness_ledger.py
python3 .github/scripts/test_milestone_e_public_beta_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_pre_approval_gap_ledger.py
python3 .github/scripts/test_milestone_e_public_beta_current_main_refresh_prep.py
python3 .github/scripts/test_milestone_e_public_beta_current_main_source_only_approval.py
python3 schemas/validate_examples.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Current-main source-only public beta approval validation passed
Reviewed branch commit and merged main commit have the same source tree
Public-surface posture and claims gates passed
Milestone E prep target passed
Source-checkout CLI build passed
git diff --check passed
```
