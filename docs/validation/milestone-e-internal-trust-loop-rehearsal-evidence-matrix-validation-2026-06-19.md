# Milestone E Internal Trust-Loop Rehearsal Evidence Matrix Validation - 2026-06-19

## Purpose

Record internal validation for the source-only internal trust-loop rehearsal/evidence matrix added
during Milestone E prep.

This record covers matrix guard wiring only. It does not promote any fixture, approve public
reports, approve release artifacts, approve package publication, approve production positioning,
approve hosted surfaces, or approve public result wording. It also does not make performance,
quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an internal
continuation decision only.

## Status

Status: **pass for internal Milestone E trust-loop rehearsal/evidence matrix validation**.

Ethos remains source-only pre-alpha. The matrix defines internal evidence lanes for rehearsal
planning over the current use protocol; it does not move any fixture beyond internal planning. The
record is limited to evidence grounding, diagnostics, fixture/evaluator validation, and explicit
blockers.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `8f0206d`
- Fixture-candidate inventory: `docs/milestone-e-fixture-candidates.json`
- Fixture-promotion criteria: `docs/milestone-e-fixture-promotion-criteria.json`
- Internal trust-loop walkthrough plan: `docs/milestone-e-internal-trust-loop-walkthrough.json`
- Internal trust-loop use protocol: `docs/milestone-e-internal-trust-loop-use-protocol.json`
- Internal trust-loop rehearsal/evidence matrix:
  `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`
- Rehearsal/evidence matrix schema:
  `schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json`
- Guard: `.github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py`
- Status: `source-only-pre-alpha-internal-milestone-e-prep`
- Scope: tracked source tree, matrix-to-protocol consistency, protocol-to-walkthrough consistency,
  protocol-to-criteria consistency, path-backed fixtures, allowlisted validation commands,
  explicit diagnostic boundaries, explicit blockers, evidence-lane coverage, schema validation,
  public posture exclusions, CI/static guard wiring, and diff hygiene
- Excluded: public reports, public result wording, hosted surfaces, release artifacts, package
  publication, production positioning, broad demo-generation workflows, benchmark publication, and
  any performance, quality, footprint, table-quality, or parser-quality claims

## Commands

```sh
python3 -m json.tool docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json
python3 -m json.tool schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json
<jsonschema-venv>/bin/python schemas/validate_examples.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py
python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol_validation_record.py
python3 .github/scripts/test_milestone_e_prep_scope.py
python3 .github/scripts/test_ci_workflow.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git grep <matrix-forbidden-wording-expression> -- README.md docs/milestone-e-prep-scope.md docs/roadmap.md docs/execution-status.md docs/demos examples fixtures schemas
git grep <matrix-record-private-path-expression> -- docs/validation/milestone-e-internal-trust-loop-rehearsal-evidence-matrix-validation-2026-06-19.md
git diff --check
```

The grep command used the forbidden matrix wording covered by
`.github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py`; active
non-validation surfaces returned no matches.

## Result

```text
internal trust-loop rehearsal/evidence matrix guard green
matrix rows exactly matched the current use-protocol steps
matrix rows exactly matched the current walkthrough steps
matrix rows exactly matched current fixture-promotion criteria
schema/example validation green
Milestone E prep scope guard green
CI workflow static guard green
public-surface posture and claims gates green
Milestone E prep target green
active-surface forbidden-wording grep returned no matches
git diff --check green
```

## Validated Matrix Boundary

- The matrix stays source-only, internal, and non-public.
- The matrix scope remains `internal_trust_loop_rehearsal_evidence_matrix`.
- The matrix boundary remains `internal_source_only_rehearsal_evidence_matrix`.
- The matrix status remains
  `internal_source_only_rehearsal_evidence_matrix_defined_not_executed`.
- Each row status remains `internal_source_only_rehearsal_defined_not_promoted`.
- The matrix promotion status remains `not_promoted_beyond_internal_fixture_planning`.
- The matrix references `docs/milestone-e-fixture-candidates.json`.
- The matrix references `docs/milestone-e-fixture-promotion-criteria.json`.
- The matrix references `docs/milestone-e-internal-trust-loop-walkthrough.json`.
- The matrix references `docs/milestone-e-internal-trust-loop-use-protocol.json`.
- The matrix references only current protocol step ids and candidate ids.
- Each matrix row exactly matches its protocol step for validation command, input fixtures,
  diagnostic boundary, blocker wording, and promotion status.
- Each matrix row exactly matches its walkthrough step and criteria entry for validation command,
  input fixtures, diagnostic boundary, blocker wording, and promotion status.
- Required input fixtures are relative, tracked, and path-backed.
- Validation commands are existing allowlisted Make targets.
- Evidence lanes are exactly evidence grounding, diagnostics, fixture/evaluator validation, and
  explicit blockers.
- Schema validation covers the matrix plan and schema.
- Public boundaries remain explicit and blocked.

## Validated Matrix Rows

- `native-grounding-baseline` maps `native-verification-trust-loop` to `make verify-alpha`.
  Inputs are `examples/verify/cases.json` and
  `examples/verify/goldens/native_grounded_report.json`. Its diagnostic boundary is:
  `Native quote, table-cell, and presence evidence checks over checked-in document JSON.` The
  `public result wording` and `public-report blockers` blockers remain explicit. The evidence
  lanes are evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
- `diagnostic-boundary-check` maps `split-quote-unsupported-claim-diagnostics` to
  `make verify-alpha`.
  Inputs are `examples/verify/native_split_quote_citations.json` and
  `examples/verify/native_non_v1_claims_citations.json`. Its diagnostic boundary is:
  `Adjacent native text evidence matching and explicit unsupported non-v1 claim diagnostics.`
  The `future claim-kind expansion` blocker remains explicit. The evidence lanes are evidence
  grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
- `capability-downgrade-boundary` maps `capability-downgrade-diagnostics` to
  `make milestone-d-capability-downgrade-contract`.
  Inputs are `examples/verify/capability_downgrade_v1_contract.json` and
  `examples/verify/goldens/opendataloader_capability_limited_report.json`. Its diagnostic
  boundary is: `Grounding-source capability limits surface as warnings and capability-blocked
  checks.` The `missing source capabilities` blocker remains explicit. The evidence lanes are
  evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
- `opendataloader-adapter-grounding` maps `opendataloader-style-adapter-grounding` to
  `make milestone-d-opendataloader-adapter-shape-contract`.
  Inputs are `examples/verify/opendataloader_adapter_shape_v1_contract.json` and
  `examples/verify/opendataloader.json`. Its diagnostic boundary is: `OpenDataLoader-style input
  shape maps to parser-neutral grounding metadata with deterministic adapter diagnostics.` The
  `broader foreign-adapter hardening` blocker remains explicit. The evidence lanes are evidence
  grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
- `pinned-opendataloader-fixture-path` maps `pinned-real-opendataloader-fixture-path` to
  `make verify-alpha`.
  Inputs are `fixtures/foreign/opendataloader/real/manifest.json`,
  `fixtures/foreign/opendataloader/real/expected.verification_report.json`, and
  `fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json`. Its
  diagnostic boundary is: `Pinned foreign output exercises grounded and ungrounded verification
  paths without public comparison wording.` The `public comparison reports` and `claim wording`
  blockers remain explicit. The evidence lanes are evidence grounding, diagnostics,
  fixture/evaluator validation, and explicit blockers.
- `crop-descriptor-source-bound-shape` maps `crop-descriptor-source-bound-crop-shape` to
  `make milestone-d-internal-contracts`.
  Inputs are `examples/crop/crop_element_v1_contract.json` and
  `examples/crop/crop_element_surface_shape_v1_contract.json`. Its diagnostic boundary is:
  `Source-bound crop descriptor identity and callable CLI/Python surface shape remain tied to
  current request and descriptor schemas.` The `Node crop surfaces`, `MCP crop surfaces`,
  `hosted crop surfaces`, `sandbox-backed crop surfaces`, and `foreign-adapter crop surfaces`
  blockers remain explicit. The evidence lanes are evidence grounding, diagnostics,
  fixture/evaluator validation, and explicit blockers.
- `rag-chunk-artifact-loop` maps `rag-chunk-artifact-loop` to `make rag-chunk-alpha`.
  Input is `schemas/examples/chunks.example.jsonl`. Its diagnostic boundary is:
  `RAG chunk output stays fixture-backed with stale-reference and warning-reference validation.`
  The `broader provenance integration`, `broader citation integration`, `parser integration`, and
  `table integration` blockers remain explicit. The evidence lanes are evidence grounding,
  diagnostics, fixture/evaluator validation, and explicit blockers.
- `security-report-artifact-loop` maps `security-report-artifact-loop` to
  `make security-report-alpha`.
  Input is `schemas/examples/security-report.example.json`. Its diagnostic boundary is:
  `Security-report output stays source-grounded with locator, warning-lane, and summary
  diagnostics.` The `broader security-report generation semantics` and `artifact UX` blockers
  remain explicit. The evidence lanes are evidence grounding, diagnostics, fixture/evaluator
  validation, and explicit blockers.
- `demo-narrative-index` maps `demo-narrative-index` to `make verify-alpha`.
  Input is `docs/demos/verify-alpha.md`. Its diagnostic boundary is: `Existing narrative index
  remains tied to checked-in alpha verification fixtures and posture guards.` The
  `broad demo-generation` and `public result wording` blockers remain explicit. The evidence
  lanes are evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers.

## Remaining Boundaries

- Public reports remain blocked.
- Public result wording remains blocked.
- Hosted surfaces remain blocked.
- Release artifacts remain blocked.
- Package publication remains blocked.
- Production positioning remains blocked.
- Broad demo-generation workflows remain blocked.
- Performance claims remain blocked.
- Quality claims remain blocked.
- Footprint claims remain blocked.
- Table-quality claims remain blocked.
- Parser-quality claims remain blocked.

## Follow-up

Future matrix changes require this guard to stay green and require either a new validation record or
an explicit superseding record. Internal rehearsal planning remains limited to source-checkout
validation over the existing fixture candidates until blockers are explicitly resolved in a later
source-only slice.
