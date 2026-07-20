# DocuShell Integration Friction Log (NIP-1.6)

Collection status: complete for NIP-1.1–1.5 (NIP-1.6 done 2026-07-19). Open entry statuses below
are dispositioned Ethos product gaps, not missing decisions; they remain assigned to their owning
roadmap tasks. Every point of confusion, missing capability, or manual step hit while integrating
Ethos into DocuShell is recorded here. Because DocuShell uses public surfaces only, every entry
is friction an external adopter would also hit.

## Entry format

```
### FR-<n> — <short title>
Date: YYYY-MM-DD · Found during: <NIP task or activity>
What happened: <1–3 sentences, concrete>
Disposition: fix-in-ethos (→ NIP task id) | document (→ doc/PR) | wontfix-by-design (reason)
Status: open | resolved (date, evidence)
```

Dispositions are assigned by the decider or the implementing agent with a decider note.

---

### FR-1 — No published TypeScript types for the verification report
Date: 2026-07-19 · Found during: NIP-1.1 integration design review
What happened: DocuShell hand-mirrors the verification-report and answer-release shapes in
`packages/evidence/src/ethos-answer-release.ts`. There is no published types package or
generated-from-schema artifact, so consumer types can silently drift from `schemas/`.
Disposition: fix-in-ethos → candidate new task (generate TS types from the JSON Schemas and
publish, e.g. `@docushell/ethos-types`, or ship a `.d.ts` in the existing npm package). Add to
NIP-4 scope when picked up.
Status: resolved (2026-07-19, NIP-4.5 generates report and citation-emission declarations from
the canonical schemas, includes them in the existing `@docushell/ethos-pdf` release candidate,
and compiles the packaged report type against DocuShell's actual evidence interface)

### FR-2 — Caller-provided PDFium must be hand-wired into the consumer image
Date: 2026-07-19 · Found during: NIP-1.2 design (worker image)
What happened: vendoring the CLI is not enough for parse/crop paths; the consumer must also
replicate the `scripts/fetch-pdfium.sh` pin logic inside its Docker build and export
`ETHOS_PDFIUM_LIBRARY_PATH`. Two artifacts to pin, two failure modes to debug.
Disposition: fix-in-ethos → NIP-5.1 (`ethos doctor` + pinned fetch path) and NIP-5.2
(ADR-0015 bundling proposal).
Status: resolved for the caller-provided path (2026-07-19, NIP-5.1 adds identical CLI/package
guidance, executable sha256-pinned fetch tooling, and a copy-paste Linux x64 worker stage in
`docs/pdfium-manual-setup.md`; opt-in bundling remains a separate NIP-5.2 decision)

### FR-3 — CLI vendoring requires manual sha256 bookkeeping; no container base layer
Date: 2026-07-19 · Found during: NIP-1.2 design (worker image)
What happened: consumers must download the release archive, record its sha256, and re-verify on
every version bump (same pattern the npm package's `vendor/manifest.json` implements
internally). Ethos publishes no container image or reusable Docker layer that would make this a
one-line `FROM`/`COPY`.
Disposition: document (Dockerfile snippet in `docs/integrations/docushell.md` follow-up);
re-evaluate an official OCI artifact after the ADR-0015 decision (would count as a
first-of-class surface under `docs/release-lane-v2.md`).
Status: resolved (2026-07-19, copy-paste consumer pattern and pin sources documented in
`docs/integrations/docushell.md`; DocuShell implementation is
`docker/parse-pdf/{Dockerfile,ethos-vendor.json,fetch-ethos-vendor.sh}`)

### FR-4 — Linux x64 CLI builds need an explicit Docker platform
Date: 2026-07-19 · Found during: NIP-1.2 implementation (worker image)
What happened: Ethos v0.3.0 publishes a Linux x64 CLI but no Linux arm64 CLI. On Apple Silicon,
an otherwise ordinary Docker build can select an arm64 base and produce an image containing an
unrunnable x64 binary unless the consumer explicitly fixes the stage platform.
Disposition: document (linux/amd64 is explicit in the consumer Dockerfile pattern) and fail
closed (the vendoring script rejects a non-Linux-x64 build stage instead of skipping its smoke
check).
Status: resolved (2026-07-19, DocuShell Docker stages and installer platform check; covered by
`tests/parse-pdf/ethos-vendor-manifest.test.js`)

### FR-5 — Exit 1 requires the fail-on-ungrounded flag
Date: 2026-07-19 · Found during: NIP-1.3 implementation (verify lane)
What happened: the abbreviated integration command omitted `--fail-on-ungrounded`, but the
documented `0` grounded / `1` ungrounded-with-report behavior only applies when that flag is
present. Without it, an ungrounded report exits `0` and a consumer can misclassify the outcome.
Disposition: document (the integration contract now gives the exact command and exit handling;
the DocuShell helper always supplies the flag and cross-checks the exit code against the report).
Status: resolved (2026-07-19, `docs/integrations/docushell.md` and
`tests/parse-pdf/ethos-verification.test.js`)

### FR-6 — No public helper converts parser evidence into citation input
Date: 2026-07-19 · Found during: NIP-1.3 implementation (verify lane)
What happened: Ethos publishes the citation JSON Schema and verifier, but no public helper yet
converts foreign-parser retrieval/evidence records into that schema. DocuShell had to implement
a small deterministic mapping from its emitted evidence refs to quote/table-cell claims.
Disposition: fix-in-ethos → NIP-4.1/NIP-4.2 (freeze the emission schema and ship public helpers);
keep the DocuShell mapping limited to the existing public citation/report contracts until then.
Status: resolved (2026-07-19, NIP-4.1 froze citation-emission callback schema v1.0.0 and NIP-4.2
added the dependency-free `ethos_pdf.emit` public helpers with LangChain/LlamaIndex retrieval
adapters, fail-closed vocabulary hydration, and deterministic JSON bytes. DocuShell's existing
mapping remains contract-compatible and does not need a package change merely to close the
missing-Ethos-helper gap.)

### FR-7 — Type drift hid the answer-release v1.1 support axis
Date: 2026-07-19 · Found during: NIP-1.4 implementation (answer-release gate)
What happened: DocuShell's hand-maintained TypeScript envelope still represented schema `1.0.0`
and had no `claim_support` field after the public Ethos contract advanced to `1.1.0`. The consumer
could therefore release grounded source facts without the contract's required semantic-support
decision until it manually compared the repository fixture.
Disposition: fix-in-ethos → NIP-4.5 together with FR-1 (publish generated TypeScript schema types
and versioned contract fixtures); interim DocuShell test copies the v1.1 fixture and compares the
complete decision deterministically.
Status: resolved (2026-07-19, NIP-4.5 declarations include the `1.1.0` support axis and compile
against DocuShell's aligned answer-release interface)

---

### FR-8 — `crop_element` cannot consume a foreign-parser document
Date: 2026-07-19 · Found during: NIP-1.5 implementation (crop inspection)
What happened: the public crop contract accepts only a native Ethos document, while DocuShell's
bound evidence comes from OpenDataLoader. Producing a source-bound crop therefore requires a
second native parse of the same PDF plus conservative text/table mapping; ambiguous mappings
must remain unavailable rather than being guessed.
Disposition: document/decider follow-up. NIP-4.2 keeps citation emission parser-neutral and does
not project foreign evidence into native crop elements: source-ID hydration is exact, while crop
projection would require a distinct parser-aware matching contract. The interim fail-closed
mapping remains documented in `docs/integrations/docushell.md`; adding a projection surface needs
a future ledger task/decision rather than an implicit expansion of citation emission.
Status: open (explicitly out of NIP-4.2's narrow emission-helper scope)

---

### FR-9 — Naive schema compilation widened conditional contracts
Date: 2026-07-19 · Found during: NIP-4.5 TypeScript declaration generation
What happened: the schema compiler represented the verification report's conditional version
rule as an open root object and reduced citation locator exclusivity to empty object unions. A
naively generated declaration would therefore accept invalid extra fields and locator-free
claims even though the JSON Schemas reject them.
Disposition: fix-in-ethos → NIP-4.5 (project the report's allowed schema versions and expand the
three exclusive locator alternatives before deterministic declaration compilation; runtime JSON
Schema validation remains authoritative).
Status: resolved (2026-07-19, strict negative compile fixture rejects unknown report versions and
locator-free claims; generated declarations are byte-identical across two runs)

---

### FR-10 — DocuShell requires schema-optional answer-release notes
Date: 2026-07-19 · Found during: NIP-4.5 consumer compatibility compilation
What happened: the generated `EthosAppAnswerReleaseDecision` correctly represents `notes` as
optional, but DocuShell's hand-maintained interface requires `notes: string[]`. A valid canonical
decision that omits notes therefore cannot be assigned to the consumer type.
Disposition: document (align DocuShell's mirror to `notes?: string[]`, then compile the packaged
report and answer-release declarations against `packages/evidence`).
Status: resolved (2026-07-19, DocuShell's mirror now uses `notes?: string[]`; the packaged
verification-report and answer-release declarations compile against the actual consumer types,
and the focused evidence suite passes)

---

### FR-11 — Real acceptance requires the documented Redis prerequisite
Date: 2026-07-20 · Found during: NIP-1.5 real-PDF acceptance
What happened: starting `npm run dev:all` from a stopped local environment exited when Redis was
not listening on port 6379. `CLAUDE.md` already lists local Redis as a development prerequisite;
after starting an ephemeral Redis instance, the unchanged stack completed the acceptance run.
Disposition: document (existing `CLAUDE.md` prerequisite is sufficient; no product change).
Status: resolved (2026-07-20, real born-digital PDF acceptance passed 1/1 with 38/38 anchors
bound, 38/38 verification checks grounded, all artifact downloads successful, and zero failures)

---

## Closeout summary (filled at NIP-1.7)

| Total entries | fix-in-ethos | document | wontfix | resolved |
| --- | --- | --- | --- | --- |
| 11 | 5 | 6 | 0 | 10 |
