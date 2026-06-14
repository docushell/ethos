# Gate Zero Results

Generated Gate Zero result files and evidence bundles now belong in the sibling
`ethos-bench` repository. This `ethos` directory is only a pointer kept for repository-boundary
clarity.

Platform-scoped Gate Zero results are produced and stored in `ethos-bench` as:

```text
<platform>/{g1,g2,g3}.json
```

G2/G3 result files must cite the active gate definition hash from:

```text
benchmarks/gate-zero/gates.json
```

G3 is a cross-platform gate. Platform-local G3 evidence is not sufficient for a pass decision
until the required `macos-arm64` and `linux-x64` comparisons show zero stable-payload-projection
and fingerprint divergences.

Publishable evidence sidecars are generated from saved result JSON and land under:

```text
<platform>/evidence/<gate>/<timestamp>/
```

Each evidence bundle contains the raw result archive, reproduction command, reproduction
environment sidecar, host attestation, human-readable summary, checksum manifest, and
checksum-manifest digest. The digest is not a public-key signature.

`reproduction-env.json` records the resolved benchmark environment variables when available.
If local artifact paths are unavailable, the sidecar must say so explicitly with `status:
incomplete` and blocker messages.

Diagnostic investigations that are not Gate Zero pass/fail results land in `ethos-bench` under:

```text
diagnostics/<topic>/
```

These files may explain a failure mode or candidate policy, but they are not publishable benchmark
claims and do not change G1/G2/G3 status by themselves.

Do not commit generated Gate Zero outputs to this repository. Use `ethos-bench` for generated
benchmark evidence and keep implementation-facing corpus, fixtures, schemas, and diagnostics code
in `ethos`.
