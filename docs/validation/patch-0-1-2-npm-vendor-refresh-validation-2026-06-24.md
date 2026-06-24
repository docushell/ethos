# Patch 0.1.2 npm Vendor Refresh Validation - 2026-06-24

Validated source HEAD before this record: `2323398`.

npm vendor refresh source commit: `23233986035e0f4a20295b24a9cfafafe65aa117`.

npm vendor refresh source tree: `750551f51094f0bc9625c781b8cc978431e431c3`.

Status: **patch 0.1.2 npm vendor payload refreshed from published GitHub Release assets; npm publication remains blocked**

This record validates the checked-in `@docushell/ethos-pdf@0.1.2` npm vendor payload after
refreshing it from the published GitHub Release `v0.1.2` macOS arm64 and Linux x64 CLI artifacts.
It does not approve `npm publish`, public installation wording, registry publication, hosted
surfaces, production positioning, Windows packaged artifacts, bundled project-maintained PDFium
builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or public benchmark claims.

## Published Release Artifact Inputs

Downloaded from GitHub Release `v0.1.2`:

- `ethos-macos-arm64.tar.gz`
  - SHA256: `7da7da71fb0c21b25cd2ffc198480ee80bf9f0c9e70e461cffbdcbdda8d7023c`
- `ethos-linux-x64.tar.gz`
  - SHA256: `4e260b464dc9557bc31c29fb1d1dfa75311fe12734bc79af4a31e1649797e456`

Vendor binaries assembled with:

```sh
node packages/npm/ethos-pdf/scripts/prepare-vendor.js /tmp/ethos-v0.1.2-published-assets
```

Result:

```text
prepared vendor/ethos-darwin-arm64
prepared vendor/ethos-linux-x64
```

## Vendor Payload Checksums

- `vendor/ethos-darwin-arm64`
  - SHA256: `47c2f4aaac6cb6a1ca5cf1d9a0cc1f897ef00c48cdd8549455de70f0fbc6bcc1`
- `vendor/ethos-linux-x64`
  - SHA256: `e75122f2954efbde6b8c07a98601b8d4a3b7a06647891a9e60d6aef4046649c3`
- `vendor/manifest.json`
  - SHA256: `d557e081b946be0f839b17b8593027e31267b668498e202372026020f68a97a1`

## npm Pack Candidate

Command:

```sh
npm_config_cache=/tmp/ethos-npm-vendor-refresh-0.1.2-cache npm pack --json
```

Pack toolchain:

- Node.js: `v23.11.1`
- npm: `10.9.2`

The npm shasum, tarball SHA256, and integrity below are qualified by this exact pack toolchain
because npm's gzip/tar serialization can change across npm versions. The durable package-content
provenance is the packed file list plus the per-file vendor SHA256 values as the durable content
binding for the release-derived vendor payload above.

Candidate metadata:

- package: `@docushell/ethos-pdf@0.1.2`
- filename: `docushell-ethos-pdf-0.1.2.tgz`
- npm shasum: 39b85d74f588666bfbf69e423a189c2039743de4
- tarball SHA256: `77cbc9c79dd60cc16073690a186e149ecbaabacce035fb0bd3603b267ce64112`
- integrity:
  `sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg==`

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
npm_config_cache=/tmp/ethos-npm-vendor-refresh-0.1.2-cache npm install \
  packages/npm/ethos-pdf/docushell-ethos-pdf-0.1.2.tgz \
  --prefix /tmp/ethos-npm-vendor-refresh-0.1.2-install
```

Result:

```text
added 1 package
```

Version smoke:

```sh
/tmp/ethos-npm-vendor-refresh-0.1.2-install/node_modules/.bin/ethos --version
```

Result:

```text
ethos 0.1.2
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
  exact `0.1.2` candidate and public wording.
- Public installation wording remains blocked until npm publication, registry availability, and a
  dedicated public wording closeout record pass.
- Registry publication remains blocked.
- Windows packaged artifacts remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The `@docushell/ethos-pdf@0.1.2` npm vendor payload is refreshed from the published `v0.1.2`
GitHub Release assets and locally validated. npm publication remains blocked pending a dedicated
approval request, approval decision, explicit operator action, and closeout evidence. Public
installation wording remains blocked.
