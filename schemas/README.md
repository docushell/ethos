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
| `ethos-crop-descriptor.schema.json` | crop descriptor JSON emitted by `ethos verify --crop-dir` |
| `ethos-verify-citations-contract.schema.json` | Milestone D `verify_citations` v1 source-only contract inventory |
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

Derived artifacts not schema'd here: `document.md` / `document.txt` (deterministic exports
specified by the exporter config, Milestone B) and `debug.html` (Milestone C).
