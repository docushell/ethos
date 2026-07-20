# Ethos v0.4.0 Release Preparation

Status: **in progress** — release-lane-v2 pilot for the accumulated next-minor work.
Current source/package metadata remains `0.3.0`; version activation and publication are not
approved by this document.

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
- NIP-5.3 verify-only Windows x64 draft artifact: deterministic ZIP, bundled JSON verification
  fixtures, no PDFium DLL, and target-runner smoke evidence required before publication.
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

- [ ] Review the complete `main...dev/v0-4-0` diff against this included/non-scope inventory.
- [ ] Confirm all report/config/evidence `1.0.0` compatibility and `1.1.0` migration fixtures.
- [ ] Confirm `ethos-verify` depends only on `GroundingSource`, not parser internals.
- [ ] Confirm `packages/npm/ethos-mcp` is absent from release builds and publication commands.
- [ ] Resolve or explicitly carry every open release-relevant friction-log entry.

### 2. Validation

- [ ] `cargo build --locked --workspace`
- [ ] `cargo test --locked --workspace`
- [ ] `make verify-alpha`
- [ ] `.github/scripts/public_boundary_claims_gate.py`
- [ ] Citation-emission and framework-example offline/double-run tests.
- [ ] Relevant DocuShell Mocha suites and affected workspace builds for integration changes.
- [ ] Dependency/license checks, including the no-AGPL and base-crate network boundaries.
- [ ] Windows x64 draft builds twice byte-identically and passes its verify-only smoke on the
      Windows runner.

### 3. Version activation

After the scope and validation gates pass, update the lockstep release surfaces from `0.3.0` to
`0.4.0` in a reviewed version-activation change. Public install wording must continue to name
only the already-published `0.3.0` artifacts until a human publishes v0.4.0 and approves the
corresponding wording change.

### 4. Human-operated publication and closeout

A human operator runs all registry publishes, tag pushes, and GitHub Release changes. Record the
actual published surfaces, versions, hashes, commands, wording disposition, and deviations in
the single `docs/validation/v0-4-0-release-closeout-<date>.md` record required by Release Lane
v2. Skipped surfaces must be recorded rather than silently implied.

## Product Boundary

Ethos verifies citation grounding against supplied source representations; it does not establish
semantic truth. v0.4.0 must preserve that boundary, fail closed when required capabilities are
missing, and emit byte-identical deterministic artifacts for pinned inputs and profiles.
