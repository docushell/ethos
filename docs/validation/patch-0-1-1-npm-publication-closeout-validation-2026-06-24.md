# Patch 0.1.1 npm Publication Closeout Validation - 2026-06-24

- Validated source HEAD before this record: `65360a9`

npm publication closeout source commit: `65360a9012104227ba939f6d30f2ec7b82b2ac4d`

npm publication closeout source tree: `85465e6eb1918155088e4d4cb4f5608f5ea65589`

Status: **patch 0.1.1 npm package evaluation surface published**

This record closes the bounded patch `0.1.1` npm publication lane for `@docushell/ethos-pdf@0.1.1`.
It records the operator publish action and registry verification for the exact approved npm
candidate. It does not approve hosted surfaces, production positioning, Windows packaged artifacts,
bundled project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or
public benchmark claims.

## Published Package

- Package: `@docushell/ethos-pdf`
- Version: `0.1.1`
- Registry: `https://registry.npmjs.org/`
- Publish command:

```sh
npm publish --access public
```

Publish result:

```text
+ @docushell/ethos-pdf@0.1.1
```

## Publish Warning Captured

npm emitted this warning during publish:

```text
npm warn publish npm auto-corrected some errors in your package.json when publishing. Please run "npm pkg fix" to address these errors.
npm warn publish errors corrected:
npm warn publish "bin[ethos]" script name was cleaned
```

The published tarball details still matched the approved package candidate: shasum, integrity, file
count, package version, and 11-file contents were unchanged by the warning.

## Registry Verification

Package command:

```sh
npm view @docushell/ethos-pdf --json --registry=https://registry.npmjs.org/
```

Result excerpt:

```json
{
  "dist-tags": {
    "latest": "0.1.1"
  },
  "versions": [
    "0.0.0-reserved.0",
    "0.1.0",
    "0.1.1"
  ],
  "time": {
    "0.1.1": "2026-06-23T18:33:29.003Z"
  },
  "version": "0.1.1",
  "gitHead": "65360a9012104227ba939f6d30f2ec7b82b2ac4d",
  "_nodeVersion": "23.11.1",
  "_npmVersion": "10.9.2",
  "dist": {
    "integrity": "sha512-wVF4Ew6836sRncPZkvVieyQuo8FFbbBsIQ/vdupleUQZVX4YHgXb+lFZzZNcVB54Hh7srbbY17El4Z5sV7odhA==",
    "shasum": "a150d08395724aa186d077074782413249a48689",
    "tarball": "https://registry.npmjs.org/@docushell/ethos-pdf/-/ethos-pdf-0.1.1.tgz",
    "fileCount": 11,
    "unpackedSize": 3811617
  }
}
```

Versions command:

```sh
npm view @docushell/ethos-pdf versions --json --registry=https://registry.npmjs.org/
```

Result:

```json
[
  "0.0.0-reserved.0",
  "0.1.0",
  "0.1.1"
]
```

## Approved Candidate Binding

- npm shasum: a150d08395724aa186d077074782413249a48689
- npm integrity:
  `sha512-wVF4Ew6836sRncPZkvVieyQuo8FFbbBsIQ/vdupleUQZVX4YHgXb+lFZzZNcVB54Hh7srbbY17El4Z5sV7odhA==`
- file count: `11`
- unpacked size: `3811617`
- Node.js pack/publish toolchain approved for this candidate: `v23.11.1`
- npm pack/publish toolchain approved for this candidate: `10.9.2`
- durable vendor payload checksums remain:
  - `vendor/ethos-darwin-arm64`:
    `a3d0d4be596da25313659a89de8fbff0e13f4b355462381e1bbedd05078c09f2`
  - `vendor/ethos-linux-x64`:
    `ee14be020fb79e326686fc77bcf781503f4759d2e3b7bcb6a641b2311608a354`
  - `vendor/manifest.json`:
    `7be6e6c02c0086de7c10594a6f0443c8535d5782a4ffc0bc0eed3f8ebb13bda8`

## Retained Blockers

- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

`@docushell/ethos-pdf@0.1.1` is live on npm as a bounded evaluation package for the approved macOS
arm64 and Linux x64 CLI binary payload. PDFium remains caller-provided through
`ETHOS_PDFIUM_LIBRARY_PATH`.
