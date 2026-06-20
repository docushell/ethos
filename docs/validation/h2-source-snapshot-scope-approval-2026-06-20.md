# H2 Source-Snapshot Scope Approval - 2026-06-20

## Purpose

Record H2 artifact scope approval for the first release-readiness path. The approved scope is
`source-snapshot` only.

This record does not close H2, does not approve public beta, does not approve GitHub release
binaries, does not approve wheels, does not approve npm packages, does not approve crate
publication, does not approve hosted surfaces, does not approve public benchmark reports, and does
not approve wording beyond the exact approved pre-alpha sentence.

## Status

Status: **approved artifact scope: source-snapshot only**.

Ethos remains source-only pre-alpha. H2 remains open until the source-snapshot checklist,
claim-language gates, public evidence scans, and release-candidate validation gates pass in their
proposed final state.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `cdf5be7`
- Approved artifact class: `source-snapshot`
- Excluded artifact classes: `github-release-binary`, `wheel`, `npm-package`, `crate-publication`,
  `hosted-surface`, `public-benchmark-report`
- Approval: `H2 artifact scope approved: source-snapshot only. No binaries, no wheels, no npm
  package, no crate publication, no hosted surface, and no public benchmark report.`

## Manual Review Basis

The release notice draft was reviewed after `make release-notice-draft` generated:

- `target/release-notice-draft/NOTICE.release.md`
- `target/release-notice-draft/THIRD-PARTY-CARGO-LICENSES.json`
- `target/release-notice-draft/release-notice-manifest.json`

The generated draft reported:

- artifact name: `ethos-cli-draft`
- status: `draft_not_release_ready`
- workspace packages: `7`
- third-party registry packages: `93`
- blocked artifact classes: GitHub release binaries, wheels, npm package updates, crate
  publication, and public benchmark report
- conditional notices required if any future artifact bundles PDFium or Liberation fonts

## Required Before H2 Closeout

- Replace the draft source-snapshot scope with a concrete source-snapshot identifier.
- Confirm the source snapshot contains `LICENSE`, `NOTICE`, and the required source notices.
- Rerun claim-language gates after any public-facing text changes.
- Rerun public evidence/private-path scans after validation/evidence changes.
- Record explicit decider approval for H2 closeout after source-snapshot evidence is final.
