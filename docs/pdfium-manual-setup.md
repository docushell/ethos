# PDFium Manual Setup

Ethos first public release preparation keeps PDFium caller-provided. The CLI, Python package, and
npm package do not bundle PDFium and do not download PDFium.

Set `ETHOS_PDFIUM_LIBRARY_PATH` to the platform PDFium dynamic library before running
PDFium-backed parse or crop commands.

## Paved setup path

From an Ethos source checkout, run:

```sh
scripts/fetch-pdfium.sh
```

The script selects the macOS arm64 or Linux x64 pin, verifies the downloaded archive sha256
before extraction, verifies the runtime-library sha256 after extraction, and prints the exact
`ETHOS_PDFIUM_LIBRARY_PATH` export. Apply that export, then require the configured runtime:

```sh
ethos doctor --require-pdfium
```

`ethos doctor` never downloads or changes PDFium. Without `--require-pdfium`, a missing or invalid
runtime is a visible warning and exit `0`; with the flag it is an error and exit `12`.

Modern Python wheels do not execute post-install hooks. After installing `ethos-pdf`, run
`python -m ethos_pdf` to print the same setup path. The npm package prints it as a non-blocking
postinstall warning when `ETHOS_PDFIUM_LIBRARY_PATH` is unset. Neither package automatically runs
the fetch script.

## Manual paths

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

## Consumer Dockerfile

Vendor the release-matched `scripts/fetch-pdfium.sh` beside the consumer Dockerfile, then use this
Linux x64 worker-stage pattern. The earlier CLI stage must provide the sha256-verified `ethos`
binary as `/out/ethos`.

```dockerfile
FROM --platform=linux/amd64 debian:bookworm-slim AS ethos-runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ethos-cli /out/ethos /usr/local/bin/ethos
COPY scripts/fetch-pdfium.sh /usr/local/bin/fetch-pdfium
RUN /usr/local/bin/fetch-pdfium /opt/ethos/pdfium
ENV ETHOS_PDFIUM_LIBRARY_PATH=/opt/ethos/pdfium/lib/libpdfium.so
RUN ethos doctor --require-pdfium
```

Keep `--platform=linux/amd64`: the current Linux CLI and PDFium pins are x64. Both download hashes
remain single-sourced in the deterministic profile and mirrored by the fetch script; a mismatch
fails the image build.

This document does not approve bundled project-maintained PDFium builds, hosted surfaces,
production positioning, or public benchmark reports or claims.
