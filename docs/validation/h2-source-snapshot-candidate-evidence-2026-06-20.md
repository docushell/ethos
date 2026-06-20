# H2 Source-Snapshot Candidate Evidence - 2026-06-20

## Purpose

Record the source-snapshot candidate evidence gathered after H2 artifact scope was approved for
`source-snapshot` only.

This record does not close H2, does not approve public beta, does not approve binaries, does not
approve wheels, does not approve npm packages, does not approve crate publication, does not approve
hosted surfaces, does not approve public benchmark reports, and does not approve wording beyond the
exact approved pre-alpha sentence.

## Status

Status: **source-snapshot candidate evidence recorded; H2 remains open**.

Ethos remains source-only pre-alpha. H2 remains open until the decider explicitly approves H2
closeout for the exact source-snapshot candidate and surface after final gates pass.

## Subject

- Repository: `docushell/ethos`
- Candidate source HEAD: `60abfd4`
- Candidate archive: `ethos-source-snapshot-60abfd4.tar.gz`
- Candidate archive SHA256:
  `9ae9f40e8385035101bae1b947a6894bcdaf4c7ffb852faef73cb0755452ac51`
- Candidate archive prefix: `ethos-source-snapshot-60abfd4/`
- Extracted file count: `497`
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
497 files
source-snapshot candidate audit: pass
BLOCKED_ARTIFACT_SCAN_PASS
```

Manual public-surface and claim-language checks reported:

```text
public surface posture tests: pass
public pre-alpha wording approval tests: pass
claims gate green
diff hygiene: pass
```

## Boundaries

- This record captures candidate evidence only.
- H2 remains open.
- The candidate is source-snapshot-only; binaries, wheels, npm packages, crate publication, hosted
  surfaces, and public benchmark reports remain blocked.
- Public wording remains limited to the exact approved pre-alpha sentence.

## Required Before H2 Closeout

- Decider reviews this exact candidate evidence.
- Decider approves or rejects H2 closeout for the exact source-snapshot candidate and surface.
- Final release-candidate gates run after any additional public-facing text or source changes.
