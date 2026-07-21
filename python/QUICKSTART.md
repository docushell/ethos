# Quickstart

The `ethos-pdf` Python package is a thin wrapper around a caller-provided local `ethos` CLI binary.
It does not bundle Ethos or PDFium.

Install the published evaluation wheel from PyPI with:

```sh
python3 -m pip install ethos-pdf==0.4.0
```

## PDFium Setup

PDF-backed parse and crop commands require a caller-provided PDFium dynamic library.

From an Ethos source checkout, run `scripts/fetch-pdfium.sh`, apply the export it prints, and run
`ethos doctor --require-pdfium`. The fetch script verifies the pinned archive and runtime sha256
values and never runs automatically.

Python wheels cannot run post-install hooks. Run this after wheel installation to print the same
setup path:

```sh
python -m ethos_pdf
```

Point the Python wrapper at a local `ethos` binary or ensure `ethos` is on `PATH`.

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

For Evidence Handle Bridge v2, treat only structured `claims[].evidence_id` values as citations.
Never turn handle-shaped model answer prose into links or verified badges; render those only from
trusted context plus `project_evidence_states` output.
