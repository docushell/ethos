# Milestone D Contract Closeout Prep - 2026-06-19

## Purpose

Prepare the internal Milestone D contract closeout boundary after the current source-only
contract registry, request-envelope, and fixture-backed validation guards were added.

This record covers the source tree's internal pre-alpha contract-validation path only. It does not
approve public benchmark reports, release artifacts, package publication, production positioning,
or performance, quality, footprint, table-quality, or parser-quality claims.

## Status

Status: **pass for current internal Milestone D source-only contract closeout prep, with final
D exit still pending review and a fresh validation run on `main`**.

## Subject

- Repository: `docushell/ethos`
- Prep branch starting HEAD before this record: `1070d8f`
- Scope: tracked source tree, Milestone D contract docs, contract inventories, schemas/examples,
  request envelopes, explicit blockers, focused validation commands, and Make/static guard wiring
- Excluded: sandbox hardening, Node beta, MCP experimental work, hosted/sandbox-backed/foreign
  adapter crop surfaces, cross-platform rendered-crop byte identity, public claim wording, and
  final Milestone D exit approval

## Commands

```sh
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
  source-bound `ethos crop_element` and the existing `ethos verify --crop-dir` evidence
  artifacts.
- `crop_element_surface_shape` v1 is the callable source-bound CLI/Python surface shape over the
  current crop request and descriptor schemas.
- `sandbox_subprocess` v1 is the future worker-boundary contract currently represented by the
  existing PDF worker process.
- Request-envelope identity is guarded for the current `crop_element` and `sandbox_subprocess`
  request schemas and examples.
- Explicit blockers remain mirrored between contract docs and inventories.

## Remaining Boundaries

- Final Milestone D exit still requires review, merge to `main`, and a fresh validation run from
  the merged source tree.
- Node, MCP, hosted, sandbox-backed, and foreign-adapter crop surfaces remain outside this prep
  record.
- Cross-platform rendered-crop byte identity remains outside this prep record.
- Sandbox hardening remains outside this prep record.
- Node beta and MCP experimental work remain outside this prep record unless separately staffed or
  accepted by a release-scope ADR.
- Public benchmark reports remain blocked.
- Release artifacts and package publication remain blocked.
- Production positioning remains blocked.
- Performance, quality, footprint, table-quality, and parser-quality claims remain blocked.

## Follow-up

Use `make milestone-d-internal-contracts` as the current internal Milestone D source-only contract
validation command until final D exit changes the validation contract. Contract changes should
update the Make target, its static guards, and any dated validation record that cites the target.
