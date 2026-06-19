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

Milestone D source-only pre-alpha contract work has started with the narrow
[`verify_citations` v1 contract](milestone-d-verify-citations-contract.md). The
current executable carrier remains `ethos verify`; the first D slice is a
contract and fixture-backed validation boundary, not a new public command,
binding, crop API, sandbox backend, Node beta, or MCP experimental scope.
The source-only
[`claim_kind_boundary` v1 contract](milestone-d-claim-kind-boundary-contract.md)
binds the supported v1 claim-kind boundary to current citation/config/report
fixtures so non-v1 claim inputs remain explicit diagnostics until deliberately expanded.
The source-only
[`grounding_source` v1 contract](milestone-d-grounding-source-contract.md)
binds the parser-neutral evidence boundary to current native and foreign-source
report grounding metadata without adding a new command or binding surface.
The next D contract-prep slice defines the source-only
[`crop_element` v1 contract](milestone-d-crop-element-contract.md) over the
descriptor-only `ethos crop_element` CLI carrier. It now includes an internal
`ethos-core::crop_element` descriptor-only resolver, descriptor type, shared logical crop-ref
identity helper, fail-closed descriptor diagnostics, and focused CLI validation, while Python,
Node, MCP, hosted, rendered-backend, and sandbox scope remain explicit blockers.
The source-only
[`crop_element_surface_shape` v1 contract](milestone-d-crop-element-surface-shape-contract.md)
binds the descriptor-only CLI surface shape to the existing request and descriptor schemas while
recording the current absent Python crop method and the remaining non-CLI blockers.
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
Current Milestone D source-only contract closeout is recorded in
[`docs/validation/milestone-d-contract-closeout-validation-2026-06-19.md`](validation/milestone-d-contract-closeout-validation-2026-06-19.md);
full 13-D exit still requires implementation-lane review beyond this contract boundary.

| Milestone | Window | Contents | Gate |
| --- | --- | --- | --- |
| Week 0 | pre-kickoff | ADRs, governance, corpus freeze, CI bootstrap, competitor pins | All 11 rows done; clock starts |
| A | weeks 1-8 | Contracts (5 schemas, c14n, deterministic profile), trust-boundary artifacts (`GroundingSource`, verification schemas, OpenDataLoader adapter stub, `ethos verify` CLI stub), PDFium Phase 1 spike, harness + competitor adapters, CLI skeleton | **Gate Zero**: ADR-0005 is accepted as `PROCEED` for internal Milestone B continuation. This is not public benchmark, release, package, production, or claim approval. |
| B | weeks 9-14 | **`ethos verify` alpha first**: native Ethos JSON + synthetic and pinned real OpenDataLoader verification demos, stale fingerprint checks, capability-limited reports, deterministic evidence matching including split-quote coverage, explicit unsupported non-v1 claim reporting, adapter structure diagnostics; then reading order, blocks, headings, lists, Markdown/text exporters, Python wheel scaffold, quality dashboard, Windows x64 nightly determinism | [13-B exit checklist](milestone-b-exit-checklist.md) |
| C | weeks 15-22 | Simple/bordered tables; RAG chunker + citations; non-text region coordinates; security report + default-chunk exclusion; debug overlay; internal benchmark snapshot | Current artifact-validation checkpoint recorded in [Milestone C closeout validation](validation/milestone-c-closeout-validation-2026-06-18.md); broader debug/crop/table follow-ups remain explicit |
| D | weeks 23-30 | [`verify_citations` v1 contract prep](milestone-d-verify-citations-contract.md); [`claim_kind_boundary` v1 contract prep](milestone-d-claim-kind-boundary-contract.md); [`grounding_source` v1 contract prep](milestone-d-grounding-source-contract.md); [`capability_downgrade` v1 contract prep](milestone-d-capability-downgrade-contract.md); [`opendataloader_adapter_shape` v1 contract prep](milestone-d-opendataloader-adapter-shape-contract.md); [`crop_element` v1 contract prep](milestone-d-crop-element-contract.md) plus internal descriptor-only resolver; [`crop_element_surface_shape` v1 contract prep](milestone-d-crop-element-surface-shape-contract.md); [`sandbox_subprocess` v1 contract prep](milestone-d-sandbox-subprocess-contract.md); [contract closeout validation](validation/milestone-d-contract-closeout-validation-2026-06-19.md); crop API; sandbox/subprocess backend; Node and MCP surfaces remain explicit blockers unless staffed or accepted by scoped ADR | 13-D exit |
| E | weeks 31-40 | Public benchmark report (reproducible, labeled tiers); PDFium Phase 2 project-maintained builds; stable CLI/Python docs; proof-of-trust demos; **Public Beta** | Release 1 claim audit + public-beta checkpoint |
| F / Release 2 | post-E | Complex tables, formula/LaTeX, chart classification, optional enrichment modules (never base) | Scoped after E from beta fixtures |

Fallback charter: ADR-0005 selected `PROCEED`. If a future Gate Zero successor decision rejects
G2/G3 evidence, or rejects G1 after a bounded retry path, Ethos pivots to the parser-agnostic trust
layer — standalone `ethos-verify` + chunk/citation tooling over foreign parser output. The trust
layer remains the first Milestone B product path either way.

Surface labels in Release 1: CLI + Python **stable**. Node **beta** and MCP **experimental**
ship only if staffed or accepted by release-scope ADR before public claims.
