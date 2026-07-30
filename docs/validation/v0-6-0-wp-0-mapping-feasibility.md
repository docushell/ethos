# v0.6.0 WP-0 Mapping Feasibility

Status: **blocked; positive schema-freeze proof not passed** (2026-07-30).

## Candidate and provenance

The candidate is the pinned `opendataloader-pdf` 2.4.7 output in
[`fixtures/foreign/opendataloader/real`](../../fixtures/foreign/opendataloader/real). Its source
PDF and output hashes, parser package provenance, and Apache-2.0 fixture license are recorded in
the fixture manifest.

## Executable result

Run twice from the repository root:

```text
python3 scripts/validate-v0-6-wp-0.py --output target/wp-0/run-1.json
python3 scripts/validate-v0-6-wp-0.py --output target/wp-0/run-2.json
cmp target/wp-0/run-1.json target/wp-0/run-2.json
```

The two output files are byte-identical. The result is `blocked` because the parser output does
not provide page dimensions or coordinate origin. Table capability can be declared honestly as
`false`, but the existing adapter's observed-bounding-box extent and `unknown` origin are not
acceptable Grounding JSON v1 mappings. Ethos therefore must not guess or repair those fields.

This is an explicit stop, not a schema decision. WP-1 remains unauthorized until a license-clean
real-parser output supplies honest page geometry, deterministic identity/order, and capability
declarations. No ADR, schema, runtime adapter, or parser dependency is added by this record.
