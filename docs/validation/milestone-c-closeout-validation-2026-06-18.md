# Milestone C Closeout Validation - 2026-06-18

## Purpose

Record the current internal Milestone C source-tree validation run after the RAG chunk and
security-report artifact hardening work landed on `main`.

This record covers the source tree's internal pre-alpha artifact-validation path only. It does
not approve public benchmark reports, release artifacts, package publication, production
positioning, or performance, quality, footprint, table-quality, or parser-quality claims.

## Status

Status: **pass for current internal Milestone C artifact-validation scope, with public blockers
unchanged**.

## Subject

- Repository: `docushell/ethos`
- Validated source HEAD before this record: `4e3adbb`
- Closeout record commit on `main`: `21d1810`
- Scope: tracked source tree, committed schemas/examples, `ethos rag chunk`, current
  `ethos security report` source-only artifact checks, and Make/static guard wiring
- Excluded: public benchmark-result publication, release artifacts, package publication,
  production positioning, public claim wording, broader table semantics, debug overlay
  implementation, and broader rendered-crop portability claims

## Commands

```sh
git switch main
git pull --ff-only
make milestone-c-internal-checks PYTHON=<jsonschema-venv>/bin/python
cargo fmt --all --check
cargo test --locked -p ethos-cli
```

The aggregate target currently composes:

- `make rag-chunk-alpha`
- `make security-report-alpha`
- `.github/scripts/test_milestone_c_closeout_record.py`
- `.github/scripts/test_milestone_c_internal_checks.py`
- `git diff --check`

## Result

```text
rag chunk CLI checks green
schema/example checks green
RAG chunk alpha target guard green
security report CLI checks green
security report example validation green
security report alpha target guard green
Milestone C closeout record guard green
Milestone C internal target guard green
cargo fmt --all --check green
cargo test --locked -p ethos-cli green
git diff --check green
```

## Current Internal Scope

- `ethos rag chunk` has deterministic committed-example coverage through
  `schemas/examples/document.example.json` and `schemas/examples/chunks.example.jsonl`.
- Chunk artifact validation fails closed on stale page, element, bbox-page, and warning
  references, including default-chunk exclusion warning references.
- `ethos security report` is present as a source-only pre-alpha artifact check over the
  committed document example.
- Security-report validation fails closed on report identity drift, warning lane drift, warning
  message drift, stale or malformed locators, inventory/report parity drift, summary drift,
  duplicate warning ids, deterministic warning-numbering drift, and unsupported current
  source-warning references.
- `make milestone-c-internal-checks` composes the current RAG chunk and security-report artifact
  gates and has a static guard for command drift.

## Remaining Boundaries

- Public benchmark reports remain blocked.
- Release artifacts and package publication remain blocked.
- Production positioning remains blocked.
- Performance, quality, footprint, table-quality, and parser-quality claims remain blocked.
- Debug overlay work remains future work outside this closeout record.
- Broader table semantics and parser-quality evaluation remain future work outside this closeout
  record.
- Cross-platform rendered artifact byte equality remains unclaimed.

## Follow-up

Use `make milestone-c-internal-checks` as the current internal Milestone C artifact-validation
command until the next milestone changes the validation contract. Contract changes should update
the Make target, its static guard, and any dated validation record that cites the target.

After this record lands, the next implementation branch should either capture explicit remaining
Milestone C follow-ups for debug/crop/table lanes or begin Milestone D prep from this documented
internal boundary.
