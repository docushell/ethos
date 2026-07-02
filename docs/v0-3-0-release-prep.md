# Ethos v0.3.0 Release Preparation

Status: release-candidate source activation and closeout tracker. Rust crates, the Python wheel,
the GitHub Release CLI artifacts, and npm `@docushell/ethos-pdf@0.3.0` are now published or
closed out for their exact approved surfaces. This document does not approve package tags, release
tags, DocuShell integration, hosted surfaces, production positioning, or public `0.3.0`
installability wording.

Canonical preparation sentence:

> v0.3.0 source versions are activated for app-answer-release contract validation.

The release promise being prepared is narrow:

> Ethos verifies citation grounding and derives proof summaries. Applications decide question
> relevance, source-fact versus synthesis labels, unsupported-claim labels, and final/review/blocked
> answer release policy.

## Included Preparation Scope

- Rust `ethos-doc-core` app-answer-release helpers:
  `VerificationReport::proof_summary()` and `derive_app_answer_release_decision(...)`.
- Rust `ethos-verify` and `ethos-pdf` as the existing lockstep public Rust crate set for the
  source candidate.
- Python `ethos-pdf==0.3.0` metadata for `proof_summary(...)` and
  `app_answer_release_decision(...)`.
- App-answer-release schema and example artifacts.
- Runnable app-answer-release demo showing final, review, and blocked release decisions.
- Release-candidate docs and validation guards for the contract boundary.

## Explicit Non-Scope

- LLM judging;
- DocuShell UI work;
- semantic answer verification by Ethos;
- parser-quality claims;
- broad answer correctness claims;
- Node API, Node SDK, N-API, or WASM bindings;
- npm CLI alignment release;
- hosted service;
- production/SaaS claims;
- public benchmark or performance claims;
- project-managed bundled PDFium;
- Windows packaged binaries;
- public GA for `ethos-doc` or `ethos-rag`.

## Release Sequence

### 1. Accept The Contract Prep Packet

The accepted prep packet is
`docs/validation/app-answer-release-contract-release-prep-validation-2026-07-01.md`. It binds the
merged contract, schema, Rust helper, Python helper, docs, demo, and guard commands.

### 2. Activate Source Metadata

The `v0.3.0` source activation changes only release-candidate source metadata:

- bump Rust workspace/package dependency versions from `0.2.0` to `0.3.0`;
- bump Python metadata and `ethos_pdf.__version__` from `0.2.0` to `0.3.0`;
- leave npm `@docushell/ethos-pdf` at the current public CLI package baseline `0.2.1`;
- keep public install commands on the current published `0.2.0` Rust/Python and `0.2.1` npm
  surfaces;
- add source-bound approval and activation validation records.

### 3. Run The Source Gate

Run:

```bash
make v0-3-release-prep PYTHON=python3
```

The target runs the workspace Rust test suite, app-answer-release contract guard, Python public
surface checks, 0.3.0 approval and activation guards, public posture checks, claims gates, and
diff hygiene.

### 3a. Prepare And Record CLI Artifact Evidence

The `.github/workflows/release.yml` artifact workflow is aligned to the v0.3.0 CLI artifact
evidence lane and smokes `--expected-version "ethos 0.3.0"`. The v0.3.0 CLI artifact evidence
prep record documents this workflow alignment without running the workflow, publishing artifacts,
creating tags, refreshing npm vendor payloads, or changing public install wording.

The v0.3.0 draft CLI artifact evidence record captures
`https://github.com/docushell/ethos/actions/runs/28531102130` on `main`, bound to source commit
`7287358475a96e827d536f0d2d250a1c2961ba84`, with macOS arm64 and Linux x64 archive SHA256 values,
inventory sidecars, archive listings, and smoke sidecars that report `ethos 0.3.0`.

The v0.3.0 artifact publication approval request is recorded in
`docs/validation/v0-3-0-artifact-publication-approval-request-validation-2026-07-01.md`. It asks
the decider to accept or reject only the exact macOS arm64 and Linux x64 draft CLI artifact names,
checksums, workflow evidence, and bounded wording.

The v0.3.0 artifact publication approval decision is recorded in
`docs/validation/v0-3-0-artifact-publication-approval-decision-validation-2026-07-01.md`. It
accepts only the exact macOS arm64 and Linux x64 CLI artifact names, checksums, source binding,
workflow evidence, and bounded wording for later operator attachment to GitHub Release target
`v0.3.0`.

The v0.3.0 artifact publication closeout is recorded in
`docs/validation/v0-3-0-artifact-publication-closeout-validation-2026-07-02.md`. It records
GitHub Release `v0.3.0` at source commit `4aa8b8bf25685f9cd6691669ea791a38ecc1a84a` with exact
macOS arm64 and Linux x64 CLI artifact names, checksums, sidecars, bounded release body, and
caller-provided PDFium posture.

Before that closeout, Draft artifacts remain CI evidence only. GitHub Release artifact upload
remains blocked until the approved operator action and closeout record pass. The closeout
supersedes that blocker only for the exact approved `v0.3.0` release assets. npm vendor refresh
remains blocked until a separate vendor-refresh evidence and approval lane passes. npm
publication, package tag creation, public install wording, and DocuShell integration remain
blocked.
The public install wording remains blocked until the relevant registry, artifact, npm, tag, and
wording closeout records pass.

### 3b. Refresh npm Vendor Candidate

The v0.3.0 npm vendor refresh is recorded in
`docs/validation/v0-3-0-npm-vendor-refresh-validation-2026-07-02.md`. It refreshes the
`@docushell/ethos-pdf@0.3.0` source package candidate from the published GitHub Release `v0.3.0`
macOS arm64 and Linux x64 CLI artifacts, records exact vendor binary and npm tarball evidence, and
validates local install smoke with `ethos 0.3.0`.

This refresh does not approve `npm publish`. It does not approve public `0.3.0` install wording.
npm publication, package tag creation, public install wording, and DocuShell integration remain
blocked until separate approval, operator, registry-smoke, tag, and wording closeout records pass.

### 3c. Request npm Publication Approval

The v0.3.0 npm publication approval request is recorded in
`docs/validation/v0-3-0-npm-publication-approval-request-validation-2026-07-02.md`. It asks the
decider to accept or reject only the exact `@docushell/ethos-pdf@0.3.0` npm candidate, tarball
metadata, vendor payload checksums, supported platforms, installed CLI smoke, and caller-provided
PDFium boundary.

This request does not approve `npm publish`. npm publication remains blocked until a separate
approval decision record passes and an operator publishes with npm credentials. Public `0.3.0`
install wording, package tag creation, release tag creation, and DocuShell integration remain
blocked until separate closeout lanes pass.

### 3d. Approve npm Publication Operator Action

The v0.3.0 npm publication approval decision is recorded in
`docs/validation/v0-3-0-npm-publication-approval-decision-validation-2026-07-02.md`. It accepts
the exact `@docushell/ethos-pdf@0.3.0` npm publication request and authorizes only the later
operator `npm publish` action for that bounded candidate after merged-source validation passes.

This decision did not itself publish the npm package. The later npm publication closeout below
records that the approved operator action is complete for the exact package and version. Public
`0.3.0` install wording, package tag creation, release tag creation, and DocuShell integration
remain blocked until separate evidence and closeout lanes pass.

### 3e. Close npm Publication

The v0.3.0 npm publication closeout is recorded in
`docs/validation/v0-3-0-npm-publication-closeout-validation-2026-07-02.md`. It records live npm
registry evidence for the exact `@docushell/ethos-pdf@0.3.0` package, including registry latest,
dist shasum, integrity, tarball URL, file count, unpacked size, signature metadata, source
gitHead, and the caller-provided PDFium boundary.

This closeout supersedes the npm publication blocker only for the exact package and version
`@docushell/ethos-pdf@0.3.0`. Public `0.3.0` install wording, package tag creation, release tag
creation, and DocuShell integration remain blocked until separate evidence and closeout lanes
pass.

### 3f. Request Public Install Wording Approval

The v0.3.0 public install wording approval request is recorded in
`docs/validation/v0-3-0-public-install-wording-approval-request-validation-2026-07-02.md`. It asks
the decider to accept or reject only the exact public `0.3.0` install wording packet for the
already-live Rust crates, Python wheel, npm package, and GitHub Release CLI artifacts.

This request does not change `README.md` or `docs/public-boundary-claims.json`. Public `0.3.0`
install wording remains blocked until a separate approval decision and closeout pass. Package tag
creation, release tag creation, and DocuShell integration remain blocked until separate evidence
and closeout lanes pass.

### 4. Gather Package Evidence Before Any Publication Decision

Before any public package or artifact decision, record exact evidence for the surfaces that are in
scope:

- Rust crate package/dry-run evidence for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at
  `0.3.0`.
- Python wheel build/install/helper smoke evidence for `ethos-pdf==0.3.0`.
- CLI artifact evidence only if the release scope later includes CLI artifacts.
- npm package evidence only if a later decision explicitly includes npm CLI alignment.

### 5. Flip Public Install Wording Only After Closeout

Only after registry/artifact availability and smoke closeout records pass, update public install
wording to `0.3.0` and rerun:

```bash
python3 .github/scripts/claims_gate.py
python3 .github/scripts/public_boundary_claims_gate.py
```

## Product Boundary

Ethos does not certify a complete answer. The app-answer-release contract proves a narrower path:

```text
Ethos proof summary
+ app-labeled claims
+ question relevance
+ synthesis/source-fact labels
= final / review / blocked answer-release decision
```

Safe product wording remains:

```text
Ethos verified citation grounding.
Answer relevance: direct, partial, or off-topic.
```

## DocuShell Integration Boundary

DocuShell should integrate against this demo pattern only after a release closeout or an explicit
source-dependency decision. The integration should keep retrieval citations, raw model output,
verified claims, app labels, and the final answer-release decision separate.
