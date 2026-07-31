# v0.6.0 Grounding JSON Validator Resource Baseline

Status: **measurements recorded; ceiling not yet set by the decider** (2026-07-31).

Release-prep §12 asks for resource and performance evidence showing no unacceptable regression
against the frozen v0.5.0 verification baseline, with a numeric ceiling set before implementation
freeze.

## Why this measures something different

A regression comparison against v0.5.0 verification would measure nothing. Grounding JSON adds a
parallel loader in front of the existing `GroundingSource` boundary; no existing verification code
path changes, which the unchanged native and OpenDataLoader goldens already demonstrate.

The meaningful question is what the **new** validator costs at the limits ADR-0016 froze. These
numbers answer that, and the decider can set a ceiling above them.

## Method

`target/release/ethos grounding check <artifact> --out <report>` on `darwin:x64`, release profile,
three warm runs after one discarded cold run. Wall clock and peak RSS from `/usr/bin/time -l`.

Synthetic artifacts, all structurally valid, capabilities all `false`:

| Name | Pages | Elements | On-disk |
| --- | --- | --- | --- |
| small | 1 | 10 | 3 KB |
| medium | 100 | 10,000 | 1.5 MB |
| large | 1,000 | 100,000 | 14.8 MB |

## Measurements

| Artifact | Run 1 | Run 2 | Run 3 | Peak RSS |
| --- | --- | --- | --- | --- |
| small | 30 ms | 30 ms | 30 ms | 1 MB |
| medium | 160 ms | 150 ms | 140 ms | 14 MB |
| large | 1920 ms | 1850 ms | 1800 ms | 138 MB |

Roughly linear in element count: about 18 µs and 1.4 KB of peak RSS per element. The `small` figure
is dominated by process start, not validation.

## Headroom against the frozen limits

ADR-0016 freezes 5,000 pages, 1,000,000 elements, and 256 MiB of input. The `large` artifact is
10% of the element ceiling. Linear extrapolation puts a limit-maximal artifact near 18 seconds and
1.4 GB peak RSS.

**That extrapolation is the decision-relevant number, and it has not been measured.** Peak RSS
scaling linearly to 1.4 GB deserves a check before the ceiling is set, since the validator retains
the parsed artifact rather than streaming it.

## Suggested ceiling

Replace the §12 v0.5.0 regression comparison with a bounded resource test on the new validator.
A defensible starting pair, both roughly 2× the measured `large` figures normalized per element:

- **40 µs per element wall clock**, measured on the release profile
- **3 KB per element peak RSS**

Set on measurement, not aspiration, and re-measured on any change to the strict parser.

## Outstanding

1. Decider sets the numeric ceiling.
2. Measure an artifact at the frozen element ceiling to confirm the linear extrapolation, or
   record a lower supported working set than the schema permits.
