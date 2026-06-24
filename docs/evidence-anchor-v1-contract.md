# Evidence Anchor V1 Contract Guard

Status: source-only public beta evaluation guard for the current `ethos evidence anchor` surface.

This note defines the narrow post-merge guard for `evidence_anchor` v1. It does not change the
approved public beta/evaluation posture, and it does not approve any hosted, production, benchmark,
parser-quality, table-quality, Windows, bundled-PDFium, `ethos-doc`, or `ethos-rag` surface.

The current executable carrier is the `ethos evidence anchor` CLI command. It consumes a single
source artifact plus caller-provided evidence refs and emits a deterministic evidence anchor
report. The command remains parser- and app-agnostic: native Ethos JSON and OpenDataLoader-style
JSON are current grounding inputs, while downstream applications decide what to do with the
report.

## Contract Surface

`evidence_anchor` v1 covers:

- request and report envelope identity through `ethos.evidence_anchor_request.v1` and
  `ethos.evidence_anchor_report.v1`;
- caller-provided evidence refs with page, text, text-region, and table-cell locator checks;
- native Ethos JSON and OpenDataLoader-style JSON grounding inputs;
- deterministic per-ref outcomes: `bound`, `mismatch`, `not_found`, `stale_fingerprint`,
  `capability_limited`, and `unsupported_evidence_kind`;
- usage errors for malformed request shape, missing required locator/text inputs, unknown
  grounding modes, and unsupported source artifact shape.

The executable inventory is `examples/verify/evidence_anchor_v1_contract.json`. It binds the
current command surface to schema examples, focused CLI tests, the OpenDataLoader adapter test
suite, and status/roadmap guard scripts.

## Validation Target

- `make evidence-anchor-v1-contract PYTHON=<jsonschema-venv>/bin/python`

The target runs the focused evidence-anchor CLI tests, the OpenDataLoader adapter tests,
schema/example validation, status guards, roadmap guards, this contract guard, and whitespace diff
checks.

## Boundaries Locked By This Guard

- one command: `ethos evidence anchor`;
- one source artifact per invocation;
- caller-provided evidence refs in, deterministic anchor report out;
- native Ethos JSON and OpenDataLoader-style JSON only;
- non-bound per-ref outcomes remain report data and exit `0`;
- request/schema/source-shape usage errors remain exit `2`;
- table-cell expected text uses normalized equality, not substring matching;
- mismatch takes precedence over capability-limited when a checked required axis fails.

## Explicit Blockers For This Slice

This `evidence_anchor` guard does not add:

- semantic answer verification;
- multi-source joins;
- crop rendering or source-region image generation;
- hosted API or service surfaces;
- DocuShell-specific behavior;
- production positioning;
- benchmark, speed, footprint, parser-quality, or table-quality claims.

Until those blockers are explicitly handled, public language remains limited to public beta
evaluation of deterministic evidence anchoring over the currently approved surfaces.
