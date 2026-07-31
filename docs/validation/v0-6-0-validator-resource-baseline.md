# v0.6.0 Grounding JSON Validator Resource Baseline

Status: **measured through the frozen ceiling; numeric ceiling awaiting the decider**
(2026-07-31).

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

Three responses, in preference order:

1. **Document the working set** and keep the frozen limits. Consumers size workers from a published
   figure. No schema change, no breaking change to ADR-0016.
2. **Lower the element ceiling** so peak RSS lands under a few hundred MB. This changes a frozen
   ADR limit and is a compatibility decision, not a tuning one.
3. **Add a validator memory guard** that fails with the existing `MemoryLimitExceeded` (exit `11`)
   instead of letting the host OOM-kill. New work; belongs in v0.7.0 with streaming validation.

Recommendation: option 1 for v0.6.0, with the figure in `docs/writing-a-mapper.md` limits section,
and option 3 logged as a v0.7.0 input.

## Suggested ceiling

Replace the §12 v0.5.0 regression comparison with a bounded per-element resource test on the new
validator. Measured values with roughly 1.5× headroom:

- **40 µs per element wall clock**, release profile
- **2 KB per element peak RSS**

At the frozen 1,000,000-element ceiling that permits 40 s and 2 GB. Set on measurement, not
aspiration, and re-measured on any change to the strict parser.

## Outstanding

Decider sets the numeric ceiling and picks among the three responses above. The extrapolation gap
flagged in the previous revision of this record is now closed by direct measurement.
