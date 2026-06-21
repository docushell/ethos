# Milestone E Package Publication Decision-Bundle Validation - 2026-06-21

## Purpose

Record validation for the combined package publication decision-prep bundle without approving
package publication.

This record validates that the combined decision inputs are recorded before any later dedicated
package publication approval. It does not select a package publication version, create a package
tag, change Cargo manifests, activate package dependency manifests, create a registry, activate
registry-backed dependent package assembly, approve public installation, approve package
publication, publish binaries, publish wheels, publish npm packages, approve hosted surfaces,
approve production positioning, approve public benchmark reports, approve public benchmark claims,
or approve public result wording. It does not resolve or soften blockers outside this
decision-prep bundle.

## Status

Status: **pass for package publication decision-bundle validation with publication blocked**.

Ethos remains source-only pre-alpha outside the approved source-only public beta surface and
internal package publication prep boundary.

Package publication remains blocked.

Public installation remains blocked.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `63d8647`
- Lane: package publication decision-prep bundle
- Evidence area: combined package tag, manifest activation, registry assembly, and public
  installation decision inputs with retained blocked actions

## Evidence Review

- package tag and source-commit decision inputs are recorded while creating no package tag
- package dependency manifest activation inputs are recorded while changing no Cargo manifest
- registry-backed dependent package assembly inputs are recorded while creating no registry and
  activating no assembly
- public installation wording and exclusion inputs are recorded while inviting no public
  installation

Required decision inputs retained for later dedicated approval:

- exact package tag name
- exact source commit for package tag binding
- exact package-name migration diff for ethos-doc-core
- exact dependency manifest activation diff for ethos-verify and ethos-pdf
- exact registry-backed dependent package assembly evidence for ethos-doc-core before ethos-verify
  and ethos-pdf
- exact public installation wording limited to a later approved package surface
- exact exclusion list for wheels, npm packages, binaries, hosted surfaces, production
  positioning, public benchmark reports, public benchmark claims, and project-maintained PDFium
  builds
- posture and claims gates after exact public installation wording changes

## Approval Request Packet

The non-activating package publication approval request packet is recorded with:

- packet state: `approval_request_packet_recorded_publication_blocked`
- candidate crates:
  - ethos-doc-core mapped from crates/ethos-core; package-name migration remains pending
  - ethos-verify mapped from crates/ethos-verify; dependency manifest activation remains pending
  - ethos-pdf mapped from crates/ethos-pdf; dependency manifest activation and PDFium boundary
    confirmation must remain current
- package version map:
  - ethos-doc-core has no selected package publication version
  - ethos-verify has no selected package publication version
  - ethos-pdf has no selected package publication version
- package tag name: not selected; package tag creation remains blocked
- package tag source commit: not selected; package tag binding remains blocked
- package tag source tree: not selected; package source tree binding remains blocked
- manifest activation diff: not prepared; current Cargo manifests remain unchanged
- registry assembly evidence: not activated; registry-backed dependent package assembly remains
  blocked
- public installation wording: No public installation wording is approved; public installation
  remains blocked.
- explicit exclusions: wheels, npm packages, binaries, hosted surfaces, production positioning,
  public benchmark reports, public benchmark claims, release artifacts, and project-maintained
  PDFium builds
- required before approval: exact package publication approval decision record, exact candidate
  crate list, exact SemVer package version or per-crate version map, exact package tag name and
  package_tag_source_commit, exact package-name migration diff for ethos-doc-core, exact dependency
  manifest activation diff for ethos-verify and ethos-pdf, exact registry-backed dependent package
  assembly evidence, and posture and claims gates after exact public installation wording changes

Non-approvals retained:

- this bundle does not select a package publication version
- this bundle does not create a package tag
- this bundle does not change Cargo manifests
- this bundle does not activate package dependency manifests
- this bundle does not create a registry
- this bundle does not activate registry-backed dependent package assembly
- this bundle does not invite public installation
- this bundle does not approve package publication
- this packet does not select a package publication version
- this packet does not create a package tag
- this packet does not change Cargo manifests
- this packet does not activate package dependency manifests
- this packet does not create a registry
- this packet does not activate registry-backed dependent package assembly
- this packet does not invite public installation
- this packet does not approve package publication

## Blockers Retained

- no package publication version is selected
- no package tag is created
- no package dependency manifest activation is approved
- no registry-backed dependent package assembly activation is approved
- public installation remains blocked
- package publication remains blocked
- real-version cargo publish remains blocked
- `ethos-doc` and `ethos-rag` remain reserved placeholders until package owners, manifests, README
  files, metadata, and support expectations are prepared.
- Project-maintained PDFium builds remain blocked.

## Commands

```sh
python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py
python3 .github/scripts/test_milestone_e_package_publication_decision_bundle_validation_record.py
python3 .github/scripts/test_public_surface_posture.py
python3 .github/scripts/claims_gate.py
cargo build --locked -p ethos-cli
make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python
git diff --check
```

## Explicit Boundaries

- Public reports remain blocked.
- Public result wording remains blocked.
- Package publication remains blocked.
- Public installation remains blocked.
- real-version cargo publish remains blocked
- Release artifacts remain blocked.
- Binaries remain blocked.
- Wheels remain blocked.
- Npm packages remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Project-maintained PDFium builds remain blocked.
