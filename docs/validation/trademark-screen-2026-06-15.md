# Trademark Screen Record - 2026-06-15

## Purpose

Record the release-blocking trademark validation work for the `Ethos` product name and
selected public package identifiers.

This is an engineering release-readiness record, not legal advice and not trademark
clearance. ADR-0006 remains proposed until a manual/legal review signs off or chooses a
rename.

## Current Decision

Status: **blocked pending manual/legal trademark review**.

The package registry reservations are complete for the priority public surfaces, but the
project name `Ethos` is not cleared for public launch claims, public package promotion, or
public benchmark publication.

## Product Scope To Screen

Screen the mark `Ethos` for software and developer-tool use around:

- deterministic document parsing;
- citation grounding verification;
- document evidence, provenance, and audit artifacts;
- CLI/API/library distribution;
- future hosted or agent-workflow integrations if planned.

Initial software-relevant Nice classes:

- Class 9: downloadable software, CLI tools, SDKs, libraries, machine-readable data files.
- Class 42: SaaS, software engineering, hosted verification, API services.

Class 35 should be added only if the launch plan includes marketplace, business consulting,
or advertising/analytics services under the `Ethos` mark.

## Official Sources

| Source | URL | Status | Notes |
| --- | --- | --- | --- |
| USPTO search guidance | `https://www.uspto.gov/trademarks/search` | reachable | Official page links to the Trademark Search system and recommends signing in for reliability during heavy traffic. |
| USPTO comprehensive clearance guidance | `https://www.uspto.gov/trademarks/search/comprehensive-clearance-search-similar-trademarks` | reachable | USPTO says comprehensive clearance includes federal records, state/business registries, domain names, Madrid/WIPO, EUIPO/TMview, and common-law internet use. |
| USPTO Trademark Search | `https://tmsearch.uspto.gov/search/` | reachable UI; automated probe blocked | Manual logged-in search required. |
| USPTO search app configuration | `https://tmsearch.uspto.gov/configuration.json` | reachable | Exposes `serviceUrlSearchElastic` as `https://tmsearch.uspto.gov/prod-v1-0-0/`. |
| WIPO Global Brand Database | `https://branddb.wipo.int/en/` | reachable UI; automated probe challenged | Manual search required because automated quick-search returned captcha/verification. |
| EUIPO search availability | `https://www.euipo.europa.eu/en/search-availability` | automated probe blocked | Manual search required. |
| UK IPO trademark search | `https://www.gov.uk/search-for-trademark` | reachable | Manual search recommended if UK launch or UK customer targeting is planned. |

## Searches Required Before ADR Acceptance

The reviewer should save dated screenshots or exported results for each completed search.

| Jurisdiction/source | Required queries | Required filters | Acceptance evidence |
| --- | --- | --- | --- |
| USPTO Trademark Search | `ETHOS`, exact wordmark and broad text search; similar spellings if surfaced by search UI | live + pending, dead marks separately noted; classes 9 and 42 first | result count, candidate conflicts, serial/registration numbers, owner, goods/services, live/dead status |
| WIPO Global Brand Database | `ETHOS` | software/developer-tool related goods/services where filters allow | result count and material candidate conflicts |
| EUIPO/TMview | `ETHOS` | EU marks, classes 9 and 42 first | result count and material candidate conflicts |
| UK IPO | `ETHOS` | classes 9 and 42 first if UK target is in scope | result count and material candidate conflicts |
| Common-law web search | `"Ethos" software`, `"Ethos" document`, `"Ethos" verification`, `"Ethos" AI`, `"Ethos" PDF`, `"Ethos" SaaS` | current commercial use | material third-party software/developer-tool use |
| Domain/package adjacency | `ethos.dev`, `ethos.ai`, `ethos.so`, `ethos.com`, public package registries | exact and confusingly similar technical products | collision notes, if any |

## Conflict Review Criteria

Escalate to counsel or choose a rename if a live or pending mark appears materially close on:

- exact or near-exact wordmark `ETHOS`;
- software, SaaS, AI, document management, developer tools, data provenance, compliance,
  security, or verification goods/services;
- overlapping customer channels such as developer tooling, enterprise AI, document AI, or
  compliance workflows;
- strong common-law use even without active registration.

Do not clear the name based only on package registry ownership. Package reservation prevents
namespace squatting; it does not answer trademark risk.

## Current Evidence

Engineering checks completed on 2026-06-15:

- USPTO official search page and comprehensive-clearance guidance were reachable.
- USPTO Trademark Search UI was reachable, but direct unauthenticated API probing returned
  HTTP 403, so no federal trademark result set was captured.
- WIPO Global Brand Database was reachable, but automated quick-search returned a
  captcha/verification page, so no WIPO result set was captured.
- EUIPO automated search-availability probe returned HTTP 403, so no EUIPO result set was
  captured.
- UK IPO search page was reachable, but no manual result set was captured.

Conclusion: **no clearance result exists yet**.

## Release Gate

ADR-0006 may move from `Proposed` to `Accepted` only after one of these outcomes is recorded:

- legal/manual review clears `Ethos` for the intended public use;
- legal/manual review clears `Ethos` with constraints, and those constraints are added to
  public naming and claim rules;
- legal/manual review rejects the name, and ADR-0006 records the replacement naming plan.

Until then, public GitHub launch, public benchmark release, and public package promotion remain
blocked.
