# Gate Zero Results

Platform-scoped Gate Zero results land here as:

```text
<platform>/{g1,g2,g3}.json
```

Publishable evidence sidecars are generated from saved result JSON and land under:

```text
<platform>/evidence/<gate>/<timestamp>/
```

Each evidence bundle contains the raw result archive, reproduction command, host attestation,
human-readable summary, checksum manifest, and checksum-manifest digest. The digest is not a
public-key signature.
