# ADR-0015: Opt-In Bundled PDFium Artifacts

- Status: Proposed
- Date: 2026-07-20
- Decider: Product / Gate Zero decider
- Governs: optional `ethos-full` macOS arm64 and Linux x64 archives; ADR-0002 and ADR-0013
  bundled-PDFium boundaries; `scripts/build-ethos-full-candidate.py`.

## Context

The base crates, wheel, npm package, and current CLI archives keep PDFium caller-provided under
ADR-0013. The pinned fetch command reduced setup friction, but a user must still install PDFium,
export its path, and retain the runtime beside Ethos. That remains an obstacle between a fresh
install and a first parse.

ADR-0013 also retains ADR-0002's Phase 2 project-maintained-build requirement as a hard blocker
for every bundled-PDFium artifact. No project-maintained Phase 2 build exists today. The only
available macOS arm64 and Linux x64 evidence covers the exact V8-disabled, XFA-disabled Phase 1
`bblanchon/pdfium-binaries` archives already bound into the deterministic profile.

The practical decision is therefore explicit: either keep every archive caller-provided until
Phase 2 exists, or permit a narrowly labeled, opt-in archive to redistribute the already-pinned
Phase 1 runtime with its complete license material. This proposal recommends the latter for the
standalone `ethos-full` class only. It does not make that recommendation active while this ADR is
Proposed.

## Proposed Decision

If accepted, this ADR amends ADR-0013 only as follows:

1. Add optional `ethos-full-<version>-macos-arm64.tar.gz` and
   `ethos-full-<version>-linux-x64.tar.gz` standalone archives. Base crates, wheels, npm packages,
   existing `ethos` archives, Windows artifacts, and hosted surfaces continue to bundle no
   PDFium.
2. Permit these two archives to carry the exact Phase 1 PDFium runtime pinned in
   `profiles/ethos-deterministic-v1.json`. Every archive must verify the runtime sha256 before
   assembly, keep V8 and XFA disabled, include the complete upstream package `LICENSE` and
   `licenses/` directory, and publish its own checksum and payload inventory.
3. Keep `ethos-full` opt-in and separately named. It never replaces the caller-provided
   archive or changes base-package dependencies. The archive launcher sets
   `ETHOS_PDFIUM_LIBRARY_PATH` to its relative bundled library; the Rust binary performs its
   existing runtime hash check before loading it.
4. Build archives deterministically: sorted entries, uid/gid zero, empty owner names, fixed
   modes, tar mtimes zero, and gzip mtime zero. Two builds from identical inputs must be
   byte-identical.
5. Require target-platform smoke before publication: `ethos --version`, `ethos doctor
   --require-pdfium`, and two byte-identical parses of the pinned license-clean fixture. A build
   on one platform is not evidence for the other.
6. Treat every candidate as non-publishable until this ADR is Accepted and the v0.4.0 release
   lane explicitly includes the artifact. Preparing candidates, checksums, and evidence does not
   authorize uploads, tags, release edits, or public wording.
7. Revisit Phase 2 independently. Acceptance of this narrow Phase 1 redistribution exception
   does not approve project-maintained builds, Windows-with-PDFium, or hosted execution.

## Artifact Contract

Each archive has one top-level directory and contains only:

- `ethos`: relative-path launcher;
- `bin/ethos`: target CLI binary;
- `lib/libpdfium.dylib` or `lib/libpdfium.so`;
- project `LICENSE` and `NOTICE`;
- `third-party/pdfium/LICENSE` and the complete `third-party/pdfium/licenses/` tree;
- `artifact-manifest.json` with target, input hashes, payload sizes, PDFium provenance, proposal
  status, and publication blocker.

The adjacent sha256 and inventory files are release-lane evidence, not archive payloads. The
candidate builder performs no downloads, accepts the original local PDFium archive, and verifies
its profile-pinned hash before reading any payload. Missing notices, enabled V8/XFA, an unexpected
runtime path, or an archive/runtime hash mismatch are fatal.

## Evidence and Size

Feasibility evidence is recorded in
`docs/validation/nip-5-2-ethos-full-build-evidence-2026-07-20.md`. Using the published `0.3.0`
CLI binaries as packaging fixtures and the pinned Phase 1 runtimes produced:

| Target | CLI bytes | PDFium bytes | Compressed candidate bytes |
| --- | ---: | ---: | ---: |
| macOS arm64 | 1,744,464 | 7,732,336 | 4,266,676 |
| Linux x64 | 2,249,504 | 7,645,184 | 4,510,646 |

These measurements are feasibility data, not a size promise for a future version. Both archive
and inventory outputs were byte-identical across two builds. The macOS launcher completed a real
double parse; Linux target execution remains a required later publication gate.

## Consequences

- If accepted, macOS and Linux evaluators gain a separately named archive that can parse after
  extraction without URL hunting or a global PDFium install.
- The convenience archive adds roughly 4.3–4.5 MB compressed in this feasibility build and
  redistributes third-party native code. Its checksum, provenance, license bundle, and opt-in
  naming make that tradeoff visible.
- The existing caller-provided path remains the default and the fallback. Rejecting this ADR
  requires no rollback because no release workflow or published surface is activated by the
  proposal evidence.
- The Phase 1 exception carries supply-chain reliance on `bblanchon/pdfium-binaries`; waiting for
  Phase 2 avoids that reliance but leaves the install cliff in place longer.
