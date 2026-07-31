# v0.6.0 DocuShell Consumer Acceptance

Status: **accepted and bound to a reviewed DocuShell commit** (2026-07-31).

Covers release-prep §9.4. This is a consumer acceptance test, not authorization to change
DocuShell in the Ethos release.

## Bound commits

| Repository | Commit | State |
| --- | --- | --- |
| DocuShell | `cc652ec71cc11a330e5c2843f0cc1645bf5cc10b` | reviewed, fast-forward merged to `main`, pushed to `origin/main` |
| Ethos | this branch | — |

The DocuShell commit was reviewed by the decider and merged with `--ff-only`, so the reviewed SHA
and the SHA on `main` are identical. §9.4's exact-commit requirement is satisfied.

DocuShell's existing pinned consumer state, unchanged by this work:

```text
ethos CLI      0.5.0  linux:x64  binary sha256 7b6b7cb03c1d16183b6cdd56f6d2ebe593a25ef257baa5b6553a0055c53e8f44
release asset  ethos-linux-x64.tar.gz  sha256 592b175c00d147625f2f2ccc8bc5c74fb8a00ee37f178c363757f2c72404876e
PDFium         chromium/7881, caller-provided per ADR-0013
```

Both hashes match `packages/npm/ethos-pdf/vendor/manifest.json` exactly.

## Scope: shadow lane, not migration

DocuShell had no Grounding JSON anywhere before this. Its production verification lane calls
`ethos verify --grounding opendataloader-json` from
`services/parse-pdf/src/lib/ethosVerification.js`, using `spawn` with an argument array and never
a shell, treating exits `0` and `1` as reports and bounding diagnostics.

§9.2 says v0.6.0 does not justify rewriting a working consumer, so that lane is **untouched**.
§9.4 permits a bounded acceptance mapper *or* shadow fixture; this is the shadow fixture. Nothing
in it runs inside a parse job.

## §9.4 criteria

| Criterion | Evidence |
| --- | --- |
| Only public Ethos surfaces used | CLI `grounding check` and `verify` only; no Ethos source imported |
| Mapper byte-identical across two runs | asserted directly |
| Source hash preserved honestly | `source.sha256` from the source-bound page record |
| Producer preserved honestly | `docushell-parse-pdf-shadow`, an unauthenticated declaration |
| Capabilities preserved honestly | all three `false`; report shows `missing_spans` and `capability_limited` |
| IDs and order preserved honestly | `block-1`, `block-2` from OpenDataLoader ids, emitted order, no sorting |
| Geometry preserved honestly | bottom-left points → top-left centipoints, half away from zero; every box inside its page with positive area |
| Invalid grounding fails before indexing | out-of-page box → exit `2`, `invalid_bbox` at `/elements/0/bbox` |
| Report stored without semantic relabelling | report asserted verbatim; no `verified` or `truth` key added |
| `grounded` not presented as source truth | capability downgrades asserted present in the stored report |
| DocuShell fields absent from the Ethos schema | tenant, case, workflow, billing, review, retention, job id all asserted absent; top-level keys asserted exactly the eight `ethos.grounding.v1` fields |
| Removing DocuShell leaves artifacts usable | mapper output is a plain `ethos.grounding.v1` file; `grounding check` and `verify` operate on it with no DocuShell code present |

Seven tests, all passing:
`tests/parse-pdf/ethos-grounding-shadow.test.js`, registered in `tests/.mocharc.yaml`.

## Fingerprint handling

Citations carry `representation_sha256` read from the `grounding check` report, not
`source.sha256`. Using the PDF hash would report `stale` against a correct artifact. This exercises
the accepted fingerprint identity from ADR-0016 end to end in a real consumer.

## Fixtures

The pinned OpenDataLoader 2.5.0 output and its source-bound page geometry from the WP-0
feasibility record, copied into DocuShell so the lane reproduces without running the vendor JAR.
Ethos CLI steps skip unless `ETHOS_CLI_PATH` is set, keeping the suite runnable without a binary.

## Test execution

Without `ETHOS_CLI_PATH`, the four pure-mapper tests run and the three CLI-backed tests skip, so
DocuShell CI stays green on runners without an Ethos binary. With the CLI supplied, all seven run.
Both modes were exercised before merge.

## Outstanding

None for §9.4. One optional improvement: DocuShell's parse-pdf image already installs the CLI at
`/opt/ethos/bin/ethos`, so exporting `ETHOS_CLI_PATH` in that image's test stage would move the
three CLI-backed assertions from skipped to executed in CI. Not a release blocker.
