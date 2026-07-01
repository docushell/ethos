# Ethos v0.3.0 Release Preparation

Status: release-candidate source activation record. This document does not approve `cargo
publish`, PyPI upload, `npm publish`, GitHub Release creation, package tags, release tags, CLI
artifact publication, DocuShell integration, or public `0.3.0` installability wording.

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

### 3a. Prepare CLI Artifact Evidence

The `.github/workflows/release.yml` artifact workflow is aligned to the v0.3.0 CLI artifact
evidence lane and smokes `--expected-version "ethos 0.3.0"`. The v0.3.0 CLI artifact evidence
prep record documents this workflow alignment without running the workflow, publishing artifacts,
creating tags, refreshing npm vendor payloads, or changing public install wording.

Draft artifacts remain CI evidence only until a later artifact evidence record captures the
workflow run URL, source commit, macOS arm64 and Linux x64 archive SHA256 values, inventory
sidecars, and smoke sidecars. GitHub Release artifact upload remains blocked until a separate
approval decision and operator closeout pass.

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
