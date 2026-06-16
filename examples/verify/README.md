# WS-VERIFY-ALPHA Demo

This directory contains verify-alpha fixtures, citations, and golden reports.

## Native Ethos Grounding

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --out verification_report.json
```

Expected result: `all_evidence_grounded: true`. The claims verify a quote, a table cell, and
page-level presence against native Ethos document JSON.

For a compact text view of the same check outcomes, use `--format summary`. JSON remains the
default and canonical verification report format.

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --format summary
```

The summary includes the verification config hash, declared grounding capabilities, check counts,
report warnings, non-grounded check reasons, and deterministic diagnostic lines.

`make verify-alpha` also checks summary output for a native ungrounded citation set, including
the non-grounded reason and diagnostic lines.

## Native Split Quote Grounding

```bash
ethos verify examples/verify/native_split_quote_document.json \
  --citations examples/verify/native_split_quote_citations.json \
  --out verification_report.json
```

Expected result: `all_evidence_grounded: true`. The quote locator points at the second adjacent
text element, and the verifier grounds the claim only through the explicit adjacent-element rule.

## Native Ethos Ungrounded Citations

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_ungrounded_citations.json \
  --out verification_report.json
```

Expected result: `all_evidence_grounded: false`. The quote check reports `text_mismatch`, and
the missing element check reports `element_not_found`.

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

## OpenDataLoader-Style Missing Element

```bash
ethos verify examples/verify/opendataloader.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_not_found_citations.json \
  --out verification_report.json
```

Expected result: `all_evidence_grounded: false`, check status `not_found`, reason
`element_not_found`, and the same `capability_limited` warning as the grounded synthetic fixture.

## Stale Fingerprint

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_stale_citations.json \
  --out verification_report.json
```

Expected result: `fingerprint_stale: true`, check status `stale`, and
`all_evidence_grounded: false`. Non-grounded checks include a `reason` label such as
`stale_fingerprint`, `text_mismatch`, or `missing_table_capability`.

## Capability-Limited Table Claim

```bash
ethos verify examples/verify/opendataloader_no_tables.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_table_cell_citations.json \
  --out verification_report.json
```

Expected result: check status `capability_blocked`, warning `capability_limited`, and
`all_evidence_grounded: false`.

## Reason Labels

Non-grounded checks may include a stable `reason` label:

| Reason | Meaning |
| --- | --- |
| `stale_fingerprint` | Citation fingerprint differs from the grounding source fingerprint. |
| `text_mismatch` | Target text did not match the claimed text under the active literal matcher. |
| `missing_table_capability` | The claim needs table-cell lookup, but the grounding source does not expose tables. |
| `missing_source_fingerprint` | Citations were fingerprint-pinned, but the grounding source did not declare one. |
| `missing_citation_fingerprint` | The active staleness policy requires citation fingerprints, but the input omitted one. |
| `unknown_coordinate_origin` | A bbox locator was used with a source whose coordinate origin is unknown. |
| `element_not_found` | The cited element id was not found in a source that exposes element ids. |
| `table_not_found` | The cited table id was not found in a source that exposes tables. |
| `table_cell_not_found` | The cited table exists, but the cited cell address was not found. |
| `unsupported_claim_kind` | The claim kind is unsupported by this verifier or the active config. |

## Usage Diagnostics

Malformed citations are covered as usage errors. `invalid_table_cell_citations.json` must exit
`2` because a table-cell claim is missing `table_id` and `cell`. `invalid_bbox_citations.json`
must exit `2` because a bbox locator is missing a page or another target locator.

Malformed OpenDataLoader-style grounding inputs are also covered as usage errors.
`opendataloader_malformed_bbox.json` must exit `2` because its bbox is inverted.
`opendataloader_unknown_page.json` must exit `2` because an element references a page that
the input does not declare.

The OpenDataLoader fixtures are synthetic and limited to the adapter's documented alpha
subset. They are not real pinned OpenDataLoader artifacts. Golden reports live in
`examples/verify/goldens/` and are covered by the CLI verification test.

Real pinned OpenDataLoader output lives under `fixtures/foreign/opendataloader/real/`. That
package includes both a grounded citation set and an ungrounded citation set so
`make verify-alpha` exercises the accept and reject paths against a real foreign parser output.
The same target also runs native Ethos verification with `--crop-dir`, checking that emitted
crop descriptor JSON conforms to `schemas/ethos-crop-descriptor.schema.json`.
When a native Ethos document is bound to its original PDF, `--crop-source-pdf` additionally
emits PNG crop artifacts referenced and hashed from those descriptors.
