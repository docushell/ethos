# Verify Alpha Demo

## Product Proof

Ethos verifies whether AI citations are grounded in document evidence.

This is a citation grounding check, not a truth checker: Ethos does not claim semantic
entailment, factual truth, arithmetic correctness, or answer quality. The alpha proof is the
repeatable `make verify-alpha` path:

- native Ethos JSON citation checks can pass against checked-in document evidence
- OpenDataLoader-style JSON can enter the same verification loop through a grounding adapter
- real pinned OpenDataLoader 2.4.7 output has both grounded and ungrounded citation cases
- `--fail-on-ungrounded` turns the report into a CI/agent gate with exit code `1` when evidence is not fully grounded
- native Ethos verification can emit deterministic crop descriptor artifacts with `--crop-dir`
- every demo report is compared against a golden and regenerated twice to prove byte-identical output
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
- descriptors are JSON audit artifacts; when `--crop-source-pdf` is supplied, they also bind rendered PNG crop filenames, PNG byte hashes, dimensions, and source-PDF fingerprint
- `--crop-dir` is native-Ethos-only in this alpha slice

Rendered crop production is optional and source-bound in this alpha slice. `--crop-source-pdf`
must match the native Ethos document's `source.fingerprint`; otherwise the command fails before
writing crop artifacts.

## Verification Contract

The demo is covered by `crates/ethos-cli/tests/verify.rs` and
`examples/verify/check_verify_alpha.py`. The tests run the public CLI for each command above,
compare the full JSON reports against checked-in goldens, and validate native crop
descriptor artifacts against `schemas/ethos-crop-descriptor.schema.json`.
Rendered PNG crop production is covered by the CLI test suite when PDFium is configured.
