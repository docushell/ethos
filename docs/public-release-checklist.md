# Public Release Checklist

This checklist blocks any public GitHub push, public package publish, public benchmark report,
or launch announcement. It is intentionally stricter than the day-to-day engineering gates.

## Current Status

Ethos is not public-release ready. It is pre-alpha and may be shared privately with the current
claim language. The package-name/trademark gate is closed by ADR-0006, but public benchmark,
parser-quality, table, heading, speed, footprint, and rendered-crop byte-identity claims remain
blocked.

## Required Before Public Push

- Package-name and trademark decision is closed by accepted ADR-0006 in
  `docs/decisions/ADR-0006-package-identifiers.md`.
- README, docs, examples, and benchmark summaries pass a claim-language scan.
- No generated evidence file in the public tree exposes private usernames, local machine names,
  private hostnames, or one-off absolute paths.
- Historical benchmark evidence is either regenerated through `ethos-bench` with public-safe
  reproduction metadata or kept out of public release artifacts.
- `ethos-bench` has its own public repository hygiene files: `SECURITY.md`, `CONTRIBUTING.md`,
  and `CODE_OF_CONDUCT.md`.
- Gate Zero public result files are signed or otherwise integrity-bound by the accepted release
  process; unsigned local snapshots stay internal.
- Release artifacts include third-party license and NOTICE material.

## Claim Rules

Allowed until the checklist is complete:

```text
Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
native Ethos JSON and supported foreign parser outputs.
```

Not allowed:

```text
parser speed superlatives
table-extraction release-readiness claims
heading-extraction release-readiness claims
semantic truth checking
cross-platform bit-identical rendered crops
public benchmark winner
```

## Evidence Handling

Do not hand-edit generated benchmark result JSON to make it public-safe. Regenerate it with
public-safe paths and host metadata, or keep it internal. Human-written validation records may
replace local paths with role-based placeholders as long as hashes, commit ids, outcomes, and
failure conclusions are preserved.
