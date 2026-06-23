# @docushell/ethos-pdf

`@docushell/ethos-pdf` is the npm binary package scaffold for the Ethos CLI.

Supported first-release targets:

- macOS arm64
- Linux x64

The package is prepared as a binary distribution package. It is not a hosted service, does not
include public benchmark reports or claims, and does not bundle PDFium. PDFium-backed commands use
caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.

Installing this package must not require PDFium. PDFium-backed commands fail until
`ETHOS_PDFIUM_LIBRARY_PATH` points to a caller-provided PDFium dynamic library. See
`QUICKSTART.md` in this package and `docs/pdfium-manual-setup.md` in the Ethos source repository
for the setup contract.

Runtime behavior:

- unsupported OS/CPU targets exit before invoking a binary;
- missing packaged binaries exit with a clear "binary is missing" message;
- PDFium-backed commands preserve the Rust CLI exit code and stderr.

The package is not approved for public publication until the final release approval record binds the
source commit, package version, artifact checksums, and exact public wording.
