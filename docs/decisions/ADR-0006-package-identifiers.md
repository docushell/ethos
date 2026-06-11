# ADR-0006: Package Identifiers (Registry / Trademark Validation)

- Status: **Proposed — validation due by Milestone A exit (blocking for any public artifact)**
- Date: 2026-06-11
- Governs: IMPLEMENTATION_PLAN §2 row 0.11; PRD §3.1; risk R8

## Context

The project name is **Ethos**; `ethos` is a loaded name with collision/trademark risk. Package identifiers are provisional until registries and trademark are checked. No package publish, public benchmark, or launch announcement may happen before this ADR is Accepted.

## Candidate identifiers (provisional)

| Surface | Identifier | Registry | Availability checked | Reserved |
| --- | --- | --- | --- | --- |
| CLI binary | `ethos` | — (binary name) | ☐ | n/a |
| Public module | `ethos-doc` | crates.io | ☐ | ☐ (reserve even if facade) |
| Public module | `ethos-rag` | crates.io | ☐ | ☐ (reserve even if facade) |
| Public module | `ethos-verify` | crates.io | ☐ | ☐ |
| Crates | `ethos-*` (core, pdf, layout, tables, security, render, cli, mcp) | crates.io | ☐ | ☐ |
| Python | `ethos-pdf` (import `ethos_pdf`) | PyPI | ☐ | ☐ |
| Node | `@ethos-pdf/core` | npm | ☐ | ☐ (scope: `@ethos-pdf`) |
| Schema namespace | `urn:ethos:schema:*` | — (URN, no registry claim) | n/a | n/a |

## Validation checklist (devrel owner)

- [ ] crates.io name search for every `ethos-*` identifier above
- [ ] PyPI search `ethos-pdf` (+ pep503 normalized forms)
- [ ] npm scope `@ethos-pdf` availability
- [ ] GitHub org/repo collision scan
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

## Decision

Pending validation. Identifiers above are used internally in the meantime; they may change by amendment to this ADR if unavailable. Schema `$id`s use the `urn:ethos:schema:*` form precisely so schemas need no rename if package names change.
