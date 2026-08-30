# CI Scope

Status: active. Governs what runs on every PR and what is deliberately parked.

## The rule

**CI enforces product correctness and architectural invariants. Nothing else.**

Publication gates that protect public statements run on every PR, in the `gates` job.
Gates that need release artifacts, a live registry, or a candidate build stay parked behind
`make release-gates` and run before any real publish.

The split moved in the direction "Restoring the gates" below prescribes. What forced it was
not policy but evidence: while parked, the gates did not stay still. The published GitHub
Action drifted two releases behind its own contract test, `docs/release-state.json` disagreed
with the live release in three places, and the PDF determinism step reported green while
skipping. Every one of those was invisible because the check that would have caught it was
unreachable, and every one surfaced within an hour of making them reachable again.

This is a deliberate scope decision, not decay. Before it, CI ran 81 steps across a
269-line workflow, and roughly two thirds of the scripts under `.github/scripts/`
were tests asserting that the release machinery was wired correctly rather than tests
of Ethos. That cost was worth paying while defending live claims. It is
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
| `gates` | public claims and wording, posture, ledger consistency, boundary paths, golden-change rationale, validation records, registry surfaces |
| `dco` | sign-offs on every commit |

The determinism workflow (`determinism.yml`) is separate and unchanged. Byte-equality
goldens are not negotiable and never move into this document's scope decision.

## What is parked

What is left under `make release-gates` is what genuinely cannot run on a PR: live GitHub
release metadata, readiness, execution status, validation record source, version activation,
the `ethos-full` and Windows candidate contracts, and publication dry-run smoke. These need a
published registry, a release artifact, or a candidate build.

`make release-gates` is still the single home for those, and it now calls
`release-live-state-check` rather than `release-state-check`, so it compares the ledger against
the real registry instead of against itself. If you park another gate, add it there in the same
commit so it stays findable. If a gate can run on a PR, it belongs in `gates` instead.

The frozen closed-lane record layer is gone. Its manifest listed one guard that the same suite
already ran twice elsewhere.

## Why `test_gate_reachability.py` was removed

It grepped `ci.yml` for literal script paths to prove no gate had been orphaned. That
guard existed for a real reason: gates that only ran from a `make` target had silently
rotted for months. But it enforces "every gate runs on every PR," which is the exact
policy this document changes. Parked gates are now reachable from one target instead,
and that target is the thing to check.

Recorded honestly, because the prediction was tested and the guard was right: within three
weeks of its removal, `cargo_manifest_guard.py` and `frozen_record_guard_wiring.py` had zero
references tree-wide, `make ethos-verify-action-contract` and
`make app-answer-release-demo` had rotted into failure, and the published Action was two
releases behind. "That target is the thing to check" only works if someone checks it.

## Restoring the gates

Exiting stealth was the trigger, and v0.6.0 fired it.

1. **Done.** `make release-gates` was run and four real defects were fixed: the v0.5.0 release
   body, the declared asset list, the declared release name, and the published GitHub Action's
   version pin.
2. **Done.** The claims and wording gates are back in CI, in `gates`. They protect public
   statements and public statements are the thing that returned.
3. **Open.** Whether reachability enforcement comes back. The case for it is stronger than
   when `test_gate_reachability.py` was removed: three weeks after that deletion, six scripts
   had zero references tree-wide and two `make` targets had rotted into failure without anyone
   noticing. If it returns, scope it to the keeper set rather than to every script in the tree.

## Closed-milestone guards

The nine `test_milestone_d_*.py` guards and their `make` targets are removed. They
asserted prose, not behaviour: that a doc contained a specific sentence, that the
Makefile declared `.PHONY`, that one document linked to another. The only real tests
inside those targets were `cargo test` invocations that already run under
`cargo test --workspace --all-features`.

The Milestone D contract documents themselves stay in `docs/`. They describe real
behavioural contracts, they are cross-referenced from the threat model and from live
implementation plans, and they cost nothing to keep. Ethos sells auditability; deleting
its own contract history would be the wrong instinct. `docs/validation/` stays for the
same reason, and because `docs/release-state.json` resolves into it.
