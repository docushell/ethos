# Ethos v0.4.0 Release Preparation

Status: **closed.** GitHub Release `v0.4.0` was published on 2026-07-21 from source commit
`e73477e427d2384bdb3b6b913578411325d3d107` (annotated tag object
`6041b2ed5617f923e5d226f1f69bb184d70d5fce`). The final macOS arm64 and Linux x64 caller-provided
PDFium archives and their checksum, inventory, and smoke sidecars are recorded in
`docs/validation/v0-4-0-release-closeout-summary.md`. Windows and `ethos-full` were skipped;
neither is a published v0.4.0 surface.

The release scope may be amended before tagging only through an explicitly scoped, reviewed PR.
Any implementation change invalidates earlier final-artifact hashes and requires fresh full CI,
release-artifact, determinism, and release-wording review on the resulting `main`. Feature work is
not tracked in a separate implementation ledger.

Canonical preparation sentence:

> v0.4.0 prepares the accumulated verification-hardening, report-contract, citation-emission,
> framework-example, integration, and install-adoption work as one minor release train while
> preserving Ethos's citation-grounding boundary and caller-provided PDFium posture.

This is an internal release-preparation description, not approved public wording. It does not
approve registry publication, tags, GitHub Release edits, hosted surfaces, production
positioning, benchmark claims, or changes to `README.md` / `docs/public-boundary-claims.json`.

## Included Scope

- Verification hardening over `GroundingSource`: configurable claim kinds, matching,
  staleness, and resource limits; explicit capability downgrades; deterministic proof summaries
  and claim-support labels; and corresponding CLI/report behavior.
- Additive `1.1.0` verification-config, verification-report, evidence-anchor request/report,
  and application answer-release contracts. The `1.0.0` forms remain accepted where their
  contracts permit; compatibility and migration behavior must remain fixture-backed.
- Citation-emission contract `1.0.0`, dependency-free Python LangChain/LlamaIndex emission
  helpers, and model-free framework walkthroughs, including
  fail-closed hydration and double-run byte-identical artifact checks.
- DocuShell first-consumer integration contracts, friction findings, and accepted closeout. The
  private DocuShell implementation remains versioned and validated in its own
  repository; this release does not publish DocuShell or make public adoption claims about it.
- Adoption and operator tooling originally prepared for the abandoned v0.3.1 patch scope:
  the README fixture demo, caller-run pinned PDFium fetch helper, ADR-0013, and related decision
  amendments. PDFium remains caller-provided and is never downloaded automatically by Ethos.
- Release Lane v2 governance and contributor guidance, with this document serving as the one
  prep note for the v0.4.0 train.

## Carried but Not Activated as a Release Surface

The source tree contains an unpublished `packages/npm/ethos-mcp` prototype inherited from work
that predates the current release scope. The MCP surface was deferred by the 2026-07-20 decider
decision and requires fresh scope and priority in a future release plan.
The prototype is therefore excluded from v0.4.0 package publication, release claims, and release
validation. Keeping its commits in the source tree does not activate or approve the surface.

The source tree also contains the Proposed ADR-0015 and its deterministic `ethos-full` candidate
builder/evidence. The proposal does not activate bundled PDFium: no `ethos-full` archive enters
the v0.4.0 artifact set unless the decider accepts the ADR and this prep scope is updated in a
reviewed change.

The verify-only Windows x64 implementation and draft workflow remain in source, but the Windows
package is skipped as a v0.4.0 publication surface. Its `windows-latest` double-build,
target-runtime smoke, and cross-platform determinism checks passed, completing the implementation
task. Public Windows packaging remains a separate first-of-class release decision under Release
Lane v1 and was not approved for this train. The v0.4.0 closeout must list Windows as skipped.

The release-diff review confirmed that no build, workspace, packaging, or documentation path
accidentally presents this prototype as shipped.

## Explicit Non-Scope

- `ethos-mcp` activation or npm publication; any `crates/ethos-mcp` implementation;
- additional version or lockstep package-metadata changes outside a reviewed release step;
- crates.io, PyPI, npm, tag, or GitHub Release operator actions;
- public wording changes or public benchmark results and comparative claims;
- hosted or network-served surfaces, production positioning, or a WASM playground;
- bundled/project-maintained PDFium distribution and Windows-with-PDFium artifacts;
- `ethos-rag`, native OCR, or scanned-document support claims;
- trust-benchmark publication and CI Action Marketplace publication;
- any silent weakening of verification, capability, determinism, or licensing guardrails.

## Release Gates

### 1. Scope and compatibility

- [x] Reviewed the complete `main...dev/v0-4-0` diff against this included/non-scope inventory.
- [x] Confirmed report/config/evidence `1.0.0` compatibility and `1.1.0` migration fixtures.
- [x] Confirmed `ethos-verify` depends only on the feature-limited `ethos-core`
      `GroundingSource`/verification types, not parser or PDF internals.
- [x] Confirmed `packages/npm/ethos-mcp` is absent from the Rust workspace, release workflow,
      and v0.4.0 publication commands; its metadata remains at `0.3.0`.
- [x] Reviewed the friction log: FR-1–FR-7 and FR-9–FR-10 are resolved; FR-8 is explicitly
      carried as a future parser-aware crop-projection task, with the current mapping fail-closed.

### 2. Validation

- [x] `cargo build --locked --workspace`
- [x] `cargo test --locked --workspace`
- [x] `make verify-alpha`
- [x] `.github/scripts/claims_gate.py` and `.github/scripts/public_boundary_claims_gate.py`
- [x] Citation-emission and pinned framework-example offline/double-run tests.
- [x] Relevant DocuShell Mocha suites (29 passing) and `@docushell/docs` production build.
- [x] `cargo deny check licenses bans sources`; no denied licenses or sources, and no AGPL.
- [x] Built the `ethos-doc-core` crate package plus the Python sdist/wheel, and inspected the npm
      tarball with `npm pack --dry-run`. Dependent Rust crates remain gated on publishing
      `ethos-doc-core 0.4.0` first, as required by crates.io dependency ordering.
- [x] Contributor cold-start check: this release pass followed `AGENTS.md` and one release-prep
      document without creating per-artifact ceremony records.
- [x] Windows x64 double-build/runtime smoke passed in release run `29728642038`, and the full
      macOS/Linux/Windows verification determinism matrix passed in run `29728692721`. Public
      Windows artifact publication remains a separate first-of-class release decision.

### 3. Version activation

The lockstep Rust, Python, and `@docushell/ethos-pdf` source metadata is activated at `0.4.0`,
and draft artifact workflow smoke expectations are aligned to `ethos 0.4.0`. The npm vendor
manifest remains truthfully bound to the currently vendored `0.3.0` binaries until the human
artifact/vendor-refresh step. Public install wording continues to name only the published
`0.3.0` artifacts until a human publishes v0.4.0 and approves the corresponding wording change.

### 4. Human-operated publication and closeout

A human operator runs all registry publishes, tag pushes, and GitHub Release changes. Record the
actual published surfaces, versions, hashes, commands, wording disposition, and deviations in
the single `docs/validation/v0-4-0-release-closeout-<date>.md` record required by Release Lane
v2. Skipped surfaces must be recorded rather than silently implied.

The exact public release wording in `docs/releases/v0.4.0.md` was approved by the human decider
on 2026-07-20. Final archive hashes must be inserted from the release workflow run bound to the
final merged `main` commit before publication.

## Product Boundary

Ethos verifies citation grounding against supplied source representations; it does not establish
semantic truth. v0.4.0 must preserve that boundary, fail closed when required capabilities are
missing, and emit byte-identical deterministic artifacts for pinned inputs and profiles.
