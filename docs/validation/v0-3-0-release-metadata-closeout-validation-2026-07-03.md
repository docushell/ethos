# v0.3.0 Release Metadata Closeout Validation - 2026-07-03

Validated source HEAD before this record: `37c9ecd`.

v0.3.0 release metadata closeout source commit:
`37c9ecde01ec51fb425c6834a8526b45f9376655`.

v0.3.0 release metadata closeout source tree:
`c3d0da06122fcedf8c4279cbd44a668cbfe02720`.

Status: **v0.3.0 final GitHub Release metadata and latest pointer closed out**

This record corrects the GitHub Release metadata left behind by the staged v0.3.0 publication
sequence. The release was initially created with `--latest=false` while npm publication, public
install wording, and package tags were still blocked. Those lanes later closed, but no operator
step promoted v0.3.0 or replaced its historical pre-closeout release body. The correction marks
v0.3.0 as the repository's latest release and makes `docs/releases/v0.3.0.md` the canonical final
release body.

## Corrected Live State

- Repository: `docushell/ethos`
- Release tag: `v0.3.0`
- Release name: `Release v0.3.0`
- Release database id: `347912285`
- Release draft status: `false`
- Release prerelease status: `false`
- Latest release API tag: `v0.3.0`
- Canonical release notes: `docs/releases/v0.3.0.md`
- Published asset count: `8`

The live release body exactly matches the canonical release-notes file. The live asset names remain:

- `ethos-macos-arm64.tar.gz`
- `ethos-macos-arm64.tar.gz.sha256`
- `ethos-macos-arm64.inventory.json`
- `ethos-macos-arm64.smoke.json`
- `ethos-linux-x64.tar.gz`
- `ethos-linux-x64.tar.gz.sha256`
- `ethos-linux-x64.inventory.json`
- `ethos-linux-x64.smoke.json`

## Inventory Provenance Decision

The published `*.inventory.json` assets are not replaced. They preserve the exact pre-publication CI
provenance that the artifact approval decision bound by name and digest. Their
`draft_not_release_ready` and `publication: blocked` fields describe the workflow state in which the
archive bytes were produced; they are not the current GitHub Release state. The canonical release
notes now explain that distinction. Replacing those sidecars would break the recorded artifact
digests and erase the approved provenance chain.

Future release workflows must keep draft provenance separate from final live-release metadata. The
current release intent is now represented in `docs/release-state.json`, and the live checker verifies
the latest pointer, release name, draft/prerelease status, exact body, and exact asset set.

## Commands

```sh
gh release edit v0.3.0 --repo docushell/ethos \
  --notes-file docs/releases/v0.3.0.md \
  --latest
python3 .github/scripts/check_github_release_metadata.py --repo docushell/ethos
python3 .github/scripts/test_github_release_metadata.py
python3 .github/scripts/test_v0_3_0_release_metadata_closeout.py
python3 .github/scripts/check_release_state.py --check
git diff --check
```

## Retained Boundaries

This correction does not create, move, delete, or replace tags or release assets. It does not
approve additional release targets, DocuShell integration, hosted surfaces, production positioning,
Windows packaged artifacts, bundled project-maintained PDFium builds, public benchmark reports or
claims, speed, footprint, parser-quality, table-quality, `ethos-doc`, or `ethos-rag`.

## Result

GitHub Release `v0.3.0` is the repository's latest release, its final body matches the repository's
canonical v0.3.0 notes, and the original approved release assets remain unchanged.
