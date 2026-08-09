# Ethos v0.6.0 Release Preparation

> **This document covers the Grounding JSON portion of v0.6.0 only.** That work is complete
> and merged. On 2026-08-09 v0.6.0 was expanded into the major format release; scope
> authority for the remaining work is `docs/proof-statement-v1.md`, and the task board is
> in `docs/proof-statement-v1-implementation-plan.md`.
>
> Everything below stays accurate for what it describes. It is no longer the whole picture.

Status: **accepted as the scoped v0.6.0 decider request** (2026-07-30), satisfying precondition
§3.1. Implementation is authorized through WP-3 and has landed.

This acceptance does **not** authorize publication, production positioning, or any new public
claim. Those remain gated on the release gates in §12 and the claims approval lane.

Decider rulings recorded since acceptance:

- Fingerprint identity is `representation_sha256` (§6.4, §8.1, ADR-0016).
- Public install wording advances to the published `0.5.0` baseline, verified against crates.io,
  PyPI, npm, and the GitHub Release.
- `--source-artifact` on `verify` and `verify-batch` is cut; source binding stays on
  `grounding check`. Two additions are kept and recorded in ADR-0016.

Date prepared: 2026-07-29. Accepted: 2026-07-30.

> Implementation record: [`v0-6-0-release.md`](v0-6-0-release.md) records what was actually built
> and verified against this plan, including the points where the implementation and this document
> disagree. Read it alongside this one.

## 1. Release decision

Ethos v0.6.0 should be an **adoption release**, not a receipt-platform release.

Add one strict, language-neutral `ethos.grounding.v1` JSON artifact in front of the existing
parser-neutral `GroundingSource` boundary. A parser written in any language maps its supported
PDF output into that artifact once. Ethos validates the artifact, loads it through the existing
verification path, and emits the existing `verification_report.json`.

Add only the developer surfaces required to make that path usable:

- exact artifact-type detection in the existing CLI source loader;
- `ethos grounding check`;
- generated TypeScript declarations;
- two narrow native-backed npm functions for validation and verification; and
- one JavaScript and one Python mapper example over the same synthetic parser result.

The intended architecture is:

```text
existing parser in any language
  -> one deterministic mapper owned by that integration
  -> ethos.grounding.v1 JSON
  -> one shared Ethos loader and validator
  -> existing GroundingSource
  -> existing ethos-verify algorithm
  -> existing canonical verification_report.json
  -> caller pipeline or DocuShell
```

This release must not add a plugin runtime, mapping language, parser-specific SDK, hosted service,
receipt, proof package, signing system, or exact-replay protocol.

### 1.1 Honest feasibility answer

The parser/pipeline goal is feasible in v0.6.0 because it needs one exchange contract and a thin
loader around an architecture that already exists. It does not require a new verification
algorithm or a change to the public report.

DocuShell can begin a paid managed-service experiment with this release—and can begin against the
current report path before v0.6.0—but an Ethos version cannot prove monetization. Revenue requires
external users who repeatedly choose managed operation, integration help, support, or workflow
controls over self-hosting. That evidence belongs to DocuShell's commercial lane.

The former full receipt/proof/replay proposal is deferred as its own separate release decision and
is not part of the active v0.6.0 scope.

## 2. Why this is the minimum sufficient architecture

The existing architecture already has the correct internal seam:

```text
GroundingSource -> ethos-verify -> VerificationReport
```

The adoption problem is at the process boundary. Today:

- Rust consumers can implement `GroundingSource`;
- the CLI accepts native Ethos JSON;
- the CLI hardcodes one foreign adapter, `opendataloader-json`; and
- non-Rust parser owners have no small, frozen artifact they can emit directly.

`ethos.grounding.v1` closes that gap without multiplying verification implementations.

| Option | Benefit | Cost or failure mode | v0.6 decision |
| --- | --- | --- | --- |
| One strict Grounding JSON artifact | Language-neutral, offline, inspectable, testable, and uses the existing verifier | Each parser still needs one explicit deterministic mapper | **Include** |
| More parser-specific Rust adapters | Good native fidelity for each selected parser | Ethos owns an open-ended adapter matrix and non-Rust users still need Rust | Defer until measured demand selects one |
| Dynamic plugins | In-process extensibility | ABI, sandboxing, discovery, dependency, and support surface | Exclude |
| Automatic arbitrary-JSON mapping | Low apparent setup | Guesses IDs, geometry, order, and capabilities; cannot fail closed honestly | Exclude |
| A mapping DSL | Avoids writing mapper code | Creates another language, validator, debugger, and versioned public surface | Exclude |
| Independent SDK implementation per language | Familiar APIs | Verification and canonical behavior can drift across runtimes | Exclude |
| Hosted-only API | Operationally simple for some users | Requires accounts, network access, data transfer, and DocuShell trust | DocuShell may offer it; Ethos remains offline |
| Receipt/proof/exact replay in the same release | Stronger future portability story | Separate schemas, canonicalization freeze, executable identity, storage threat model, new exits, and retained-binary operations | Defer as its own release decision |

The unavoidable cost is a mapper that knows the source parser's semantics. Ethos cannot safely
remove that work: stable IDs, reading order, coordinate conversion, and capability declarations
must come from the parser owner or integration.

## 3. Preconditions and authority

Before implementation:

1. Accept this document as the scoped v0.6.0 decider request, or create an issue that points to it.
2. Add and accept one Grounding JSON v1 ADR using the next available ADR number.
3. Reconcile the completed v0.5.0 release with `docs/execution-status.md`.
4. Freeze the schema, invariant rules, stable validation codes, and measured resource limits in
   the accepted ADR.
5. Keep `README.md` and `docs/public-boundary-claims.json` unchanged unless exact new wording
   passes the claims approval lane.
6. Add a `CHANGELOG.md` entry under `Unreleased` in every implementation change.

Authority for implementation, in order:

1. Accepted scoped issue or this accepted decider request.
2. This release-prep document.
3. The accepted Grounding JSON ADR.
4. `docs/execution-status.md`.
5. Approved public wording.
6. `SPEC.md`, `docs/determinism-contract.md`, and existing accepted ADRs.

If two authorities conflict, stop and request a decider resolution.

The uncommitted DocuShell future-architecture documents informed the commercial analysis but are
not Ethos implementation authorities and do not block this adoption release. The public
DocuShell consumer acceptance fixture must bind to an exact reviewed DocuShell commit before
v0.6.0 closeout.

## 4. Verified starting point

The plan is based on repository state inspected on 2026-07-29:

- `main` is at `d405495`, the local v0.5.0 publication closeout.
- Tag `v0.5.0` exists at `bfb7197`.
- `docs/execution-status.md`, `README.md`, and `docs/public-boundary-claims.json` still describe
  v0.4.0 as the approved public baseline. That conflict requires the existing release-truth lane.
- `GroundingSource` is already the sole parser/verifier boundary.
- `ethos-verify` depends only on the parser-neutral grounding feature and not on `ethos-pdf`,
  PDFium, layout, or parser internals.
- Native Ethos documents and the approved OpenDataLoader adapter already reach the same
  `ethos_verify::verify_claims` function.
- CLI dispatch is duplicated between verification and evidence anchoring and recognizes only
  native Ethos JSON plus explicit `opendataloader-json`.
- The public `GroundingSource` page, element, span, table, and cell structures require integer
  geometry. Accepting geometry-less sources would require a separate compatibility decision.
- The npm package is a native CLI binary distribution with generated types. It has no
  programmatic runtime entry point.
- DocuShell is a proven first consumer of the public CLI and OpenDataLoader path. Its friction
  log shows that binary invocation, type drift, adapter flags, and consumer-authored mappings are
  real adoption costs.
- Ethos is Apache-2.0 by accepted ADR-0004. Users may self-host or build competing services, so
  commercial capture cannot rely on restricting use of the Ethos binary.

## 5. Goal, success criteria, and non-goals

### 5.1 Release success

v0.6.0 succeeds only if all of these are supported by tests and release evidence:

- A parser integration written in JavaScript or Python can reach the existing verifier without
  Rust, PDFium, a running service, an Ethos account, or a network call after installation.
- The integration emits one strict `ethos.grounding.v1` artifact; it does not add code inside
  Ethos.
- `ethos grounding check` uses the same parser and invariant validator as `ethos verify`.
- `ethos verify` auto-detects only exact `artifact_type="ethos.grounding.v1"`.
- Existing native and explicit OpenDataLoader verification inputs, report bytes, defaults, and
  exits remain compatible.
- The existing `verification_report.json` schema and semantics remain unchanged.
- Invalid IDs, references, order, capabilities, coordinates, duplicate keys, unknown fields, and
  resource-limit excesses fail closed with one stable bounded error.
- Supplying the original PDF to `grounding check` independently confirms or rejects the declared
  source hash.
- A source-hash match is never presented as proof that a foreign parser extracted the PDF
  faithfully.
- Grounding JSON verification does not require PDFium.
- Generated TypeScript declarations and runtime validation agree on the frozen schema.
- The npm functions preserve CLI exit and report semantics and do not implement verification in
  JavaScript.
- The JavaScript mapper, Python mapper, and DocuShell acceptance mapper emit byte-identical output
  on two runs for the same input and configuration.
- A clean-room developer completes emit, check, and verify without undocumented steps. Any
  required private knowledge blocks release.
- Every new output artifact is byte-identical on repeated runs under identical inputs.

### 5.2 Included scope

- One `ethos.grounding.v1` JSON Schema and built-in CLI adapter.
- One deterministic grounding-validation report schema.
- One shared CLI source loader used by `verify`, `verify-batch`, and `evidence anchor`.
- Exact artifact-type detection.
- One `ethos grounding check` command with optional original-PDF hash comparison.
- Generated Grounding JSON and validation-report TypeScript declarations in the existing npm
  package.
- Two Promise-based npm functions: `checkGrounding` and `verifyClaims`.
- One JavaScript and one Python mapper example over the same synthetic parser output.
- One clean-room quickstart.
- One DocuShell consumer acceptance lane using public Ethos surfaces only.

### 5.3 Explicit exclusions

- Verification-report changes.
- Receipt, attestation, proof-package, signing, ledger, checkpoint, or exact-replay protocols.
- Executable identity or new replay exit codes.
- New PDF parsing behavior or parser-quality claims.
- New parser-specific adapters beyond the existing OpenDataLoader adapter.
- Geometry-less or free-text-only grounding profiles.
- Dynamic plugins, WASM adapters, Python plugin loading, adapter marketplaces, or mapping DSLs.
- Automatic arbitrary-JSON field inference, ID repair, coordinate guessing, capability guessing,
  or source-hash repair.
- DOCX, XLSX, PPTX, image/OCR, email, web, or tool-output profiles.
- Search, indexing, embeddings, RAG, answer generation, agents, semantic judgment, policy, or
  workflow orchestration.
- A hosted Ethos API or production positioning.
- A new npm package, Python public API, Rust public crate, per-platform npm package, or MCP surface.
- Windows artifact publication. The existing verify-only implementation remains a separately
  governed release-target decision and must not delay the adoption boundary.
- Pricing commitments, revenue claims, or a claim that DocuShell monetization is proven.

## 6. Architecture contract

### 6.1 One internal boundary

Do not add another verification algorithm.

```text
native Ethos JSON -----------\
OpenDataLoader JSON ----------> GroundingSource -> verify_claims -> VerificationReport
ethos.grounding.v1 JSON ------/
```

The new code ends at `GroundingSource`. All check matching, capability downgrades, staleness,
warnings, report construction, and canonical report output remain owned by the existing verifier.

### 6.2 One external exchange artifact

Add:

```text
schemas/ethos-grounding-source.schema.json
```

Artifact identity:

```json
{
  "artifact_type": "ethos.grounding.v1",
  "schema_version": "1.0.0"
}
```

The minimum complete shape is:

```json
{
  "artifact_type": "ethos.grounding.v1",
  "schema_version": "1.0.0",
  "source": {
    "media_type": "application/pdf",
    "sha256": "sha256:<64-lowercase-hex>"
  },
  "producer": {
    "name": "example-parser",
    "version": "1.2.3"
  },
  "capabilities": {
    "spans": false,
    "char_offsets": false,
    "tables": false
  },
  "coordinate_system": {
    "unit": "centipoint",
    "origin": "top-left"
  },
  "pages": [
    {
      "id": "page-1",
      "index": 1,
      "width": 61200,
      "height": 79200,
      "rotation": 0
    }
  ],
  "elements": [
    {
      "id": "block-17",
      "page": "page-1",
      "bbox": [7200, 8400, 54000, 10200],
      "kind": "text_block",
      "text": "Revenue increased to $12.4 million."
    }
  ]
}
```

Optional top-level arrays are `spans` and `tables`. There is no metadata or extension object in
v1. `additionalProperties: false` applies at every object boundary.

### 6.3 Fixed semantics

- `source.media_type` is exactly `application/pdf`.
- `source.sha256` is the integration's declaration of the original PDF byte hash.
- `producer.name` and `producer.version` are required bounded declarations, not authenticated
  identities.
- Page indexes are unique, 1-based, and ascending.
- Page, element, span, and table IDs are required and unique within their typed namespace.
- IDs match `^[A-Za-z0-9][A-Za-z0-9._:-]*$`.
- Every referenced page, element, and table exists.
- Element order is the producer's deterministic reading order and is semantically significant.
- `element.kind` is a bounded lowercase identifier.
- Element text is optional because the existing `GroundingElement` permits non-text elements.
- `unit` is exactly `centipoint`, one hundredth of a PDF point.
- `origin` is exactly `top-left`, with x increasing right and y increasing down.
- Page dimensions and bounding boxes are c14n-safe integers.
- Rotation is exactly `0`, `90`, `180`, or `270`.
- Every box is `[x0,y0,x1,y1]`, has positive area, and lies within its page.
- A mapper converting PDF-point floats uses the existing
  `round_half_away_from_zero(points * 100)` rule. Ethos does not guess or silently convert units.
- Optional fields are omitted rather than set to `null`.
- Floating-point numbers are rejected.

The complete schema must reuse existing `GroundingSource` meanings rather than invent parallel
verification concepts.

### 6.4 Capabilities

The producer declares only:

- `spans`;
- `char_offsets`; and
- `tables`.

Grounding JSON fixes fingerprint support to true, coordinate origin to top-left, crop support to
false, adapter ID to `ethos-grounding-json`, and adapter version to `1.0.0`.

The fingerprint **value** is `representation_sha256`, the hash of the accepted Grounding JSON
bytes, as accepted in ADR-0016 and ruled by the decider on 2026-07-30. `source.sha256` remains a
separate optional binding to the original PDF and is never substituted for the fingerprint.

The reasoning: the verifier only ever observes the Grounding JSON. Recording a PDF hash it never
read as "what was verified" would be a claim Ethos cannot support, and it would let a silently
re-mapped artifact with different geometry present as fresh. The accepted cost is that re-emitting
the artifact changes the fingerprint — including a `producer.version` bump against an unchanged
PDF — so citations bound to a previous representation correctly report `stale`.

Rules:

- `char_offsets=true` requires `spans=true`.
- Supplied spans are forbidden when `spans=false`.
- Supplied tables are forbidden when `tables=false`.
- Character offsets are zero-based Unicode scalar indexes with an exclusive end.
- When offsets are declared, the referenced scalar slice must equal the span text exactly.
- Empty span or table arrays do not change declared capability.
- Ethos never upgrades a false declaration by inspecting one document.

Missing capabilities remain explicit verifier downgrades. They are never approximated.

### 6.5 IDs, tables, and ordering

- A span and its owning element reference the same page.
- Cells use `(table_id,row,col)`; no new cell ID is added because `GroundingCell` has none.
- Rows and columns are zero-based.
- Row and column spans are positive.
- Cells are ordered by ascending `(row,col)` and occupied ranges do not overlap.
- Checked arithmetic is used for cell ranges.
- The validator preserves submitted array order. It does not sort or repair the artifact.

A mapper for a parser without native stable IDs may derive ordinal IDs only after that parser has
established deterministic output order. That derivation belongs to the mapper and must pass a
double-run test. Ethos never generates IDs during loading.

### 6.6 Honest geometry limitation

Grounding JSON v1 requires page geometry and element boxes because the released
`GroundingSource` contract requires them. This means some text-only parsers cannot use this
profile honestly.

Do not use page-sized boxes, zero boxes, or invented coordinates to admit such parsers. Making
geometry optional would reshape a public trait and verification assumptions; it requires a
separate compatibility decision informed by real blocked integrations.

## 7. Strict validation and source loading

### 7.1 One strict parser

Add one reusable strict JSON parser behind the existing full/core boundary. Use it for the new
Grounding JSON and validation-report inputs only.

It must reject:

- invalid UTF-8 or JSON;
- a UTF-8 BOM;
- duplicate object keys at any depth before value construction;
- unknown fields;
- `null` where not explicitly allowed;
- floats, exponent forms, and integers outside the accepted safe range;
- oversized input, arrays, strings, or IDs before retaining unbounded data; and
- every invariant violation in section 6.

Existing native Ethos and OpenDataLoader input parsing remains unchanged in v0.6.0.

Return one deterministic first error. Precedence is:

1. byte limit, UTF-8, syntax, duplicate keys, and streaming container/string limits;
2. artifact and schema identity;
3. typed shape and unknown fields;
4. capability combinations;
5. pages in input order;
6. elements in input order;
7. spans in input order;
8. tables and cells in input order; and
9. optional source-PDF preflight and hash comparison.

Messages are bounded Ethos-owned text. Do not copy parser-library diagnostics, document text,
local paths, or unbounded values into a deterministic report.

### 7.2 Grounding check

Add:

```text
schemas/ethos-grounding-validation-report.schema.json
```

Command:

```text
ethos grounding check <grounding.json>
  [--source-artifact <document.pdf>]
  --out <grounding-validation.json>
```

Successful output:

```json
{
  "artifact_type": "ethos.grounding_validation.v1",
  "schema_version": "1.0.0",
  "structure": "valid",
  "source_binding": "matched",
  "representation_sha256": "sha256:...",
  "counts": {
    "pages": 1,
    "elements": 1,
    "spans": 0,
    "tables": 0
  }
}
```

Invalid output contains one error:

```json
{
  "artifact_type": "ethos.grounding_validation.v1",
  "schema_version": "1.0.0",
  "structure": "invalid",
  "source_binding": "not_checked",
  "error": {
    "code": "duplicate_element_id",
    "path": "/elements/8/id",
    "message": "element id must be unique"
  }
}
```

Rules:

- `representation_sha256` hashes the exact accepted Grounding JSON bytes.
- Without `--source-artifact`, source binding is `not_checked`, never `matched`.
- With source bytes, validate the configured size and PDF magic, stream SHA-256 once, and compare
  it with `source.sha256`.
- A match proves only that the mapper declared the supplied PDF hash. It does not prove faithful
  extraction.
- Structural validity with binding `matched` or `not_checked` exits `0`.
- Invalid structure, invariant failure, limit failure, malformed PDF, or source mismatch writes
  the bounded result where safe and exits `2`.
- Outputs are atomic and deterministic.

### 7.3 Shared source selection

Read bounded input bytes once. Use one internal loader from `verify`, `verify-batch`, and
`evidence anchor`:

1. An existing explicit `--grounding` option selects that existing path.
2. Otherwise inspect only the optional top-level `artifact_type`.
3. Exact `ethos.grounding.v1` selects the new strict loader.
4. An absent `artifact_type` selects the existing native Ethos loader.
5. A duplicate, non-string, unknown, or unsupported present artifact type fails with exit `2`.
6. Never fall back to another loader after a selected loader fails.
7. Never select an adapter by guessing field names.

OpenDataLoader remains explicit with `--grounding opendataloader-json`. Crop options remain
unsupported for foreign grounding.

For `evidence anchor`, remove only the implementation default that prevents shared dispatch.
Explicit `ethos-json` and `opendataloader-json` remain valid, and no-flag native behavior remains
compatible.

## 8. Developer and pipeline surfaces

### 8.1 CLI path

The complete non-Rust path is:

```text
npx ethos grounding check parser-grounding.json \
  --source-artifact source.pdf \
  --out grounding-validation.json

npx ethos verify parser-grounding.json \
  --citations citations.json \
  --out verification-report.json \
  --fail-on-ungrounded
```

The standalone release binary provides the same commands. Grounding validation and verification
must not require PDFium.

The quickstart must show that the retrieval or agent layer submits literal claims against the
same accepted IDs, fingerprinted by the accepted representation rather than the source PDF.

`grounding check` reports the value to use:

```json
{
  "artifact_type": "ethos.grounding_validation.v1",
  "structure": "valid",
  "source_binding": "matched",
  "representation_sha256": "sha256:<representation hash>"
}
```

Citations carry that value as `document_fingerprint`:

```json
{
  "document_fingerprint": "sha256:<representation hash>",
  "claims": [
    {
      "kind": "quote",
      "text": "Revenue increased to $12.4 million.",
      "citation": {
        "page": "page-1",
        "element_id": "block-17"
      }
    }
  ]
}
```

Using `source.sha256` here would report `stale` against a correct artifact. The two hashes answer
different questions and the quickstart must say so: `source.sha256` records which PDF the mapper
claims it read, `representation_sha256` records which representation Ethos actually verified. See
§6.4 and `docs/writing-a-mapper.md` §7.

Ethos does not generate claims, select evidence, or decide relevance. It checks the submitted
literal claim and locator against the recorded representation.

### 8.2 Minimal npm runtime

Keep `@docushell/ethos-pdf`. Add one CommonJS runtime entry and generated declarations:

```typescript
checkGrounding(options): Promise<EthosCommandResult<GroundingValidationReport>>
verifyClaims(options): Promise<EthosCommandResult<VerificationReport>>
```

Shared result:

```typescript
{
  exitCode: number;
  artifact: T | null;
  reason: string | null;
}
```

Minimum options:

| Function | Required | Optional |
| --- | --- | --- |
| `checkGrounding` | `inputPath`, `outputPath` | `sourceArtifactPath`, `timeoutMs`, `signal` |
| `verifyClaims` | `inputPath`, `citationsPath` | `configPath`, `outputPath`, `failOnUngrounded`, `grounding: "opendataloader-json"`, `timeoutMs`, `signal` |

Rules:

- Invoke the packaged native binary with `spawn`, never a shell.
- Accept explicit paths, not an arbitrary argument string.
- Preserve CLI exit and report semantics.
- Return exit `1` with its report when `failOnUngrounded` is set.
- Reject process launch failure, timeout, cancellation, missing bounded output, or invalid output
  with one small typed SDK error.
- Bound stdout and stderr.
- Do not implement parsing, validation, verification, hashing, or report construction in
  production JavaScript.
- Existing CLI-only consumers continue to work.

Do not add receipt/proof functions, a generic process wrapper, or a second npm package.

### 8.3 Mapper examples

Add one dependency-light JavaScript example and one Python example. Both consume the same small
synthetic parser result and emit equivalent typed Grounding JSON.

Each example owns only:

1. stable ID and reading-order projection;
2. explicit coordinate conversion; and
3. honest capability declarations.

Each runs twice and compares exact output bytes before the Ethos validation and verification
steps. The Python example invokes the standalone CLI by path; it does not expand the Python public
API.

## 9. DocuShell and monetization boundary

### 9.1 Open Ethos versus commercial DocuShell

| Open Ethos v0.6.0 | Commercial DocuShell |
| --- | --- |
| Grounding JSON contract and conformance fixtures | Authenticated managed verification API |
| Offline CLI and existing Rust/Python/npm distributions | Usage controls, tenant isolation, queues, retries, observability, and support |
| Existing deterministic verification report | Approved adapters and compatibility operation |
| Thin native-backed npm functions | Evidence viewer and bounded review workflow when customer evidence supports it |
| Honest limitations and source-binding states | `docushell.verification_bundle.v0`, retention, authorization, and export under DocuShell contracts |

Do not make the open artifact intentionally painful to create or verify. Artificial friction would
reduce the adoption that DocuShell needs. Commercial value must come from reliable operation and a
measured workflow outcome.

Because Ethos is Apache-2.0, do not assume exclusive usage-based revenue from the binary or
protocol. A third party may self-host it or operate a competing service subject to the license.
Changing the license is outside v0.6.0 and would conflict with accepted ADR-0004.

### 9.2 What v0.6.0 can enable

DocuShell can:

- accept an authoritative PDF or approved resolver plus typed claims and native locators;
- project an approved parser representation into Grounding JSON;
- validate before indexing or claim generation;
- run the existing verifier in a bounded worker;
- preserve the unmodified `verification_report.json`;
- wrap it in accurately named DocuShell application records;
- offer managed integration, operation, support, evidence inspection, and bounded review; and
- measure whether customers prefer that managed path over self-hosting.

DocuShell's existing production-shaped OpenDataLoader lane may keep using the released explicit
adapter. v0.6.0 does not justify rewriting a working consumer merely to exercise the new format.
The Grounding JSON acceptance may run as a bounded fixture or shadow path until a new parser or
real consumer benefits from it.

DocuShell must not call its current wrapper a canonical Ethos receipt. Until a separate receipt
release passes, use the already planned `docushell.verification_bundle.v0` name and state that
portable receipt integrity and exact replay are unavailable.

### 9.3 Commercial validation is not a release gate

The first offer should be a fixed-scope paid integration evaluation: one PDF profile, one
integration, defined limits, support boundary, weekly-use expectation, success criteria, and
commercial decision date. If users repeat and prefer managed operation, test an annual minimum
plus measured usage. Do not freeze per-page or per-claim pricing before real cost and willingness
to pay are measured.

Track:

- clean-room integration time and undocumented steps;
- weekly active integrations and verified claim volume;
- self-hosted versus managed preference and the stated reason;
- support and custom-code hours per integration;
- compute, storage, and operational cost;
- failure, invalid-input, and unsupported rates;
- whether external recipients use the exported report or DocuShell bundle; and
- paid evaluation, conversion decision, and repeat use.

The DocuShell programme may use its existing evidence targets—three production-like integrations,
weekly repeat use, at least one paid evaluation, and measured managed-service preference—as a
business decision gate. These outcomes decide whether to productize DocuShell Cloud; they do not
block a technically sound Ethos v0.6.0 release.

### 9.4 DocuShell acceptance for v0.6.0

Before Ethos closeout, one reviewed DocuShell commit must prove:

- only public Ethos surfaces are used;
- the bounded Grounding JSON acceptance mapper or shadow fixture is byte-identical across two
  runs, without forcing migration of the working OpenDataLoader production lane;
- source hash, producer, capabilities, IDs, order, and geometry are preserved honestly;
- invalid grounding fails before indexing or verification;
- the existing report is stored without semantic relabelling;
- `grounded` is not presented as source truth, relevance, completeness, freshness, or business
  correctness;
- DocuShell tenant, case, workflow, billing, review, and retention fields do not enter the Ethos
  schema; and
- removing DocuShell still leaves the Grounding JSON artifact and Ethos report independently
  usable.

This is a consumer acceptance test, not authorization to change DocuShell in the Ethos release.

## 10. Implementation sequence

### WP-0 — Governance and baseline

Deliver:

- accepted scope and Grounding JSON ADR;
- corrected v0.5.0 current-release ledger;
- frozen resource limits and stable error vocabulary; and
- separate public-wording request if any.

Done when no authority conflict remains and production positioning stays blocked.

### WP-1 — Schema and strict parser

Start in:

- `schemas/`;
- `crates/ethos-core` behind its existing full feature; and
- focused schema/conformance fixtures.

Deliver:

- Grounding JSON and validation-report schemas;
- recursive duplicate-key rejection;
- typed shape and invariant validator;
- measured limits; and
- positive, negative, Unicode, integer, unknown-field, and limit fixtures.

Done when the schema and Rust validator reject and accept the same fixture set, errors are stable,
and no new runtime dependency is required unless separately justified and accepted.

### WP-2 — Adapter, shared loader, and CLI

Start in:

- `crates/ethos-cli/src/cmd/verify.rs`;
- `crates/ethos-cli/src/cmd/evidence.rs`; and
- one narrowly scoped internal Grounding JSON module.

Deliver:

- built-in `GroundingSource` implementation;
- one shared source loader;
- exact artifact-type detection;
- `ethos grounding check`; and
- atomic deterministic validation output.

Do not publish a new Rust crate.

Done when existing native and OpenDataLoader goldens are unchanged and a valid Grounding JSON
fixture reaches the existing verifier without PDFium.

### WP-3 — npm and examples

Start in `packages/npm/ethos-pdf`.

Deliver:

- generated types;
- `checkGrounding`;
- `verifyClaims`;
- clean temporary-project tests; and
- JavaScript and Python mapper examples plus quickstart.

Done when existing package consumers still compile and a clean Node project plus clean Python
environment complete the documented path without Rust or PDFium.

### WP-4 — Consumer and release evidence

Deliver:

- DocuShell acceptance against an exact reviewed commit;
- double-run artifact evidence;
- compatibility, claims, schema, package, dependency, and release gates;
- bounded resource/performance evidence; and
- closeout records tied to final published bytes.

Do not rebuild after publication candidates are accepted.

## 11. Required test matrix

### 11.1 Compatibility

- Existing `verify` and `verify-batch` report bytes and exits unchanged.
- Existing evidence-anchor behavior unchanged.
- Native input still selects the native loader.
- Explicit OpenDataLoader input still selects its existing loader.
- Existing Rust, Python, npm, and Action consumers remain valid.
- No input is reclassified by field-name heuristics.

### 11.2 Grounding JSON conformance

- Minimal valid artifact.
- Valid spans and tables.
- Duplicate root and nested keys.
- Unknown field at every object boundary.
- Missing, wrong, and unsupported artifact/schema identity.
- Duplicate and malformed IDs.
- Missing or cross-namespace references.
- Out-of-order or duplicate page indexes.
- Float, unsafe integer, invalid rotation, invalid dimensions, reversed box, zero-area box, and
  out-of-page box.
- Invalid capability combinations.
- Invalid Unicode scalar offsets, including emoji and combining-mark vectors.
- Overlapping or out-of-order table cells.
- Resource limit and one-over-limit cases.
- No repair of IDs, coordinates, order, capabilities, or source hashes.

### 11.3 Source binding and claims

- Source hash absent from supplied PDF comparison, matching, malformed, and mismatching.
- `not_checked` never rendered as `matched`.
- Hash match never rendered as extraction-fidelity proof.
- Grounding JSON fingerprint participates in existing stale checks without changing report
  semantics.
- Grounded, ungrounded, stale, unsupported, and capability-limited reports match the existing
  verifier contract.

### 11.4 Determinism

- Validation report bytes equal across two runs.
- JavaScript mapper bytes equal across two runs.
- Python mapper bytes equal across two runs.
- DocuShell mapper bytes equal across two runs.
- Same accepted Grounding JSON and citations produce the same report through single and batch
  verification where the existing contract requires equality.

### 11.5 SDK and clean-room

- `spawn` receives an argument array and never a shell string.
- Timeout and cancellation terminate safely.
- Output and diagnostics are bounded.
- Exit `0`, exit `1` with report, and exit `2` invalid-input cases retain typed meaning.
- Unsupported platform and missing binary fail before pretending verification ran.
- Clean temporary Node project completes install, check, and verify.
- Clean Python environment completes emit, check, and verify through the standalone binary.
- A developer who did not implement the feature completes the quickstart without undocumented
  intervention.

## 12. Release gates

Before publication:

- Governance and release-truth preconditions pass.
- Schema, invariants, limits, and error vocabulary are frozen.
- Existing compatibility suite is green.
- Grounding JSON conformance and double-run tests are green.
- Clean-room JavaScript and Python paths pass.
- DocuShell consumer acceptance passes against exact reviewed inputs.
- `cargo deny`, claims, schema, generated-artifact, npm package, and release-state gates pass.
- No AGPL, network-capable base dependency, new parser, or PDFium requirement enters the new path.
- Resource and performance evidence shows no unacceptable regression against the frozen v0.5.0
  verification baseline; the decider must set the numeric ceiling before implementation freeze.
- Publication uses accepted artifacts without rebuilding.
- Exact public wording, if any, is separately approved.

Failure of a deferred Windows, receipt, proof, signing, hosted, or commercial lane must not delay
or weaken this release.

## 13. Tradeoffs and deliberate decisions

### Grounding JSON is an adapter ABI, not a universal document model

It contains only what the existing verifier needs. Parser-native metadata remains with the parser
or caller. This avoids turning Ethos into a second canonical representation for every document
system.

### A mapper remains necessary

The mapper is small but cannot be eliminated honestly. Only the integration knows which source
IDs are stable, what reading order means, and how coordinates and capabilities map.

### Geometry limits initial reach

Requiring real boxes excludes text-only parsers. That is preferable to false inspectability. Log
blocked integrations and reconsider the trait only when evidence justifies a versioned profile.

### A thin npm wrapper is enough

Node is the proven consumer runtime. The wrapper removes raw child-process management while the
native binary remains the only implementation. More SDKs wait for measured demand.

### The open protocol and commercial service should not be coupled

Ethos adoption should survive without DocuShell. DocuShell wins when customers pay to avoid
operating, integrating, supporting, and governing the path themselves—not because independent
verification is withheld.

### Portable receipts remain a separate bet

Receipts may become strategically valuable, but they require a distinct threat model and
compatibility contract. Customer learning can proceed with the existing report and accurately
named DocuShell bundle. Do not make the larger protocol a prerequisite for learning whether
anyone pays.

## 14. Open blockers and decider choices

These are explicit blockers:

- This scope is not yet accepted.
- The v0.5.0 release ledger and approved public baseline are inconsistent.
- The Grounding JSON ADR does not exist.
- Exact resource limits and the performance-regression ceiling are not frozen.
- Stable validation error codes are not frozen.
- The final DocuShell acceptance commit is not selected.
- No new public Grounding JSON or npm SDK wording is approved.

> Current state of these blockers is tracked in [`v0-6-0-release.md`](v0-6-0-release.md) §8. The
> ADR now exists and freezes the limits and error vocabulary; the remaining items are open.

The decider must choose:

1. Accept v0.6.0 as the adoption release described here.
2. Keep receipt/proof/replay deferred to a separately scoped release.
3. Keep Windows publication off the v0.6.0 critical path.
4. Preserve Apache-2.0 and test commercial capture through DocuShell managed operation.

Until those choices are accepted, this is a detailed proposal, not permission to ship.
