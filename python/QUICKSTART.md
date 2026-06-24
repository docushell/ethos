# Quickstart

The `ethos-pdf` Python package is a thin wrapper around a caller-provided local `ethos` CLI binary.
It does not bundle Ethos or PDFium.

Install the published evaluation wheel from PyPI with:

```sh
python3 -m pip install ethos-pdf==0.1.1
```

## PDFium Setup

PDF-backed parse and crop commands require a caller-provided PDFium dynamic library.

1. Install or build PDFium for your platform.
2. Set `ETHOS_PDFIUM_LIBRARY_PATH` to the dynamic library path.
3. Point the Python wrapper at a local `ethos` binary or ensure `ethos` is on `PATH`.

Example:

```sh
export ETHOS_PDFIUM_LIBRARY_PATH=/absolute/path/to/libpdfium.so
python - <<'PY'
from ethos_pdf import parse_pdf_json

document = parse_pdf_json("document.pdf", ethos_bin="ethos")
print(document["artifact_type"])
PY
```

On Linux the library is typically named `libpdfium.so`; on macOS it is typically
`libpdfium.dylib`.

Importing `ethos_pdf` does not require PDFium. If a PDF-backed CLI command reports missing PDFium,
the wrapper raises `PdfiumNotFoundError` and preserves the CLI stderr for display to the caller.
