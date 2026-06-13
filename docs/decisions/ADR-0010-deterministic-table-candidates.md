# ADR-0010: Deterministic Table Candidates

- Status: **Accepted**
- Date: 2026-06-13
- Decider: Gate Zero decider
- Governs: table candidate extraction, table-cell provenance, and ODL-bench table work.

## Context

The OpenDataLoader extraction benchmark baseline showed Ethos has strong deterministic text
coverage, but records zero table and heading structure because the current parser emits paragraph
blocks only. A focused external prototype over two text-layer ODL-bench tables showed that existing
Ethos spans are enough to recover high table scores when the document exposes a regular text grid:

- `01030000000047`: TEDS `0.0000` -> `0.8575`
- `01030000000128`: TEDS `0.0000` -> `0.9292`

The same inspection also showed a separate class of failure (`01030000000110`) where the benchmark
ground truth contains table content that Ethos spans do not expose. That is an extraction coverage
problem, not a table-structure problem.

## Decision

Start table work with deterministic table candidates over already-extracted, quantized spans. The
first implementation lane is intentionally narrow:

- no OCR/image-only table recovery,
- no semantic table interpretation,
- no arithmetic or data-type inference,
- no default parser-output changes until the candidate contract is proven by tests and fixtures.

A table candidate may be emitted only when spans form a regular row/column grid under deterministic
thresholds. Cell text, row/column order, and candidate omission must be deterministic functions of
span ids, quantized geometry, and extracted text.

Table cells now allow optional `span_refs` in addition to `element_refs`. This lets table candidates
retain cell-level provenance before layout has created table anchor elements or per-cell elements.

## Consequences

- `ethos-tables` can develop and test candidate logic without changing Gate Zero G1/G3 parser
  outputs.
- Public claims must distinguish text-layer table candidates from OCR/image-table recovery.
- ODL-bench can be used as an external quality suite, but it must remain separate from Gate Zero.
- The next parser-output change should wire candidates only after small fixture coverage proves
  stable row/column behavior and the resulting G1/G3 churn is intentional.
