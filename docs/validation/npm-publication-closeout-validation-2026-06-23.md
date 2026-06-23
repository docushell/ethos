# npm Publication Closeout Validation - 2026-06-23

- Validated source HEAD before this record: `bbaa34d`

npm publication closeout source commit: `bbaa34dbf4d6dfaa2e8d637f22b5b494cd81d721`

npm publication closeout source tree: `ab3e1cf061ba5a9605e415177b299e5b06187d30`

Status: **npm package evaluation surface published**

This record closes the bounded npm publication lane for `@docushell/ethos-pdf@0.1.0`. It records
the operator publish action and registry verification for the exact approved npm candidate. It does
not approve hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or public
benchmark claims.

## Published Package

- Package: `@docushell/ethos-pdf`
- Version: `0.1.0`
- Registry: `https://registry.npmjs.org/`
- Publish command:

```sh
npm publish --access public --registry=https://registry.npmjs.org/
```

Publish result:

```text
+ @docushell/ethos-pdf@0.1.0
```

## Publish Warning Captured

npm emitted this warning during publish:

```text
npm warn publish npm auto-corrected some errors in your package.json when publishing. Please run "npm pkg fix" to address these errors.
npm warn publish errors corrected:
npm warn publish "bin[ethos]" script name was cleaned
```

The published tarball details still matched the approved package candidate: shasum,
integrity, file count, package version, and 11-file contents were unchanged by the warning.

## Registry Verification

Version command:

```sh
npm view @docushell/ethos-pdf version --registry=https://registry.npmjs.org/
```

Result:

```text
0.1.0
```

Versions command:

```sh
npm view @docushell/ethos-pdf versions --json --registry=https://registry.npmjs.org/
```

Result:

```json
[
  "0.0.0-reserved.0",
  "0.1.0"
]
```

Dist command:

```sh
npm view @docushell/ethos-pdf dist --json --registry=https://registry.npmjs.org/
```

Result:

```json
{
  "integrity": "sha512-uWTHYd9Hfkm3nkahK2UchCMOVvYWe82z03jffZnX6aYPqYGd6LkuiEoTH5DjrXl+oA817EjlE88fIKBxZbhjMw==",
  "shasum": "17a053c5ccb802bca2a295e1b1d0e6106c6a3ca6",
  "tarball": "https://registry.npmjs.org/@docushell/ethos-pdf/-/ethos-pdf-0.1.0.tgz",
  "fileCount": 11,
  "unpackedSize": 3774465
}
```

## Approved Candidate Binding

- npm shasum: `17a053c5ccb802bca2a295e1b1d0e6106c6a3ca6`
- npm integrity:
  `sha512-uWTHYd9Hfkm3nkahK2UchCMOVvYWe82z03jffZnX6aYPqYGd6LkuiEoTH5DjrXl+oA817EjlE88fIKBxZbhjMw==`
- file count: `11`
- unpacked size: `3774465`
- Node.js pack/publish toolchain approved for this candidate: `v23.11.1`
- npm pack/publish toolchain approved for this candidate: `10.9.2`
- durable vendor payload checksums remain:
  - `vendor/ethos-darwin-arm64`:
    `f1b0c9e47dace78b7e8b3639b9445afe9a01f0db5d5b7b0bd81858def4df2cf5`
  - `vendor/ethos-linux-x64`:
    `7ef796a6d1c86b7c3b5b1afe58dd9cc348b706cec441602833540d8a0c9260ac`
  - `vendor/manifest.json`:
    `0d03124957255dca55b7374e3318707da488f4b6648bfcec5e6e598079353b1f`

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

`@docushell/ethos-pdf@0.1.0` is live on npm as a bounded evaluation package for the approved macOS
arm64 and Linux x64 CLI binary payload. PDFium remains caller-provided through
`ETHOS_PDFIUM_LIBRARY_PATH`.
