# Ethos Schemas — the product contract

JSON Schema draft 2020-12. `$id`s use `urn:ethos:schema:<name>:<major>` so schema identity
survives any package rename (ADR-0006). Changes only via `contract-change` PRs with version
bumps and downstream sign-off; output-changing heuristics are semver events (PRD §5.1).

| Schema | Artifact it governs |
| --- | --- |
| `ethos-document.schema.json` | `ethos.json` — canonical document graph (primary artifact) |
| `ethos-chunks.schema.json` | `chunks.jsonl` — one self-describing RAG chunk per line |
| `ethos-security-report.schema.json` | `security_report.json` |
| `ethos-citations.schema.json` | citation input consumed by `ethos verify --citations` |
| `ethos-verification-report.schema.json` | `verification_report.json` |
| `ethos-verification-config.schema.json` | verification config (its c14n hash stamps reports) |
| `ethos-crop-descriptor.schema.json` | crop descriptor JSON emitted by `ethos crop_element` and `ethos verify --crop-dir` |
| `ethos-crop-element-request.schema.json` | source-only request envelope for Milestone D `crop_element` v1 contract work |
| `ethos-verify-citations-contract.schema.json` | Milestone D `verify_citations` v1 source-only contract inventory |
| `ethos-claim-kind-boundary-contract.schema.json` | Milestone D `claim_kind_boundary` v1 source-only contract inventory |
| `ethos-grounding-source-contract.schema.json` | Milestone D `grounding_source` v1 source-only contract inventory |
| `ethos-capability-downgrade-contract.schema.json` | Milestone D `capability_downgrade` v1 source-only contract inventory |
| `ethos-opendataloader-adapter-shape-contract.schema.json` | Milestone D `opendataloader_adapter_shape` v1 source-only contract inventory |
| `ethos-crop-element-contract.schema.json` | Milestone D `crop_element` v1 source-only contract inventory |
| `ethos-crop-element-surface-shape-contract.schema.json` | Milestone D `crop_element_surface_shape` v1 source-only contract inventory |
| `ethos-sandbox-subprocess-request.schema.json` | source-only request envelope for Milestone D `sandbox_subprocess` v1 contract work |
| `ethos-sandbox-subprocess-contract.schema.json` | Milestone D `sandbox_subprocess` v1 source-only contract inventory |
| `ethos-deterministic-profile.schema.json` | `profiles/ethos-deterministic-v*.json` checker |

Conventions: snake_case keys; `additionalProperties: false` everywhere except the
runtime-only `diagnostics` envelope field; geometry is integer quanta (no floats anywhere in
canonical values); confidences are integer per-mille; fingerprints are `sha256:<64 lowercase
hex>`; ID grammar and ordering are normative in `docs/determinism-contract.md` §5.

`examples/` validate in CI via `validate_examples.py` (also enforces referential integrity
and bbox sanity that JSON Schema cannot express). The examples are documentation-grade — keep
them small, valid, and mutually consistent (same fingerprints across document / chunks /
security-report / verification-report examples).

`verification-report.example.json` shows a grounded report.
`verification-report-negative.example.json` shows a non-grounded report with a per-check
`reason` label.

Milestone D `verify_citations` v1 contract work is tracked in
`docs/milestone-d-verify-citations-contract.md`. In this source-only pre-alpha slice,
`verify_citations` names the citation-input to verification-report contract currently carried by
`ethos verify`; it does not add a new command or binding surface. The contract inventory at
`examples/verify/verify_citations_v1_contract.json` is schema-validated here; its alignment with
the executable case inventory and report goldens is checked by the Milestone D repository guard.

Milestone D `claim_kind_boundary` v1 contract work is tracked in
`docs/milestone-d-claim-kind-boundary-contract.md`. In this source-only pre-alpha slice,
`claim_kind_boundary` names the supported v1 claim-kind boundary currently carried by
`ethos verify`; it does not add new claim-kind support or a new command/binding surface. The
contract inventory at `examples/verify/claim_kind_boundary_v1_contract.json` is schema-validated
here; its alignment with the committed non-v1 claim fixture and report golden is checked by the
Milestone D repository guard.

Milestone D `grounding_source` v1 contract work is tracked in
`docs/milestone-d-grounding-source-contract.md`. In this source-only pre-alpha slice,
`grounding_source` names the parser-neutral evidence boundary currently carried by the
`GroundingSource` trait and `ethos verify` report grounding metadata; it does not add a new
command or binding surface. The contract inventory at
`examples/verify/grounding_source_v1_contract.json` is schema-validated here; its alignment with
trait methods, source implementations, focused verifier tests, and report goldens is checked by
the Milestone D repository guard.

Milestone D `capability_downgrade` v1 contract work is tracked in
`docs/milestone-d-capability-downgrade-contract.md`. In this source-only pre-alpha slice,
`capability_downgrade` names the grounding-source capability declaration to verification-report
downgrade contract currently carried by `ethos verify`; it does not add a new command or binding
surface. The contract inventory at `examples/verify/capability_downgrade_v1_contract.json` is
schema-validated here; its alignment with report goldens is checked by the Milestone D repository
guard.

Milestone D `opendataloader_adapter_shape` v1 contract work is tracked in
`docs/milestone-d-opendataloader-adapter-shape-contract.md`. In this source-only pre-alpha
slice, `opendataloader_adapter_shape` names the adapter input-shape to `GroundingSource`
contract currently carried by `ethos-grounding-opendataloader-json` and
`ethos verify --grounding opendataloader-json`; it does not add a new command or binding surface.
The contract inventory at `examples/verify/opendataloader_adapter_shape_v1_contract.json` is
schema-validated here; its alignment with adapter tests, CLI grounding tests, report goldens, and
usage diagnostics is checked by the Milestone D repository guard.

Milestone D `crop_element` v1 contract work is tracked in
`docs/milestone-d-crop-element-contract.md`. In this source-only pre-alpha slice,
`crop_element` names the element-to-crop-descriptor contract currently carried by the
descriptor-only `ethos crop_element` CLI command. The existing `ethos verify --crop-dir` carrier
continues to emit verifier evidence artifacts from the same descriptor type. The request envelope
example at `schemas/examples/crop-element-request.example.json` and contract inventory at
`examples/crop/crop_element_v1_contract.json` are schema-validated here; their alignment with the
document and crop-descriptor examples is checked by the Milestone D repository guard. The request
envelope carries a c14n-derived `request_ref` identity guarded in that same source-only contract
check.

Milestone D `crop_element_surface_shape` v1 contract work is tracked in
`docs/milestone-d-crop-element-surface-shape-contract.md`. In this source-only pre-alpha slice,
`crop_element_surface_shape` names the callable crop surface shape that must preserve the
existing crop request and descriptor bindings. The contract inventory at
`examples/crop/crop_element_surface_shape_v1_contract.json` is schema-validated here; its
alignment with the request schema, descriptor schema, descriptor-only CLI command, and absent
Python crop method is checked by the Milestone D repository guard.

Milestone D `sandbox_subprocess` v1 contract work is tracked in
`docs/milestone-d-sandbox-subprocess-contract.md`. In this source-only pre-alpha slice,
`sandbox_subprocess` names the future worker-boundary contract currently represented by the
existing PDF worker process behind `ethos doc parse` and `ethos fingerprint`; it does not add a
hardened sandbox or a new command/binding surface. The request envelope examples under
`schemas/examples/sandbox-subprocess-*.example.json` and the contract inventory at
`examples/sandbox/sandbox_subprocess_v1_contract.json` are schema-validated here; their alignment
with the executable worker tests is checked by the Milestone D repository guard. Each request
envelope carries a c14n-derived `request_ref` identity guarded in that same source-only contract
check.

Derived artifacts not schema'd here: `document.md` / `document.txt` (deterministic exports
specified by the exporter config, Milestone B) and `debug.html` (Milestone C).
