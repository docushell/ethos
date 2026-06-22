# Ethos Public Roadmap

Updated at every milestone boundary; landscape refreshed before each milestone and at least
every 90 days (`docs/landscape-log.md`). Weeks are plan commitments (IMPLEMENTATION_PLAN), not
PRD requirements. Nothing below is a release promise until its milestone exit criteria pass.
This roadmap reflects ADR-0001 reduced staffing: one active implementation lane plus 0.25
benchmark/devrel support. It also reflects ADR-0007: Ethos is a verification and grounding
layer that includes a deterministic parser, not a parser that may later add verification.

Current PM status and blockers: `docs/execution-status.md`.

Milestone C has an internal source-tree artifact-validation closeout for the
current RAG chunk and security-report trust-loop checks. The canonical status
tracker records the current pre-alpha validation posture plus the remaining
external blockers. This closeout does not approve public benchmark reports,
releases, packages, production positioning, or performance/quality/footprint
claims.

Milestone D source-only pre-alpha work is internally closed for the current source-tree scope.
The narrow [`verify_citations` v1 contract](milestone-d-verify-citations-contract.md) keeps the
current executable carrier as `ethos verify`; this is a contract and fixture-backed validation
boundary, not a new public command, binding, crop API, sandbox backend, Node beta, or MCP
experimental scope.
The source-only
[`claim_kind_boundary` v1 contract](milestone-d-claim-kind-boundary-contract.md)
binds the supported v1 claim-kind boundary to current citation/config/report
fixtures so non-v1 claim inputs remain explicit diagnostics until deliberately expanded.
The source-only
[`grounding_source` v1 contract](milestone-d-grounding-source-contract.md)
binds the parser-neutral evidence boundary to current native and foreign-source
report grounding metadata without adding a new command or binding surface.
The D crop contract slice defines the source-only
[`crop_element` v1 contract](milestone-d-crop-element-contract.md) over the
source-bound `ethos crop_element` CLI carrier. It now includes an internal
`ethos-core::crop_element` resolver, descriptor type, shared logical crop-ref
identity helper, fail-closed descriptor diagnostics, source-bound rendered artifact support for
caller-provided source PDFs, and focused CLI/Python validation, while Node, MCP, hosted,
sandbox-backed, and foreign-adapter scope remain explicit blockers.
The source-only
[`crop_element_surface_shape` v1 contract](milestone-d-crop-element-surface-shape-contract.md)
binds the source-bound CLI/Python surface shape to the existing request and descriptor schemas
while recording the remaining Node, MCP, hosted, sandbox-backed, and foreign-adapter blockers.
The source-only
[`capability_downgrade` v1 contract](milestone-d-capability-downgrade-contract.md)
binds existing grounding-source capability declarations to verification-report
capability limits, warnings, and blocked-check diagnostics without adding a new
command or binding surface.
The source-only
[`opendataloader_adapter_shape` v1 contract](milestone-d-opendataloader-adapter-shape-contract.md)
binds the existing OpenDataLoader-style adapter shape boundary to `GroundingSource`
identity, capabilities, accepted fixture shapes, and deterministic diagnostics.
The source-only [`sandbox_subprocess` v1 contract](milestone-d-sandbox-subprocess-contract.md)
classifies the existing PDF worker-process boundary behind `ethos doc parse` and
`ethos fingerprint`; it does not add hardened sandbox rules or a new command or
binding surface.
Current Milestone D source-only final closeout is recorded in
[`docs/validation/milestone-d-final-closeout-validation-2026-06-19.md`](validation/milestone-d-final-closeout-validation-2026-06-19.md).
The prior contract closeout is recorded in
[`docs/validation/milestone-d-contract-closeout-validation-2026-06-19.md`](validation/milestone-d-contract-closeout-validation-2026-06-19.md);
13-D exit is complete for the current source-only pre-alpha scope. The accepted D closeout scope
keeps Node, MCP, hosted, sandbox-backed, and foreign-adapter crop surfaces out of Milestone D, and
cross-platform rendered-crop byte identity is not required for D closeout.
Milestone E prep begins with a source-only pre-alpha boundary note at
[`docs/milestone-e-prep-scope.md`](milestone-e-prep-scope.md) and a guarded internal fixture
candidate inventory at
[`docs/milestone-e-fixture-candidates.json`](milestone-e-fixture-candidates.json), with internal
fixture-promotion criteria in
[`docs/milestone-e-fixture-promotion-criteria.json`](milestone-e-fixture-promotion-criteria.json).
These E prep JSON artifacts are schema-bound by
[`schemas/ethos-milestone-e-fixture-candidates.schema.json`](../schemas/ethos-milestone-e-fixture-candidates.schema.json)
and
[`schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json`](../schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json).
The internal trust-loop walkthrough plan is recorded in
[`docs/milestone-e-internal-trust-loop-walkthrough.json`](milestone-e-internal-trust-loop-walkthrough.json)
and schema-bound by
[`schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json`](../schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json).
The internal trust-loop use protocol is recorded in
[`docs/milestone-e-internal-trust-loop-use-protocol.json`](milestone-e-internal-trust-loop-use-protocol.json)
and schema-bound by
[`schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json`](../schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json).
The internal trust-loop rehearsal/evidence matrix is recorded in
[`docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`](milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json)
and schema-bound by
[`schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json`](../schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json).
The internal trust-loop blocker ledger is recorded in
[`docs/milestone-e-internal-trust-loop-blocker-ledger.json`](milestone-e-internal-trust-loop-blocker-ledger.json)
and schema-bound by
[`schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json`](../schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json).
The public approval lane blocker ledger is recorded in
[`docs/milestone-e-public-approval-lane-blockers.json`](milestone-e-public-approval-lane-blockers.json)
and schema-bound by
[`schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json`](../schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json).
The public beta approval prep lane is recorded in
[`docs/milestone-e-public-beta-approval-prep.json`](milestone-e-public-beta-approval-prep.json)
and schema-bound by
[`schemas/ethos-milestone-e-public-beta-approval-prep.schema.json`](../schemas/ethos-milestone-e-public-beta-approval-prep.schema.json);
source-only public beta evaluation is approved for reviewed commit `902c423` and merged main
commit `6019a97`, whose source trees match.
The current public beta required-evidence records are indexed under `docs/validation/` for approval
decision review, engineering blocker review, public setup path review, and PDFium build-path review;
they are superseded by the source-only public beta approval record and remain evidence for the
rescoped blockers.
The package publication approval prep lane is recorded in
[`docs/milestone-e-package-publication-approval-prep.json`](milestone-e-package-publication-approval-prep.json)
and schema-bound by
[`schemas/ethos-milestone-e-package-publication-approval-prep.schema.json`](../schemas/ethos-milestone-e-package-publication-approval-prep.schema.json);
package publication prep is approved for internal Rust crate publication preparation only across
the five ADR-0006 reserved priority crates.io identifiers, and does not approve package
publication. Package publication evidence records are indexed under `docs/validation/` for
reserved-name inventory, metadata/license/README readiness, dry-run/smoke planning, version/tag
policy, and PDFium packaging boundary review, while package publication remains blocked. The
metadata-readiness follow-up records README, NOTICE, manifest metadata, and include-list readiness
for `ethos-core`, `ethos-verify`, and `ethos-pdf`; `ethos-doc` and `ethos-rag` remain reserved
placeholders without in-tree manifests. The current dry-run/smoke follow-up records local package
assembly for `ethos-doc-core` and source-tree checks for `ethos-verify` and `ethos-pdf`; exact
registry-backed assembly activation, public installation, and package publication remain blocked.
The version/tag policy follow-up records source-tree version, reserved placeholder version, source
snapshot tag, and future package tag namespace separation; real package version selection, package
tag creation, public installation, and package publication remain blocked.
The PDFium boundary follow-up records the current source-tree `ethos-pdf` packaging boundary; no
project-maintained PDFium build, public installation, or package publication is approved.
The dependency-ordering follow-up records that any later dependent-candidate review must stage
`ethos-doc-core` before `ethos-verify` and `ethos-pdf`; registry-backed dependent package assembly,
package dependency manifest migration, public installation, and package publication remain blocked.
The manifest-migration prep follow-up records future Cargo manifest shape while current Cargo
manifests remain unchanged; registry-backed dependent package assembly, package dependency manifest
activation, public installation, and package publication remain blocked.
The manifest-activation prep follow-up records future package dependency manifest activation review
while current Cargo manifests remain unchanged; package dependency manifest activation,
registry-backed dependent package assembly activation, public installation, and package publication
remain blocked.
The manifest activation applied follow-up is recorded in
[`docs/validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md`](validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md)
and records the source package name `ethos-doc-core`, Rust library name `ethos_core`, and workspace
dependency activation for review only; `publish = false`, public installation, and package
publication remain blocked.
The current registry-equivalent assembly follow-up is recorded in
[`docs/validation/milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md`](validation/milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md)
and records non-public assembly evidence for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`;
public installation and package publication remain blocked.
The final approval request is recorded in
[`docs/validation/milestone-e-package-publication-final-approval-request-validation-2026-06-22.md`](validation/milestone-e-package-publication-final-approval-request-validation-2026-06-22.md)
and records exact candidate crates, version map, package tag names, source binding, proposed public
installation wording, and explicit exclusions for decider review; public installation and package
publication remain blocked.
The final approval decision is recorded in
[`docs/validation/milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md`](validation/milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md)
and accepts the exact bounded candidate crates, version map, package tag names, source binding,
wording, and explicit exclusions; publish-flag activation remains blocked, package tag creation
remains blocked, real-version cargo publish remains blocked, and public installation instructions
remain unchanged until later gated activation.
The publish-flag activation request is recorded in
[`docs/validation/milestone-e-package-publication-publish-flag-activation-request-validation-2026-06-22.md`](validation/milestone-e-package-publication-publish-flag-activation-request-validation-2026-06-22.md)
and records the exact requested source diff for the three accepted candidate manifests only;
activation remains blocked, package tag source binding must be refreshed after activation, package
tag creation remains blocked, real-version cargo publish remains blocked, and public installation
instructions remain unchanged.
The package publication activation applied follow-up is recorded in
[`docs/validation/milestone-e-package-publication-activation-applied-validation-2026-06-22.md`](validation/milestone-e-package-publication-activation-applied-validation-2026-06-22.md)
and binds the activated candidate manifests to source commit `f50f294` / tree
`00c3e4df7a7b3b368659650601a2df76b63a2ce8`; package tag source binding must be refreshed, public
installation remains blocked, and real-version cargo publish remains blocked.
The package publication tag binding refresh is recorded in
[`docs/validation/milestone-e-package-publication-tag-binding-refresh-validation-2026-06-22.md`](validation/milestone-e-package-publication-tag-binding-refresh-validation-2026-06-22.md)
and binds the accepted package tag names to activated main commit `421bed8` / tree
`aa0d5d31d879540fd0044052dfeb747f12b64204`; operator evidence remains required, package tag
creation remains blocked, registry publication remains blocked, and public installation remains
blocked.
The package publication operator preflight is recorded in
[`docs/validation/milestone-e-package-publication-operator-preflight-validation-2026-06-22.md`](validation/milestone-e-package-publication-operator-preflight-validation-2026-06-22.md)
and records manual crates.io owner/account evidence requirements, reserved-name confirmation,
dependency order, package tag names, and command order; manual registry evidence remains required,
public installation remains blocked, and registry publication remains blocked.
The package publication manual registry evidence request is recorded in
[`docs/validation/milestone-e-package-publication-manual-registry-evidence-request-validation-2026-06-22.md`](validation/milestone-e-package-publication-manual-registry-evidence-request-validation-2026-06-22.md)
and provides the exact non-secret output packet required from the operator for crates.io
owner/account confirmation, reserved-name owner outputs, dry-run outputs, package tag names, and
explicit exclusions; manual registry evidence remains required, public installation remains
blocked, and registry publication remains blocked.
The package publication manual registry evidence supplied record is recorded in
[`docs/validation/milestone-e-package-publication-manual-registry-evidence-supplied-validation-2026-06-22.md`](validation/milestone-e-package-publication-manual-registry-evidence-supplied-validation-2026-06-22.md)
and captures the supplied non-secret owner/account evidence, reserved-name owner outputs,
`ethos-doc-core` dry-run output, expected blocked dependent dry-run outputs, package tag names, and
explicit exclusions; manual registry evidence supplied is recorded, public installation remains
blocked, and registry publication remains blocked.
The package publication registry action authorization request is recorded in
[`docs/validation/milestone-e-package-publication-registry-action-authorization-request-validation-2026-06-22.md`](validation/milestone-e-package-publication-registry-action-authorization-request-validation-2026-06-22.md)
and provides the exact non-secret authorization packet and command order for later package tag
creation and the first registry action; package tag creation remains blocked, public installation
remains blocked, and registry publication remains blocked.
The registry-assembly prep follow-up records future non-public dependent candidate assembly
rehearsal while no registry is created and current Cargo manifests remain unchanged;
registry-backed dependent package assembly activation, package dependency manifest activation,
public installation, and package publication remain blocked.
The registry-assembly activation prep follow-up records future registry-backed dependent package
assembly activation review while no registry is created and no registry-backed assembly is
activated; registry-backed dependent package assembly activation, public installation, and package
publication remain blocked.
The real-version-selection prep follow-up records future SemVer candidate review while selecting no
package publication version; real package version selection approval, package tag creation, public
installation, and package publication remain blocked.
The tag-creation prep follow-up records future package tag creation review while creating no
package tag; package tag creation, public installation, and package publication remain blocked.
The public-facing readiness ledger is recorded in
[`docs/milestone-e-public-facing-readiness-ledger.json`](milestone-e-public-facing-readiness-ledger.json)
and schema-bound by
[`schemas/ethos-milestone-e-public-facing-readiness-ledger.schema.json`](../schemas/ethos-milestone-e-public-facing-readiness-ledger.schema.json);
it records current main `6019a97` / tree `f56fde854f6f6e4c4070209329f8c7b12310aa51` as the
current-main source-only public beta source binding, keeps the exact public beta wording unchanged,
and retains package-publication resolution gaps while package publication remains blocked.
The public beta current-main refresh prep lane is recorded in
[`docs/milestone-e-public-beta-current-main-refresh-prep.json`](milestone-e-public-beta-current-main-refresh-prep.json)
and schema-bound by
[`schemas/ethos-milestone-e-public-beta-current-main-refresh-prep.schema.json`](../schemas/ethos-milestone-e-public-beta-current-main-refresh-prep.schema.json);
it records current main `9262b28` / tree `9f18f9e40c57551aef9b0cb2a53641c87207546b` as a
current-main refresh candidate only and does not refresh the reviewed source-only public beta source
state.
The current-main source-only public beta approval is recorded in
[`docs/validation/milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md`](validation/milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md)
for reviewed commit `902c423`, merged main commit `6019a97`, and tree
`f56fde854f6f6e4c4070209329f8c7b12310aa51`.
The package publication approval resolution plan is recorded in
[`docs/validation/milestone-e-package-publication-approval-resolution-plan-validation-2026-06-21.md`](validation/milestone-e-package-publication-approval-resolution-plan-validation-2026-06-21.md)
for current source commit `524535a` / tree `0785ffca8423c42e2c4105df7752e290cc88e5c2`, with
package publication remains blocked and public installation remains blocked.
The package publication decision input packet is recorded in
[`docs/validation/milestone-e-package-publication-decision-input-packet-validation-2026-06-21.md`](validation/milestone-e-package-publication-decision-input-packet-validation-2026-06-21.md)
for source commit `54bf70f` / tree `5a197bee718e3b31399563340169e9efd4f1317c`. Candidate version,
tag, manifest, assembly, and wording inputs are recorded while package publication remains blocked
and public installation remains blocked.
The package publication approval readiness review is recorded in
[`docs/validation/milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md`](validation/milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md)
for source commit `9054f1c` / tree `3f8cb66249826d67ab6030032c7784a2a4ff411b`. Exact approval
decision, signoff, manifest review, assembly evidence, and post-wording gates remain required
while package publication remains blocked and public installation remains blocked.
The package publication manifest-activation diff review is recorded in
[`docs/validation/milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md`](validation/milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md)
for source commit `89d24c8` / tree `21b263dca908ef7cc977e7669e40206096eef93e`. The candidate
manifest activation diff is reviewed while current Cargo manifests remain unchanged, package
publication remains blocked, and public installation remains blocked.
The package publication registry-assembly evidence review is recorded in
[`docs/validation/milestone-e-package-publication-registry-assembly-evidence-review-validation-2026-06-21.md`](validation/milestone-e-package-publication-registry-assembly-evidence-review-validation-2026-06-21.md)
for source commit `3f0f3ed` / tree `6c748cd6f4a8de7789e42666697d1f25aa99f6f9`. Registry-backed
dependent package assembly evidence requirements are recorded while no registry is created,
registry-backed assembly is not activated, package publication remains blocked, and public
installation remains blocked.
The package publication public installation wording review is recorded in
[`docs/validation/milestone-e-package-publication-public-installation-wording-review-validation-2026-06-21.md`](validation/milestone-e-package-publication-public-installation-wording-review-validation-2026-06-21.md)
for source commit `8b446e3` / tree `385dd7799cf898fc850555ce13d6d74e8ee15196`. Candidate
wording and explicit exclusions are recorded for later approval review only while package
publication remains blocked and public installation remains blocked.
The package publication approval decision template is recorded in
[`docs/validation/milestone-e-package-publication-approval-decision-template-validation-2026-06-21.md`](validation/milestone-e-package-publication-approval-decision-template-validation-2026-06-21.md)
for source commit `66979cc` / tree `58ef15e1cac8ce7df35a7e88da2044e57eb66c10`. The template
lists the exact future decider inputs required after the wording review while package publication
remains blocked and public installation remains blocked.
The package publication approval decision is recorded in
[`docs/validation/milestone-e-package-publication-approval-decision-validation-2026-06-21.md`](validation/milestone-e-package-publication-approval-decision-validation-2026-06-21.md)
for source commit `fdbd5b7` / tree `4a7bf5cda2c779e41a04c3feb691a12fec1e5c8d`. The current
package-publication request is rejected because required activation evidence is absent; package
publication remains blocked and public installation remains blocked.
The package publication candidate activation evidence is recorded in
[`docs/validation/milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md`](validation/milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md)
for source commit `6cf211c` / tree `ae76bc588b64dc1e8087d9096d52545a3560c2c0`. A temporary
non-public package activation workspace validates the candidate package-name and dependency shape
while source Cargo manifests remain blocked, package publication remains blocked, and public
installation remains blocked.
The package publication approval decision refresh is recorded in
[`docs/validation/milestone-e-package-publication-approval-decision-refresh-validation-2026-06-22.md`](validation/milestone-e-package-publication-approval-decision-refresh-validation-2026-06-22.md)
for source commit `6a91511` / tree `8b150d9aebdc282c358e4552a4d709c3140f41b4`. Activation
evidence is present, but manual exact approval remains required; source Cargo manifests remain
unchanged, package publication remains blocked, and public installation remains blocked.
This prep only identifies tracked trust-loop fixture candidates and guard wiring for internal
continuation; blocked-output alignment keeps the current trust-loop protocol, rehearsal/evidence
matrix, blocker ledger, and matching schemas on the same explicit blockers, while evidence-lane
alignment keeps the current rehearsal/evidence matrix, blocker ledger, and matching schemas on the
same internal evidence lanes. The diagnostic-boundary alignment guard keeps the current fixture
candidates, promotion criteria, walkthrough, use protocol, rehearsal/evidence matrix, blocker
ledger, matching schemas, and row validation records on the same source-only diagnostic
boundaries. The promotion-status alignment guard keeps current artifacts and rows at
`not_promoted_beyond_internal_fixture_planning`. The source-status alignment guard keeps current
artifacts at `source-only-pre-alpha-internal-milestone-e-prep`. The applies-to binding alignment
guard keeps the current E artifacts bound from `docs/milestone-e-fixture-candidates.json` through
`docs/milestone-e-internal-trust-loop-blocker-ledger.json`. The required-before alignment guard
keeps current readiness gates tied to `make milestone-e-prep remains green`, posture checks,
claims gates, diagnostic boundaries, and explicit blockers. The validation-record source-head
alignment guard keeps each `Validated source HEAD before this record` line source-bound. The public
approval lane blocker ledger records source-only public beta evaluation approval and package
publication prep approval while package publication, hosted surface, production positioning, public
benchmark report, public benchmark claim, release-artifact, binary, wheel, npm package, crate
publication, real-version cargo publish, and project-maintained PDFium build lanes remain blocked.
The public beta approval prep lane records exact source-only public beta wording and exclusions.
The package publication approval prep lane remains `prep_approved_publication_blocked`, does not
approve package publication, and does not broaden public wording. The public-facing readiness
ledger records a current-main refresh candidate and package-publication gap retention only; it does
not approve package publication, public installation, hosted surfaces, production positioning,
public benchmark reports, public benchmark claims, or broader public wording. The public beta
current-main refresh prep records refresh evidence inputs only; it does not change the approved
public beta wording, approve package publication, approve public installation, or broaden public
wording. The
Milestone E prep source-only closeout is recorded in
[`docs/validation/milestone-e-final-closeout-validation-2026-06-20.md`](validation/milestone-e-final-closeout-validation-2026-06-20.md)
for the current internal prep boundary only. This prep does not resolve or soften blockers, approve
public result wording, hosted surfaces,
package/distribution work, or
public-facing claims.

| Milestone | Window | Contents | Gate |
| --- | --- | --- | --- |
| Week 0 | pre-kickoff | ADRs, governance, corpus freeze, CI bootstrap, competitor pins | All 11 rows done; clock starts |
| A | weeks 1-8 | Contracts (5 schemas, c14n, deterministic profile), trust-boundary artifacts (`GroundingSource`, verification schemas, OpenDataLoader adapter stub, `ethos verify` CLI stub), PDFium Phase 1 spike, harness + competitor adapters, CLI skeleton | **Gate Zero**: ADR-0005 is accepted as `PROCEED` for internal Milestone B continuation. This is not public benchmark, release, package, production, or claim approval. |
| B | weeks 9-14 | **`ethos verify` alpha first**: native Ethos JSON + synthetic and pinned real OpenDataLoader verification demos, stale fingerprint checks, capability-limited reports, deterministic evidence matching including split-quote coverage, explicit unsupported non-v1 claim reporting, adapter structure diagnostics; then reading order, blocks, headings, lists, Markdown/text exporters, Python wheel scaffold, quality dashboard, Windows x64 nightly determinism | [13-B exit checklist](milestone-b-exit-checklist.md) |
| C | weeks 15-22 | Simple/bordered tables; RAG chunker + citations; non-text region coordinates; security report + default-chunk exclusion; debug overlay; internal benchmark snapshot | Current artifact-validation checkpoint recorded in [Milestone C closeout validation](validation/milestone-c-closeout-validation-2026-06-18.md); broader debug/crop/table follow-ups remain explicit |
| D | weeks 23-30 | [`verify_citations` v1 contract prep](milestone-d-verify-citations-contract.md); [`claim_kind_boundary` v1 contract prep](milestone-d-claim-kind-boundary-contract.md); [`grounding_source` v1 contract prep](milestone-d-grounding-source-contract.md); [`capability_downgrade` v1 contract prep](milestone-d-capability-downgrade-contract.md); [`opendataloader_adapter_shape` v1 contract prep](milestone-d-opendataloader-adapter-shape-contract.md); [`crop_element` v1 contract prep](milestone-d-crop-element-contract.md) plus internal resolver and source-bound CLI/Python descriptor/rendered carriers; [`crop_element_surface_shape` v1 contract prep](milestone-d-crop-element-surface-shape-contract.md); [`sandbox_subprocess` v1 contract prep](milestone-d-sandbox-subprocess-contract.md); [contract closeout validation](validation/milestone-d-contract-closeout-validation-2026-06-19.md); [final closeout validation](validation/milestone-d-final-closeout-validation-2026-06-19.md); Node/MCP/hosted crop surfaces, sandbox-backed crop behavior, foreign-adapter crop coordinates, and cross-platform rendered-crop byte identity are explicit post-D blockers, not D closeout requirements | 13-D exit complete for source-only pre-alpha scope |
| E | weeks 31-40 | Initial source-only prep scope in [`docs/milestone-e-prep-scope.md`](milestone-e-prep-scope.md), with current internal prep closeout recorded in [`docs/validation/milestone-e-final-closeout-validation-2026-06-20.md`](validation/milestone-e-final-closeout-validation-2026-06-20.md); source-only public beta evaluation is tracked in [`docs/milestone-e-public-beta-approval-prep.json`](milestone-e-public-beta-approval-prep.json) with exact wording and exclusions; current-main source-only public beta approval is recorded in [`docs/validation/milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md`](validation/milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md); package publication approval prep is tracked in [`docs/milestone-e-package-publication-approval-prep.json`](milestone-e-package-publication-approval-prep.json) as internal Rust crate publication prep only, with evidence, metadata-readiness, dry-run/smoke, version/tag policy, PDFium boundary, dependency-ordering, and approval resolution-plan records under `docs/validation/`; current-main public-facing readiness is tracked in [`docs/milestone-e-public-facing-readiness-ledger.json`](milestone-e-public-facing-readiness-ledger.json) without approving package publication; current-main source-only public beta refresh prep is tracked in [`docs/milestone-e-public-beta-current-main-refresh-prep.json`](milestone-e-public-beta-current-main-refresh-prep.json) without changing approved wording or approving package publication; actual package publication, later public-report, project-maintained PDFium build, stable CLI/Python docs, and hosted demo work remain blocked on explicit claim-audit and release-scope decisions | Release 1 claim audit + source-only public-beta checkpoint |
| F / Release 2 | post-E | Complex tables, formula/LaTeX, chart classification, optional enrichment modules (never base) | Scoped after E from beta fixtures |

Fallback charter: ADR-0005 selected `PROCEED`. If a future Gate Zero successor decision rejects
G2/G3 evidence, or rejects G1 after a bounded retry path, Ethos pivots to the parser-agnostic trust
layer — standalone `ethos-verify` + chunk/citation tooling over foreign parser output. The trust
layer remains the first Milestone B product path either way.

Surface labels in Release 1: CLI + Python **stable**. Node **beta** and MCP **experimental**
ship only if staffed or accepted by release-scope ADR before public claims.
