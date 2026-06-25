# v0.2.0 npm Vendor Refresh Validation - 2026-06-25

Validated source HEAD before this record: `aba17c7`.

v0.2.0 npm vendor refresh source commit:
`aba17c7254f2e42b9ccbf71db1a3b53113dc0e18`.

v0.2.0 npm vendor refresh source tree:
`2029e1a25629f80f251ac6ab670231187bada0a9`.

Status: **v0.2.0 npm vendor payload refreshed from validated draft CLI artifacts; npm 0.2.0 deprecated and corrected by npm 0.2.1**

This record validates the checked-in `@docushell/ethos-pdf` npm vendor payload after
refreshing it from the v0.2.0 macOS arm64 and Linux x64 draft CLI artifacts recorded in
`v0-2-0-draft-artifact-evidence-validation-2026-06-25.md`. The first npm publication as
`@docushell/ethos-pdf@0.2.0` used stale binaries and is deprecated. The corrected published npm
package is `@docushell/ethos-pdf@0.2.1`, which vendors binaries that report `ethos 0.2.0`. This
record does not approve hosted surfaces, production positioning, Windows packaged artifacts,
bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or
public benchmark claims.

## Draft Artifact Inputs

Downloaded from GitHub Actions run `28175143857`:

- `ethos-macos-arm64.tar.gz`
  - SHA256: `c588ee77bbaf99a7d933673e6cd9db190f5992e47d40955def803435a9f9fc5a`
- `ethos-linux-x64.tar.gz`
  - SHA256: `00137b20ca2c2a2d2089df1d135920b021b0905d779b1347d134e8a2fb7bfa23`

Vendor binaries assembled with:

```sh
node packages/npm/ethos-pdf/scripts/prepare-vendor.js <artifact-input-dir>
```

Result:

```text
prepared vendor/ethos-darwin-arm64
prepared vendor/ethos-linux-x64
```

## Vendor Payload Checksums

- `vendor/ethos-darwin-arm64`
  - SHA256: `e139da8fe635a3e6a42fafb49d66fcf674dbff3d7bdd8dfe844b9eb424e5b53e`
- `vendor/ethos-linux-x64`
  - SHA256: `5ab007b03eba6b1730e95053d1b0095b892a40272b610232568295a67c076a83`
- `vendor/manifest.json`
  - SHA256: `a5cd55d7670e41ede06eb7955cae76a553ebf9ba506ed374d9a409b75f3dde40`

## npm Pack Candidate

Command:

```sh
npm_config_cache=<temp-cache> npm pack --json
```

Pack toolchain:

- Node.js: `v23.11.1`
- npm: `10.9.2`

The npm shasum, tarball SHA256, and integrity below are qualified by this exact pack toolchain
because npm's gzip/tar serialization can change across npm versions. The durable package-content
provenance is the packed file list plus the per-file vendor SHA256 values as the durable content
binding for the draft-artifact-derived vendor payload above.

Candidate metadata:

- package: `@docushell/ethos-pdf@0.2.1`
- filename: `docushell-ethos-pdf-0.2.1.tgz`
- npm shasum: `8f2e2633edb60cea415915c4646da7e9b4dfb4ed`
- tarball SHA256: `c832c9efb3fc8d5480070d8eeb76e00b73f7396d9346a1d490c6ee9109708b2b`
- integrity:
  `sha512-WFNV1h/H90FssbhQBxBsriunVa1XIp8MAWeBtstJ+FKF7AsQkkXEoiSY1WQPDZ3BH6iobHuM2j/ZQ2u6zMcfdA==`
- size: `1858822`
- unpacked size: `3976145`
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
npm_config_cache=<temp-cache> npm install packages/npm/ethos-pdf/docushell-ethos-pdf-0.2.1.tgz --prefix <temp-install>
```

Result:

```text
added 1 package
```

Version smoke:

```sh
<temp-install>/node_modules/.bin/ethos --version
```

Result:

```text
ethos 0.2.0
```

PDFium boundary smoke:

```sh
<temp-install>/node_modules/.bin/ethos doctor --require-pdfium
```

Result:

```text
exit code 12
version: ethos 0.2.0
platform: darwin:arm64
packaged target: supported by the approved npm vendor manifest
ETHOS_PDFIUM_LIBRARY_PATH is unset
```

## Validation Command

```sh
python3 .github/scripts/test_v0_2_0_npm_vendor_refresh.py
make v0-2-release-prep PYTHON=python3
```

Result:

```text
test_v0_2_0_npm_vendor_refresh.py: PASS (4 tests)
v0-2-release-prep: PASS
```

## npm Publication Correction

- `@docushell/ethos-pdf@0.2.0` was published and then deprecated because registry install smoke
  reported `ethos 0.1.2`.
- `@docushell/ethos-pdf@0.2.1` was published after local tarball smoke reported `ethos 0.2.0`.
- Registry install smoke for `@docushell/ethos-pdf@0.2.1` reported `ethos 0.2.0`.

## Retained Blockers

- Windows packaged artifacts remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The `@docushell/ethos-pdf` npm vendor payload is refreshed from validated v0.2.0 draft CLI
artifacts. The corrected public npm package is `@docushell/ethos-pdf@0.2.1`, and it installs a
CLI that reports `ethos 0.2.0`.
