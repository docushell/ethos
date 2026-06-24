# Ethos Python Package

This directory contains the `ethos-pdf` Python package source for Ethos.

Install the published evaluation wheel from PyPI with:

```sh
python3 -m pip install ethos-pdf==0.1.1
```

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
the wrapper raises `PdfiumNotFoundError` and preserves the underlying CLI stderr so callers can show
the setup guidance from `QUICKSTART.md` or `docs/pdfium-manual-setup.md`.

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

Run the focused tests with:

```sh
make python-surface-test
```

The tests use a fake local command, so they do not require PDFium.
