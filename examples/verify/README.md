# WS-VERIFY-ALPHA Demo

This directory contains the first parser-agnostic verification demo.

## Native Ethos Grounding

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --out verification_report.json
```

Expected result: `all_evidence_grounded: true`. The claims verify a quote, a table cell, and
page-level presence against native Ethos document JSON.

## OpenDataLoader-Style Grounding

```bash
ethos verify examples/verify/opendataloader.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_grounded_citations.json \
  --out verification_report.json
```

Expected result: `all_evidence_grounded: true` with a top-level `capability_limited`
warning. The warning is intentional: the synthetic OpenDataLoader-style fixture has no
fingerprint, spans, character offsets, or known coordinate origin, but its element and table
evidence can still ground these claims.

## Stale Fingerprint

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_stale_citations.json \
  --out verification_report.json
```

Expected result: `fingerprint_stale: true`, check status `stale`, and
`all_evidence_grounded: false`.

## Capability-Limited Table Claim

```bash
ethos verify examples/verify/opendataloader_no_tables.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_table_cell_citations.json \
  --out verification_report.json
```

Expected result: check status `capability_blocked`, warning `capability_limited`, and
`all_evidence_grounded: false`.

The OpenDataLoader fixtures are synthetic and limited to the adapter's documented alpha
subset. They are not real pinned OpenDataLoader artifacts. Golden reports live in
`examples/verify/goldens/` and are covered by the CLI verification test.

Real pinned OpenDataLoader output lives under `fixtures/foreign/opendataloader/real/`. That
package includes both a grounded citation set and an ungrounded citation set so
`make verify-alpha` proves the accept and reject paths against a real foreign parser output.
