# Ethos v0.2.0 Release Preparation

Status: source-preparation record. This document does not approve `cargo publish`, PyPI upload,
GitHub Release creation, package tags, or public `0.2.0` installability wording.

Canonical preparation sentence:

> v0.2.0 is being prepared to publish registry install surfaces for JSON verification and evidence
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

## Publication Governance

Before any `0.2.0` publication action:

- obtain explicit `0.2.0` publication approval;
- confirm crates.io ownership for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`;
- confirm ADR-0006 package-identifier governance;
- confirm publication metadata for intended crates;
- confirm how `reserved_crates_io_version` remains historical reservation metadata;
- confirm whether the Python wrapper is in the public promise;
- confirm the operator and closeout evidence owner.

If approval or registry publication is deferred, public wording must stay in preparation language
and must not claim `0.2.0` registry installation.

## Publish Order

The intended Rust order is:

1. Run local tests and gates.
2. Dry-run only `ethos-doc-core` before any `0.2.0` crate is live.
3. Publish `ethos-doc-core`.
4. Wait for crates.io index availability and smoke a clean temp project.
5. Dry-run and publish `ethos-verify`.
6. Run a real API smoke with the bring-your-own-parser example.
7. Dry-run and publish `ethos-pdf` as a continuity crate.

`ethos-verify` and `ethos-pdf` registry-resolution dry-runs belong after
`ethos-doc-core 0.2.0` is live in the crates.io index.

## Required Gates

Source-prep gates:

```bash
make v0-2-release-prep PYTHON=python3
```

The target expands to the workspace Rust test suite, Python surface tests, schema example
validation, public claims gates, and whitespace diff checks.

Post-publication wording flip gates:

```bash
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
```

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
