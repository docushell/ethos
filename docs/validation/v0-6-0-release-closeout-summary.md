# Ethos v0.6.0 Release Closeout Summary

Status: closed on 2026-09-07.

## Source commits

Two commits, not one. The published CLI archives, the three crates, and the Python wheel were
built from `8adda91cd01baae487c9f2b18e4054b58a378a20`, to which the annotated `v0.6.0` tag
dereferences. The npm payload — both vendored binaries, `vendor/manifest.json`, `package.json`,
and both lockfile version fields — moved in `d2423bb189d153ccab037ce734c9b8c275586a4b` (#242),
two commits later, because a payload refresh can only record digests that already exist.

Recorded as two commits deliberately. The v0.5.0 record bound core-A and npm-B separately for the
same reason, and binding every surface here to a single commit would state a provenance fact that
is false for the npm tarball.

## GitHub Release

[v0.6.0](https://github.com/docushell/ethos/releases/tag/v0.6.0) is live, non-draft,
non-prerelease, and marked latest. It carries 16 assets: the macOS arm64 and Linux x64
caller-PDFium CLI archives and the optional `ethos-full` archives, each with checksum, inventory,
and target-smoke sidecars. No Windows artifact was published; the run produced a verify-only
Windows candidate, which was deliberately withheld because Windows packaged artifacts remain a
blocked lane.

Published archive SHA-256 values:

- `ethos-macos-arm64.tar.gz`: `c116b3449a3de1f4bddc6217e7717a1307a6ef58c240e5404be0850af81789bb`;
- `ethos-linux-x64.tar.gz`: `c12772255ba8a85b020bd9b6bb8bf77d01eaf11a6928a0d7348536eff7c378f2`;
- `ethos-full-0.6.0-macos-arm64.tar.gz`: `a0fe3df1b572f47c42b8fc4d456d6ce0983277191a8324b889747407bddd2625`;
- `ethos-full-0.6.0-linux-x64.tar.gz`: `d8cf121f111ff6ecb73670c79db4fc1c81e05d02b8cd5d8367104f5cbf3b38ac`.

Each was recomputed from the downloaded archive and matched its published `.sha256` sidecar. That
check verifies transport rather than provenance, because the sidecar is generated in the same
workflow step as the archive; provenance rests on the source commit and release run 33325655578
recorded in [`v0-6-0-release-promotion.md`](v0-6-0-release-promotion.md).

**The eight published `*.inventory.json` sidecars still read `draft_not_release_ready` and
`publication: blocked`.** `write_release_artifact_inventory.py` hard-codes both and cannot describe
an approved artifact. They record how each archive was produced, not its publication state. Read
this record for publication state, not the sidecars.

## Registries

The Rust crates `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` are live on crates.io at
`0.6.0`, none yanked. The Python `ethos-pdf` wheel is live on PyPI at `0.6.0`, its wheel and sdist
byte-identical to the locally built artifacts. `@docushell/ethos-pdf@0.6.0` is live on npm; the
published tarball was downloaded and its vendored binaries verified byte-identical to the release
archives, with the darwin binary executed and confirmed to report `ethos 0.6.0`.

## Package tags

The `ethos-package-*-0.6.0` tags are recorded in `docs/release-state.json`.

**A prior claim is corrected here rather than repeated.** The ledger declared
`ethos-package-*-0.4.0` and `ethos-package-*-0.5.0` closed out against the v0.5.0 closeout record,
which does not mention package tags at all. Those six tags do not exist, locally or on the remote:
only the `0.1.0`, `0.1.2`, and `0.3.0` triples were ever created. `check_release_state.py`
string-matches the declared names against `release.rust_crates` and never consults git, which is
how the gap survived two releases.

## Public wording

The exact wording packet approved on 2026-07-31 in
[`v0-6-0-public-wording-request.md`](v0-6-0-public-wording-request.md) is applied at this
publication, which is the only point at which it was authorised to land. The mechanical hold that
approval names — `test_v0_6_0_version_activation.py` — is retired here, its durable lockstep and
npm-payload assertions preserved in a version-neutral module that reads the target version from
the ledger rather than from a hard-coded constant.

The approval's limits are unchanged and none is widened: no production positioning, no hosted
surfaces, no Windows artifacts, no benchmark claims, no OCR, no parser-quality claim, and no claim
that a source-hash match proves faithful extraction.

## Gates

Release-prep, deterministic-build, target-smoke, claims, licence, package, and release-state gates
passed before publication. `release-live-state-check` compares this ledger against the live GitHub
Release rather than against itself.

**Consumer acceptance is bound to the 0.5.0 CLI, not 0.6.0.**
[`v0-6-0-docushell-acceptance.md`](v0-6-0-docushell-acceptance.md) records DocuShell pinned to
`ethos 0.5.0` with the v0.5.0 archive and binary digests. It evidences that a real consumer reaches
the verifier through public surfaces only; it does not evidence a consumer exercising the 0.6.0
bytes. Stated rather than inherited from the v0.5.0 record's wording.

**Release-prep §5.1, the clean-room developer criterion, was removed by decider decision on
2026-08-30** rather than satisfied. The capability claim — any parser reaching the verifier through
one mapper, with no Rust and no PDFium — stays evidenced by the JavaScript, Python, and DocuShell
mappers. Discoverability, which §5.1 protected, is evidenced by nothing and is not claimed.

## Boundary

The release retains the caller-provided PDFium boundary for base archives. Public benchmark, speed,
footprint, parser-quality, table-quality, hosted, production, and Windows packaged claims remain
outside the approved release boundary, as do `ethos-doc` and `ethos-rag`.

## Source binding

Recorded against Ethos `8adda91cd01baae487c9f2b18e4054b58a378a20` and
`d2423bb189d153ccab037ce734c9b8c275586a4b`.
