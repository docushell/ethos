# Contributing to Ethos

Thanks for being here. Ethos is open source (Apache-2.0) and contributions are welcome — code,
fixtures, docs, adapters, bug reports, and design ideas all count. This page is the entire
process, from first idea to shipped release. There is no other process document you need to read.

## The whole process at a glance

```
idea ──► GitHub Discussion or issue ──► PR ──► CI green + one review ──► merge ──► next release train
```

Three human gates exist in the entire pipeline — everything else is automated CI:

1. **PR review** — one maintainer approval.
2. **Registry publish** — a human runs `cargo publish` / `npm publish` / PyPI upload.
3. **Public claims** — changes to README claim strings need maintainer sign-off (honesty gate).

Nothing waits on anything else. If CI is green and a reviewer approves, it merges.

## Your first contribution in five steps

```bash
# 1. Fork and clone, then build (Rust 1.87+, see rust-toolchain.toml)
cargo build --locked --workspace

# 2. Run the tests
cargo test --locked --workspace
make verify-alpha            # the golden-path demo suite

# 3. Make your change on any descriptively named branch
# 4. Add one line to CHANGELOG.md under "## Unreleased"
# 5. Commit with sign-off and open a PR
git commit -s -m "fix: ..."
```

A PR needs exactly three things: **tests pass**, **a CHANGELOG line**, and **DCO sign-off**
(`git commit -s` — we use the [Developer Certificate of Origin](https://developercertificate.org/),
no CLA). CI checks everything else automatically and tells you what to fix.

Good entry points: fixture contributions (`fixtures/README.md`), issues labeled
`good-first-issue`, framework adapters (`adapters/`), and docs fixes. If you're an AI agent,
read `AGENTS.md` and work only from the explicitly scoped issue, PR, or decider request.

## Ideas and design changes

Open a GitHub Discussion or issue first for anything user-visible — a quick "here's what I want
to do, here's why" is enough. Small fixes can go straight to PR. Architecture-level decisions
get a short ADR in `docs/decisions/` (copy an existing one; they're one page).

## Project invariants (CI enforces these — you don't need to memorize them)

| Invariant | What it means for your PR |
| --- | --- |
| Determinism is a contract | Same input + pinned profile ⇒ byte-identical output. New artifacts need a double-run byte-diff test. A flaky fingerprint is the bug — never retry into green. |
| Fixtures before heuristics | A PR that adds/changes a heuristic ships its fixtures in the same PR. |
| Fail closed | Missing capability ⇒ explicit warning/downgrade, never a silent pass. |
| Contracts change by labeled PR | Schemas, c14n spec, error codes, deterministic profile: label the PR `contract-change` + version bump. |
| No network in base crates | No `std::net` or network deps in base crates; CI enforces. |
| License allowlist | Apache-2.0, MIT, BSD-2/3, ISC, Zlib, Unicode-DFS-2016, CC0-1.0, MPL-2.0. No copyleft (ADR-0004). |
| Claims discipline | No superlatives or unearned speed/quality claims anywhere; CI greps for them. Numbers require a reproducible benchmark. |
| Parser-agnostic verify | `ethos-verify` compiles against `GroundingSource` only, never parser internals; CI proves it. |
| No OCR/ML in base | Optional enrichment lives behind non-default features or separate packages. |

Local pre-flight (optional — CI runs all of it anyway):

```bash
cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings
cargo deny check
python3 schemas/validate_examples.py && python3 fixtures/validate_fixtures.py
```

## How a release ships (maintainer side)

Releases follow `docs/release-lane-v2.md`: a release train is one version across all surfaces,
and it produces exactly **two documents** — one prep doc (scope + gate checklist) and one
closeout record (versions, hashes, evidence). When the checklist is green, a maintainer bumps
the version, tags, publishes to crates.io/PyPI/npm/GitHub Releases, and writes the closeout.
No approval queues, no waiting. First-of-class surfaces (first hosted service, first bundled
PDFium, first Windows artifact, breaking report-schema changes) get extra review because they
change what users can rely on — everything else rides the routine train.

Your merged PR ships in the next train; the CHANGELOG line you wrote becomes the release note.

## Community

- Questions and design ideas: GitHub Discussions.
- Bugs and parser failures: issues (templates provided). Security: `SECURITY.md` (private).
- Response target: median first maintainer response under 48 hours.
- Code of conduct: `CODE_OF_CONDUCT.md`. Roles and decision-making: `GOVERNANCE.md`.

## Commit sign-off hook

Every commit needs a `Signed-off-by` trailer (ADR-0004), and CI enforces it across the
full PR range. Install the local guard once:

```bash
cp scripts/hooks/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
```

It rejects a missing sign-off and a sign-off stranded outside the trailer block by a
blank line. Git only parses trailers in the final paragraph, so keep `Signed-off-by`
and any `Co-Authored-By` adjacent with no blank line between them.
