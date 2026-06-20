# Public Pre-Alpha Wording Approval - 2026-06-20

## Purpose

Record product approval for the exact source-only pre-alpha public sentence after manual review of
the `ethos-bench` evidence-hygiene preflight and source-repository claim gates.

This record approves only the exact sentence below on current source-repository public surfaces. It
does not approve public benchmark reports, does not approve release artifacts, does not approve
package publication, does not approve production positioning, does not approve hosted surfaces,
does not approve public comparison reports, and does not approve altered public wording.

## Approved Sentence

```text
Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across native Ethos JSON and supported foreign parser outputs.
```

## Status

Status: **pass for exact pre-alpha wording approval**.

Ethos remains source-only pre-alpha. Broader public result language remains blocked until a future
claim-audit and decider review maps each exact sentence to an approved surface.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `a1d2cfc`
- Sibling evidence-hygiene branch: `dev/gate-zero-publication-preflight`
- Sibling ethos-bench commit: `572bae9`
- Approved surfaces: README status block, public-release checklist claim-rule block,
  execution-status PM rule, and source-repository docs that repeat the exact approved sentence
- Excluded surfaces: public benchmark reports, comparison reports, release notes, package registry
  pages, hosted surfaces, production pages, generated result summaries, and any wording that
  changes the approved sentence

## Manual Verification

The product/decider review confirmed:

- `make benchmark-publication-preflight` passed in `ethos-bench`.
- `make test` passed in `ethos-bench`.
- `make smoke` passed in `ethos-bench`.
- `ethos_bench readiness --ethos-repo ../ethos --stdout` reported `status: ready` with zero
  readiness blockers.
- `target/public-safety-audit.json` reported `status: pass`.
- `target/claim-audit.json` reported `status: pass`.
- `target/attestation-audit.json` reported no blocked status.
- `python3 .github/scripts/test_public_surface_posture.py` passed in `ethos`.
- `python3 .github/scripts/claims_gate.py` passed in `ethos`.
- `git diff --check` passed in `ethos`.
- Private-path grep over the Milestone E final closeout record returned no matches.

## Commands

```sh
make benchmark-publication-preflight
make test
make smoke
PYTHONPATH=src python3 -m ethos_bench readiness --ethos-repo ../ethos --stdout
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
git grep <prealpha-wording-private-path-expression> -- docs/validation/milestone-e-final-closeout-validation-2026-06-20.md
git diff --check
```

## Remaining Boundaries

- Public benchmark reports remain blocked.
- Public comparison reports remain blocked.
- Release artifacts remain blocked.
- Package publication remains blocked.
- Production positioning remains blocked.
- Hosted surfaces remain blocked.
- Public release/package scope remains blocked by `docs/public-release-checklist.md`.
- Any sentence other than the approved sentence above requires a new claim-audit and decider
  review before it is used on public-facing surfaces.
