# Benchmark Ownership

Ethos benchmark work is split across two repositories.

## `ethos`

This repository owns implementation-adjacent benchmark inputs and historical evidence:

- parser, verification, schema, profile, and fixture code
- synthetic and public-domain corpus fixtures used by tests and Gate Zero
- internal diagnostics and generated evidence needed to debug parser behavior
- validation records that affect product claims or determinism boundaries

Generated Gate Zero benchmark results are not checked into `ethos`; they belong in
`ethos-bench`. Public wording must continue to point readers at `docs/execution-status.md` for
the current pre-alpha status and blockers.

Before any public repository push, run the public-release checklist in
`docs/public-release-checklist.md`. Historical generated evidence may contain local reproduction
paths; do not edit those files by hand. Regenerate public-safe evidence through the accepted
benchmark flow in `ethos-bench` or keep the snapshots internal.

## `ethos-bench`

The sibling repository at `../ethos-bench` owns public benchmark orchestration:

- the standalone Python harness package
- G1/G2/G3 runner commands
- gate evaluator tests
- competitor execution wiring and pinned artifact checks
- generated result and evidence layout under `benchmarks/results/gate-zero/`

`ethos-bench` runs against an Ethos checkout through `--ethos-repo`; it should not duplicate
the Ethos source tree or rewrite Ethos parser behavior.

## Claim Rule

No public performance, footprint, quality, table, heading, or parser-speed superlative claim is
allowed from either repository until signed G1/G2/G3 result files exist for the required hosts
and the claim audit says the wording is supported.

Allowed current wording:

```text
Ethos is pre-alpha. The benchmark harness and contracts exist, but public benchmark claims remain blocked.
```

Not allowed current wording:

```text
parser speed superlatives
production-readiness claims for table extraction
production-readiness claims for heading extraction
cross-platform rendered-crop byte-identity claims
```

## Update Flow

1. Change parser, verification, fixtures, profiles, or schemas in `ethos`.
2. Change benchmark orchestration, metric evaluation, or result summarization in `ethos-bench`.
3. Run the relevant local test suite in each touched repository.
4. Record cross-host or claim-affecting evidence in `ethos/docs/validation/` or in signed
   `ethos-bench/benchmarks/results/gate-zero/` files, depending on whether the evidence is a
   product-boundary validation or a benchmark result.
