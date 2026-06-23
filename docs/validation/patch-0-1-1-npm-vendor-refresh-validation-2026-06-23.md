# Patch 0.1.1 npm Vendor Refresh Validation - 2026-06-23

Validated source HEAD before this record: `da5b5f4`.

npm vendor refresh source commit: `da5b5f4ed1a2645e13d8e629ed18d67babaf7eee`.

npm vendor refresh source tree: `24781c7305a3daca92cd5c1cb0ae6efe3edf1f23`.

Status: **patch 0.1.1 npm vendor payload refreshed from published GitHub Release assets; npm publication remains blocked**

This record validates the checked-in `@docushell/ethos-pdf@0.1.1` vendor payload after refreshing it
from the published GitHub Release `v0.1.1` macOS arm64 and Linux x64 CLI artifacts. It does not
approve `npm publish`, hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or public
benchmark claims.

## Published Release Artifact Inputs

Downloaded from GitHub Release `v0.1.1`:

- `ethos-macos-arm64.tar.gz`
  - SHA256: `eac79cddc6f5fc834ecc279401905729978d73e99ae11a2bea82d7356a4bcd88`
- `ethos-linux-x64.tar.gz`
  - SHA256: `842aa4b71333aecc54f344d9f5362160d0943d8efd32dffabe99dc19553916a0`

Vendor binaries assembled with:

```sh
node packages/npm/ethos-pdf/scripts/prepare-vendor.js /tmp/ethos-v0.1.1-published-assets
```

Result:

```text
prepared vendor/ethos-darwin-arm64
prepared vendor/ethos-linux-x64
```

## Vendor Payload Checksums

- `vendor/ethos-darwin-arm64`
  - SHA256: `a3d0d4be596da25313659a89de8fbff0e13f4b355462381e1bbedd05078c09f2`
- `vendor/ethos-linux-x64`
  - SHA256: `ee14be020fb79e326686fc77bcf781503f4759d2e3b7bcb6a641b2311608a354`
- `vendor/manifest.json`
  - SHA256: `7be6e6c02c0086de7c10594a6f0443c8535d5782a4ffc0bc0eed3f8ebb13bda8`

## npm Pack Candidate

Command:

```sh
npm_config_cache=/tmp/ethos-npm-vendor-refresh-cache npm pack --json
```

Pack toolchain:

- Node.js: `v23.11.1`
- npm: `10.9.2`

The npm shasum, tarball SHA256, and integrity below are qualified by this exact pack toolchain
because npm's gzip/tar serialization can change across npm versions. The durable package-content
provenance is the packed file list plus the per-file vendor SHA256 values as the durable content
binding for the release-derived vendor payload above.

Candidate metadata:

- package: `@docushell/ethos-pdf@0.1.1`
- filename: `docushell-ethos-pdf-0.1.1.tgz`
- npm shasum: a150d08395724aa186d077074782413249a48689
- tarball SHA256: `4b227d37bd125c6db1ffe40534f6cb5223a60073f26e3c4dbf60709561671d3d`
- integrity:
  `sha512-wVF4Ew6836sRncPZkvVieyQuo8FFbbBsIQ/vdupleUQZVX4YHgXb+lFZzZNcVB54Hh7srbbY17El4Z5sV7odhA==`

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
npm_config_cache=/tmp/ethos-npm-vendor-refresh-cache npm install \
  packages/npm/ethos-pdf/docushell-ethos-pdf-0.1.1.tgz \
  --prefix /tmp/ethos-npm-vendor-refresh-install
```

Result:

```text
added 1 package
```

Version smoke:

```sh
/tmp/ethos-npm-vendor-refresh-install/node_modules/.bin/ethos --version
```

Result:

```text
ethos 0.1.1
```

Missing-PDFium smoke with an existing dummy PDF returned exit code `12` and included
`ETHOS_PDFIUM_LIBRARY_PATH`.

## Validation Command

```sh
python3 .github/scripts/test_npm_tarball_candidate_evidence.py
```

Result:

```text
Ran 4 tests
OK
```

## Retained Blockers

- npm publication remains blocked until a dedicated decider record approves `npm publish` for this
  exact `0.1.1` candidate and public wording.
- Windows packaged artifacts remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The `@docushell/ethos-pdf@0.1.1` npm vendor payload is refreshed from the published `v0.1.1`
GitHub Release assets and locally validated. npm publication remains blocked pending a dedicated
approval request, approval decision, explicit operator action, and closeout evidence.
