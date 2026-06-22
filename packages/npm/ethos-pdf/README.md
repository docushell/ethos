# @docushell/ethos-pdf

`@docushell/ethos-pdf` is the npm binary package scaffold for the Ethos CLI.

Supported first-release targets:

- macOS arm64
- Linux x64

The package is prepared as a binary distribution package. It is not a hosted service, does not
include public benchmark reports or claims, and does not bundle PDFium. PDFium-backed commands use
caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.

The package is not approved for public publication until the final release approval record binds the
source commit, package version, artifact checksums, and exact public wording.
