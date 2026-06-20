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
approval lane blocker ledger keeps public beta, package publication, hosted surface, production
positioning, and public benchmark report lanes blocked pending dedicated approval records,
evidence, owners, wording, gate scripts, validation records, and decider review. The
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
| E | weeks 31-40 | Initial source-only prep scope in [`docs/milestone-e-prep-scope.md`](milestone-e-prep-scope.md), with current internal prep closeout recorded in [`docs/validation/milestone-e-final-closeout-validation-2026-06-20.md`](validation/milestone-e-final-closeout-validation-2026-06-20.md); later public-report, project-maintained PDFium build, stable CLI/Python docs, demo, and beta work remain blocked on explicit claim-audit and release-scope decisions | Release 1 claim audit + public-beta checkpoint |
| F / Release 2 | post-E | Complex tables, formula/LaTeX, chart classification, optional enrichment modules (never base) | Scoped after E from beta fixtures |

Fallback charter: ADR-0005 selected `PROCEED`. If a future Gate Zero successor decision rejects
G2/G3 evidence, or rejects G1 after a bounded retry path, Ethos pivots to the parser-agnostic trust
layer — standalone `ethos-verify` + chunk/citation tooling over foreign parser output. The trust
layer remains the first Milestone B product path either way.

Surface labels in Release 1: CLI + Python **stable**. Node **beta** and MCP **experimental**
ship only if staffed or accepted by release-scope ADR before public claims.
