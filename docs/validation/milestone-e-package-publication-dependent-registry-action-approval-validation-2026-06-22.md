# Milestone E Package Publication Dependent Registry Action Approval Validation - 2026-06-22

- Validated source HEAD before this record: `868e371`

Approval source commit: `868e371cac09247f14fd48eeeaa03361ef507dbb`

Approval source tree: `acf16996446a439ec170a7f0727c00c46dff4ebb`

Accepted package tag source commit: `421bed8c6e04fa3d2299c6a1d9c99ccfd508122e`

Accepted package tag source tree: `aa0d5d31d879540fd0044052dfeb747f12b64204`

Status: **pass for dependent registry action approval with public installation blocked**

Ethos remains source-only pre-alpha outside the approved GitHub source-repository public beta
surface. Public reports remain blocked. Public result wording remains blocked.

## Approval Packet

Lane: Package publication dependent registry actions

Decision: approve

Exact authorized registry actions:

```text
cargo publish --locked -p ethos-verify
cargo publish --locked -p ethos-pdf
```

Exact source binding acknowledged:

```text
421bed8c6e04fa3d2299c6a1d9c99ccfd508122e
```

Exact package tags acknowledged:

```text
ethos-package-ethos-verify-0.1.0
ethos-package-ethos-pdf-0.1.0
```

Preconditions acknowledged:

- `ethos-doc-core v0.1.0` is published on crates.io.
- `cargo publish --dry-run --locked -p ethos-verify` passed after `ethos-doc-core v0.1.0`
  was available.
- `cargo publish --dry-run --locked -p ethos-pdf` passed after `ethos-doc-core v0.1.0`
  was available.
- Registry action evidence is recorded in
  `docs/validation/milestone-e-package-publication-registry-action-evidence-validation-2026-06-22.md`.
- Registry action evidence is recorded in commit
  `868e371cac09247f14fd48eeeaa03361ef507dbb`.

Explicit exclusions retained:

- wheels
- npm packages
- binaries
- hosted surfaces
- production positioning
- public benchmark reports
- public benchmark claims
- project-maintained PDFium builds
- `ethos-doc`
- `ethos-rag`

Public installation wording:

```text
blocked until all approved crate registry actions complete and a separate wording record is prepared.
```

Approver: `docushell-admin`

Date: `2026-06-22`

## Boundaries

This record authorizes only the two dependent registry actions listed above.

It does not authorize:

- public installation wording;
- wheels, npm packages, binaries, hosted surfaces, or project-maintained PDFium builds;
- production positioning;
- public benchmark reports or public benchmark claims;
- `ethos-doc` or `ethos-rag` registry actions;
- any source, manifest, API, fixture, schema, or workflow change.

## Result

The dependent registry action approval is recorded. The next manual actions may proceed one at a
time:

```text
cargo publish --locked -p ethos-verify
cargo publish --locked -p ethos-pdf
```

Public installation remains blocked until the completed dependent registry action evidence is
recorded and separate wording approval is prepared.
