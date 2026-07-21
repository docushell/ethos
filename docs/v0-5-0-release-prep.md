# Ethos v0.5.0 Release Preparation

Status: **accepted implementation scope.** This document is the scoped decider request for the
four v0.5.0 deliverables. It authorizes implementation only; publication remains subject to the
freeze, target-smoke, claims, licence, determinism, and operator gates below.

## Included scope

1. Optional `ethos-full-0.5.0-macos-arm64.tar.gz` and
   `ethos-full-0.5.0-linux-x64.tar.gz` under accepted ADR-0015. Base archives and all packages
   remain caller-PDFium.
2. `ethos verify-batch` for 1–1,024 canonical citation requests against one validated source,
   with atomic canonical NDJSON output and documented aggregate exit semantics.
3. `ethos report html`, a deterministic self-contained, cropless-by-default proof view of a
   supported verification report.
4. Evidence Handle Bridge v1 trusted contexts and v2 structured model citations, including
   deterministic hydration and evidence-state projection. Citation-emission v1 remains frozen.

## Explicit exclusions

No search, indexing, embeddings, model extraction, answer-prose citation parsing, multi-document
contexts, multiple handles per claim, locator repair, XLSX adapter, artifact bundling, Windows
public artifacts, Windows-with-PDFium, `ethos-mcp`, hosted services, benchmark/production claims,
or DocuShell type-mirror retirement is in scope. Windows verify-only CI remains maintained and
unpublished.

## Deliverable boundaries and acceptance

`ethos-full` is separately named, has a relative launcher, includes only the allowlisted binary,
runtime, licence/notice material and canonical manifest, verifies profile-pinned upstream/archive
and runtime hashes, and is double-built byte-identically. It requires macOS arm64 and Linux x64
smoke, including `doctor --require-pdfium` and two identical pinned-fixture parses.

Batch validates all input before processing or writing; blank, malformed, empty, oversized, crop,
or more than 1,024 requests fail atomically. Each output line must byte-equal the corresponding
single `verify` report with only its final newline removed.

HTML has no JavaScript, network resources, timestamps, random IDs, external fonts, or
environment-dependent metadata. It escapes controlled content, preserves report/check order,
states the citation-grounding boundary, and permits crop links only with a safe relative prefix.

Evidence handles use one document fingerprint, 1–1,024 unique opaque IDs, exactly one trusted
primary locator per entry, and 1–256 model claims each with exactly one handle. Hydration fails
closed on invalid contexts, version/schema errors, and mismatches. Projection fails closed on
invalid or internally inconsistent reports; a schema-valid stale report projects every handle
with `verified=false`. Display and excerpt have no proof authority.

## Consumer and release gates

DocuShell worker integration, package/version/vendor migration, and its acceptance harness are
cross-repository work. Ethos will retain its platform-neutral type mirror in v0.5 and will not
claim that external migration complete until its separately scoped change is supplied and passes.

Every deliverable adds focused tests and an Unreleased changelog entry. Required gates include
locked workspace build/tests, schemas/examples, Python API/package tests, npm generated-type and
consumer compilation, claims gates, `cargo deny` licence/source/ban checks, release-state and
changelog validation, relevant DocuShell acceptance, and clean generated-artifact validation.
All new artifacts require double-run byte identity. Before freeze, record the 30-sample cold
single-request comparison against v0.4.0 (no more than 10% regression) and the 32-request batch
comparison (batch median at most 50% of individual-process median).

## Freeze and publication

Freeze core commit A after core validation; build all candidates and record target smoke/hashes.
Refresh npm payload/types from A and freeze npm commit B. Rebuild unaffected candidates for byte
identity, run binding performance and consumer acceptance against A/B bytes, then publish without
rebuilding. Record a closeout only after live registries and GitHub assets match accepted hashes;
confirm that no Windows artifact was published.
