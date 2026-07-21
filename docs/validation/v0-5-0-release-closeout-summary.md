# Ethos v0.5.0 Release Closeout Summary

Status: closed on 2026-07-21.

Validated source HEAD before this record: `bfb71970b65826c1826097d0a7bccd6bf2059e2d`.
Core-A evidence was bound to commit `77a62e3d18fdf1a6791c79e48892ab5671d13c8d`; npm B was
prepared from that frozen core and committed in core-B HEAD above. Both commits carry DCO
sign-offs.

GitHub Release [v0.5.0](https://github.com/docushell/ethos/releases/tag/v0.5.0) is live,
non-draft, and non-prerelease. Its annotated tag dereferences to core-B HEAD. It contains the
macOS arm64 and Linux x64 caller-PDFium CLI archives and the optional `ethos-full` archives,
with checksum, inventory, and target-smoke sidecars. No Windows artifact was published.

Published archive SHA-256 values:

- `ethos-macos-arm64.tar.gz`: `30fa34afda745d168e1af39a134e2281f4a409d425765f3dc85c2e312fcbbcc2`;
- `ethos-linux-x64.tar.gz`: `592b175c00d147625f2f2ccc8bc5c74fb8a00ee37f178c363757f2c72404876e`;
- `ethos-full-0.5.0-macos-arm64.tar.gz`: `3ac08c2c32a1d08e4481cdeeb2b7a8b5780e9b0c09ebc40da9cbd59d4c2a4795`;
- `ethos-full-0.5.0-linux-x64.tar.gz`: `8608c3e5c7a51bed45d6ead7a717d59e226f27839ad8aab2fde384a46db425b1`.

The Rust crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are live on crates.io at
`0.5.0`; the Python `ethos-pdf` wheel is live on PyPI at `0.5.0`; and
`@docushell/ethos-pdf@0.5.0` is live on npm. Release-prep, deterministic-build, target-smoke,
performance, claims, licence, package, and consumer validation gates passed before publication.

The release retains the caller-provided PDFium boundary for base archives. Public benchmark,
speed, footprint, parser-quality, table-quality, hosted, production, and Windows packaged
claims remain outside the approved release boundary.
