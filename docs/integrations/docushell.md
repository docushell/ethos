# Integration Contract: DocuShell (first consumer)

Status: active. Created: 2026-07-19. Integration closeout accepted 2026-07-20.
This document is the template for future `docs/integrations/<consumer>.md` files.

## Why this document exists

DocuShell is the first production-shaped consumer of Ethos. Because Ethos is open source, the
DocuShell integration doubles as the integration proof for any external business: DocuShell may
use **public Ethos surfaces only**. If DocuShell needs anything not available on a public
surface, that is an Ethos product gap — it goes into the
[friction log](docushell-friction-log.md), never into a private workaround.

## Consumer profile

- DocuShell: private npm-workspaces monorepo (Next.js apps + Express/BullMQ services).
- Integration point: `services/parse-pdf` (Express API + worker; OpenDataLoader hybrid backend
  `docling-fast`), plus the evidence layer in `packages/evidence`.
- DocuShell currently mirrors Ethos verification-report and answer-release types in TypeScript
  (`packages/evidence/src/ethos-answer-release.ts`, `openai-chat-evidence.ts`) and implements
  the release policy from `docs/app-answer-release-contract.md`. The v0.4.0 candidate adds
  schema-generated declarations to the npm candidate so that mirror can be retired after
  publication.

## Surfaces DocuShell consumes (all public)

| Surface | Contract |
| --- | --- |
| CLI binary | GitHub Release Linux x64 artifact, sha256-pinned in the DocuShell worker image. Version recorded below. |
| PDFium | Caller-provided, installed in the worker image using the exact pins from `docs/pdfium-profile.md` via `scripts/fetch-pdfium.sh`; exposed via `ETHOS_PDFIUM_LIBRARY_PATH`. |
| Verification | `ethos verify <source> --citations <file> --grounding opendataloader-json --out <report> --fail-on-ungrounded`; canonical report JSON per `schemas/`. |
| Evidence anchoring | `ethos evidence anchor` JSON reports. |
| Crops | `ethos crop_element` descriptors + rendered crop artifacts (PDFium-backed). |
| Answer release | `proof_summary` + `app_answer_release_decision` semantics per `docs/app-answer-release-contract.md`. |
| TypeScript declarations | Schema-generated verification-report, citation-emission, and app answer-release declarations in the `@docushell/ethos-pdf` package's root type entry. Runtime JSON Schema validation remains authoritative. |
| Exit codes / errors | Stable exit-code and JSON error-envelope contract as documented for the CLI and Python wrapper (0 grounded; 1 ungrounded with report; ≥2 error — fail closed). |

Pinned versions (update on every DocuShell bump):

| Item | Version | Pinned at |
| --- | --- | --- |
| `ethos` CLI artifact | v0.5.0 (Linux x64) | 2026-08-11 — vendored in the DocuShell parse-pdf worker image (`docker/parse-pdf/ethos-vendor.json`) |
| PDFium (caller-provided) | `chromium/7881` (PDFium 151.0.7881.0, Linux x64) | 2026-07-19 — installed by the same image, `ETHOS_PDFIUM_LIBRARY_PATH` set at build |
| Report schema | as shipped in v0.5.0 (`schema_version` 1.0.0; 1.1.0 exists but requires an opt-in `--config` with `hardening`, which DocuShell does not pass) | 2026-08-11 |
| Grounding adapter | `opendataloader-json` | 2026-07-19 |
| Citation emission callback | v1.0.0 (not yet consumed) | 2026-07-19 — frozen contract with delivered Python helpers |
| TypeScript declarations | published in `@docushell/ethos-pdf@0.5.0` (`types/verification-report.d.ts`) | 2026-08-11 — generated from the canonical schemas; carries `dispersion`, `provenance`, `resolved_element_ids`, and `schema_version: "1.0.0" \| "1.1.0"` |

Known consumer gaps, recorded because they are what an external adopter would also hit:

- **The generated declarations did not replace the hand mirror.** FR-1 anticipated retiring
  `packages/evidence/src/ethos-answer-release.ts` once schema-generated types shipped. They shipped;
  the mirror did not retire. `packages/evidence/src/index.ts` re-exports it, so the hand-written
  `EthosVerificationReportCheck` — which carries neither the hardening fields nor `evidence_tier` —
  is the type DocuShell's release logic actually sees. Drift between the two is unguarded.
- **`evidence_tier` is not reachable at this pin.** It lands in v0.6.0 alongside `attestation`, so a
  consumer writing a tier-based demotion against v0.5.0 output reads `undefined` and the demotion
  silently never fires. Consumers gating on tier need the 0.6.0 bump, not a config change.
- **`capability_limits` is never empty on the `opendataloader-json` path.** The adapter declares
  `spans: false`, `char_offsets: false` and `coordinate_origin: unknown`, so every report carries
  `missing_spans`, `missing_char_offsets` and `unknown_coordinate_origin`. Any consumer rule keyed on
  that array being empty is unsatisfiable. Limits describe the adapter, not the document.

### Consumer Dockerfile pattern (friction entry FR-3)

DocuShell vendors both artifacts in a dedicated build stage with sha256 pins duplicated into a
consumer-side manifest (`docker/parse-pdf/ethos-vendor.json`), verified before extraction and
after install, failing the build closed on any mismatch. The shape any consumer can copy:

```dockerfile
# Stage: download + verify the pinned Ethos CLI and PDFium (linux/amd64 only —
# Ethos publishes no Linux arm64 CLI artifact; use --platform linux/amd64).
FROM --platform=linux/amd64 node:20-slim AS ethos-vendor
RUN apt-get update && apt-get install -y ca-certificates curl --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY ethos-vendor.json fetch-ethos-vendor.sh ./
# fetch-ethos-vendor.sh: verify archive sha256 BEFORE extraction, verify
# binary/library sha256 after, preserve license notices, and install to
# /opt/ethos. Fail closed.
RUN ./fetch-ethos-vendor.sh ./ethos-vendor.json

# Final image: copy the verified tree, expose the two env vars Ethos needs.
FROM --platform=linux/amd64 <your-runtime-base>
COPY --from=ethos-vendor /opt/ethos /opt/ethos
ENV ETHOS_CLI_PATH=/opt/ethos/bin/ethos
ENV ETHOS_PDFIUM_LIBRARY_PATH=/opt/ethos/pdfium/lib/libpdfium.so
```

Pins to duplicate into the consumer manifest: the CLI release-asset and binary sha256 values
(the same values recorded in `packages/npm/ethos-pdf/vendor/manifest.json`) and the PDFium
archive/library sha256 values from `docs/pdfium-profile.md` / `scripts/fetch-pdfium.sh`.
Consumers must re-sync these pins by hand on every version bump (friction entries FR-2/FR-3/FR-4).

## Compatibility promise (Ethos → DocuShell and all consumers)

- Within 0.x: verification-report schema changes are at most semver-minor, called out
  explicitly in `CHANGELOG.md`, and never silently reshape existing fields.
- Any PR changing report or emission schemas must add a same-PR entry to the
  [friction log](docushell-friction-log.md) noting the required consumer-side update.
- Exit codes and the error envelope are stable; additions only.
- Backward-incompatible report changes require the full v1 release lane
  (`docs/release-lane-v2.md`) and a major/minor version decision.

## Integration architecture rules (DocuShell side)

- Ethos runs in the **worker lane only** (BullMQ workers / Express services), never inside a
  Next.js request handler — consistent with DocuShell's own CPU-work golden rule.
- Verification failure is a job-level error state, not a silent pass (fail closed), consistent
  with DocuShell's billing/security fail-closed rule.
- Reports are stored with the job record so status/download routes can serve them under the
  existing ownership/expiry checks; crop artifacts follow DocuShell's retention/purge windows.

### Parse-job verification lane

After OpenDataLoader produces JSON, the parse worker deterministically projects its selected
evidence refs into quote/table-cell citations and runs the public CLI with
`--grounding opendataloader-json --fail-on-ungrounded`. The canonical report is stored as
`<document>.ethos-verification-report.json` and exposed through the job's
`ethos_verification_report_download` link under the normal ownership and expiry checks.

- Exit `0`: report is present and `all_evidence_grounded=true`; job continues.
- Exit `1`: report is present and ungrounded; job continues with the report and an explicit
  `ethos_verification.status=ungrounded` rollup. It is never retried to obtain a different result.
- Exit `>=2`, missing CLI, missing report, malformed report, or incomplete citation emission:
  the parse job fails with `phase=citation_verification` instead of silently passing.

The worker stores only the canonical report as a companion artifact; its checks contain the
submitted claims, and the deterministic citation input is tested byte-identically across runs.
This verifies citation grounding, not the semantic truth of parser text.

### Answer-release gate

The server-owned Evidence Chat answer path derives `proof_summary` from the canonical Ethos
report, maps reusable check IDs back to stable application claim IDs, and then applies
DocuShell-owned `question_relevance`, `claim_type`, and `claim_support` labels before returning
answer text. The decision envelope follows
`ethos.app_answer_release_decision.v1` schema version `1.1.0`.

- Grounded, relevant `source_fact` claims with `claim_support=supported` may enter the final answer.
- Grounded synthesis remains in the review surface.
- Omitted or `not_evaluated` claim support is held for review; it is never implicit support.
- `unsupported` and `contradicted` claims are blocked even when their citations are grounded.
- Non-reusable checks, stale fingerprints, missing CLI capability, and malformed reports block
  release rather than falling back to model output.

The DocuShell fixture test reproduces the checked-in Ethos
`examples/app-answer-release/{claims,proof-summary,expected-decision}.json` decision and emits
byte-identical JSON across two runs. The canonical verification report remains the grounding
audit artifact; the answer-release envelope records application policy above it.

### Crop inspection lane

Evidence-required parse jobs render inspectable citation crops while the original PDF is still
available in the parse worker. Because the public `crop_element` contract accepts native Ethos
documents rather than foreign-parser documents, the worker first runs the pinned CLI's native
`doc parse` over the same source PDF. It then maps each bound OpenDataLoader evidence reference
to a unique native element on the same page using normalized exact text (or a uniquely
containing native element). Table cells map only when their exact text identifies one native
table and one table element. Missing or ambiguous mappings are recorded as unavailable; the
worker never guesses an element ID.

For up to 12 bound evidence references, the worker submits a canonical
`ethos.crop_element_request.v1` with `rendering=rendered`, the native document fingerprint, and
the sha256 fingerprint of the caller's PDF. It validates the returned descriptor, PNG signature,
source fingerprint, and rendered sha256 before storing a deterministic
`docushell.ethos_crop_bundle.v1` JSON companion artifact. The bundle embeds the validated PNGs
so it follows the existing job ownership, expiry, one-shot download, and purge behavior as one
artifact.

Evidence Chat requires this bundle during setup and indexes crops by the stable DocuShell
evidence ID. The inspector displays the Ethos-rendered PNG for a cited region. A citation with
an explicitly unavailable mapping retains the browser page highlight with a warning that it is
not an Ethos-rendered artifact. Missing CLI/PDFium capability, malformed native output, invalid
descriptor/PNG, no bound evidence, or zero safely mapped crops fails the evidence-required parse
job with `phase=crop_inspection`; it never silently falls back to browser rendering.

The integration test runs crop production twice over identical inputs and compares the emitted
bundle bytes, checks request-reference compatibility with Ethos's committed schema example, and
covers partial mapping plus missing-PDFium failure behavior.

## Integration history

The vendored CLI, verification lane, answer-release gate, crop inspection, friction log, and
closeout were completed in sequence. The dated validation record retains their historical task
IDs and evidence bindings.

## Friction log process

Every integration step records friction in
[`docushell-friction-log.md`](docushell-friction-log.md). Entry format and dispositions are
defined there. An empty log at closeout is treated as "didn't look," not "no friction."
