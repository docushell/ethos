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

## Verification Contract

The demo is covered by `crates/ethos-cli/tests/verify.rs`. The test runs the public CLI for
each command above and compares the full JSON reports against the checked-in goldens.
