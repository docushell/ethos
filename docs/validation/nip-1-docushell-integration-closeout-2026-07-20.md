# NIP-1 DocuShell Integration Closeout — 2026-07-20

Status: **accepted and complete**. The decider accepted this record on 2026-07-20 and cleared the
current DocuShell integration blocker.

## Source Binding

- Ethos source: `15c7c4a5235a9c25732ba9138c26ec0c465105a7`
- DocuShell integration source: `74cf59984587d742e592ca32b508f842b91fe217`
  (`codex/nip-1-2-docushell-vendoring`)
- Public Ethos CLI consumed by DocuShell: `0.3.0`, Linux x64 archive and executable sha256-pinned
- Caller-provided PDFium: Chromium profile `7881` / PDFium `151.0.7881.0`, Linux x64
- Verification report schema consumed by the integration: `1.0.0`
- Grounding adapter: `opendataloader-json`

The DocuShell checkout contained later uncommitted test/type-alignment follow-ups during final
acceptance. They did not change the committed NIP-1.2–1.5 worker, report, crop, or routing
implementation bound above. No private Ethos API was used.

## Delivered Integration

- NIP-1.2: the worker-only image installs sha256-pinned Ethos and caller-provided PDFium assets;
  checksum, platform, and missing-artifact failures stop the build.
- NIP-1.3: parse jobs emit deterministic citation input, run the public OpenDataLoader grounding
  adapter, preserve exit `1` reports, fail on exit `>=2`, and store the canonical report.
- NIP-1.4: Evidence Chat applies the v1.1 answer-release support policy above canonical citation
  grounding; missing or unsupported support never becomes an implicit pass.
- NIP-1.5: evidence-required jobs conservatively map foreign evidence to native elements and
  render source-bound crops; missing PDFium, malformed output, ambiguity, or zero safe mappings
  fails closed.
- NIP-1.6: all eleven integration rough edges are recorded and dispositioned. Ten are resolved.
  FR-8 remains an explicit future parser-aware crop-projection product gap; the current mapping
  stays conservative and never guesses an element.

Ethos verifies citation grounding against supplied source representations. This integration does
not establish semantic truth and makes no parser-quality claim.

## Validation

Focused DocuShell integration suite:

```sh
npx mocha tests/parse-pdf/ethos-vendor-manifest.test.js \
  tests/parse-pdf/ethos-verification.test.js \
  tests/parse-pdf/ethos-crops.test.js \
  tests/evidence/ethos-answer-release.test.js \
  tests/evidence/evidence-core.test.js \
  --timeout 15000 --exit
```

Result: `29 passing`.

Affected DocuShell build:

```sh
npm run build:docs
```

Result: passed; the production documentation application generated 70 routes.

Operator-approved real born-digital PDF acceptance:

```sh
REAL_PDF_ACCEPTANCE_REPORT=/tmp/docushell-nip-1-5-acceptance.json \
  npm run acceptance:parse-pdf:real -- <one-page-born-digital.pdf>
```

Result: one job passed in 3,498 ms; `38/38` evidence anchors bound; `38/38` canonical verification
checks grounded; `evidence_verified=true`; `usable_for_verified_citations=true`; report
fingerprint not stale; every advertised artifact download returned HTTP 200 with non-empty bytes;
zero failures. The local API credential is intentionally not recorded.

The Ethos task baseline also passed at the bound source: `cargo build --locked --workspace`,
`cargo test --locked --workspace`, `make verify-alpha`, both claims gates, and `git diff --check`.

## Boundary and Friction Disposition

- No approved claim string in `README.md` or `docs/public-boundary-claims.json` changed.
- No registry, tag, GitHub Release, hosted-service, or public benchmark action ran.
- PDFium remains caller-provided.
- DocuShell remains a private first consumer; this record does not approve public adoption claims.
- The friction log contains 11 entries: 5 fix-in-Ethos, 6 documentation/design dispositions,
  10 resolved, and 1 open product gap (FR-8) with an explicit fail-closed interim behavior.

## Decider Review

- [x] Accepted 2026-07-20; clear the DocuShell integration blocker in
      `docs/execution-status.md`.
- [ ] Amendments required: —
