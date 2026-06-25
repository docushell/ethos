# Validation Records

This directory stores dated evidence records for validation runs that affect Ethos product
claims or determinism boundaries.

Human-written validation records should avoid private usernames, hostnames, and one-off absolute
paths unless the path itself is the subject under test. Preserve commit ids, hashes, commands,
and pass/fail conclusions. Generated benchmark result files follow the evidence-handling policy
in `docs/public-release-checklist.md`.

Records:

Patch `0.1.2` closeout records now document the approved public beta/evaluation npm package and
macOS arm64/Linux x64 CLI artifact surfaces, while Rust crate and Python wheel install wording
remain on the published `0.1.1` baseline. Patch `0.1.1` closeout records document the approved
public beta/evaluation surfaces for source, Rust crates, the Python wheel, npm package, and macOS
arm64/Linux x64 CLI artifacts. Historical package publication evidence records below keep their
at-the-time blocker wording for traceability.
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
- `milestone-e-package-publication-current-dry-run-smoke-validation-2026-06-22.md` - package
  publication dry-run/smoke validation refresh after source manifest activation; the record keeps
  package publication and public installation blocked while recording local package assembly for
  `ethos-doc-core`, source-tree checks for `ethos-verify` and `ethos-pdf`, and the separate
  registry-equivalent dependent package assembly evidence boundary.
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
- `milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md` - package
  publication current registry-equivalent assembly validation after source manifest activation; the
  record keeps package publication and public installation blocked while recording non-public
  assembly evidence for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`.
- `milestone-e-package-publication-final-approval-request-validation-2026-06-22.md` - package
  publication final approval request validation; the record keeps package publication and public
  installation blocked while recording exact candidate crates, version map, package tag names,
  source binding, proposed public installation wording, and explicit exclusions for decider review.
- `milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md` - package
  publication final approval decision validation; the record accepts the exact bounded candidate
  crates, version map, tag names, source binding, wording, and exclusions while recording that
  publish-flag activation remains blocked, package tag creation remains blocked, real-version
  cargo publish remains blocked, and public installation instructions remain a later gated action.
- `milestone-e-package-publication-publish-flag-activation-request-validation-2026-06-22.md` -
  package publication publish-flag activation request validation; the record captures the exact
  requested activation diff for the three accepted candidate manifests while keeping activation
  blocked, recording that package tag source binding must be refreshed after activation, and
  keeping tag creation, real-version cargo publish, and public installation instructions blocked.
- `milestone-e-package-publication-activation-applied-validation-2026-06-22.md` - package
  publication activation applied validation; the record binds the applied manifest activation to
  source commit `f50f294` / tree `00c3e4df7a7b3b368659650601a2df76b63a2ce8`, records that only
  the three accepted candidate manifests changed, records that non-candidate crates stay blocked,
  and keeps package tag source binding refresh, real-version cargo publish, and public
  installation instructions blocked.
- `milestone-e-package-publication-tag-binding-refresh-validation-2026-06-22.md` - package
  publication tag binding refresh validation; the record refreshes the package tag source binding
  to activated main commit `421bed8` / tree `aa0d5d31d879540fd0044052dfeb747f12b64204`, keeps
  package tag creation and registry publication blocked, and records that operator evidence
  remains required while public installation remains blocked.
- `milestone-e-package-publication-operator-preflight-validation-2026-06-22.md` - package
  publication operator preflight validation; the record lists manual crates.io owner/account
  evidence, reserved-name confirmation, dependency order, package tag names, and command order for
  a later registry action while recording that manual registry evidence remains required and public
  installation remains blocked.
- `milestone-e-package-publication-manual-registry-evidence-request-validation-2026-06-22.md` -
  package publication manual registry evidence request validation; the record provides the exact
  non-secret evidence output packet for crates.io owner/account confirmation, reserved-name owner
  outputs, dry-run outputs, package tag names, and explicit exclusions while keeping package tag
  creation, registry publication, and public installation blocked.
- `milestone-e-package-publication-manual-registry-evidence-supplied-validation-2026-06-22.md` -
  package publication manual registry evidence supplied validation; the record captures the
  non-secret crates.io owner/account evidence, reserved-name owner outputs, dry-run output for
  `ethos-doc-core`, expected blocked dependent dry-run outputs, package tag names, and explicit
  exclusions while keeping package tag creation blocked; registry publication remains blocked,
  and public installation remains blocked.
- `milestone-e-package-publication-registry-action-authorization-request-validation-2026-06-22.md` -
  package publication registry action authorization request validation; the record provides the
  exact non-secret authorization packet and command order for later package tag creation and the
  first registry action while recording that package tag creation remains blocked, registry
  publication remains blocked, and public installation remains blocked.
- `milestone-e-package-publication-registry-action-approval-validation-2026-06-22.md` - package
  publication registry action approval validation; the record captures exact bounded authorization
  for the three annotated package tags and first `ethos-doc-core` registry action while recording
  that dependent registry actions remain blocked and public installation remains blocked.
- `milestone-e-package-publication-registry-action-evidence-validation-2026-06-22.md` - package
  publication registry action evidence validation; the record captures tag evidence, first
  `ethos-doc-core` registry action evidence, and refreshed dependent dry-run evidence while
  recording that dependent registry actions remain blocked and public installation remains blocked.
- `milestone-e-package-publication-dependent-registry-action-approval-validation-2026-06-22.md` -
  package publication dependent registry action approval validation; the record authorizes only the
  dependent `ethos-verify` and `ethos-pdf` registry actions while recording that public
  installation remains blocked.
- `milestone-e-package-publication-dependent-registry-action-evidence-validation-2026-06-22.md` -
  package publication dependent registry action evidence validation; the record captures completed
  `ethos-verify` and `ethos-pdf` registry action evidence while recording that public installation
  wording remains blocked.
- `milestone-e-package-publication-public-installation-availability-validation-2026-06-22.md` -
  package publication public installation availability validation; the record captures crates.io
  availability for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.0` and bounds Rust
  crate installation wording while retaining CLI, wheel, npm, binary, hosted, production, public
  benchmark, PDFium-build, `ethos-doc`, and `ethos-rag` blockers.
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
- `milestone-e-public-evaluation-current-state-closeout-validation-2026-06-22.md` - public
  evaluation current-state closeout validation recorded current main `034881e` / tree
  `fb089e027641a7d2152d7d1ebd499f45bb1f6a1c` as GitHub source repository plus
  `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.0` for Rust crate evaluation; CLI,
  wheel, npm, binary, hosted, production, public benchmark, project-maintained PDFium-build,
  `ethos-doc`, `ethos-rag`, and broader public wording blockers remain explicit.
- `first-public-release-scope-decision-validation-2026-06-22.md` - first public release scope
  decision validation starts release preparation for draft CLI artifacts, Python package
  preparation, and npm binary package preparation on macOS arm64 and Linux x64 with
  caller-provided PDFium; public artifact publication remains blocked, and hosted, production,
  public benchmark, Windows x64, bundled PDFium, `ethos-doc`, and `ethos-rag` blockers remain
  explicit.
- `first-public-release-launch-copy-audit-template-2026-06-22.md` - launch copy audit template
  records the required sentence-level evidence mapping for future first public release wording; no
  launch wording is approved, and hosted, production, public benchmark, Windows x64, bundled
  PDFium, `ethos-doc`, and `ethos-rag` blockers remain explicit.
- `first-public-release-artifact-evidence-validation-2026-06-23.md` - first public release
  artifact evidence validation records release-candidate prep, macOS arm64 draft CLI artifact,
  Python wheel, and npm package evidence while recording build/package caveats; public artifact
  publication remains blocked, and launch wording, hosted, production, public benchmark, Windows
  x64, bundled PDFium, `ethos-doc`, and `ethos-rag` blockers remain explicit.
- `first-public-release-final-decider-validation-2026-06-23.md` - first public release final
  decider validation approves only the evidenced macOS arm64 CLI artifact and Python wheel
  evaluation surfaces, records the exact approved launch wording, and keeps Linux x64 CLI artifact
  publication blocked; npm publication remains blocked, and hosted, production, public benchmark,
  Windows x64, bundled PDFium, `ethos-doc`, and `ethos-rag` blockers remain explicit.
- `first-public-release-macos-artifact-publication-reconciliation-validation-2026-06-23.md` -
  first public release macOS artifact publication reconciliation records the discrepancy between
  checked-in local draft checksum evidence and the handoff-reported published GitHub Release
  checksum; Linux x64 CLI artifact publication remains blocked until the published macOS release
  asset checksum sidecars are operator-verified and cited in Linux evidence.
- `first-public-release-linux-x64-workflow-evidence-validation-2026-06-23.md` - first public
  release Linux x64 workflow evidence validation records that release workflow run `28004938177`
  passed the Linux x64 draft artifact job and runtime smoke step, while keeping Linux x64
  publication blocked until the uploaded artifact bytes, checksum, inventory, and smoke sidecar are
  retrieved and recorded.
- `first-public-release-linux-x64-artifact-evidence-validation-2026-06-23.md` - first public
  release Linux x64 artifact evidence validation records the downloaded workflow artifact,
  `ethos-linux-x64.tar.gz` SHA256, inventory, smoke sidecar, archive contents, and operator-verified
  published macOS checksum; Linux x64 publication remains blocked until the final decider record.
- `first-public-release-linux-x64-final-decider-validation-2026-06-23.md` - first public release
  Linux x64 final decider validation approves only attaching the exact evidenced Linux x64 CLI
  artifact assets to existing GitHub Release `v0.1.0` for evaluation, updates bounded launch
  wording to include Linux x64, and keeps npm, hosted, production, public benchmark, Windows x64,
  bundled PDFium, `ethos-doc`, and `ethos-rag` blockers explicit.
- `first-public-release-linux-x64-publication-closeout-validation-2026-06-23.md` - first public
  release Linux x64 publication closeout validation records successful upload of the four approved
  Linux x64 assets to GitHub Release `v0.1.0`, verifies the release asset list, and closes the
  bounded first public evaluation release for approved source, Rust crate, Python wheel, macOS
  arm64 CLI artifact, and Linux x64 CLI artifact surfaces.
- `npm-vendor-binary-payload-strategy-validation-2026-06-23.md` - npm vendor binary payload
  strategy validation records the local package contract for assembling approved macOS arm64 and
  Linux x64 CLI release archives into `@docushell/ethos-pdf` `vendor/` binaries, including checksum
  validation, target selection, and `npm pack` inclusion checks; npm publication remains blocked
  until a dedicated decider binds the exact assembled npm tarball, source commit, package version,
  vendor payload checksums, and public wording.
- `npm-tarball-candidate-evidence-validation-2026-06-23.md` - npm tarball candidate evidence
  validation records the exact local `@docushell/ethos-pdf@0.1.0` candidate assembled from approved
  macOS arm64 and Linux x64 release artifacts, including vendor binary checksums, `npm pack`
  metadata, tarball SHA256, packed file list, install smoke, and missing-PDFium exit `12`; npm
  publication remains blocked until a dedicated decider approves `npm publish`.
- `npm-publication-final-approval-request-validation-2026-06-23.md` - npm publication final
  approval request validation records the exact `@docushell/ethos-pdf@0.1.0` candidate package,
  npm shasum, tarball SHA256, integrity, vendor payload checksums, installed CLI smoke, PDFium
  boundary, and retained blockers for decider review; npm publish remains blocked until a separate
  approval decision and explicit operator action with npm credentials.
- `npm-publication-final-approval-decision-validation-2026-06-23.md` - npm publication final
  approval decision validation accepts the exact `@docushell/ethos-pdf@0.1.0` bounded npm candidate
  after the provenance blocker was resolved, binds the Node.js `v23.11.1` and npm `10.9.2`
  toolchain-qualified tarball metadata plus durable per-file vendor SHA256 values, keeps unrelated
  blockers explicit, and leaves operator publish pending as a separate credentialed action.
- `npm-publication-closeout-validation-2026-06-23.md` - npm publication closeout validation records
  successful publication of `@docushell/ethos-pdf@0.1.0`, registry verification for version,
  shasum, integrity, file count, unpacked size, npm's publish-time bin-name auto-correction warning,
  and retained blockers for hosted, production, Windows, bundled PDFium, `ethos-doc`, `ethos-rag`,
  and public benchmark surfaces.
- `patch-0-1-1-readiness-prep-validation-2026-06-23.md` - patch 0.1.1 readiness prep validation
  records candidate onboarding contents after `ethos doctor`, synthetic fixture golden-change
  guarding, the 2-minute PDF parse quickstart, and improved missing/unusable PDFium guidance landed
  on `main`; no release, tag, version bump, package publish, GitHub Release artifact, hosted
  surface, production positioning, Windows packaged artifact, bundled project-maintained PDFium
  build, public benchmark report, or public benchmark claim is approved.
- `patch-0-1-1-release-artifact-evidence-validation-2026-06-23.md` - patch 0.1.1 release artifact
  evidence validation records the green release workflow run, downloaded macOS arm64 and Linux x64
  draft CLI artifacts, matching SHA256 sidecars, inventory status `draft_not_release_ready`,
  `publication: blocked`, and smoke evidence showing `ethos 0.1.1`; it does not approve GitHub
  Release publication, npm vendor refresh, npm publication, hosted surfaces, production
  positioning, Windows packaged artifacts, bundled project-maintained PDFium, or public benchmark
  claims.
- `patch-0-1-1-artifact-publication-approval-request-validation-2026-06-23.md` - patch 0.1.1
  artifact publication approval request validation binds the exact requested macOS arm64 and Linux
  x64 GitHub Release `v0.1.1` artifact names, SHA256 values, source commit, workflow evidence, and
  bounded public wording for decider review while keeping publication, npm vendor refresh, npm
  publication, hosted surfaces, production positioning, Windows packaged artifacts, bundled
  project-maintained PDFium, and public benchmark claims blocked.
- `patch-0-1-1-artifact-publication-approval-decision-validation-2026-06-23.md` - patch 0.1.1
  artifact publication approval decision validation accepts only the exact evidenced macOS arm64
  and Linux x64 GitHub Release `v0.1.1` artifact assets and bounded public wording while leaving
  operator upload, post-upload closeout evidence, npm vendor refresh, npm publication, hosted
  surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium,
  and public benchmark claims blocked.
- `patch-0-1-1-artifact-publication-closeout-validation-2026-06-23.md` - patch 0.1.1 artifact
  publication closeout validation records GitHub Release `v0.1.1`, approved tag target, exact
  published macOS arm64 and Linux x64 assets, matching checksums, sidecars, archive payloads,
  macOS smoke output, bounded release wording, and retained blockers; npm vendor refresh and npm
  publication remain separate blocked lanes.
- `patch-0-1-1-npm-vendor-refresh-validation-2026-06-23.md` - patch 0.1.1 npm vendor refresh
  validation records the checked-in `@docushell/ethos-pdf@0.1.1` vendor payload refreshed from
  published GitHub Release `v0.1.1` assets, per-file vendor SHA256 values, local `npm pack`
  metadata, install smoke, missing-PDFium behavior, and retained publication blockers.
- `patch-0-1-1-npm-publication-approval-request-validation-2026-06-23.md` - patch 0.1.1 npm
  publication approval request validation binds the exact `@docushell/ethos-pdf@0.1.1` npm
  candidate, toolchain-qualified tarball hashes, durable vendor payload checksums, installed CLI
  smoke, PDFium boundary, and retained blockers for decider review; npm publish remains blocked.
- `patch-0-1-1-npm-publication-approval-decision-validation-2026-06-23.md` - patch 0.1.1 npm
  publication approval decision validation accepts the exact `@docushell/ethos-pdf@0.1.1` bounded
  npm candidate, binds the Node.js `v23.11.1` and npm `10.9.2` toolchain-qualified tarball
  metadata plus durable per-file vendor SHA256 values, keeps unrelated blockers explicit, and
  leaves operator publish pending as a separate credentialed action.
- `patch-0-1-1-npm-publication-closeout-validation-2026-06-24.md` - patch 0.1.1 npm publication
  closeout validation records successful publication of `@docushell/ethos-pdf@0.1.1`, registry
  verification for version, latest tag, shasum, integrity, file count, unpacked size, npm's
  publish-time bin-name auto-correction warning, and retained blockers.
- `patch-0-1-1-crates-publication-approval-request-validation-2026-06-24.md` - patch 0.1.1
  crates.io publication approval request validation binds the exact `ethos-doc-core`,
  `ethos-verify`, and `ethos-pdf` `0.1.1` crate set, source commit, package tag names, local crate
  artifact hashes, publish order, and retained blockers for decider review; `cargo publish`
  remains blocked.
- `patch-0-1-1-crates-publication-approval-decision-validation-2026-06-24.md` - patch 0.1.1
  crates.io publication approval decision validation accepts the exact `ethos-doc-core`,
  `ethos-verify`, and `ethos-pdf` `0.1.1` crate set, package source binding, package tag names,
  dependency-ordered operator commands, and retained blockers; operator publish remains pending.
- `patch-0-1-1-crates-publication-closeout-validation-2026-06-24.md` - patch 0.1.1 crates.io
  publication closeout validation records successful crates.io publication and live registry
  verification for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` `0.1.1`, while keeping public
  installation wording and unrelated public/support surfaces blocked.
- `patch-0-1-1-python-publication-approval-request-validation-2026-06-24.md` - patch 0.1.1
  Python PyPI publication approval request validation binds the exact `ethos-pdf==0.1.1` wheel,
  source commit, wheel metadata, wheel SHA256, local install/import smoke, and retained blockers
  for decider review; PyPI upload remains blocked.
- `patch-0-1-1-python-publication-approval-decision-validation-2026-06-24.md` - patch 0.1.1
  Python PyPI publication approval decision validation accepts the exact `ethos-pdf==0.1.1` wheel
  candidate, source binding, wheel metadata, SHA256, and retained blockers; operator upload remains
  pending.
- `patch-0-1-1-python-wheel-reproducibility-blocker-validation-2026-06-24.md` - patch 0.1.1
  Python wheel reproducibility blocker validation records that a fresh standard pre-upload rebuild
  did not match the approved wheel SHA256 because generated ZIP timestamps drifted; PyPI upload
  remains blocked pending a deterministic wheel approval request and decision.
- `patch-0-1-1-python-deterministic-wheel-approval-request-validation-2026-06-24.md` - patch
  0.1.1 Python deterministic wheel approval request validation binds the exact
  `SOURCE_DATE_EPOCH=0` `ethos-pdf==0.1.1` wheel candidate, source commit, wheel metadata,
  deterministic SHA256, local install/import smoke, and retained blockers for decider review; PyPI
  upload remains blocked.
- `patch-0-1-1-python-deterministic-wheel-approval-decision-validation-2026-06-24.md` - patch
  0.1.1 Python deterministic wheel approval decision validation accepts the exact
  `SOURCE_DATE_EPOCH=0` `ethos-pdf==0.1.1` wheel candidate, source binding, wheel metadata,
  deterministic SHA256, and retained blockers; operator upload remains pending.
- `patch-0-1-1-python-publication-closeout-validation-2026-06-24.md` - patch 0.1.1
  Python PyPI publication closeout validation records successful publication of the exact
  deterministic `ethos-pdf==0.1.1` wheel and live PyPI registry verification while keeping public
  installation wording in a separate bounded docs lane.
- `patch-0-1-1-public-install-wording-closeout-validation-2026-06-24.md` - patch 0.1.1
  public installation wording closeout validation documents published evaluation install paths for
  Rust crates, the Python wheel, npm package, and GitHub Release CLI artifacts while retaining
  hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` blockers.
- `patch-0-1-1-execution-status-refresh-validation-2026-06-24.md` - patch 0.1.1 execution
  status refresh validation updates the current execution-status summary and PM rule for published
  evaluation surfaces while retaining hosted, production, Windows, bundled PDFium, benchmark,
  `ethos-doc`, and `ethos-rag` blockers.
- `patch-0-1-2-readiness-prep-validation-2026-06-24.md` - patch 0.1.2 readiness prep validation
  records the narrow beta patch candidate boundary after `ethos evidence anchor`, the
  `evidence_anchor` v1 guard, and professional public README status wording landed, while keeping
  the current public install baseline at `0.1.1` and leaving release, tag, publication, GitHub
  Release artifact, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and
  `ethos-rag` surfaces unapproved.
- `patch-0-1-2-version-activation-validation-2026-06-24.md` - patch 0.1.2 version activation
  validation records Rust workspace and Python source/package metadata at `0.1.2`, keeps npm and
  public install wording on the published `0.1.1` baseline until matching CLI artifacts and
  publication evidence exist, and leaves release, tag, publication, GitHub Release artifact,
  hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces
  unapproved.
- `patch-0-1-2-artifact-package-evidence-validation-2026-06-24.md` - patch 0.1.2
  artifact/package evidence validation dynamically checks `0.1.2` Rust crate candidates and the
  `ethos_pdf-0.1.2-py3-none-any.whl` candidate, updates draft CLI artifact workflow smoke
  expectations to `ethos 0.1.2`, and keeps npm at `0.1.1`, public install wording blocked,
  registry publication blocked, GitHub Release artifact publication blocked, hosted, production,
  Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces unapproved.
- `patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md` - patch 0.1.2 draft artifact
  evidence validation records the green `release.yml` workflow run and downloaded macOS arm64 and
  Linux x64 draft CLI artifact sidecars, with smoke output `ethos 0.1.2`, while keeping GitHub
  Release artifact publication, registry publication, npm vendor refresh, public install wording,
  hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces
  blocked.
- `patch-0-1-2-artifact-publication-approval-request-validation-2026-06-24.md` - patch 0.1.2
  artifact publication approval request binds the exact macOS arm64 and Linux x64 draft CLI
  artifact names, SHA256 values, source commit, workflow evidence, and requested bounded wording
  for decider review while keeping publication, registry, npm vendor refresh, public install
  wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag`
  surfaces blocked.
- `patch-0-1-2-artifact-publication-approval-decision-validation-2026-06-24.md` - patch 0.1.2
  artifact publication approval decision accepts only the exact macOS arm64 and Linux x64 CLI
  artifact names, SHA256 values, source binding, workflow evidence, and bounded wording for later
  operator upload while keeping upload, registry, npm vendor refresh, public install wording,
  hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces
  blocked until separate closeout or approval records pass.
- `patch-0-1-2-artifact-publication-closeout-validation-2026-06-24.md` - patch 0.1.2
  artifact publication closeout validation records GitHub Release `v0.1.2`, approved tag target,
  exact published macOS arm64 and Linux x64 assets, matching checksums, sidecars, bounded release
  wording, and retained blockers; registry publication, npm vendor refresh, npm publication, and
  public installation wording remain separate blocked lanes.
- `patch-0-1-2-npm-vendor-refresh-validation-2026-06-24.md` - patch 0.1.2 npm vendor refresh
  validation records the checked-in `@docushell/ethos-pdf@0.1.2` vendor payload refreshed from
  published GitHub Release `v0.1.2` assets, per-file vendor SHA256 values, local `npm pack`
  metadata, install smoke, missing-PDFium behavior, and retained publication blockers; npm publish
  and public installation wording remain blocked.
- `patch-0-1-2-npm-publication-approval-request-validation-2026-06-24.md` - patch 0.1.2 npm
  publication approval request validation binds the exact `@docushell/ethos-pdf@0.1.2` npm
  candidate, toolchain-qualified tarball hashes, durable vendor checksums, installed CLI smoke,
  missing-PDFium behavior, and retained blockers for decider review; npm publish remains blocked.
- `patch-0-1-2-npm-publication-approval-decision-validation-2026-06-24.md` - patch 0.1.2 npm
  publication approval decision validation accepts the exact `@docushell/ethos-pdf@0.1.2`
  bounded npm candidate, toolchain-qualified tarball hashes, durable vendor checksums, installed
  CLI smoke, missing-PDFium behavior, and retained blockers; it leaves operator publish pending.
- `patch-0-1-2-npm-publication-blocker-validation-2026-06-24.md` - patch 0.1.2 npm
  publication blocker validation records that the approved `@docushell/ethos-pdf@0.1.2` publish
  attempt failed with npm `E404`, registry checks still show latest `0.1.1`, and retry, registry
  closeout, and public installation wording remain blocked pending npm account/scope resolution.
- `patch-0-1-2-npm-publication-closeout-validation-2026-06-24.md` - patch 0.1.2 npm
  publication closeout validation records successful publication of `@docushell/ethos-pdf@0.1.2`,
  registry verification for latest version, shasum, integrity, tarball URL, file count, unpacked
  size, source commit binding, and retained blockers; public installation wording remains blocked.
- `patch-0-1-2-public-install-wording-closeout-validation-2026-06-24.md` - patch 0.1.2
  public install wording closeout validation records README and public claim-inventory wording for
  `@docushell/ethos-pdf@0.1.2` and GitHub Release `v0.1.2` CLI artifacts while keeping Rust crate
  and Python wheel install wording on the published `0.1.1` baseline until separate crates.io/PyPI
  `0.1.2` publication closeout records pass.
- `patch-0-1-2-crates-publication-approval-request-validation-2026-06-25.md` - patch 0.1.2
  crates.io publication approval request validation records exact `ethos-doc-core`,
  `ethos-verify`, and `ethos-pdf` `0.1.2` crate artifacts, SHA256 values, source binding,
  package tag names, publish order, requested later operator commands, and retained blockers;
  `cargo publish`, tag creation, and Rust crate public installation wording remain blocked.
- `patch-0-1-2-crates-publication-approval-decision-validation-2026-06-25.md` - patch 0.1.2
  crates.io publication approval decision validation accepts only bounded later operator execution
  for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` `0.1.2`; actual publication, package tag
  creation, Rust crate public installation wording, PyPI publication, hosted, production, Windows,
  bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces remain blocked until separate
  closeout or approval records pass.
- `patch-0-1-2-crates-publication-closeout-validation-2026-06-25.md` - patch 0.1.2 crates.io
  publication closeout validation records operator evidence and live crates.io visibility for
  `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` `0.1.2`; Rust crate public installation
  wording, PyPI publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`,
  and `ethos-rag` surfaces remain blocked until separate closeout or approval records pass.
- `patch-0-1-2-rust-public-install-wording-closeout-validation-2026-06-25.md` - patch 0.1.2
  Rust public install wording closeout validation records README and public claim-inventory wording
  for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`; PyPI publication, hosted,
  production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces remain
  blocked until separate closeout or approval records pass.
- `patch-0-1-2-python-publication-approval-request-validation-2026-06-25.md` - patch 0.1.2
  Python PyPI publication approval request validation binds the exact deterministic
  `ethos-pdf==0.1.2` wheel candidate, source commit, source tree, metadata, SHA256, and local
  install/import smoke for decider review; PyPI upload and Python public installation wording
  remain blocked until separate decision, operator, and closeout records pass.
- `patch-0-1-2-python-publication-approval-decision-validation-2026-06-25.md` - patch 0.1.2
  Python PyPI publication approval decision validation accepts only bounded later operator
  execution for the exact deterministic `ethos-pdf==0.1.2` wheel candidate; actual upload,
  Python public installation wording, package tag creation, hosted, production, Windows, bundled
  PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces remain blocked until separate operator
  evidence, closeout, or approval records pass.
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
