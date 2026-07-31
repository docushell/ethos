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
all structurally valid.

**Two capability shapes are measured, because they cost differently.** Shape A is `capabilities`
all `false` — the cheapest artifact, and the only one the original 2026-07-31 measurement covered.
Shape B declares `spans: true, char_offsets: true`, which is what the mapper guide encourages and
what reaches the span→element cross-reference. Shape B carries one span per element, each span
referencing an element, so span count tracks element count.

## Measurements — shape A (`capabilities` all `false`)

| Artifact | Elements | Input | Wall | Peak RSS | RSS ÷ input |
| --- | --- | --- | --- | --- | --- |
| small | 10 | 3 KB | 30 ms | 1 MB | — |
| medium | 10,000 | 1.5 MB | 150 ms | 14 MB | 9.3× |
| large | 100,000 | 14.8 MB | 1.85 s | 138 MB | 9.3× |
| **frozen element ceiling** | **1,000,000** | **151 MB** | **26.5 s** | **1.29 GB** | 8.5× |
| near input limit | 1,000,000 | 203 MiB | 26.9 s | 1.42 GB | 6.0× |
| over input limit | 1,000,000 | 277 MiB | 0.0 s | 1 MB | rejected |

Per element at the ceiling: **26.5 µs wall, 1.29 KB peak RSS**.

## Measurements — shape B (`spans` + `char_offsets`)

Re-measured after the O(spans × elements) scan in `validate` was replaced with a hashed index.
Before that change this shape was quadratic: a 15 MB artifact took 128.8 s and 20,000 elements
cost 443 µs/element, 11× over the accepted wall-clock ceiling.

| Artifact | Elements + spans | Input | Wall | Peak RSS |
| --- | --- | --- | --- | --- |
| medium | 10,000 | 2.3 MB | 0.13 s | 28 MB |
| large | 100,000 | 23.5 MB | 1.22 s | 270 MB |
| **frozen element ceiling** | **1,000,000** | **227 MiB** | **13.0 s** | **2.66 GB** |

Per element at the ceiling: **13.0 µs wall, 2.66 KB peak RSS**.

Shape B is *faster* per element than shape A because the indexed lookups replaced work that shape
A never did, but it holds roughly twice the resident set: the artifact carries a span record per
element as well as the element itself.

## Three findings

**1. Wall clock scales with record count, not bytes.** Holding elements at 1,000,000 and raising
input 34% (151 MB → 203 MiB) changed wall clock 1.5%. Record count is the cost driver, so a
per-element ceiling is the meaningful shape — but "records" means elements *and* spans, not
elements alone. The original wording ("element count, not bytes") was measured only on shape A,
which has no spans, and it does not generalize: cost is linear in each of them separately only
because the cross-reference between them is now indexed.

**2. Peak RSS runs 6–9× input size.** The validator retains the parsed artifact rather than
streaming it. The 256 MiB input limit therefore does **not** bound memory to a comparable figure: a
schema-legal artifact just under that limit reached 1.42 GB resident.

**3. The input limit fails closed and fails cheaply.** A 277 MiB artifact was rejected in 0.0 s at
1 MB RSS with exit `7` (`FileTooLarge`), before any parse work. Oversized input cannot be used to
exhaust memory.

## Operational consequence worth deciding on

**A schema-legal artifact can require roughly 2.7 GB resident.** Wall clock at the ceiling is now
13–27 s depending on shape.

Release-prep §9.2 has DocuShell running the verifier in a bounded worker. A worker capped below
about **3 GB** will be killed by a legal artifact rather than rejecting it, which converts a
resource limit into an opaque crash. That is an integration property, not an Ethos defect, but it
should be stated rather than discovered.

The earlier 1.5 GB figure came from shape A alone and understates a spans-bearing artifact by
roughly 2×. Anything sized against it — including the sizing table in
`docs/writing-a-mapper.md` — must use the shape B numbers.

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

**Wall clock: holds on both shapes.** 26.5 µs/element (shape A) and 13.0 µs/element (shape B),
against the 40 µs ceiling.

**Peak RSS: holds on shape A, exceeded on shape B.** 1.29 KB/element against the 2 KB ceiling for
shape A; **2.66 KB/element for shape B, which is 33% over.** The ceiling was set from shape A
measurements and no spans-bearing artifact was measured before it was accepted. See Outstanding.

Wall clock is enforced by two tests in `crates/ethos-core/src/grounding_json.rs` —
`validator_stays_within_the_accepted_resource_ceiling` (shape A) and
`ceiling_holds_when_the_mapper_declares_spans_and_char_offsets` (shape B). Both are release-only,
because a debug build runs about an order of magnitude slower than the profile the ceiling
describes, and both are opt-in through `ETHOS_CHECK_VALIDATOR_CEILING` because wall-clock
assertions flake on shared CI runners. Run both with:

```sh
make validator-ceiling-check
```

CI runs that target in the `test` job, so a superlinear regression fails the build rather than
merging green. Each test validates 100,000 and 20,000 records respectively, well below the frozen
limit; cost is linear in elements and in spans once the cross-reference is indexed, so those are
representative while staying fast enough to run on every PR.

Peak RSS is not asserted in-process; measuring it portably would cost more than it proves. It is
recorded here and re-measured on any change to the strict parser.

## Outstanding

**The 2 KB/element peak-RSS ceiling is exceeded by shape B (2.66 KB/element, 33% over).** The
ceiling was accepted on 2026-07-31 from shape A measurements only; no spans-bearing artifact was
measured before acceptance. The wall-clock half of the ceiling holds on both shapes.

This needs a decision, not a silent re-baseline. The options are to raise the RSS ceiling to
roughly 3 KB/element with the shape B evidence above, or to treat 2 KB as binding and reduce the
working set, which means the streaming or two-pass validation already recorded as a v0.7.0 input.
Raising a ceiling to match what the code does is only legitimate when the number was never
measured against the relevant shape — which is the case here, but it should be recorded as a
deliberate revision rather than absorbed.

Until that decision lands, `docs/writing-a-mapper.md` §9 publishes the shape B numbers so
integrators size workers against the larger figure.

§12's resource and performance evidence requirement is otherwise met.
