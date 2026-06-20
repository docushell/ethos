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
- `milestone-e-fixture-promotion-criteria-validation-2026-06-19.md` - internal Milestone E
  fixture-promotion criteria validation for `docs/milestone-e-fixture-promotion-criteria.json`
  passed through criteria consistency checks, JSON parsing, public-surface posture checks,
  `make milestone-e-prep`, and diff hygiene; fixture promotion remains internal planning only.
- `milestone-e-fixture-candidate-blocker-alignment-validation-2026-06-20.md` - internal
  Milestone E fixture-candidate blocker alignment validation passed through fixture-candidate
  schema checks, criteria alignment checks, public-surface posture checks, `make
  milestone-e-prep`, and diff hygiene; fixture blockers remain explicit and unresolved.
- `milestone-e-prep-scope-structured-blocker-validation-2026-06-20.md` - internal Milestone E
  prep-scope structured blocker validation passed through prep-scope checks, fixture-promotion
  criteria checks, fixture-candidate blocker-alignment checks, public-surface posture checks,
  `make milestone-e-prep`, and diff hygiene; fixture blockers remain structured, explicit, and
  unresolved.
- `milestone-e-internal-trust-loop-walkthrough-validation-2026-06-19.md` - internal Milestone E
  trust-loop walkthrough validation for `docs/milestone-e-internal-trust-loop-walkthrough.json`
  passed through walkthrough consistency checks, schema validation, `make verify-alpha`,
  public-surface posture checks, `make milestone-e-prep`, and diff hygiene; walkthrough sequencing
  remains internal planning only.
- `milestone-e-internal-trust-loop-walkthrough-all-candidates-validation-2026-06-19.md` - internal
  Milestone E all-candidates trust-loop walkthrough validation for
  `docs/milestone-e-internal-trust-loop-walkthrough.json` passed through walkthrough consistency
  checks, schema validation, current candidate command coverage, public-surface posture checks,
  `make milestone-e-prep`, and diff hygiene; walkthrough sequencing remains internal planning only.
- `milestone-e-internal-trust-loop-use-protocol-validation-2026-06-19.md` - internal Milestone E
  trust-loop use protocol validation for
  `docs/milestone-e-internal-trust-loop-use-protocol.json` passed through protocol consistency
  checks, schema validation, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; internal walkthrough use remains source-only and not promoted beyond planning.
- `milestone-e-internal-trust-loop-rehearsal-evidence-matrix-validation-2026-06-19.md` -
  internal Milestone E trust-loop rehearsal/evidence matrix validation for
  `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json` passed through matrix
  consistency checks, schema validation, public-surface posture checks, `make milestone-e-prep`,
  and diff hygiene; internal rehearsal planning remains source-only and not promoted beyond
  planning.
- `milestone-e-internal-trust-loop-blocker-ledger-validation-2026-06-19.md` - internal Milestone E
  trust-loop blocker ledger validation for
  `docs/milestone-e-internal-trust-loop-blocker-ledger.json` passed through ledger consistency
  checks, schema validation, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; internal blocker tracking remains source-only and does not resolve or soften blockers.
- `milestone-e-native-grounding-baseline-rehearsal-validation-2026-06-19.md` - internal Milestone E
  native-grounding-baseline rehearsal validation passed through `make verify-alpha`,
  row-specific consistency checks, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; the record covers only `native-grounding-baseline` and does not resolve or soften
  blockers.
- `milestone-e-diagnostic-boundary-check-rehearsal-validation-2026-06-19.md` - internal Milestone E
  diagnostic-boundary-check rehearsal validation passed through `make verify-alpha`,
  row-specific consistency checks, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; the record covers only `diagnostic-boundary-check` and does not resolve or soften
  blockers.
- `milestone-e-capability-downgrade-boundary-rehearsal-validation-2026-06-19.md` - internal
  Milestone E capability-downgrade-boundary rehearsal validation passed through
  `make milestone-d-capability-downgrade-contract`, row-specific consistency checks,
  public-surface posture checks, `make milestone-e-prep`, and diff hygiene; the record covers only
  `capability-downgrade-boundary` and does not resolve or soften blockers.
- `milestone-e-opendataloader-adapter-grounding-rehearsal-validation-2026-06-19.md` - internal
  Milestone E opendataloader-adapter-grounding rehearsal validation passed through
  `make milestone-d-opendataloader-adapter-shape-contract`, row-specific consistency checks,
  public-surface posture checks, `make milestone-e-prep`, and diff hygiene; the record covers only
  `opendataloader-adapter-grounding` and does not resolve or soften blockers.
- `milestone-e-pinned-opendataloader-fixture-path-rehearsal-validation-2026-06-19.md` - internal
  Milestone E pinned-opendataloader-fixture-path rehearsal validation passed through
  `make verify-alpha`, row-specific consistency checks, public-surface posture checks,
  `make milestone-e-prep`, and diff hygiene; the record covers only
  `pinned-opendataloader-fixture-path` and does not resolve or soften blockers.
- `milestone-e-crop-descriptor-source-bound-shape-rehearsal-validation-2026-06-20.md` -
  internal Milestone E crop-descriptor-source-bound-shape rehearsal validation passed through
  `make milestone-d-internal-contracts`, row-specific consistency checks, public-surface posture
  checks, `make milestone-e-prep`, and diff hygiene; the record covers only
  `crop-descriptor-source-bound-shape` and does not resolve or soften blockers.
- `milestone-e-rag-chunk-artifact-loop-rehearsal-validation-2026-06-20.md` - internal Milestone E
  rag-chunk-artifact-loop rehearsal validation passed through `make rag-chunk-alpha`,
  row-specific consistency checks, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; the record covers only `rag-chunk-artifact-loop` and does not resolve or soften
  blockers.
- `milestone-e-security-report-artifact-loop-rehearsal-validation-2026-06-20.md` - internal
  Milestone E security-report-artifact-loop rehearsal validation passed through
  `make security-report-alpha`, row-specific consistency checks, public-surface posture checks,
  `make milestone-e-prep`, and diff hygiene; the record covers only
  `security-report-artifact-loop` and does not resolve or soften blockers.
- `milestone-e-demo-narrative-index-rehearsal-validation-2026-06-20.md` - internal Milestone E
  demo-narrative-index rehearsal validation passed through `make verify-alpha`, row-specific
  consistency checks, public-surface posture checks, `make milestone-e-prep`, and diff hygiene;
  the record covers only `demo-narrative-index` and does not resolve or soften blockers.
- `milestone-e-rehearsal-row-record-coverage-validation-2026-06-20.md` - internal Milestone E
  rehearsal row-record coverage validation passed through row-record coverage checks, matrix and
  blocker-ledger consistency checks, public-surface posture checks, `make milestone-e-prep`, and
  diff hygiene; the record covers only current matrix row-record coverage and does not resolve or
  soften blockers.
- `milestone-e-schema-registry-alignment-validation-2026-06-20.md` - internal Milestone E
  schema-registry alignment validation passed through schema-artifact pair checks, schema docs,
  roadmap/status references, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; the record covers only current E prep schema-artifact alignment and does not resolve or
  soften blockers.
- `milestone-e-public-boundary-alignment-validation-2026-06-20.md` - internal Milestone E
  public-boundary alignment validation passed through public-boundary checks, schema-registry
  checks, public-surface posture checks, `make milestone-e-prep`, and diff hygiene; the record
  covers only current E prep public-boundary alignment and does not resolve or soften blockers.
- `milestone-e-blocked-output-alignment-validation-2026-06-20.md` - internal Milestone E
  blocked-output alignment validation passed through blocked-output vocabulary checks, schema enum
  checks, ledger row-copy checks, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; the record covers only current E prep blocked-output alignment and does not resolve or
  soften blockers.
- `milestone-e-evidence-lane-alignment-validation-2026-06-20.md` - internal Milestone E
  evidence-lane alignment validation passed through evidence-lane vocabulary checks, schema enum
  checks, matrix and ledger row-copy checks, public-surface posture checks, `make
  milestone-e-prep`, and diff hygiene; the record covers only current E prep evidence-lane
  alignment and does not resolve or soften blockers.
- `milestone-e-diagnostic-boundary-alignment-validation-2026-06-20.md` - internal Milestone E
  diagnostic-boundary alignment validation passed through diagnostic-boundary vocabulary checks,
  schema field checks, row-record checks, public-surface posture checks, `make milestone-e-prep`,
  and diff hygiene; the record covers only current E prep diagnostic-boundary alignment and does
  not resolve or soften blockers.
- `milestone-e-promotion-status-alignment-validation-2026-06-20.md` - internal Milestone E
  promotion-status alignment validation passed through promotion-status vocabulary checks, top-level
  and row-level schema const checks, row-record checks, public-surface posture checks, `make
  milestone-e-prep`, and diff hygiene; the record covers only current E prep promotion-status
  alignment and does not resolve or soften blockers.
- `milestone-e-source-status-alignment-validation-2026-06-20.md` - internal Milestone E
  source-status alignment validation passed through source-status vocabulary checks, top-level and
  row-level schema const checks, validation-record checks, public-surface posture checks, `make
  milestone-e-prep`, and diff hygiene; the record covers only current E prep source-status
  alignment and does not resolve or soften blockers.
- `milestone-e-applies-to-binding-alignment-validation-2026-06-20.md` - internal Milestone E
  applies-to binding alignment validation passed through artifact binding checks, schema const
  checks, validation-record checks, public-surface posture checks, `make milestone-e-prep`, and
  diff hygiene; the record covers only current E prep source-artifact binding alignment and does
  not resolve or soften blockers.
- `milestone-e-required-before-alignment-validation-2026-06-20.md` - internal Milestone E
  required-before alignment validation passed through readiness-gate checks, schema enum checks,
  validation-record checks, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; the record covers only current E prep readiness-gate alignment and does not resolve or
  soften blockers.
- `milestone-e-validation-command-index-validation-2026-06-20.md` - internal Milestone E
  validation-command index validation passed through command-alignment checks, schema enum checks,
  row-record checks, public-surface posture checks, `make milestone-e-prep`, and diff hygiene; the
  record covers only current E validation-command coverage and does not resolve or soften blockers.
- `milestone-e-validation-record-index-validation-2026-06-20.md` - internal Milestone E
  validation-record index validation passed through validation-record index checks, guard wiring
  checks, public-surface posture checks, `make milestone-e-prep`, and diff hygiene; the record
  covers only current E validation-record index coverage and does not resolve or soften blockers.
- `milestone-e-validation-source-head-alignment-validation-2026-06-20.md` - internal Milestone E
  validation-record source-head alignment validation passed through source-head provenance checks,
  validation-record checks, public-surface posture checks, `make milestone-e-prep`, and diff
  hygiene; the record covers only validation-record source-head alignment and does not resolve or
  soften blockers.
- `milestone-e-prep-guard-sequence-index-validation-2026-06-20.md` - internal Milestone E prep
  guard-sequence index validation passed through exact Makefile sequence checks, CI ordering checks,
  public-surface posture checks, `make milestone-e-prep`, and diff hygiene; the record covers only
  current E prep guard ordering and does not resolve or soften blockers.
- `milestone-e-prep-current-guard-validation-2026-06-20.md` - internal Milestone E current prep
  guard validation passed through guard-sequence index checks, validation-record index checks,
  public-surface posture checks, `make milestone-e-prep`, and diff hygiene; the record covers only
  current E prep guard state and does not resolve or soften blockers.
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
