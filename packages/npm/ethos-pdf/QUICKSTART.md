# Quickstart

`@docushell/ethos-pdf` installs an `ethos` CLI binary for supported first-release targets:

- macOS arm64
- Linux x64

The package does not bundle PDFium. Commands that parse or crop PDFs require a caller-provided
PDFium dynamic library.

## Vendor Binary Assembly

Before publication, assemble the package vendor payload from the approved GitHub Release archives:

```sh
npm run prepare:vendor -- /absolute/path/to/release-assets
```

The directory must contain `ethos-macos-arm64.tar.gz` and `ethos-linux-x64.tar.gz`. The assembly
script verifies the checksums in `vendor/manifest.json` before writing the packaged binaries.

## PDFium Setup

1. Install or build PDFium for your platform.
2. Set `ETHOS_PDFIUM_LIBRARY_PATH` to the dynamic library path before running PDF-backed commands.

Example:

```sh
export ETHOS_PDFIUM_LIBRARY_PATH=/absolute/path/to/libpdfium.dylib
ethos doc parse document.pdf --format json
```

On Linux the library is typically named `libpdfium.so`; on macOS it is typically
`libpdfium.dylib`.

If PDFium is missing, PDF-backed commands fail with a message that names
`ETHOS_PDFIUM_LIBRARY_PATH`. Installation only warns because non-PDF commands and setup workflows
must remain usable before PDFium is configured. The warning is an initial-setup hint only; CI,
Docker images, and deployment environments may set `ETHOS_PDFIUM_LIBRARY_PATH` later at runtime.
