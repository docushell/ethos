# Ethos v0.4.0 Release Preparation

Status: **release candidate prepared** — source/package metadata is activated at `0.4.0`; human
PR review, CI, registry publication, tag/GitHub Release actions, and closeout remain pending.
Public installation wording remains on the actually published `0.3.0` surfaces.

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
- Citation-emission contract `1.0.0` (NIP-4.1), dependency-free Python LangChain/LlamaIndex
  emission helpers (NIP-4.2), and model-free framework walkthroughs (NIP-4.3), including
  fail-closed hydration and double-run byte-identical artifact checks.
- DocuShell first-consumer integration contracts and friction findings for NIP-1.1–1.6. The
  private DocuShell implementation remains versioned and validated in its own repository; this
  release does not publish DocuShell or make public adoption claims about it.
- Adoption and operator tooling originally prepared for the abandoned v0.3.1 patch scope:
  the README fixture demo, caller-run pinned PDFium fetch helper, ADR-0013, and related decision
  amendments. PDFium remains caller-provided and is never downloaded automatically by Ethos.
- Release Lane v2 governance and contributor guidance, with this document serving as the one
  prep note for the v0.4.0 train.

## Carried but Not Activated as a Release Surface

The source tree contains an unpublished `packages/npm/ethos-mcp` prototype inherited from work
that predates the active NIP priority decision. NIP-2 remains P2-gated until all P0/P1 work is
done or the decider explicitly changes that dependency. The prototype is therefore excluded
from v0.4.0 package publication, release claims, and release validation. Keeping its commits in
the branch does not activate or approve the surface.

The source tree also contains the Proposed ADR-0015 and its deterministic `ethos-full` candidate
builder/evidence. The proposal does not activate bundled PDFium: no `ethos-full` archive enters
the v0.4.0 artifact set unless the decider accepts the ADR and this prep scope is updated in a
reviewed change.

The NIP-5.3 verify-only Windows x64 implementation and draft workflow remain in source, but the
Windows package is skipped as a v0.4.0 publication surface. It is a first-of-class artifact and
cannot ship until its `windows-latest` double-build and target-runtime smoke pass. A later
closeout must list it as skipped unless that evidence lands before publication.

Before the v0.4.0 release candidate is frozen, the release diff must verify that no build,
workspace, packaging, or documentation path accidentally presents this prototype as shipped.

## Explicit Non-Scope

- `ethos-mcp` activation or npm publication; any `crates/ethos-mcp` implementation;
- version activation and lockstep package-version changes until their reviewed release step;
- crates.io, PyPI, npm, tag, or GitHub Release operator actions;
- public wording changes or public benchmark results and comparative claims;
- hosted or network-served surfaces, production positioning, or a WASM playground;
- bundled/project-maintained PDFium distribution and Windows-with-PDFium artifacts;
- `ethos-rag`, native OCR, or scanned-document support claims;
- NIP-3 trust-benchmark publication and NIP-6 CI Action publication;
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
- [x] NIP-7.3 cold-start check: this release pass followed `AGENTS.md` → active plan → one prep
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

## Product Boundary

Ethos verifies citation grounding against supplied source representations; it does not establish
semantic truth. v0.4.0 must preserve that boundary, fail closed when required capabilities are
missing, and emit byte-identical deterministic artifacts for pinned inputs and profiles.
