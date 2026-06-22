# Release Artifact Notices

Ethos is source-only pre-alpha. This document defines the license and NOTICE bundle contract for
future release artifacts; it does not authorize releases, package publication, binaries, wheels,
npm updates, or public benchmark reports.

## Artifact Classes

Release candidates must declare one artifact class before packaging:

- `source-snapshot`: GitHub source archive only.
- `github-release-binary`: compiled CLI plus any bundled native libraries, schemas, profiles,
  and font assets.
- `wheel`: Python package contents plus native payloads, if any.
- `npm-package`: Node package contents plus native or WASM payloads, if any.
- `crate-publication`: Rust package contents published to crates.io.
- `benchmark-report`: public benchmark evidence and report assets.

## Required Bundle Contents

Every artifact class needs a reviewed license/NOTICE bundle containing:

- project `LICENSE`;
- project `NOTICE`;
- generated Cargo third-party dependency manifest or a reviewed derivative;
- artifact payload inventory with checksums;
- upstream license and notice material for every bundled non-Cargo asset;
- a statement of excluded optional or benchmark-only dependencies.

## Conditional External Notices

PDFium is not vendored in the source tree. If any future artifact bundles PDFium, that artifact
must include upstream PDFium BSD-3-Clause license and notice material, plus the PDFium version,
source/provenance, build flags, and hashes.

Liberation fonts are policy-selected but not vendored in the source tree. If any future artifact
bundles Liberation font files, that artifact must include SIL Open Font License 1.1 material and
the exact font payload inventory.

## Draft Generation

The current draft target is:

```sh
make release-notice-draft
```

It writes a planning bundle under `target/release-notice-draft/`:

- `NOTICE.release.md`
- `THIRD-PARTY-CARGO-LICENSES.json`
- `release-notice-manifest.json`

The draft bundle is intentionally marked `draft_not_release_ready`.

The first public release-prep workflow may also create CI-only draft CLI artifact archives for
macOS arm64 and Linux x64. Those archives must include SHA256 checksums and an
`ethos.release_artifact_inventory.v1` inventory marked `draft_not_release_ready` and
`publication: blocked`.

## Release Gate

Approved H2 artifact scope as of 2026-06-20 is `source-snapshot` only. This scope does not approve
GitHub release binaries, wheels, npm packages, crate publication, hosted surfaces, public benchmark
reports, or wording beyond the exact approved pre-alpha sentence. The approval record is
`docs/validation/h2-source-snapshot-scope-approval-2026-06-20.md`.

Before any public release artifact:

- replace the draft artifact identifier with the concrete artifact name and platform;
- review the artifact payload inventory and checksums;
- include PDFium/font notices when those assets are bundled;
- rerun `make release-advisory`;
- rerun `make third-party-license-manifest`;
- rerun claim-language and public readiness gates;
- keep public benchmark reports blocked until `ethos-bench` owns signed or otherwise
  integrity-bound public-safe G1/G2/G3 evidence.
