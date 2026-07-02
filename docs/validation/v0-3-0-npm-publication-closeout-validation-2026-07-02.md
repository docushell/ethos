# v0.3.0 npm Publication Closeout Validation - 2026-07-02

Validated source HEAD before this record: `bb93a30`.

v0.3.0 npm publication closeout source commit:
`bb93a30140ba4d3a64faacfb3ac0bed1e4fc59b2`.

v0.3.0 npm publication closeout source tree:
`1e562c9604cb8e1105ff51145f8f8a9ff984c0a8`.

Status: **v0.3.0 npm publication closeout recorded; `@docushell/ethos-pdf@0.3.0` is live on npm**

This record closes the exact npm publication lane approved by
`v0-3-0-npm-publication-approval-decision-validation-2026-07-02.md`. It records live registry
evidence for only `@docushell/ethos-pdf@0.3.0`. It does not change public `0.3.0` install wording,
create package tags or release tags, approve DocuShell integration, add hosted surfaces, approve
production positioning, add Windows packaged artifacts, bundle PDFium, approve `ethos-doc`,
approve `ethos-rag`, or approve public benchmark reports or claims.

The previous published npm baseline for this lane was `@docushell/ethos-pdf@0.2.1`.

## Subject

- Repository: `docushell/ethos`
- Lane: npm publication closeout
- Package: `@docushell/ethos-pdf`
- Version: `0.3.0`
- Published package: `@docushell/ethos-pdf@0.3.0`
- Approval decision record:
  `docs/validation/v0-3-0-npm-publication-approval-decision-validation-2026-07-02.md`
- Approval request record:
  `docs/validation/v0-3-0-npm-publication-approval-request-validation-2026-07-02.md`
- Candidate evidence record:
  `docs/validation/v0-3-0-npm-vendor-refresh-validation-2026-07-02.md`
- Published package gitHead: `bb93a30140ba4d3a64faacfb3ac0bed1e4fc59b2`
- PDFium policy: caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`

## Publish Evidence

Command:

```sh
npm publish --access public
```

Bounded result:

```text
+ @docushell/ethos-pdf@0.3.0
```

The publish notice reported:

- package: `@docushell/ethos-pdf@0.3.0`
- filename: `docushell-ethos-pdf-0.3.0.tgz`
- package size: `1.9 MB`
- unpacked size: `4.0 MB`
- npm shasum: 1a90cebd8d52011ea5c41629becdfb37dec73ee7
- integrity:
  `sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ==`
- total files: `11`
- publish destination: `https://registry.npmjs.org/`
- access: public

npm also warned:

```text
npm auto-corrected some errors in your package.json when publishing.
"bin[ethos]" script name was cleaned
```

That warning did not prevent publication. This closeout does not run `npm pkg fix`, does not
modify `package.json`, and does not mutate the source package after the exact approved publication.
A separate hygiene lane may inspect npm's package-json correction if needed.

## Registry Evidence

Command:

```sh
npm view @docushell/ethos-pdf version
```

Result:

```text
0.3.0
```

Registry latest is now `0.3.0`.

Command:

```sh
npm view @docushell/ethos-pdf@0.3.0 dist --json
```

Result:

```json
{
  "integrity": "sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ==",
  "shasum": "1a90cebd8d52011ea5c41629becdfb37dec73ee7",
  "tarball": "https://registry.npmjs.org/@docushell/ethos-pdf/-/ethos-pdf-0.3.0.tgz",
  "fileCount": 11,
  "unpackedSize": 4005888,
  "signatures": [
    {
      "keyid": "SHA256:DhQ8wR5APBvFHLF/+Tc+AYvPOdTpcIDqOhxsBHRwC7U",
      "sig": "MEUCIQDba2Q4kRW068MuweRo5a5Hz+vLTtgV0S02cU3xp5POtwIgWUf5YaUD1fv0dCAcRlijDgNVl+P2AjBPVG36DmZ7WDI="
    }
  ]
}
```

Additional public registry metadata observed for `@docushell/ethos-pdf@0.3.0`:

- `dist-tags`: `"latest": "0.3.0"`
- published time: `2026-07-02T12:01:02.015Z`
- Node.js: `v23.11.1`
- npm: `10.9.2`
- npm user: `docushell-dev <hello@docushell.com>`
- supported OS values: `darwin`, `linux`
- supported CPU values: `arm64`, `x64`
- binary entry: `ethos` -> `bin/ethos-pdf.js`

## Candidate Binding

The published registry metadata matches the approved candidate:

- npm shasum: 1a90cebd8d52011ea5c41629becdfb37dec73ee7
- integrity:
  `sha512-ZWoIY5BO7O8tzN88ICGvRasmOt7/RSN/xWFM2ONT8lavQqIOuCY/bQjvxnuK9vGpNeogh8X4UXHLLSRKqqHVOQ==`
- file count: `11`
- unpacked size: `4005888`
- tarball URL:
  `https://registry.npmjs.org/@docushell/ethos-pdf/-/ethos-pdf-0.3.0.tgz`
- source gitHead: `bb93a30140ba4d3a64faacfb3ac0bed1e4fc59b2`

The checked-in vendor payload remains bound by the durable per-file SHA256 values from the vendor
refresh and approval decision records:

- `vendor/ethos-darwin-arm64`
  - SHA256: `777e1fb243425a46b83b63ed92fbf7cb810f59cfedd81cfe671cf791410c20dc`
- `vendor/ethos-linux-x64`
  - SHA256: `b416993fc38e6f794611b8b71789ed85af18eb6aa63fef380d9ae7738661f154`
- `vendor/manifest.json`
  - SHA256: `e313b42e49b258171611935455fd9e70bad7ce61c409df63ab90aaa2732a46af`

## Closeout Boundary

This closeout supersedes the npm publication blocker only for the exact package and version:
`@docushell/ethos-pdf@0.3.0`.

Public `0.3.0` install wording remains blocked.
package tag creation remains blocked.
release tag creation remains blocked.
DocuShell integration remains blocked.
hosted surfaces remain blocked.
production positioning remains blocked.
public benchmark reports remain blocked.
public benchmark claims remain blocked.
Windows packaged artifacts remain blocked.
bundled project-maintained PDFium builds remain blocked.
`ethos-doc` remains blocked.
`ethos-rag` remains blocked.
broader public wording remains blocked.

PDFium-backed commands remain caller-provided through `ETHOS_PDFIUM_LIBRARY_PATH`; no bundled or
project-maintained PDFium build is approved by this closeout.

## Non-Actions

- This closeout does not change public `0.3.0` install wording.
- This closeout does not create package tags.
- This closeout does not create release tags.
- This closeout does not approve DocuShell integration.
- This closeout does not approve hosted surfaces.
- This closeout does not approve production positioning.
- This closeout does not approve Windows packaged artifacts.
- This closeout does not approve bundled project-maintained PDFium builds.
- This closeout does not approve public benchmark reports.
- This closeout does not approve public benchmark claims.
- This closeout does not approve `ethos-doc`.
- This closeout does not approve `ethos-rag`.
- This closeout does not run `npm pkg fix`.
- This closeout does not alter the npm package contents after publication.

## Result

The exact approved npm publication for `@docushell/ethos-pdf@0.3.0` is complete and verified live
on the npm registry. The remaining public-release work is limited to later lanes for public
`0.3.0` install wording, package/release tags, DocuShell integration, and the explicitly retained
blocked surfaces above.
