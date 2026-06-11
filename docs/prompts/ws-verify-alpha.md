# WS-VERIFY-ALPHA Implementation Prompt

Use this prompt when starting the next implementation lane after the current WS-ENGINE /
WS-HARNESS checkpoints.

## Target Lock

Start **WS-VERIFY-ALPHA**.

Implement the first real `ethos verify` flow over `GroundingSource`.

Strategic principle from ADR-0007:

> Ethos is a verification and grounding layer that includes a deterministic parser, not a parser
> that may later add verification.

Do not expand parser, layout, table, OCR, crop, or PDFium scope in this task.

## Scope

Implement quote and presence citation checks over:

1. Native Ethos document JSON.
2. OpenDataLoader-style JSON through `--grounding opendataloader-json`.

Required behavior:

- Read citations JSON from `--citations`.
- Produce a `verification_report.json` with non-empty checks.
- Support existing schema statuses: `grounded`, `not_found`, `mismatch`, `stale`,
  `unsupported_claim_kind`, `capability_blocked`, and `error`.
- Do not invent new status values unless this task explicitly performs a contract/schema bump.
- Treat `capability_limited` as a warning/report concept, not a check status. Use
  `capability_blocked` only when a missing capability blocks a specific check.
- Implement deterministic quote normalization only: line-ending normalization, ASCII whitespace
  collapse, trim.
- Do not implement fuzzy matching, semantic matching, embeddings, model calls, or edit-distance
  fallbacks.
- Implement stale fingerprint behavior as a report-level failure:
  `fingerprint_stale=true` and `all_evidence_grounded=false`. Use check status `stale` only when a
  specific check is stale under the fingerprint policy.
- Surface missing spans, missing character offsets, unknown coordinate origin, missing fingerprint,
  and missing crop support through capability metadata or warnings. These should not block
  quote/presence checks unless the specific check requires the missing capability.
- Represent unsupported claim kinds explicitly with `unsupported_claim_kind` and
  `unsupported_claim_kinds`.
- Treat malformed citations JSON or schema-invalid citations as deterministic CLI usage errors,
  unless the schema is intentionally changed in this task.
- Preserve parser isolation: `ethos-verify` must not depend on `ethos-pdf`, `ethos-layout`,
  `ethos-tables`, PDFium, or parser internals.
- Add synthetic Ethos and OpenDataLoader fixtures.
- Add a public CLI demo where one citation passes and one fake citation fails.

Do not implement:

- Semantic verification.
- Fuzzy matching.
- Arithmetic verification.
- Table verification.
- Crops or image rendering.
- OCR.
- Layout expansion.
- Parser changes.
- New parser fixtures unrelated to verification.

## Acceptance

- `ethos verify` produces `verification_report.json` with non-empty checks.
- Native Ethos JSON path works.
- OpenDataLoader adapter path works through the public CLI.
- Stale fingerprint behavior is tested.
- Capability-limited report behavior is tested.
- Unsupported claim kinds are explicit.
- `all_evidence_grounded=false` when any check is stale, unsupported, mismatched, not found,
  capability-blocked, or semantically unverified.
- `cargo tree -p ethos-verify -e normal` proves `ethos-verify` has no parser-internal dependency.
- All listed test commands pass.

## Subagent Plan

### [Subagent: Architect-Subagent]

**Objective:** Map the existing verification schemas, `GroundingSource` trait, CLI surface, and
fixture layout. Produce the smallest implementation plan that satisfies this prompt.

**Context Provided:** `schemas/verification-report.schema.json`,
`schemas/verification-config.schema.json`, `crates/ethos-core`, `crates/ethos-verify`,
`crates/ethos-cli`, and `adapters/grounding`.

**Output Hand-off:** File-level edit plan and any schema constraints discovered. No code changes.

### [Subagent: Verify-Engine-Subagent]

**Objective:** Implement quote/presence checks, deterministic quote normalization, stale
fingerprint handling, unsupported claim kind handling, and capability warnings inside the
parser-agnostic verification layer.

**Context Provided:** Architect handoff plus the exact files needed in `crates/ethos-verify` and
`crates/ethos-core`.

**Output Hand-off:** Verification implementation and focused unit tests.

### [Subagent: Adapter-CLI-Subagent]

**Objective:** Wire native Ethos JSON and OpenDataLoader-style JSON into `ethos verify` without
adding parser dependencies.

**Context Provided:** CLI command files, grounding adapter files, and synthetic fixture shape.

**Output Hand-off:** CLI support, synthetic fixtures, and public demo command.

### [Subagent: Test-Subagent]

**Objective:** Add and run tests for native path, ODL path, stale fingerprint, capability-limited
reporting, unsupported claim kinds, one passing citation, and one failing fake citation.

**Context Provided:** Modified files and acceptance criteria above.

**Output Hand-off:** Exact commands run, pass/fail output, and dependency proof from
`cargo tree -p ethos-verify -e normal`.

## Required Verification Commands

Run the closest available equivalents if the repo command names differ:

```bash
cargo test -p ethos-verify
cargo test -p ethos-cli verify
cargo tree -p ethos-verify -e normal
python3 schemas/validate_examples.py
git diff --check
```

If any command fails, stop feature work and spawn a Debug-Subagent focused only on the failing
path.
