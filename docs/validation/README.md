# Validation Records

This directory stores dated evidence records for validation runs that affect Ethos product
claims or determinism boundaries.

Human-written validation records should avoid private usernames, hostnames, and one-off absolute
paths unless the path itself is the subject under test. Preserve commit ids, hashes, commands,
and pass/fail conclusions. Generated benchmark result files follow the evidence-handling policy
in `docs/public-release-checklist.md`.

Records:

Current package publication evidence records keep publication blocked while tracking reserved-name
inventory, metadata/readiness, dry-run planning, version/tag policy, and PDFium boundary blockers.
The public-facing readiness ledger keeps the current-main refresh candidate and package publication
resolution gaps explicit without approving package publication or public installation.
The public beta current-main refresh prep record keeps refreshed source approval blocked while
recording the exact current-main source candidate and required follow-up evidence.

- `advisory-scan-2026-06-16.md` - full `cargo-deny` advisory, ban, license, and source scan
  passed with a sidecar Rust 1.94 toolchain and `cargo-deny 0.19.9`; release artifacts still
  need artifact-specific license/NOTICE bundles and package-specific readiness work.
- `claim-language-scan-2026-06-15.md` - current README/docs/examples/benchmark wording was
  scanned for unsupported public claims; README wording was narrowed to avoid speed,
  footprint, table, and heading overclaims.
- `ethos-bench-hygiene-2026-06-15.md` - sibling `ethos-bench` repo hygiene files were verified
  and its local unit/smoke checks passed.
- `h1-public-safe-comparison-closeout-2026-06-20.md` - H1 public-safe competitor comparison
  evidence was accepted for closeout after `ethos-bench` publication preflight, tests, smoke,
  readiness, public-safety audit, claim audit, attestation audit, evidence-tree review, and
  benchmark-owner approval; the record closes only H1 evidence review and does not approve public
  benchmark claims, public benchmark reports, release artifacts, package publication, production
  positioning, hosted surfaces, or wording beyond the exact approved pre-alpha sentence.
- `h2-source-snapshot-scope-approval-2026-06-20.md` - H2 artifact scope approval is limited to
  `source-snapshot` only after review of the release notice draft; the record does not approve
  binaries, wheels, npm packages, crate publication, hosted surfaces, public benchmark reports, or
  wording beyond the exact approved pre-alpha sentence.
- `h2-source-snapshot-candidate-evidence-2026-06-20.md` - H2 source-snapshot candidate evidence
  is recorded for source HEAD `60abfd4`, archive SHA256
  `9ae9f40e8385035101bae1b947a6894bcdaf4c7ffb852faef73cb0755452ac51`, extracted file count
  `497`, source-snapshot candidate audit, blocked-artifact scan, public-surface posture checks,
  public pre-alpha wording approval checks, claims gate, and diff hygiene; closeout is recorded
  separately for the exact source-snapshot candidate and surface.
- `h2-source-snapshot-closeout-2026-06-20.md` - H2 is closed for the exact source-snapshot
  candidate at source HEAD `60abfd4`, archive SHA256
  `9ae9f40e8385035101bae1b947a6894bcdaf4c7ffb852faef73cb0755452ac51`, and
  source-snapshot-only surface; binaries, wheels, npm packages, crate publication, hosted
  surfaces, public benchmark reports, public beta, production positioning, and wording beyond the
  exact approved pre-alpha sentence remain blocked.
- `h2-source-snapshot-candidate-evidence-660f268-2026-06-20.md` - refreshed H2 source-snapshot
  candidate evidence is recorded for approved candidate source HEAD `660f268`, archive SHA256
  `58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87`, extracted file count
  `501`, source-snapshot candidate audit, blocked-artifact scan, untracked/build-path scan,
  public-surface posture checks, public pre-alpha wording approval checks, claims gate, and diff
  hygiene; closeout is recorded separately for the exact source-snapshot candidate and surface.
- `h2-source-snapshot-closeout-660f268-2026-06-20.md` - H2 is closed for the exact
  source-snapshot candidate at source HEAD `660f268`, archive SHA256
  `58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87`, and
  source-snapshot-only surface; binaries, wheels, npm packages, crate publication, hosted
  surfaces, public benchmark reports, public beta, production positioning, and wording beyond the
  exact approved pre-alpha sentence remain blocked.
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
- `milestone-e-public-approval-lane-blockers-validation-2026-06-20.md` - internal Milestone E
  public approval lane blocker validation for
  `docs/milestone-e-public-approval-lane-blockers.json` passed through approval-lane ledger checks,
  schema validation, validation-record checks, public-surface posture checks, `make
  milestone-e-prep`, and diff hygiene; the record covers only blocker prep for public beta,
  package publication, hosted surface, production positioning, and public benchmark report lanes,
  and does not approve any lane.
- `milestone-e-public-beta-approval-prep-validation-2026-06-20.md` - internal Milestone E
  public beta approval prep validation for `docs/milestone-e-public-beta-approval-prep.json`
  passed through public beta approval prep checks, schema validation, validation-record checks,
  public-surface posture checks, `make milestone-e-prep`, and diff hygiene; the record starts
  required-evidence and blocker prep only, keeps public beta blocked, and does not approve public
  beta.
- `milestone-e-public-beta-approval-decision-validation-2026-06-20.md` - internal Milestone E
  public beta required-evidence validation for the dedicated public beta approval decision review;
  the record keeps public beta blocked, does not approve public beta, and records that exact
  wording and surface signoff are not granted.
- `milestone-e-public-beta-release-scope-engineering-blocker-review-validation-2026-06-20.md` -
  internal Milestone E public beta required-evidence validation for release-scope engineering
  blocker review; the record keeps public beta blocked and does not approve public beta.
- `milestone-e-public-beta-public-setup-path-review-validation-2026-06-20.md` - internal Milestone E
  public beta required-evidence validation for public setup path review; the record keeps public
  beta blocked and does not approve public beta.
- `milestone-e-public-beta-pdfium-build-path-review-validation-2026-06-20.md` - internal Milestone E
  public beta required-evidence validation for Phase 2 PDFium build-path review; the record keeps
  public beta blocked and does not approve public beta.
- `milestone-e-public-beta-source-only-approval-validation-2026-06-20.md` - source-only public beta
  approval validation for the GitHub source repository surface; the record approves only
  source-only evaluation for reviewed commit `d755e7c` and merged main commit `3f9e1c4`, while
  keeping package publication, hosted surfaces, production positioning, public benchmark reports,
  public benchmark claims, release artifacts, binaries, wheels, npm packages, crate publication,
  project-maintained PDFium builds, public reports, and public result wording blocked.
- `milestone-e-package-publication-approval-prep-validation-2026-06-20.md` - internal Milestone E
  package publication approval prep validation for
  `docs/milestone-e-package-publication-approval-prep.json` passed through package publication
  approval prep checks, schema validation, validation-record checks, public-surface posture checks,
  `make milestone-e-prep`, and diff hygiene; the record starts required-evidence and blocker prep
  only, keeps package publication blocked, and does not approve package publication.
- `milestone-e-package-publication-prep-approval-validation-2026-06-20.md` - package publication
  prep approval validation for the five ADR-0006 reserved priority crates.io identifiers; the
  record approves internal prep only, keeps real-version cargo publish and public installation
  blocked, and keeps wheels, npm packages, binaries, hosted surfaces, production positioning,
  public benchmark reports, public benchmark claims, release artifacts, and project-maintained
  PDFium builds blocked.
- `milestone-e-package-publication-inventory-reconciliation-validation-2026-06-20.md` - package
  publication evidence validation for ADR-0006 reserved-name to source-tree workspace
  reconciliation; the record keeps package publication and public installation blocked.
- `milestone-e-package-publication-metadata-readiness-validation-2026-06-20.md` - package
  publication evidence validation for metadata, license, NOTICE, and README readiness; the record
  keeps per-crate README, package metadata, and NOTICE packaging blockers explicit.
- `milestone-e-package-publication-dry-run-smoke-plan-validation-2026-06-20.md` - package
  publication evidence validation for the future dry-run and smoke-build path; the record does not
  run or approve real-version `cargo publish`.
- `milestone-e-package-publication-version-tag-policy-validation-2026-06-20.md` - package
  publication evidence validation for version and tag policy; the record keeps workspace `0.1.0`
  and crates.io `0.0.0-reserved.0` reservations unreconciled for publication.
- `milestone-e-package-publication-pdfium-boundary-validation-2026-06-20.md` - package
  publication evidence validation for the `ethos-pdf` PDFium boundary; the record keeps
  `ethos-pdf` held out unless no bundled PDFium binary and no public PDFium types can be
  guaranteed.
- `milestone-e-package-publication-metadata-readiness-closeout-validation-2026-06-21.md` - package
  publication metadata readiness validation for the current in-tree priority candidate crates; the
  record keeps package publication and public installation blocked while recording README, NOTICE,
  manifest metadata, and include-list readiness for `ethos-core`, `ethos-verify`, and `ethos-pdf`.
- `milestone-e-package-publication-dry-run-smoke-closeout-validation-2026-06-21.md` - package
  publication dry-run/smoke validation for the current source-tree candidate path; the record keeps
  package publication and public installation blocked while recording local package assembly for
  `ethos-core`, source-tree checks for `ethos-verify` and `ethos-pdf`, and retained dependent
  package assembly blockers.
- `milestone-e-package-publication-version-tag-policy-closeout-validation-2026-06-21.md` - package
  publication version/tag policy validation for the current source-tree candidate path; the record
  keeps package publication and public installation blocked while recording source-tree version,
  reserved placeholder version, source snapshot tag, and future package tag namespace separation.
- `milestone-e-package-publication-pdfium-boundary-closeout-validation-2026-06-21.md` - package
  publication PDFium boundary validation for the current source-tree `ethos-pdf` path; the record
  keeps package publication and public installation blocked while recording no bundled PDFium
  binary, caller-provided PDFium loading, and no raw PDFium FFI types across public schemas/APIs.
- `milestone-e-package-publication-dependency-ordering-closeout-validation-2026-06-21.md` -
  package publication dependency-ordering validation for future dependent-candidate review; the
  record keeps package publication and public installation blocked while recording that
  `ethos-doc-core` must precede `ethos-verify` and `ethos-pdf` in any later dedicated publication
  approval.
- `milestone-e-package-publication-manifest-migration-prep-validation-2026-06-21.md` - package
  publication manifest-migration prep validation for a future core package-name migration and
  workspace dependency alias; the record keeps package publication and public installation blocked
  while recording that current Cargo manifests remain unchanged.
- `milestone-e-package-publication-manifest-activation-prep-validation-2026-06-21.md` - package
  publication manifest-activation prep validation for future package dependency manifest review;
  the record keeps package publication and public installation blocked while recording that no
  Cargo manifest is changed.
- `milestone-e-package-publication-registry-assembly-prep-validation-2026-06-21.md` - package
  publication registry-assembly prep validation for future non-public dependent candidate assembly
  rehearsal; the record keeps package publication and public installation blocked while recording
  that no registry is created and current Cargo manifests remain unchanged.
- `milestone-e-package-publication-registry-assembly-activation-prep-validation-2026-06-21.md` -
  package publication registry-assembly activation prep validation for future dependent package
  assembly activation review; the record keeps package publication and public installation blocked
  while recording that no registry-backed assembly is activated.
- `milestone-e-package-publication-real-version-selection-prep-validation-2026-06-21.md` -
  package publication real-version-selection prep validation for future SemVer candidate review;
  the record keeps package publication and public installation blocked while recording that no
  package publication version is selected.
- `milestone-e-package-publication-tag-creation-prep-validation-2026-06-21.md` - package
  publication tag-creation prep validation for future package tag review; the record keeps package
  publication and public installation blocked while recording that no package tag is created.
- `milestone-e-package-publication-decision-bundle-validation-2026-06-21.md` - package
  publication decision-bundle validation for the combined decision inputs; the record keeps
  package publication and public installation blocked while recording that no package publication
  version is selected, no package tag is created, no Cargo manifest is changed, no registry is
  created, no registry-backed assembly is activated, and no public installation is invited.
- `milestone-e-package-publication-pre-approval-gap-ledger-validation-2026-06-21.md` - package
  publication pre-approval gap-ledger validation for the unresolved package publication approval
  inputs; the record keeps package publication and public installation blocked while recording the
  missing version map, package tag, source binding, manifest activation diff, registry-backed
  assembly evidence, public installation wording, and posture/claims rerun requirements.
- `milestone-e-package-publication-approval-resolution-plan-validation-2026-06-21.md` - package
  publication approval resolution-plan validation for the package publication approval resolution
  plan and current gap ledger; the resolution plan record binds the future exact decision review
  to current source commit `524535a` / tree
  `0785ffca8423c42e2c4105df7752e290cc88e5c2`, orders the remaining version, tag, manifest,
  registry-backed assembly, public installation wording, and posture/claims inputs, and records
  that package publication remains blocked and public installation remains blocked.
- `milestone-e-package-publication-decision-input-packet-validation-2026-06-21.md` - package
  publication decision-input packet validation for the package publication decision input packet;
  the record binds candidate
  version, tag, source, manifest, assembly, and wording inputs to source commit `54bf70f` / tree
  `5a197bee718e3b31399563340169e9efd4f1317c` while package publication remains blocked and
  public installation remains blocked.
- `milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md` - package
  publication approval-readiness review validation for the package publication approval readiness
  review; the record summarizes present decision inputs and remaining approval blockers for source
  commit `9054f1c` / tree `3f8cb66249826d67ab6030032c7784a2a4ff411b` while package publication
  remains blocked and public installation remains blocked.
- `milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md` -
  package publication manifest-activation diff review validation for the candidate manifest
  activation diff; the record binds the reviewed diff inputs to source commit `89d24c8` / tree
  `21b263dca908ef7cc977e7669e40206096eef93e` while package publication remains blocked and
  public installation remains blocked.
- `milestone-e-package-publication-registry-assembly-evidence-review-validation-2026-06-21.md` -
  package publication registry-assembly evidence review validation for the registry-backed
  dependent package assembly evidence requirements; the record binds the requirements to source
  commit `3f0f3ed` / tree `6c748cd6f4a8de7789e42666697d1f25aa99f6f9` while package publication
  remains blocked and public installation remains blocked.
- `milestone-e-package-publication-public-installation-wording-review-validation-2026-06-21.md` -
  package publication public installation wording review validation for candidate wording and
  explicit exclusions; the record binds the wording review to source commit `8b446e3` / tree
  `385dd7799cf898fc850555ce13d6d74e8ee15196` while package publication remains blocked and
  public installation remains blocked.
- `milestone-e-package-publication-approval-decision-template-validation-2026-06-21.md` -
  package publication approval decision template validation for exact future decider inputs; the
  record binds the not-approved template to source commit `66979cc` / tree
  `58ef15e1cac8ce7df35a7e88da2044e57eb66c10` while package publication remains blocked and
  public installation remains blocked.
- `milestone-e-package-publication-approval-decision-validation-2026-06-21.md` -
  package publication approval decision validation for the current package-publication request; the
  record binds the rejected decision to source commit `fdbd5b7` / tree
  `4a7bf5cda2c779e41a04c3feb691a12fec1e5c8d` while package publication remains blocked and
  public installation remains blocked.
- `milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md` -
  package publication candidate activation evidence validation for a temporary non-public package
  activation workspace; the record binds the evidence to source commit `6cf211c` / tree
  `ae76bc588b64dc1e8087d9096d52545a3560c2c0` while package publication remains blocked and
  public installation remains blocked.
- `milestone-e-package-publication-approval-decision-refresh-validation-2026-06-22.md` -
  package publication approval decision refresh validation after candidate activation evidence is
  present; the record binds the refresh to source commit `6a91511` / tree
  `8b150d9aebdc282c358e4552a4d709c3140f41b4`, records that manual exact approval remains
  required, and keeps package publication and public installation blocked.
- `milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md` -
  package publication manifest activation applied validation for the source package name
  `ethos-doc-core`, Rust library name `ethos_core`, workspace dependency activation, and retained
  `publish = false` blockers; package publication and public installation remain blocked.
- `milestone-e-public-facing-readiness-ledger-validation-2026-06-21.md` - public-facing readiness
  ledger validation recorded `docs/milestone-e-public-facing-readiness-ledger.json` as a
  current-main refresh candidate and package-publication gap-retention artifact; current main
  `847e12d` / tree `9d3701aa14d98017626583c2a0a0ef45ac0df79f` is not treated as a refreshed
  reviewed source-only public beta source state, and package publication remains blocked.
- `milestone-e-public-beta-current-main-refresh-prep-validation-2026-06-21.md` - public beta
  current-main refresh prep validation recorded
  `docs/milestone-e-public-beta-current-main-refresh-prep.json` as a current-main refresh
  candidate artifact for commit `9262b28` / tree `9f18f9e40c57551aef9b0cb2a53641c87207546b`;
  refreshed reviewed source-only public beta state, public installation, and package publication
  remain blocked.
- `milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md` -
  current-main source-only public beta approval validation recorded reviewed commit `902c423`,
  merged main commit `6019a97`, and tree `f56fde854f6f6e4c4070209329f8c7b12310aa51` as the
  refreshed GitHub source-repository public beta source binding; package publication, public
  installation, hosted surfaces, production positioning, public benchmark reports, public
  benchmark claims, release artifacts, binaries, wheels, npm packages, crate publication,
  project-maintained PDFium builds, public reports, and public result wording remain blocked.
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
- `milestone-e-final-closeout-validation-2026-06-20.md` - final internal Milestone E source-only
  prep closeout passed through prep validation-record checks, validation-record source-head checks,
  validation-record index checks, guard-sequence index checks, public-surface posture checks, `make
  milestone-e-prep`, and diff hygiene; the record covers only the current source-only prep boundary
  and does not resolve or soften blockers.
- `public-evidence-scan-2026-06-15.md` - tracked evidence and benchmark-result locations were
  scanned for private paths, hostnames, and generated Gate Zero output that belongs in
  `ethos-bench`.
- `public-prealpha-wording-approval-2026-06-20.md` - product approval for the exact source-only
  pre-alpha public sentence passed through manual `ethos-bench` evidence-hygiene review, source
  public-surface posture checks, claims gate, and diff hygiene; the record does not approve public
  benchmark reports, release artifacts, package publication, production positioning, hosted
  surfaces, or altered public wording.
- `release-readiness-next-steps-approval-2026-06-20.md` - product approval for the five-step
  next execution sequence from H1 through release-candidate validation gates; the record does not
  close H1/H2 and does not approve public benchmark reports, release artifacts, package
  publication, production positioning, hosted surfaces, or wording beyond the exact approved
  pre-alpha sentence.
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
