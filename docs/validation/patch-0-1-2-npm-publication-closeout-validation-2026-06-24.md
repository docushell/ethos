# Patch 0.1.2 npm Publication Closeout Validation - 2026-06-24

- Validated source HEAD before this record: `b7476e9`

npm publication closeout source commit: `b7476e95db438b849d12e44a54296da9380091e2`

npm publication closeout source tree: `958417827cb1678ec2bf492c12a698143c58f58b`

Status: **patch 0.1.2 npm package evaluation surface published**

This record closes the bounded patch `0.1.2` npm publication lane for `@docushell/ethos-pdf@0.1.2`.
It records the operator publish action and registry verification for the exact approved npm
candidate. It does not approve public installation wording changes, hosted surfaces, production
positioning, Windows packaged artifacts, bundled project-maintained PDFium builds, `ethos-doc`,
`ethos-rag`, public benchmark reports, or public benchmark claims.

## Published Package

- Package: `@docushell/ethos-pdf`
- Version: `0.1.2`
- Registry: `https://registry.npmjs.org/`
- Publish command:

```sh
npm publish --access public
```

Publish result:

```text
+ @docushell/ethos-pdf@0.1.2
```

The first publish attempt failed with npm `E404`; that blocker is recorded in
`docs/validation/patch-0-1-2-npm-publication-blocker-validation-2026-06-24.md`. After npm login
and authentication completed, the retry succeeded.

## Registry Verification

Package command:

```sh
npm view @docushell/ethos-pdf@0.1.2 --json --registry=https://registry.npmjs.org/
```

Result excerpt:

```json
{
  "dist-tags": {
    "latest": "0.1.2"
  },
  "versions": [
    "0.0.0-reserved.0",
    "0.1.0",
    "0.1.1",
    "0.1.2"
  ],
  "time": {
    "0.1.2": "2026-06-24T17:48:40.528Z"
  },
  "version": "0.1.2",
  "gitHead": "b7476e95db438b849d12e44a54296da9380091e2",
  "_nodeVersion": "23.11.1",
  "_npmVersion": "10.9.2",
  "dist": {
    "integrity": "sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg==",
    "shasum": "39b85d74f588666bfbf69e423a189c2039743de4",
    "tarball": "https://registry.npmjs.org/@docushell/ethos-pdf/-/ethos-pdf-0.1.2.tgz",
    "fileCount": 11,
    "unpackedSize": 3934993
  }
}
```

Versions command:

```sh
npm view @docushell/ethos-pdf version versions --json --registry=https://registry.npmjs.org/
```

Result:

```json
{
  "version": "0.1.2",
  "versions": [
    "0.0.0-reserved.0",
    "0.1.0",
    "0.1.1",
    "0.1.2"
  ]
}
```

The registry latest is now `0.1.2`.

## Approved Candidate Binding

- npm shasum: 39b85d74f588666bfbf69e423a189c2039743de4
- npm integrity:
  `sha512-3loga13tnAkUkjuOrjKjpA0D3Cm5lW6Al8OwTyRx7NGMt6EB4gMpZOoaSCPjZWchYv7as1uPaEnZyOqrmFOPxg==`
- file count: `11`
- unpacked size: `3934993`
- Node.js pack/publish toolchain approved for this candidate: `v23.11.1`
- npm pack/publish toolchain approved for this candidate: `10.9.2`
- durable vendor payload checksums remain:
  - `vendor/ethos-darwin-arm64`:
    `47c2f4aaac6cb6a1ca5cf1d9a0cc1f897ef00c48cdd8549455de70f0fbc6bcc1`
  - `vendor/ethos-linux-x64`:
    `e75122f2954efbde6b8c07a98601b8d4a3b7a06647891a9e60d6aef4046649c3`
  - `vendor/manifest.json`:
    `d557e081b946be0f839b17b8593027e31267b668498e202372026020f68a97a1`

## Retained Blockers

- Public installation wording remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

`@docushell/ethos-pdf@0.1.2` is live on npm as a bounded evaluation package for the approved macOS
arm64 and Linux x64 CLI binary payload. PDFium remains caller-provided through
`ETHOS_PDFIUM_LIBRARY_PATH`. Public installation wording remains blocked until a separate public
wording closeout lane passes.
