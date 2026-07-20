# Ethos Next Implementation Plan (NIP-1)

Status: **active — this is the canonical "what to build next" document.**
Created: 2026-07-19. Revised: 2026-07-20 (v1.3). Owner: product / decider.
Supersedes nothing; complements `IMPLEMENTATION_PLAN.md` (historical milestone plan A–F) and
`docs/roadmap.md` (milestone/closeout record). Where those documents describe *how Ethos got
here*, this document describes *what to do next and in what order*.

> **If you are an AI agent or engineer opening this repository to implement something: start
> here.** Read §0 (how to use this document), §2 (operating rules), then pick the highest-priority
> `not_started` task in the Progress Ledger (§7) whose dependencies are `done`. Do not invent new
> workstreams before the P0 set is complete.

Revision v1.1 (2026-07-19, decider): `ethos-mcp` (NIP-2) deprioritized P0 → P2 — do not start it
before P0/P1 are complete. Citation emission (NIP-4) and install-friction (NIP-5) promoted to P0.
Execution model switched to AI-agent implementation with human review (§6.0); estimates added to
the ledger. NIP-1.1 delivered; NIP-1.6 and NIP-7.1 started (see ledger).

Revision v1.2 (2026-07-19, decider): **smoothness rule adopted** (§2 rule 9) — from idea to
release there are exactly three human gates (PR review, registry publish, public-wording
changes); everything else is automated CI, and nothing waits on ceremony. Release Lane v2
accepted (NIP-7.1 done). `CONTRIBUTING.md` rewritten as the single idea-to-release process page
with an external-contributor fast path (NIP-7.3 done). "Blocked" in historical docs is
reinterpreted: honesty gates (no unearned claims) remain as automated checks; approval-queue
blockers are retired.

Revision v1.3 (2026-07-20, decider): NIP-5.1 validation accepts the committed isolated macOS
`env -i` install smoke in place of a clean-VM transcript. Platform-specific artifact tasks retain
their own target-platform validation requirements.

---

## 0. How to use this document

### 0.1 For AI agents and implementing engineers

1. Read §2 (operating rules) fully before writing code. They are non-negotiable repo invariants.
2. Open the Progress Ledger (§7). Select the first task that is `not_started` or `in_progress`,
   ordered by priority (P0 → P1 → P2), whose `Depends on` entries are all `done`.
3. Implement against the task's **Acceptance criteria** and **Validation** commands in §5. A task
   is not done until every listed validation command passes locally and in CI.
4. **Update the Progress Ledger row when you finish**: set status, date, and an evidence link
   (PR, validation record, or command output committed under `docs/validation/`). This is
   mandatory — the ledger is the single source of truth for NIP-1 progress. Stale ledgers are
   treated as bugs.
5. If you are blocked, set the row to `blocked`, add one line describing the blocker in the
   ledger's Notes column, and stop rather than working around a guardrail.
6. Keep CHANGELOG discipline: every landed task adds one entry under `## Unreleased` in
   `CHANGELOG.md`, in the existing house style.

### 0.2 Status vocabulary

`not_started` · `in_progress` · `blocked` · `done` · `dropped` (requires a decider note).

### 0.3 What this document does NOT approve

Consistent with `docs/execution-status.md` and the claims gates: this plan approves engineering
work and internal evidence gathering only. It does **not** approve public benchmark claims,
speed/footprint/parser-quality/table-quality claims, hosted production surfaces, production
positioning, Windows packaged artifacts, bundled project-maintained PDFium distribution, or any
change to approved public wording in `README.md` / `docs/public-boundary-claims.json`. Public
wording changes continue to require their own approval lane. Nothing here weakens that.

---

## 1. Context snapshot (2026-07-19)

What exists and is shipped:

- v0.3.0 public beta evaluation surfaces: source repo; crates `ethos-doc-core`, `ethos-verify`,
  `ethos-pdf`; PyPI wheel `ethos-pdf==0.3.0`; npm `@docushell/ethos-pdf@0.3.0`; macOS arm64 and
  Linux x64 CLI artifacts. PDFium is caller-provided via `ETHOS_PDFIUM_LIBRARY_PATH`.
- The working trust loop: `ethos doc parse` → chunks/citations → `ethos verify
  --fail-on-ungrounded` → `ethos crop_element` → `ethos evidence anchor`, deterministic and
  golden-tested (`make verify-alpha`).
- The OpenDataLoader-style JSON grounding adapter (foreign-parser verification path).
- v0.4.0 release train (`docs/v0-4-0-release-prep.md`): the accumulated next-minor verification,
  citation-emission, integration, adoption-tooling, and governance work. Source versions remain
  `0.3.0` until the release gates pass; the prep note explicitly excludes the P2-gated MCP
  prototype from activation and publication.

What is honestly true about adoption: registry downloads are at mirror-bot baseline, there are no
known external users, and there is one maintainer (ADR-0001). The strategy below is written for
that reality.

Empty surfaces reserved but unbuilt: `crates/ethos-mcp` (deprioritized to P2 by decider decision
2026-07-19), `crates/ethos-rag` (no NIP workstream; do not start), Node beta.

---

## 2. Operating rules (guardrails — read before any task)

1. **Determinism is a contract.** Same input + same pinned profile ⇒ byte-identical canonical
   payload and fingerprints. Every new surface (Action, adapters, emission helpers) must preserve
   this and add determinism tests (double-run byte-diff) for any new artifact it emits.
2. **Fail closed.** Missing capability ⇒ explicit `capability_limited` downgrade, never a silent
   pass. New surfaces must map errors to the stable exit-code/error-envelope contract
   (see `docs/milestone-d-capability-downgrade-contract.md`, PRD §10).
3. **Claims gates stay green.** `.github/scripts/public_boundary_claims_gate.py` must pass on
   every PR. Do not edit approved claim strings. No ranking/superlative claims anywhere,
   including code comments and examples (PRD §11.3).
4. **Scope honesty.** Ethos verifies *citation grounding*, not semantic truth. Every new doc,
   demo, or integration repeats this boundary where a user could confuse the two.
5. **Licensing:** no AGPL dependencies (ADR-0004). PDFium stays caller-provided in the base
   install until a decider accepts a bundling ADR (ADR-0013).
6. **Parser-agnostic first.** New verification features must work over `GroundingSource`, not
   only the native parser (ADR-0007). If a feature only works natively, it must degrade with an
   explicit capability warning on foreign sources.
7. **Governance right-sizing (NIP-7):** use **one prep note + one closeout record per release**
   per `docs/release-lane-v2.md` (accepted 2026-07-19), not per-artifact lanes. Keep the full
   v1 lane only for first-of-class surfaces.
8. **AI-execution boundary (v1.1).** AI agents implement, test, and prepare evidence. Humans
   retain: decider approvals, all registry-facing operator actions (cargo/npm/PyPI publish, tag
   pushes, GitHub Release edits), and public-wording changes. An agent must never execute a
   registry action or edit approved claim strings, even if credentials are available.
9. **Smoothness rule (v1.2).** From first idea to final release there are exactly three human
   gates: PR review, registry publish, public-wording changes. No task, PR, or release waits on
   any other approval, record, or ceremony. If you find yourself writing a request/decision/
   evidence document chain for routine work, stop — that pattern is retired. Honesty gates
   (claims CI, determinism CI) are automated checks, not queues.

---

## 3. Strategic direction

### 3.1 The thesis (unchanged, reaffirmed)

Ethos is a **verification and grounding layer** that includes a deterministic parser — not a
parser competing with Docling/Marker/MinerU on conversion quality (ADR-0007). The differentiated
wedge is: *citations as tests* — `--fail-on-ungrounded` as a CI/agent release gate, deterministic
reports as audit artifacts, crops as human-inspectable proof.

### 3.2 DocuShell is the first consumer — and the integration proof

DocuShell (the private monorepo at `docushell/`, sibling to this repo) consumes Ethos first.
This is deliberate dogfooding with a public purpose: **Ethos is open source, and DocuShell's
integration is the test of whether any outside business can integrate it.** Every point of
friction DocuShell hits is, by definition, friction every future adopter will hit.

Consequences:

- DocuShell integrates through **public surfaces only**: the published CLI artifacts, the
  published wheel/npm package, and documented JSON contracts. No private APIs, no reaching into
  Ethos internals. If DocuShell needs something not on a public surface, that is an Ethos
  product gap — file it in the friction log (NIP-1.6), don't special-case it.
- The integration contract lives in `docs/integrations/docushell.md` (delivered, NIP-1.1);
  the friction log lives in `docs/integrations/docushell-friction-log.md` (open, seeded with
  FR-1..FR-3).
- DocuShell already mirrors the verification-report contract in TypeScript
  (`packages/evidence/src/ethos-answer-release.ts`, `openai-chat-evidence.ts`) and implements
  the answer-release policy from `docs/app-answer-release-contract.md`. Keep these in lockstep:
  any report-schema change requires a same-PR note in the friction log and a version bump note
  for DocuShell (see friction entry FR-1 for the types-package gap).
- DocuShell's `services/parse-pdf` runs the OpenDataLoader hybrid backend (`docling-fast`).
  Its output enters Ethos through the existing `opendataloader-json` grounding adapter — the
  foreign-parser lane, exactly as an external adopter would use it.

### 3.3 Priorities in one sentence each

- **P0** — Prove and unblock the loop: DocuShell integration end-to-end (NIP-1), the trust
  benchmark that answers "why not LLM-as-a-judge?" (NIP-3), citation emission so real pipelines
  can feed `verify` (NIP-4), a one-step install (NIP-5), and right-sized governance (NIP-7).
- **P1** — The CI retention socket (NIP-6) and the contributor on-ramp (NIP-7.3).
- **P2** — Widen the funnel only after the above: `ethos-mcp` (NIP-2, deprioritized by decider),
  WASM playground (NIP-8), scanned-document path via foreign parsers (NIP-9).

---

## 4. Workstreams and tasks

Task IDs are stable; never renumber. Add new tasks with the next free number in their workstream.

---

### NIP-1 (P0) — DocuShell first-consumer integration

**Goal:** DocuShell's parse/evidence lane verifies AI citations with Ethos in a worker-lane
deployment, using only public Ethos surfaces, and produces a written integration-friction report
that drives the Ethos DX backlog.

**Why first:** it converts "no known users" into "one real production-shaped consumer," produces
the strongest possible DX feedback, and creates the reference integration story for every
external adopter.

**Non-goals:** no hosted Ethos service, no Ethos claims about DocuShell in public wording, no
DocuShell-specific code inside Ethos.

| Task | Description |
| --- | --- |
| NIP-1.1 | **Integration contract note.** ✅ Delivered: `docs/integrations/docushell.md` — surfaces consumed, version pins, compatibility promise, worker-lane rules, friction-log process. Template for future `docs/integrations/<consumer>.md` files. |
| NIP-1.2 | **Vendored CLI in the DocuShell worker image.** (DocuShell-side task, tracked here for sequencing.) DocuShell's `services/parse-pdf` worker image vendors the released Linux x64 `ethos` CLI artifact (sha256-pinned, same pattern as `packages/npm/ethos-pdf` vendor manifest) plus PDFium via `scripts/fetch-pdfium.sh` pins. Worker-lane only — never inside a Next.js request handler (DocuShell golden rule). Update the version-pin table in `docs/integrations/docushell.md` when done. |
| NIP-1.3 | **Verify lane.** DocuShell parse jobs emit OpenDataLoader-style JSON; a post-parse step runs `ethos verify <source> --citations <emitted> --grounding opendataloader-json --out <report>` and stores the report alongside job output. Exit-code semantics preserved: 0 grounded / 1 ungrounded-with-report / ≥2 error (fail closed → job error, not silent pass). |
| NIP-1.4 | **Answer-release gate.** DocuShell's OpenAI-playground evidence path feeds `proof_summary` + claim labels into its existing `ethos-answer-release.ts` policy so unverified claims are blocked or flagged before an answer is released. Validate against `docs/app-answer-release-contract.md` fixtures. |
| NIP-1.5 | **Crop inspection.** DocuShell surfaces `crop_element` rendered crops for at least one flow (evidence playground), so a human can see the cited region. Requires caller-provided PDFium in the worker image (NIP-1.2). |
| NIP-1.6 | **Integration friction log.** `docs/integrations/docushell-friction-log.md` — created and seeded with FR-1 (no published TS types), FR-2 (PDFium image wiring), FR-3 (CLI vendoring bookkeeping). Stays open through NIP-1.2–1.5; every step adds or dispositions entries. **Required deliverable.** |
| NIP-1.7 | **Closeout.** One validation record `docs/validation/nip-1-docushell-integration-closeout-<date>.md`: versions used, commands, friction-log summary, and explicit statement that no public wording changed. This satisfies the "DocuShell integration blocked pending separate evidence" line in `docs/execution-status.md`; a decider updates that status file. |

**Acceptance criteria (workstream):** a DocuShell parse job on a born-digital PDF produces a
stored Ethos verification report; an ungrounded citation demonstrably blocks/flags an answer via
the release policy; friction log has all entries dispositioned; closeout record merged.

---

### NIP-2 (P2 — deprioritized) — `ethos-mcp` v0: the agent surface

> **Decider decision 2026-07-19: do not start this workstream before P0 and P1 are complete.**
> Rationale: prove the loop with the first real consumer (DocuShell) and remove trial-killing
> friction before adding new surfaces. Scope below is preserved unchanged for when it unblocks.

**Goal:** a local MCP (Model Context Protocol) server exposing the trust loop to AI agents:
`verify`, `evidence_anchor`, `crop_element`, `doc_parse` (parse optional, PDFium-gated).

**Design constraints (unchanged):** experimental label per PRD §9.4; thin adapter over the same
internal code paths as the CLI (no forked logic); fail closed on missing PDFium; stdio transport
only in v0; distribution as an `ethos mcp serve` subcommand on the existing CLI binary.

Tasks NIP-2.1–2.5 as originally scoped: ADR-0014 (scope/security posture) → core `verify` +
`evidence_anchor` tools with golden/determinism tests → PDFium-gated `crop_element`/`doc_parse`
→ `docs/mcp.md` quickstart (copy-paste configs) → release inside a routine NIP-7 train.

**Acceptance criteria:** a stock MCP client config can call `verify` against
`schemas/examples/document.example.json` + the checked-in citation fixtures and receive the
grounded/ungrounded reports; determinism tests pass; experimental label present in every
user-facing string; claims gate green.

---

### NIP-3 (P0) — Trust benchmark: Ethos verify vs LLM-as-a-judge

**Goal:** a reproducible, labeled-fixture study comparing deterministic citation verification
against LLM-judge citation checking on: accuracy (precision/recall on grounded/ungrounded
labels), cost per 1,000 citations, latency, and run-to-run variance.

**Why:** LLM-as-a-judge is the incumbent alternative; this is the one benchmark category
(**Trust**, `docs/benchmark-plan.md` §Categories) that does not depend on Gate Zero G1/G2 and
directly answers every prospect's first question. Nobody has published this comparison well.

**Rules (inherited, strict):** results leave the harness only as JSON with reproduction
commands; label Ethos fixtures as Ethos-authored (never neutral); no ranking/superlative
language; LLM-judge prompts, model versions, and dates pinned in the manifest; judge
non-determinism is reported as data (variance across N runs), not editorialized. **Publication
of results remains gated** by the existing claim-audit lane — this workstream builds the study
and internal report; the decider approves public wording separately.

| Task | Description |
| --- | --- |
| NIP-3.1 | Labeled corpus: extend `fixtures/` with ≥200 citation checks over ≥20 born-digital documents — grounded, fabricated-quote, wrong-page, paraphrase-drift, split-quote, stale-fingerprint, and capability-limited cases. Labels reviewed twice (AI-generated labels require one human spot-check pass over a ≥20% sample); labeling guide committed. Runs in the `ethos-bench` sibling repo per `docs/benchmark-ownership.md`, fixtures live here. |
| NIP-3.2 | Judge harness: 2–3 pinned LLM judges (one frontier, one small/cheap) with a fixed citation-checking prompt; N=5 runs each for variance; cost/latency capture. Judge API runs are a human-triggered operation (spend approval), prepared end-to-end by the agent. |
| NIP-3.3 | Report generator: JSON results + auto-generated table with repro commands; internal snapshot first (dev-labeled per benchmark cadence rules). |
| NIP-3.4 | Claim-audit packet for the decider: proposed public wording, with the honest cells included (where judges beat Ethos, e.g. paraphrase tolerance, say so — that boundary is the semantic-truth line Ethos already disclaims). |

**Acceptance criteria:** `make trust-bench` (or ethos-bench equivalent) reproduces all numbers
one-command from pinned inputs; internal report exists; publication packet delivered to decider.

---

### NIP-4 (P0 — promoted in v1.1) — Citation emission: meet RAG frameworks where they are

**Goal:** close the chicken-and-egg — pipelines don't emit Ethos-checkable citations today. Ship
the *emit* side so `verify` has native inputs in real stacks.

Builds on `docs/citation-emission-spec-and-attestation-implementation-plan.md` (the spec exists;
this workstream implements it) and the existing `adapters/langchain`, `adapters/llamaindex`,
`adapters/docling`, `adapters/unstructured` directories.

| Task | Description |
| --- | --- |
| NIP-4.1 | Freeze citation-emission spec v1 (JSON shape a framework callback must produce) with schema + fixtures; version it independently of the report schema. |
| NIP-4.2 | Python package `ethos-emit` (or a module inside the existing wheel): helpers that wrap LangChain/LlamaIndex retrieval results + model answers into emission-spec citations. Pure Python, no PDFium, no CLI required to *emit*. |
| NIP-4.3 | Two runnable end-to-end examples in `examples/`: LangChain RAG → emit → `ethos verify --fail-on-ungrounded`; LlamaIndex equivalent. Pinned versions; CI-smoked with recorded/model-free fixtures so CI needs no API keys. |
| NIP-4.4 | Publish integration docs where discovery happens (framework-side integration listings), once wording passes the claims gate. |
| NIP-4.5 | **TypeScript report types (from friction log FR-1).** Generate TS types from the report/emission JSON Schemas and ship them on a public surface (`.d.ts` in the existing npm package or a types package), so consumers like DocuShell stop hand-mirroring types. |

**Acceptance criteria:** a RAG engineer can go from an existing LangChain pipeline to a failing
`--fail-on-ungrounded` exit on a fabricated citation in <30 minutes using only public docs;
DocuShell friction-log entries FR-1 (and any input-authoring entries from NIP-1) dispositioned.

---

### NIP-5 (P0 — promoted in v1.1) — Kill the install cliff

**Goal:** "time to first parse" (north-star metric, PRD §3.3) passes without manual PDFium steps.

| Task | Description |
| --- | --- |
| NIP-5.1 | Make `scripts/fetch-pdfium.sh` the paved road: `ethos doctor` subcommand that checks PDFium presence, prints the exact fix command, and validates sha256 pins. Wheel and npm postinstall print the same guidance (never auto-download in v0 — posture stays ADR-0013-compliant). Include the consumer Dockerfile snippet promised in friction entries FR-2/FR-3 in `docs/pdfium-manual-setup.md`. |
| NIP-5.2 | ADR-0015 proposal: opt-in bundled PDFium artifact class (`ethos-full` archives) for macOS arm64 + Linux x64, with license notices and size documented. Decision remains the decider's; this task prepares the ADR + build evidence only. |
| NIP-5.3 | Windows x64 CLI artifact (parse-optional): ship verify-only Windows support first — verification needs no PDFium, so Windows users get the trust loop's JSON half immediately; PDFium-on-Windows follows the ADR-0015 outcome. |

**Acceptance criteria:** fresh macOS/Linux machine → working parse in ≤3 commands with zero
manual URL hunting; fresh Windows machine → working `verify` on fixtures in ≤2 commands.

---

### NIP-6 (P1) — `ethos-verify` CI Action

**Goal:** the retention socket. A GitHub Action (separate `docushell/ethos-verify-action` repo)
that runs `ethos verify --fail-on-ungrounded` on PR-supplied evidence/citation artifacts and
annotates the PR with per-check statuses.

| Task | Description |
| --- | --- |
| NIP-6.1 | Action v0: pin CLI artifact by sha256, accept source/citations/grounding inputs, emit PR annotations from the report JSON, fail on exit 1/≥2. |
| NIP-6.2 | Dogfood: this repo's own CI runs the Action on the README demo fixtures (the "we gate ourselves" story). |
| NIP-6.3 | Marketplace listing after wording passes the claims gate. |

**Acceptance criteria:** a third-party repo can add ≤10 lines of workflow YAML and see a
fabricated-citation PR fail with a readable annotation.

---

### NIP-7 (P0, meta) — Right-size governance

**Goal:** protect the claims/approval discipline while cutting its cost ~in half, per §2 rule 7.

| Task | Description |
| --- | --- |
| NIP-7.1 | ✅ `docs/release-lane-v2.md` — written and **accepted 2026-07-19**. One prep doc + one closeout record per release train; full v1 lane retained for first-of-class surfaces only; smoothness rule embedded. |
| NIP-7.2 | Apply it: the next release (carrying NIP-5 work and landed NIP-1/NIP-4 deliverables) ships under the v2 lane as its pilot. |
| NIP-7.3 | ✅ Contributor on-ramp delivered 2026-07-19: `CONTRIBUTING.md` rewritten as the single idea-to-release process page — five-step first PR, three-requirement PR bar (tests, CHANGELOG line, DCO), invariants as a CI-enforced reference table, release process summary. A contributor never needs to read `docs/validation/`. Remaining follow-up: validate with one real first-time contributor or cold-start agent run (fold into NIP-7.2 pilot evidence). |

**Acceptance criteria:** next release's governance artifacts = exactly 2 documents; contributor
docs tested on one first-time contributor or one cold-start agent run.

---

### NIP-8 (P2) — WASM verify playground

**Goal:** in-browser `verify` over pasted/attached JSON — the 10-second "aha" with zero install.
Verification is JSON-only (no PDFium), so `ethos-verify` compiles to wasm32 with modest effort.
Static page (GitHub Pages) — prepare an ADR clarifying that a static, client-side page is not a
"hosted surface" in the blocked sense, and let the decider rule.

Tasks: NIP-8.1 wasm build of `ethos-verify` + JS shim; NIP-8.2 static page with the README demo
fixtures preloaded; NIP-8.3 ADR + decider review before anything is published.

---

### NIP-9 (P2) — Scanned documents via foreign parsers (not native OCR)

**Goal:** scanned/image-only PDFs enter the trust loop through OCR-capable foreign parsers
(Docling first) with explicit capability downgrades — Ethos does **not** build OCR (PRD
Release-3 boundary stands).

Tasks: NIP-9.1 promote the Docling adapter to a documented, fixture-backed grounding source with
an OCR-provenance capability flag; NIP-9.2 verification behavior spec for OCR-derived text
(`match_method` and confidence semantics stay honest — no pixel-proof claims); NIP-9.3 end-to-end
example: scanned PDF → Docling → verify, with downgrade warnings visible.

---

## 5. Validation commands (per task, run before marking `done`)

Baseline for **every** task: `cargo build --locked --workspace` · `cargo test --locked
--workspace` · `make verify-alpha` · claims gate script · determinism double-run on any new
artifact. Additional per-workstream:

- NIP-1: DocuShell-side narrow Mocha suite for the touched service (`npm run test:resume-parse`
  / parse-pdf suites) + `npm run acceptance:parse-pdf:real` for parse/OCR-adjacent claims, per
  DocuShell `CLAUDE.md`; Ethos-side closeout record lint (dates, versions, links resolve).
- NIP-2 (when unblocked): MCP golden tests ×2 runs byte-identical; quickstart configs
  copy-paste-verified against at least one real client.
- NIP-3: full one-command repro from a clean checkout of the bench repo; manifest pins resolve.
- NIP-4: both examples run end-to-end offline in CI via fixtures; <30-min walkthrough timed once;
  generated TS types compile against DocuShell's `packages/evidence` usage (FR-1 evidence).
- NIP-5.1: isolated install transcript from a fresh home and `env -i` environment committed as
  evidence; `ethos doctor` exit codes tested. Later platform-specific artifact tasks must still
  validate on their target platforms.
- NIP-6: Action integration test in a scratch repo; annotation snapshot committed.
- NIP-8: wasm build reproducible; page works with JS-disabled fallback message.
- NIP-9: adapter fixtures include at least one real (consented, license-clean) scanned document.

---

## 6. Execution model and sequencing

### 6.0 Execution model (v1.1): AI-implemented, human-gated

The default implementer for every task is an **AI agent**; the maintainer acts as reviewer,
decider, and operator. Consequences for planning:

- Estimates are in **agent-days**: one focused AI working session producing a reviewable PR,
  including tests and CHANGELOG entry. Implementation is rarely the bottleneck.
- The critical path is **human gates**: PR review, decider sign-offs (NIP-7.1, NIP-3.4, ADRs),
  spend approvals (NIP-3.2 judge runs), and registry operator actions. Batch them: one review
  session can clear several agent PRs.
- Agents must respect §2 rule 8 (no registry actions, no claim-string edits) and the ledger
  protocol (§0.1) without exception.
- Calendar guidance at this model: **P0 ≈ 3–4 calendar weeks** (≈15 agent-days of
  implementation, dominated by review/decider cadence), P1 ≈ +1 week. The original human-lane
  milestone pacing (weeks per feature) no longer applies.

### 6.1 Dependency order

```
NIP-7.1(sign-off) ──► all release-carrying work uses v2 lane (NIP-7.2)
NIP-1.1 ✅ ──► NIP-1.2 ──► NIP-1.3 ──► NIP-1.4/1.5 ──► NIP-1.6 ──► NIP-1.7
NIP-3.1 ──► NIP-3.2 ──► NIP-3.3 ──► NIP-3.4 (decider gate for publication)
NIP-4.1 ──► NIP-4.2 ──► NIP-4.3 ──► NIP-4.4 (claims gate); NIP-4.5 after NIP-4.1
NIP-5.1 ──► NIP-5.2(ADR) ──► NIP-5.3
NIP-6.1 ──► NIP-6.2 ──► NIP-6.3
P2 workstreams (NIP-2, NIP-8, NIP-9) start only when all P0/P1 tasks are done or explicitly
dropped by the decider.
```

Parallelism guidance: with AI implementation, NIP-1, NIP-3.1, NIP-4.1, and NIP-5.1 can run as
parallel lanes immediately — they touch disjoint areas. Keep one lane per PR to keep human review
tractable.

---

## 7. Progress Ledger — **update this section as work completes**

Est. = agent-days (see §6.0). Human-gate tasks marked (gate).

| Task | Priority | Status | Est. | Depends on | Date | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NIP-1.1 | P0 | done | 0.5 | — | 2026-07-19 | `docs/integrations/docushell.md` | |
| NIP-1.2 | P0 | done | 1 | NIP-1.1 | 2026-07-19 | `docs/integrations/docushell.md` | DocuShell worker-only image; offline determinism + fail-closed installer test |
| NIP-1.3 | P0 | done | 1 | NIP-1.2 | 2026-07-19 | `docs/integrations/docushell.md#parse-job-verification-lane-nip-13` | Stored canonical report; exit 1 preserved; missing capability/exit >=2 fail closed |
| NIP-1.4 | P0 | done | 1 | NIP-1.3 | 2026-07-19 | `docs/integrations/docushell.md#answer-release-gate-nip-14` | v1.1 claim-support labels; official fixture reproduced deterministically; missing support held for review |
| NIP-1.5 | P0 | blocked | 0.5 | NIP-1.2 | 2026-07-19 | `docs/integrations/docushell.md#crop-inspection-lane-nip-15` | Implementation, deterministic tests, narrow suites, and affected builds pass; required `npm run acceptance:parse-pdf:real` cannot start without operator-provided `API_KEY`/`DOCUSHELL_API_KEY` |
| NIP-1.6 | P0 | done | ongoing | NIP-1.1 | 2026-07-19 | `docs/integrations/docushell-friction-log.md` | FR-1..FR-10 recorded and dispositioned; FR-1/FR-7/FR-10 resolved by NIP-4.5; remaining product gaps assigned to NIP-5 or explicit follow-up |
| NIP-1.7 | P0 | not_started | 0.5 | NIP-1.4, NIP-1.5, NIP-1.6 | | | decider reviews (gate) |
| NIP-3.1 | P0 | done | 2 | — | 2026-07-20 | `fixtures/trust-benchmark/LABELING_GUIDE.md`; `fixtures/trust-benchmark/review-record.json`; `fixtures/trust-benchmark/v1/manifest.json` | Deterministic 20-document/200-check corpus and sibling `ethos-bench` harness pass; all labels executable-reviewed, and the Ethos dev team agreed with the balanced 40-check (20%) human spot-check without corrections. |
| NIP-3.2 | P0 | blocked | 1 | NIP-3.1 | 2026-07-20 | `../ethos-bench/benchmarks/trust/judges.lock.json`; `../ethos-bench/src/ethos_bench/trust_judges.py` | Engineering complete and spend approved; the first live attempt failed closed on a provider read timeout before writing results. Prior-call cost is unknown, so a fresh run with a longer timeout awaits renewed spend approval. |
| NIP-3.3 | P0 | not_started | 1 | NIP-3.2 | | | |
| NIP-3.4 | P0 | not_started | 0.5 | NIP-3.3 | | | decider gate |
| NIP-4.1 | P0 | done | 0.5 | — | 2026-07-19 | `docs/citation-emission-spec.md` | Independently versioned v1 schema; parser-neutral source IDs; grounded/fabricated/OOV/conflict fixtures; hydration and reports double-run byte-identical |
| NIP-4.2 | P0 | done | 1.5 | NIP-4.1 | 2026-07-19 | `python/README.md#citation-emission` | Pure-Python duck-typed LangChain/LlamaIndex adapters; strict retrieval metadata and OOV rejection; emission/hydration artifacts double-run byte-identical; no framework, CLI, PDFium, or network dependency |
| NIP-4.3 | P0 | done | 1 | NIP-4.2 | 2026-07-19 | `examples/README.md` | Native framework objects with resolvable exact core-package pins; Python 3.12 clean-environment install and model-free double-run suite pass in under 7 seconds with grounded exit 0 and fabricated exit 1 artifacts byte-identical |
| NIP-4.4 | P0 | dropped | 0.5 | NIP-4.3 | 2026-07-19 | `adapters/langchain/README.md`; `adapters/llamaindex/README.md` | Decider deferred framework-owned listings on 2026-07-19; adapters and walkthroughs remain available in Ethos, and the prepared upstream patches may be revisited after v0.4.0 |
| NIP-4.5 | P0 | done | 1 | NIP-4.1 | 2026-07-19 | `packages/npm/ethos-pdf/types/index.d.ts` | Schema-generated report, emission, and answer-release declarations ship in the npm candidate; strict fixtures, double-run generation, package tests, actual DocuShell type compatibility, and focused consumer tests pass |
| NIP-5.1 | P0 | done | 1 | — | 2026-07-20 | `docs/validation/nip-5-1-pdfium-install-smoke-2026-07-19.md` | Isolated fresh-home `env -i` macOS fetch, doctor, and byte-identical parse accepted by the decider under plan revision v1.3 |
| NIP-5.2 | P0 | done | 0.5 | NIP-5.1 | 2026-07-20 | `docs/decisions/ADR-0015-opt-in-bundled-pdfium-artifacts.md`; `docs/validation/nip-5-2-ethos-full-build-evidence-2026-07-20.md` | Proposed only: deterministic macOS/Linux candidates and notices verified; publication remains blocked pending ADR acceptance and target-platform smoke |
| NIP-5.3 | P0 | blocked | 1.5 | — | 2026-07-20 | `docs/validation/nip-5-3-windows-verify-draft-2026-07-20.md` | Implementation, deterministic packaging tests, and Windows cross-target check pass; actual `.exe` link/smoke requires the new `windows-latest` job because this macOS host has no `link.exe` or Windows runtime |
| NIP-6.1 | P1 | not_started | 1 | — | | | separate Action repo |
| NIP-6.2 | P1 | not_started | 0.5 | NIP-6.1 | | | |
| NIP-6.3 | P1 | not_started | 0.5 | NIP-6.2 | | | claims gate |
| NIP-7.1 | P0 | done | 0.5 | — | 2026-07-19 | `docs/release-lane-v2.md` | accepted by decider |
| NIP-7.2 | P0 | in_progress | 0.5 | NIP-7.1 | 2026-07-19 | `docs/v0-4-0-release-prep.md` | v0.4.0 pilot prep opened; release validation, version activation, publication, and closeout remain |
| NIP-7.3 | P1 | done | 0.5 | NIP-7.1 | 2026-07-19 | `CONTRIBUTING.md` | validate with first contributor during NIP-7.2 |
| NIP-2.1 | P2 | not_started | 0.5 | all P0/P1 done | | | deprioritized 2026-07-19 |
| NIP-2.2 | P2 | not_started | 2 | NIP-2.1 | | | |
| NIP-2.3 | P2 | not_started | 1 | NIP-2.2 | | | |
| NIP-2.4 | P2 | not_started | 0.5 | NIP-2.2 | | | |
| NIP-2.5 | P2 | not_started | 0.5 | NIP-2.3, NIP-2.4, NIP-7.1 | | | |
| NIP-8.1 | P2 | not_started | 1.5 | all P0/P1 done | | | |
| NIP-8.2 | P2 | not_started | 0.5 | NIP-8.1 | | | |
| NIP-8.3 | P2 | not_started | 0.5 | NIP-8.2 | | | decider gate |
| NIP-9.1 | P2 | not_started | 1 | all P0/P1 done | | | |
| NIP-9.2 | P2 | not_started | 0.5 | NIP-9.1 | | | |
| NIP-9.3 | P2 | not_started | 0.5 | NIP-9.2 | | | |

---

## 8. Success metrics (review monthly)

- **Time-to-first-verify:** <5 minutes from cold README on a fresh machine (measured, not
  estimated; commit transcripts as evidence).
- **DocuShell in production-shape:** verification reports stored for real parse jobs; ≥1
  answer-release gate live; friction log actively dispositioned.
- **Sticky-socket installs:** repos running the CI Action (and MCP quickstart completions once
  NIP-2 unblocks).
- **Trust benchmark:** internal report complete; publication decision made either way.
- **OSS health:** median first response on public issues <48h (PRD §3.3); one external
  contributor PR landed via the NIP-7.3 fast path; one co-maintainer conversation started.
- **Governance cost:** ≤2 governance documents per release train.

---

## 9. Completion and handoff protocol

When the last P0/P1 task is `done` (or `dropped` with decider notes):

1. Write `docs/validation/nip-1-closeout-<date>.md` summarizing ledger state, metric readings,
   and the friction-log disposition table.
2. Propose NIP-2 (the successor plan) as a fresh document; do not extend this one past its
   scope — plans that grow forever stop being picked up first.
3. Update `AGENTS.md` to point new agents at the successor plan.

*Maintained by: product/decider. Implementers update §7; only the decider edits §2 and §3.*
