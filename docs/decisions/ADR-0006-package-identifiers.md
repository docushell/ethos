# ADR-0006: Package Identifiers (Registry / Trademark Validation)

- Status: **Proposed — Docushell ownership selected; reservation and trademark validation still block public artifacts**
- Date: 2026-06-11
- Governs: IMPLEMENTATION_PLAN §2 row 0.11; PRD §3.1; risk R8

## Context

The project name is **Ethos**; `ethos` is a loaded name with collision/trademark risk. Package identifiers are provisional until registries and trademark are checked. No package publish, public benchmark, or launch announcement may happen before this ADR is Accepted.

## Candidate identifiers (provisional)

| Surface | Identifier | Registry | Availability checked | Reserved |
| --- | --- | --- | --- | --- |
| CLI binary | `ethos` | — (binary name) | n/a | n/a |
| Public module | `ethos-doc` | crates.io | 2026-06-14: not found | ☐ (reserve even if facade) |
| Public module | `ethos-rag` | crates.io | 2026-06-14: not found | ☐ (reserve even if facade) |
| Public module | `ethos-verify` | crates.io | 2026-06-14: not found | ☐ |
| Core crate | `ethos-doc-core` (public package; internal crate may remain `ethos-core` pre-publish) | crates.io | 2026-06-14: not found | ☐ |
| Retired candidate | `ethos-core` | crates.io | 2026-06-14: exists | n/a |
| Crates | `ethos-*` (pdf, layout, tables, security, render, cli, mcp) | crates.io | 2026-06-14: checked not found | ☐ |
| Python | `ethos-pdf` (import `ethos_pdf`) | PyPI | 2026-06-14: not found | ☐ |
| Node | `@docushell/ethos-pdf` | npm | 2026-06-15: package not found | ☐ (scope: `@docushell`) |
| GitHub source | `docushell/ethos`, `docushell/ethos-bench` | GitHub | 2026-06-15: owner exists | n/a |
| Schema namespace | `urn:ethos:schema:*` | — (URN, no registry claim) | n/a | n/a |

## Validation checklist (devrel owner)

- [x] crates.io name search for every `ethos-*` identifier above (conflict: `ethos-core`; replacement `ethos-doc-core` selected and checked)
- [x] PyPI search `ethos-pdf` (+ pep503 normalized forms)
- [x] npm package lookup `@docushell/ethos-pdf` (scope/package reservation still pending)
- [x] GitHub owner/repo validation (`docushell` selected; no separate `ethos-pdf` GitHub org)
- [ ] Trademark scan (software classes) for "Ethos" in primary jurisdictions
- [x] Record outcomes here; if any conflict → rename via this ADR before any public artifact (risk R8 trigger)

## Evidence required before acceptance

| Check | Evidence to record |
| --- | --- |
| crates.io | Search date, exact names checked, availability/reservation result, owner account if reserved |
| PyPI | Search date, normalized package name checked, availability/reservation result, owner account if reserved |
| npm | Search date, scope/package checked, availability/reservation result, owner account if reserved |
| GitHub | Search date, org/repo names checked, collision notes |
| Trademark | Search date, jurisdictions/classes checked, conflict assessment |

## Validation log

### 2026-06-14 — partial registry/GitHub check

Direct registry validation from the local engineering environment was inconclusive:

- crates.io API and `cargo search` checks for `ethos-doc`, `ethos-rag`, `ethos-verify`, and `ethos-pdf` timed out or failed DNS resolution. No crates.io availability conclusion is recorded.
- PyPI API check for `ethos-pdf` timed out. No PyPI availability conclusion is recorded.
- npm registry / `npm view` check for `@ethos-pdf/core` timed out. No npm availability conclusion is recorded.
- Web trademark search did not produce an official, auditable USPTO/EUIPO/TMview result. Trademark/legal validation remains required.

GitHub collision scan produced preliminary evidence:

- `https://api.github.com/orgs/ethos-pdf` returned 404, so no GitHub organization named `ethos-pdf` was visible to this check.
- GitHub repository search for `ethos-verify` in repository names returned `total_count: 0`.
- GitHub repository search for `ethos-rag` in repository names returned `total_count: 0`.
- GitHub repository search for `ethos-pdf` in repository names returned `total_count: 1`; the result was not an exact `ethos-pdf` repository name (`manjeetsingh-ethos/WeasyPrint-Nodejs-Html-pdf`).
- GitHub repository search for `ethos-doc` in repository names returned `total_count: 16`; first-page results were not exact `ethos-doc` package repositories, but the namespace is noisy enough to review manually before public launch.

Outcome: this ADR is not accepted. Public package publishing, public benchmark release, and launch announcements remain blocked until registry availability/reservation and trademark/legal checks are completed from an environment with reliable registry access.

### 2026-06-14 — registry check after VPN removal

Registry checks were rerun with direct network access and an explicit user agent.

crates.io API results:

| Name | Result |
| --- | --- |
| `ethos-doc` | 404 not found |
| `ethos-rag` | 404 not found |
| `ethos-verify` | 404 not found |
| `ethos-core` | 200 exists |
| `ethos-pdf` | 404 not found |
| `ethos-layout` | 404 not found |
| `ethos-tables` | 404 not found |
| `ethos-security` | 404 not found |
| `ethos-render` | 404 not found |
| `ethos-cli` | 404 not found |
| `ethos-mcp` | 404 not found |

`cargo search ethos-core --limit 5` confirmed:

```text
ethos-core = "0.0.0"    # Ethos Core components
```

The existing `ethos-core` crate metadata reported version `0.0.0`, description `Ethos Core components`, repository `https://github.com/NickelAngeStudio/nswindow`, 18 downloads, and `created_at` / `updated_at` `2026-01-19T14:06:03.017094Z`.

Other registry results:

- PyPI `https://pypi.org/pypi/ethos-pdf/json` returned 404 not found.
- npm `https://registry.npmjs.org/%40ethos-pdf%2Fcore` returned 404 not found; `npm view @ethos-pdf/core name version --json` also returned `E404`.
- GitHub organization `https://api.github.com/orgs/ethos-pdf` returned 404 not found.

Outcome: `ethos-core` cannot be treated as an available public crates.io identifier. Before this ADR can be accepted, the public Rust crate naming plan must either rename the core crate or explicitly choose not to publish a crate under that name. Trademark/legal validation remains required.

### 2026-06-14 — core crate replacement selected

`ethos-doc-core` is the selected public crates.io replacement for the blocked `ethos-core` package identifier. `https://crates.io/api/v1/crates/ethos-doc-core` returned 404 not found with direct network access and an explicit user agent.

This is a public package identifier decision only. The internal Rust crate directory, dependency key, and import path may remain `ethos-core` / `ethos_core` until the publishing migration is implemented. That keeps this ADR update decoupled from code churn and lets the publish packaging change happen as a separate reviewed step.

Outcome: `ethos-doc-core` should replace `ethos-core` in public-package planning. This ADR still cannot be accepted until reservation ownership and trademark/legal validation are complete.

### 2026-06-15 — Docushell ownership selected

GitHub source ownership is standardized under the existing `docushell` owner. The canonical source repositories are `docushell/ethos` and `docushell/ethos-bench`; no separate `ethos-pdf` GitHub organization should be created for this project.

Validation:

- `https://api.github.com/users/docushell` returned 200.
- `https://api.github.com/orgs/docushell` returned 404, so `docushell` appears as a GitHub user owner rather than an organization endpoint.
- `https://registry.npmjs.org/%40docushell%2Fethos-pdf` returned 404 not found.

Outcome: npm planning moves from `@ethos-pdf/core` to `@docushell/ethos-pdf` so package ownership aligns with the existing Docushell GitHub owner. The historical `@ethos-pdf/core` checks remain recorded above but are no longer the selected npm package plan.

## Decision

Pending validation. Identifiers above are used internally in the meantime; they may change by amendment to this ADR if unavailable. `ethos-doc-core` is the selected public crates.io replacement for the unavailable `ethos-core` package identifier. GitHub source ownership and npm scope should use Docushell (`docushell/ethos`, `docushell/ethos-bench`, `@docushell/ethos-pdf`). Schema `$id`s use the `urn:ethos:schema:*` form precisely so schemas need no rename if package names change.
