# Public Release Checklist

This checklist blocks any public GitHub push, public package publish, public benchmark report,
or launch announcement. It is intentionally stricter than the day-to-day engineering gates.

## Current Status

Ethos is not package-release, artifact-release, benchmark-report, or launch-announcement ready.
It may be pushed as a public pre-alpha source repository only if the latest public-source
preflight passes and the current claim language is used. The package-name/trademark gate is
closed by ADR-0006, but public benchmark, parser-quality, table, heading, speed, footprint, and
rendered-crop byte-identity claims remain blocked.

Patch `0.1.1` readiness prep is recorded in
`docs/validation/patch-0-1-1-readiness-prep-validation-2026-06-23.md` for review only. It records
candidate onboarding contents after `ethos doctor`, synthetic fixture golden-change guarding, the
2-minute PDF parse quickstart, and improved missing/unusable PDFium guidance landed on `main`. It
does not approve a release, tag, version bump, package publish, GitHub Release artifact, hosted
surface, production positioning, Windows packaged artifact, bundled project-maintained PDFium
build, public benchmark report, or public benchmark claim.

Patch `0.1.2` readiness prep is recorded in
`docs/validation/patch-0-1-2-readiness-prep-validation-2026-06-24.md` for review only. It records
the narrow beta patch candidate boundary after `ethos evidence anchor`, the `evidence_anchor` v1
guard, and professional public README status wording landed on `main`. It keeps the current public
install baseline at `0.1.1` and does not approve a release, tag, version bump, package publish,
GitHub Release artifact, hosted surface, production positioning, Windows packaged artifact,
bundled project-maintained PDFium build, public benchmark report, or public benchmark claim.

Patch `0.1.2` version activation is recorded in
`docs/validation/patch-0-1-2-version-activation-validation-2026-06-24.md` for candidate validation
only. It moves Rust workspace and Python source/package metadata to `0.1.2`, keeps npm and public
install wording on the published `0.1.1` baseline until matching CLI artifacts and publication
evidence exist, and does not approve a release, tag, package publish, GitHub Release artifact,
hosted surface, production positioning, Windows packaged artifact, bundled project-maintained
PDFium build, public benchmark report, or public benchmark claim.

Patch `0.1.2` artifact/package evidence is recorded in
`docs/validation/patch-0-1-2-artifact-package-evidence-validation-2026-06-24.md` for local
candidate validation only. It dynamically checks `0.1.2` Rust crate candidates and the
`ethos_pdf-0.1.2-py3-none-any.whl` candidate, and it updates draft CLI artifact workflow smoke
expectations to `ethos 0.1.2`. The public install baseline remains `0.1.1`, public installation
wording remains blocked, registry publication remains blocked, GitHub Release artifact publication
remains blocked, and npm vendor refresh remains blocked until separate approval, operator evidence,
and closeout records pass.

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
- H2 source-snapshot candidate evidence is recorded in
  `docs/validation/h2-source-snapshot-candidate-evidence-2026-06-20.md` for source HEAD
  `60abfd4`; closeout is recorded separately for the exact source-snapshot candidate and surface.
- H2 is closed for the exact source-snapshot candidate and source-snapshot-only surface in
  `docs/validation/h2-source-snapshot-closeout-2026-06-20.md`. Binaries, wheels, npm packages,
  crate publication, and hosted surfaces remain blocked; public benchmark reports remain blocked;
  public beta, production positioning, and wording beyond the exact approved pre-alpha sentence
  remain blocked.
- Refreshed H2 source-snapshot candidate evidence is recorded in
  `docs/validation/h2-source-snapshot-candidate-evidence-660f268-2026-06-20.md` for approved
  candidate source HEAD `660f268`.
- H2 is closed for the exact source-snapshot candidate at source HEAD `660f268` and
  source-snapshot-only surface in
  `docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md`. Binaries, wheels, npm
  packages, crate publication, and hosted surfaces remain blocked; public benchmark reports remain
  blocked; public beta, production positioning, and wording beyond the exact approved pre-alpha
  sentence remain blocked.

## Approved Execution Sequence

Manual product approval on 2026-06-20 approved the following next-step sequence. That sequence
approval was not a public-release approval and did not itself close H1 or H2. It does not approve
public benchmark reports, does not approve release artifacts, does not approve package
publication, does not approve production positioning, does not approve hosted surfaces, and does
not approve wording beyond the exact approved pre-alpha sentence. Subsequent records close H1 and
H2 only within their stated boundaries.

1. Close H1: closed for public-safe evidence acceptance only in
   `docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md`; public benchmark claims and
   comparison-report wording remain blocked.
2. Close H2: closed for the exact source-snapshot candidate at source HEAD `660f268` and
   source-snapshot-only surface in
   `docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md`. The approved artifact scope is
   `source-snapshot` only; binaries, wheels, npm packages, crate publication, hosted surfaces,
   public benchmark reports, public beta, production positioning, and wording beyond the exact
   approved pre-alpha sentence remain blocked.
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
