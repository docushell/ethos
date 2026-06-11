# WS-VERIFY-ALPHA Demo

This directory contains the first parser-agnostic verification demo.

Native Ethos document JSON:

```bash
ethos verify schemas/examples/document.example.json \
  --citations examples/verify/native_citations.json \
  --out verification_report.json
```

OpenDataLoader-style JSON through the grounding adapter:

```bash
ethos verify examples/verify/opendataloader.json \
  --grounding opendataloader-json \
  --citations examples/verify/answer_citations.json \
  --out verification_report.json
```

Each citations file contains one grounded quote and one fake quote that must fail with
`mismatch`. The ODL fixture is synthetic and limited to the adapter's documented alpha subset; it
is not a real pinned OpenDataLoader artifact.
