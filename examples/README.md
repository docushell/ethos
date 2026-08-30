# examples

Pinned fixture set: RAG demo (parse -> chunks -> citations -> verification),
agent demo (verify + crop), foreign-parser demo (verify over OpenDataLoader JSON), and
app-answer-release demo (proof summary -> app release decision). Pinned fixtures only.

Offline framework citation-emission walkthroughs:

- [LangChain RAG → Ethos](langchain-rag/README.md)
- [LlamaIndex RAG → Ethos](llamaindex-rag/README.md)

Both use recorded retrieval/model fixtures and preserve the verifier's exit-`1` report for a
fabricated citation. Ethos verifies citation grounding, not semantic truth.
