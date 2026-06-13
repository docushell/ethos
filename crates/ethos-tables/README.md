# ethos-tables

Deterministic table-candidate extraction for already-quantized Ethos spans.

Current scope is intentionally narrow:

- regular text-grid candidates only,
- no OCR or image-table recovery,
- no semantic/header inference beyond configured leading header rows,
- no default parser-output wiring yet.

See `docs/decisions/ADR-0010-deterministic-table-candidates.md`.
