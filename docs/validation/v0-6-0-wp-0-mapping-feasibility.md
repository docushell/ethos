# v0.6.0 WP-0 Mapping Feasibility

Status: **positive mapping proof passed; manual WP-0 acceptance remains** (2026-07-30).

## Candidate and provenance

The candidate is the pinned DocuShell-vendored `opendataloader-pdf` 2.5.0 output in
[`fixtures/foreign/opendataloader/real`](../../fixtures/foreign/opendataloader/real). Its source
PDF hash is recorded in the fixture manifest. The vendor JAR SHA-256 is
`516ce47832a6726e87cb17db77c20174ca8cabbe9a6b56db1418babc7c9ddcba`; the vendor README records
Apache-2.0 licensing and the complete third-party notice set.

OpenDataLoader documents its bounding boxes as `[left,bottom,right,top]` in PDF points. The
source-bound page sidecar records the PDF's `595 × 841` point page geometry and rotation `0`.
The mapper converts that bottom-left geometry to Ethos's top-left origin and quantizes points to
centipoints using half-away-from-zero rounding.

## Executable result

Run twice from the repository root:

```text
python3 scripts/validate-v0-6-wp-0.py \
  --vendor-jar ../docushell/vendor/opendataloader/opendataloader-pdf-cli.jar \
  --vendor-version-file ../docushell/vendor/opendataloader/VERSION \
  --output target/wp-0/run-1.json
python3 scripts/validate-v0-6-wp-0.py \
  --vendor-jar ../docushell/vendor/opendataloader/opendataloader-pdf-cli.jar \
  --vendor-version-file ../docushell/vendor/opendataloader/VERSION \
  --output target/wp-0/run-2.json
cmp target/wp-0/run-1.json target/wp-0/run-2.json
```

The two output files and their mapped artifacts are byte-identical. The mapped artifact hash is
`sha256:7bc28b1aa2acd36206c5e5165d7d6513714c689583363f4c49ee2d4308093c82`. The mapper declares
`spans=false`, `char_offsets=false`, and `tables=false`; it does not infer unsupported data.

This is a positive feasibility result, not yet a schema decision. WP-1 can start after manual
review accepts the coordinate conversion, source-page sidecar, stable ID/order projection, and
capability gaps, followed by review and acceptance of the Grounding JSON ADR and the coordinated
public-posture request. No parser dependency or production adapter is added by this record.
