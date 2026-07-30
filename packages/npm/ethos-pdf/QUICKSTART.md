# Quickstart

`@docushell/ethos-pdf` installs an `ethos` CLI binary for supported first-release targets:

- macOS arm64
- Linux x64

The package does not bundle PDFium. Commands that parse or crop PDFs require a caller-provided
PDFium dynamic library.

Install the current published npm package with:

```sh
npm install -g @docushell/ethos-pdf@0.4.0
```

The current published npm package is `@docushell/ethos-pdf@0.4.0`. Its vendored CLI binaries report
`ethos 0.4.0`.

## Vendor Binary Assembly

To prepare a future package release, assemble its vendor payload from the approved GitHub Release
archives:

```sh
npm run prepare:vendor -- /absolute/path/to/release-assets
```

The directory must contain `ethos-macos-arm64.tar.gz` and `ethos-linux-x64.tar.gz`. The assembly
script verifies the release-archive and extracted-executable checksums in `vendor/manifest.json`
before writing the packaged binaries.

## PDFium Setup

From an Ethos source checkout, run `scripts/fetch-pdfium.sh`, apply the export it prints, and run
`ethos doctor --require-pdfium`. The fetch script verifies the pinned archive and runtime sha256
values and never runs automatically. The package repeats this guidance as a non-blocking
postinstall warning when `ETHOS_PDFIUM_LIBRARY_PATH` is unset.

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

## Grounding JSON quickstart

The package includes a pinned parser result and Grounding JSON example. The SDK checks and verifies
those installed files without Rust or PDFium:

```js
const path = require("node:path");
const { checkGrounding, verifyClaims } = require("@docushell/ethos-pdf");

const root = path.join(__dirname, "node_modules/@docushell/ethos-pdf/examples/fixtures");
const inputPath = path.join(root, "grounding.json");

const validation = await checkGrounding({ inputPath });
console.log(validation.exitCode, validation.artifact.structure);

const verification = await verifyClaims({
  inputPath,
  citationsPath: path.join(root, "citations.json"),
});
console.log(verification.exitCode, verification.artifact.all_evidence_grounded);
```

The JavaScript and Python mapper examples consume the pinned parser output and page metadata,
convert bottom-left point coordinates to top-left centipoints, and emit identical Grounding JSON.

To practice correcting one documented validation failure, copy `examples/fixtures/grounding-invalid.json`
to a working file and run `checkGrounding`. The report identifies `/elements/0/bbox` as an
out-of-page bounding box. Change its right coordinate from `60000` to `39415`, rerun the check,
and confirm that `structure` becomes `valid`. Ethos does not repair submitted artifacts.
