# Contributing to Ethos

## DCO — required on every commit

Ethos uses the [Developer Certificate of Origin](https://developercertificate.org/) (no CLA).
Every commit must carry a `Signed-off-by:` line matching the author (`git commit -s`). CI
rejects unsigned commits.

## Ground rules (enforced in review and CI)

1. **Fixtures before heuristics.** Any PR that adds or changes a heuristic ships its fixtures
   in the same PR. Reviewers reject otherwise. See `fixtures/README.md`.
2. **Contracts change by labeled PR only.** Schemas, the c14n spec, error/warning codes, and
   the deterministic profile change only via PRs labeled `contract-change` with a version bump
   and downstream sign-off. Output-changing heuristics are semver events with CHANGELOG entries.
3. **Determinism failures are never retried into green.** A flaky fingerprint IS the bug.
4. **No network in base crates.** No `std::net`, no network-capable dependencies (`reqwest`,
   `hyper`, `ureq`, `curl`, …) in base crates. Three CI layers enforce this; don't fight them.
5. **License allowlist.** Base dependencies: Apache-2.0, MIT, BSD-2/3, ISC, Zlib,
   Unicode-DFS-2016, CC0-1.0, MPL-2.0. Copyleft/source-available/custom-condition: denied
   (ADR-0004). Exceptions require an ADR before merge.
6. **Claims discipline.** No "#1", no superlatives, no speed/quality claims anywhere in docs
   or announcements without a reproducible benchmark behind them. CI greps for banned phrases.
7. **No OCR/VLM/ML dependencies in base.** Optional enrichment lives behind non-default
   features or separate packages.
8. **`ethos-verify` stays parser-agnostic.** It compiles against the `GroundingSource` trait
   module alone — never against parser internals. CI proves it.

## Branch discipline

One branch per lane: `ws/<lane>-<milestone>` (e.g. `ws/contracts-a`), merged via PR only.
Every PR must pass: schema validation, fixture suite, same-platform double-parse byte-diff,
clippy/fmt/deny, c14n property tests, and the rules above.

## Local checks

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo deny check
cargo test --workspace
python3 schemas/validate_examples.py     # schema/example validation
```

## Good first contributions

Fixture contributions are the best entry point — see `fixtures/README.md`. Issues labeled
`good-first-issue` are maintained as part of the monthly community funnel review.
