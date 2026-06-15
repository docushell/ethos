# Public Source Push Preflight - 2026-06-15

## Purpose

Record the final preflight for making the Ethos source repository public on GitHub.

This record applies only to a **pre-alpha source push**. It does not approve package publication,
GitHub releases, binaries, wheels, npm updates, public benchmark reports, launch announcements, or
production-readiness claims.

## Status

Status: **pass for public pre-alpha source push, with artifact and claim restrictions**.

Allowed public positioning remains:

```text
Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
native Ethos JSON and supported foreign parser outputs.
```

## Subject

- Repository: `docushell/ethos`
- Starting HEAD before this preflight record: `5494169 Add release hygiene check`
- Scope: tracked source tree and human-written validation records
- Excluded: ignored local generated files, package publication, release artifacts, benchmark
  reports, binary artifacts, registry updates, and launch copy

## Commands

```sh
git status --short
python3 .github/scripts/readiness_gate.py public
python3 .github/scripts/claims_gate.py
make release-hygiene CARGO_DENY=<tmp-tools>/bin/cargo-deny
git ls-files benchmarks/results
git check-ignore -v benchmarks/results/fixtures/baseline.json
git ls-files | rg '(^|/)(g1|g2|g3)\.json$|gate-zero.*\.json$|benchmark.*result.*\.json$|diagnostics/.*\.json$'
git ls-files -z | xargs -0 rg -n '<private-user-or-host-pattern>|/Users/|/scratch/|/private/tmp|/private/var'
git ls-files -z | xargs -0 rg -n 'fastest|production[- ]grade|truth checker|truth-checker|10x|public benchmark winner|cross-platform bit-identical rendered crops'
git diff --check
```

## Results

```text
git status --short
clean before this preflight record was written

python3 .github/scripts/readiness_gate.py public
public readiness: green

python3 .github/scripts/claims_gate.py
claims gate green

make release-hygiene CARGO_DENY=<tmp-tools>/bin/cargo-deny
pass; cargo-deny reported warnings only, then `bans ok, licenses ok, sources ok`

git ls-files benchmarks/results
benchmarks/results/fixtures/README.md
benchmarks/results/gate-zero/README.md

git check-ignore -v benchmarks/results/fixtures/baseline.json
.gitignore excludes benchmarks/results/fixtures/*.json
```

Tracked generated-result scan:

```text
Only schema/manifest files matched the result-shaped filename pattern:
benchmarks/gate-zero/g2-result.schema.json
benchmarks/gate-zero/g3-result.schema.json
benchmarks/gate-zero/gates.json
benchmarks/gate-zero/gates.schema.json
benchmarks/gate-zero/manifest.json
benchmarks/gate-zero/reproduction-env.schema.json
benchmarks/gate-zero/result.schema.json
```

Tracked private path / hostname scan:

```text
No tracked private usernames, private hostnames, workstation paths, or one-off absolute paths
matched after normalizing the temporary cargo-deny path in the license validation record.
```

Tracked claim scan:

```text
Matches are intentional guardrails, tests, or validation records that prohibit unsupported claims.
No marketing surface claims Ethos is fastest, production-grade for tables/headings, a truth
checker, a public benchmark winner, or cross-platform bit-identical for rendered crops.
```

## Remaining Blockers Outside This Source Push

- Package publishing remains blocked until package-specific release work is complete.
- GitHub releases, binaries, wheels, npm updates, and other artifacts remain blocked until
  third-party license/NOTICE manifests are generated and attached.
- The advisory portion of `cargo-deny` remains blocked locally by the Rust 1.87 / cargo-deny
  compatibility issue recorded in `license-notice-check-2026-06-15.md`; run it in a compatible
  Rust 1.88+ toolchain before release artifacts.
- Public benchmark reports remain blocked until `ethos-bench` owns public-safe, signed or
  otherwise integrity-bound G1/G2/G3 evidence.
- Speed, footprint, parser-quality, production-grade table/heading, semantic truth, and
  cross-platform rendered-crop byte-identity claims remain blocked.

## Result

The repository is ready for a public GitHub **source-only pre-alpha push** under the current claim
language. It is not ready for public releases, package publication, benchmark publication, or
launch claims.
