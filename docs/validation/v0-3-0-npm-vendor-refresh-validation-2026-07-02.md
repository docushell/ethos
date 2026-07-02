# v0.3.0 npm Vendor Refresh Validation - 2026-07-02

Validated source HEAD before this record: `8e20db3`.

v0.3.0 npm vendor refresh source commit:
`8e20db3c796f051925b059f62c294f41f981bcfa`.

v0.3.0 npm vendor refresh source tree:
`7f528ace4993e21e457aefb5a0aa65ed40297c6c`.

Status: **v0.3.0 npm vendor payload refreshed from published GitHub Release assets; npm publication remains blocked**

This record validates the checked-in `@docushell/ethos-pdf@0.3.0` npm source package candidate
after refreshing its vendor payload from the published GitHub Release `v0.3.0` macOS arm64 and
Linux x64 CLI artifacts recorded in
`v0-3-0-artifact-publication-closeout-validation-2026-07-02.md`. It does not approve `npm publish`,
public `0.3.0` install wording, package tags, release tags, hosted surfaces, production
positioning, Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`,
`ethos-rag`, public benchmark reports, public benchmark claims, or DocuShell integration.

## Published Release Artifact Inputs

Downloaded from GitHub Release `v0.3.0`:

- `ethos-macos-arm64.tar.gz`
  - SHA256: `efb163f140bf4afffd1caeb396f79e42f484591c3e90a86810ca6c0f0c209c96`
- `ethos-linux-x64.tar.gz`
  - SHA256: `b549ba5968e04b7679a8d3e879cd45d27f3e9a6fd226eee5c270a4e4f5c01405`

Vendor binaries assembled with:

```sh
node packages/npm/ethos-pdf/scripts/prepare-vendor.js target/v0-3-published-assets-check
```

Result:

```text
prepared vendor/ethos-darwin-arm64
prepared vendor/ethos-linux-x64
```

## Vendor Payload Checksums

- `vendor/ethos-darwin-arm64`
  - SHA256: `777e1fb243425a46b83b63ed92fbf7cb810f59cfedd81cfe671cf791410c20dc`
- `vendor/ethos-linux-x64`
  - SHA256: `b416993fc38e6f794611b8b71789ed85af18eb6aa63fef380d9ae7738661f154`
- `vendor/manifest.json`
  - SHA256: `e313b42e49b258171611935455fd9e70bad7ce61c409df63ab90aaa2732a46af`

The checked-in package metadata now identifies the source package candidate as
`@docushell/ethos-pdf@0.3.0`. The current published npm package remains
`@docushell/ethos-pdf@0.2.1` until a separate npm approval decision, operator publish, registry
smoke, and closeout record pass.

## npm Pack Candidate

Command:

```sh
npm_config_cache=<target-cache> npm pack --json --pack-destination <target-evidence-dir>
```

Pack toolchain:

- Node.js: `v23.11.1`
- npm: `10.9.2`

The npm shasum, tarball SHA256, and integrity below are qualified by this exact pack toolchain
because npm's gzip/tar serialization can change across npm versions. The durable package-content
provenance is the packed file list plus the per-file vendor SHA256 values as the durable content
binding for the release-derived vendor payload above.

Candidate metadata:

- package: `@docushell/ethos-pdf@0.3.0`
- filename: `docushell-ethos-pdf-0.3.0.tgz`
- npm shasum: `1a90cebd8d52011ea5c41629becdfb37dec73ee7`
- tarball SHA256: `1b72ef2fd9415f9edff93319ee2763e8f67cd6168ea00cd64d89a3760101c5fa`
- integrity:
  `sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ==`
- size: `1865393`
- unpacked size: `4005888`
- entry count: `11`

Packed file list:

- `LICENSE`
- `NOTICE`
- `QUICKSTART.md`
- `README.md`
- `bin/ethos-pdf.js`
- `package.json`
- `scripts/postinstall.js`
- `scripts/prepare-vendor.js`
- `vendor/ethos-darwin-arm64`
- `vendor/ethos-linux-x64`
- `vendor/manifest.json`

The vendor binaries were packed with executable mode `493`.

## Local Install Smoke

Install command:

```sh
npm_config_cache=<target-cache> npm install <target-evidence-dir>/docushell-ethos-pdf-0.3.0.tgz \
  --prefix <target-install-smoke>
```

Result:

```text
added 1 package
```

Version smoke:

```sh
<target-install-smoke>/node_modules/.bin/ethos --version
```

Result:

```text
ethos 0.3.0
```

PDFium boundary smoke:

```sh
<target-install-smoke>/node_modules/.bin/ethos doctor --require-pdfium
```

Result:

```text
exit code 12
version: ethos 0.3.0
platform: darwin:arm64
packaged target: supported by the approved npm vendor manifest
ETHOS_PDFIUM_LIBRARY_PATH is unset
```

## Validation Commands

```sh
node packages/npm/ethos-pdf/scripts/prepare-vendor.js target/v0-3-published-assets-check
packages/npm/ethos-pdf/vendor/ethos-darwin-arm64 --version
node packages/npm/ethos-pdf/test/platform-selection.test.js
node packages/npm/ethos-pdf/test/vendor-assembly.test.js
python3 .github/scripts/test_v0_3_0_npm_vendor_refresh.py
python3 .github/scripts/test_npm_binary_package_scaffold.py
npm test --prefix packages/npm/ethos-pdf
make v0-3-release-prep PYTHON=python3
```

## Retained Blockers

- npm publication remains blocked until a dedicated decider record approves `npm publish` for this
  exact `0.3.0` candidate.
- Public `0.3.0` install wording remains blocked until npm publication, registry availability,
  artifact/package availability, tag decisions, and a dedicated public wording closeout record pass.
- Release tag creation remains blocked.
- Package tag creation remains blocked.
- DocuShell integration remains blocked.
- Windows packaged artifacts remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.
- PDFium remains caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Result

The `@docushell/ethos-pdf@0.3.0` npm source package candidate is refreshed from the published
`v0.3.0` GitHub Release assets and locally validated. npm publication remains blocked pending a
dedicated approval request, approval decision, explicit operator action, and closeout evidence.
Public `0.3.0` install wording remains blocked.
