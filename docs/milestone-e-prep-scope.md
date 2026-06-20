# Milestone E Prep Scope

Status: source-only pre-alpha prep for internal Milestone E continuation.

This note defines the first narrow Milestone E prep slice. It does not approve public benchmark
reports, release artifacts, package publication, production positioning, public result wording, or
performance, quality, footprint, table-quality, or parser-quality claims. ADR-0005 remains an
internal continuation decision only.

## Purpose

Milestone D closed the current source-only contract boundary. Milestone E prep starts by preserving
that boundary while selecting already-validated trust-loop artifacts that can support internal demo
fixture planning.

The prep slice is allowed to:

- document the source-only pre-alpha E prep boundary;
- identify existing D and C trust-loop artifacts that are candidates for internal E demo fixtures;
- keep claim language tied to evidence grounding, diagnostics, fixture/evaluator validation, and
  explicit blockers;
- add static guards that prevent this prep note from becoming public launch or result wording.

The prep slice is not allowed to:

- create public report wording or public result summaries;
- add hosted surfaces, package/distribution work, or release artifacts;
- expand Node, MCP, sandbox-backed, or foreign-adapter crop surfaces;
- claim speed, footprint, quality, table-quality, parser-quality, or production readiness;
- treat the E prep fixture list as a finished demo plan.

## Internal Demo Fixture Candidates

The current E prep candidate set is restricted to tracked source-tree artifacts already covered by
existing guards. The machine-readable inventory is
`docs/milestone-e-fixture-candidates.json` and is schema-bound by
`schemas/ethos-milestone-e-fixture-candidates.schema.json`. Internal fixture-promotion criteria
live in `docs/milestone-e-fixture-promotion-criteria.json` and are schema-bound by
`schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json`; they define what must be
rechecked before a candidate can enter an internal demo plan, not public demo approval. Each
candidate row must keep a structured `blockers_must_remain_explicit` list that matches the
promotion criteria row before any internal fixture-planning use.
The internal trust-loop walkthrough plan lives in
`docs/milestone-e-internal-trust-loop-walkthrough.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json`. It sequences the current
fixture-candidate inventory for internal source-only planning, not public result wording.
The internal trust-loop use protocol lives in
`docs/milestone-e-internal-trust-loop-use-protocol.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json`. It defines only the
required source-checkout validation and blocker-preservation rules for internal walkthrough use,
not public result wording.
The internal trust-loop rehearsal/evidence matrix lives in
`docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json`. It maps
the existing use-protocol steps to evidence grounding, diagnostics, fixture/evaluator validation,
and explicit blockers for internal source-only rehearsal planning, not public result wording.
The internal trust-loop blocker ledger lives in
`docs/milestone-e-internal-trust-loop-blocker-ledger.json` and is schema-bound by
`schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json`. It derives explicit
blockers from the rehearsal/evidence matrix and keeps them visible for internal source-only
planning; it does not resolve or soften blockers and is not public result wording.
The public approval lane blocker ledger lives in
`docs/milestone-e-public-approval-lane-blockers.json` and is schema-bound by
`schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json`. It records source-only
public beta evaluation as approved for the GitHub source repository while keeping package
publication, hosted surface, production positioning, public benchmark report, public benchmark
claim, release-artifact, binary, wheel, npm package, crate publication, and project-maintained
PDFium build lanes blocked; it is not public result wording.
The public beta approval prep lane lives in
`docs/milestone-e-public-beta-approval-prep.json` and is schema-bound by
`schemas/ethos-milestone-e-public-beta-approval-prep.schema.json`. It records the source-only
public beta approval for reviewed commit `d755e7c` and merged main commit `3f9e1c4`, whose source
trees match, and records the exact allowed wording, setup boundary, and exclusions.
The public beta required-evidence records live in
`docs/validation/milestone-e-public-beta-approval-decision-validation-2026-06-20.md`,
`docs/validation/milestone-e-public-beta-release-scope-engineering-blocker-review-validation-2026-06-20.md`,
`docs/validation/milestone-e-public-beta-public-setup-path-review-validation-2026-06-20.md`,
and `docs/validation/milestone-e-public-beta-pdfium-build-path-review-validation-2026-06-20.md`.
They complete the evidence-record set that was later rescoped by
`docs/validation/milestone-e-public-beta-source-only-approval-validation-2026-06-20.md`; the
source-only approval record does not approve package publication, hosted surfaces, production
positioning, public benchmark reports, public benchmark claims, release artifacts, binaries, wheels,
npm packages, crate publication, or project-maintained PDFium builds.
The package publication approval prep lane lives in
`docs/milestone-e-package-publication-approval-prep.json` and is schema-bound by
`schemas/ethos-milestone-e-package-publication-approval-prep.schema.json`. It approves internal
Rust crate publication preparation only for the five ADR-0006 reserved priority crates.io
identifiers, records required evidence, exact blockers, allowed/forbidden wording, and the PDFium
packaging boundary, and does not approve package publication, real-version `cargo publish`, public
installation, release artifacts, binaries, wheels, npm packages, hosted surfaces, production
positioning, public benchmark reports, or public benchmark claims.
The use protocol, rehearsal/evidence matrix, and blocker ledger must keep the same blocked-output
alignment so public reports, public result wording, hosted surfaces, release artifacts, package
publication, production positioning, broad demo-generation workflows, benchmark publication, and
all performance, quality, footprint, table-quality, and parser-quality claims remain explicitly
blocked.
The rehearsal/evidence matrix and blocker ledger must also keep the same evidence-lane alignment so
evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers remain the
only current internal rehearsal lanes.
All nine current E prep JSON artifacts and their row validation records must keep the same
diagnostic-boundary alignment so expected diagnostic boundaries remain tied to source-only
evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
All current E prep artifacts and rows that carry promotion status must also keep
promotion-status alignment at `not_promoted_beyond_internal_fixture_planning` until a later
source-only decision changes that state.
All current E prep artifacts must keep source-status alignment at
`source-only-pre-alpha-internal-milestone-e-prep`, and fixture-candidate rows must remain
`source-only-pre-alpha-internal-candidate`.
The current E prep artifacts with `applies_to_*` fields must keep applies-to binding alignment
across `docs/milestone-e-fixture-candidates.json`,
`docs/milestone-e-fixture-promotion-criteria.json`,
`docs/milestone-e-internal-trust-loop-walkthrough.json`,
`docs/milestone-e-internal-trust-loop-use-protocol.json`,
`docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`, and
`docs/milestone-e-internal-trust-loop-blocker-ledger.json`.
The current E prep artifacts with `required_before_*` fields must keep required-before alignment
so `make milestone-e-prep remains green`, public-surface posture checks, claims gates, diagnostic
boundaries, and explicit blockers remain required before any internal planning use advances.
Milestone E validation records must keep validation-record source-head alignment so each
`Validated source HEAD before this record` line names the source checkout state validated before
that record was added.

| Candidate | Existing artifact | Current guard |
| --- | --- | --- |
| Native verification trust loop | `examples/verify/cases.json` and `examples/verify/goldens/native_grounded_report.json` | `make verify-alpha` |
| Split-quote and unsupported-claim diagnostics | `examples/verify/native_split_quote_citations.json` and `examples/verify/native_non_v1_claims_citations.json` | `make verify-alpha` |
| Capability downgrade diagnostics | `examples/verify/capability_downgrade_v1_contract.json` and `examples/verify/goldens/opendataloader_capability_limited_report.json` | `make milestone-d-capability-downgrade-contract` |
| OpenDataLoader-style adapter grounding | `examples/verify/opendataloader_adapter_shape_v1_contract.json` and `examples/verify/opendataloader.json` | `make milestone-d-opendataloader-adapter-shape-contract` |
| Pinned real OpenDataLoader fixture path | `fixtures/foreign/opendataloader/real/manifest.json`, `fixtures/foreign/opendataloader/real/expected.verification_report.json`, and `fixtures/foreign/opendataloader/real/expected.ungrounded.verification_report.json` | `make verify-alpha` |
| Crop descriptor and source-bound crop shape | `examples/crop/crop_element_v1_contract.json` and `examples/crop/crop_element_surface_shape_v1_contract.json` | `make milestone-d-internal-contracts` |
| RAG chunk artifact loop | `schemas/examples/chunks.example.jsonl` | `make rag-chunk-alpha` |
| Security-report artifact loop | `schemas/examples/security-report.example.json` | `make security-report-alpha` |
| Demo narrative index | `docs/demos/verify-alpha.md` | `make verify-alpha` |

These are internal fixture candidates, not public proof points. Any future demo plan must still
state the validated command, input fixture, expected diagnostic boundary, blocker status, and every
structured blocker before the fixture can be promoted beyond source-only pre-alpha planning.

## Prep Guard

Focused validation command:

- `make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python`

The target runs status/roadmap posture checks, public-surface posture checks, the claims gate,
public pre-alpha wording approval, release-readiness next-step approval, H1 public-safe comparison
closeout validation, H2 source-snapshot scope approval, source-snapshot candidate audit,
H2 source-snapshot candidate evidence, H2 source-snapshot closeout, schema/example validation,
schema-registry alignment for the E prep JSON artifacts, public-boundary alignment,
blocked-output alignment, evidence-lane alignment, diagnostic-boundary alignment,
promotion-status alignment, source-status alignment, applies-to binding alignment,
required-before alignment, validation-record source-head alignment, this prep-scope guard,
fixture-candidate blocker-alignment validation,
the internal trust-loop walkthrough, use-protocol,
rehearsal/evidence matrix, blocker-ledger guards, and public approval lane blocker guard,
public beta approval prep guard, public beta required-evidence record guard,
public beta source-only approval guard,
package publication approval prep guard,
package publication prep approval validation guard,
validation-command index checks,
validation-record index checks, the prep guard-sequence index, validation-record guards, and diff
hygiene. It intentionally does not run public-report, release, package, hosted, benchmark-report,
or broad demo-generation workflows.

## Exit Criteria For This Prep Slice

- `docs/roadmap.md` and `docs/execution-status.md` point to this prep boundary.
- The source-tree guard keeps the fixture-candidate list explicit and path-backed.
- The source-tree guard keeps internal fixture-promotion criteria aligned with the candidate
  inventory.
- The schema validation gate keeps the fixture-candidate inventory and fixture-promotion criteria
  closed to unreviewed fields.
- The schema-registry alignment guard keeps the nine E prep JSON artifacts and their nine schemas in
  one-to-one sync across schema validation and source-tree status docs.
- Fixture-candidate blocker lists remain structured, nonempty, and visible before any internal
  fixture-planning use.
- The internal trust-loop walkthrough plan remains limited to existing candidates and criteria.
- The internal trust-loop use protocol remains limited to existing walkthrough steps and explicit
  blockers.
- The internal trust-loop rehearsal/evidence matrix remains limited to existing protocol steps,
  evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers.
- The internal trust-loop blocker ledger remains limited to existing matrix rows and does not
  resolve or soften blockers.
- The public approval lane blocker ledger records source-only public beta evaluation approval and
  keeps package publication, hosted surfaces, production positioning, public benchmark reports,
  public benchmark claims, release artifacts, binaries, wheels, npm packages, crate publication, and
  project-maintained PDFium builds blocked.
- The public beta approval prep lane remains limited to source-only public beta evaluation for the
  GitHub source repository and records the exact approved wording and exclusions.
- The public beta required-evidence records remain historical evidence for the blocker reviews
  rescoped by the source-only public beta approval record.
- The package publication approval prep lane remains limited to internal Rust crate publication
  preparation for the five ADR-0006 reserved priority crates.io identifiers, remains
  `prep_approved_publication_blocked`, and does not approve package publication.
- Blocked-output alignment remains identical across the use protocol, rehearsal/evidence matrix,
  blocker ledger, and matching schemas.
- Evidence-lane alignment remains identical across the rehearsal/evidence matrix, blocker ledger,
  and matching schemas.
- Diagnostic-boundary alignment remains identical across the fixture candidates, promotion
  criteria, walkthrough, use protocol, rehearsal/evidence matrix, blocker ledger, matching schemas,
  and row validation records.
- Promotion-status alignment remains `not_promoted_beyond_internal_fixture_planning` across
  current artifacts, rows, matching schemas, and row validation records.
- Source-status alignment remains `source-only-pre-alpha-internal-milestone-e-prep` across current
  artifacts and `source-only-pre-alpha-internal-candidate` across fixture-candidate rows.
- Applies-to binding alignment remains exact across current fixture-candidate inventory,
  fixture-promotion criteria, walkthrough, use protocol, rehearsal/evidence matrix, blocker ledger,
  and matching schemas.
- Required-before alignment remains exact across fixture-promotion criteria, walkthrough, use
  protocol, rehearsal/evidence matrix, blocker ledger, and matching schemas.
- Validation-record source-head alignment remains exact across Milestone E validation records.
- Public language remains limited to the exact source-only public beta wording for the approved
  GitHub source repository surface and internal-continuation scoped outside that surface.
- External blockers remain visible before any public-facing Milestone E work starts.
