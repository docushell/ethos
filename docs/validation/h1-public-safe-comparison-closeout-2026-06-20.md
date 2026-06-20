# H1 Public-Safe Comparison Closeout - 2026-06-20

## Purpose

Record H1 closeout for public-safe competitor comparison evidence acceptance. H1 is the evidence
review blocker only: execute and review the public-safe competitor comparison flow, then record
reviewable comparison evidence without unsupported wording.

This record does not approve public benchmark claims, does not approve public benchmark reports,
does not approve comparison-report wording, does not approve release artifacts, does not approve
package publication, does not approve production positioning, does not approve hosted surfaces, and
does not approve wording beyond the exact approved pre-alpha sentence.

## Status

Status: **H1 closed for public-safe evidence acceptance only**.

Ethos remains source-only pre-alpha. H2 remains open, public benchmark reports remain blocked,
public beta remains blocked, and first-release status remains blocked until the release checklist,
wording approvals, release-scope engineering blockers, and release-candidate validation gates close.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `85617c3`
- Sibling evidence repository: `docushell/ethos-bench`
- Sibling branch: `dev/gate-zero-publication-preflight`
- Sibling commit: `572bae915b915c5d4e329146007de869e6c56c7a`
- Approval: `H1 approved: public-safe competitor comparison evidence is accepted for closeout,
  without approving public benchmark claims.`

## Manual Validation Summary

The benchmark owner / decider review accepted H1 after these checks:

- `make benchmark-publication-preflight` completed successfully.
- `make test` completed successfully with 24 tests passing.
- `make smoke` completed successfully.
- `ethos_bench readiness --ethos-repo ../ethos --stdout` reported `status: ready` and
  `blockers_total: 0`.
- `target/public-safety-audit.json` reported `status: pass`, `findings_total: 0`, and
  `files_scanned: 21`.
- `target/claim-audit.json` reported `status: pass`, `blockers_total: 0`,
  `claim_findings_total: 0`, `evidence_bundles_total: 5`, and
  `public_key_signatures_total: 0`.
- `target/attestation-audit.json` reported `status: pass`, `blockers_total: 0`, and
  `public_safe_bundles_total: 5`.
- The public-safe evidence tree contained reviewable summaries for `macos-arm64/g1`,
  `macos-arm64/g2`, `linux-x64/g1`, `linux-x64/g2`, and `cross-platform/g3`.
- Each public-safe summary retained `Public claim status: blocked_until_claim_audit_passes` and
  stated that the bundle is public-safety evidence only, not benchmark-claim approval.
- Local path values were not retained in public-safe summaries.

## Evidence Identifiers

| Evidence | SHA-256 |
| --- | --- |
| `target/public-safety-audit.json` | `b50ad38527c6a13319601f6f8c7a7f45b4b982c8036552758dc72c1e1f1ba0eb` |
| `target/claim-audit.json` | `0e56baaafd87204d39f081d1bbc2f0adcea9af3e7053868256bde1fb4dce862a` |
| `target/attestation-audit.json` | `0e1ec0e745f0fb62535890c8d4e33ed2c92c0a544e1e988265d05436e11963fb` |
| `benchmarks/results/gate-zero/evidence-index.json` | `5dc7e55f5a8cdb9044a4dda5ffc1bd540d2c14aef6b20e54868c9bc118e35919` |
| `benchmarks/results/gate-zero/public-safe/evidence-attestation.json` | `27f2ed5927d3ec85722d558ef1c7c21876e2fc3f8cae3e38054bfa9a2ba5b0d0` |

## Required Before Public Report Or Release

- H2 closes with `docs/public-release-checklist.md` complete and explicitly approved.
- Each public sentence beyond the exact approved pre-alpha sentence has accepted evidence mapping,
  exact wording approval, and exact surface approval.
- Release/package artifacts receive their own approval.
- Release-candidate validation gates pass after public-facing text and generated evidence are in
  their proposed final state.
