# Milestone B Internal Exit Checklist

This checklist maps the current committed source tree to the Milestone B lanes in
`docs/IMPLEMENTATION_PLAN.md` and the PRD's Milestone B section.

Status: Internal Milestone B closeout validation is green for the current committed scope.
Milestone exit remains a decider call. This checklist does not approve public benchmark reports,
release artifacts, package publication, production positioning, or performance/quality/footprint
claims.

## Required Internal Validation

Run the aggregate closeout target from a clean tree:

```sh
make milestone-b-internal-checks PYTHON=<jsonschema-venv>/bin/python
```

The target includes fixture validation, font-policy validation, status/roadmap/closeout-record
guards, `make verify-alpha`, `make layout-evaluator-alpha`, `make python-surface-test`, claim
language guardrails, public-readiness guardrails, and `git diff --check`.

## Exit Evidence

| Lane | Internal B criterion | Current evidence | Closeout status | Still outside scope |
| --- | --- | --- | --- | --- |
| WS-VERIFY-ALPHA | Alpha verification over native Ethos JSON and OpenDataLoader-style grounding sources, with deterministic evidence matching and capability-aware reports | `make verify-alpha`; native, synthetic OpenDataLoader-style, and pinned real OpenDataLoader fixtures; split-quote, stale-fingerprint, non-v1, capability-limited, malformed-input, and summary diagnostics coverage | Present for current v1 alpha policy | Future claim-kind expansion, `verify_citations` v1 hardening, broader adapter shapes, semantic/arithmetic verification |
| WS-LAYOUT | Reading order, block grouping, heading/list alpha behavior, and Markdown/text export fixtures | `make layout-evaluator-alpha`; fixture metadata and committed extraction/layout/text/Markdown goldens | Present for current fixture-backed alpha scope | Broader table, nested-list, richer heading, OCR/image-only, and wider layout semantics |
| WS-SURFACES | Internal Python surface scaffold for local CLI-backed parsing calls | `make python-surface-test`; stdlib tests with a fake caller-provided `ethos` command | Present as internal scaffold | Native bindings, wheel publication, package setup, public API stability |
| WS-HARNESS | Internal validation path composes fixture, trust-loop, layout, surface, and policy guardrails | `make milestone-b-internal-checks`; `docs/validation/milestone-b-closeout-validation-2026-06-17.md` | Present for current source-tree validation | Public comparison report flow, claim-wording approval, release/package approval |
| DETERMINISM | PR and nightly workflow guardrails cover current deterministic contracts, with Windows x64 preflight for core contracts | CI workflow static guards; `test_determinism_workflow.py`; same-platform checks in current internal validation paths | Present for current configured contracts | Windows PDFium runtime provisioning and broader cross-platform corpus validation |

## Boundaries

- This checklist is internal closeout evidence only.
- Public benchmark reports remain blocked.
- Release artifacts and package publication remain blocked.
- Production positioning remains blocked.
- Performance/quality/footprint claims remain blocked.
- Table-quality and parser-quality claims remain blocked.
- No semantic/arithmetic verification expansion is claimed.
- No broader parser/table/OCR completion is claimed.

## Next Milestone Hand-off

Milestone C should start from the trust-loop and fixture/evaluator contracts already guarded here.
The first C slice should choose a single lane, add fixture-backed behavior first, and update this
checklist only if the Milestone B closeout contract itself changes.
