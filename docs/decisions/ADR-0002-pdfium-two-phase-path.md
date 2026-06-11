# ADR-0002: PDFium Two-Phase Distribution Path

- Status: Accepted (recorded from PRD v3.5 §6.1, §15)
- Date: 2026-06-11
- Governs: IMPLEMENTATION_PLAN §2 row 0.4, §6.1; PRD §6.1

## Context

PDFium is the Release 1 candidate backend, used only behind `EthosPdfBackend`. The archived `chromium/pdfium` GitHub repository is a mirror, not the source of truth; the canonical source is `pdfium.googlesource.com`. Gate Zero (week 4) cannot wait for project-maintained builds, but Public Beta cannot ship on third-party binaries.

## Decision

Two phases:

1. **Phase 1 — Milestone A / Gate Zero:** pinned `bblanchon/pdfium-binaries` artifacts, **V8 disabled, XFA disabled**, pinned by exact release/version and per-platform sha256. Pins land in `docs/pdfium-profile.md` and the deterministic profile manifest (WS-ENGINE week 1).
2. **Phase 2 — by Milestone E / Public Beta:** project-maintained builds from `pdfium.googlesource.com` with pinned source revision, recorded build flags, toolchain, patches, and per-platform hashes.

**Public Beta is blocked on Phase 2.** If project-maintained builds are not ready by Milestone E, Public Beta is blocked or re-scoped — never shipped on Phase 1 binaries.

Base build requirements (both phases): V8 off, XFA off, revision pinned, flags/toolchain/patches/distribution recorded, deterministic font profile recorded, geometry quantization recorded. V8/XFA-enabled builds fail security review and Gate Zero G2 automatically.

## Consequences

- `ethos-pdf` is the only crate that links PDFium; public schemas/APIs never expose PDFium types (invariant 3).
- Backend identity (version + hashes + flags) enters the profile manifest and therefore the document fingerprint.
- Sandbox/subprocess mode (PRD §6.3) is a backend implementation concern; feasibility spike in A, build-out in D.
