# Verify Alpha Demo

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

## Verification Contract

The demo is covered by `crates/ethos-cli/tests/verify.rs`. The test runs the public CLI for
each command above and compares the full JSON reports against the checked-in goldens.
