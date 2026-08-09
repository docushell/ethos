# CI Scope

Status: active. Governs what runs on every PR and what is deliberately parked.

## The rule

**CI enforces product correctness and architectural invariants. Nothing else.**

Publication gates do not run on PRs while Ethos is pre-publication. They are parked
behind `make release-gates` and run manually before any real publish.

This is a deliberate scope decision, not decay. Before it, CI ran 81 steps across a
269-line workflow, and roughly two thirds of the scripts under `.github/scripts/`
were tests asserting that the release machinery was wired correctly rather than tests
of Ethos. That cost was worth paying for a public beta defending live claims. It is
not worth paying while nothing is published.

## What CI runs

| Job | What it protects |
| --- | --- |
| `fmt` | formatting |
| `clippy` | lints, including the disallowed network APIs from `clippy.toml` (invariant 5b) |
| `deny` | ADR-0004 license allowlist, network-crate bans, advisories (invariants 5a, 6) |
| `test` | unit and fixture tests, c14n property tests, contract vectors, validator resource ceiling, Python surface, npm package integrity |
| `dogfood` | the product claim end to end: grounded citations exit 0, fabricated exit 1 |
| `verify-portability` | invariant 4 — `ethos-verify` builds against the grounding trait alone, with no parser internals in its tree |
| `schema-validate` | published schemas validate their examples |
| `no-network-runtime` | invariant 5c — the CLI runs with zero egress under a network-denied namespace |
| `dco` | sign-offs on every commit |

The determinism workflow (`determinism.yml`) is separate and unchanged. Byte-equality
goldens are not negotiable and never move into this document's scope decision.

## What is parked

Everything under `make release-gates`: release state, GitHub release metadata, registry
source consistency, claims and public-wording gates, boundary paths, frozen closed-lane
records, readiness, execution status, validation record source, version activation,
candidate contracts, and publication dry-run smoke.

`make release-gates` is the single home for these. If you park another gate, add it there
in the same commit so it stays findable.

## Why `test_gate_reachability.py` was removed

It grepped `ci.yml` for literal script paths to prove no gate had been orphaned. That
guard existed for a real reason: gates that only ran from a `make` target had silently
rotted for months. But it enforces "every gate runs on every PR," which is the exact
policy this document changes. Parked gates are now reachable from one target instead,
and that target is the thing to check.

## Restoring the gates

Exiting stealth is the trigger. When Ethos publishes again:

1. Run `make release-gates` and fix whatever has drifted.
2. Move the claims and wording gates back into CI first. They protect public statements
   and public statements are the thing that returns.
3. Decide then whether reachability enforcement comes back, and if so, scope it to the
   keeper set rather than to every script in the tree.

## Archived material

Closed-milestone contract guards, their docs, and historical validation records live in
`docs/archive/`. They are kept because Ethos sells auditability and deleting your own
audit trail is the wrong instinct. They are not wired to anything.
