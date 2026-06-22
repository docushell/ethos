# Milestone E Prep Scope

Status: source-only pre-alpha prep for internal Milestone E continuation.

This note defines the first narrow Milestone E prep slice. It does not approve public benchmark
reports, release artifacts, package publication, production positioning, public result wording, or
performance, quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an
internal continuation decision only.

## Purpose

Milestone D closed the current source-only contract boundary. Milestone E prep starts by preserving
that boundary while selecting already-validated trust-loop artifacts that can support internal demo
fixture planning.

The prep slice is allowed to:

- document the source-only pre-alpha E prep boundary;
- identify existing D and C trust-loop artifacts that are candidates for internal E demo fixtures;
- keep claim language tied to evidence grounding, diagnostics, fixture/evaluator validation, and
  explicit blockers;
- add static guards that prevent this prep note from becoming public launch or result wording.

The prep slice is not allowed to:

- create public report wording or public result summaries;
- add hosted surfaces, package/distribution work, or release artifacts;
- expand Node, MCP, sandbox-backed, or foreign-adapter crop surfaces;
- claim speed, footprint, quality, table-quality, parser-quality, or production readiness;
- treat the E prep fixture list as a finished demo plan.

## Internal Demo Fixture Candidates

The current E prep candidate set is restricted to tracked source-tree artifacts already covered by
existing guards. The machine-readable inventory is
`docs/milestone-e-fixture-candidates.json` and is schema-bound by
`schemas/ethos-milestone-e-fixture-candidates.schema.json`. Internal fixture-promotion criteria
live in `docs/milestone-e-fixture-promotion-criteria.json` and are schema-bound by
`schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json`; they define what must be
rechecked before a candidate can enter an internal demo plan, not public demo approval. Each
candidate row must keep a structured `blockers_must_remain_explicit` list that matches the
promotion criteria row before any internal fixture-planning use.
The internal trust-loop walkthrough plan lives in
`docs/milestone-e-internal-trust-loop-walkthrough.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json`. It sequences the current
fixture-candidate inventory for internal source-only planning, not public result wording.
The internal trust-loop use protocol lives in
`docs/milestone-e-internal-trust-loop-use-protocol.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json`. It defines only the
required source-checkout validation and blocker-preservation rules for internal walkthrough use,
not public result wording.
The internal trust-loop rehearsal/evidence matrix lives in
`docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json`. It maps
the existing use-protocol steps to evidence grounding, diagnostics, fixture/evaluator validation,
and explicit blockers for internal source-only rehearsal planning, not public result wording.
The internal trust-loop blocker ledger lives in
`docs/milestone-e-internal-trust-loop-blocker-ledger.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json`. It derives explicit
blockers from the rehearsal/evidence matrix and keeps them visible for internal source-only
planning; it does not resolve or soften blockers and is not public result wording.
The public approval lane blocker ledger lives in
`docs/milestone-e-public-approval-lane-blockers.json` and is schema-bound by
`schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json`. It records source-only
public beta evaluation as approved for the GitHub source repository while keeping package
publication, hosted surface, production positioning, public benchmark report, public benchmark
claim, release-artifact, binary, wheel, npm package, crate publication, and project-maintained
PDFium build lanes blocked; it is not public result wording.
The public beta approval prep lane lives in
`docs/milestone-e-public-beta-approval-prep.json` and is schema-bound by
`schemas/ethos-milestone-e-public-beta-approval-prep.schema.json`. It records the source-only
public beta approval for reviewed commit `902c423` and merged main commit `6019a97`, whose source
trees match, and records the exact allowed wording, setup boundary, and exclusions.
The public beta required-evidence records live in
`docs/validation/milestone-e-public-beta-approval-decision-validation-2026-06-20.md`,
`docs/validation/milestone-e-public-beta-release-scope-engineering-blocker-review-validation-2026-06-20.md`,
`docs/validation/milestone-e-public-beta-public-setup-path-review-validation-2026-06-20.md`,
and `docs/validation/milestone-e-public-beta-pdfium-build-path-review-validation-2026-06-20.md`.
They complete the evidence-record set that was later rescoped by
`docs/validation/milestone-e-public-beta-source-only-approval-validation-2026-06-20.md`; the
source-only approval record does not approve package publication, hosted surfaces, production
positioning, public benchmark reports, public benchmark claims, release artifacts, binaries, wheels,
npm packages, crate publication, or project-maintained PDFium builds.
The package publication approval prep lane lives in
`docs/milestone-e-package-publication-approval-prep.json` and is schema-bound by
`schemas/ethos-milestone-e-package-publication-approval-prep.schema.json`. It approves internal
Rust crate publication preparation only for the five ADR-0006 reserved priority crates.io
identifiers, records required evidence, exact blockers, allowed/forbidden wording, and the PDFium
packaging boundary, and does not approve package publication, real-version `cargo publish`, public
installation, release artifacts, binaries, wheels, npm packages, hosted surfaces, production
positioning, public benchmark reports, or public benchmark claims.
The package publication evidence records under `docs/validation/` record reserved-name inventory
reconciliation, metadata/license/README readiness, dry-run/smoke planning, version/tag policy, and
PDFium packaging boundary evidence for that prep lane. They keep package publication blocked.
The public-facing readiness ledger lives in
`docs/milestone-e-public-facing-readiness-ledger.json` and is schema-bound by
`schemas/ethos-milestone-e-public-facing-readiness-ledger.schema.json`. It records current main
`6019a97` / tree `f56fde854f6f6e4c4070209329f8c7b12310aa51` as the current-main source-only
public beta source binding, keeps the exact public beta wording unchanged, and retains
package-publication resolution gaps while package publication remains blocked.
The public beta current-main refresh prep lane lives in
`docs/milestone-e-public-beta-current-main-refresh-prep.json` and is schema-bound by
`schemas/ethos-milestone-e-public-beta-current-main-refresh-prep.schema.json`. It records current
main `9262b28` / tree `9f18f9e40c57551aef9b0cb2a53641c87207546b` as a current-main refresh
candidate only and does not refresh the reviewed source-only public beta source state.
The current-main source-only public beta approval is recorded in
`docs/validation/milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md`.
It pins reviewed commit `902c423`, merged main commit `6019a97`, and tree
`f56fde854f6f6e4c4070209329f8c7b12310aa51` for the same source-only GitHub repository surface.
The package publication approval resolution plan is recorded in
`docs/validation/milestone-e-package-publication-approval-resolution-plan-validation-2026-06-21.md`.
It binds the future exact decision review to current source commit `524535a` / tree
`0785ffca8423c42e2c4105df7752e290cc88e5c2` while package publication remains blocked and public
installation remains blocked.
The package publication decision input packet is recorded in
`docs/validation/milestone-e-package-publication-decision-input-packet-validation-2026-06-21.md`.
It binds candidate review inputs to source commit `54bf70f` / tree
`5a197bee718e3b31399563340169e9efd4f1317c` while package publication remains blocked and public
installation remains blocked.
The package publication approval readiness review is recorded in
`docs/validation/milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md`.
It records readiness status for source commit `9054f1c` / tree
`3f8cb66249826d67ab6030032c7784a2a4ff411b` while package publication remains blocked and public
installation remains blocked.
The package publication manifest-activation diff review is recorded in
`docs/validation/milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md`.
It records the candidate manifest activation diff for source commit `89d24c8` / tree
`21b263dca908ef7cc977e7669e40206096eef93e` while current Cargo manifests remain unchanged,
package publication remains blocked, and public installation remains blocked.
The package publication registry-assembly evidence review is recorded in
`docs/validation/milestone-e-package-publication-registry-assembly-evidence-review-validation-2026-06-21.md`.
It records registry-backed dependent package assembly evidence requirements for source commit
`3f0f3ed` / tree `6c748cd6f4a8de7789e42666697d1f25aa99f6f9` while no registry is created,
registry-backed assembly is not activated, package publication remains blocked, and public
installation remains blocked.
The package publication public installation wording review is recorded in
`docs/validation/milestone-e-package-publication-public-installation-wording-review-validation-2026-06-21.md`.
It records candidate public installation wording and explicit exclusions for source commit
`8b446e3` / tree `385dd7799cf898fc850555ce13d6d74e8ee15196` while the wording is not approved,
package publication remains blocked, and public installation remains blocked.
The package publication approval decision template is recorded in
`docs/validation/milestone-e-package-publication-approval-decision-template-validation-2026-06-21.md`.
It records the exact future decider inputs required after the wording review for source commit
`66979cc` / tree `58ef15e1cac8ce7df35a7e88da2044e57eb66c10` while no decision is approved,
package publication remains blocked, and public installation remains blocked.
The package publication approval decision is recorded in
`docs/validation/milestone-e-package-publication-approval-decision-validation-2026-06-21.md`.
It rejects the current package-publication request for source commit `fdbd5b7` / tree
`4a7bf5cda2c779e41a04c3feb691a12fec1e5c8d` because required activation evidence is absent;
package publication remains blocked, and public installation remains blocked.
The package publication candidate activation evidence is recorded in
`docs/validation/milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md`.
It validates a temporary non-public package activation workspace for source commit `6cf211c` /
tree `ae76bc588b64dc1e8087d9096d52545a3560c2c0`; source Cargo manifests remain blocked, package
publication remains blocked, and public installation remains blocked.
The package publication approval decision refresh is recorded in
`docs/validation/milestone-e-package-publication-approval-decision-refresh-validation-2026-06-22.md`.
It records that activation evidence is present for source commit `6a91511` / tree
`8b150d9aebdc282c358e4552a4d709c3140f41b4`, while manual exact approval remains required,
source Cargo manifests remain unchanged, package publication remains blocked, and public
installation remains blocked.
The package publication manifest activation applied follow-up is recorded in
`docs/validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md`.
It records the source package name `ethos-doc-core`, Rust library name `ethos_core`, and workspace
dependency activation for review only; `publish = false`, public installation, and package
publication remain blocked.
The package publication current registry-equivalent assembly follow-up is recorded in
`docs/validation/milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md`.
It records current registry-equivalent assembly evidence for `ethos-doc-core`, `ethos-verify`, and
`ethos-pdf`; public installation and package publication remain blocked.
The package publication final approval request is recorded in
`docs/validation/milestone-e-package-publication-final-approval-request-validation-2026-06-22.md`.
It records exact candidate crates, version map, package tag names, source binding, proposed public
installation wording, and explicit exclusions for decider review; public installation and package
publication remain blocked.
The package publication final approval decision is recorded in
`docs/validation/milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md`.
It accepts the exact bounded candidate crates, version map, package tag names, source binding,
wording, and exclusions; publish-flag activation remains blocked, package tag creation remains
blocked, real-version cargo publish remains blocked, and public installation instructions remain
unchanged until later gated activation.
The package publication publish-flag activation request is recorded in
`docs/validation/milestone-e-package-publication-publish-flag-activation-request-validation-2026-06-22.md`.
It records the exact requested activation diff for the three accepted candidate manifests only;
activation remains blocked, package tag source binding must be refreshed after activation,
package tag creation remains blocked, real-version cargo publish remains blocked, and public
installation instructions remain unchanged.
The metadata-readiness follow-up record under `docs/validation/` covers README, NOTICE, manifest
metadata, and include-list readiness for `ethos-core`, `ethos-verify`, and `ethos-pdf` only.
`ethos-doc` and `ethos-rag` remain reserved placeholders without in-tree package manifests, and
package publication remains blocked.
The current dry-run/smoke follow-up record under `docs/validation/` covers local package assembly
for `ethos-doc-core` and source-tree checks for `ethos-verify` and `ethos-pdf` only after source
manifest activation. Public installation, exact registry-backed assembly activation, and package
publication remain blocked.
The version/tag policy follow-up record under `docs/validation/` covers source-tree version,
reserved placeholder version, source snapshot tag, and future package tag namespace separation
only. Real package version selection, package tag creation, public installation, and package
publication remain blocked.
The PDFium boundary follow-up record under `docs/validation/` covers the current source-tree
`ethos-pdf` packaging boundary only: no bundled PDFium binary, caller-provided PDFium through
`ETHOS_PDFIUM_LIBRARY_PATH`, and no raw PDFium FFI types across public schemas/APIs.
Project-maintained PDFium builds, public installation, and package publication remain blocked.
The dependency-ordering follow-up record under `docs/validation/` covers the future dependent
candidate order only: `ethos-doc-core` before `ethos-verify` and `ethos-pdf`. Registry-backed
dependent package assembly, package dependency manifest migration, public installation, and package
publication remain blocked.
The manifest-migration prep follow-up record under `docs/validation/` covers future Cargo manifest
shape only: core package-name migration to `ethos-doc-core`, a workspace dependency alias, and
stable source dependency keys for `ethos-verify` and `ethos-pdf`. Current Cargo manifests remain
unchanged; registry-backed dependent package assembly, package dependency manifest activation,
public installation, and package publication remain blocked.
The manifest-activation prep follow-up record under `docs/validation/` covers future package
dependency manifest activation review only. Current Cargo manifests remain unchanged; package
dependency manifest activation, registry-backed dependent package assembly activation, public
installation, and package publication remain blocked.
The registry-assembly prep follow-up record under `docs/validation/` covers future non-public
dependent candidate assembly rehearsal only. No registry is created, current Cargo manifests remain
unchanged, and registry-backed dependent package assembly activation, package dependency manifest
activation, public installation, and package publication remain blocked.
The registry-assembly activation prep follow-up record under `docs/validation/` covers future
registry-backed dependent package assembly activation review only. No registry is created and no
registry-backed assembly is activated; registry-backed dependent package assembly activation,
public installation, and package publication remain blocked.
The real-version-selection prep follow-up record under `docs/validation/` covers future SemVer
candidate review only. No package publication version is selected; real package version selection
approval, package tag creation, public installation, and package publication remain blocked.
The tag-creation prep follow-up record under `docs/validation/` covers future package tag creation
review only. No package tag is created; package tag creation, public installation, and package
publication remain blocked.
The use protocol, rehearsal/evidence matrix, and blocker ledger must keep the same blocked-output
alignment so public reports, public result wording, hosted surfaces, release artifacts, package
publication, production positioning, broad demo-generation workflows, benchmark publication, and
all performance, quality, footprint, table-quality, and parser-quality claims remain explicitly
blocked.
The rehearsal/evidence matrix and blocker ledger must also keep the same evidence-lane alignment so
evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers remain the
only current internal rehearsal lanes.
All nine current E prep JSON artifacts and their row validation records must keep the same
diagnostic-boundary alignment so expected diagnostic boundaries remain tied to source-only
evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
All current E prep artifacts and rows that carry promotion status must also keep
promotion-status alignment at `not_promoted_beyond_internal_fixture_planning` until a later
source-only decision changes that state.
All current E prep artifacts must keep source-status alignment at
`source-only-pre-alpha-internal-milestone-e-prep`, and fixture-candidate rows must remain
`source-only-pre-alpha-internal-candidate`.
The current E prep artifacts with `applies_to_*` fields must keep applies-to binding alignment
across `docs/milestone-e-fixture-candidates.json`,
`docs/milestone-e-fixture-promotion-criteria.json`,
`docs/milestone-e-internal-trust-loop-walkthrough.json`,
`docs/milestone-e-internal-trust-loop-use-protocol.json`,
`docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`, and
`docs/milestone-e-internal-trust-loop-blocker-ledger.json`.
The current E prep artifacts with `required_before_*` fields must keep required-before alignment
so `make milestone-e-prep remains green`, public-surface posture checks, claims gates, diagnostic
boundaries, and explicit blockers remain required before any internal planning use advances.
Milestone E validation records must keep validation-record source-head alignment so each
`Validated source HEAD before this record` line names the source checkout state validated before
that record was added.

| Candidate | Existing artifact | Current guard |
| --- | --- | --- |
| Native verification trust loop | `examples/verify/cases.json` and `examples/verify/goldens/native_grounded_report.json` | `make verify-alpha` |
| Split-quote and unsupported-claim diagnostics | `examples/verify/native_split_quote_citations.json` and `examples/verify/native_non_v1_claims_citations.json` | `make verify-alpha` |
| Capability downgrade diagnostics | `examples/verify/capability_downgrade_v1_contract.json` and `examples/verify/goldens/opendataloader_capability_limited_report.json` | `make milestone-d-capability-downgrade-contract` |
| OpenDataLoader-style adapter grounding | `examples/verify/opendataloader_adapter_shape_v1_contract.json` and `examples/verify/opendataloader.json` | `make milestone-d-opendataloader-adapter-shape-contract` |
| Pinned real OpenDataLoader fixture path | `fixtures/foreign/opendataloader/real/manifest.json`, `fixtures/foreign/opendataloader/real/expected.verification_report.json`, and `fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json` | `make verify-alpha` |
| Crop descriptor and source-bound crop shape | `examples/crop/crop_element_v1_contract.json` and `examples/crop/crop_element_surface_shape_v1_contract.json` | `make milestone-d-internal-contracts` |
| RAG chunk artifact loop | `schemas/examples/chunks.example.jsonl` | `make rag-chunk-alpha` |
| Security-report artifact loop | `schemas/examples/security-report.example.json` | `make security-report-alpha` |
| Demo narrative index | `docs/demos/verify-alpha.md` | `make verify-alpha` |

These are internal fixture candidates, not public proof points. Any future demo plan must still
state the validated command, input fixture, expected diagnostic boundary, blocker status, and every
structured blocker before the fixture can be promoted beyond source-only pre-alpha planning.

## Prep Guard

Focused validation command:

- `make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python`

The target runs status/roadmap posture checks, public-surface posture checks, the claims gate,
public pre-alpha wording approval, release-readiness next-step approval, H1 public-safe comparison
closeout validation, H2 source-snapshot scope approval, source-snapshot candidate audit,
H2 source-snapshot candidate evidence, H2 source-snapshot closeout, schema/example validation,
schema-registry alignment for the E prep JSON artifacts, public-boundary alignment,
blocked-output alignment, evidence-lane alignment, diagnostic-boundary alignment,
promotion-status alignment, source-status alignment, applies-to binding alignment,
required-before alignment, validation-record source-head alignment, this prep-scope guard,
fixture-candidate blocker-alignment validation,
the internal trust-loop walkthrough, use-protocol,
rehearsal/evidence matrix, blocker-ledger guards, and public approval lane blocker guard,
public beta approval prep guard, public beta required-evidence record guard,
public beta source-only approval guard,
package publication approval prep guard,
package publication prep approval validation guard,
package publication evidence records guard,
package publication metadata-readiness guard,
package publication dry-run/smoke guard,
package publication version/tag policy guard,
package publication PDFium boundary guard,
package publication dependency-ordering guard,
package publication approval decision refresh guard,
validation-command index checks,
validation-record index checks, the prep guard-sequence index, validation-record guards, and diff
hygiene. It intentionally does not run public-report, release, package, hosted, benchmark-report,
or broad demo-generation workflows.

## Exit Criteria For This Prep Slice

- `docs/roadmap.md` and `docs/execution-status.md` point to this prep boundary.
- The source-tree guard keeps the fixture-candidate list explicit and path-backed.
- The source-tree guard keeps internal fixture-promotion criteria aligned with the candidate
  inventory.
- The schema validation gate keeps the fixture-candidate inventory and fixture-promotion criteria
  closed to unreviewed fields.
- The schema-registry alignment guard keeps the nine E prep JSON artifacts and their nine schemas in
  one-to-one sync across schema validation and source-tree status docs.
- Fixture-candidate blocker lists remain structured, nonempty, and visible before any internal
  fixture-planning use.
- The internal trust-loop walkthrough plan remains limited to existing candidates and criteria.
- The internal trust-loop use protocol remains limited to existing walkthrough steps and explicit
  blockers.
- The internal trust-loop rehearsal/evidence matrix remains limited to existing protocol steps,
  evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
- The internal trust-loop blocker ledger remains limited to existing matrix rows and does not
  resolve or soften blockers.
- The public approval lane blocker ledger records source-only public beta evaluation approval and
  keeps package publication, hosted surfaces, production positioning, public benchmark reports,
  public benchmark claims, release artifacts, binaries, wheels, npm packages, crate publication, and
  project-maintained PDFium builds blocked.
- The public beta approval prep lane remains limited to source-only public beta evaluation for the
  GitHub source repository and records the exact approved wording and exclusions.
- The public beta required-evidence records remain historical evidence for the blocker reviews
  rescoped by the source-only public beta approval record.
- The package publication approval prep lane remains limited to internal Rust crate publication
  preparation for the five ADR-0006 reserved priority crates.io identifiers, remains
  `prep_approved_publication_blocked`, and does not approve package publication.
- The package publication evidence records remain indexed, source-bound, and limited to current
  prep blockers for reserved-name inventory, metadata/license/README readiness, dry-run/smoke
  planning, version/tag policy, and PDFium packaging boundary review.
- The package publication metadata-readiness follow-up remains limited to README, NOTICE, manifest
  metadata, and include-list readiness for `ethos-core`, `ethos-verify`, and `ethos-pdf`, while
  `ethos-doc`, `ethos-rag`, dry-run/smoke, version/tag policy, PDFium follow-through, and package
  publication remain blocked.
- The package publication current dry-run/smoke follow-up remains limited to local package
  assembly for `ethos-doc-core` and source-tree checks for `ethos-verify` and `ethos-pdf`; exact
  registry-backed assembly activation, public installation, real package version selection,
  package tag creation, PDFium follow-through, and package publication remain blocked.
- The package publication version/tag policy follow-up remains limited to source-tree version,
  reserved placeholder version, source snapshot tag, and future package tag namespace separation;
  real package version selection, package tag creation, public installation, and package publication
  remain blocked.
- The package publication PDFium boundary follow-up remains limited to the current source-tree
  `ethos-pdf` packaging boundary; project-maintained PDFium builds, public installation, and
  package publication remain blocked.
- The package publication dependency-ordering follow-up remains limited to future dependent
  candidate order; registry-backed dependent package assembly, package dependency manifest
  migration, public installation, and package publication remain blocked.
- The package publication manifest-migration prep follow-up remains limited to future Cargo
  manifest shape; current Cargo manifests remain unchanged, and registry-backed dependent package
  assembly, package dependency manifest activation, public installation, and package publication
  remain blocked.
- The package publication registry-assembly prep follow-up remains limited to future non-public
  dependent candidate assembly rehearsal; no registry is created, current Cargo manifests remain
  unchanged, and registry-backed dependent package assembly activation, package dependency manifest
  activation, public installation, and package publication remain blocked.
- The package publication real-version-selection prep follow-up remains limited to future SemVer
  candidate review; no package publication version is selected, and real package version selection
  approval, package tag creation, public installation, and package publication remain blocked.
- The package publication approval decision refresh records that activation evidence is present;
  manual exact approval remains required, source Cargo manifests remain unchanged, public
  installation remains blocked, and package publication remains blocked.
- The package publication manifest activation applied follow-up records the source package name
  `ethos-doc-core`, Rust library name `ethos_core`, and workspace dependency activation for review
  only; `publish = false`, public installation, and package publication remain blocked.
- The package publication current registry-equivalent assembly follow-up records non-public
  assembly evidence for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`; public installation and
  package publication remain blocked.
- The package publication final approval request records exact candidate crates, version map,
  package tag names, source binding, proposed public installation wording, and explicit exclusions
  for decider review; public installation and package publication remain blocked.
- The package publication final approval decision records exact decider acceptance of the bounded
  candidate crates, version map, package tag names, source binding, wording, and exclusions;
  publish-flag activation remains blocked, package tag creation remains blocked, and real-version
  cargo publish remains blocked until later gated activation.
- The package publication publish-flag activation request records exact requested source changes
  for the three accepted candidate manifests only; activation remains blocked, package tag source
  binding must be refreshed after activation, package tag creation remains blocked, and
  real-version cargo publish remains blocked.
- The public-facing readiness ledger records the current-main source-only public beta source binding
  and package-publication gap retention; it does not approve package publication, approve public
  installation, or soften any current
  public-facing blocker.
- The public beta current-main refresh prep remains limited to refresh evidence preparation for
  current main `9262b28`; it does not change the approved public beta wording, refresh the reviewed
  source-only public beta source state, approve package publication, approve public installation, or
  soften any current public-facing blocker.
- Blocked-output alignment remains identical across the use protocol, rehearsal/evidence matrix,
  blocker ledger, and matching schemas.
- Evidence-lane alignment remains identical across the rehearsal/evidence matrix, blocker ledger,
  and matching schemas.
- Diagnostic-boundary alignment remains identical across the fixture candidates, promotion
  criteria, walkthrough, use protocol, rehearsal/evidence matrix, blocker ledger, matching schemas,
  and row validation records.
- Promotion-status alignment remains `not_promoted_beyond_internal_fixture_planning` across
  current artifacts, rows, matching schemas, and row validation records.
- Source-status alignment remains `source-only-pre-alpha-internal-milestone-e-prep` across current
  artifacts and `source-only-pre-alpha-internal-candidate` across fixture-candidate rows.
- Applies-to binding alignment remains exact across current fixture-candidate inventory,
  fixture-promotion criteria, walkthrough, use protocol, rehearsal/evidence matrix, blocker ledger,
  and matching schemas.
- Required-before alignment remains exact across fixture-promotion criteria, walkthrough, use
  protocol, rehearsal/evidence matrix, blocker ledger, and matching schemas.
- Validation-record source-head alignment remains exact across Milestone E validation records.
- Public language remains limited to the exact source-only public beta wording for the approved
  GitHub source repository surface and internal-continuation scoped outside that surface.
- External blockers remain visible before any public-facing Milestone E work starts.
