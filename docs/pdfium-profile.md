# PDFium Profile

Status: **pending WS-ENGINE implementation — Phase 1 pins are a Gate Zero blocker**
(plan §6.1; ADR-0002; current PM status in `docs/execution-status.md`). The profile artifact (`profiles/ethos-deterministic-v1.json`) carries
the same identity as machine-readable fields; this document is the human-readable record.

## Distribution path (ADR-0002)

- **Phase 1 (Gate Zero):** pinned `bblanchon/pdfium-binaries`, V8/XFA disabled.
- **Phase 2 (blocks Public Beta):** project-maintained builds from `pdfium.googlesource.com`
  (pinned revision, flags, toolchain, patches, hashes). The archived `chromium/pdfium` GitHub
  mirror is NOT the source of truth.

## Phase 1 pins (to be filled by WS-ENGINE — Gate Zero blocker)

| Field | Value |
| --- | --- |
| Release/version | _TBD_ |
| V8 | disabled (required) |
| XFA | disabled (required) |
| macOS arm64 artifact sha256 | _TBD_ |
| Linux x64 artifact sha256 | _TBD_ |
| Windows x64 artifact sha256 | _TBD (nightly determinism by Milestone B exit)_ |
| Distribution method | _TBD (vendored vs fetched-and-verified at build)_ |

When filled, mirror into `profiles/ethos-deterministic-v1.json` → `backend` (phase, version,
platform_hashes) — that is what binds the backend identity into every document fingerprint.

## Phase 1 acceptance checklist

- [ ] Pin exact `bblanchon/pdfium-binaries` release/version.
- [ ] Record macOS arm64 and Linux x64 artifact sha256 values before Gate Zero.
- [ ] Record Windows x64 artifact sha256 before Windows joins nightly determinism.
- [ ] Prove selected artifacts have V8 disabled and XFA disabled.
- [ ] Decide vendored vs fetched-and-verified distribution path.
- [ ] Add build/runtime loader checks that reject missing or mismatched artifacts with stable errors.
- [ ] Mirror backend identity into `profiles/ethos-deterministic-v1.json`.

## Font profile (ADR-0003)

- Embedded fonts first; missing fonts → versioned `font-substitution-table.json`; fallback →
  bundled Liberation (OFL-1.1); system-font fallback disabled (PDFium font mapper overridden);
  glyph miss → deterministic `.notdef` + stable warning; non-embedded CJK warns, out of R1.
- Table + bundle sha256 land in the profile artifact when WS-ENGINE ships them.

## Quirk validation log

Ligatures, hyphenation, CID fonts, rotation — run on the Gate Zero manifest subset; blocking
quirks escalate to the decider at the WS-ENGINE check-in (risk R1). Record findings here.

## Phase 2 build record (Milestone E)

Source revision, build flags, toolchain, patches, per-platform hashes — to be recorded when
project-maintained builds land. Public Beta does not ship on Phase 1 binaries.
