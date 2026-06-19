# Validation Records

This directory stores dated evidence records for validation runs that affect Ethos product
claims or determinism boundaries.

Human-written validation records should avoid private usernames, hostnames, and one-off absolute
paths unless the path itself is the subject under test. Preserve commit ids, hashes, commands,
and pass/fail conclusions. Generated benchmark result files follow the evidence-handling policy
in `docs/public-release-checklist.md`.

Records:

- `advisory-scan-2026-06-16.md` - full `cargo-deny` advisory, ban, license, and source scan
  passed with a sidecar Rust 1.94 toolchain and `cargo-deny 0.19.9`; release artifacts still
  need artifact-specific license/NOTICE bundles and package-specific readiness work.
- `claim-language-scan-2026-06-15.md` - current README/docs/examples/benchmark wording was
  scanned for unsupported public claims; README wording was narrowed to avoid speed,
  footprint, table, and heading overclaims.
- `ethos-bench-hygiene-2026-06-15.md` - sibling `ethos-bench` repo hygiene files were verified
  and its local unit/smoke checks passed.
- `license-notice-check-2026-06-15.md` - source license metadata, NOTICE boundaries, and
  non-advisory `cargo-deny` policy checks pass; the follow-up advisory scan is recorded in
  `advisory-scan-2026-06-16.md`, and release artifacts still need artifact-specific
  license/NOTICE bundles.
- `milestone-b-closeout-validation-2026-06-17.md` - internal Milestone B closeout validation
  passed through `make milestone-b-internal-checks`; public benchmark reports, release artifacts,
  package publication, production positioning, and claim wording remain blocked.
- `milestone-c-closeout-validation-2026-06-18.md` - internal Milestone C artifact-validation
  closeout passed through `make milestone-c-internal-checks`; public benchmark reports, release
  artifacts, package publication, production positioning, and claim wording remain blocked.
- `milestone-d-contract-closeout-prep-2026-06-19.md` - internal Milestone D source-only contract
  closeout prep passed through `make milestone-d-internal-contracts`; final D exit still requires
  review, merge to `main`, and a fresh validation run.
- `milestone-d-contract-closeout-validation-2026-06-19.md` - internal Milestone D source-only
  contract closeout passed through `make milestone-d-internal-contracts`; implementation lanes
  and public blockers remain outside this validation record.
- `milestone-d-final-closeout-validation-2026-06-19.md` - final internal Milestone D source-only
  closeout passed through `make milestone-d-internal-contracts`, `cargo test --locked -p
  ethos-cli`, clippy, formatting, and diff hygiene; Ethos remains source-only pre-alpha.
- `milestone-e-prep-validation-2026-06-19.md` - internal Milestone E source-only prep validation
  passed through `make milestone-e-prep`, CI/static guard checks, fixture-candidate JSON parsing,
  public-surface posture grep, and diff hygiene; public-facing E work remains blocked.
- `public-evidence-scan-2026-06-15.md` - tracked evidence and benchmark-result locations were
  scanned for private paths, hostnames, and generated Gate Zero output that belongs in
  `ethos-bench`.
- `public-source-push-preflight-2026-06-15.md` - final public GitHub source-push preflight
  passed for a pre-alpha source repository, with package releases, binary artifacts, public
  benchmark reports, and launch claims still blocked.
- `rendered-crops-2026-06-14.md` - same-host rendered crop repeatability passed on macOS
  arm64 and Linux x64; cross-platform rendered crop byte identity failed because evidence
  bbox differed slightly across platforms.
- `release-notice-draft-2026-06-16.md` - artifact-specific license/NOTICE bundle scaffolding
  now generates an explicit `draft_not_release_ready` bundle with Cargo dependency counts,
  conditional PDFium/font obligations, and release blockers.
- `trademark-screen-2026-06-15.md` - package registry reservations are complete for priority
  public surfaces, and manual review reported a clean `Ethos` trademark outcome for ADR-0006.
- `third-party-manifest-2026-06-16.md` - Cargo third-party dependency license manifest
  generation is repeatable and public-path safe for the current source graph; final release
  artifacts still need artifact-specific license and NOTICE bundles.
