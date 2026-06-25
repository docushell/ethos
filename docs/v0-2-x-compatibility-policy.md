# Ethos v0.2.x Compatibility Policy

Status: preparation policy for the v0.2.0 JSON verification and evidence anchoring lane.

This policy describes what callers can expect across the `0.2.x` line once the `0.2.0` package
surfaces are approved, published, and smoke-tested. It does not record publication approval and it
does not make any `0.2.0` installability claim by itself.

## Frozen Across 0.2.x

The following contracts are stable for compatible `0.2.x` updates:

- `GroundingSource` implementer obligations and method meanings.
- Verification report schema shape and field meanings.
- Evidence anchor request and report schema shape and field meanings.
- Default verification config semantics, including fingerprint matching.
- CLI JSON input/output shape for `ethos verify`.
- CLI JSON input/output shape for `ethos evidence anchor`.
- RAG chunk text projection contract.
- Verify exit-code classification.
- Evidence-anchor no-fail-flag behavior.

## Allowed In 0.2.x

Compatible `0.2.x` updates may include:

- additive fields;
- additive diagnostics;
- additive warnings;
- documentation clarifications;
- bug fixes that make invalid input fail closed;
- new examples and tests.

## Requires 0.3.0

The following changes require a new minor line:

- removing or renaming public fields;
- changing default fingerprint behavior;
- changing report meaning;
- changing `GroundingSource` obligations;
- changing chunk text projection semantics;
- reclassifying normal verification verdicts as tool failures;
- adding an evidence-anchor fail flag if it changes CLI or Python wrapper expectations.

## Breaking-Change Process

A breaking contract change requires:

- a contract-change PR;
- a changelog entry;
- a migration note;
- schema and example updates;
- public-claims review.

