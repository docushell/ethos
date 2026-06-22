# Ethos Python Package

This directory contains the `ethos-pdf` Python package source for Ethos.

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
- `EthosOutputError`
- `parse_pdf_json`
- `parse_pdf_markdown`
- `parse_pdf_text`
- `crop_element`

The current module is intentionally thin: it shells out to a caller-provided local `ethos` CLI
binary and returns `ethos doc parse` output or source-bound `ethos crop_element` JSON. It can pass
caller-provided source PDF and crop artifact directory arguments for rendered crop artifacts. It
does not bundle PDFium, does not publish hosted surfaces, and does not expand parser behavior. The
Rust CLI remains the source of truth.

PDFium-backed parse and crop paths require caller-provided PDFium through
`ETHOS_PDFIUM_LIBRARY_PATH`. Importing `ethos_pdf` does not require PDFium. If PDFium is missing,
the underlying CLI error is preserved in `EthosCommandError.stderr` so callers can show the setup
guidance from `docs/pdfium-manual-setup.md`.

Run the focused tests with:

```sh
make python-surface-test
```

The tests use a fake local command, so they do not require PDFium.
