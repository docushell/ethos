# Verify Alpha Demo

## Verification Loop

Ethos verifies whether AI citations are grounded in document evidence.

This is a citation grounding check, not a semantic-truth system: Ethos does not claim semantic
entailment, factual truth, arithmetic correctness, or answer quality. The alpha loop is the
repeatable `make verify-alpha` path:

- native Ethos JSON citation checks can pass against checked-in document evidence
- OpenDataLoader-style JSON can enter the same verification loop through a grounding adapter
- real pinned OpenDataLoader 2.4.7 output has both grounded and ungrounded citation cases
- native and synthetic OpenDataLoader fixtures cover missing cited elements
- malformed citation inputs and malformed OpenDataLoader-style grounding inputs return usage
  diagnostics with exit code `2`
- `--fail-on-ungrounded` turns the report into a CI/agent gate with exit code `1` when evidence is not fully grounded
- native Ethos verification can emit deterministic crop descriptor artifacts with `--crop-dir`
- every demo report is compared against a golden and regenerated twice to check byte-identical output
- crop descriptor files are regenerated twice, compared byte-for-byte, validated against schema, and checked against the committed descriptor example

Ethos verifies document evidence for AI systems. The deterministic parser is one grounding
source; foreign parser output can be another grounding source through an adapter.

This demo uses small checked-in fixtures so the behavior is deterministic and easy to audit.

## Native Ethos JSON

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --out /tmp/ethos-native-verification-report.json
```

Expected outcome:

- `grounding.parser.name` is `ethos`
- `all_evidence_grounded` is `true`
- the report contains grounded quote, table-cell, and presence checks

Golden report:

```text
examples/verify/goldens/native_grounded_report.json
```

For terminal review, `--format summary` emits a compact text view with the verification config
hash, declared grounding capabilities, check counts, warnings, and non-grounded check reasons.
The JSON report remains the canonical artifact.
`make verify-alpha` checks this summary path for a native ungrounded citation set.

## Native Ethos Ungrounded Citations

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_ungrounded_citations.json \
  --out /tmp/ethos-native-ungrounded-report.json
```

Expected outcome:

- `all_evidence_grounded` is `false`
- one quote check status is `mismatch` with reason `text_mismatch`
- one presence check status is `not_found` with reason `element_not_found`

Golden report:

```text
examples/verify/goldens/native_ungrounded_report.json
```

## OpenDataLoader-Style JSON

```bash
ethos verify examples/verify/opendataloader.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_grounded_citations.json \
  --out /tmp/ethos-odl-verification-report.json
```

Expected outcome:

- `grounding.parser.adapter` is `opendataloader-json`
- `all_evidence_grounded` is `true`
- `warnings` includes `capability_limited`
- `capability_limits` lists the missing metadata from this foreign source

The capability warning is not a failure. It is the trust-layer contract: Ethos states exactly
which evidence capabilities the source lacks instead of silently pretending the parser can do
more than it can.

Golden report:

```text
examples/verify/goldens/opendataloader_grounded_report.json
```

## OpenDataLoader-Style Missing Element

```bash
ethos verify examples/verify/opendataloader.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_not_found_citations.json \
  --out /tmp/ethos-odl-not-found-report.json
```

Expected outcome:

- `grounding.parser.adapter` is `opendataloader-json`
- `all_evidence_grounded` is `false`
- the presence check status is `not_found` with reason `element_not_found`
- `warnings` includes `capability_limited`

Golden report:

```text
examples/verify/goldens/opendataloader_not_found_report.json
```

## Real OpenDataLoader JSON

```bash
ethos verify fixtures/foreign/opendataloader/real/opendataloader-output.json \
  --grounding opendataloader-json \
  --citations fixtures/foreign/opendataloader/real/citations.json \
  --out /tmp/ethos-real-odl-verification-report.json
```

Expected outcome:

- `grounding.parser.name` is `opendataloader-pdf`
- `grounding.parser.version` is `unknown` because OpenDataLoader JSON does not carry it
- `all_evidence_grounded` is `true`
- quote, value, and presence claims are grounded against real OpenDataLoader 2.4.7 output

Fixture package:

```text
fixtures/foreign/opendataloader/real/
```

## Real OpenDataLoader Ungrounded Citation

```bash
ethos verify fixtures/foreign/opendataloader/real/opendataloader-output.json \
  --grounding opendataloader-json \
  --citations fixtures/foreign/opendataloader/real/ungrounded_citations.json \
  --out /tmp/ethos-real-odl-ungrounded-report.json
```

Expected outcome:

- `grounding.parser.name` is `opendataloader-pdf`
- the value claim status is `mismatch`
- `all_evidence_grounded` is `false`
- a value substring does not ground against a longer cited paragraph
- adding `--fail-on-ungrounded` exits `1`

Golden report:

```text
fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json
```

## Stale Fingerprint

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_stale_citations.json \
  --out /tmp/ethos-stale-verification-report.json
```

Expected outcome:

- `fingerprint_stale` is `true`
- the check status is `stale`
- `all_evidence_grounded` is `false`

Golden report:

```text
examples/verify/goldens/native_stale_report.json
```

## Capability-Limited Foreign Output

```bash
ethos verify examples/verify/opendataloader_no_tables.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_table_cell_citations.json \
  --out /tmp/ethos-capability-limited-report.json
```

Expected outcome:

- the table-cell check status is `capability_blocked`
- `capability_limits` includes `missing_tables`
- `all_evidence_grounded` is `false`

Golden report:

```text
examples/verify/goldens/opendataloader_capability_limited_report.json
```

## CI And Agent Gate

Use `--fail-on-ungrounded` when an automated workflow should fail if verification completes
but any cited evidence is stale, missing, mismatched, unsupported, or capability-blocked.

```bash
ethos verify examples/verify/opendataloader.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_grounded_citations.json \
  --fail-on-ungrounded \
  --out /tmp/ethos-verification-report.json
```

Exit behavior:

- `0`: verification completed and all requested evidence is grounded
- `1`: verification completed, but not all requested evidence is grounded
- `2`: invalid input, malformed citations, adapter failure, or another usage error

## Malformed Citation Inputs

The harness also checks citation validation failures:

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/invalid_table_cell_citations.json
```

Expected outcome: exit code `2` with a diagnostic that the table-cell citation must include
`table_id` and `cell`.

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/invalid_bbox_citations.json
```

Expected outcome: exit code `2` with a diagnostic that the bbox citation requires a page unless
another target locator is present.

## Malformed OpenDataLoader-Style Inputs

The harness also checks adapter input validation failures:

```bash
ethos verify examples/verify/opendataloader_malformed_bbox.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_grounded_citations.json
```

Expected outcome: exit code `2` with a diagnostic that the bbox is malformed.

```bash
ethos verify examples/verify/opendataloader_unknown_page.json \
  --grounding opendataloader-json \
  --citations examples/verify/opendataloader_grounded_citations.json
```

Expected outcome: exit code `2` with a diagnostic that an element references an undeclared page.

## Crop Descriptors

Native Ethos document grounding can emit deterministic crop descriptor JSON files for each
verified evidence region:

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_grounded_citations.json \
  --crop-dir /tmp/ethos-crops \
  --out /tmp/ethos-native-verification-report.json
```

Expected outcome:

- `evidence.crop_ref` points to files under the requested crop directory
- crop descriptor files validate against `schemas/ethos-crop-descriptor.schema.json`
- crop descriptor files bind `document_fingerprint`, `page`, `bbox`, and `check_ids`
- native Ethos `crop_ref` filenames are stable logical evidence references derived from
  document fingerprint, check id, and page; the descriptor still records the exact observed bbox
- descriptors are JSON audit artifacts; when `--crop-source-pdf` is supplied, they also bind rendered PNG crop filenames, PNG byte hashes, dimensions, and source-PDF fingerprint
- `--crop-dir` is native-Ethos-only in this alpha slice

Rendered crop production is optional and source-bound in this alpha slice. `--crop-source-pdf`
must match the native Ethos document's `source.fingerprint`; otherwise the command fails before
writing crop artifacts.

Same-host rendered crop repeatability is checked separately from `verify-alpha` because it
requires a configured PDFium runtime:

```bash
make verify-rendered-crops
```

That target parses `fixtures/synthetic/simple-text/document.pdf` twice, verifies the same
citation twice with `--crop-source-pdf`, then compares the parsed document JSON,
verification report JSON, crop descriptor JSON, and rendered PNG bytes across both runs. This
is not a cross-platform rendered-image determinism claim.

To classify two rendered-crop runs explicitly:

```bash
make compare-rendered-crops \
  COMPARE_RENDERED_CROPS_LEFT=target/verify-rendered-crops/run1 \
  COMPARE_RENDERED_CROPS_RIGHT=target/verify-rendered-crops/run2
```

The compare helper separates logical evidence identity from rendered artifact byte equality.
It is expected to pass both layers for same-host repeated runs with pinned PDFium. A
2026-06-14 macOS arm64 vs Linux x64 check on commit `64541dd` preserved document
fingerprint and `payload_sha256`, but rendered artifact byte equality failed because the
evidence bbox differed slightly across platforms. The full evidence record is
`docs/validation/rendered-crops-2026-06-14.md`. The honest claim is therefore:

```text
Ethos rendered crop artifacts are same-host repeatable with pinned PDFium.
Cross-platform rendered crop bit-identical output is not currently proven.
```

## Verification Contract

The demo is covered by `crates/ethos-cli/tests/verify.rs` and
`examples/verify/check_verify_alpha.py`. The tests run the public CLI for each command above,
compare the full JSON reports against checked-in goldens, and validate native crop
descriptor artifacts against `schemas/ethos-crop-descriptor.schema.json`.
Rendered PNG crop production is covered by the CLI test suite when PDFium is configured and
by `examples/verify/check_rendered_crops.py` for same-host repeated-run evidence.
