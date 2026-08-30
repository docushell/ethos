# ADR-0013: Caller-Provided PDFium Beta Posture

- Status: Proposed
- Date: 2026-07-10
- Decider: Gate Zero decider
- Governs: PDFium distribution posture for public surfaces; amends ADR-0002's phase model;
  `ETHOS_PDFIUM_LIBRARY_PATH`; `scripts/fetch-pdfium.sh`.

## Context

ADR-0002 defined two distribution phases: Phase 1 pinned `bblanchon/pdfium-binaries` artifacts for
Gate Zero, and Phase 2 project-maintained builds from `pdfium.googlesource.com`, with "Public Beta
is blocked on Phase 2."

What v0.3.0 actually shipped is a third path not in ADR-0002's decision space: **caller-provided
PDFium** through `ETHOS_PDFIUM_LIBRARY_PATH`. Ethos distributes no PDFium binaries at all — not
Phase 1 third-party artifacts, not Phase 2 project builds. The released crates, wheel, npm
package, and CLI archives load an operator-supplied library by exact path and verify the recorded
runtime hash before `dlopen`/`LoadLibraryW` (docs/pdfium-profile.md, "Distribution method").

This posture is recorded across release-prep and closeout documents
(`docs/v0-3-0-release-prep.md`, `docs/execution-status.md`, the v0.3.0 validation records) and in
public wording (`docs/public-boundary-claims.json`), but no ADR records the decision itself. The
project's most consequential distribution decision since ADR-0002 currently exists only as
scattered validation prose.

## Decision

1. **Caller-provided PDFium is the accepted distribution posture for public
   surfaces.** Ethos ships no PDFium binaries in any published artifact. PDFium-backed commands
   require `ETHOS_PDFIUM_LIBRARY_PATH`; JSON verification and evidence-anchor paths require no
   PDFium at all.

2. **ADR-0002's Phase 2 gate is re-scoped, not removed.** "Public Beta is blocked on Phase 2"
   applied to beta surfaces that *distribute* PDFium. Because the shipped beta distributes none,
   the current distribution status does not violate ADR-0002. Phase 2 project-maintained builds
   remain a hard blocker for: bundled-PDFium artifacts of any kind, Windows packaged artifacts
   that include PDFium, and hosted surfaces. Those surfaces stay blocked in
   `docs/execution-status.md` until Phase 2 lands.

3. **Phase 1 pins remain the verification reference.** The exact `bblanchon` release, archive
   sha256, and runtime library sha256 values in `docs/pdfium-profile.md` and
   `profiles/ethos-deterministic-v1.json` define which caller-provided library the deterministic
   profile and Gate Zero evidence are bound to. Runtime hash verification against those pins is
   unchanged.

4. **`scripts/fetch-pdfium.sh` is operator tooling, not distribution.** The helper downloads only
   the exact pinned Phase 1 archive, verifies the recorded archive sha256 before extraction and
   the recorded runtime library sha256 after, and fails closed on any mismatch. The `ethos`
   binary itself still never downloads, installs, repairs, or vets dynamic libraries. Shipping
   the script does not constitute bundling or redistributing PDFium.

## Consequences

- The README status badge, ADR-0002, and shipped reality are reconciled in one record;
  future "why is beta live if Phase 2 isn't done" questions resolve here.
- First-run setup cost drops for evaluators (one script instead of a manual pinned download),
  without changing the trust boundary: hashes verified are the same hashes already recorded.
- Phase 2 remains on the roadmap with a sharper purpose: it gates *bundling*, Windows packaged
  artifacts with PDFium, and hosted surfaces.
- Pin updates now touch three places in the same PR: `docs/pdfium-profile.md`,
  `profiles/ethos-deterministic-v1.json`, and `scripts/fetch-pdfium.sh`. A drift check between
  them is cheap CI follow-up work.
- If a future release *does* bundle PDFium, that release re-enters ADR-0002 Phase 2 obligations
  in full and requires its own approval record.
