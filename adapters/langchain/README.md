# LangChain citation emission

Ethos provides a dependency-free, duck-typed helper in the existing Python wheel. It accepts
LangChain `Document` objects without importing LangChain:

```python
from ethos_pdf import emit_langchain_citations

documents = retriever.invoke(question)
citations = emit_langchain_citations(documents, model_output["answer"], model_output["claims"])
```

Before retrieval, preserve the source contract in every `Document.metadata` mapping:
`document_fingerprint` plus one or more arrays named `page_refs`, `element_refs`, or `span_refs`.
Exact table coordinates may be supplied as `table_cells` objects with `table_id`, `row`, and
`col`. The helper rejects missing/mixed fingerprints, malformed metadata, and model IDs absent
from the retrieved records. It does not infer stable IDs from LangChain's numeric `page` metadata.

See `python/README.md#citation-emission` for the complete API and failure boundary. NIP-4.3 owns
the pinned runnable end-to-end example; this directory intentionally adds no framework runtime
dependency.
