# Ethos Python Package

This directory contains the `ethos-pdf` Python package source for Ethos.

Install the published evaluation wheel from PyPI with:

```sh
python3 -m pip install ethos-pdf==0.3.0
```

`v0.3.0` includes JSON verification and evidence-anchor wrapper calls through a caller-provided
`ethos` CLI binary. The Python wheel does not bundle the CLI or PDFium.

The package exposes a public semver API beginning at `0.1.0` for Python `>=3.8`. Patch releases
must not break public function signatures, exception classes, or documented return shapes. Minor
releases may add backward-compatible API, and major releases may break API after a release-scope
decision.

Public API:

- `EthosCli`
- `EthosPythonSurfaceError`
- `EthosNotFoundError`
- `EthosTimeoutError`
- `EthosCommandError`
- `PdfiumNotFoundError`
- `InvalidPdfError`
- `CorruptPdfError`
- `ParseTimeoutError`
- `EthosOutputError`
- `CitationEmissionError`
- `parse_pdf_json`
- `parse_pdf_markdown`
- `parse_pdf_text`
- `crop_element`
- `verify`
- `proof_summary`
- `app_answer_release_decision`
- `anchor`
- `build_citation_emission`
- `build_langchain_context`
- `build_llamaindex_context`
- `citation_json_bytes`
- `emit_langchain_citations`
- `emit_llamaindex_citations`
- `hydrate_citations`

The CLI wrapper remains intentionally thin: it shells out to a caller-provided local `ethos` CLI
binary and returns `ethos doc parse` output, source-bound `ethos crop_element` JSON, `ethos verify`
JSON reports, or `ethos evidence anchor` JSON reports. The citation-emission helpers below are pure
Python and do not invoke that binary. The wheel does not bundle PDFium, does not publish hosted
surfaces, and does not expand parser behavior. The Rust CLI remains the verification source of
truth.

The package name is historical continuity naming. JSON verification and evidence-anchor calls do
not require PDF parsing, but the package is still named `ethos-pdf`.

PDFium-backed parse and crop paths require caller-provided PDFium through
`ETHOS_PDFIUM_LIBRARY_PATH`. Importing `ethos_pdf` does not require PDFium. If PDFium is missing,
the wrapper raises `PdfiumNotFoundError` and preserves the underlying CLI stderr so callers can show
the setup guidance from `QUICKSTART.md` or `docs/pdfium-manual-setup.md`.

Python wheels do not run post-install hooks. Run `python -m ethos_pdf` after installation to print
the paved `scripts/fetch-pdfium.sh` setup path; the command prints guidance only and never downloads
or changes PDFium.

## Exceptions

All wrapper-owned exceptions inherit from `EthosPythonSurfaceError`.

Subprocess failures inherit from `EthosCommandError` and expose `command`, `returncode`, `stdout`,
and `stderr`. When the CLI emits its stable JSON error envelope on stderr, the wrapper maps by
`error.code`; otherwise it falls back to the documented exit code:

| CLI condition | Exit | Python exception |
| --- | ---: | --- |
| missing caller-provided PDFium | any non-zero exit with PDFium setup stderr | `PdfiumNotFoundError` |
| `invalid_pdf` | 3 | `InvalidPdfError` |
| `corrupt_pdf` | 4 | `CorruptPdfError` |
| `parse_timeout` | 10 | `ParseTimeoutError` |
| any other non-zero CLI exit | other | `EthosCommandError` |

Wrapper-side timeouts raised by `subprocess.run(..., timeout=...)` use `EthosTimeoutError`.
Missing input files raise Python `FileNotFoundError` before invoking the CLI.

## JSON Verify And Evidence Anchor

Use the `binary` constructor alias when a caller manages the CLI path explicitly:

```python
from ethos_pdf import EthosCli

ethos = EthosCli(binary="/path/to/ethos")

report = ethos.verify(
    source="source.ethos.json",
    citations="citations.json",
    grounding=None,
    config=None,
    fail_on_ungrounded=False,
    output_format="json",
    timeout=30,
)

anchor_report = ethos.anchor(
    source="source.ethos.json",
    evidence_refs="evidence_refs.json",
    grounding=None,
    output_format="json",
    timeout=30,
)
```

`verify(...)` maps `source` to the positional CLI input, maps `citations` to `--citations`, maps
`grounding` to an adapter id such as `opendataloader-json`, maps `config` to `--config`, and maps
`fail_on_ungrounded=True` to `--fail-on-ungrounded`.

`anchor(...)` maps `source` to the positional CLI input, maps `evidence_refs` to `--evidence-refs`,
and maps `grounding` to an adapter id. It does not expose a fail flag in the v0.2 preparation
surface. Non-bound evidence-anchor outcomes are returned as structured reports, not exceptions.

Verify exit semantics:

- exit `0` with JSON returns a report;
- exit `1` with JSON returns a negative verification report when `fail_on_ungrounded=True`;
- exit `>=2` raises `EthosCommandError` or a more specific subclass.

Use `proof_summary(report)` when a product or API wrapper needs the same derived status as the Rust
`VerificationReport::proof_summary()` helper:

```python
from ethos_pdf import EthosCli, proof_summary

ethos = EthosCli(binary="/path/to/ethos")
report = ethos.verify("source.ethos.json", citations="citations.json")
summary = proof_summary(report)
print(summary["proof_status"])
```

The summary is not a replacement for the canonical verification report. It deterministically
derives `proof_status`, `request_certified`, reusable grounded check ids, needs-review check ids,
and proof limitations from the report that `ethos verify` already emitted.

Use `app_answer_release_decision(...)` when an application has already labeled claim relevance,
synthesis, and support, and wants the conservative release policy from
`docs/app-answer-release-contract.md`:

```python
from ethos_pdf import app_answer_release_decision, proof_summary

summary = proof_summary(report)
decision = app_answer_release_decision(
    "What was Q3 2025 revenue?",
    summary,
    [
        {
            "id": "claim-revenue",
            "text": "Revenue grew to $12.4M in Q3 2025.",
            "check_ids": ["v0001"],
            "question_relevance": "direct_answer",
            "claim_type": "source_fact",
            "claim_support": "supported",
        }
    ],
)
print(decision["app_status"])
```

The helper does not judge relevance, synthesis, or claim support. Callers supply those labels; the
helper applies the release rule and requires referenced Ethos check IDs to be reusable before a
claim can enter the final answer. For a grounded claim, missing `claim_support` becomes
`not_evaluated` and requires review. The helper also rejects duplicate claim IDs so
`final_answer_claim_ids`, `review_claim_ids`, and `blocked_claim_ids` stay unambiguous.

## Citation emission

The source API builds the independently versioned citation-emission v1
artifact and hydrates it into verifier input. Registry publication remains a human release action.
No CLI, PDFium, LangChain, or LlamaIndex package is imported by these helpers.

Retrieval objects must carry an explicit Ethos metadata contract. Each object's `metadata` mapping
must contain one `document_fingerprint` and at least one source locator in `page_refs`,
`element_refs`, `span_refs`, or `table_cells`. Reference fields are arrays of non-blank IDs.
`table_cells` entries have exactly `table_id`, `row`, and `col`. All records in one call must use
the same fingerprint. Numeric framework page indexes and other aliases are deliberately ignored;
copy stable source IDs into these fields rather than asking the helper to guess.

For an existing LangChain retrieval result:

```python
from ethos_pdf import citation_json_bytes, emit_langchain_citations

documents = retriever.invoke(question)
# Each Document.metadata follows the explicit contract above.
claims = structured_model_output["claims"]
citations = emit_langchain_citations(
    documents,
    structured_model_output["answer"],
    claims,
)
citations_bytes = citation_json_bytes(citations)
```

Use `emit_llamaindex_citations(nodes, answer, claims)` for `TextNode` or `NodeWithScore` results.
Both adapters are duck typed and accept mapping equivalents, so applications do not add an Ethos
framework dependency. `build_langchain_context` and `build_llamaindex_context` expose the trusted
retrieval vocabulary separately; `build_citation_emission` builds model-facing v1 output; and
`hydrate_citations` joins the two when an application needs separate callback and hydration steps.

Every malformed claim, missing or mixed fingerprint, unshown source ID, unexposed table cell, and
configured claim-limit violation raises `CitationEmissionError`. Its stable `code` plus optional
`claim_index` or `record_index` can be returned to a structured-output retry. The whole batch is
rejected; helpers never repair, drop, or infer a locator. This validates citation structure and
retrieval provenance only—verification still requires `ethos verify`, and grounding is not a
semantic-truth judgment.

Runnable, provider-free walkthroughs are in `examples/langchain-rag/README.md` and
`examples/llamaindex-rag/README.md`. Both preserve the verifier's intentional exit-`1` report for
a fabricated citation and require no model API key.

Run the focused tests with:

```sh
make python-surface-test
```

The tests use a fake local command, so they do not require PDFium.
