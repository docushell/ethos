# Release NOTICE Draft Check - 2026-06-16

## Purpose

Record the first artifact-specific license/NOTICE bundle scaffold for future release review.

This is not a release artifact and does not unblock GitHub Releases, binaries, wheels, npm
updates, crates.io publication, or public benchmark reports.

## Status

Status: **draft scaffold completed**.

The repository now has a durable draft target:

```sh
make release-notice-draft
```

The target generates a planning bundle under `target/release-notice-draft/`:

- `NOTICE.release.md`
- `THIRD-PARTY-CARGO-LICENSES.json`
- `release-notice-manifest.json`

The generated manifest is explicitly marked `draft_not_release_ready`.

## Scope

Checked source state:

- Repository: `docushell/ethos`
- HEAD: `5d8f33f4f2c8a96822fc6b7f9db8effdbbc57c9b`

The generated draft bundle covers:

- project `LICENSE` and `NOTICE` expectations;
- generated Cargo third-party dependency manifest;
- conditional PDFium notice obligation if PDFium is bundled;
- conditional Liberation font notice obligation if fonts are bundled;
- release blockers for binaries, wheels, npm packages, crate publication, and public benchmark
  reports.

## Verification Commands

```sh
make release-notice-draft

python3 -c "import json; d=json.load(open('target/release-notice-draft/release-notice-manifest.json')); print(d['status'])"

rg -n "/Users|Desktop|/private|/tmp|\\.cargo|local-user|local-host|saumil|diwaker|oracle" \
  target/release-notice-draft
```

## Result

The generated draft reported:

```text
status: draft_not_release_ready
artifact_name: ethos-cli-draft
workspace_package_count: 7
third_party_package_count: 93
conditional_external_materials: 2
blocked_release_artifact_types:
- github-release-binary
- wheel
- npm-package
- crate-publication
- public-benchmark-report
```

The local-path/private-term scan produced no matches.

## Remaining Release Work

- Replace the draft artifact identifier with a concrete artifact name and platform.
- Add artifact payload inventory and checksums.
- Include upstream PDFium license/notice material if PDFium is bundled.
- Include upstream font license/notice material if fonts are bundled.
- Attach the reviewed bundle to future artifacts.
- Keep release workflows blocked until package-specific readiness and claim gates pass.
