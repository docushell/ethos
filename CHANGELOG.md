# Changelog

## Unreleased

- Recompute source and citation fixture hashes when validating v0.5 performance evidence.

- Add independent validation for v0.5 internal performance evidence and threshold derivations.

- Make Evidence Handle Bridge state projection validate verification-report shape, status, and metadata fail-closed.

- Reject empty v1 Evidence Handle Bridge contexts before hydration or state projection.

- Reject unsafe URI-like and traversal-like HTML proof-report crop prefixes before link rendering.

- Add an operator-only runner for v0.5 cold and batch verification timing evidence.

- Activate v0.5.0 core Rust and Python candidate metadata in lockstep while retaining the
  published v0.4.0 npm payload and public install wording until the frozen-A payload refresh.
- Reconcile stale public install wording to the closed v0.4.0 release baseline.
- Validate `ethos-full` archive, checksum, and inventory binding before target-host extraction.

- verify: add black-box coverage for `verify-batch` canonical per-line equivalence, ordering,
  repeat determinism, aggregate exit semantics, and invalid-input atomicity.
- packaging: promote the deterministic `ethos-full` builder from ADR proposal evidence to a
  v0.5 release candidate pending required target smoke and release gates.
- examples: add a deterministic, model-free Evidence Handle Bridge walkthrough bound to a
  recorded verification report.
- python: add Evidence Handle Bridge v1 trusted contexts and v2 structured model citations with
  deterministic, fail-closed hydration while preserving citation-emission v1.
- npm: generate Evidence Handle Bridge context and model-output declarations, and add
  fail-closed evidence-state projection for verification-report-bound application views.
- report: add deterministic, self-contained HTML proof reports with supported-schema checks,
  escaped report content, and fail-closed crop-root validation.
- verify: add buffered, atomic `verify-batch` NDJSON verification against one validated source,
  with canonical per-line reports and aggregate ungrounded exit semantics.
- release: reconcile the published v0.4.0 baseline, accept the bounded v0.5.0
  `ethos-full` exception, and establish the v0.5.0 four-deliverable release scope.

## 0.4.0 - 2026-07-21

- boundary-exception: refresh the v0.4.0 npm vendor payload from the final stable, byte-identical
  macOS arm64/Linux x64 CLI archives after removing the manifest checksum self-reference.
- release: remove the CLI's compile-time npm vendor-manifest inclusion so the final CLI artifact
  and npm vendor checksums are not self-referential.
- boundary-exception: refresh the v0.4.0 npm vendor payload from the final byte-identical
  macOS arm64/Linux x64 CLI archive builds without rebuilding those publication artifacts.
- ci: keep the verification Action checksum-pinned to the published v0.3.0 CLI while npm
  candidate vendor metadata advances to v0.4.0.
- boundary-exception: refresh the v0.4.0 npm vendor manifest and macOS arm64/Linux x64 binaries
  from the byte-identical caller-provided-PDFium CLI candidates; keep public installation wording
  on the actually published 0.3.0 package until publication closeout.
- boundary-exception: normalize CLI release archive metadata and gzip headers so repeated macOS arm64 and Linux
  x64 candidate builds are byte-identical before npm vendoring or publication.
- build: remove unused Cargo Deny license allowances and document the unavoidable transitive
  `wit-bindgen` duplicate so release hygiene runs without warnings.
- boundary-exception: remove completed release and milestone records together with their retired
  validation guards; preserve the compact current-release closeout summary required by release-state validation.
- boundary-exception: retire the completed temporary next-implementation ledger and kickoff
  prompt, move v0.4.0 publication tracking wholly into the accepted release-prep/closeout lane,
  and remove active-plan wording from the validation index and accepted PDFium install record
  while preserving their historical evidence IDs and conclusions.
- release: begin v0.4.0 post-merge finalization, reconcile the dropped MCP and deliberately
  skipped Windows publication boundaries, and record approved bounded release-note wording
  without changing currently approved public install claims.
- planning: drop the remaining P2 NIP-2, NIP-8, and NIP-9 workstreams from the current
  implementation plan by decider decision; retain them only as unapproved candidates requiring
  fresh scope and priority in a future release plan.
- ci: close NIP-5.3 and NIP-6.1–6.2 against green Windows x64 build/runtime smoke,
  macOS/Linux/Windows verification determinism, and released-CLI Action dogfood evidence while
  retaining the separate public Windows artifact and Action publication boundaries.
- ci: bind registry-facing install checks to the published release-state versions rather than
  ahead-of-publication candidate metadata, and make the DocuShell source binding externally
  verifiable without treating its commit as an Ethos repository object; remove the accepted
  DocuShell integration from the generated current-release blocker source of truth.
- benchmark: accept merged NIP-3.3 full comparison evidence at `ethos-bench` merge `5945fce` and
  the complete NIP-3.4 internal claim-audit packet at merge `9287671`, closing the internal trust
  benchmark workstream while keeping every public comparative claim gated.
- benchmark: prepare NIP-3.3's source/binary-bound Ethos 0.4.0 baseline and deterministic internal
  comparison covering confusion matrices, precision/recall, cost per 1,000 citations, and
  descriptive latency variance while explicitly supporting no public or cross-system speed claim.
- planning: accept merged NIP-3.2 sibling evidence under the current review-plus-local-validation
  process, explicitly defer `ethos-bench` workflows outside the Ethos critical path, and activate
  the full NIP-3.3 comparison report as the next P0 task.
- corrective-audit: reopen incomplete NIP-3 benchmark and NIP-6 remote-CI ledger rows, reconcile
  candidate/public version authority and governance wording, distinguish released-CLI Action
  dogfood from candidate verification, and keep the quarantined MCP prototype outside the active
  implementation lane.
- ci: dogfood the in-repository verification Action against the README grounded and fabricated
  fixtures, asserting both expected outcomes so allowed failure cannot hide a regression.
- integration: close NIP-1's DocuShell first-consumer lane with accepted source bindings, real-PDF
  acceptance, complete friction dispositions, and no public wording changes.
- ci: add an in-repository, checksum-pinned Ethos verification Action with deterministic
  pull-request annotations and fail-closed exit handling.
- release: activate v0.4.0 source/package metadata and complete the Release Lane v2 pilot
  preflight while keeping publication, public wording, and Windows artifact gates explicit.
- benchmark: record the NIP-3.4 internal claim-audit packet for decider review without changing
  approved public claim strings.
- benchmark: record NIP-3.3's deterministic internal trust-judge report and retain the publication
  block pending the NIP-3.4 claim-audit packet.
- benchmark: complete NIP-3.2's dated two-model, five-run LLM citation-judge study with 200
  schema-valid live records, cost/latency capture, and an internal-only result pending report
  generation and claim audit.
- benchmark: add NIP-3.1's deterministic 20-document, 200-check synthetic trust corpus,
  labeling guide, verifier label harness, and explicit pending human-review gate.
- distribution: add NIP-5.3 deterministic Windows x64 verify-only draft packaging, bundled
  fixtures, cross-target compilation, and fail-closed no-PDFium smoke coverage.
- boundary-exception: add the non-publishable NIP-5.2 ADR-0015 opt-in `ethos-full` proposal with
  deterministic, fail-closed macOS arm64/Linux x64 candidate evidence and complete PDFium
  notices while retaining the caller-provided release posture pending decider acceptance.
- install: make NIP-5.1's caller-provided PDFium path executable and sha256-checked through
  `ethos doctor`, aligned Python/npm guidance, and a copy-paste Linux x64 consumer stage.
- npm: add NIP-4.5 schema-generated verification-report, citation-emission, and app
  answer-release TypeScript declarations to `@docushell/ethos-pdf`, with conditional-contract
  projection, strict consumer compilation, and double-run byte-identical generation tests.
- release: reclassify the accumulated next-release train as v0.4.0, replace the obsolete narrow
  v0.3.1 prep with a scope-honest Release Lane v2 pilot, and keep the P2-gated MCP prototype
  explicitly excluded from activation and publication.
- examples: add NIP-4.3 resolvably pinned, model-free LangChain and LlamaIndex
  retrieval-to-verification walkthroughs with exit-1 preservation and double-run artifact
  checks.
- python: add NIP-4.2 dependency-free LangChain/LlamaIndex citation-emission helpers with strict
  retrieval metadata, fail-closed source-vocabulary hydration, and byte-stable JSON output.
- contracts: freeze NIP-4.1 citation-emission v1 as an independently versioned, parser-neutral
  model/callback schema with fail-closed hydration fixtures and double-run verification-report
  determinism coverage.
- integration: close NIP-1.6 after auditing and dispositioning all eight DocuShell integration
  friction entries gathered across NIP-1.1–1.5, while keeping unresolved Ethos product gaps
  explicitly open against their owning roadmap tasks.
- integration: complete NIP-1.5 with DocuShell's worker-only native PDF crop projection,
  deterministic source-bound crop bundles, public artifact routing, fail-closed PDFium handling,
  and rendered citation-region inspection in Evidence Chat.
- integration: complete NIP-1.4 with DocuShell's fail-closed answer-release gate, v1.1
  `claim_support` policy, deterministic contract-fixture coverage, and explicit review/rejection
  states above canonical citation grounding.
- integration: complete NIP-1.3 with DocuShell's worker-only OpenDataLoader citation-verification lane, stored canonical reports, deterministic citation emission, preserved exit-1 reports, and fail-closed verifier errors.
- integration: complete NIP-1.2 by sha256-pinning the public v0.3.0 Linux x64 CLI and caller-provided PDFium in DocuShell's worker-only image, with deterministic offline install and fail-closed checksum/platform tests.
- planning: add `NEXT_IMPLEMENTATION_PLAN.md` (NIP-1), the canonical next-steps plan covering
  DocuShell first-consumer integration, the trust benchmark study, citation emission adapters,
  install-friction work, the CI Action, and governance right-sizing, with a task-level progress
  ledger; rework `AGENTS.md` so implementing agents read the plan first. This plan approves
  engineering work and internal evidence only — public wording, benchmark claims, hosted
  surfaces, and production positioning remain in their existing approval lanes.
- planning: revise NIP-1 to v1.1 by decider decision — deprioritize `ethos-mcp` (NIP-2) to P2,
  promote citation emission (NIP-4) and install-friction (NIP-5) to P0, and switch the execution
  model to AI-agent implementation with human review/decider/operator gates, replacing week-based
  pacing with agent-day estimates in the progress ledger.
- docs: add `docs/integrations/docushell.md` (NIP-1.1), the first-consumer integration contract
  binding DocuShell to public Ethos surfaces only, with version pins, compatibility promises,
  and worker-lane rules; add `docs/integrations/docushell-friction-log.md` (NIP-1.6) seeded with
  the first three dispositioned friction entries (TypeScript report types, PDFium image wiring,
  CLI vendoring bookkeeping).
- governance: add `docs/release-lane-v2.md` (NIP-7.1, accepted 2026-07-19): routine release
  trains produce exactly one prep doc and one closeout record; the full multi-record v1 lane is
  retained for first-of-class surfaces only; a smoothness rule limits human gates across the
  whole pipeline to PR review, registry publish, and public-wording changes.
- docs: rewrite `CONTRIBUTING.md` (NIP-7.3) as the single idea-to-release process page — a
  five-step first-PR quickstart, a three-requirement PR bar (tests, CHANGELOG line, DCO
  sign-off), project invariants as a CI-enforced reference table, and a maintainer release
  summary — so external contributors and AI agents can contribute without reading the internal
  governance apparatus.
- docs: add a "catch a fabricated citation in 60 seconds" README lead demo over checked-in JSON
  fixtures (no PDFium required), preserving every existing public-boundary claim string and
  adding no new capability, benchmark, parser-quality, or production claims.
- tooling: add `scripts/fetch-pdfium.sh`, an optional operator helper that downloads only the
  exact pinned `bblanchon/pdfium-binaries` release recorded in `docs/pdfium-profile.md`, verifies
  the recorded archive and runtime-library sha256 values fail-closed, and prints the
  `ETHOS_PDFIUM_LIBRARY_PATH` export line; the `ethos` binary still never downloads or installs
  libraries, and PDFium remains caller-provided and unbundled.
- decisions: record ADR-0013 (caller-provided PDFium beta posture) reconciling the shipped
  v0.3.0 no-PDFium-distribution posture with ADR-0002's phase model; re-scope the Phase 2
  blocker to bundled, Windows-with-PDFium, and hosted surfaces; add an ADR-0001 addendum
  confirming the reduced-staff schedule and clarifying that the npm binary distribution package
  is not the gated "Node beta" surface.
- boundary-exception: correct v0.3.0 final GitHub Release notes and latest-release intent, add a
  live metadata checker for the latest pointer, body, status, and asset set, and preserve the exact
  approved draft-inventory provenance without replacing published assets or widening release scope.
- boundary-exception: harden next-release npm binary provenance, registry-package wording,
  parser-neutral dependency enforcement, determinism CI, and release-governance checks without
  changing Ethos verification semantics or approving DocuShell integration, hosted surfaces,
  production positioning, Windows artifacts, bundled PDFium, or public benchmark claims.
- boundary-exception: close existing v0.3.0 GitHub Release tag evidence without creating,
  moving, deleting, or replacing tags while keeping additional release tags or release targets,
  hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`, and
  DocuShell integration blocked pending separate lanes.
- boundary-exception: close exact v0.3.0 package tag creation with remote tag evidence while
  keeping additional release tags or release targets, hosted, production, Windows, bundled PDFium,
  benchmark, `ethos-doc`, `ethos-rag`, and DocuShell integration blocked pending separate lanes.
- boundary-exception: approve exact v0.3.0 package tag creation for later operator tag creation
  while keeping actual package tag creation, additional release tags or release targets, hosted,
  production, Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`, and DocuShell
  integration blocked pending operator action and closeout lanes.
- boundary-exception: request decider review for exact v0.3.0 package tags while keeping package
  tag creation, additional release tags or release targets, hosted, production, Windows, bundled
  PDFium, benchmark, `ethos-doc`, `ethos-rag`, and DocuShell integration blocked pending separate
  lanes.
- boundary-exception: close exact public `0.3.0` install wording in README and public-boundary
  claims across live Rust, Python, npm, and GitHub Release evaluation surfaces while keeping
  release/package tags, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`,
  `ethos-rag`, and DocuShell integration blocked pending separate lanes.
- boundary-exception: approve exact public `0.3.0` install wording across live Rust, Python, npm,
  and GitHub Release evaluation surfaces while keeping README/public-boundary closeout, tags,
  hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`, and DocuShell
  integration blocked until the bounded closeout record passes.
- boundary-exception: request decider review for exact public `0.3.0` install wording across
  live Rust, Python, npm, and GitHub Release evaluation surfaces while keeping public docs,
  release/package tags, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`,
  `ethos-rag`, and DocuShell integration blocked pending a later decision and closeout.
- boundary-exception: close exact `@docushell/ethos-pdf@0.3.0` npm publication with live registry
  evidence while keeping public install wording, release/package tags, hosted, production,
  Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`, and DocuShell integration blocked
  pending separate lanes.
- boundary-exception: approve exact `@docushell/ethos-pdf@0.3.0` npm publication operator action
  while keeping actual `npm publish`, public install wording, registry closeout,
  release/package tags, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`,
  `ethos-rag`, and DocuShell integration blocked pending operator action, registry smoke, and
  closeout lanes.
- boundary-exception: request decider review for exact `@docushell/ethos-pdf@0.3.0` npm
  publication inputs while keeping `npm publish`, public install wording, release/package tags,
  hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`, and
  DocuShell integration blocked pending a later approval decision, operator action, registry
  smoke, and closeout lanes.
- boundary-exception: refresh the `@docushell/ethos-pdf@0.3.0` npm source package candidate from
  published v0.3.0 GitHub Release CLI artifacts while keeping npm publish, public install wording,
  package tags, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`,
  and DocuShell integration blocked pending separate lanes.
- boundary-exception: close exact v0.3.0 macOS arm64 and Linux x64 GitHub Release CLI artifact
  publication with published asset evidence while keeping npm vendor refresh, npm publish, public
  install wording, package tags, hosted, production, Windows, bundled PDFium, benchmark,
  `ethos-doc`, `ethos-rag`, and DocuShell integration blocked pending separate lanes.
- boundary-exception: approve exact v0.3.0 macOS arm64 and Linux x64 GitHub Release CLI artifact
  publication for later operator upload while keeping upload, npm vendor refresh, npm publish,
  public install wording, package tags, hosted, production, Windows, bundled PDFium, benchmark,
  `ethos-doc`, `ethos-rag`, and DocuShell integration blocked pending operator action and
  closeout lanes.
- boundary-exception: request decider review for exact v0.3.0 macOS arm64 and Linux x64 GitHub
  Release CLI artifact publication inputs while keeping upload, npm vendor refresh, npm publish,
  public install wording, release/package tags, hosted, production, Windows, bundled PDFium,
  benchmark, `ethos-doc`, `ethos-rag`, and DocuShell integration blocked pending later approval,
  operator action, and closeout lanes.
- boundary-exception: record v0.3.0 macOS arm64 and Linux x64 draft CLI artifact evidence while
  keeping GitHub Release artifact upload, npm vendor refresh, npm publish, public install wording,
  release/package tags, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`,
  `ethos-rag`, and DocuShell integration blocked pending later evidence, approval, and closeout
  lanes.
- boundary-exception: align the v0.3.0 draft CLI artifact workflow smoke expectation to
  `ethos 0.3.0` and record CLI artifact evidence prep while keeping GitHub Release artifact
  upload, npm vendor refresh, npm publish, public install wording, release/package tags, hosted,
  production, Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`, and DocuShell
  integration blocked pending later evidence and approval lanes.
- boundary-exception: close v0.3.0 Rust crates.io and Python PyPI publication with exact live
  registry evidence while keeping GitHub Release artifact upload, npm publish, public install
  wording, release/package tags, hosted, production, Windows, bundled PDFium, benchmark,
  `ethos-doc`, `ethos-rag`, and DocuShell integration blocked pending later evidence lanes.
- boundary-exception: record v0.3.0 Rust crates.io and PyPI publication approval decision for
  later operator action while keeping actual GitHub Release artifact upload, npm publish,
  installable `0.3.0` wording, release/package tags, hosted, production, Windows, bundled PDFium,
  benchmark, `ethos-doc`, `ethos-rag`, and DocuShell integration blocked pending later evidence
  and closeout records.
- boundary-exception: request decider review for exact v0.3.0 Rust crates.io publication inputs
  and exact v0.3.0 deterministic PyPI wheel publication inputs while keeping `cargo publish`,
  PyPI upload, npm publish, GitHub Release artifact publication, release/package tags, installable
  `0.3.0` wording, npm alignment, hosted, production, Windows, bundled PDFium, benchmark,
  `ethos-doc`, `ethos-rag`, and DocuShell integration blocked.
- boundary-exception: record v0.3.0 Rust package candidate and Python wheel evidence while keeping
  `cargo publish`, PyPI upload, npm publish, GitHub Release artifact publication, release/package
  tags, installable `0.3.0` wording, npm alignment, hosted, production, Windows, bundled PDFium,
  benchmark, `ethos-doc`, `ethos-rag`, and DocuShell integration blocked.
- boundary-exception: harden v0.3.0 release-candidate CI guards and document the current release
  workflow artifact smoke pin while keeping `cargo publish`, PyPI upload, npm publish, GitHub
  Release artifact publication, release/package tags, installable `0.3.0` wording, hosted,
  production, Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`, and DocuShell
  integration blocked.
- boundary-exception: activate v0.3.0 release-candidate source versions for Rust workspace and
  Python package metadata while keeping npm at `0.2.1` and keeping `cargo publish`, PyPI upload,
  npm publish, GitHub Release artifact publication, release/package tags, installable `0.3.0`
  wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, `ethos-rag`, and
  DocuShell integration blocked.
- boundary-exception: record decider approval for v0.3.0 app-answer-release release-candidate
  source activation while keeping package publication, artifact publication, tag creation, npm
  alignment, installable `0.3.0` wording, hosted, production, Windows, bundled PDFium, benchmark,
  `ethos-doc`, `ethos-rag`, and DocuShell integration blocked pending separate evidence records.
- boundary-exception: record app-answer-release contract release-prep packet for decider review
  while keeping version bump, package publication, tag creation, artifact publication,
  installable `0.3.0` wording, npm publication, hosted, production, Windows, bundled PDFium,
  benchmark, `ethos-doc`, `ethos-rag`, and DocuShell integration blocked.
- boundary-exception: record passing `ethos-doc-core 0.2.0` locked cargo publish dry-run evidence
  while keeping actual `cargo publish`, dependent-crate dry-runs, PyPI upload, npm publish, GitHub
  Release artifact publication, release/package tags, installable `0.2.0` wording, hosted,
  production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: record v0.2.0 package/build evidence for the Python wheel, local macOS arm64
  draft CLI artifact, and npm package metadata while keeping npm artifact candidacy blocked on
  stale vendored `ethos 0.1.2` binaries and keeping publication, artifact upload, tags, installable
  `0.2.0` wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and
  `ethos-rag` surfaces blocked.
- boundary-exception: activate v0.2.0 release-candidate source versions for Rust, Python, and npm
  package metadata while keeping `cargo publish`, PyPI upload, npm publish, GitHub Release
  artifact publication, release/package tags, installable `0.2.0` wording, hosted, production,
  Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: record decider approval for v0.2.0 release-candidate activation while
  keeping package publication, artifact publication, tag creation, installable `0.2.0` wording,
  hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces
  blocked pending separate evidence records.
- boundary-exception: add v0.2.0 source-preparation docs and gates for JSON verification and
  evidence anchoring, the v0.2.x compatibility policy, and the bring-your-own-parser tutorial; no
  `0.2.0` publication, package tag, GitHub Release artifact, or public install wording is approved
  by this entry.
- python: add `EthosCli.verify(...)`, `EthosCli.anchor(...)`, top-level `verify(...)`, and
  top-level `anchor(...)` as caller-provided CLI wrapper calls; verify exit `1` with a JSON report
  returns a negative result instead of raising.
- boundary-exception: close patch `0.1.2` current status for the approved evaluation surfaces; no hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, or `ethos-rag` boundary change.
- boundary-exception: close patch `0.1.2` package tag creation with exact remote tag evidence while retaining hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` blockers.
- boundary-exception: record decider approval for exact patch `0.1.2` package tag creation while keeping actual tag creation as a later operator action and retaining hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` blockers.
- boundary-exception: request decider review for exact patch `0.1.2` package tag creation while keeping tag creation, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked pending a separate approval decision.
- boundary-exception: close patch `0.1.2` Python public install wording for published PyPI wheel `ethos-pdf==0.1.2` while keeping package tag creation, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: close patch `0.1.2` Python PyPI publication with exact registry evidence for `ethos-pdf==0.1.2` while keeping Python public install wording, package tag creation, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: record decider approval for bounded later deterministic patch `0.1.2` Python PyPI wheel publication while keeping actual upload, Python public install wording, package tag creation, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: request decider review for exact deterministic patch `0.1.2` Python PyPI wheel publication while keeping PyPI upload, Python public install wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: close patch `0.1.2` Rust public install wording for published crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` while keeping PyPI publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: close patch `0.1.2` crates.io publication for Rust crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` while keeping Rust public install wording, PyPI publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: record decider approval for bounded later crates.io publication of patch `0.1.2` Rust crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` while keeping actual operator publication, package tag creation, Rust public install wording, PyPI publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: request decider review for exact patch `0.1.2` Rust crates.io publication of `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` while keeping `cargo publish`, package tag creation, Rust public install wording, PyPI publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: close patch `0.1.2` public install wording for the published npm package and GitHub Release CLI artifacts while keeping Rust crates and Python wheel install wording on `0.1.1`, and retaining hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` blockers.
- boundary-exception: close patch `0.1.2` npm publication with exact registry evidence for `@docushell/ethos-pdf@0.1.2` while keeping public install wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: record patch `0.1.2` npm publication blocker after an approved `@docushell/ethos-pdf@0.1.2` publish attempt failed with npm `E404`; retry, registry closeout, public install wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces remain blocked.
- boundary-exception: approve exact patch `0.1.2` npm publication decision for later operator publish of `@docushell/ethos-pdf@0.1.2` while keeping publish execution, public install wording, registry closeout, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: request decider review for exact patch `0.1.2` npm publication of `@docushell/ethos-pdf@0.1.2` while keeping publish, public install wording, registry closeout, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: refresh the `@docushell/ethos-pdf@0.1.2` npm vendor payload from published patch `0.1.2` GitHub Release CLI artifacts while keeping npm publication, public install wording, registry publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: close exact patch `0.1.2` macOS arm64 and Linux x64 GitHub Release CLI artifact publication while keeping registry, npm vendor refresh, public install wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked until separate lanes pass.
- boundary-exception: approve exact patch `0.1.2` macOS arm64 and Linux x64 GitHub Release CLI artifact publication for later operator upload while keeping upload, registry, npm vendor refresh, public install wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked until separate closeout or approval records pass.
- boundary-exception: request decider review for exact patch `0.1.2` macOS arm64 and Linux x64 GitHub Release CLI artifact publication while keeping publication, registry, npm vendor refresh, public install wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: record patch `0.1.2` draft CLI artifact evidence for macOS arm64 and Linux x64 while keeping GitHub Release publication, registry publication, npm vendor refresh, public install wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: record patch `0.1.2` artifact/package evidence prep and update draft CLI artifact smoke expectations to `ethos 0.1.2` while keeping npm, public install wording, registry publication, GitHub Release publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` surfaces blocked.
- boundary-exception: activate Rust workspace and Python source/package metadata for patch `0.1.2` candidate validation while keeping npm and public install wording on the published `0.1.1` baseline; no release, tag, package publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, or `ethos-rag` boundary change.
- boundary-exception: record narrow patch `0.1.2` readiness prep and professional public README beta wording while retaining `0.1.1` install baselines; no release, tag, package publication, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, or `ethos-rag` boundary change.
- boundary-exception: add an `evidence_anchor` v1 guard target, CI guard step, and schema-bound inventory for the merged source-only command; no hosted, production, Windows, bundled PDFium, benchmark, parser-quality, table-quality, or release-posture boundary change.
- boundary-exception: add source-only `ethos evidence anchor` schema and CLI surface for deterministic evidence refs; no hosted, production, Windows, bundled PDFium, benchmark, parser-quality, table-quality, or release-posture boundary change.
- boundary-exception: refresh patch `0.1.1` execution status for published evaluation surfaces while retaining hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` blockers.
- boundary-exception: document bounded patch `0.1.1` public install paths for published evaluation surfaces while retaining hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, and `ethos-rag` blockers.
- boundary-exception: close patch `0.1.1` Python PyPI publication with exact registry evidence; no public install wording, hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, or `ethos-rag` boundary change.
- boundary-exception: approve exact patch `0.1.1` deterministic Python PyPI wheel publication decision for later operator upload; no PyPI upload or support-boundary change.
- boundary-exception: request exact patch `0.1.1` deterministic Python PyPI wheel approval for decider review; no PyPI upload or support-boundary change.
- boundary-exception: record patch `0.1.1` Python wheel reproducibility blocker after pre-upload hash mismatch; no PyPI upload or support-boundary change.
- boundary-exception: approve exact patch `0.1.1` Python PyPI wheel publication decision for later operator upload; no PyPI upload or support-boundary change.
- boundary-exception: request exact patch `0.1.1` Python PyPI wheel publication approval for decider review; no PyPI upload or support-boundary change.
- boundary-exception: close patch `0.1.1` Rust crates.io publication with exact registry evidence; no public installation wording or support-boundary change.
- boundary-exception: approve exact patch `0.1.1` Rust crates.io publication decision for later operator publish; no `cargo publish` or support-boundary change.
- boundary-exception: request exact patch `0.1.1` Rust crates.io publication approval for decider review; no `cargo publish` or support-boundary change.
- boundary-exception: close patch `0.1.1` npm publication with exact registry evidence; no hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, or `ethos-rag` boundary change.
- boundary-exception: approve exact patch `0.1.1` npm publication decision for later operator publish; no npm publish or support-boundary change.
- boundary-exception: request patch `0.1.1` npm publication approval for exact refreshed package candidate; no npm publish or support-boundary change.
- boundary-exception: refresh patch `0.1.1` npm vendor payload from published CLI artifacts; no npm publication or support-boundary change.
- boundary-exception: close patch `0.1.1` CLI artifact publication with exact GitHub Release evidence; no npm vendor refresh, npm publication, or support-boundary change.
- boundary-exception: approve exact patch `0.1.1` CLI artifact publication decision for later operator upload; no upload, npm vendor refresh, npm publication, or support-boundary change.
- boundary-exception: request patch `0.1.1` artifact publication approval for exact evidenced CLI assets; no publication, npm vendor refresh, npm publication, or support-boundary change.
- boundary-exception: record patch `0.1.1` draft artifact evidence for decider review; no GitHub Release publication, npm vendor refresh, npm publication, or support-boundary change.
- boundary-exception: clarify patch `0.1.1` artifact and npm vendor refresh prep in operator docs; no artifact publication, package publication, or support-boundary change.
- boundary-exception: prepare patch `0.1.1` workspace, Python, npm, CLI, and public install/version surfaces for review; no new hosted, production, Windows, bundled PDFium, benchmark, `ethos-doc`, or `ethos-rag` boundary opens.
- boundary-exception: add patch `0.1.1` readiness-prep record for review only; no version bump, release approval, artifact approval, package publication, or support-boundary change.
- process-follow-up: record patch `0.1.1` readiness prep contents and retained blockers without approving release action or changing versions.
- process-follow-up: keep validation-record integrity from treating decimal workflow run IDs as git refs.
- cli: point missing or unusable PDFium errors to `ethos doctor`, `ethos doctor --require-pdfium`, and the manual setup doc without changing exit codes.
- docs: add a bounded 2-minute PDF parse quickstart using the synthetic born-digital fixture and `ethos doctor --require-pdfium`.
- boundary-exception: add `ethos doctor` docs pointer for caller-provided PDFium diagnostics; no PDFium posture or support-boundary change.
- process-follow-up: include synthetic fixture stage goldens in the light-lane golden-change rationale guard; no parser output change.
- boundary-exception: prune redundant Milestone E command-index, record-index, source-head, and guard-sequence checks from routine prep and CI after light-check absorbed generic validation.
- boundary-exception: pilot centralizes public boundary wording and adds local light-lane gates; no release surface or support boundary changes.
- process-follow-up: add npm/crate/pyproject boundary-claim surfaces and align golden detection with export fixtures after the pilot lands.
