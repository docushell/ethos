# Ethos Python Surface Scaffold

This directory contains the internal pre-alpha Python surface scaffold for Ethos.

The current module is intentionally thin: it shells out to a caller-provided local
`ethos` CLI binary and returns `ethos doc parse` output or source-bound
`ethos crop_element` JSON. It can pass caller-provided source PDF and crop artifact
directory arguments for rendered crop artifacts. It does not bundle a binary, publish
an install path, add Node/MCP/hosted crop surfaces, or expand parser behavior. The
scaffold exists so the Python-facing API shape can stay locked while the Rust CLI
remains the source of truth.

Run the focused tests with:

```sh
make python-surface-test
```

The tests use a fake local command, so they do not require PDFium.
