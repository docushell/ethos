# Citation Emission Spec v1

Status: frozen application-layer contract. Schema version: `1.0.0`. Schema identity:
`urn:ethos:schema:llm-citation-output:1`.

This contract defines the structured JSON a model or framework callback produces before an
application deterministically hydrates it into `ethos-citations.schema.json`. It is versioned
independently from the verification-report schema. The verifier does not consume this artifact
directly, and this contract adds no verifier status or claim kind.

Ethos verifies citation grounding, not semantic truth. A grounded claim means the claimed text
matched the cited source under the selected verification configuration. It does not mean the
claim is relevant, complete, logically sound, or true outside that source.

## Normative pipeline

1. Parse a document with Ethos or a supported foreign parser.
2. Build retrieval records that preserve source IDs and the document fingerprint.
3. Show the model only records selected for the current answer, including their source IDs.
4. Require output that validates against
   `schemas/ethos-llm-citation-output.schema.json`.
5. Hydrate that output in deterministic application code: validate every ID against the records
   actually shown, inject the document fingerprint, and map locators into `claims[].citation`.
6. Run `ethos verify ... --fail-on-ungrounded --out report.json`.
7. Apply application-owned relevance and release policy to the report.

The model MUST NOT emit document fingerprints or bounding boxes. The hydrator MUST NOT repair,
guess, or silently drop a malformed claim.

## Retrieval context

Every source ID accepted from the callback MUST have appeared in the retrieval context supplied
for that answer. ID syntax belongs to the selected `GroundingSource`; native Ethos IDs normally
use `pNNNN`, `eNNNNNN`, `sNNNNNN`, and `tNNNN`, while foreign adapters may use different
namespaces. The v1 schema therefore requires bounded non-blank strings and leaves stricter ID
validation to hydration.

Ordinary Ethos chunk records expose element and page IDs. They do not expose table IDs or cell
coordinates. A callback MAY emit `table_cell` only when the application explicitly supplied the
corresponding `table_id` and `{row,col}` in its retrieval context. Otherwise it MUST use an
actually exposed element/span/page locator for an applicable claim or abstain. Models MUST NOT
infer table coordinates from rendered text.

All retrieval records used for one emission batch MUST carry the same document fingerprint.
Mixed fingerprints fail hydration. Multi-document emission is outside v1; applications must
split it into one batch per source document.

## Output shape

The top-level object contains:

- `schema_version`: exactly `1.0.0`;
- `answer`: non-blank answer text;
- `claims`: 1–256 atomic claims.

Supported claim shapes are:

| Kind | Required assertion | Permitted locator |
| --- | --- | --- |
| `quote` | non-blank `text` | exactly one of `element_id`, `span_id`, or page-only; `page` may accompany an element/span |
| `value` | non-blank `text` | same as `quote` |
| `presence` | no `text` | exactly one of `element_id`, `span_id`, or page-only |
| `table_cell` | non-blank `text` | `table_id` plus `cell {row,col}`; `page` is optional context |

No other fields are accepted. In particular, fingerprints, bounding boxes, chunk IDs,
verification results, confidence scores, and free-form metadata are forbidden.

### Pointer-first mode

Pointer-first emission is preferred. For presence claims the callback emits only a locator. For
quote and value claims it emits the asserted text plus the narrowest locator actually present in
the retrieval context.

Pointer emission does not make the model honest; it changes what is guaranteed. Ethos still
checks the claimed text against the resolved element. What pointers buy is (a) a small,
unambiguous match target instead of a page-level haystack, (b) fabricated or dangling IDs fail
loudly, (c) stale documents fail loudly, and (d) if the UI displays hydrated source text, the
displayed quote is source-true by construction even when the model's rendition was sloppy.

### Typed-quote fallback

If the application cannot preserve narrower IDs, `quote` and `value` may use a page-only locator.
The model still copies the exact asserted text. This has a wider match target and must not be
presented as stronger evidence. Programmatic bbox locators remain available in the hydrated
citations contract but are deliberately absent from model-facing v1.

## Deterministic hydration

Hydration maps fields without semantic rewriting:

| Emission field | Hydrated citation field |
| --- | --- |
| `kind` | `claims[].kind` |
| `text` | `claims[].text` |
| `page` | `claims[].citation.page` |
| `element_id` | `claims[].citation.element_id` |
| `span_id` | `claims[].citation.span_id` |
| `table_id` + `cell` | `claims[].citation.table_id` + `.cell` |
| retrieval-context fingerprint | envelope `document_fingerprint` |

Before emitting hydrated JSON, the application MUST validate the v1 schema, reject IDs and table
cells absent from the shown context, reject conflicting locator groups, enforce its configured
claim limit, and inject the fingerprint from trusted retrieval data. It MUST preserve claim order
and asserted text exactly. It MUST reject the entire batch if any claim fails.

`examples/citation-emission/` contains grounded, fabricated-quote, dangling-ID, and conflicting-
locator fixtures plus deterministic hydrated outputs. `make citation-emission-v1-contract`
validates the schemas, hydrates twice byte-identically, and verifies grounded/fabricated outputs
twice byte-identically.

The reference pure-Python implementation is `ethos_pdf.emit`. Its LangChain and LlamaIndex
helpers are duck typed and require each retrieval record's metadata to carry
`document_fingerprint` plus at least one of `page_refs`, `element_refs`, `span_refs`, or exact
`table_cells`. They do not import either framework, invoke the Ethos CLI, load PDFium, infer
aliases, or perform network operations. See `python/README.md#citation-emission`.

## Failure policy

| Signal | Meaning | Required application action |
| --- | --- | --- |
| Schema or hydration rejection | malformed output, unshown ID, mixed fingerprint, or unsupported locator | Re-prompt at most once with the specific rejection, then fail the answer |
| Exit `2` | malformed citations/configuration; pipeline bug | Alert and fix; do not retry as evidence |
| Exit `1` with report | verification completed and at least one check is not grounded | Preserve the report and apply release policy; MUST NOT regenerate until green |
| Exit `0` with report | all requested checks grounded | Apply relevance/synthesis release policy; grounding is not semantic truth |

A verifier whose negative verdicts are silently regenerated away provides no assurance.
Applications MUST NOT retry an exit-1 verification merely to obtain a green result.

## Model instruction block

Applications may adapt prose but must preserve these constraints:

```text
Answer only from the supplied source records. Each record includes source IDs that are the only
citation vocabulary you may use.

For every factual statement, emit one atomic claim in the required JSON output:
- quote/value: copy the exact asserted text and one source locator shown in the context;
- table_cell: use table_id and cell coordinates only when both were explicitly shown;
- presence: cite one shown element, span, or page.

Never invent IDs, fingerprints, coordinates, or unsupported facts. Do not reformat numbers. If
the supplied sources do not support a statement, omit the statement.
```

## Compatibility

Additive optional fields require a schema-version decision; removals, renamed fields, changed
claim semantics, relaxed fail-closed rules, or newly accepted locator combinations require a new
major schema identity. Verification-report evolution does not implicitly change this contract.
No network client, prompt library, parser dependency, or PDFium capability is required to emit
the v1 application artifact.
