# Ethos Python Surface Scaffold

This directory contains the internal pre-alpha Python surface scaffold for Ethos.

The current module is intentionally thin: it shells out to a caller-provided local
`ethos` CLI binary and returns the `ethos doc parse` output. It does not bundle a
binary, publish an install path, or expand parser behavior. The scaffold exists so
Milestone B can begin locking a Python-facing API shape while the Rust CLI remains
the source of truth.

Run the focused tests with:

```sh
make python-surface-test
```

The tests use a fake local command, so they do not require PDFium.
