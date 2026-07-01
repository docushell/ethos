# Ethos Execution Status

Date: 2026-07-01
Owner: product / decider
Status: v0.2.0 public beta/evaluation surfaces are live for the GitHub source repository; Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.2.0`; the Python `ethos-pdf` wheel at `0.2.0`; npm `@docushell/ethos-pdf@0.2.1`; and GitHub Release `v0.2.0` macOS arm64/Linux x64 CLI artifacts. npm `@docushell/ethos-pdf@0.2.0` is deprecated because it shipped stale CLI binaries that reported `ethos 0.1.2`; use `0.2.1`. v0.3.0 release-candidate source metadata is active in the repository for app-answer-release validation only; no public `0.3.0` install wording, publication, artifact, tag, npm alignment, or DocuShell integration is approved. PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`. Hosted surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds, public benchmark reports, public benchmark claims, speed, footprint, parser-quality, table-quality, `ethos-doc`, and `ethos-rag` remain blocked.

v0.3.0 package/build evidence is recorded in
`docs/validation/v0-3-0-package-build-evidence-validation-2026-07-01.md`. Rust candidate package
assembly passed for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.3.0`, the
registry-equivalent Rust consumer check passed, and the local Python wheel build/install/helper
smoke passed for `ethos-pdf==0.3.0`. Installable `0.3.0` wording remains blocked, and `cargo
publish`, PyPI upload, npm publication, GitHub Release artifact publication, tag creation, npm
alignment, and DocuShell integration remain blocked.

v0.3.0 package publication approval request is recorded in
`docs/validation/v0-3-0-package-publication-approval-request-validation-2026-07-01.md`. It requests
decider review for the exact `0.3.0` crates.io publication inputs for `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf`, and the exact deterministic PyPI wheel
`ethos_pdf-0.3.0-py3-none-any.whl`. Actual crates.io publication, PyPI upload, package tag
creation, release tag creation, installable `0.3.0` wording, npm alignment, GitHub Release artifact
publication, and DocuShell integration remain blocked pending explicit approval, operator action,
and closeout records.

v0.3.0 release approval decision is recorded in
`docs/validation/v0-3-0-release-approval-decision-validation-2026-07-01.md`. It accepts the exact
app-answer-release contract release-prep packet and authorizes source activation on
`dev/v0-3-approval-packet` for Rust and Python metadata only. Package publication, tag creation,
artifact publication, npm alignment, installable `0.3.0` wording, hosted surfaces, production
positioning, Windows packaged artifacts, bundled project-maintained PDFium builds, public
benchmark claims, `ethos-doc`, `ethos-rag`, and DocuShell integration remain blocked until
separate evidence records and operator decisions pass.

v0.3.0 version activation is recorded in
`docs/validation/v0-3-0-version-activation-validation-2026-07-01.md`. Rust workspace/package
metadata, internal path-dependency pins, `Cargo.lock`, Python package metadata, and
`ethos_pdf.__version__` now point to `0.3.0` for app-answer-release candidate validation. npm
remains at `0.2.1`, and public install commands remain on the current published `0.2.0`
Rust/Python and `0.2.1` npm surfaces until publication, registry/artifact availability, smoke
evidence, and wording closeout records pass.

App-answer-release contract release prep is recorded in
`docs/validation/app-answer-release-contract-release-prep-validation-2026-07-01.md` for decider
review only. It binds the merged app-release source surfaces, proposes `0.3.0` for review, and
feeds the later v0.3.0 approval and activation records. Package publication, tag creation,
artifact publication, installable `0.3.0` wording, npm publication, hosted surfaces, production
positioning, Windows packaged artifacts, bundled project-maintained PDFium builds, public
benchmark claims, `ethos-doc`, `ethos-rag`, and DocuShell integration remain blocked pending later
evidence records.

Historical baseline before v0.2.0 closeout: Public beta evaluation was approved for the GitHub source repository; the three bounded Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`; the Python `ethos-pdf` wheel at `0.1.2`; the npm `@docushell/ethos-pdf` CLI package at `0.1.2`; and the GitHub Release `v0.1.2` macOS arm64 and Linux x64 CLI artifacts. Internal Milestone D source-only closeout remains complete, with Milestone E prep source-only closeout recorded for the internal prep boundary. Week 0 governance is accepted, WS-ENGINE Phase 1 has a real narrow PDFium path, WS-VERIFY-ALPHA has real deterministic evidence checks over native Ethos JSON and pinned OpenDataLoader output, WS-HARNESS has fail-closed readiness scaffolding, the Gate Zero corpus/hardware manifest and direct competitor lock are frozen/signed, ADR-0005 records an accepted `PROCEED` decision for internal Milestone B continuation, ADR-0006 closes package identifier/trademark validation, ADR-0007 locks the product direction, and patch `0.1.1` plus patch `0.1.2` publication/install wording closeouts are recorded for the approved evaluation surfaces. The exact historical public sentence approved for source, Rust crate, Python wheel, npm package, macOS arm64 CLI artifact, and Linux x64 CLI artifact evaluation surfaces was: "Ethos is a deterministic document evidence layer for source-grounded verification and citation checking across native Ethos JSON and supported foreign parser outputs. The current beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`, the Python `ethos-pdf` wheel at `0.1.2`, the npm `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS arm64/Linux x64 CLI artifacts. PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`." Milestone C has a source-tree internal artifact-validation closeout for the RAG chunk and security-report trust-loop checks. Milestone D has a source-tree internal source-only closeout recorded in `docs/validation/milestone-d-final-closeout-validation-2026-06-19.md`; the narrow `verify_citations` v1 contract in `docs/milestone-d-verify-citations-contract.md` remains carried by the existing `ethos verify` path and fixture-backed validation. The D `crop_element` v1 contract in `docs/milestone-d-crop-element-contract.md` is carried by the source-bound `ethos crop_element` CLI command plus existing `ethos verify --crop-dir` evidence artifacts; `ethos-core::crop_element` validates request identity, resolves one native document element, and emits descriptor/rendered crop metadata for that source-only contract when caller-provided source PDF bytes are bound. The `sandbox_subprocess` v1 contract in `docs/milestone-d-sandbox-subprocess-contract.md` classifies existing PDF worker-process timeout, memory-limit, stable-error, and diagnostics-gated stderr behavior without adding hardened sandbox rules. The first Milestone E prep boundary is recorded in `docs/milestone-e-prep-scope.md`, the internal fixture-candidate inventory is recorded in `docs/milestone-e-fixture-candidates.json`, internal fixture-promotion criteria are recorded in `docs/milestone-e-fixture-promotion-criteria.json`, the internal trust-loop walkthrough plan is recorded in `docs/milestone-e-internal-trust-loop-walkthrough.json`, the internal trust-loop use protocol is recorded in `docs/milestone-e-internal-trust-loop-use-protocol.json`, the internal trust-loop rehearsal/evidence matrix is recorded in `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`, and the internal trust-loop blocker ledger is recorded in `docs/milestone-e-internal-trust-loop-blocker-ledger.json`; these E prep JSON artifacts are schema-validated by `schemas/validate_examples.py` and only identify tracked trust-loop fixture candidates, internal promotion criteria, internal walkthrough sequencing, source-checkout rules for internal use, internal evidence-lane rehearsal planning, blocked-output alignment, evidence-lane alignment, diagnostic-boundary alignment, promotion-status alignment at `not_promoted_beyond_internal_fixture_planning`, source-status alignment at `source-only-pre-alpha-internal-milestone-e-prep`, applies-to binding alignment across current E source artifacts, required-before alignment for current readiness gates including `make milestone-e-prep remains green`, validation-record source-head alignment for each `Validated source HEAD before this record` line, and explicit blocker tracking that does not resolve or soften blockers. The Milestone E prep source-only closeout is recorded in `docs/validation/milestone-e-final-closeout-validation-2026-06-20.md` and does not resolve or soften blockers outside the approved public beta evaluation surfaces. Hosted surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, public benchmark claims, and all speed/footprint/parser-quality/table-quality/production claims remain blocked. The controlled-run handoff remains `docs/gate-zero-evidence-runbook.md`; the accepted decision record is `docs/decisions/ADR-0005-gate-zero-decision.md`.

v0.2.0 release-candidate activation is recorded in `docs/v0-2-0-release-prep.md`. The
release-candidate lane adds the bounded public sentence "v0.2.0 release-candidate source versions
are activated for JSON verification and evidence anchoring" while keeping `0.2.0` publication,
package tags, GitHub Release artifacts, PyPI upload, public install wording, hosted surfaces,
production positioning, public benchmark claims, Windows packaged artifacts, and bundled
project-maintained PDFium blocked until separate approval, operator evidence, and closeout records
pass.

v0.2.0 release approval request is recorded in
`docs/validation/v0-2-0-release-approval-request-validation-2026-06-25.md` for decider review
only. It requests exact review of the source commit, version-bump plan, `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf` crate set, `ethos-pdf` continuity decision, Python scope, npm
fate, CLI artifact decision, tag/package-tag request, ADR-0006/name ownership confirmation,
`reserved_crates_io_version` handling, crates.io append-only risk, operator and closeout owner,
and retained blockers. Version bump, release-candidate branch creation, package publication, tag
creation, artifact publication, and installable `0.2.0` wording remain blocked until explicit
approval and later evidence records pass.

v0.2.0 release approval decision is recorded in
`docs/validation/v0-2-0-release-approval-decision-validation-2026-06-25.md`. It accepts
release-candidate version activation on `dev/v0-2-approval-packet` for the exact `0.2.0` Rust
crate set, Python wheel scope, npm CLI package scope, CLI artifact preparation, `CHANGELOG.md`,
and release-candidate wording only. `cargo publish`, PyPI upload, `npm publish`, GitHub Release
artifact upload, release tag creation, package tag creation, and installable `0.2.0` public
wording remain blocked until separate evidence records and operator decisions pass.

v0.2.0 version activation is recorded in
`docs/validation/v0-2-0-version-activation-validation-2026-06-25.md`. Rust workspace/package
dependency versions, Python package metadata and `ethos_pdf.__version__`, npm package metadata,
and release-candidate wording now point to `0.2.0` for candidate validation. Public install
commands and installable wording remain on the approved `0.1.2` evaluation baseline until
publication, registry/artifact availability, smoke evidence, and wording closeout records pass.

v0.2.0 `ethos-doc-core` dry-run evidence is recorded in
`docs/validation/v0-2-0-ethos-doc-core-cargo-publish-dry-run-evidence-validation-2026-06-25.md`.
The first Rust registry dry-run gate passed for `ethos-doc-core 0.2.0` and recorded the generated
crate SHA256
`de86ce74dd791b50d0722cddc878756cceabae2162f747e9e24902b88e5c7de1`. Actual `cargo publish`,
dependent-crate dry-runs, tag creation, artifact publication, and installable `0.2.0` wording
remain blocked until separate evidence and operator decisions pass.

v0.2.0 package/build evidence is recorded in
`docs/validation/v0-2-0-package-build-evidence-validation-2026-06-25.md`. Python wheel local build,
install, and wrapper smoke passed; the local macOS arm64 draft CLI artifact smoke reported
`ethos 0.2.0`; npm tests and dry-run package metadata passed for `@docushell/ethos-pdf@0.2.0`.
npm v0.2.0 artifact candidacy remains blocked because the checked-in vendored binaries still
report `ethos 0.1.2`. Linux x64 CLI artifact evidence, npm vendor refresh, publication, tag
creation, artifact upload, and installable `0.2.0` wording remain blocked.

v0.2.0 draft artifact evidence is recorded in
`docs/validation/v0-2-0-draft-artifact-evidence-validation-2026-06-25.md`. The release workflow
passed on `dev/v0-2-approval-packet` and produced macOS arm64 plus Linux x64 draft CLI artifacts
whose smoke sidecars report `ethos 0.2.0`. Artifact publication, npm vendor refresh, registry
publication, tag creation, and installable `0.2.0` wording remain blocked until separate records
and operator decisions pass.

v0.2.0 npm vendor refresh is recorded in
`docs/validation/v0-2-0-npm-vendor-refresh-validation-2026-06-25.md`. The checked-in npm vendor
payload comes from the validated v0.2.0 macOS arm64 and Linux x64 draft CLI artifacts. npm
`@docushell/ethos-pdf@0.2.0` was published with stale binaries and deprecated; npm
`@docushell/ethos-pdf@0.2.1` was published and registry install smoke reports `ethos 0.2.0`.

Older Milestone E paragraphs below preserve historical review records and their blockers at the time they were written. Patch `0.1.1` closeout records supersede those historical blockers only for the approved source, Rust crate, Python wheel, npm package, macOS arm64 CLI artifact, and Linux x64 CLI artifact evaluation surfaces.

Patch `0.1.2` npm publication approval request is recorded in
`docs/validation/patch-0-1-2-npm-publication-approval-request-validation-2026-06-24.md` for decider
review only. It binds the exact `@docushell/ethos-pdf@0.1.2` npm candidate from the refreshed
vendor payload, but `npm publish`, registry closeout, public installation wording, hosted surfaces,
production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds,
public benchmark reports, public benchmark claims, `ethos-doc`, and `ethos-rag` remain blocked.

Patch `0.1.2` npm publication approval decision is recorded in
`docs/validation/patch-0-1-2-npm-publication-approval-decision-validation-2026-06-24.md` for later
operator action only. It accepts the exact `@docushell/ethos-pdf@0.1.2` npm candidate and required
pre-publish checks, but does not run `npm publish`; registry closeout, public installation wording,
hosted surfaces, production positioning, Windows packaged artifacts, bundled project-maintained
PDFium builds, public benchmark reports, public benchmark claims, `ethos-doc`, and `ethos-rag`
remain blocked.

Patch `0.1.2` npm publication blocker is recorded in
`docs/validation/patch-0-1-2-npm-publication-blocker-validation-2026-06-24.md`. The approved
`@docushell/ethos-pdf@0.1.2` publish attempt failed with npm `E404`; registry checks still show
latest `0.1.1`, so retry, registry closeout, public installation wording, hosted surfaces,
production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds,
public benchmark reports, public benchmark claims, `ethos-doc`, and `ethos-rag` remain blocked.

Patch `0.1.2` npm publication closeout is recorded in
`docs/validation/patch-0-1-2-npm-publication-closeout-validation-2026-06-24.md`. npm now reports
`@docushell/ethos-pdf@0.1.2` as latest with matching registry shasum, integrity, tarball URL,
source commit, file count, and unpacked size. Public installation wording, hosted surfaces,
production positioning, Windows packaged artifacts, bundled project-maintained PDFium builds,
public benchmark reports, public benchmark claims, `ethos-doc`, and `ethos-rag` remain blocked.

Patch `0.1.2` public install wording closeout is recorded in
`docs/validation/patch-0-1-2-public-install-wording-closeout-validation-2026-06-24.md`. The
public README and public boundary inventory now point npm installation to
`@docushell/ethos-pdf@0.1.2` and GitHub Release CLI archives to `v0.1.2`. Rust crate installation
remains at `0.1.1`, and Python installation remains at `ethos-pdf==0.1.1` until separate
crates.io/PyPI `0.1.2` publication closeout records pass.

Patch `0.1.2` crates.io publication approval request is recorded in
`docs/validation/patch-0-1-2-crates-publication-approval-request-validation-2026-06-25.md` for
decider review only. It binds exact `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` crate
artifacts at `0.1.2`, SHA256 values, source commit, source tree, package tag names, and requested
operator commands. `cargo publish` remains blocked, package tag creation remains blocked, Rust
crate public installation wording remains blocked, and Python installation remains at
`ethos-pdf==0.1.1` until separate approval, operator publication, and closeout records pass.

Patch `0.1.2` crates.io publication approval decision is recorded in
`docs/validation/patch-0-1-2-crates-publication-approval-decision-validation-2026-06-25.md`.
It accepts only the exact bounded later operator commands for `ethos-doc-core`, `ethos-verify`,
and `ethos-pdf` at `0.1.2`. Actual crates.io publication remains a separate operator action,
package tag creation remains blocked until publication closeout, Rust crate public installation
wording remains blocked until registry availability closeout, and Python installation remains at
`ethos-pdf==0.1.1` until separate PyPI `0.1.2` approval, operator publication, and closeout records
pass.

Patch `0.1.2` crates.io publication closeout is recorded in
`docs/validation/patch-0-1-2-crates-publication-closeout-validation-2026-06-25.md`. crates.io now
reports `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`. Rust crate public
installation wording remains blocked until a separate wording and availability closeout, and Python
installation remains at `ethos-pdf==0.1.1` until separate PyPI `0.1.2` approval, operator
publication, and closeout records pass.

Patch `0.1.2` Rust public install wording closeout is recorded in
`docs/validation/patch-0-1-2-rust-public-install-wording-closeout-validation-2026-06-25.md`.
The public README and public boundary inventory now point Rust crate installation to
`ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`. Python installation remains at
`ethos-pdf==0.1.1` until separate PyPI `0.1.2` approval, operator publication, and closeout
records pass.

Patch `0.1.2` Python PyPI publication approval request is recorded in
`docs/validation/patch-0-1-2-python-publication-approval-request-validation-2026-06-25.md`. It
binds the exact deterministic `ethos-pdf==0.1.2` wheel candidate, source commit, source tree,
metadata, SHA256, and local install/import smoke for decider review only. PyPI upload, Python
public installation wording, package tag creation, hosted surfaces, production positioning, Windows
packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, and public
benchmark claims remain blocked.

Patch `0.1.2` Python PyPI publication approval decision is recorded in
`docs/validation/patch-0-1-2-python-publication-approval-decision-validation-2026-06-25.md`. It
accepts only the exact bounded later operator action for the deterministic `ethos-pdf==0.1.2`
wheel. Actual PyPI upload remains a separate operator action, Python public installation wording
remains blocked until PyPI availability closeout, package tag creation remains blocked, and hosted
surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
builds, `ethos-doc`, `ethos-rag`, and public benchmark claims remain blocked.

Patch `0.1.2` Python PyPI publication closeout is recorded in
`docs/validation/patch-0-1-2-python-publication-closeout-validation-2026-06-25.md`. PyPI now
reports `ethos-pdf==0.1.2` with matching wheel filename, SHA256, upload time, size, URL, and
non-yanked status. Python public installation wording remains blocked until a separate wording and
availability closeout, package tag creation remains blocked, and hosted surfaces, production
positioning, Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`,
`ethos-rag`, and public benchmark claims remain blocked.

Patch `0.1.2` Python public install wording closeout is recorded in
`docs/validation/patch-0-1-2-python-public-install-wording-closeout-validation-2026-06-25.md`.
The public README, Python package docs, and public boundary inventory now point Python installation
to `ethos-pdf==0.1.2`. Package tag creation remains blocked, and hosted surfaces, production
positioning, Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`,
`ethos-rag`, and public benchmark claims remain blocked.

Patch `0.1.2` package tag approval request is recorded in
`docs/validation/patch-0-1-2-package-tag-approval-request-validation-2026-06-25.md`. It records the
exact package tag names, source commit, source tree, and requested later operator commands for
decider review only. Package tag creation remains blocked until a separate explicit approval
decision is recorded, and hosted surfaces, production positioning, Windows packaged artifacts,
bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, and public benchmark claims
remain blocked.

Patch `0.1.2` package tag approval decision is recorded in
`docs/validation/patch-0-1-2-package-tag-approval-decision-validation-2026-06-25.md`. It accepts
the exact package tag names, source commit, source tree, and later operator commands. Package tag
creation remains a separate operator action after this decision is merged and validation passes on
merged source, and hosted surfaces, production positioning, Windows packaged artifacts, bundled
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

Public approval lane blocker prep is recorded in
`docs/milestone-e-public-approval-lane-blockers.json` and schema-bound by
`schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json`. This public approval lane
blocker ledger records the original source-only public beta evaluation approval and keeps hosted
surface, production positioning, public benchmark report, public benchmark claim, release-artifact,
binary, wheel, npm package, unapproved crate, and project-maintained PDFium build lanes blocked.
Public beta source-only evaluation is approved for the GitHub source repository surface reviewed at
commit `902c423` and merged to main as source-equivalent commit `6019a97`; the later Rust crate
evaluation surface is recorded separately in
`docs/validation/milestone-e-package-publication-public-installation-availability-validation-2026-06-22.md`.
Hosted surfaces remain blocked. Production positioning remains blocked. Public benchmark reports
remain blocked. Public benchmark claims remain blocked.

Public beta approval prep is recorded in `docs/milestone-e-public-beta-approval-prep.json` and
schema-bound by `schemas/ethos-milestone-e-public-beta-approval-prep.schema.json`. Source-only
public beta evaluation is approved for the GitHub source repository only. Exact approved wording:
"Ethos is public beta for source-only evaluation. It verifies whether AI citations are grounded in
document evidence across native Ethos JSON and supported foreign parser outputs. Package
publication, hosted surfaces, production positioning, and public benchmark claims remain blocked."
The approval does not approve package publication, hosted surfaces, production positioning, public
benchmark reports, public benchmark claims, release artifacts, binaries, wheels, npm packages, crate
publication, project-maintained PDFium builds, or public result wording.

Public beta required-evidence records are recorded in
`docs/validation/milestone-e-public-beta-approval-decision-validation-2026-06-20.md`,
`docs/validation/milestone-e-public-beta-release-scope-engineering-blocker-review-validation-2026-06-20.md`,
`docs/validation/milestone-e-public-beta-public-setup-path-review-validation-2026-06-20.md`,
and `docs/validation/milestone-e-public-beta-pdfium-build-path-review-validation-2026-06-20.md`.
They complete the current evidence-record set for review, do not approve public beta, and keep
the historical blocker-review conclusions visible. The later source-only approval record is
`docs/validation/milestone-e-public-beta-source-only-approval-validation-2026-06-20.md`.

Package publication approval prep is recorded in
`docs/milestone-e-package-publication-approval-prep.json` and schema-bound by
`schemas/ethos-milestone-e-package-publication-approval-prep.schema.json`. Package publication
prep is approved for internal Rust crate publication preparation only, scoped to the five ADR-0006
reserved priority crates.io identifiers. It does not approve package publication, real-version
`cargo publish`, public installation, release artifacts, binaries, wheels, npm packages, hosted
surfaces, production positioning, public benchmark reports, public benchmark claims, or
project-maintained PDFium builds. The dedicated prep approval record is
`docs/validation/milestone-e-package-publication-prep-approval-validation-2026-06-20.md`.
Package publication evidence records are indexed under `docs/validation/` for reserved-name
inventory reconciliation, metadata/license/README readiness, dry-run/smoke planning, version/tag
policy, and PDFium packaging boundary review. They record blockers for the prep lane and do not
approve package publication.
The metadata-readiness follow-up is recorded in
`docs/validation/milestone-e-package-publication-metadata-readiness-closeout-validation-2026-06-21.md`
for the three current in-tree priority candidate crates. `ethos-doc` and `ethos-rag` remain reserved
placeholders without in-tree manifests, and package publication remains blocked.
The current dry-run/smoke follow-up is recorded in
`docs/validation/milestone-e-package-publication-current-dry-run-smoke-validation-2026-06-22.md`.
It records local package assembly for `ethos-doc-core` and source-tree checks for `ethos-verify`
and `ethos-pdf`; exact registry-backed assembly activation, public installation, and package
publication remain blocked.
The version/tag policy follow-up is recorded in
`docs/validation/milestone-e-package-publication-version-tag-policy-closeout-validation-2026-06-21.md`.
It records source-tree version, reserved placeholder version, source snapshot tag, and future
package tag namespace separation; real package version selection, package tag creation, public
installation, and package publication remain blocked.
The PDFium boundary follow-up is recorded in
`docs/validation/milestone-e-package-publication-pdfium-boundary-closeout-validation-2026-06-21.md`.
It records the current source-tree `ethos-pdf` boundary: no bundled PDFium binary, caller-provided
PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`, and no raw PDFium FFI types across public schemas/APIs;
project-maintained PDFium builds, public installation, and package publication remain blocked.
The dependency-ordering follow-up is recorded in
`docs/validation/milestone-e-package-publication-dependency-ordering-closeout-validation-2026-06-21.md`.
It records that any later dependent-candidate review must stage `ethos-doc-core` before
`ethos-verify` and `ethos-pdf`; registry-backed dependent package assembly, package dependency
manifest migration, real package version selection, package tag creation, public installation, and
package publication remain blocked.
The manifest-migration prep follow-up is recorded in
`docs/validation/milestone-e-package-publication-manifest-migration-prep-validation-2026-06-21.md`.
It records the future core package-name migration and workspace dependency alias shape while
leaving current Cargo manifests unchanged; registry-backed dependent package assembly, package
dependency manifest activation, real package version selection, package tag creation, public
installation, and package publication remain blocked.
The manifest-activation prep follow-up is recorded in
`docs/validation/milestone-e-package-publication-manifest-activation-prep-validation-2026-06-21.md`.
It records the future package dependency manifest activation review boundary while changing no
Cargo manifests; package dependency manifest activation, registry-backed dependent package
assembly activation, public installation, and package publication remain blocked.
The registry-assembly prep follow-up is recorded in
`docs/validation/milestone-e-package-publication-registry-assembly-prep-validation-2026-06-21.md`.
It records the future non-public dependent candidate assembly rehearsal boundary while creating no
registry and leaving current Cargo manifests unchanged; registry-backed dependent package assembly
activation, package dependency manifest activation, real package version selection, package tag
creation, public installation, and package publication remain blocked.
The registry-assembly activation prep follow-up is recorded in
`docs/validation/milestone-e-package-publication-registry-assembly-activation-prep-validation-2026-06-21.md`.
It records the future registry-backed dependent package assembly activation review boundary while
creating no registry and activating no registry-backed assembly; registry-backed dependent package
assembly activation, public installation, and package publication remain blocked.
The real-version-selection prep follow-up is recorded in
`docs/validation/milestone-e-package-publication-real-version-selection-prep-validation-2026-06-21.md`.
It records the future SemVer candidate review boundary while selecting no package publication
version; real package version selection approval, package tag creation, public installation, and
package publication remain blocked.
The tag-creation prep follow-up is recorded in
`docs/validation/milestone-e-package-publication-tag-creation-prep-validation-2026-06-21.md`.
It records the future package tag creation review boundary while creating no package tag and
selecting no package publication version; package tag creation, public installation, and package
publication remain blocked.

## Current Reality

The repository is in public beta/evaluation for the approved source, package, and CLI artifact surfaces, and production positioning remains blocked. Real parsing and real alpha verification exist. They are narrow, fixture-backed, and now have an accepted internal Gate Zero decision for roadmap control. That decision is not a public benchmark report, release approval, package approval, production approval, or claim approval.

The committed implementation now includes:

- A real PDFium-backed born-digital PDF extraction path in `ethos-pdf`, loaded only from an explicit `ETHOS_PDFIUM_LIBRARY_PATH`.
- A pinned Phase 1 PDFium profile in `docs/pdfium-profile.md` and `profiles/ethos-deterministic-v1.json`: `chromium/7881`, V8/XFA disabled, platform artifact hashes, runtime library hashes, and provenance are recorded.
- Runtime checks that reject missing or mismatched PDFium versions, release artifacts, and extracted libraries with stable errors before dynamic loading.
- The determinism workflow includes a Windows x64 preflight lane for core c14n/profile/fingerprint contract tests, while PDFium-backed corpus work remains explicitly skipped unless the pinned runtime is configured on that runner. A static workflow test guards that matrix wiring.
- `ethos doc parse` / `ethos fingerprint` PDF execution through a worker process with `max_parse_ms` timeout enforcement, stable error-envelope relay, diagnostics-gated worker stderr, and page-range validation/filtering.
- Quantized page/span extraction at the backend boundary, plus a basic deterministic layout pass that assembles paragraph `text_block` elements, fixture-backed alpha heading and flat list-item elements, and simple column reading order for the current born-digital fixtures. Current alpha layout confidence is explicit for heading signals, and below-threshold layout confidence emits deterministic `low_confidence_reading_order` diagnostics instead of staying silent. Fixture validation binds selected `fixture.json` expectations to committed extraction/layout goldens and binds current alpha text/Markdown exports to committed layout output so current read-order, element-type, heading-export, list-item, and export cases fail closed on drift.
- An internal layout evaluator scaffold exists at `fixtures/evaluate_layout_alpha.py` and `make layout-evaluator-alpha`. It reads committed `fixture.json`, `extraction.json`, `layout.json`, `text.txt`, and `markdown.md` files, summarizes alpha element-type and subset coverage, and fails closed on missing layout expectations, dangling/invalid warning references, confidence-policy drift, export-golden drift, invalid span expectation metadata, expected page/span-text/font-id drift, expected rotation drift, or drift in fixture-backed reading order / heading / list-item / hyphenation / ligature cases. PR CI runs the evaluator and has a static workflow guard for that wiring.
- Schema/example/profile validation is green through `schemas/validate_examples.py` using `jsonschema` draft 2020-12 validation, including the crop descriptor artifact contract plus referential-integrity and bbox sanity checks outside JSON Schema. Fixture validation also binds internal font-isolation PDFs to committed manifest hashes.
- `ethos verify` now produces non-empty quote, value, presence, and table-cell verification checks over native Ethos document JSON and synthetic OpenDataLoader-style JSON through `--grounding opendataloader-json`; it also verifies quote/value/presence citations over pinned real OpenDataLoader 2.4.7 JSON, including grounded and ungrounded cases, maps explicit real OpenDataLoader-style row/cell structures to table-cell grounding, and normalizes conservative real-style text/child-container aliases when page/bbox/text data remains explicit. Citation/config inputs are rejected when they drift outside the closed schemas. The public demo harness covers grounded, ungrounded, split-quote, not-found, stale-fingerprint, unsupported non-v1 claim, capability-limited, malformed-citation, malformed OpenDataLoader-style input, and summary-format reject paths.
- Verification semantics are now trust-honest at alpha scope: quote containment is explicitly labeled, value/table-cell checks require normalized equality, fingerprint-pinned citations fail closed when source fingerprints are unavailable, and structured capability limits explain why a run is downgraded.
- `ethos evidence anchor` now has a post-merge [`evidence_anchor` v1 guard](evidence-anchor-v1-contract.md) over the deterministic source-tracing command, request/report schemas, focused CLI tests, native Ethos JSON and OpenDataLoader-style grounding inputs, and explicit non-goals. Focused validation is `make evidence-anchor-v1-contract PYTHON=<jsonschema-venv>/bin/python`; PR CI also runs `.github/scripts/test_evidence_anchor_v1_contract.py` so the guard's richer drift checks are enforced automatically. This guard does not expand public beta/evaluation posture, hosted surfaces, production positioning, semantic answer verification, or benchmark/parser/table-quality claims.
- `make verify-alpha` is the current alpha trust-loop command: it checks native examples, split-quote evidence matching, unsupported non-v1 claim reporting, synthetic OpenDataLoader-style examples, pinned real OpenDataLoader grounded/ungrounded examples, schema validation, verify-alpha case inventory coverage, usage diagnostics for malformed citations and malformed OpenDataLoader-style structures, byte-identical repeated verification reports, byte-identical native crop descriptors, summary diagnostics for an ungrounded native case, and foreign fixture manifest hash binding. `make milestone-b-internal-checks` composes the current internal Milestone B validation path across fixture validation, font-policy profile checks, verify alpha, layout evaluator, Python surface tests, and policy gates; CI has a static guard for that target's command wiring.
- The Python surface under `python/ethos_pdf` shells out to a caller-provided local `ethos` CLI binary for `ethos doc parse` JSON, Markdown, text output, and source-bound `ethos crop_element` JSON/artifact arguments, and has stdlib unit tests that use a fake local command. The published `ethos-pdf==0.1.1` wheel exposes this bounded wrapper for evaluation; it does not bundle the CLI or PDFium.
- Native Ethos verification can emit deterministic, schema-backed crop descriptor JSON artifacts through `--crop-dir`; these bind `document_fingerprint`, page, bbox, and check ids. Native `crop_ref` filenames are logical evidence references derived from document fingerprint, check id, and page, while descriptors still record the exact observed bbox. When `--crop-source-pdf` is supplied, the CLI validates source-PDF fingerprint binding and emits PNG crop artifacts whose filenames, byte hashes, dimensions, and source fingerprint are bound from the descriptor. `make verify-rendered-crops` checks same-host repeated-run stability for the rendered artifact path, and `make compare-rendered-crops` classifies two rendered-crop runs by separating logical evidence identity from rendered artifact byte equality. Cross-platform rendered image determinism is not claimed; the 2026-06-14 macOS arm64 vs Linux x64 validation record in `docs/validation/rendered-crops-2026-06-14.md` preserved document fingerprint and `payload_sha256` but failed rendered artifact byte equality because the evidence bbox differed slightly across platforms.
- `ethos rag chunk` has a committed-example artifact loop over `schemas/examples/document.example.json` and `schemas/examples/chunks.example.jsonl`. The current internal checks cover exact fixture/golden output, repeated-run byte identity, schema/example validation, stale page/element/bbox-page reference rejection, and default-chunk exclusion warning-reference rejection.
- `ethos security report` has a source-only pre-alpha artifact check over the committed document example. The current internal checks cover deterministic report output, report/source identity grounding, security-warning lane and message diagnostics, locator grounding, inventory/report parity, summary drift, warning id uniqueness, deterministic warning numbering, and explicit rejection of unsupported current source-warning references.
- `make milestone-c-internal-checks` composes the current internal Milestone C artifact-validation path across RAG chunk and security-report gates; CI/static guard scripts fail closed if that command wiring or the dated closeout record drifts.
- Milestone D source-only pre-alpha contract work is internally closed for the current source-tree scope. `docs/milestone-d-verify-citations-contract.md` defines `verify_citations` v1 as the citation-input, verification-config, grounding-source, and verification-report contract currently carried by `ethos verify`; schema/example validation checks that the minimal citation example and verification-report example stay coherent. Focused validation is `make milestone-d-verify-citations-contract PYTHON=<jsonschema-venv>/bin/python`.
- Milestone D `claim_kind_boundary` v1 contract is closed with `docs/milestone-d-claim-kind-boundary-contract.md`. It defines the supported v1 claim-kind boundary currently carried by `ethos verify`; schema/example validation checks the inventory at `examples/verify/claim_kind_boundary_v1_contract.json`, and the repository guard checks that the non-v1 claim fixture and report golden stay coherent. Focused validation is `make milestone-d-claim-kind-boundary-contract PYTHON=<jsonschema-venv>/bin/python`.
- Milestone D `grounding_source` v1 contract is closed with `docs/milestone-d-grounding-source-contract.md`. It defines `grounding_source` as the parser-neutral evidence boundary currently carried by the `GroundingSource` trait and `ethos verify` report grounding metadata; schema/example validation checks the inventory at `examples/verify/grounding_source_v1_contract.json`, and the repository guard checks that it stays coherent with trait methods, current source implementations, focused verifier tests, and report goldens. Focused validation is `make milestone-d-grounding-source-contract PYTHON=<jsonschema-venv>/bin/python`.
- Milestone D `opendataloader_adapter_shape` v1 contract is closed with `docs/milestone-d-opendataloader-adapter-shape-contract.md`. It defines `opendataloader_adapter_shape` as the OpenDataLoader-style input-shape to `GroundingSource` contract currently carried by `ethos-grounding-opendataloader-json` and `ethos verify --grounding opendataloader-json`; schema/example validation checks the inventory at `examples/verify/opendataloader_adapter_shape_v1_contract.json`, and the repository guard checks that it stays coherent with adapter tests, CLI grounding tests, report goldens, and usage diagnostics. Focused validation is `make milestone-d-opendataloader-adapter-shape-contract PYTHON=<jsonschema-venv>/bin/python`.
- Milestone D `capability_downgrade` v1 contract is closed with `docs/milestone-d-capability-downgrade-contract.md`. It defines `capability_downgrade` as the grounding-source capability declaration to verification-report downgrade contract currently carried by `ethos verify`; schema/example validation checks the inventory at `examples/verify/capability_downgrade_v1_contract.json`, and the repository guard checks that it stays coherent with report goldens. Focused validation is `make milestone-d-capability-downgrade-contract PYTHON=<jsonschema-venv>/bin/python`.
- Milestone D `crop_element` v1 contract is closed with `docs/milestone-d-crop-element-contract.md`. It defines `crop_element` as the element-to-crop-descriptor contract currently carried by source-bound `ethos crop_element` plus existing `ethos verify --crop-dir` evidence artifacts; `ethos-core::crop_element` now validates the source-only request identity, resolves one native document element, builds descriptor/rendered crop metadata, provides the shared logical crop-ref identity helper, supplies the descriptor type used by the verifier crop carrier, and has fail-closed descriptor diagnostics for missing document fingerprints, unsafe crop artifact filenames, crop reference collisions, and source fingerprint mismatches. Schema/example validation checks the request envelope at `schemas/examples/crop-element-request.example.json` and inventory at `examples/crop/crop_element_v1_contract.json`, and the repository guard checks that request identity, document, crop-descriptor examples, and source-bound CLI behavior stay coherent. Focused validation is `make milestone-d-crop-element-contract PYTHON=<jsonschema-venv>/bin/python`.
- Milestone D `crop_element_surface_shape` v1 contract is closed with `docs/milestone-d-crop-element-surface-shape-contract.md`. It defines `crop_element_surface_shape` as the callable source-bound CLI/Python surface shape over the existing crop request and descriptor schemas; schema/example validation checks the inventory at `examples/crop/crop_element_surface_shape_v1_contract.json`, and the repository guard checks that it stays coherent with the request schema, descriptor schema, source-bound CLI command, and source-bound Python wrapper. Focused validation is `make milestone-d-crop-element-surface-shape-contract PYTHON=<jsonschema-venv>/bin/python`.
- Milestone D `sandbox_subprocess` v1 contract is closed with `docs/milestone-d-sandbox-subprocess-contract.md`. It defines `sandbox_subprocess` as the future worker-boundary contract currently represented by the existing PDF worker process behind `ethos doc parse` and `ethos fingerprint`; schema/example validation checks the request envelopes under `schemas/examples/sandbox-subprocess-*.example.json` and inventory at `examples/sandbox/sandbox_subprocess_v1_contract.json`, and the repository guard checks that they stay coherent with the worker test slice. Focused validation is `make milestone-d-sandbox-subprocess-contract PYTHON=<jsonschema-venv>/bin/python`.
- `make milestone-d-internal-contracts PYTHON=<jsonschema-venv>/bin/python` composes the current Milestone D source-only contract gates and has a static guard for that target's command wiring and contract registry, plus the Milestone D contract closeout validation record in `docs/validation/milestone-d-contract-closeout-validation-2026-06-19.md` and final closeout validation record in `docs/validation/milestone-d-final-closeout-validation-2026-06-19.md`. Full 13-D exit is complete for the current source-only pre-alpha scope.
- `make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python` composes the Milestone E prep guard over `docs/milestone-e-prep-scope.md`, `docs/milestone-e-fixture-candidates.json`, `docs/milestone-e-fixture-promotion-criteria.json`, `docs/milestone-e-internal-trust-loop-walkthrough.json`, `docs/milestone-e-internal-trust-loop-use-protocol.json`, `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`, `docs/milestone-e-internal-trust-loop-blocker-ledger.json`, `docs/milestone-e-public-approval-lane-blockers.json`, `docs/milestone-e-public-beta-approval-prep.json`, `docs/milestone-e-package-publication-approval-prep.json`, status/roadmap posture checks, public-surface posture checks, the claims gate, public pre-alpha wording approval guard, release-readiness next-step approval guard, H1 public-safe comparison closeout guard, H2 source-snapshot scope approval guard, source-snapshot candidate audit guard, H2 source-snapshot candidate evidence guard, H2 source-snapshot closeout guard, schema validation, schema-registry alignment, public-boundary alignment, blocked-output alignment, evidence-lane alignment, diagnostic-boundary alignment, promotion-status alignment, source-status alignment, applies-to binding alignment, required-before alignment, public approval lane blocker validation, public beta approval prep validation, public beta required-evidence validation, public beta source-only approval validation, package publication approval prep validation, package publication prep approval validation, package publication evidence record validation, package publication metadata-readiness validation, package publication dry-run/smoke validation, package publication version/tag policy validation, package publication PDFium boundary validation, package publication dependency-ordering validation, validation-command indexing, validation-record indexing, validation-record source-head alignment, the prep guard-sequence index, current prep guard validation, the Milestone E prep source-only closeout record in `docs/validation/milestone-e-final-closeout-validation-2026-06-20.md`, and diff hygiene. This target is source-only and intentionally excludes public-report, release, package, hosted, and broad demo-generation workflows.

Still absent or not claimable: public benchmark reports, public competitor-comparison claims, public speed/quality/footprint claims, OCR/image-only support, real table extraction, mature list/heading/layout semantics beyond current fixture-backed alpha paths, semantic/arithmetic verification beyond deterministic evidence lookup, hosted surfaces, production positioning, Windows packaged artifacts, Phase 2 project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, and any public wording beyond the exact approved patch `0.1.1` public beta/evaluation wording.

## Human / External Blockers

This section preserves the historical Gate Zero and Milestone E blocker ledger. Patch `0.1.1`
closeout records above supersede its old package/release blockers only for the approved source,
Rust crate, Python wheel, npm package, macOS arm64 CLI artifact, and Linux x64 CLI artifact
evaluation surfaces.

PM execution packet: `benchmarks/gate-zero/FREEZE_PACKET.md`.

Resolved control point: ADR-0005 is accepted with `PROCEED` for internal Milestone B
continuation. Its indexed result files and evidence bundles live in the sibling `ethos-bench`
repository. This does not unblock public benchmark reports, releases, packages, production
positioning, or wording beyond the exact approved pre-alpha sentence.

H1 is closed for public-safe evidence acceptance only in
`docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md`. This does not approve public benchmark claims, does not approve public benchmark reports, does not approve comparison-report wording, does not approve releases, does not approve packages, does not approve production positioning, does not approve hosted surfaces, or wording beyond the exact approved pre-alpha sentence.

| ID | Blocker | Required output | Owner | Blocks |
| --- | --- | --- | --- | --- |
| H1 | Execute and review public-safe competitor comparison flow | Closed for public-safe evidence acceptance only in `docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md`; benchmark owner accepted the public-safe competitor comparison evidence for closeout without approving public benchmark claims | Benchmark owner | Public competitor-comparison report remains blocked until exact wording and surface approval |
| H2 | Complete public release/package checklist | Source-snapshot scope is approved in `docs/validation/h2-source-snapshot-scope-approval-2026-06-20.md`; candidate evidence is recorded in `docs/validation/h2-source-snapshot-candidate-evidence-2026-06-20.md`; historical closeout for source HEAD `60abfd4` is recorded in `docs/validation/h2-source-snapshot-closeout-2026-06-20.md`; refreshed candidate evidence for approved candidate source HEAD `660f268` is recorded in `docs/validation/h2-source-snapshot-candidate-evidence-660f268-2026-06-20.md`; H2 is closed for the exact source-snapshot candidate at source HEAD `660f268` and source-snapshot-only surface in `docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md`; binaries, wheels, npm packages, crate publication, and hosted surfaces remain blocked; public benchmark reports remain blocked; H2 itself does not approve public beta, production positioning, or wording beyond the exact approved pre-alpha sentence; later source-only public beta approval is recorded in `docs/validation/milestone-e-public-beta-source-only-approval-validation-2026-06-20.md` | Devrel / decider | Public releases, packages, and production positioning |
| H3 | Approve exact pre-alpha public sentence | Closed for the exact approved pre-alpha sentence only: "Ethos is pre-alpha. It verifies whether AI citations are grounded in document evidence across native Ethos JSON and supported foreign parser outputs." Broader public result language remains blocked. | Benchmark owner / decider | Public text beyond the approved sentence |

The corpus/hardware freeze and direct competitor pins are recorded in `benchmarks/gate-zero/manifest.json` and `benchmarks/competitors.lock.json`. The remaining blockers are public-report, public-release, and broader wording blockers, not manifest/pin placeholders.

## Approved Next-Step Sequence

This sequence is retained as historical 2026-06-20 execution context. Later patch `0.1.1`
records closed the approved release/package/public-install lanes for the bounded evaluation
surfaces named in the current status summary.

Manual product approval on 2026-06-20 approved this execution sequence for the next
release-readiness work. That sequence approval did not itself close H1 or H2. It does not approve
public beta, does not approve public benchmark reports, does not approve release artifacts, does
not approve package publication, does not approve production positioning, does not approve hosted
surfaces, and does not approve wording beyond the exact approved pre-alpha sentence. Subsequent
records close H1 and H2 only within their stated boundaries.

1. Close H1: closed for public-safe evidence acceptance only in
   `docs/validation/h1-public-safe-comparison-closeout-2026-06-20.md`; public benchmark claims and
   comparison-report wording remain blocked.
2. Close H2: closed for the exact source-snapshot candidate at source HEAD `660f268` and
   source-snapshot-only surface in
   `docs/validation/h2-source-snapshot-closeout-660f268-2026-06-20.md`. The approved artifact scope is
   `source-snapshot` only; binaries, wheels, npm packages, crate publication, hosted surfaces,
   public benchmark reports, public beta, production positioning, and wording beyond the exact
   approved pre-alpha sentence remain blocked.
3. Approve any wording beyond the exact pre-alpha sentence: benchmark owner maps each exact
   sentence to accepted evidence, and the decider approves the exact wording and surface.
4. Harden release-scope engineering blockers: release packaging/operator setup, stable CLI/Python
   docs, public setup path, Phase 2 project-maintained PDFium builds, broader corpus/failure
   fixtures, and cross-platform runtime provisioning.
5. Run release-candidate validation gates: source gates plus `ethos-bench` publication preflight,
   readiness, smoke, and test gates, then rerun posture and claims gates after any public-facing
   text changes.

## Current Milestone Posture

Historical milestone-record summaries below keep their at-the-time blocker wording. The current
patch `0.1.1` status is the source of truth for approved evaluation surfaces and retained blockers.

Milestone A has an accepted internal Gate Zero decision for roadmap control, Milestone B is internally closed for the current source-tree validation scope, Milestone C has an internal artifact-validation closeout record, and Milestone D is internally closed for the current source-only pre-alpha scope. Milestone E prep is limited to the source-only boundary in `docs/milestone-e-prep-scope.md`, the internal fixture inventory in `docs/milestone-e-fixture-candidates.json`, the internal fixture-promotion criteria in `docs/milestone-e-fixture-promotion-criteria.json`, the internal trust-loop walkthrough plan in `docs/milestone-e-internal-trust-loop-walkthrough.json`, the internal trust-loop use protocol in `docs/milestone-e-internal-trust-loop-use-protocol.json`, the internal trust-loop rehearsal/evidence matrix in `docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json`, the internal trust-loop blocker ledger in `docs/milestone-e-internal-trust-loop-blocker-ledger.json`, the public approval lane blocker ledger in `docs/milestone-e-public-approval-lane-blockers.json`, public beta approval prep in `docs/milestone-e-public-beta-approval-prep.json`, public beta required-evidence records in `docs/validation/`, source-only public beta approval in `docs/validation/milestone-e-public-beta-source-only-approval-validation-2026-06-20.md`, package publication approval prep in `docs/milestone-e-package-publication-approval-prep.json`, package publication evidence records in `docs/validation/`, package publication metadata-readiness follow-up in `docs/validation/milestone-e-package-publication-metadata-readiness-closeout-validation-2026-06-21.md`, package publication current dry-run/smoke follow-up in `docs/validation/milestone-e-package-publication-current-dry-run-smoke-validation-2026-06-22.md`, package publication version/tag policy follow-up in `docs/validation/milestone-e-package-publication-version-tag-policy-closeout-validation-2026-06-21.md`, package publication PDFium boundary follow-up in `docs/validation/milestone-e-package-publication-pdfium-boundary-closeout-validation-2026-06-21.md`, package publication dependency-ordering follow-up in `docs/validation/milestone-e-package-publication-dependency-ordering-closeout-validation-2026-06-21.md`, package publication manifest-migration prep follow-up in `docs/validation/milestone-e-package-publication-manifest-migration-prep-validation-2026-06-21.md`, package publication manifest-activation prep follow-up in `docs/validation/milestone-e-package-publication-manifest-activation-prep-validation-2026-06-21.md`, package publication registry-assembly prep follow-up in `docs/validation/milestone-e-package-publication-registry-assembly-prep-validation-2026-06-21.md`, package publication registry-assembly activation prep follow-up in `docs/validation/milestone-e-package-publication-registry-assembly-activation-prep-validation-2026-06-21.md`, package publication real-version-selection prep follow-up in `docs/validation/milestone-e-package-publication-real-version-selection-prep-validation-2026-06-21.md`, and package publication tag-creation prep follow-up in `docs/validation/milestone-e-package-publication-tag-creation-prep-validation-2026-06-21.md` until explicit blockers are resolved. The public beta approval prep lane approves only source-only public beta evaluation for the GitHub source repository. The package publication approval prep lane approves only internal Rust crate publication preparation for the five ADR-0006 reserved priority crates.io identifiers; it does not approve package publication. The package publication evidence records document current prep blockers and do not approve package publication. The metadata-readiness follow-up records README, NOTICE, manifest metadata, and include-list readiness for `ethos-core`, `ethos-verify`, and `ethos-pdf`; it does not approve package publication. The current dry-run/smoke follow-up records local package assembly for `ethos-doc-core` and source-tree checks for `ethos-verify` and `ethos-pdf`; public installation and package publication remain blocked. The version/tag policy follow-up records separation between source-tree version, reserved placeholder version, source snapshot tag, and future package tag namespace; real package version selection, package tag creation, public installation, and package publication remain blocked. The real-version-selection prep follow-up records a future SemVer candidate review boundary while selecting no package publication version; real package version selection approval, package tag creation, public installation, and package publication remain blocked. The tag-creation prep follow-up records a future package tag creation review boundary while creating no package tag; package tag creation, public installation, and package publication remain blocked. The PDFium boundary follow-up records the current source-tree `ethos-pdf` boundary; project-maintained PDFium builds, public installation, and package publication remain blocked. The dependency-ordering follow-up records the future dependent-candidate ordering constraint; registry-backed dependent package assembly, package dependency manifest migration, public installation, and package publication remain blocked. The manifest-migration prep follow-up records future manifest shape while current Cargo manifests remain unchanged; registry-backed dependent package assembly, package dependency manifest activation, public installation, and package publication remain blocked. The manifest-activation prep follow-up records future package dependency manifest activation review while current Cargo manifests remain unchanged; registry-backed dependent package assembly activation, package dependency manifest activation, public installation, and package publication remain blocked. The registry-assembly prep follow-up records future non-public dependent candidate assembly rehearsal while no registry is created and current Cargo manifests remain unchanged; registry-backed dependent package assembly activation, package dependency manifest activation, public installation, and package publication remain blocked. The registry-assembly activation prep follow-up records future registry-backed dependent package assembly activation review while no registry is created and no registry-backed assembly is activated; registry-backed dependent package assembly activation, public installation, and package publication remain blocked. The public-facing readiness ledger in `docs/milestone-e-public-facing-readiness-ledger.json`, schema-bound by `schemas/ethos-milestone-e-public-facing-readiness-ledger.schema.json`, records current main `6019a97` / tree `f56fde854f6f6e4c4070209329f8c7b12310aa51` as the current-main source-only public beta source binding while retaining package-publication resolution gaps with package publication blocked. The Milestone E prep source-only closeout record in `docs/validation/milestone-e-final-closeout-validation-2026-06-20.md` closes only that current internal prep boundary. The E prep JSON files are schema-bound, but that does not promote any fixture beyond internal source-only planning, does not approve package publication, hosted surfaces, production positioning, public benchmark reports, or public benchmark claims, and does not resolve or soften blockers outside the source-only public beta approval and package prep approval boundaries. The product can demonstrate a narrow parser-backed grounding loop today, but the decision cannot be used as public benchmark credibility.

The public beta current-main refresh prep in `docs/milestone-e-public-beta-current-main-refresh-prep.json`, schema-bound by `schemas/ethos-milestone-e-public-beta-current-main-refresh-prep.schema.json`, records current main `9262b28` / tree `9f18f9e40c57551aef9b0cb2a53641c87207546b` as a current-main refresh candidate only. This public beta current-main refresh prep does not refresh the reviewed source-only public beta source state, change the approved public beta wording, approve package publication, approve public installation, or soften any current public-facing blocker.

The current-main source-only public beta approval in `docs/validation/milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md` records reviewed commit `902c423`, merged main commit `6019a97`, and tree `f56fde854f6f6e4c4070209329f8c7b12310aa51` as the refreshed GitHub source-repository public beta source binding. Package publication remains blocked, public installation remains blocked, hosted surfaces remain blocked, production positioning remains blocked, public benchmark reports remain blocked, public benchmark claims remain blocked, release artifacts remain blocked, and public result wording remains blocked.

The package publication approval resolution plan in `docs/validation/milestone-e-package-publication-approval-resolution-plan-validation-2026-06-21.md` records current source commit `524535a` / tree `0785ffca8423c42e2c4105df7752e290cc88e5c2` as the source state for later exact package-publication decision review. It orders the remaining version, tag, manifest activation, registry-backed assembly, public installation wording, and posture/claims inputs while package publication remains blocked and public installation remains blocked.

The package publication decision input packet in `docs/validation/milestone-e-package-publication-decision-input-packet-validation-2026-06-21.md` records candidate version, tag, source binding, manifest activation, registry-backed assembly, and public installation wording inputs for later review against source commit `54bf70f` / tree `5a197bee718e3b31399563340169e9efd4f1317c`. Package publication remains blocked and public installation remains blocked.

The package publication approval readiness review in `docs/validation/milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md` records the current readiness status against source commit `9054f1c` / tree `3f8cb66249826d67ab6030032c7784a2a4ff411b`. Exact approval decision, signoff, manifest review, assembly evidence, and post-wording gates remain required while package publication remains blocked and public installation remains blocked.

The package publication manifest-activation diff review in `docs/validation/milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md` records the candidate manifest activation diff against source commit `89d24c8` / tree `21b263dca908ef7cc977e7669e40206096eef93e`. Current Cargo manifests remain unchanged, package publication remains blocked, and public installation remains blocked.

The package publication registry-assembly evidence review in `docs/validation/milestone-e-package-publication-registry-assembly-evidence-review-validation-2026-06-21.md` records registry-backed dependent package assembly evidence requirements against source commit `3f0f3ed` / tree `6c748cd6f4a8de7789e42666697d1f25aa99f6f9`. No registry is created, registry-backed assembly is not activated, package publication remains blocked, and public installation remains blocked.

The package publication public installation wording review in `docs/validation/milestone-e-package-publication-public-installation-wording-review-validation-2026-06-21.md` records candidate wording and explicit exclusions against source commit `8b446e3` / tree `385dd7799cf898fc850555ce13d6d74e8ee15196`. The wording is not approved, package publication remains blocked, and public installation remains blocked.

The package publication approval decision template in `docs/validation/milestone-e-package-publication-approval-decision-template-validation-2026-06-21.md` records exact future decider inputs against source commit `66979cc` / tree `58ef15e1cac8ce7df35a7e88da2044e57eb66c10`. No decision is approved, package publication remains blocked, and public installation remains blocked.

The package publication approval decision in `docs/validation/milestone-e-package-publication-approval-decision-validation-2026-06-21.md` rejects the current package-publication request against source commit `fdbd5b7` / tree `4a7bf5cda2c779e41a04c3feb691a12fec1e5c8d` because required activation evidence is absent. Package publication remains blocked, and public installation remains blocked.

The package publication candidate activation evidence in `docs/validation/milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md` validates a temporary non-public package activation workspace against source commit `6cf211c` / tree `ae76bc588b64dc1e8087d9096d52545a3560c2c0`. Source Cargo manifests remain blocked, package publication remains blocked, and public installation remains blocked.

The package publication approval decision refresh in `docs/validation/milestone-e-package-publication-approval-decision-refresh-validation-2026-06-22.md` records that activation evidence is present against source commit `6a91511` / tree `8b150d9aebdc282c358e4552a4d709c3140f41b4`. Manual exact approval remains required; source Cargo manifests remain unchanged, package publication remains blocked, and public installation remains blocked.

The package publication manifest activation applied record in `docs/validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md` records the source package name `ethos-doc-core`, Rust library name `ethos_core`, and workspace dependency activation for review only. `publish = false`, package publication, and public installation remain blocked.

The package publication current registry-equivalent assembly record in `docs/validation/milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md` records non-public assembly evidence for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` against source commit `b48e2f2` / tree `4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3`. Package publication remains blocked, and public installation remains blocked.

The package publication final approval request in `docs/validation/milestone-e-package-publication-final-approval-request-validation-2026-06-22.md` records exact candidate crates, version map, package tag names, source binding, proposed public installation wording, and explicit exclusions for decider review. Package publication remains blocked, and public installation remains blocked.

The package publication final approval decision in `docs/validation/milestone-e-package-publication-final-approval-decision-validation-2026-06-22.md` records decider acceptance of the exact bounded candidate crates, version map, package tag names, source binding, wording, and explicit exclusions. Publish-flag activation remains blocked, package tag creation remains blocked, real-version cargo publish remains blocked, and public installation instructions remain unchanged until later gated activation.

The package publication publish-flag activation request in `docs/validation/milestone-e-package-publication-publish-flag-activation-request-validation-2026-06-22.md` records the exact requested activation diff for the three accepted candidate manifests only. Activation remains blocked, package tag source binding must be refreshed after activation, package tag creation remains blocked, real-version cargo publish remains blocked, and public installation instructions remain unchanged.

The package publication activation applied record in `docs/validation/milestone-e-package-publication-activation-applied-validation-2026-06-22.md` binds the applied manifest activation to source commit `f50f294` / tree `00c3e4df7a7b3b368659650601a2df76b63a2ce8`. The three accepted candidate manifests are activated, non-candidate crates remain blocked, package tag source binding must be refreshed, real-version cargo publish remains blocked, and public installation remains blocked.

The package publication tag binding refresh in `docs/validation/milestone-e-package-publication-tag-binding-refresh-validation-2026-06-22.md` binds the accepted package tag names to activated main commit `421bed8` / tree `aa0d5d31d879540fd0044052dfeb747f12b64204`. Operator evidence remains required, package tag creation remains blocked, registry publication remains blocked, and public installation remains blocked.

The package publication operator preflight in `docs/validation/milestone-e-package-publication-operator-preflight-validation-2026-06-22.md` records manual crates.io owner/account evidence requirements, reserved-name confirmation, dependency order, package tag names, and command order for a later registry action. Manual registry evidence remains required, public installation remains blocked, and registry publication remains blocked.

The package publication manual registry evidence request in `docs/validation/milestone-e-package-publication-manual-registry-evidence-request-validation-2026-06-22.md` records the exact non-secret output packet required from the operator for crates.io owner/account confirmation, reserved-name owner outputs, dry-run outputs, package tag names, and explicit exclusions. Manual registry evidence remains required, public installation remains blocked, and registry publication remains blocked.

The package publication manual registry evidence supplied record in `docs/validation/milestone-e-package-publication-manual-registry-evidence-supplied-validation-2026-06-22.md` captures the supplied non-secret owner/account evidence, reserved-name owner outputs, `ethos-doc-core` dry-run output, expected blocked dependent dry-run outputs, package tag names, and explicit exclusions. Manual registry evidence supplied is recorded, public installation remains blocked, and registry publication remains blocked.

The package publication registry action authorization request in `docs/validation/milestone-e-package-publication-registry-action-authorization-request-validation-2026-06-22.md` provides the exact non-secret authorization packet and command order for later package tag creation and the first registry action. Package tag creation remains blocked, public installation remains blocked, and registry publication remains blocked.

The package publication registry action approval in `docs/validation/milestone-e-package-publication-registry-action-approval-validation-2026-06-22.md` captures exact bounded authorization for the three annotated package tags and first `ethos-doc-core` registry action. Dependent registry actions remain blocked and public installation remains blocked.

The package publication registry action evidence in `docs/validation/milestone-e-package-publication-registry-action-evidence-validation-2026-06-22.md` captures tag evidence, first `ethos-doc-core` registry action evidence, and refreshed dependent dry-run evidence. Dependent registry actions remain blocked and public installation remains blocked.

The package publication dependent registry action approval in `docs/validation/milestone-e-package-publication-dependent-registry-action-approval-validation-2026-06-22.md` authorizes only the dependent `ethos-verify` and `ethos-pdf` registry actions. Public installation remains blocked.

The package publication dependent registry action evidence in `docs/validation/milestone-e-package-publication-dependent-registry-action-evidence-validation-2026-06-22.md` captures completed `ethos-verify` and `ethos-pdf` registry action evidence. Public installation wording remains blocked.

The package publication public installation availability record in `docs/validation/milestone-e-package-publication-public-installation-availability-validation-2026-06-22.md` captures crates.io availability for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.0` and bounds Rust crate installation wording while retaining CLI, wheel, npm, binary, hosted, production, public benchmark, PDFium-build, `ethos-doc`, and `ethos-rag` blockers.

The public evaluation current-state closeout record in `docs/validation/milestone-e-public-evaluation-current-state-closeout-validation-2026-06-22.md` records current main `034881e` / tree `fb089e027641a7d2152d7d1ebd499f45bb1f6a1c` as GitHub source repository plus `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.0` for Rust crate evaluation. Hosted surfaces, production positioning, public benchmark claims, CLI distribution, wheels, npm packages, binaries, project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, and broader public wording remain blocked.

The patch `0.1.1` readiness prep record in `docs/validation/patch-0-1-1-readiness-prep-validation-2026-06-23.md` records candidate onboarding contents after `ethos doctor`, synthetic fixture golden-change guarding, the 2-minute PDF parse quickstart, and improved missing/unusable PDFium guidance landed on `main`. This is a prep record only: it does not approve a release, tag, version bump, package publish, GitHub Release artifact, hosted surface, production positioning, Windows packaged artifact, bundled project-maintained PDFium build, public benchmark report, or public benchmark claim. The current public baseline remains `v0.1.0` until a separate release decision, version update, artifact build, smoke evidence, and operator action are completed.

The patch `0.1.2` readiness prep record in `docs/validation/patch-0-1-2-readiness-prep-validation-2026-06-24.md` records the narrow beta patch candidate boundary after `ethos evidence anchor`, the `evidence_anchor` v1 guard, and professional public README status wording landed on `main`. This is a prep record only: it does not approve a release, tag, version bump, package publish, GitHub Release artifact, hosted surface, production positioning, Windows packaged artifact, bundled project-maintained PDFium build, public benchmark report, or public benchmark claim. The current public install baseline remains `0.1.1` until a separate release decision, version update, artifact build, smoke evidence, registry/GitHub Release evidence, and operator action are completed.

The patch `0.1.2` version activation record in `docs/validation/patch-0-1-2-version-activation-validation-2026-06-24.md` moves the Rust workspace and Python source/package metadata to `0.1.2` for candidate validation only. npm and public install wording remain on the published `0.1.1` baseline until matching `0.1.2` CLI artifacts, registry/GitHub Release evidence, and operator actions are recorded. This activation does not approve a release, tag, package publish, GitHub Release artifact, hosted surface, production positioning, Windows packaged artifact, bundled project-maintained PDFium build, public benchmark report, or public benchmark claim.

The patch `0.1.2` artifact/package evidence record in `docs/validation/patch-0-1-2-artifact-package-evidence-validation-2026-06-24.md` adds a dynamic release-candidate-prep guard for local `0.1.2` Rust crate candidates and the `ethos_pdf-0.1.2-py3-none-any.whl` candidate, and updates draft CLI artifact workflow smoke expectations to `ethos 0.1.2`. The public install baseline remains `0.1.1`, public installation wording remains blocked, registry publication remains blocked, GitHub Release artifact publication remains blocked, and npm vendor refresh remains blocked until separate approval, operator evidence, and closeout records pass.

The patch `0.1.2` draft artifact evidence record in `docs/validation/patch-0-1-2-draft-artifact-evidence-validation-2026-06-24.md` records a green `release.yml` workflow run and downloaded macOS arm64/Linux x64 draft CLI artifact sidecars. Both draft artifact smokes reported `ethos 0.1.2`; the public install baseline remains `0.1.1`, GitHub Release artifact publication remains blocked, registry publication remains blocked, npm vendor refresh remains blocked, and public installation wording remains blocked until separate approval, operator evidence, and closeout records pass.

The patch `0.1.2` artifact publication approval request in `docs/validation/patch-0-1-2-artifact-publication-approval-request-validation-2026-06-24.md` binds the exact macOS arm64/Linux x64 draft CLI artifact names, SHA256 values, source commit, workflow evidence, and requested bounded wording for decider review only. Publication remains blocked, the public install baseline remains `0.1.1`, registry publication remains blocked, npm vendor refresh remains blocked, and public installation wording remains blocked until a separate decision and operator evidence pass.

The patch `0.1.2` artifact publication approval decision in `docs/validation/patch-0-1-2-artifact-publication-approval-decision-validation-2026-06-24.md` accepts only the exact macOS arm64/Linux x64 CLI artifact names, SHA256 values, source binding, workflow evidence, and bounded wording for later operator upload to GitHub Release `v0.1.2`. Upload remains pending, the public install baseline remains `0.1.1`, registry publication remains blocked, npm vendor refresh remains blocked, and public installation wording remains blocked until post-upload closeout or separate approval records pass.

The patch `0.1.2` artifact publication closeout in `docs/validation/patch-0-1-2-artifact-publication-closeout-validation-2026-06-24.md` records GitHub Release `v0.1.2`, the approved tag target, exact macOS arm64/Linux x64 CLI artifact assets, matching checksums, sidecars, and bounded release wording. The public install baseline remains `0.1.1`, registry publication remains blocked, npm vendor refresh remains blocked, npm publication remains blocked, and public installation wording remains blocked until separate lanes pass.

The patch `0.1.2` npm vendor refresh in `docs/validation/patch-0-1-2-npm-vendor-refresh-validation-2026-06-24.md` refreshes the checked-in `@docushell/ethos-pdf@0.1.2` vendor payload from the published GitHub Release `v0.1.2` assets and records local pack/install smoke evidence. npm publication remains blocked, public installation wording remains blocked, registry publication remains blocked, and the public install baseline remains `0.1.1` until separate approval, operator, registry, and wording closeout lanes pass.

| Work item | Current status | Remaining blocker |
| --- | --- | --- |
| PDFium Phase 1 profile | Landed: pinned profile, V8/XFA-disabled state, platform hashes, runtime library hashes, and provenance are recorded | Phase 2 project-maintained builds still block Public Beta |
| PDFium loader/runtime checks | Landed: missing/mismatched version, artifact, and runtime library hashes fail deterministically | Release packaging and operator setup path still need hardening |
| Real PDF backend | Landed for simple born-digital PDFs: page count, quantized spans, worker execution, timeout, page filtering, and fingerprint path exist | Wider corpus coverage, failure fixtures, memory-limit behavior, quirk log, and Gate Zero run are still missing |
| Layout groundwork | Landed: basic paragraph text blocks, fixture-backed alpha heading and flat list-item elements, simple column reading order over quantized spans, explicit alpha heading-confidence values, deterministic below-threshold confidence diagnostics, fixture metadata checks against committed extraction/layout goldens for current read-order and element-type expectations, and alpha text/Markdown export goldens derived from committed layout output | Tables, nested/richer list and heading semantics, broader rotation/quirk handling, and broader confidence dimensions remain future work |
| Layout evaluator scaffold | Landed: deterministic internal evaluator over committed extraction/layout fixture expectations, with heading/list/reading-order/rotation/hyphenation/ligature/font-identity/span-expectation coverage checks, expected page/span-text/font-id checks, expected-spans metadata validation, warning-reference checks, confidence-policy checks, text/Markdown export-golden checks, expectation drift diagnostics, report JSON, Make target, unit coverage, PR CI wiring, and static CI workflow guard coverage | Broader evaluator dimensions remain future work |
| Python surface | Landed: `ethos-pdf==0.1.1` public evaluation wheel wrapping a caller-provided local `ethos` CLI command, with explicit JSON/Markdown/text methods, page selection passthrough, diagnostics passthrough, timeout handling, command failure reporting, and mocked-command unit coverage; it does not bundle the CLI or PDFium | Native binding work and broader API design remain future work |
| Font policy groundwork | Partially landed: substitution table and profile policy are present; substitution-table bytes are pinned by the deterministic profile and checked by schema/example validation; absent bundled fallback assets must remain represented by a null fallback-bundle hash; fixture output uses deterministic substitution IDs, committed embedded-font fixture metadata now binds expected extraction font identity, document schema/font extraction keep emitted font ids inside the deterministic ASCII `embedded:` / `subst:` contract, and CLI font-isolation PDFs are manifest/hash-bound | Bundled fallback asset introduction/hash pinning and broader font/CID validation remain open |
| Schema/example validation | Landed: schemas, examples, deterministic profile, referential integrity, and bbox sanity pass the `jsonschema` validation gate | Contract changes still require explicit versioning and compatibility review |
| Trust-layer implementation | Landed: `ethos verify` quote/value/presence/table-cell checks, explicit quote-containment labeling, normalized equality for value/table-cell checks, stale and unverifiable fingerprint handling, unsupported claim reporting, structured capability limits, native Ethos JSON path, ODL-style adapter path with synthetic table/cell mapping, explicit real OpenDataLoader-style row/cell table grounding, conservative real-style text/child-container alias normalization, pinned real OpenDataLoader 2.4.7 grounded/ungrounded fixtures, foreign fixture manifest hash validation, crop-ref evidence plumbing, stable logical native crop refs, native crop descriptor artifacts, internal `crop_element` source-bound resolver, raw BGRA crop rendering in `ethos-pdf`, CLI/Python source-bound crop descriptor and rendered artifact plumbing for bound native source PDFs, same-host rendered crop repeatability check, rendered-crop run comparison helper, strict citation/config input validation, citation input schema, split-quote fixture coverage, explicit unsupported non-v1 claim reporting, OpenDataLoader-style structure diagnostics for malformed bbox and unknown-page references, verify-alpha case inventory checks, demo fixtures, and a first Milestone D `verify_citations` v1 contract note that binds the current citation-input to verification-report contract without adding a new command or binding surface | Post-D blockers/future work: additional adapter hardening against broader real output shapes, future claim-kind expansion outside the current v1 alpha policy, sandbox/subprocess backend work, Node/MCP/hosted crop surfaces, foreign-adapter crop coordinate hardening, and any cross-platform rendered crop artifact byte-identity requirement; these are not D closeout requirements |
| RAG chunk artifact checks | Landed for current source examples: deterministic command-level fixture/golden output, repeated-run byte identity, schema/example validation, stale reference rejection, and default-chunk exclusion warning-reference rejection | Broader chunk provenance/citation policy and future parser/table integration remain future work |
| Security report artifact checks | Landed for current source examples: source-only `ethos security report`, deterministic output, source/report identity validation, security-warning locator grounding, warning-lane diagnostics, inventory/report parity, summary drift checks, and deterministic warning id checks | Broader security-report generation semantics, debug overlay integration, and future artifact UX remain future work |
| WS-HARNESS readiness | Partially landed: readiness path is green for frozen corpus/hardware and pinned competitors, Gate Zero evidence preflight validates the current `ethos-bench` handoff, and gates fail closed if those records regress | Public-safe comparison report flow, release/package approval, claim-wording approval, and future evidence-refresh workflow still need hardening |
| Determinism workflow | Landed: macOS arm64, Linux x64, and Windows x64 matrix entries run core contract tests; PDFium-backed corpus work stays gated on an explicitly configured pinned runtime; static workflow tests guard the matrix | Windows PDFium runtime provisioning and broader cross-platform corpus validation remain future work |

## PM Rule

Public language may use this exact approved sentence on the current source, Rust crate, Python wheel, npm package, macOS arm64 CLI artifact, and Linux x64 CLI artifact evaluation surfaces: "Ethos is a deterministic document evidence layer for source-grounded verification and citation checking across native Ethos JSON and supported foreign parser outputs. The current beta includes the GitHub source repository, Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.2`, the Python `ethos-pdf` wheel at `0.1.2`, the npm `@docushell/ethos-pdf@0.1.2` package, and GitHub Release `v0.1.2` macOS arm64/Linux x64 CLI artifacts. PDFium-backed commands use caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`." All wording beyond that sentence still requires claim-audit and decider review for the exact surface. Do not describe Ethos as having public benchmark validation, production readiness, broad parser completeness, speed, footprint, parser-quality, or table-quality claims. Hosted surfaces, Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`, and `ethos-rag` remain blocked. Internal parser work should proceed only when it supports accepted evidence paths or the trust layer; the product-differentiating path remains verification and grounding first, with parser expansion serving that path.
