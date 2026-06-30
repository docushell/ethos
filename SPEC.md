# Ethos Evidence Format (EEF)

**Version 0.2 — Public beta evaluation**

Ethos Evidence Format is an open, local-first format for representing document evidence that can
be parsed, cited, anchored, and verified. It is designed for humans, agents, RAG systems, parser
authors, and CI jobs that need to inspect what a document pipeline actually proved.

The format is intentionally small at the packaging layer: a set of JSON, JSONL, Markdown, text,
and optional crop artifacts governed by the JSON Schemas in [`schemas/`](schemas/). If you can
read files from a directory and validate JSON Schema draft 2020-12, you can consume Ethos
artifacts.

This document defines the exchange shape and conformance rules for the current Ethos artifact
family. It does not introduce a hosted API, a new command, a benchmark claim, a production
guarantee, OCR support, Windows packaged artifacts, bundled project-maintained PDFium, or semantic
answer verification.

---

## 1. Motivation

Many document and RAG systems can produce extracted text, chunks, or citations. Fewer systems make
the evidence boundary explicit enough to answer:

- Which source bytes produced this document graph?
- Which page, element, text span, table cell, or region does a citation refer to?
- Is the cited evidence fresh relative to the source fingerprint?
- Did verification fail because the claim is wrong, the locator is stale, or the parser lacks a
  required capability?
- Can a reviewer inspect the cited source region instead of trusting a model-generated citation?

EEF takes the position that document-grounded AI needs portable, deterministic evidence artifacts:
source fingerprints, stable IDs, parser capabilities, evidence refs, verification reports, and
source-inspection artifacts that survive outside one application.

### Goals

1. Define the portable artifact set that Ethos producers can write and Ethos consumers can read.
2. Keep source evidence, retrieval citations, evidence anchoring, and verification reports
   separate.
3. Make deterministic identity explicit through canonical JSON, schema versions, fingerprints,
   stable IDs, and capability declarations.
4. Allow native Ethos parser output and supported foreign parser output to share one verification
   boundary through `GroundingSource`.
5. Give agents and CI systems a small set of conformance rules for safe consumption.

### Non-goals

- Replacing the field-level JSON Schemas in [`schemas/`](schemas/).
- Defining a general-purpose document conversion, OCR, ETL, or hosted parsing format.
- Claiming semantic truth, answer quality, arithmetic correctness, pixel-level proof, or model
  entailment.
- Requiring one directory layout for every CLI invocation. Current commands produce individual
  artifacts; this document defines the recommended bundle shape for exchange.
- Making public benchmark, parser-quality, table-quality, speed, footprint, hosted, production, or
  bundled-PDFium claims.

---

## 2. Terminology

- **Evidence Bundle** — A directory or archive containing one or more Ethos artifacts for a single
  source document or a deliberately grouped set of related source documents.
- **Source Document** — The original document bytes, such as a born-digital PDF. Source bytes may
  be included, stored elsewhere, or unavailable; the source fingerprint remains the identity hook.
- **Source Fingerprint** — `sha256:<64 lowercase hex>` over the source bytes when the producer can
  bind artifacts to exact bytes.
- **Document Artifact** — The canonical Ethos document graph governed by
  [`schemas/ethos-document.schema.json`](schemas/ethos-document.schema.json).
- **Stable Payload Projection** — The canonical document payload subset used for payload hashing
  and document fingerprinting under the determinism contract.
- **Document Fingerprint** — The fingerprint of an Ethos document artifact, derived from source
  fingerprint, profile hash, config hash, payload hash, and schema version.
- **Grounding Source** — A parser-neutral evidence provider exposed through the `GroundingSource`
  contract. Native Ethos JSON is one grounding source; supported foreign parser output can be
  another.
- **Capability Declaration** — The grounding source's statement about what it can prove, such as
  spans, character offsets, tables, fingerprints, coordinate origin, and crop support.
- **Evidence Ref** — A caller-provided reference to page, text, text-region, table-cell, region, or
  other source evidence, consumed by `ethos evidence anchor`.
- **Citation Claim** — A caller-provided claim consumed by `ethos verify --citations`, such as a
  quote, value, presence, table-cell, or region claim.
- **Evidence Anchor Report** — A deterministic report showing whether evidence refs bind to source
  document evidence. This is source tracing, not semantic answer verification.
- **Verification Report** — A deterministic report showing whether citation claims are grounded in
  a grounding source. This is literal evidence grounding, not semantic answer verification.
- **Crop Descriptor** — JSON metadata describing a source-bound crop target, with optional rendered
  PNG output when caller-provided source PDF bytes and PDFium are available.
- **Deterministic Profile** — A versioned profile that pins canonicalization, quantization, ID,
  font, backend, warning, and hash-input behavior.

---

## 3. Bundle Structure

An Evidence Bundle is a directory tree of artifacts. The directory structure is a packaging
convention; the normative contracts are the schemas, deterministic profile, and command-specific
input/output rules.

```text
path/to/evidence-bundle/
├── source.pdf                         # Optional source bytes.
├── document.ethos.json                # Primary Ethos document artifact.
├── document.md                        # Optional derived Markdown projection.
├── document.txt                       # Optional derived plain-text projection.
├── chunks.jsonl                       # Optional retrieval chunks.
├── security_report.json               # Optional source/security findings.
├── citations.json                     # Optional verification input.
├── verification_report.json           # Optional verification output.
├── evidence_anchor_request.json       # Optional evidence-anchor input.
├── evidence_anchor_report.json        # Optional evidence-anchor output.
├── crops/
│   ├── crop_descriptors.jsonl         # Optional collection of crop descriptors.
│   └── <crop-ref>.png                 # Optional rendered crop artifacts.
└── profiles/
    └── ethos-deterministic-v1.json    # Optional copied deterministic profile.
```

An Evidence Bundle MAY be distributed as:

- a git repository or subdirectory;
- a tarball or zip archive;
- a build artifact emitted by CI;
- a directory passed between a parser, RAG system, verifier, and reviewer.

Consumers MUST NOT assume every optional artifact is present. A bundle containing only
`document.ethos.json` is valid if that artifact conforms to its schema. A bundle containing only
foreign parser output plus verification artifacts can still be useful when the foreign output is
adapted through `GroundingSource`.

### 3.1 Recommended filenames

The following filenames have conventional meaning when present:

| Filename | Purpose | Normative schema |
| --- | --- | --- |
| `document.ethos.json` | Canonical Ethos document graph. | [`ethos-document.schema.json`](schemas/ethos-document.schema.json) |
| `chunks.jsonl` | One retrieval chunk per line. | [`ethos-chunks.schema.json`](schemas/ethos-chunks.schema.json) |
| `security_report.json` | Document-level risk and security findings. | [`ethos-security-report.schema.json`](schemas/ethos-security-report.schema.json) |
| `citations.json` | Citation-claim input for `ethos verify --citations`. | [`ethos-citations.schema.json`](schemas/ethos-citations.schema.json) |
| `verification_report.json` | Citation evidence verification output. | [`ethos-verification-report.schema.json`](schemas/ethos-verification-report.schema.json) |
| `evidence_anchor_request.json` | Evidence-ref input for `ethos evidence anchor`. | [`ethos-evidence-anchor-request.schema.json`](schemas/ethos-evidence-anchor-request.schema.json) |
| `evidence_anchor_report.json` | Evidence anchoring output. | [`ethos-evidence-anchor-report.schema.json`](schemas/ethos-evidence-anchor-report.schema.json) |
| `crop_descriptor.json` | One crop descriptor. | [`ethos-crop-descriptor.schema.json`](schemas/ethos-crop-descriptor.schema.json) |
| `crop_descriptors.jsonl` | One crop descriptor per line. | Each line follows [`ethos-crop-descriptor.schema.json`](schemas/ethos-crop-descriptor.schema.json). |
| `document.md` | Derived Markdown projection. | Deterministic derived artifact; not schema-bound here. |
| `document.txt` | Derived plain-text projection. | Deterministic derived artifact; not schema-bound here. |

Producers MAY use different filenames when a command or application needs them. Consumers SHOULD
prefer schema identity, `artifact_type`, `schema_version`, and surrounding metadata over filename
alone when possible.

---

## 4. Core Artifacts

### 4.1 Document artifact

The document artifact is the primary native Ethos artifact. It contains:

- `schema_version`;
- parser identity;
- deterministic profile identity;
- source fingerprint and source-byte metadata;
- config and payload hashes;
- document fingerprint;
- payload: coordinate system, pages, elements, spans, tables, chunks, regions, warnings, and
  security signals;
- optional runtime diagnostics outside canonical equality.

The normative shape is
[`schemas/ethos-document.schema.json`](schemas/ethos-document.schema.json). Native Ethos document
artifacts use a top-left quantized coordinate system. The current page, span, element, table,
region, chunk, warning, finding, and check ID schemes are defined in
[`docs/determinism-contract.md`](docs/determinism-contract.md).

### 4.2 Chunk artifact

`chunks.jsonl` contains one self-describing RAG chunk per line. Each chunk carries source and
document fingerprints, text, token estimate, page refs, element refs, bounding boxes, and warnings
where applicable.

The chunk text is a deterministic projection from referenced document elements. Consumers MUST
treat chunk citations as source references, not proof by themselves. To prove a downstream answer
or citation, pass citation claims to `ethos verify` or evidence refs to `ethos evidence anchor`.

### 4.3 Citation input

`citations.json` is input to `ethos verify --citations`. It may be a bare non-empty array of claims
or an envelope carrying an optional document fingerprint plus a non-empty claim list.

Supported v1 claim kinds are:

- `quote`;
- `value`;
- `presence`;
- `table_cell`;
- `region`;
- `other`.

Unsupported or insufficiently specified claims are report data, not permission to approximate.
The verifier reports unsupported kinds, missing locators, missing required text, stale
fingerprints, and capability-blocked checks explicitly.

### 4.4 Verification report

`verification_report.json` is output from `ethos verify`. It records:

- grounding parser identity and capabilities;
- capability limits;
- fingerprint freshness;
- `all_evidence_grounded`;
- per-check status, reason, and match method;
- unsupported claim kinds;
- warnings.

Per-check statuses are currently:

- `grounded`;
- `not_found`;
- `mismatch`;
- `stale`;
- `unsupported_claim_kind`;
- `capability_blocked`;
- `error`.

`all_evidence_grounded` is true only when supported checks are grounded, no unsupported claim kinds
remain, and the evidence is not stale. A grounded report means the requested evidence matched under
declared rules. It does not mean the full answer is semantically correct.

Consumers MAY derive a proof-status view from the report for UI, CLI summary, or API wrapper use.
This derived view MUST NOT change the canonical verification report. The derived vocabulary is:

- `verified`: `all_evidence_grounded` is true;
- `partially_verified`: `all_evidence_grounded` is false, but at least one check is reusable;
- `unverified`: no check is reusable.

A check is reusable only when `checks[].status` is `grounded`, `checks[].semantic_unverified` is
false, and `fingerprint_stale` is false. `partially_verified` therefore means "some check IDs are
reusable"; it does not certify the request as submitted. Derived proof limitations SHOULD surface
capability limits, stale fingerprints, unsupported claim kinds, non-grounded checks, and
semantic-unverified checks.

### 4.5 Evidence anchor request

`evidence_anchor_request.json` is input to `ethos evidence anchor`. It contains an
`artifact_type` of `ethos.evidence_anchor_request.v1`, schema version `1.0.0`, an optional source
fingerprint, and caller-provided evidence refs.

Supported v1 evidence kinds are:

- `page`;
- `text`;
- `text_region`;
- `table_cell`;
- `region`;
- `other`.

Required anchor levels are:

- `page`;
- `text`;
- `bbox`;
- `text_bbox`;
- `table_cell`.

Evidence-anchor requests use `ethos_quantized_top_left_v1` for coordinate-profile identity and
`ethos_collapse_whitespace_v1` for text-normalization identity where those fields apply.

### 4.6 Evidence anchor report

`evidence_anchor_report.json` is output from `ethos evidence anchor`. It contains an
`artifact_type` of `ethos.evidence_anchor_report.v1`, schema version `1.0.0`, grounding identity,
capabilities, and one anchor result per input evidence ref.

Anchor statuses are currently:

- `bound`;
- `mismatch`;
- `not_found`;
- `stale_fingerprint`;
- `capability_limited`;
- `unsupported_evidence_kind`.

Evidence anchoring answers the narrow question "does this evidence ref bind to source evidence?"
It does not answer "is this natural-language answer true?"

### 4.7 Crop descriptors and rendered crops

A crop descriptor identifies a source-bound page and bounding box with a deterministic `crop_ref`,
document fingerprint, check IDs where applicable, text hash, and rendering status.

`rendering_status` is either:

- `descriptor_only`;
- `rendered`.

Rendered crop artifacts are PNG when present. Rendering requires caller-provided source PDF bytes
and a configured PDFium runtime. Logical crop descriptors remain useful even when rendered PNGs are
not available.

### 4.8 Security report

`security_report.json` records document-level findings and inventories such as hidden text,
annotations, actions, attachments, scripts, links, and related warnings when supported by the
current extractor.

Consumers SHOULD surface security warnings near chunks, citations, and verification results when
they affect trust in source evidence.

### 4.9 Derived Markdown and text

`document.md` and `document.txt` are deterministic derived projections from the canonical document
graph and exporter configuration. They are useful for human review and retrieval workflows, but
they are not the primary evidence identity. Use the document artifact, chunks, citations,
verification reports, and evidence-anchor reports for source-grounding decisions.

---

## 5. Identity, Canonicalization, and Fingerprints

Ethos identity is hash- and schema-driven.

### 5.1 Hash form

All prefixed fingerprints use:

```text
sha256:<64 lowercase hex>
```

Important fingerprints and hashes include:

| Name | Meaning |
| --- | --- |
| `source.fingerprint` / `source_fingerprint` | Hash of original source bytes when available. |
| `payload_sha256` | Hash of the canonical stable payload projection. |
| `profile.sha256` | Hash of the deterministic profile artifact. |
| `config_sha256` | Hash of the effective config subset that changes stable output. |
| `fingerprint` / `document_fingerprint` | Document-level fingerprint used for freshness checks. |
| `verification_config_sha256` | Hash of verification config semantics stamped into reports. |

### 5.2 Canonical JSON

Canonical JSON follows c14n v1 in [`docs/determinism-contract.md`](docs/determinism-contract.md):
UTF-8, no insignificant whitespace, sorted object keys, integers only, stable string escaping, and
no duplicate keys. Runtime diagnostics are outside canonical equality.

Consumers that compare fingerprints SHOULD compare the hash fields rather than reimplement every
producer pipeline. Producers that emit new canonical Ethos artifacts MUST use the repository c14n
implementation or an implementation proven against the same vectors.

### 5.3 IDs and ordering

Native Ethos IDs are deterministic functions of canonical order. Current native forms include:

| Kind | Format |
| --- | --- |
| page | `p%04d` |
| span | `s%06d` |
| element | `e%06d` |
| table | `t%04d` |
| region | `r%04d` |
| chunk | `c%06d` |
| warning | `w%04d` |
| finding | `f%04d` |
| verification check | `v%04d` |

Foreign grounding sources MAY expose different source-native IDs. Their adapters MUST keep page
identity, element identity, table-cell identity, coordinate origin, and capability limits explicit
instead of silently pretending to be native Ethos output.

---

## 6. Grounding and Verification

Ethos separates four layers that are often collapsed in RAG systems:

```text
source bytes
    ↓
document or foreign parser artifact
    ↓
GroundingSource
    ↓
evidence anchor report or verification report
```

Retrieval citations, source refs, evidence refs, and verification outcomes are related, but they
are not the same object.

### 6.1 GroundingSource rules

A grounding source SHOULD:

- return deterministic pages, elements, spans, tables, and regions in stable order;
- use explicit parser identity;
- expose a source fingerprint when it can bind evidence to exact bytes;
- declare missing spans, character offsets, tables, fingerprints, coordinate origin, and crop
  support as capability limits;
- fail closed on malformed locators, negative coordinates, impossible page references, and
  out-of-page boxes;
- keep table-cell text projection distinct from Markdown table rendering.

### 6.2 Verification rules

`ethos verify` checks caller-provided citation claims against a grounding source. It MAY use exact
text, normalized text, containment, table-cell lookup, bounding-box containment, or presence-only
matching depending on claim kind and available capabilities.

Verifier consumers MUST inspect:

- `fingerprint_stale`;
- `all_evidence_grounded`;
- every `checks[].status`;
- every `checks[].reason` when present;
- `capability_limits`;
- `unsupported_claim_kinds`;
- `warnings`.

Consumers MUST NOT treat a citation string, retrieval chunk, LLM answer, or model-returned evidence
ID as proof until the evidence has been checked against a trusted grounding source.
If a wrapper exposes an `invalid_request` status, it is a process or API envelope for malformed
input and MUST NOT be derived from a `VerificationReport`.

### 6.3 Evidence anchor rules

`ethos evidence anchor` checks caller-provided evidence refs against a single source artifact. It
is useful when a downstream application already has evidence IDs or locators and needs to prove
that those refs are still bound to the source.

Evidence-anchor consumers MUST inspect each anchor independently. A non-bound anchor is report
data. Request/schema/source-shape errors are tool usage errors.

---

## 7. Cross-linking and Source Inspection

EEF artifacts link through explicit IDs and fingerprints rather than markdown-only links.

Common relationships include:

- chunk `element_refs` → document payload elements;
- chunk `page_refs` → document payload pages;
- citation claim locator → grounding source page, element, span, table, or region;
- verification check ID → crop descriptor `check_ids`;
- evidence ref ID → evidence anchor report anchor;
- crop descriptor `document_fingerprint` → document artifact fingerprint;
- source and document fingerprints → source freshness checks.

Consumers SHOULD preserve unresolved refs as unresolved. They MUST NOT guess a page, element,
table cell, or crop when a locator cannot be resolved.

Human-facing source-inspection UIs SHOULD show:

- the cited text or cell;
- page identity and page index;
- bounding box where available;
- source fingerprint freshness;
- parser identity and capability limits;
- warnings that may affect trust in the evidence.

---

## 8. Conformance

An Evidence Bundle is **conformant with EEF 0.2** if every included Ethos artifact satisfies the
schema and artifact rules that apply to it.

At minimum:

1. Every `.json` Ethos artifact with a schema in [`schemas/`](schemas/) MUST validate against that
   schema.
2. Every `.jsonl` Ethos artifact MUST contain one valid JSON value per non-empty line, and each
   line MUST validate against the corresponding schema.
3. Every declared `artifact_type` and `schema_version` MUST match the schema that governs the
   artifact.
4. Every prefixed fingerprint MUST use `sha256:<64 lowercase hex>`.
5. Native Ethos document artifacts MUST keep runtime diagnostics outside canonical equality.
6. Producers MUST NOT silently upgrade missing source capabilities into stronger evidence claims.
7. Consumers MUST tolerate missing optional artifacts.
8. Consumers MUST tolerate unknown additive fields only when the governing schema version permits
   them. Current public schemas generally use `additionalProperties: false`, so unknown fields are
   rejected unless a schema deliberately allows them.
9. Consumers MUST preserve non-grounded, non-bound, stale, unsupported, and capability-limited
   outcomes as explicit states.
10. Consumers MUST NOT reinterpret evidence anchoring or citation verification as semantic answer
    verification.

Recommended validation command from a source checkout:

```bash
python3 schemas/validate_examples.py
```

Focused verification and evidence-anchor guard targets include:

```bash
make verify-alpha
make evidence-anchor-v1-contract PYTHON=python3
```

Use the repository's current documented Python environment requirements when running those targets.

---

## 9. Compatibility and Versioning

EEF 0.2 follows the repository's v0.2.x compatibility policy:

- verification report schema shape and field meanings are stable across compatible `0.2.x`
  updates;
- evidence-anchor request and report schema shape and field meanings are stable across compatible
  `0.2.x` updates;
- `GroundingSource` obligations and default verification-config semantics are stable across
  compatible `0.2.x` updates;
- CLI JSON input/output shape for `ethos verify` and `ethos evidence anchor` is stable across
  compatible `0.2.x` updates.

Compatible `0.2.x` changes may add diagnostics, warnings, examples, tests, documentation
clarifications, and bug fixes that make invalid input fail closed.

Breaking changes require a contract-change PR, changelog entry, migration note, schema/example
updates, and public-claims review. Examples of breaking changes include removing or renaming public
fields, changing report meaning, changing default fingerprint behavior, changing
`GroundingSource` obligations, or reclassifying normal verification verdicts as tool failures.

---

## 10. Relationship to Other Formats

EEF is intentionally close to established file-based exchange patterns:

- JSON Schema-governed build artifacts;
- JSONL retrieval chunk exports;
- markdown and text projections for human review and lightweight retrieval;
- provenance metadata stored next to source outputs;
- parser adapters that expose a common trait rather than forcing one parser schema.

EEF differs by making the trust boundary explicit. It treats document evidence as something that
can be fingerprinted, cited, anchored, downgraded by capability, and verified deterministically.

Foreign parser outputs do not need to become native Ethos JSON to participate. They need an adapter
that exposes the evidence they can actually prove through `GroundingSource`.

---

## Appendix A — Minimal Native Bundle

```text
minimal-native/
├── document.ethos.json
├── citations.json
└── verification_report.json
```

Verification command:

```bash
ethos verify document.ethos.json \
  --citations citations.json \
  --fail-on-ungrounded \
  --out verification_report.json
```

Consumer rule:

1. Validate `document.ethos.json`.
2. Validate `citations.json`.
3. Validate `verification_report.json`.
4. Treat the answer as evidence-grounded only if `all_evidence_grounded` is true, every supported
   check is `grounded`, `fingerprint_stale` is false, unsupported claim kinds are empty, and no
   capability limit invalidates the intended use.
5. If deriving partial output, assemble it only from reusable grounded checks; the original request
   remains uncertified until all required checks pass.

---

## Appendix B — Minimal Evidence Anchor Bundle

```text
minimal-anchor/
├── document.ethos.json
├── evidence_anchor_request.json
└── evidence_anchor_report.json
```

Evidence-anchor command:

```bash
ethos evidence anchor document.ethos.json \
  --evidence-refs evidence_anchor_request.json \
  --out evidence_anchor_report.json
```

Consumer rule:

1. Validate the source artifact and evidence-anchor request.
2. Validate `evidence_anchor_report.json`.
3. Inspect every anchor. `bound` means the requested evidence ref binds at the achieved anchor
   level. `mismatch`, `not_found`, `stale_fingerprint`, `capability_limited`, and
   `unsupported_evidence_kind` remain explicit non-bound outcomes.

---

## Appendix C — Foreign Parser Verification Bundle

```text
foreign-parser-verification/
├── source.foreign.json
├── citations.json
└── verification_report.json
```

Verification command shape:

```bash
ethos verify source.foreign.json \
  --grounding opendataloader-json \
  --citations citations.json \
  --out verification_report.json
```

Consumer rule:

1. Treat the foreign parser output as source evidence only through the selected grounding adapter.
2. Inspect grounding parser identity and capability limits before trusting the result.
3. Do not assume missing spans, missing tables, missing fingerprints, unknown coordinate origin, or
   missing crop support are harmless. They are part of the evidence verdict.
