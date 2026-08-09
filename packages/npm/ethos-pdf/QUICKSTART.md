# Quickstart

`@docushell/ethos-pdf` installs an `ethos` CLI binary for supported first-release targets:

- macOS arm64
- Linux x64

## Supported hosts

The packaged binaries and the pinned PDFium profile cover **macOS arm64 and Linux x64 only**.

On any other host — macOS x64 (Intel) included — the npm package fails closed with a typed
`unsupported_platform` error before running anything, and `ethos doctor --require-pdfium` reports
that no pinned PDFium profile exists for the platform. Neither is a sign of a broken install.

Everything in the Grounding JSON section below still works on those hosts: build the CLI from an
Ethos source checkout with `cargo build --locked -p ethos-cli` and use that binary. Grounding JSON
validation and verification never require PDFium.

The package does not bundle PDFium. Commands that parse or crop PDFs require a caller-provided
PDFium dynamic library.

Install the current published npm package with:

```sh
npm install -g @docushell/ethos-pdf@0.5.0
```

The current published npm package is `@docushell/ethos-pdf@0.5.0`. Its vendored CLI binaries report
`ethos 0.5.0`.

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

### Citations use the representation hash

There are two hashes and they answer different questions. `source.sha256` is the original PDF hash
that your mapper declares. `representation_sha256` is the hash of the accepted Grounding JSON, and
it is what the verifier records as `document_fingerprint`.

**Citations must carry `representation_sha256`.** Read it from the validation report:

```sh
ethos grounding check grounding.json --out validation.json
# -> "representation_sha256": "sha256:f0f1…"
```

Use that value as `document_fingerprint` in your citations file. Re-emitting the artifact changes
it — including a `producer.version` bump against an unchanged PDF — and older citations then report
`stale`.

### Running the mapper examples

Both examples take three positional arguments:

```sh
node   examples/map-grounding.js parser-output.json page-metadata.json grounding.json
python examples/map_grounding.py parser-output.json page-metadata.json grounding.json
```

With the packaged fixtures, from the `examples/` directory:

```sh
node map-grounding.js fixtures/parser-output.json fixtures/page-metadata.json out.json
```

They consume the pinned parser output and page metadata, convert bottom-left point coordinates to
top-left centipoints, and emit byte-identical Grounding JSON.

### Where `page-metadata.json` comes from

Grounding JSON requires real page dimensions and rotation, and most parsers — including
OpenDataLoader — do not emit them. That geometry comes from the **PDF**, not from the parser, which
is why the examples take a small sidecar file alongside the parser output.

Read it with any PDF library that can report MediaBox dimensions and rotation without doing
extraction: `pypdf`, `pikepdf`, or `PyMuPDF` in Python, `pdf-lib` in JavaScript, PDFBox in Java, or
`pdfinfo` from poppler-utils. Your mapper can obtain geometry any way you like; a sidecar is just
the simplest dependency-free approach.

If your parser is text-only and you have no geometry, this profile is not usable honestly yet. Do
not substitute page-sized or zero boxes — see
[Writing a Grounding JSON Mapper](../../../docs/writing-a-mapper.md).

To practice correcting one documented validation failure, copy `examples/fixtures/grounding-invalid.json`
to a working file and run `checkGrounding`. The report identifies `/elements/0/bbox` as an
out-of-page bounding box. Change its right coordinate from `60000` to `39415`, rerun the check,
and confirm that `structure` becomes `valid`. Ethos does not repair submitted artifacts.
