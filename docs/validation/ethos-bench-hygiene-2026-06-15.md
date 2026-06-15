# ethos-bench Hygiene Check - 2026-06-15

## Purpose

Record the public-release checklist check that the sibling `ethos-bench` repository has the
required public repository hygiene files and clearly owns generated Gate Zero evidence.

## Subject

- Repository: sibling checkout `../ethos-bench`
- Checked commit: `14506e5 Add public project policy docs`
- Worktree status before checks: clean

## Files Verified

Required public hygiene files are present:

- `SECURITY.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `README.md`

The `README.md` states that `ethos-bench` is the standalone benchmark harness for Ethos
parser-core evidence and records benchmark contracts, runnable harnesses, result JSON, and tests.

`CONTRIBUTING.md` states that `ethos-bench` owns benchmark orchestration and generated benchmark
evidence for Ethos, and that generated Gate Zero evidence belongs under
`benchmarks/results/gate-zero/`.

`SECURITY.md` states that generated benchmark result JSON and evidence bundles must not be
hand-edited and that configured parser commands, artifacts, input PDFs, and result files should
be treated as potentially hostile unless pinned.

## Verification Commands

```sh
make test
make smoke
```

Results:

```text
make test
Ran 13 tests in 2.750s
OK

make smoke
completed CLI help smoke checks for ethos_bench, readiness, g1, g2, g3, and summarize
```

Worktree status after checks: clean.

## Result

The `ethos-bench` public hygiene gate is complete for the current repository state. Public
benchmark claims still require public-safe, signed or otherwise integrity-bound G1/G2/G3 evidence
and a claim audit.
