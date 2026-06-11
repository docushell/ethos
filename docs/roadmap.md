# Ethos Public Roadmap

Updated at every milestone boundary; landscape refreshed before each milestone and at least
every 90 days (`docs/landscape-log.md`). Weeks are plan commitments (IMPLEMENTATION_PLAN), not
PRD requirements. Nothing below is a release promise until its milestone exit criteria pass.
This roadmap reflects ADR-0001 reduced staffing: one active implementation lane plus 0.25
benchmark/devrel support. It also reflects ADR-0007: Ethos is a verification and grounding
layer that includes a deterministic parser, not a parser that may later add verification.

Current PM status and blockers: `docs/execution-status.md`.

| Milestone | Window | Contents | Gate |
| --- | --- | --- | --- |
| Week 0 | pre-kickoff | ADRs, governance, corpus freeze, CI bootstrap, competitor pins | All 11 rows done; clock starts |
| A | weeks 1-8 | Contracts (5 schemas, c14n, deterministic profile), trust-boundary artifacts (`GroundingSource`, verification schemas, OpenDataLoader adapter stub, `ethos verify` CLI stub), PDFium Phase 1 spike, harness + competitor adapters, CLI skeleton | **Gate Zero**: G1 throughput, G2 footprint, G3 determinism - PROCEED / G1_RETRY / FALLBACK (ADR-0005). A is incomplete without the trust-boundary artifacts. |
| B | weeks 9-14 | **`ethos verify` alpha first**: native Ethos JSON + OpenDataLoader verification demo, stale fingerprint checks, capability-limited reports, deterministic evidence matching; then reading order, blocks, headings, lists, Markdown/text exporters, Python wheel scaffold, quality dashboard, Windows x64 nightly determinism | 13-B exit checklist |
| C | weeks 15-22 | Simple/bordered tables; RAG chunker + citations; non-text region coordinates; security report + default-chunk exclusion; debug overlay; internal benchmark snapshot | 13-C exit + first checkpoint |
| D | weeks 23-30 | `verify_citations` v1; crop API; sandbox/subprocess backend; Node beta and MCP experimental only if staffed or accepted by release-scope ADR | 13-D exit |
| E | weeks 31-40 | Public benchmark report (reproducible, labeled tiers); PDFium Phase 2 project-maintained builds; stable CLI/Python docs; proof-of-trust demos; **Public Beta** | Release 1 claim audit + public-beta checkpoint |
| F / Release 2 | post-E | Complex tables, formula/LaTeX, chart classification, optional enrichment modules (never base) | Scoped after E from beta fixtures |

Fallback charter: if Gate Zero fails on G2/G3 (or a failed G1 retry), Ethos pivots to the
parser-agnostic trust layer — standalone `ethos-verify` + chunk/citation tooling over foreign
parser output. The trust layer ships as a Milestone B alpha either way.

Surface labels in Release 1: CLI + Python **stable**. Node **beta** and MCP **experimental**
ship only if staffed or accepted by release-scope ADR before public claims.
