# PDFium Manual Setup

Ethos first public release preparation keeps PDFium caller-provided. The CLI, Python package, and
npm package do not bundle PDFium and do not download PDFium.

Set `ETHOS_PDFIUM_LIBRARY_PATH` to the platform PDFium dynamic library before running
PDFium-backed parse or crop commands.

Examples:

```sh
export ETHOS_PDFIUM_LIBRARY_PATH=/path/to/libpdfium.dylib
ethos doctor --require-pdfium
ethos doc parse input.pdf --format json
```

```sh
export ETHOS_PDFIUM_LIBRARY_PATH=/path/to/libpdfium.so
ethos doctor --require-pdfium
python -c 'from ethos_pdf import parse_pdf_json; print(parse_pdf_json("input.pdf"))'
```

```sh
export ETHOS_PDFIUM_LIBRARY_PATH=/path/to/libpdfium.so
ethos doctor --require-pdfium
ethos doc parse input.pdf --format text
```

If the variable is not set, PDFium-backed paths must fail with a clear setup error naming
`ETHOS_PDFIUM_LIBRARY_PATH`. Python import and npm package installation must not require PDFium.
`ethos doctor` reports PDFium setup warnings without changing files, downloading dependencies, or
vetting untrusted dynamic libraries.

This document does not approve bundled project-maintained PDFium builds, hosted surfaces,
production positioning, or public benchmark reports or claims.
