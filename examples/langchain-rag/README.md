# LangChain RAG → Ethos

This offline example converts recorded Ethos chunks into native LangChain `Document` retrieval
results, hydrates recorded structured model output with `emit_langchain_citations`, and runs
`ethos verify --fail-on-ungrounded`. It calls no model or hosted service and needs no API key.

From the repository root, with Python 3.10 or newer:

```sh
python3 -m pip install -r examples/citation-emission/requirements-frameworks.txt
cargo build --locked -p ethos-cli
python3 examples/langchain-rag/run.py --case fabricated
```

The final command intentionally exits `1` and writes `verification-report.json` under
`target/rag-framework-examples/langchain/fabricated/`: verification completed and the fabricated
`$99M` quote is not grounded. Do not regenerate until green; preserve and handle the negative
report. Use `--case grounded` for the exit-`0` fixture.

Replace `retrieval_records()` and the recorded model-output JSON with your retriever results and
structured model response. Preserve `document_fingerprint`, `page_refs`, `element_refs`, optional
`span_refs`, and explicitly exposed `table_cells` in each `Document.metadata` mapping.

Ethos verifies citation grounding, not semantic truth. Applications still own relevance,
completeness, synthesis, and answer-release policy.
