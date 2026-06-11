# ADR-0003: Deterministic Font Policy

- Status: Accepted (recorded from PRD v3.5 §6.1.1, §15)
- Date: 2026-06-11
- Governs: IMPLEMENTATION_PLAN §2 row 0.5; PRD §6.1.1; risk R1

## Context

System-font fallback is the classic determinism killer: the same PDF parses differently per host. G3 requires byte-identical canonical payloads across platforms, so font resolution must be fully specified by the deterministic profile.

## Decision

1. **Embedded PDF fonts are always preferred.**
2. Missing-font handling goes through a versioned **`font-substitution-table.json`** (shipped with the engine; its sha256 is part of the profile manifest).
3. The Release 1 fallback bundle is the **Liberation family (SIL OFL 1.1, ~4 MB)**, chosen for metric compatibility with the standard-14 PDF font territory. NOTICE carries the OFL attribution.
4. **PDFium's font mapper is overridden** to use the bundled deterministic profile; system-font fallback is disabled.
5. A glyph miss emits a deterministic **`.notdef`** rendering plus stable warning code (`unsupported_pdf_feature` at error level only when parse cannot proceed; otherwise warning).
6. **Non-embedded CJK fallback is out of Release 1**: it must warn clearly (`capability_limited`) instead of silently using system fonts.

## Consequences

- The font profile (bundle hash + substitution-table hash) is part of the parser profile manifest and Gate Zero determinism evidence.
- Acceptance test (WS-ENGINE week 2): the same missing-font fixture yields identical spans on all Gate Zero platforms; red by day 10 escalates to the decider (risk R1).
- Liberation adds ~4 MB against the 30 MB G2 budget; weekly footprint measurement watches this (risk R4).
