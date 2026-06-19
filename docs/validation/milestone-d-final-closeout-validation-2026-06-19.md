# Milestone D Final Closeout Validation - 2026-06-19

## Purpose

Record final internal Milestone D source-only closeout after the implementation lanes and scope
decision landed on `main`.

This record covers the source tree's internal pre-alpha validation boundary only. It does not
approve public benchmark reports, release artifacts, package publication, production positioning,
or performance, quality, footprint, table-quality, or parser-quality claims.

## Status

Status: **pass for internal Milestone D source-only closeout**.

Milestone D is internally complete for the current source-tree, source-only pre-alpha scope. Ethos
remains source-only pre-alpha.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `792190e`
- Prior contract closeout record:
  `docs/validation/milestone-d-contract-closeout-validation-2026-06-19.md`
- Scope: tracked source tree, Milestone D contract docs, contract inventories, schemas/examples,
  request envelopes, source-bound CLI/Python crop carrier, existing PDF worker-process contract,
  explicit blockers, focused validation commands, CI/static guard wiring, diagnostics, and
  fixture-backed validation
- Excluded: Node beta, MCP experimental work, hosted/sandbox-backed/foreign-adapter crop surfaces,
  cross-platform rendered-crop byte identity, public claim wording, and Milestone E scope

## Commands

```sh
git switch main
git pull --ff-only
make milestone-d-internal-contracts PYTHON=<jsonschema-venv>/bin/python
cargo test --locked -p ethos-cli
cargo clippy --locked -p ethos-core -p ethos-cli --all-targets -- -D warnings
cargo fmt --all --check
git diff --check
```

## Result

```text
Milestone D internal contract target green
ethos-cli test suite green
ethos-core and ethos-cli clippy green
cargo fmt --all --check green
git diff --check green
```

## Closed Internal D Scope

- `verify_citations` v1 is the citation-input to verification-report contract currently carried by
  `ethos verify`.
- `claim_kind_boundary` v1 is the supported claim-kind boundary for the current verification
  policy.
- `grounding_source` v1 is the parser-neutral evidence boundary carried by the current grounding
  trait and verification metadata.
- `opendataloader_adapter_shape` v1 is the OpenDataLoader-style input-shape to grounding-source
  contract.
- `capability_downgrade` v1 is the capability declaration to verification-report downgrade
  contract.
- `crop_element` v1 is the source-bound element-to-crop-descriptor contract carried by
  `ethos crop_element` and the existing `ethos verify --crop-dir` evidence artifacts.
- `crop_element_surface_shape` v1 is the callable source-bound CLI/Python surface shape over the
  current crop request and descriptor schemas.
- `sandbox_subprocess` v1 is the worker-boundary contract represented by the existing PDF worker
  process.
- Request-envelope identity is guarded for the current `crop_element` and `sandbox_subprocess`
  request schemas and examples.
- Explicit blockers remain mirrored between contract docs and inventories.
- CI and repository guards bind the focused validation commands to the current source-only
  contract registry.

## Remaining Boundaries

- Node, MCP, hosted, sandbox-backed, and foreign-adapter crop surfaces are post-D blockers and are
  not required for Milestone D closeout.
- Cross-platform rendered-crop byte identity is not required for Milestone D closeout.
- Sandbox hardening beyond the current worker-process contract remains future work.
- Public benchmark reports remain blocked.
- Release artifacts and package publication remain blocked.
- Production positioning remains blocked.
- Performance, quality, footprint, table-quality, and parser-quality claims remain blocked.

## Follow-up

Use `make milestone-d-internal-contracts` as the current Milestone D regression gate while Milestone
E prep begins. Future work should keep Milestone D closed unless a source-tree regression requires
a targeted corrective record.
