# Milestone D Contract Closeout Validation - 2026-06-19

## Purpose

Record the current internal Milestone D source-only contract-validation run after the contract
closeout prep branch landed on `main`.

This record covers the source tree's internal pre-alpha contract boundary only. It does not
approve public benchmark reports, release artifacts, package publication, production positioning,
or performance, quality, footprint, table-quality, or parser-quality claims.

## Status

Status: **pass for current internal Milestone D source-only contract closeout, with implementation
lanes and public blockers unchanged**.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `2514400`
- Prior closeout prep record: `docs/validation/milestone-d-contract-closeout-prep-2026-06-19.md`
- Scope: tracked source tree, Milestone D contract docs, contract inventories, schemas/examples,
  request envelopes, explicit blockers, focused validation commands, CI/static guard wiring,
  diagnostics, and fixture-backed validation
- Excluded: first-class crop API implementation, sandbox hardening, Node beta, MCP experimental
  work, public claim wording, and full 13-D exit approval

## Commands

```sh
git switch main
git pull --ff-only
make milestone-d-internal-contracts PYTHON=<jsonschema-venv>/bin/python
cargo fmt --all --check
git diff --check
```

The aggregate target currently composes:

- `make milestone-d-verify-citations-contract`
- `make milestone-d-claim-kind-boundary-contract`
- `make milestone-d-grounding-source-contract`
- `make milestone-d-opendataloader-adapter-shape-contract`
- `make milestone-d-capability-downgrade-contract`
- `make milestone-d-crop-element-contract`
- `make milestone-d-crop-element-surface-shape-contract`
- `make milestone-d-sandbox-subprocess-contract`
- `.github/scripts/test_milestone_d_closeout_prep_record.py`
- `.github/scripts/test_milestone_d_closeout_record.py`
- `.github/scripts/test_milestone_d_internal_contracts.py`
- `git diff --check`

## Result

```text
verify_citations contract target green
claim_kind_boundary contract target green
grounding_source contract target green
opendataloader_adapter_shape contract target green
capability_downgrade contract target green
crop_element contract target green
crop_element_surface_shape contract target green
sandbox_subprocess contract target green
Milestone D closeout prep record guard green
Milestone D closeout validation record guard green
Milestone D internal contract registry guard green
cargo fmt --all --check green
git diff --check green
```

## Current Internal Contract Scope

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
- `crop_element` v1 is the element-to-crop-descriptor contract currently represented by
  descriptor-only `ethos crop_element` and the existing `ethos verify --crop-dir` evidence
  artifacts.
- `crop_element_surface_shape` v1 is the callable descriptor-only CLI surface shape over the
  current crop request and descriptor schemas.
- `sandbox_subprocess` v1 is the future worker-boundary contract currently represented by the
  existing PDF worker process.
- Request-envelope identity is guarded for the current `crop_element` and `sandbox_subprocess`
  request schemas and examples.
- Explicit blockers remain mirrored between contract docs and inventories.
- CI and repository guards bind the focused validation commands to the current source-only
  contract registry.

## Remaining Boundaries

- Full 13-D exit still requires review of implementation lanes beyond the contract boundary.
- First-class crop API implementation remains future work outside this closeout record.
- Sandbox hardening remains future work outside this closeout record.
- Node beta and MCP experimental work remain outside this closeout record unless separately
  staffed or accepted by a scoped ADR.
- Public benchmark reports remain blocked.
- Release artifacts and package publication remain blocked.
- Production positioning remains blocked.
- Performance, quality, footprint, table-quality, and parser-quality claims remain blocked.

## Follow-up

Use `make milestone-d-internal-contracts` as the current internal Milestone D source-only contract
validation command until implementation-lane work changes the validation contract. Future changes
should update the Make target, its static guards, and any dated validation record that cites the
target.
