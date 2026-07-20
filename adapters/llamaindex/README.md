# LlamaIndex citation emission

Ethos provides a dependency-free, duck-typed helper in the existing Python wheel. It accepts
LlamaIndex `TextNode` and `NodeWithScore` objects without importing LlamaIndex:

```python
from ethos_pdf import emit_llamaindex_citations

nodes = retriever.retrieve(question)
citations = emit_llamaindex_citations(nodes, model_output["answer"], model_output["claims"])
```

Before retrieval, preserve the source contract in every node's `metadata` mapping:
`document_fingerprint` plus one or more arrays named `page_refs`, `element_refs`, or `span_refs`.
Exact table coordinates may be supplied as `table_cells` objects with `table_id`, `row`, and
`col`. The helper unwraps `NodeWithScore.node`, rejects missing/mixed fingerprints, and rejects
model IDs or cells absent from the retrieved nodes. It never guesses from framework metadata.

See `python/README.md#citation-emission` for the complete API and failure boundary, and
`examples/llamaindex-rag/README.md` for the pinned offline end-to-end walkthrough. This directory
intentionally adds no framework runtime dependency.
