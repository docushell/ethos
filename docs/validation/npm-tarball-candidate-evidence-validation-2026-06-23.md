# npm Tarball Candidate Evidence Validation - 2026-06-23

- Validated source HEAD before this record: `5a956a5`

npm tarball candidate source commit: `5a956a562ea70e1ae63eccb4e830d68699d5f767`

npm tarball candidate source tree: `5f9d252ed8544850bd7b1327dfb2e7f1660b3a03`

Status: **exact npm tarball candidate assembled and locally validated; npm publication remains blocked**

This record validates a local npm tarball candidate for `@docushell/ethos-pdf@0.1.0` using the
already-approved macOS arm64 and Linux x64 CLI release artifacts. It does not approve `npm publish`,
Windows packaged artifacts, hosted surfaces, production positioning, bundled project-maintained
PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or public benchmark claims.

## Release Artifact Inputs

Downloaded from GitHub Release `v0.1.0`:

- `ethos-macos-arm64.tar.gz`
  - SHA256: `9cb66dac20f93c55f574357dd0494e0cad711e1e5969cdfb29ae4c64ddf7c95d`
- `ethos-linux-x64.tar.gz`
  - SHA256: `59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2`

Vendor binaries assembled with:

```sh
npm run prepare:vendor -- /tmp/ethos-npm-candidate-assets
```

Result:

```text
prepared vendor/ethos-darwin-arm64
prepared vendor/ethos-linux-x64
```

## Vendor Payload Checksums

- `vendor/ethos-darwin-arm64`
  - SHA256: `f1b0c9e47dace78b7e8b3639b9445afe9a01f0db5d5b7b0bd81858def4df2cf5`
- `vendor/ethos-linux-x64`
  - SHA256: `7ef796a6d1c86b7c3b5b1afe58dd9cc348b706cec441602833540d8a0c9260ac`
- `vendor/manifest.json`
  - SHA256: `0d03124957255dca55b7374e3318707da488f4b6648bfcec5e6e598079353b1f`

## npm Pack Candidate

Command:

```sh
npm_config_cache=/tmp/ethos-npm-cache npm pack --json
```

Pack toolchain:

- Node.js: `v23.11.1`
- npm: `10.9.2`

The npm shasum, tarball SHA256, and integrity below are qualified by this exact pack toolchain
because npm's gzip/tar serialization can change across npm versions. The durable package-content
provenance is the packed file list plus the per-file SHA256 values for the release-derived vendor
payload above.

Candidate metadata:

- package: `@docushell/ethos-pdf@0.1.0`
- filename: `docushell-ethos-pdf-0.1.0.tgz`
- npm shasum: `17a053c5ccb802bca2a295e1b1d0e6106c6a3ca6`
- tarball SHA256: `8d0483d69a6de471dee52c8ef06d46712c06861682a0d7319ca573fdb1fe6376`
- integrity:
  `sha512-uWTHYd9Hfkm3nkahK2UchCMOVvYWe82z03jffZnX6aYPqYGd6LkuiEoTH5DjrXl+oA817EjlE88fIKBxZbhjMw==`

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

## Provenance Chain

- GitHub Release `v0.1.0` approved and published the macOS arm64 and Linux x64 CLI release
  archives named above.
- `scripts/prepare-vendor.js` extracted only the `ethos` executable from each approved archive.
- The extracted vendor payload is durably bound by per-file SHA256:
  `vendor/ethos-darwin-arm64`, `vendor/ethos-linux-x64`, and `vendor/manifest.json`.
- The npm tarball shasum, tarball SHA256, and integrity are reproducibility checks only under
  Node.js `v23.11.1` and npm `10.9.2`; they are not the primary cross-toolchain provenance binding.

## Local Install Smoke

Install command:

```sh
npm_config_cache=/tmp/ethos-npm-cache npm install \
  <npm-tarball-candidate-path>/docushell-ethos-pdf-0.1.0.tgz \
  --prefix /tmp/ethos-npm-candidate-install
```

Result:

```text
added 1 package
```

Version smoke:

```sh
/tmp/ethos-npm-candidate-install/node_modules/.bin/ethos --version
```

Result:

```text
ethos 0.1.0
```

Missing-PDFium smoke with an existing dummy PDF returned exit code `12` and included:

```text
PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path
```

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
  exact candidate and public wording.
- Windows packaged artifacts remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The exact npm tarball candidate is assembled and locally validated. This closes the candidate
evidence step for the npm lane but does not approve publication. Any operator reproducing or
publishing this candidate must use Node.js `v23.11.1` and npm `10.9.2` for npm tarball hash
comparison, and must treat the per-file vendor SHA256 values as the durable content binding.
