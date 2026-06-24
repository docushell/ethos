# Patch 0.1.1 crates.io Publication Approval Decision Validation - 2026-06-24

Validated source HEAD before this record: `5de6014`.

Patch 0.1.1 crates publication approval decision source commit: `5de6014e0fe668bac306eb2c2f5b2963ab5baf96`.

Patch 0.1.1 crates publication approval decision source tree: `6fc0207e61681da6ba868772e77bcbc808c98bfb`.

Status: **patch 0.1.1 crates.io publication approval decision recorded; operator publish remains pending**

This record accepts the exact patch `0.1.1` crates.io publication request packet after decider
approval. It approves only the bounded later operator actions for `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf` version `0.1.1`. It does not run `cargo publish`, publish any
crate, change public wording, approve hosted surfaces, approve production positioning, approve
Windows packaged artifacts, approve bundled project-maintained PDFium builds, approve `ethos-doc`,
approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Rust crates publication
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/patch-0-1-1-crates-publication-approval-request-validation-2026-06-24.md`
- Package source commit accepted by this decision: `a0851030e28c155c12f5f966af8fa0739a536ea9`
- Package source tree accepted by this decision: `0238c3f6bfd264f8803708e4a828d8352320f08f`

## Exact Decision Fields

- Decision: accept exact patch `0.1.1` crates.io publication decision packet.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-24.
- Exact candidate crate list accepted by this decision: `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf` only.
- Exact package version map accepted by this decision: `ethos-doc-core = 0.1.1`,
  `ethos-verify = 0.1.1`, and `ethos-pdf = 0.1.1`.
- Exact package tag name set accepted by this decision: `ethos-package-ethos-doc-core-0.1.1`,
  `ethos-package-ethos-verify-0.1.1`, and `ethos-package-ethos-pdf-0.1.1`.
- Exact package tag source commit accepted by this decision:
  `a0851030e28c155c12f5f966af8fa0739a536ea9`.
- Exact package tag source tree accepted by this decision:
  `0238c3f6bfd264f8803708e4a828d8352320f08f`.
- Exact operator commands accepted by this decision:
  - `cargo publish --locked -p ethos-doc-core`
  - `cargo publish --locked -p ethos-verify`
  - `cargo publish --locked -p ethos-pdf`

## Approved Operator Action

After this decision record is merged and validation passes on merged source, an operator may run
only these commands:

```sh
cargo publish --locked -p ethos-doc-core
cargo publish --locked -p ethos-verify
cargo publish --locked -p ethos-pdf
```

The operator must publish `ethos-doc-core` first. The operator must wait for crates.io to report
`ethos-doc-core = 0.1.1` before publishing dependent crates. The operator must stop if candidate
contents differ, package versions differ, crates.io reports any unexpected version state, or any
retained blocker is softened.

Publication remains a separate operator action. This decision record does not run `cargo publish`.

## Required Operator Pre-Publish Checks

Before publishing, the operator must run:

```sh
cargo package --locked --offline -p ethos-doc-core --allow-dirty --no-verify
cargo check --locked --offline -p ethos-verify
cargo check --locked --offline -p ethos-pdf
python3 .github/scripts/test_patch_0_1_1_crates_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_1_crates_publication_approval_request.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Explicit Exclusions

- `ethos-cli` remains excluded from crates.io publication.
- `ethos-layout` remains excluded from crates.io publication.
- `ethos-tables` remains excluded from crates.io publication.
- `ethos-grounding-opendataloader-json` remains excluded from crates.io publication.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- Broader public wording remains blocked.

## Evidence Bound To This Decision

- Decider decision supplied: Approved; exact patch `0.1.1` Rust crates.io publication request
  accepted.
- `python3 .github/scripts/test_patch_0_1_1_crates_publication_approval_request.py` passed.
- `python3 .github/scripts/test_milestone_e_package_publication_current_registry_assembly.py`
  passed.
- `python3 .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py` passed.
- `cargo package --locked --offline -p ethos-doc-core --allow-dirty --no-verify` passed.
- `cargo check --locked --offline -p ethos-verify` passed.
- `cargo check --locked --offline -p ethos-pdf` passed.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this decision branch.

## Non-Actions

- This decision record does not run `cargo publish`.
- This decision record does not publish any crate.
- This decision record does not create package tags.
- This decision record does not approve public installation wording.
- This decision record does not approve hosted surfaces.
- This decision record does not approve production positioning.
- This decision record does not approve public benchmark reports.
- This decision record does not approve public benchmark claims.
- This decision record does not approve Windows packaged artifacts.
- This decision record does not approve bundled project-maintained PDFium builds.
- This decision record does not approve `ethos-doc`.
- This decision record does not approve `ethos-rag`.

## Retained Blockers

- Public installation wording remains blocked until registry availability is closed out.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The exact patch `0.1.1` crates.io publication decision packet for `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf` is accepted. Actual crates.io publication remains a separate
operator action requiring final pre-publish checks, crates.io credentials, dependency-order
discipline, and later registry closeout evidence.
