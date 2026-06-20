# H2 Source-Snapshot Candidate Evidence - 660f268 - 2026-06-20

## Purpose

Record refreshed source-snapshot candidate evidence for approved candidate source HEAD `660f268`
after H2 artifact scope was approved for `source-snapshot` only.

This record does not close H2 for this candidate, does not approve public beta, does not approve
binaries, does not approve wheels, does not approve npm packages, does not approve crate
publication, does not approve hosted surfaces, does not approve public benchmark reports, and does
not approve wording beyond the exact approved pre-alpha sentence.

## Status

Status: **refreshed source-snapshot candidate evidence recorded; closeout recorded separately for this candidate**.

Ethos remains source-only pre-alpha. The prior H2 closeout remains limited to the exact
source-snapshot candidate at source HEAD `60abfd4`. Closeout for the exact `660f268` candidate and
surface is recorded in `docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md`.

## Subject

- Repository: `docushell/ethos`
- Candidate source HEAD: `660f268`
- Candidate archive: `ethos-source-snapshot-660f268.tar.gz`
- Candidate archive SHA256:
  `58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87`
- Candidate archive prefix: `ethos-source-snapshot-660f268/`
- Extracted file count: `501`
- Approved artifact class: `source-snapshot`
- Excluded artifact classes: `github-release-binary`, `wheel`, `npm-package`,
  `crate-publication`, `hosted-surface`, `public-benchmark-report`

## Required Files Confirmed

The candidate archive includes:

- `LICENSE`
- `NOTICE`
- `README.md`
- `docs/gate-zero-evidence-runbook.md`
- `docs/public-release-checklist.md`
- `docs/release-artifact-notices.md`

## Manual Validation Evidence

Manual candidate generation and extraction checks reported:

```text
SOURCE_SNAPSHOT_EXTRACT_OK
501 files
source-snapshot candidate audit: pass
BLOCKED_ARTIFACT_SCAN_PASS
UNTRACKED_OR_BUILD_PATH_SCAN_PASS
```

Manual public-surface and claim-language checks reported:

```text
public surface posture tests: pass
public pre-alpha wording approval tests: pass
claims gate green
diff hygiene: pass
```

## Boundaries

- This record captures refreshed candidate evidence only.
- H2 closeout is recorded separately for this candidate.
- The candidate is source-snapshot-only; binaries, wheels, npm packages, crate publication, hosted
  surfaces, and public benchmark reports remain blocked.
- Public wording remains limited to the exact approved pre-alpha sentence.

## Closeout Record

- Decider approval for source HEAD `660f268`, archive
  `ethos-source-snapshot-660f268.tar.gz`, SHA256
  `58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87`, and the
  source-snapshot-only surface is recorded in
  `docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md`.
- Final release-candidate gates run after any additional public-facing text or source changes.
