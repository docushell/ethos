# Third-Party Manifest Check - 2026-06-16

## Purpose

Record the first repeatable third-party license manifest generation path for the Cargo dependency
graph.

This is not a final release artifact license bundle. It covers Cargo registry dependencies in the
locked workspace graph only. Future binaries, wheels, npm packages, bundled PDFium libraries,
bundled fonts, and other packaged payloads still need artifact-specific license and NOTICE
assembly.

## Status

Status: **completed for the current Cargo source dependency graph**.

The repository now has a durable generator:

```sh
make third-party-license-manifest
```

The target writes a deterministic JSON manifest from `cargo metadata --locked --offline` and
`Cargo.lock` checksums. It intentionally omits local absolute paths from Cargo metadata.

## Verification Commands

```sh
make third-party-license-manifest \
  THIRD_PARTY_MANIFEST_OUT=target/release-third-party/cargo-third-party-licenses.json

python3 -c "import json; d=json.load(open('target/release-third-party/cargo-third-party-licenses.json')); print(d['summary'])"

rg -n "/Users|Desktop|/private|/tmp|\\.cargo|local-user|local-host" \
  target/release-third-party/cargo-third-party-licenses.json
```

## Result

The generated manifest reported:

```text
workspace_package_count: 7
third_party_package_count: 93
license_expressions:
- (MIT OR Apache-2.0) AND Unicode-3.0
- Apache-2.0 / MIT
- Apache-2.0 OR MIT
- Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT
- BSD-2-Clause OR Apache-2.0 OR MIT
- MIT
- MIT OR Apache-2.0
- MIT OR Apache-2.0 OR LGPL-2.1-or-later
- MIT/Apache-2.0
- Unlicense OR MIT
- Zlib
```

The local-path/private-term scan produced no matches.

## Remaining Release Work

- Generate artifact-specific license and NOTICE bundles when actual release artifacts exist.
- Include PDFium upstream license/notice material if any artifact bundles PDFium.
- Include font license/notice material if any artifact bundles fonts.
- Attach the generated manifest or a reviewed derivative to each future artifact release.
- Re-run `cargo-deny` and the manifest generator after dependency or feature changes.
