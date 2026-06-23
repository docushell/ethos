# npm Vendor Binary Payload Strategy Validation - 2026-06-23

- Validated source HEAD before this record: `e705962`

npm vendor payload strategy source commit: `e705962eb08224c2c397126adb40ec2110020f95`

npm vendor payload strategy source tree: `3741717e6b5d9bbb7c8f46e5aa4a81c05147fd0c`

Status: **npm vendor binary payload implementation lane prepared; npm publication remains blocked**

This record validates the implementation strategy for packaging the already-approved macOS arm64
and Linux x64 CLI release artifacts inside `@docushell/ethos-pdf`. It does not approve npm
publication, Windows packaged artifacts, hosted surfaces, production positioning, bundled
project-maintained PDFium builds, `ethos-doc`, `ethos-rag`, public benchmark reports, or public
benchmark claims.

## Implemented Package Contract

- `packages/npm/ethos-pdf/package.json` includes `vendor/` in the npm package `files` list.
- `packages/npm/ethos-pdf/vendor/manifest.json` binds the supported npm targets to approved
  release asset names and SHA256 values:
  - `darwin:arm64` -> `ethos-darwin-arm64` from `ethos-macos-arm64.tar.gz`;
  - `linux:x64` -> `ethos-linux-x64` from `ethos-linux-x64.tar.gz`.
- `packages/npm/ethos-pdf/bin/ethos-pdf.js` validates the vendor manifest before resolving the
  packaged platform binary.
- `packages/npm/ethos-pdf/scripts/prepare-vendor.js` accepts a local release artifact directory,
  verifies release archive checksums, extracts the `ethos` executable, and writes the exact vendor
  binary names used by runtime platform selection.

## Validation Commands

```sh
npm test --prefix packages/npm/ethos-pdf
```

Result:

```text
platform selection ok
vendor assembly ok
```

```sh
python3 .github/scripts/test_npm_binary_package_scaffold.py
```

Result:

```text
Ran 6 tests
OK
```

## Covered Edge Cases

- unsupported `win32:x64`, `darwin:x64`, and `linux:arm64` targets are rejected before invoking a
  binary;
- missing selected vendor binary exits with the existing clear "binary is missing" error;
- malformed or incomplete vendor manifests fail validation;
- release archive checksum mismatch fails vendor assembly with `Checksum mismatch`;
- missing release archive fails vendor assembly with `Missing release asset`;
- `npm pack --json --dry-run` includes `vendor/manifest.json`, `vendor/ethos-darwin-arm64`, and
  `vendor/ethos-linux-x64` when the vendor binaries are present.

## Retained Blockers

- npm publication remains blocked until a dedicated decider record binds the exact assembled npm
  tarball, source commit, package version, vendor payload checksums, and public wording.
- Windows packaged artifacts remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The npm binary payload strategy is implemented and locally validated for the two approved first
public evaluation CLI artifacts. The implementation prepares the package for a future npm decider
lane but does not publish or approve npm distribution.
