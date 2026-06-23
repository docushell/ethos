# First Public Release Linux x64 Publication Closeout Validation - 2026-06-23

- Validated source HEAD before this record: `415a654`

Linux-publication closeout source commit: `415a654e07ab2fc653d8361b104b4e40613df948`

Linux-publication closeout source tree: `aa5fbd86c0747a036ab3040d1cf127b2f97bf1bb`

Status: **Linux x64 artifact evaluation assets published to GitHub Release v0.1.0**

This record closes the bounded Linux x64 CLI artifact publication lane for the first public
evaluation release. It does not approve npm publication, Windows packaged artifacts, hosted
surfaces, production positioning, bundled project-maintained PDFium builds, `ethos-doc`,
`ethos-rag`, public benchmark reports, or public benchmark claims.

## Publication Command

The operator uploaded the approved Linux x64 assets with:

```sh
GH_PROMPT_DISABLED=1 gh release upload v0.1.0 \
  /tmp/ethos-release-run-28004938177/ethos-linux-x64.tar.gz \
  /tmp/ethos-release-run-28004938177/ethos-linux-x64.tar.gz.sha256 \
  /tmp/ethos-release-run-28004938177/ethos-linux-x64.inventory.json \
  /tmp/ethos-release-run-28004938177/ethos-linux-x64.smoke.json
```

Result:

```text
Successfully uploaded 4 assets to v0.1.0
```

## Published Release Verification

Verification command:

```sh
GH_PROMPT_DISABLED=1 gh release view v0.1.0 --json tagName,url,assets \
  --jq '{tagName, url, assets: [.assets[].name]}'
```

Result:

```json
{
  "assets": [
    "ethos-linux-x64.inventory.json",
    "ethos-linux-x64.smoke.json",
    "ethos-linux-x64.tar.gz",
    "ethos-linux-x64.tar.gz.sha256",
    "ethos-macos-arm64.inventory.json",
    "ethos-macos-arm64.tar.gz",
    "ethos-macos-arm64.tar.gz.sha256"
  ],
  "tagName": "v0.1.0",
  "url": "https://github.com/docushell/ethos/releases/tag/v0.1.0"
}
```

## Published Linux x64 Asset Set

- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`

Approved Linux x64 SHA256:

```text
59dc8e4efe4888afe80d18488fd83b08293ea30550ab38961e601f8f18a098b2
```

Approved release URL:

```text
https://github.com/docushell/ethos/releases/tag/v0.1.0
```

## Final Bounded Public Evaluation State

The first public evaluation release now includes:

- GitHub source repository public beta evaluation;
- Rust library crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` at `0.1.0`;
- Python `ethos-pdf` wheel at `0.1.0`;
- macOS arm64 CLI artifact evaluation;
- Linux x64 CLI artifact evaluation;
- caller-provided PDFium through `ETHOS_PDFIUM_LIBRARY_PATH`.

## Retained Blockers

- npm publication remains blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports remain blocked.
- Public benchmark claims remain blocked.
- Windows x64 packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- `ethos-doc` remains blocked.
- `ethos-rag` remains blocked.

## Result

The bounded first public evaluation release is complete for the approved source, Rust crate,
Python wheel, macOS arm64 CLI artifact, and Linux x64 CLI artifact surfaces. All retained blockers
remain in force.
