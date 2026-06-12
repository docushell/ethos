# Gate Zero Results

Platform-scoped Gate Zero results land here as:

```text
<platform>/{g1,g2,g3}.json
```

G2/G3 result files must cite the active gate definition hash from:

```text
benchmarks/gate-zero/gates.json
```

G3 is a cross-platform gate. Platform-local G3 evidence is not sufficient for a pass decision
until the required `macos-arm64` and `linux-x64` comparisons show zero canonical-payload and
fingerprint divergences.

Publishable evidence sidecars are generated from saved result JSON and land under:

```text
<platform>/evidence/<gate>/<timestamp>/
```

Each evidence bundle contains the raw result archive, reproduction command, host attestation,
human-readable summary, checksum manifest, and checksum-manifest digest. The digest is not a
public-key signature.
