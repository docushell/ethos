# Ethos Public Roadmap

Updated at every milestone boundary; landscape refreshed before each milestone and at least
every 90 days (`docs/landscape-log.md`). Weeks are plan commitments (IMPLEMENTATION_PLAN), not
PRD requirements. Nothing below is a release promise until its milestone exit criteria pass.

| Milestone | Window | Contents | Gate |
| --- | --- | --- | --- |
| Week 0 | pre-kickoff | ADRs, governance, corpus freeze, CI bootstrap, competitor pins | All 11 rows done; clock starts |
| A | weeks 1–4 | Contracts (5 schemas, c14n, deterministic profile), PDFium Phase 1 spike, harness + competitor adapters, CLI skeleton | **Gate Zero**: G1 throughput, G2 footprint, G3 determinism — PROCEED / G1_RETRY / FALLBACK (ADR-0005) |
| B | weeks 5–8 | Reading order, blocks, headings, lists; Markdown/text exporters; Python wheels; **`ethos verify` alpha + OpenDataLoader grounding adapter**; quality dashboard; Windows x64 joins nightly determinism | 13-B exit checklist |
| C | weeks 9–13 | Simple/bordered tables; RAG chunker + citations; non-text region coordinates; security report + default-chunk exclusion; debug overlay; internal benchmark snapshot | 13-C exit + one-quarter checkpoint |
| D | weeks 14–19 | `verify_citations` v1; Node binding (beta); crop API; MCP server (experimental, §9.4 rules); sandbox/subprocess backend | 13-D exit |
| E | weeks 20–26 | Public benchmark report (reproducible, labeled tiers); PDFium Phase 2 project-maintained builds; stable CLI/Python docs; proof-of-trust demos; **Public Beta** | Release 1 claim audit + two-quarter checkpoint |
| F / Release 2 | post-E | Complex tables, formula/LaTeX, chart classification, optional enrichment modules (never base) | Scoped after E from beta fixtures |

Fallback charter: if Gate Zero fails on G2/G3 (or a failed G1 retry), Ethos pivots to the
parser-agnostic trust layer — standalone `ethos-verify` + chunk/citation tooling over foreign
parser output. The trust layer ships as a Milestone B alpha either way.

Surface labels in Release 1: CLI + Python **stable**, Node **beta**, MCP **experimental**.
