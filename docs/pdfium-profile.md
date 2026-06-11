# PDFium Profile

Status: **Phase 1 profile pinned for WS-ENGINE / Gate Zero**
(plan §6.1; ADR-0002; current PM status in `docs/execution-status.md`). The profile artifact
(`profiles/ethos-deterministic-v1.json`) carries the same identity as machine-readable fields;
this document is the human-readable record.

## Distribution path (ADR-0002)

- **Phase 1 (Gate Zero):** pinned `bblanchon/pdfium-binaries`, V8/XFA disabled.
- **Phase 2 (blocks Public Beta):** project-maintained builds from `pdfium.googlesource.com`
  (pinned revision, flags, toolchain, patches, hashes). The archived `chromium/pdfium` GitHub
  mirror is NOT the source of truth.

## Phase 1 pins

| Field | Value |
| --- | --- |
| Distribution source | `bblanchon/pdfium-binaries` |
| Release tag | `chromium/7881` |
| Release name | `PDFium 151.0.7881.0` |
| Release URL | <https://github.com/bblanchon/pdfium-binaries/releases/tag/chromium/7881> |
| Published at | `2026-06-08T17:07:25Z` |
| V8 | disabled (required; `pdf_enable_v8=false` in `args.gn`) |
| XFA | disabled (required; `pdf_enable_xfa=false` in `args.gn`) |
| Attestation artifact sha256 | `24dec7cd76acb81106a0c29b908cceceef8215b050f6ff6ffbf875465811ef60` |
| Distribution method | Phase 1 loads an operator-supplied extracted library by exact path. Build/fetch lanes verify the release archive hash; runtime verifies the extracted library hash before `dlopen`/`LoadLibraryW`. |

The same backend identity is mirrored into `profiles/ethos-deterministic-v1.json` → `backend`
(phase, version, flags, artifact hashes, runtime library hashes) — that is what binds the backend
identity into every document fingerprint.

### Phase 1 artifacts

| Platform | Release artifact | Artifact sha256 | Runtime library path | Runtime library sha256 |
| --- | --- | --- | --- | --- |
| macOS arm64 | `pdfium-mac-arm64.tgz` | `52e94ca5aa8847934330daf3f8150c190682c5ca93831468794f8b90d4392e40` | `lib/libpdfium.dylib` | `1bc45b15466b34cef96641ce25c77a876e70010c6b114f909dda2f5325fc5bd7` |
| Linux x64 | `pdfium-linux-x64.tgz` | `1470e21b8b4a3b4ad7f85684e2da11d94f3b69a86d81dee11b9b6709d927ac1d` | `lib/libpdfium.so` | `f728930966f503652b92acc89b9374a2eeca00ce42e26dccd3e4b5c5161b2d64` |
| Windows x64 | `pdfium-win-x64.tgz` | `73cc0de638ac2095e7445bf56a38200a5b7c7ca0e9f4ba144598f2457377ac08` | `bin/pdfium.dll` | `79d4676b656cfb1abcea88f9ade3b4b0826c5200382db5f4ec72a636c598c118` |

## Phase 1 acceptance checklist

- [x] Pin exact `bblanchon/pdfium-binaries` release/version.
- [x] Record macOS arm64 and Linux x64 artifact sha256 values before Gate Zero.
- [x] Record Windows x64 artifact sha256 before Windows joins nightly determinism.
- [x] Prove selected artifacts have V8 disabled and XFA disabled.
- [x] Decide Phase 1 runtime path: exact extracted library path plus deterministic hash check.
- [x] Add loader checks that reject missing or mismatched artifacts/libraries with stable errors.
- [x] Mirror backend identity into `profiles/ethos-deterministic-v1.json`.

Follow-up before Public Beta: replace these Phase 1 third-party artifacts with Phase 2
project-maintained builds from `pdfium.googlesource.com`, including pinned source revision,
toolchain, patches, flags, and hashes.

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
