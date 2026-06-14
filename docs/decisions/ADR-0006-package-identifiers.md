# ADR-0006: Package Identifiers (Registry / Trademark Validation)

- Status: **Proposed — partial GitHub validation recorded; registry and trademark validation still block public artifacts**
- Date: 2026-06-11
- Governs: IMPLEMENTATION_PLAN §2 row 0.11; PRD §3.1; risk R8

## Context

The project name is **Ethos**; `ethos` is a loaded name with collision/trademark risk. Package identifiers are provisional until registries and trademark are checked. No package publish, public benchmark, or launch announcement may happen before this ADR is Accepted.

## Candidate identifiers (provisional)

| Surface | Identifier | Registry | Availability checked | Reserved |
| --- | --- | --- | --- | --- |
| CLI binary | `ethos` | — (binary name) | n/a | n/a |
| Public module | `ethos-doc` | crates.io | unresolved | ☐ (reserve even if facade) |
| Public module | `ethos-rag` | crates.io | unresolved | ☐ (reserve even if facade) |
| Public module | `ethos-verify` | crates.io | unresolved | ☐ |
| Crates | `ethos-*` (core, pdf, layout, tables, security, render, cli, mcp) | crates.io | unresolved | ☐ |
| Python | `ethos-pdf` (import `ethos_pdf`) | PyPI | unresolved | ☐ |
| Node | `@ethos-pdf/core` | npm | unresolved | ☐ (scope: `@ethos-pdf`) |
| Schema namespace | `urn:ethos:schema:*` | — (URN, no registry claim) | n/a | n/a |

## Validation checklist (devrel owner)

- [ ] crates.io name search for every `ethos-*` identifier above
- [ ] PyPI search `ethos-pdf` (+ pep503 normalized forms)
- [ ] npm scope `@ethos-pdf` availability
- [x] GitHub org/repo collision scan (preliminary; 2026-06-14)
- [ ] Trademark scan (software classes) for "Ethos" in primary jurisdictions
- [ ] Record outcomes here; if any conflict → rename via this ADR before any public artifact (risk R8 trigger)

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

## Decision

Pending validation. Identifiers above are used internally in the meantime; they may change by amendment to this ADR if unavailable. Schema `$id`s use the `urn:ethos:schema:*` form precisely so schemas need no rename if package names change.
