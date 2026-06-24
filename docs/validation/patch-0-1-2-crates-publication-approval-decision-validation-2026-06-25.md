# Patch 0.1.2 crates.io Publication Approval Decision Validation - 2026-06-25

Validated source HEAD before this record: `63f6533`.

Patch 0.1.2 crates publication approval decision source commit: `63f6533d80918cd9304bfa6cb54e7dfdc10eebfc`.

Patch 0.1.2 crates publication approval decision source tree: `adc6b379d1fa74e9124e59a7ffad4ff9d22b103c`.

Status: **patch 0.1.2 crates.io publication approval decision recorded; operator publish remains pending**

This record accepts the exact patch `0.1.2` crates.io publication request packet after decider
approval. It approves only the bounded later operator actions for `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf` version `0.1.2`. It does not run `cargo publish`, publish any
crate, change public wording, approve PyPI upload, approve hosted surfaces, approve production
positioning, approve Windows packaged artifacts, approve bundled project-maintained PDFium builds,
approve `ethos-doc`, approve `ethos-rag`, or approve public benchmark reports or claims.

## Subject

- Repository: `docushell/ethos`
- Lane: Rust crates publication
- Approval owner: `docushell-admin`
- Approval request record:
  `docs/validation/patch-0-1-2-crates-publication-approval-request-validation-2026-06-25.md`
- Package source commit accepted by this decision: `3bc3564e38c1168b2db72f38863d324b6b57bd4d`
- Package source tree accepted by this decision: `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`

## Exact Decision Fields

- Decision: accept exact patch `0.1.2` crates.io publication decision packet.
- Approver: `docushell-admin` acting as decider.
- Date: 2026-06-25.
- Exact candidate crate list accepted by this decision: `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf` only.
- Exact package version map accepted by this decision: `ethos-doc-core = 0.1.2`,
  `ethos-verify = 0.1.2`, and `ethos-pdf = 0.1.2`.
- Exact package tag name set accepted by this decision: `ethos-package-ethos-doc-core-0.1.2`,
  `ethos-package-ethos-verify-0.1.2`, and `ethos-package-ethos-pdf-0.1.2`.
- Exact package tag source commit accepted by this decision:
  `3bc3564e38c1168b2db72f38863d324b6b57bd4d`.
- Exact package tag source tree accepted by this decision:
  `eda8c7a605a4eb29c155ae3b9e6e9f0c35798f8c`.
- Exact candidate package artifacts accepted by this decision:
  - `ethos-doc-core-0.1.2.crate`
    - SHA256: `471956cac567f2d328ab2538291462a0bf57e082ef40dd86d877ffaa363bb632`
  - `ethos-verify-0.1.2.crate`
    - SHA256: `cc4356aa24b304d2f18187d5c3a0c02f847031c1d74e2f6a902a742711d65bf4`
  - `ethos-pdf-0.1.2.crate`
    - SHA256: `9245cf03c71802c385d65ac8539e678e513114fdbb359543ad0d1373af02b900`
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
`ethos-doc-core = 0.1.2` before publishing dependent crates. The operator must stop if candidate
contents differ, package versions differ, crates.io reports any unexpected version state, or any
retained blocker is softened.

Publication remains a separate operator action. This decision record does not run `cargo publish`.

## Required Operator Pre-Publish Checks

Before publishing, the operator must run:

```sh
python3 .github/scripts/test_patch_0_1_2_crates_publication_approval_decision.py
python3 .github/scripts/test_patch_0_1_2_crates_publication_approval_request.py
python3 .github/scripts/package_publication_candidate_activation.py --json
python3 .github/scripts/test_patch_0_1_2_artifact_package_evidence.py
python3 .github/scripts/test_patch_0_1_2_public_install_wording_closeout.py
make release-candidate-prep PYTHON=python3
git diff --check
```

## Explicit Exclusions

- `ethos-cli` remains excluded from crates.io publication.
- `ethos-layout` remains excluded from crates.io publication.
- `ethos-tables` remains excluded from crates.io publication.
- `ethos-grounding-opendataloader-json` remains excluded from crates.io publication.
- PyPI publication remains blocked.
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

- Decider decision supplied: Approved; exact patch `0.1.2` Rust crates.io publication request
  accepted for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`.
- `python3 .github/scripts/test_patch_0_1_2_crates_publication_approval_request.py` passed on
  merged `main` before this decision branch.
- `python3 .github/scripts/test_release_candidate_prep.py` passed on merged `main` before this
  decision branch.
- `python3 .github/scripts/test_patch_0_1_2_public_install_wording_closeout.py` passed on merged
  `main` before this decision branch.
- `make light-check PYTHON=python3` passed on merged `main` before this decision branch.
- `make release-candidate-prep PYTHON=python3` passed on merged `main` before this decision branch.
- `git diff --check` passed on merged `main` before this decision branch.

## Non-Actions

- This decision record does not run `cargo publish`.
- This decision record does not publish any crate.
- This decision record does not create package tags.
- This decision record does not approve public installation wording.
- This decision record does not approve PyPI upload.
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
- PyPI publication remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The exact patch `0.1.2` crates.io publication decision packet for `ethos-doc-core`,
`ethos-verify`, and `ethos-pdf` is accepted. Actual crates.io publication remains a separate
operator action requiring final pre-publish checks, crates.io credentials, dependency-order
discipline, and later registry closeout evidence.
