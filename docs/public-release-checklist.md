# Public Release Checklist

This checklist blocks any public GitHub push, public package publish, public benchmark report,
or launch announcement. It is intentionally stricter than the day-to-day engineering gates.

## Current Status

Ethos has approved public beta/evaluation surfaces for the GitHub source repository, Rust library
crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`, the Python `ethos-pdf` wheel
at `0.1.2`, the npm `@docushell/ethos-pdf@0.1.2` package, GitHub Release `v0.1.2` macOS arm64 and
Linux x64 CLI artifacts, and the three approved annotated package tags. The approved patch `0.1.2`
evaluation surfaces are closed by
`docs/validation/patch-0-1-2-current-state-closeout-validation-2026-06-25.md`. Hosted surfaces,
production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds,
public benchmark reports, public benchmark claims, speed, footprint, parser-quality, table-quality,
`ethos-doc`, and `ethos-rag` remain blocked.

v0.2.0 release approval request is recorded in
`docs/validation/v0-2-0-release-approval-request-validation-2026-06-25.md` for decider review
only. It does not approve version bump, release-candidate branch creation, package publication,
tag creation, artifact publication, or installable `0.2.0` wording. The request keeps Python
public scope conditional on a PyPI wheel, matching `v0.2.0` CLI artifacts, and naming docs for
the historical `ethos-pdf` package. The request keeps npm scoped to a CLI binary distribution
decision, not a Node SDK/API claim.

v0.2.0 release approval decision is recorded in
`docs/validation/v0-2-0-release-approval-decision-validation-2026-06-25.md`. It accepts
release-candidate version activation on the current branch for Rust, Python, npm, `CHANGELOG.md`,
and release-candidate wording only. It does not approve package publication, tag creation,
artifact publication, installable `0.2.0` wording, hosted surfaces, production positioning,
Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`,
or public benchmark claims.

v0.2.0 version activation is recorded in
`docs/validation/v0-2-0-version-activation-validation-2026-06-25.md`. It moves Rust, Python, and
npm source/package metadata to `0.2.0` for release-candidate validation only. Public install
commands and installable wording remain on the approved `0.1.2` evaluation baseline until
publication, registry/artifact availability, smoke evidence, and wording closeout records pass.

v0.2.0 `ethos-doc-core` dry-run evidence is recorded in
`docs/validation/v0-2-0-ethos-doc-core-cargo-publish-dry-run-evidence-validation-2026-06-25.md`.
It records a passing `cargo publish --dry-run --locked -p ethos-doc-core` for
`ethos-doc-core 0.2.0`; no publication, tag, artifact upload, dependent-crate dry-run, or
installable `0.2.0` wording is approved by that record.

v0.2.0 package/build evidence is recorded in
`docs/validation/v0-2-0-package-build-evidence-validation-2026-06-25.md`. It records local package
build checks for the Python wheel, macOS arm64 draft CLI artifact, and npm package metadata. The
npm candidate remains blocked until v0.2.0 macOS arm64 and Linux x64 CLI artifacts both exist and
the vendored payload is refreshed from those artifacts; no publication, artifact upload, tag, or
installable `0.2.0` wording is approved by that record.

Patch `0.1.1` readiness prep is recorded in
`docs/validation/patch-0-1-1-readiness-prep-validation-2026-06-23.md` for review only. It records
candidate onboarding contents after `ethos doctor`, synthetic fixture golden-change guarding, the
2-minute PDF parse quickstart, and improved missing/unusable PDFium guidance landed on `main`. It
does not approve a release, tag, version bump, package publish, GitHub Release artifact, hosted
surface, production positioning, Windows packaged artifact, bundled project-maintained PDFium
build, public benchmark report, or public benchmark claim.

Patch `0.1.2` readiness prep is recorded in
`docs/validation/patch-0-1-2-readiness-prep-validation-2026-06-24.md` for review only. It records
the narrow beta patch candidate boundary after `ethos evidence anchor`, the `evidence_anchor` v1
guard, and professional public README status wording landed on `main`. It keeps the current public
install baseline at `0.1.1` and does not approve a release, tag, version bump, package publish,
GitHub Release artifact, hosted surface, production positioning, Windows packaged artifact,
bundled project-maintained PDFium build, public benchmark report, or public benchmark claim.

Patch `0.1.2` version activation is recorded in
`docs/validation/patch-0-1-2-version-activation-validation-2026-06-24.md` for candidate validation
only. It moves Rust workspace and Python source/package metadata to `0.1.2`, keeps npm and public
install wording on the published `0.1.1` baseline until matching CLI artifacts and publication
evidence exist, and does not approve a release, tag, package publish, GitHub Release artifact,
hosted surface, production positioning, Windows packaged artifact, bundled project-maintained
PDFium build, public benchmark report, or public benchmark claim.

Patch `0.1.2` artifact/package evidence is recorded in
`docs/validation/patch-0-1-2-artifact-package-evidence-validation-2026-06-24.md` for local
candidate validation only. It dynamically checks `0.1.2` Rust crate candidates and the
`ethos_pdf-0.1.2-py3-none-any.whl` candidate, and it updates draft CLI artifact workflow smoke
expectations to `ethos 0.1.2`. The public install baseline remains `0.1.1`, public installation
wording remains blocked, registry publication remains blocked, GitHub Release artifact publication
remains blocked, and npm vendor refresh remains blocked until separate approval, operator evidence,
and closeout records pass.

Patch `0.1.2` draft artifact evidence is recorded in
`docs/validation/patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md` for artifact
candidate validation only. The downloaded macOS arm64 and Linux x64 draft CLI artifact sidecars
smoke as `ethos 0.1.2`. The public install baseline remains `0.1.1`, GitHub Release artifact
publication remains blocked, registry publication remains blocked, npm vendor refresh remains
blocked, and public installation wording remains blocked until separate approval, operator
evidence, and closeout records pass.

Patch `0.1.2` artifact publication approval request is recorded in
`docs/validation/patch-0-1-2-artifact-publication-approval-request-validation-2026-06-24.md` for
decider review only. It binds the exact macOS arm64/Linux x64 CLI artifact names and SHA256 values
for possible GitHub Release publication, but publication remains blocked, the public install
baseline remains `0.1.1`, registry publication remains blocked, npm vendor refresh remains blocked,
and public installation wording remains blocked until a separate decision and operator evidence
pass.

Patch `0.1.2` artifact publication approval decision is recorded in
`docs/validation/patch-0-1-2-artifact-publication-approval-decision-validation-2026-06-24.md` for
later operator upload only. It accepts the exact macOS arm64/Linux x64 CLI artifact names and
SHA256 values for GitHub Release `v0.1.2`, but upload remains pending, the public install baseline
remains `0.1.1`, registry publication remains blocked, npm vendor refresh remains blocked, and
public installation wording remains blocked until post-upload closeout or separate approval records
pass.

Patch `0.1.2` artifact publication closeout is recorded in
`docs/validation/patch-0-1-2-artifact-publication-closeout-validation-2026-06-24.md`. GitHub
Release `v0.1.2` now contains the exact approved macOS arm64/Linux x64 CLI artifact assets and
bounded release wording, but the public install baseline remains `0.1.1`, registry publication
remains blocked, npm vendor refresh remains blocked, npm publication remains blocked, and public
installation wording remains blocked until separate lanes pass.

Patch `0.1.2` npm vendor refresh is recorded in
`docs/validation/patch-0-1-2-npm-vendor-refresh-validation-2026-06-24.md` for candidate validation
only. The checked-in `@docushell/ethos-pdf@0.1.2` vendor payload is refreshed from published
GitHub Release `v0.1.2` assets, but npm publication remains blocked, public installation wording
remains blocked, registry publication remains blocked, and the public install baseline remains
`0.1.1` until separate approval, operator, registry, and wording closeout lanes pass.

Patch `0.1.2` npm publication approval request is recorded in
`docs/validation/patch-0-1-2-npm-publication-approval-request-validation-2026-06-24.md` for decider
review only. It binds the exact `@docushell/ethos-pdf@0.1.2` npm candidate, toolchain-qualified
tarball hashes, durable vendor checksums, installed CLI smoke, and missing-PDFium behavior, but
`npm publish` remains blocked until a separate approval decision and operator action pass. Public
installation wording remains blocked.

Patch `0.1.2` npm publication approval decision is recorded in
`docs/validation/patch-0-1-2-npm-publication-approval-decision-validation-2026-06-24.md` for later
operator action only. It accepts the exact `@docushell/ethos-pdf@0.1.2` npm candidate and required
pre-publish checks, but does not run `npm publish`; registry closeout and public installation
wording remain blocked until separate operator evidence and closeout lanes pass.

Patch `0.1.2` npm publication blocker is recorded in
`docs/validation/patch-0-1-2-npm-publication-blocker-validation-2026-06-24.md`. The approved
`@docushell/ethos-pdf@0.1.2` publish attempt failed with npm `E404`, and registry checks still
show latest `0.1.1`; retry, registry closeout, and public installation wording remain blocked
pending npm account or `@docushell` scope permission resolution.

Patch `0.1.2` npm publication closeout is recorded in
`docs/validation/patch-0-1-2-npm-publication-closeout-validation-2026-06-24.md`. npm now reports
`@docushell/ethos-pdf@0.1.2` as the latest published package with matching shasum, integrity,
tarball URL, source commit, file count, and unpacked size. Public installation wording remains
blocked until a separate public wording closeout lane passes.

Patch `0.1.2` public install wording closeout is recorded in
`docs/validation/patch-0-1-2-public-install-wording-closeout-validation-2026-06-24.md`. Public
README and claim-inventory wording now point npm installation to `@docushell/ethos-pdf@0.1.2`
and GitHub Release CLI archives to `v0.1.2`. Rust crate installation remains at `0.1.1`, and
Python installation remains at `ethos-pdf==0.1.1` until separate crates.io/PyPI `0.1.2`
publication closeout records pass.

Patch `0.1.2` crates.io publication approval request is recorded in
`docs/validation/patch-0-1-2-crates-publication-approval-request-validation-2026-06-25.md` for
decider review only. It binds exact `0.1.2` candidate crates, artifact hashes, source binding,
package tag names, and requested later operator commands, but `cargo publish` remains blocked,
package tag creation remains blocked, Rust crate public installation wording remains blocked, PyPI
publication remains blocked, hosted surfaces remain blocked, production positioning remains
blocked, Windows packaged artifacts remain blocked, bundled project-maintained PDFium builds remain
blocked, `ethos-doc` remains blocked, `ethos-rag` remains blocked, and public benchmark claims
remain blocked.

Patch `0.1.2` crates.io publication approval decision is recorded in
`docs/validation/patch-0-1-2-crates-publication-approval-decision-validation-2026-06-25.md`.
It approves only bounded later operator execution for `ethos-doc-core`, `ethos-verify`, and
`ethos-pdf` at `0.1.2`. Actual crates.io publication remains a separate operator action, package
tag creation remains blocked until registry closeout, Rust crate public installation wording
remains blocked until registry availability closeout, PyPI publication remains blocked, hosted
surfaces remain blocked, production positioning remains blocked, Windows packaged artifacts remain
blocked, bundled project-maintained PDFium builds remain blocked, `ethos-doc` remains blocked,
`ethos-rag` remains blocked, and public benchmark claims remain blocked.

Patch `0.1.2` crates.io publication closeout is recorded in
`docs/validation/patch-0-1-2-crates-publication-closeout-validation-2026-06-25.md`. crates.io
reports `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`. Rust crate public
installation wording remains blocked until a separate wording and availability closeout, PyPI
publication remains blocked, hosted surfaces remain blocked, production positioning remains
blocked, Windows packaged artifacts remain blocked, bundled project-maintained PDFium builds remain
blocked, `ethos-doc` remains blocked, `ethos-rag` remains blocked, and public benchmark claims
remain blocked.

Patch `0.1.2` Rust public install wording closeout is recorded in
`docs/validation/patch-0-1-2-rust-public-install-wording-closeout-validation-2026-06-25.md`.
README and claim-inventory wording now point Rust crate installation to `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf` at `0.1.2`. PyPI publication remains blocked, hosted surfaces
remain blocked, production positioning remains blocked, Windows packaged artifacts remain blocked,
bundled project-maintained PDFium builds remain blocked, `ethos-doc` remains blocked, `ethos-rag`
remains blocked, and public benchmark claims remain blocked.

Patch `0.1.2` Python PyPI publication approval request is recorded in
`docs/validation/patch-0-1-2-python-publication-approval-request-validation-2026-06-25.md`. It
requests decider review for the exact deterministic `ethos-pdf==0.1.2` wheel candidate only. PyPI
upload remains blocked, Python public installation wording remains blocked, hosted surfaces remain
blocked, production positioning remains blocked, Windows packaged artifacts remain blocked, bundled
project-maintained PDFium builds remain blocked, `ethos-doc` remains blocked, `ethos-rag` remains
blocked, and public benchmark claims remain blocked.

Patch `0.1.2` Python PyPI publication approval decision is recorded in
`docs/validation/patch-0-1-2-python-publication-approval-decision-validation-2026-06-25.md`. It
accepts only later operator upload of the exact deterministic `ethos-pdf==0.1.2` wheel candidate.
Actual PyPI upload remains a separate operator action, Python public installation wording remains
blocked until PyPI availability closeout, package tag creation remains blocked, hosted surfaces
remain blocked, production positioning remains blocked, Windows packaged artifacts remain blocked,
bundled project-maintained PDFium builds remain blocked, `ethos-doc` remains blocked, `ethos-rag`
remains blocked, and public benchmark claims remain blocked.

Patch `0.1.2` Python PyPI publication closeout is recorded in
`docs/validation/patch-0-1-2-python-publication-closeout-validation-2026-06-25.md`. PyPI reports
`ethos-pdf==0.1.2` as the exact deterministic wheel approved for publication. Python public
installation wording remains blocked until a separate wording and availability closeout, package tag
creation remains blocked, hosted surfaces remain blocked, production positioning remains blocked,
Windows packaged artifacts remain blocked, bundled project-maintained PDFium builds remain blocked,
`ethos-doc` remains blocked, `ethos-rag` remains blocked, and public benchmark claims remain
blocked.

Patch `0.1.2` Python public install wording closeout is recorded in
`docs/validation/patch-0-1-2-python-public-install-wording-closeout-validation-2026-06-25.md`.
README, Python package docs, and claim-inventory wording now point Python installation to
`ethos-pdf==0.1.2`. Package tag creation remains blocked, hosted surfaces remain blocked,
production positioning remains blocked, Windows packaged artifacts remain blocked, bundled
project-maintained PDFium builds remain blocked, `ethos-doc` remains blocked, `ethos-rag` remains
blocked, and public benchmark claims remain blocked.

Patch `0.1.2` package tag approval request is recorded in
`docs/validation/patch-0-1-2-package-tag-approval-request-validation-2026-06-25.md`. It records the
exact package tag names, source commit, source tree, and requested later operator commands for
decider review only. Package tag creation remains blocked until a separate explicit approval
decision is recorded; hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, and public benchmark claims remain
blocked.

Patch `0.1.2` package tag approval decision is recorded in
`docs/validation/patch-0-1-2-package-tag-approval-decision-validation-2026-06-25.md`. It accepts
the exact package tag names, source commit, source tree, and later operator commands. Package tag
creation remains a separate operator action after this decision is merged and validation passes on
merged source; hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, and public benchmark claims remain
blocked.

Patch `0.1.2` package tag closeout is recorded in
`docs/validation/patch-0-1-2-package-tag-closeout-validation-2026-06-25.md`. Package tag creation
closeout is complete for the three approved annotated package tags, and remote `origin` tag refs
dereference to the approved package source commit. Hosted surfaces, production positioning, Windows
packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, and public
benchmark claims remain blocked.

Patch `0.1.2` current-state closeout is recorded in
`docs/validation/patch-0-1-2-current-state-closeout-validation-2026-06-25.md`. The approved patch
`0.1.2` evaluation surfaces are closed for the GitHub source repository, Rust crates, Python wheel,
npm package, macOS arm64/Linux x64 CLI artifacts, and annotated package tags. Hosted surfaces,
production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds,
`ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, speed, footprint,
parser-quality, table-quality, and production claims remain blocked.

v0.2.0 source preparation is tracked in `docs/v0-2-0-release-prep.md`,
`docs/v0-2-x-compatibility-policy.md`, and `docs/bring-your-own-parser.md`. This lane prepares
JSON verification and evidence anchoring over caller-provided source evidence, plus the Python
CLI-wrapper calls for `verify(...)` and `anchor(...)`. It does not approve `0.2.0` package
publication, package tags, GitHub Release artifacts, PyPI upload, public install wording, hosted
surfaces, production positioning, public benchmark claims, Windows packaged artifacts, or bundled
project-maintained PDFium.

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
  the current check: `docs/validation/license-notice-check-2026-06-15.md`. The full advisory
  scan passes for the current source tree in `docs/validation/advisory-scan-2026-06-16.md`.
  Cargo third-party manifest generation is recorded in
  `docs/validation/third-party-manifest-2026-06-16.md`. Release artifacts still need
  artifact-specific license/NOTICE bundles under `docs/release-artifact-notices.md` before
  public release.
- Current public-source preflight:
  `docs/validation/public-source-push-preflight-2026-06-15.md`.
- H1 public-safe competitor comparison evidence is accepted for closeout in
  `docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md`. This closes only the
  evidence-review blocker and does not approve public benchmark reports, does not approve public
  benchmark claims, does not approve release artifacts, does not approve package publication, does
  not approve production positioning, does not approve hosted surfaces, or wording beyond the exact
  approved pre-alpha sentence.
- H2 artifact scope is approved for `source-snapshot` only in
  `docs/validation/h2-source-snapshot-scope-approval-2026-06-20.md`. This does not approve
  binaries, wheels, npm packages, crate publication, hosted surfaces, public benchmark reports, or
  wording beyond the exact approved pre-alpha sentence.
- H2 source-snapshot candidate evidence is recorded in
  `docs/validation/h2-source-snapshot-candidate-evidence-2026-06-20.md` for source HEAD
  `60abfd4`; closeout is recorded separately for the exact source-snapshot candidate and surface.
- H2 is closed for the exact source-snapshot candidate and source-snapshot-only surface in
  `docs/validation/h2-source-snapshot-closeout-2026-06-20.md`. Binaries, wheels, npm packages,
  crate publication, and hosted surfaces remain blocked; public benchmark reports remain blocked;
  public beta, production positioning, and wording beyond the exact approved pre-alpha sentence
  remain blocked.
- Refreshed H2 source-snapshot candidate evidence is recorded in
  `docs/validation/h2-source-snapshot-candidate-evidence-660f268-2026-06-20.md` for approved
  candidate source HEAD `660f268`.
- H2 is closed for the exact source-snapshot candidate at source HEAD `660f268` and
  source-snapshot-only surface in
  `docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md`. Binaries, wheels, npm
  packages, crate publication, and hosted surfaces remain blocked; public benchmark reports remain
  blocked; public beta, production positioning, and wording beyond the exact approved pre-alpha
  sentence remain blocked.

## Approved Execution Sequence

Manual product approval on 2026-06-20 approved the following next-step sequence. That sequence
approval was not a public-release approval and did not itself close H1 or H2. It does not approve
public benchmark reports, does not approve release artifacts, does not approve package
publication, does not approve production positioning, does not approve hosted surfaces, and does
not approve wording beyond the exact approved pre-alpha sentence. Subsequent records close H1 and
H2 only within their stated boundaries.

1. Close H1: closed for public-safe evidence acceptance only in
   `docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md`; public benchmark claims and
   comparison-report wording remain blocked.
2. Close H2: closed for the exact source-snapshot candidate at source HEAD `660f268` and
   source-snapshot-only surface in
   `docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md`. The approved artifact scope is
   `source-snapshot` only; binaries, wheels, npm packages, crate publication, hosted surfaces,
   public benchmark reports, public beta, production positioning, and wording beyond the exact
   approved pre-alpha sentence remain blocked.
3. Approve any wording beyond the exact pre-alpha sentence only after the benchmark owner maps each
   exact sentence to accepted evidence and the decider approves the exact wording and surface.
4. Harden release-scope engineering blockers: release packaging/operator setup, stable CLI/Python
   docs, public setup path, Phase 2 project-maintained PDFium builds, broader corpus/failure
   fixtures, and cross-platform runtime provisioning.
5. Run release-candidate validation gates: source gates plus `ethos-bench` publication preflight,
   readiness, smoke, and test gates, then rerun posture and claims gates after any public-facing
   text changes.

## Claim Rules

Approved exact public source wording until the checklist is complete:

```text
Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across
native Ethos JSON and supported foreign parser outputs.
```

This approval is limited to the exact sentence above on current source-repository public surfaces.
It does not approve public benchmark reports, does not approve release artifacts, does not approve
package publication, does not approve production positioning, does not approve hosted surfaces, and
does not approve altered public wording.

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
