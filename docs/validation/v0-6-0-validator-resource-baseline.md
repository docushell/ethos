# v0.6.0 Grounding JSON Validator Resource Baseline

Status: **accepted** (2026-07-31). Ceiling set at 40 µs and 2 KB per element. Frozen structural
limits unchanged; the working set is documented rather than reduced.

Release-prep §12 asks for resource and performance evidence showing no unacceptable regression
against the frozen v0.5.0 verification baseline, with a numeric ceiling set before implementation
freeze.

## Why this measures something different

A regression comparison against v0.5.0 verification would measure nothing. Grounding JSON adds a
parallel loader in front of the existing `GroundingSource` boundary; no existing verification code
path changes, which the unchanged native and OpenDataLoader goldens already demonstrate.

The decision-relevant question is what the **new** validator costs at the limits ADR-0016 froze.

## Method

`target/release/ethos grounding check <artifact> --out <report>` on `darwin:x64`, release profile,
after a discarded cold run. Wall clock and peak RSS from `/usr/bin/time -l`. Synthetic artifacts,
all structurally valid, capabilities all `false`.

## Measurements

| Artifact | Elements | Input | Wall | Peak RSS | RSS ÷ input |
| --- | --- | --- | --- | --- | --- |
| small | 10 | 3 KB | 30 ms | 1 MB | — |
| medium | 10,000 | 1.5 MB | 150 ms | 14 MB | 9.3× |
| large | 100,000 | 14.8 MB | 1.85 s | 138 MB | 9.3× |
| **frozen element ceiling** | **1,000,000** | **151 MB** | **26.5 s** | **1.29 GB** | 8.5× |
| near input limit | 1,000,000 | 203 MiB | 26.9 s | 1.42 GB | 6.0× |
| over input limit | 1,000,000 | 277 MiB | 0.0 s | 1 MB | rejected |

Per element at the ceiling: **26.5 µs wall, 1.29 KB peak RSS**.

## Three findings

**1. Wall clock scales with element count, not bytes.** Holding elements at 1,000,000 and raising
input 34% (151 MB → 203 MiB) changed wall clock 1.5%. Element count is the cost driver, so a
per-element ceiling is the meaningful shape.

**2. Peak RSS runs 6–9× input size.** The validator retains the parsed artifact rather than
streaming it. The 256 MiB input limit therefore does **not** bound memory to a comparable figure: a
schema-legal artifact just under that limit reached 1.42 GB resident.

**3. The input limit fails closed and fails cheaply.** A 277 MiB artifact was rejected in 0.0 s at
1 MB RSS with exit `7` (`FileTooLarge`), before any parse work. Oversized input cannot be used to
exhaust memory.

## Operational consequence worth deciding on

**A schema-legal artifact can require roughly 1.5 GB resident and half a minute of wall clock.**

Release-prep §9.2 has DocuShell running the verifier in a bounded worker. A worker capped below
about 1.6 GB will be killed by a legal artifact rather than rejecting it, which converts a resource
limit into an opaque crash. That is an integration property, not an Ethos defect, but it should be
stated rather than discovered.

**Decision (2026-07-31): document the working set and keep the frozen limits.**

The sizing table is in `docs/writing-a-mapper.md`, where integrators meet it before running the
check. No structural limit changes, so ADR-0016 stays intact and no consumer breaks.

Two alternatives were considered and rejected for v0.6.0. Lowering the element ceiling would change
a frozen ADR limit, which is a compatibility decision rather than a tuning one. Adding a validator
memory guard that fails with the existing `MemoryLimitExceeded` (exit `11`) instead of letting the
host OOM-kill is real work; it is recorded as a v0.7.0 input alongside streaming validation.

## Accepted ceiling

Replaces the §12 v0.5.0 regression comparison with a bounded per-element resource test on the new
validator. Measured values with roughly 1.5× headroom:

- **40 µs per element wall clock**, release profile
- **2 KB per element peak RSS**

At the frozen 1,000,000-element limit that permits 40 s and 2 GB.

Wall clock is enforced by `validator_stays_within_the_accepted_resource_ceiling` in
`crates/ethos-core/src/grounding_json.rs`. It is release-only, because a debug build runs about an
order of magnitude slower than the profile the ceiling describes, and opt-in through
`ETHOS_CHECK_VALIDATOR_CEILING` because wall-clock assertions flake on shared CI runners:

```sh
ETHOS_CHECK_VALIDATOR_CEILING=1 cargo test --release -p ethos-doc-core validator_stays
```

It validates 100,000 elements, a tenth of the frozen limit. Cost is linear, so that is
representative while staying fast enough to run on demand.

Peak RSS is not asserted in-process; measuring it portably would cost more than it proves. It is
recorded here and re-measured on any change to the strict parser.

## Outstanding

None. §12's resource and performance evidence requirement is met.
