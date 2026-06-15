# Public Release Checklist

This checklist blocks any public GitHub push, public package publish, public benchmark report,
or launch announcement. It is intentionally stricter than the day-to-day engineering gates.

## Current Status

Ethos is not package-release, artifact-release, benchmark-report, or launch-announcement ready.
It may be pushed as a public pre-alpha source repository only if the latest public-source
preflight passes and the current claim language is used. The package-name/trademark gate is
closed by ADR-0006, but public benchmark, parser-quality, table, heading, speed, footprint, and
rendered-crop byte-identity claims remain blocked.

## Required Before Public Push

- Package-name and trademark decision is closed by accepted ADR-0006 in
  `docs/decisions/ADR-0006-package-identifiers.md`.
- README, docs, examples, and benchmark summaries pass a claim-language scan. Current scan:
  `docs/validation/claim-language-scan-2026-06-15.md`; rerun before public push if public-facing
  text or generated evidence changes.
- No generated evidence file in the public tree exposes private usernames, local machine names,
  private hostnames, or one-off absolute paths. Current scan:
  `docs/validation/public-evidence-scan-2026-06-15.md`; rerun before public push if benchmark
  outputs, validation records, fixture baselines, or reproduction sidecars change.
- Historical benchmark evidence is either regenerated through `ethos-bench` with public-safe
  reproduction metadata or kept out of public release artifacts.
- `ethos-bench` has its own public repository hygiene files: `SECURITY.md`, `CONTRIBUTING.md`,
  and `CODE_OF_CONDUCT.md`. Current check:
  `docs/validation/ethos-bench-hygiene-2026-06-15.md`.
- Gate Zero public result files are signed or otherwise integrity-bound by the accepted release
  process; unsigned local snapshots stay internal.
- Source license metadata, NOTICE boundaries, and non-advisory `cargo-deny` policy checks pass
  the current check: `docs/validation/license-notice-check-2026-06-15.md`. Release artifacts
  still need generated third-party license/NOTICE manifests and an advisory scan with a
  compatible `cargo-deny`/Rust toolchain before public release.
- Current public-source preflight:
  `docs/validation/public-source-push-preflight-2026-06-15.md`.

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
