# Ethos v0.2.0 Release Preparation

Status: release-candidate activation record. This document does not approve `cargo publish`, PyPI
upload, GitHub Release creation, package tags, or public `0.2.0` installability wording.

Canonical preparation sentence:

> v0.2.0 release-candidate source versions are activated for JSON verification and evidence
> anchoring.

The release promise being prepared is narrow:

> Ethos v0.2.0 verifies grounded citations and evidence anchors over caller-provided JSON sources.
> The verify and evidence-anchor paths do not require PDFium; parser, crop, and render paths may
> still require PDFium.

## Included Preparation Scope

- `ethos-doc-core` as the Rust package for `GroundingSource` implementers.
- `ethos-verify` as the Rust package for verification consumers.
- `ethos-pdf` as a continuity crate if the lockstep Rust workspace is published at `0.2.0`.
- Python `ethos-pdf` CLI-wrapper calls for JSON `verify(...)` and `anchor(...)`, if the Python
  package remains in the public promise.
- JSON verify quickstart with no PDFium requirement.
- JSON evidence-anchor quickstart with no PDFium requirement.
- Bring-your-own-parser tutorial.
- `0.2.x` compatibility policy.
- Security and RAG hardening notes aligned with current implementation.

## Explicit Non-Scope

- broad parser GA;
- pure-Python implementation;
- PyO3/native Python bindings;
- Node-NAPI or WASM bindings;
- hosted service;
- production/SaaS claims;
- public benchmark or performance claims;
- project-managed bundled PDFium;
- Windows packaged binaries;
- public GA for `ethos-doc` or `ethos-rag`;
- hidden/off-page/low-contrast text detection;
- annotation, link, embedded-file, or JavaScript inventories unless implemented.

## Release Sequence

### 1. Decide Python Scope

Before approval, decide whether Python is public in `v0.2.0`.

If Python is public in `v0.2.0`, commit to all of these surfaces together:

- PyPI wheel;
- `v0.2.0` CLI artifacts usable by the wrapper;
- docs explaining that `ethos-pdf` is historical package naming and that JSON verify/anchor calls
  use a caller-provided CLI binary.

If Python is not public in `v0.2.0`, remove Python from the public promise before approval.

### 2. Prepare Approval Packet

The approval packet must bind:

- exact source commit;
- version-bump plan;
- crates: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`;
- explicit `ethos-pdf` continuity decision;
- Python decision;
- npm `@docushell/ethos-pdf` fate;
- CLI artifact decision;
- tag and package-tag approval;
- ADR-0006/name ownership confirmation;
- `reserved_crates_io_version` handling;
- append-only crates.io risk;
- operator and closeout owner;
- retained blockers.

If approval or registry publication is deferred, public wording must stay in preparation language
and must not claim `0.2.0` registry installation.

### 3. Create Release-Candidate Branch

After approval, create a release-candidate branch and make the versioned release-candidate changes:

- bump Rust workspace/package dependency versions to `0.2.0`;
- bump Python metadata and `__version__` if Python is included;
- bump npm if npm is included;
- finalize `CHANGELOG.md`;
- update version-pinned docs to release-candidate wording, not installable wording yet.

### 4. Run Full Gates On The Bumped Tree

Run:

```bash
make v0-2-release-prep PYTHON=python3
cargo publish --dry-run -p ethos-doc-core
```

Also run package/build checks for Python, npm, and CLI artifacts if those surfaces are included.

### 5. Publish In Dependency Order

Rust publication order:

1. Publish `ethos-doc-core`.
2. Wait for crates.io index availability.
3. Dry-run and publish `ethos-verify`.
4. Dry-run and publish `ethos-pdf`.

`ethos-verify` and `ethos-pdf` registry-resolution dry-runs belong after
`ethos-doc-core 0.2.0` is live in the crates.io index.

Publish Python, npm, and CLI artifacts only if they are in scope.

### 6. Smoke Real Usage

Smoke:

- Rust bring-your-own-parser API;
- CLI JSON verify;
- CLI evidence anchor;
- Python wrapper against the published CLI artifact if Python is in scope.

### 7. Flip Docs Only After Smoke

Only after registry/artifact availability and smoke evidence, flip docs to installable `0.2.0`
wording and rerun:

```bash
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
```

## Source-Prep Gate

Current source-prep gate before a release-candidate branch:

```bash
make v0-2-release-prep PYTHON=python3
```

The target expands to the workspace Rust test suite, Python surface tests, schema example
validation, public claims gates, and whitespace diff checks.

## Python Wrapper Contract

If Python remains included, the `ethos-pdf` package name is historical continuity naming. The
`verify(...)` and `anchor(...)` methods shell out to a caller-provided local `ethos` binary. The
wrapper is not pure Python, does not bundle the CLI, and does not bundle PDFium.

`verify(...)` maps to:

```bash
ethos verify <source> \
  --citations <citations> \
  [--grounding <adapter-id>] \
  [--config <path>] \
  [--fail-on-ungrounded] \
  --format json
```

`anchor(...)` maps to:

```bash
ethos evidence anchor <source> \
  --evidence-refs <evidence_refs> \
  [--grounding <adapter-id>]
```

Evidence anchor has no v0.2 fail flag. Non-bound anchor outcomes remain exit-0 structured reports.

## DocuShell Design-Partner Pilot

The DocuShell wedge should stay internal/design-partner scoped as "Evidence-Checked Answers", not a
public launch.

The two learning goals are:

- claim extraction quality;
- non-PDF ingestion.

Those decide whether the deterministic trust layer is easy to apply outside Ethos' own parser path.
