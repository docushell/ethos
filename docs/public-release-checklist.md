# Public Release Checklist

This checklist blocks any public GitHub push, public package publish, public benchmark report,
or launch announcement. It is intentionally stricter than the day-to-day engineering gates.

## Current Status

Ethos is not package-release, artifact-release, benchmark-report, or launch-announcement ready.
It may be pushed as a public pre-alpha source repository only if the latest public-source
preflight passes and the current claim language is used. The package-name/trademark gate is
closed by ADR-0006, but public benchmark, parser-quality, table, heading, speed, footprint, and
rendered-crop byte-identity claims remain blocked.

## Required Before Public Push

- Package-name and trademark decision is closed by accepted ADR-0006 in
  `docs/decisions/ADR-0006-package-identifiers.md`.
- README, docs, examples, and benchmark summaries pass a claim-language scan. Current scan:
  `docs/validation/claim-language-scan-2026-06-15.md`; rerun before public push if public-facing
  text or generated evidence changes.
- No generated evidence file in the public tree exposes private usernames, local machine names,
  private hostnames, or one-off absolute paths. Current scan:
  `docs/validation/public-evidence-scan-2026-06-15.md`; rerun before public push if benchmark
  outputs, validation records, fixture baselines, or reproduction sidecars change.
- Historical benchmark evidence is either regenerated through `ethos-bench` with public-safe
  reproduction metadata or kept out of public release artifacts.
- `ethos-bench` has its own public repository hygiene files: `SECURITY.md`, `CONTRIBUTING.md`,
  and `CODE_OF_CONDUCT.md`. Current check:
  `docs/validation/ethos-bench-hygiene-2026-06-15.md`.
- Gate Zero public result files are signed or otherwise integrity-bound by the accepted release
  process; unsigned local snapshots stay internal.
- Source license metadata, NOTICE boundaries, and non-advisory `cargo-deny` policy checks pass
  the current check: `docs/validation/license-notice-check-2026-06-15.md`. The full advisory
  scan passes for the current source tree in `docs/validation/advisory-scan-2026-06-16.md`.
  Cargo third-party manifest generation is recorded in
  `docs/validation/third-party-manifest-2026-06-16.md`. Release artifacts still need
  artifact-specific license/NOTICE bundles under `docs/release-artifact-notices.md` before
  public release.
- Current public-source preflight:
  `docs/validation/public-source-push-preflight-2026-06-15.md`.
- H1 public-safe competitor comparison evidence is accepted for closeout in
  `docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md`. This closes only the
  evidence-review blocker and does not approve public benchmark reports, does not approve public
  benchmark claims, does not approve release artifacts, does not approve package publication, does
  not approve production positioning, does not approve hosted surfaces, or wording beyond the exact
  approved pre-alpha sentence.
- H2 artifact scope is approved for `source-snapshot` only in
  `docs/validation/h2-source-snapshot-scope-approval-2026-06-20.md`. This does not approve
  binaries, wheels, npm packages, crate publication, hosted surfaces, public benchmark reports, or
  wording beyond the exact approved pre-alpha sentence.

## Approved Execution Sequence

Manual product approval on 2026-06-20 approves the following next-step sequence. This sequence is
not a public-release approval, does not close H1 or H2, does not approve public benchmark reports,
does not approve release artifacts, does not approve package publication, does not approve
production positioning, does not approve hosted surfaces, and does not approve wording beyond the
exact approved pre-alpha sentence.

1. Close H1: closed for public-safe evidence acceptance only in
   `docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md`; public benchmark claims and
   comparison-report wording remain blocked.
2. Close H2 by completing this checklist, including explicit release/package artifact approval and
   passing claim-language gates. The approved artifact scope is `source-snapshot` only; binaries,
   wheels, npm packages, crate publication, hosted surfaces, and public benchmark reports remain
   blocked.
3. Approve any wording beyond the exact pre-alpha sentence only after the benchmark owner maps each
   exact sentence to accepted evidence and the decider approves the exact wording and surface.
4. Harden release-scope engineering blockers: release packaging/operator setup, stable CLI/Python
   docs, public setup path, Phase 2 project-maintained PDFium builds, broader corpus/failure
   fixtures, and cross-platform runtime provisioning.
5. Run release-candidate validation gates: source gates plus `ethos-bench` publication preflight,
   readiness, smoke, and test gates, then rerun posture and claims gates after any public-facing
   text changes.

## Claim Rules

Approved exact public source wording until the checklist is complete:

```text
Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
native Ethos JSON and supported foreign parser outputs.
```

This approval is limited to the exact sentence above on current source-repository public surfaces.
It does not approve public benchmark reports, does not approve release artifacts, does not approve
package publication, does not approve production positioning, does not approve hosted surfaces, and
does not approve altered public wording.

Not allowed:

```text
parser speed superlatives
table-extraction release-readiness claims
heading-extraction release-readiness claims
semantic truth checking
cross-platform bit-identical rendered crops
public benchmark winner
```

## Evidence Handling

Do not hand-edit generated benchmark result JSON to make it public-safe. Regenerate it with
public-safe paths and host metadata, or keep it internal. Human-written validation records may
replace local paths with role-based placeholders as long as hashes, commit ids, outcomes, and
failure conclusions are preserved.
