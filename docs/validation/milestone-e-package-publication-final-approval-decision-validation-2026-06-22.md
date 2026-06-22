# Milestone E Package Publication Final Approval Decision Validation - 2026-06-22

## Purpose

Record the decider acceptance of the exact package-publication decision packet after the final
approval request, current dry-run smoke evidence, current registry-equivalent assembly evidence,
and source manifest activation review are present.

This record accepts the exact bounded crates.io candidate surface, version map, tag names, source
binding, public installation wording, and exclusions supplied by `docushell-admin`. It does not
create package tags, remove `publish = false`, activate package metadata, run `cargo publish`, or
publish any package.

## Status

Status: **pass for final package-publication approval decision with activation pending**.

Decision: accept exact package-publication decision packet for the bounded crates.io candidate
surface.

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `4fee88f`
- Approval decision record source commit: `4fee88f005a9573de3c2f310ff824861768249c1`
- Approval decision record source tree: `7f801f0b5aeb51c7f79ecaac1ca19847f0cd1b61`
- Lane: package publication
- Final approval request record:
  `docs/validation/milestone-e-package-publication-final-approval-request-validation-2026-06-22.md`
- Current dry-run smoke record:
  `docs/validation/milestone-e-package-publication-current-dry-run-smoke-validation-2026-06-22.md`
- Current registry-equivalent assembly record:
  `docs/validation/milestone-e-package-publication-current-registry-assembly-validation-2026-06-22.md`
- Manifest activation applied record:
  `docs/validation/milestone-e-package-publication-manifest-activation-applied-validation-2026-06-22.md`
- Approval owner: `docushell-admin`

## Exact Decision Fields

- Decision: accept exact package-publication decision packet for the bounded crates.io candidate
  surface.
- Approver: docushell-admin acting as decider.
- Date: 2026-06-22.
- Exact candidate crate list accepted by this decision: `ethos-doc-core`, `ethos-verify`, and
  `ethos-pdf` only.
- Exact package version map accepted by this decision: `ethos-doc-core = 0.1.0`,
  `ethos-verify = 0.1.0`, and `ethos-pdf = 0.1.0`.
- Exact package tag name set accepted by this decision: `ethos-package-ethos-doc-core-0.1.0`,
  `ethos-package-ethos-verify-0.1.0`, and `ethos-package-ethos-pdf-0.1.0`.
- Exact package tag source commit accepted by this decision:
  `b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875`.
- Exact package tag source tree accepted by this decision:
  `4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3`.
- Exact public installation wording accepted by this decision: Ethos Rust crates ethos-doc-core,
  ethos-verify, and ethos-pdf version 0.1.0 are proposed for crates.io installation only after
  explicit package-publication approval and package-tag creation. ethos-pdf requires
  caller-provided PDFium through ETHOS_PDFIUM_LIBRARY_PATH. Wheels, npm packages, binaries, hosted
  surfaces, production positioning, public benchmark reports, public benchmark claims,
  project-maintained PDFium builds, ethos-doc, and ethos-rag remain blocked.
- Exact manifest activation reviewed by this decision: source package name `ethos-doc-core`,
  Rust library name `ethos_core`, and workspace dependency key `ethos-core` resolving package
  `ethos-doc-core`.
- Publish-flag activation status: still pending a later activation change; `publish = false`
  remains in all three source manifests.
- Package tag creation status: still pending a later tag operation; no package tag is created by
  this decision record.
- Real-version cargo publish status: still blocked pending later activation and operator evidence.
- Public-surface posture check result after this decision: passed against unchanged public surfaces
  and this accepted wording record.
- Claims gate result after this decision: passed against unchanged public surfaces and this
  accepted wording record.
- Milestone E prep result after this decision record: required for this record branch.

## Approved Package Source Binding

- Approved package tag source commit: `b48e2f2c7ff6f3507bbf84c6d603cf4a385b9875`.
- Approved package tag source tree: `4d660bd7c1de69259d0f8c59e6ac8d1c2cb6a3a3`.
- The approval record itself is documentation-only and is intentionally not the package tag source
  commit.

## Explicit Exclusions

- wheels remain blocked
- npm packages remain blocked
- binaries remain blocked
- hosted surfaces remain blocked
- production positioning remains blocked
- public benchmark reports remain blocked
- public benchmark claims remain blocked
- project-maintained PDFium builds remain blocked
- `ethos-doc` remains excluded
- `ethos-rag` remains excluded
- broader public wording remains blocked
- Public reports remain blocked
- Public result wording remains blocked

## Activation Blockers Retained After This Decision

- publish-flag activation remains blocked until a later source change removes `publish = false`
  from the three accepted candidate manifests only
- package metadata activation remains blocked until a later source change updates the accepted
  candidate metadata only
- package tag creation remains blocked until a later tag operation binds the accepted names to the
  accepted source commit
- real-version cargo publish remains blocked until the later activation state and operator evidence
  are present
- public README or installation instructions remain unchanged until the accepted package surface is
  actually available through the registry

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_final_approval_decision.py
python3 .github/scripts/test_milestone_e_package_publication_final_approval_request.py
python3 .github/scripts/test_milestone_e_package_publication_current_registry_assembly.py
python3 .github/scripts/test_milestone_e_package_publication_dry_run_smoke.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Result

```text
Final approval decision validation passed
Exact candidate crate list, version map, tag names, source binding, wording, and exclusions were accepted
No package tag was created
No publish flag was changed
No package metadata was activated
No package was published
Public-surface posture and claims gates passed
Milestone E prep target passed
git diff --check passed
```
