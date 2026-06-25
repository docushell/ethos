# @docushell/ethos-pdf

`@docushell/ethos-pdf` is the npm binary package for the Ethos CLI.

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

Vendor assembly:

- place the approved `ethos-macos-arm64.tar.gz` and `ethos-linux-x64.tar.gz` release archives in
  one local directory;
- run `npm run prepare:vendor -- <release-artifact-dir>`;
- the script verifies the archive SHA256 values recorded in `vendor/manifest.json`;
- the script extracts the `ethos` executable from each archive and writes
  `vendor/ethos-darwin-arm64` and `vendor/ethos-linux-x64`.

The current npm package is `@docushell/ethos-pdf@0.2.1`, which vendors CLI binaries that report
`ethos 0.2.0`. Version `0.2.0` is deprecated because it shipped stale CLI binaries that reported
`ethos 0.1.2`.
