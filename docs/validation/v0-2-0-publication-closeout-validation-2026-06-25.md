# v0.2.0 Publication Closeout Validation - 2026-06-25

Status: **v0.2.0 public beta/evaluation surfaces published and smoke-verified; npm 0.2.0 deprecated and corrected by npm 0.2.1**

This record closes the v0.2.0 publication lane for the bounded public beta/evaluation surfaces.
It does not approve hosted surfaces, production positioning, Windows packaged artifacts, bundled
project-maintained PDFium builds, public benchmark reports, public benchmark claims, speed,
footprint, parser-quality, table-quality, `ethos-doc`, or `ethos-rag`.

## Published Surfaces

- crates.io:
  - `ethos-doc-core = "0.2.0"`
  - `ethos-verify = "0.2.0"`
  - `ethos-pdf = "0.2.0"`
- PyPI:
  - `ethos-pdf==0.2.0`
- npm:
  - `@docushell/ethos-pdf@0.2.1` is the current package.
  - `@docushell/ethos-pdf@0.2.0` is deprecated because it shipped stale CLI binaries that
    reported `ethos 0.1.2`.
- GitHub Release:
  - `v0.2.0`
  - macOS arm64 and Linux x64 CLI artifacts, checksum sidecars, inventory sidecars, and smoke
    sidecars.

## Operator Evidence

`cargo search ethos-doc-core --limit 1`:

```text
ethos-doc-core = "0.2.0"    # Ethos canonical document model, IDs, errors, schema types, traits, c14n and fingerprints
```

`cargo search ethos-verify --limit 1`:

```text
ethos-verify = "0.2.0"    # Parser-agnostic citation evidence verification over GroundingSource (alpha lands Milestone B)
```

`cargo search ethos-pdf --limit 1`:

```text
ethos-pdf = "0.2.0"    # PDFium backend behind EthosPdfBackend — quantize-at-extraction lives here (WS-ENGINE, Milestone A)
```

`python3 -m pip index versions ethos-pdf`:

```text
ethos-pdf (0.2.0)
Available versions: 0.2.0, 0.1.2, 0.1.1, 0.1.0, 0.0.0.post0
LATEST:    0.2.0
```

PyPI clean venv smoke:

```text
Successfully installed ethos-pdf-0.2.0
0.2.0
```

`npm view @docushell/ethos-pdf dist-tags versions --json`:

```json
{
  "dist-tags": {
    "latest": "0.2.1"
  },
  "versions": [
    "0.0.0-reserved.0",
    "0.1.0",
    "0.1.1",
    "0.1.2",
    "0.2.0",
    "0.2.1"
  ]
}
```

`npm view @docushell/ethos-pdf@0.2.0 --json` contains:

```json
{
  "deprecated": "Do not use: published with stale CLI binary reporting ethos 0.1.2. Use a later 0.2.x patch release."
}
```

`npm view @docushell/ethos-pdf@0.2.1 version dist.shasum`:

```text
version = '0.2.1'
dist.shasum = '95a55f89347ed8159d08aa31d59bf81e08337793'
```

npm clean install smoke:

```text
added 1 package, and audited 2 packages in 493ms
found 0 vulnerabilities
ethos 0.2.0
```

`gh release view v0.2.0 --json tagName,isDraft,isPrerelease,url`:

```json
{
  "isDraft": false,
  "isPrerelease": false,
  "tagName": "v0.2.0",
  "url": "https://github.com/docushell/ethos/releases/tag/v0.2.0"
}
```

Downloaded GitHub Release CLI artifact digest verification:

```text
ethos-macos-arm64.tar.gz
 actual:    3c4fd236b1f76b87d0c765be5a35d9fd1476cac8475552a281f37df1d2fca06d
 checksum:  3c4fd236b1f76b87d0c765be5a35d9fd1476cac8475552a281f37df1d2fca06d
 inventory: 3c4fd236b1f76b87d0c765be5a35d9fd1476cac8475552a281f37df1d2fca06d
 ok: True
ethos-linux-x64.tar.gz
 actual:    0a1173471a9a4f1f8a2b9e60fa8192ab2af4796170b8f407883299dd85148ca7
 checksum:  0a1173471a9a4f1f8a2b9e60fa8192ab2af4796170b8f407883299dd85148ca7
 inventory: 0a1173471a9a4f1f8a2b9e60fa8192ab2af4796170b8f407883299dd85148ca7
 ok: True
```

Local macOS CLI artifact smoke:

```text
ethos 0.2.0
Deterministic PDF parsing, RAG artifacts, and citation evidence verification
```

GitHub Actions release workflow:

```text
Run release (28189912786) completed with 'success'
```

## Retained Blockers

- Windows packaged artifacts remain blocked.
- Bundled project-maintained PDFium builds remain blocked.
- Hosted surfaces remain blocked.
- Production positioning remains blocked.
- Public benchmark reports and public benchmark claims remain blocked.
- Speed, footprint, parser-quality, table-quality, and production claims remain blocked.
- `ethos-doc` and `ethos-rag` remain blocked as public package/product surfaces.
