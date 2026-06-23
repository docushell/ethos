# First Public Release macOS Artifact Publication Reconciliation Validation - 2026-06-23

- Validated source HEAD before this record: `62f9152`

Reconciliation source commit: `62f91521a1bcb87e4bb4be92d9188fc1c27e92c6`

Reconciliation source tree: `5d0cc9f2046edd9dd05242c218497e727c96eee9`

Status: **publication checksum discrepancy recorded; Linux x64 remains blocked**

This record reconciles the first public release handoff against the checked-in macOS arm64 artifact
evidence before any Linux x64 artifact publication work proceeds. It does not approve Linux x64
publication, npm publication, hosted surfaces, production positioning, public benchmark reports,
public benchmark claims, Windows packaged artifacts, bundled project-maintained PDFium builds,
`ethos-doc`, or `ethos-rag`.

## Checked-In Evidence State

The checked-in artifact evidence and final decider records name the local draft macOS arm64
artifact checksum:

```text
35c7cc19ea51231edb1a0cfb6d160d3a2e620ba9357d116ef071f66ebc5e236f
```

That checksum remains historical evidence for the local draft artifact captured in:

- `docs/validation/first-public-release-artifact-evidence-validation-2026-06-23.md`
- `docs/validation/first-public-release-final-decider-validation-2026-06-23.md`

## Handoff Publication State

The release handoff records the final published GitHub Release macOS arm64 artifact checksum as:

```text
9cb66dac20f93c55f574357dd0494e0cad711e1e5969cdfb29ae4c64ddf7c95d
```

The handoff also records that the published GitHub Release is:

```text
https://github.com/docushell/ethos/releases/tag/v0.1.0
```

## Reconciliation Boundary

The two checksums must be treated as different artifact states:

- `35c7cc19...` is the checked-in local draft artifact evidence.
- `9cb66dac...` is the handoff-reported final published artifact checksum.

The local environment attempted read-only public verification against the GitHub release before this
record, but unauthenticated GitHub API access was rate-limited and direct asset downloads did not
progress in the available network path. Because independent download verification was unavailable
in this environment, this record does not replace the historical checked-in draft checksum. It
records the discrepancy and requires operator verification against the GitHub Release asset before
the Linux x64 artifact is attached to `v0.1.0`.

## Required Operator Check Before Linux Publication

Before publishing Linux x64 artifacts to the existing `v0.1.0` GitHub Release, the operator must
verify that the current published macOS arm64 release assets are internally consistent:

```sh
sha256sum ethos-macos-arm64.tar.gz
cat ethos-macos-arm64.tar.gz.sha256
cat ethos-macos-arm64.inventory.json
```

Required result:

- the recomputed archive SHA256 matches the `.sha256` sidecar;
- the inventory `sha256` matches the recomputed archive SHA256;
- the verified published macOS SHA256 is recorded in the Linux x64 artifact evidence record;
- if the verified published SHA256 is not
  `9cb66dac20f93c55f574357dd0494e0cad711e1e5969cdfb29ae4c64ddf7c95d`, publication stops until a
  new reconciliation and decider record pass.

## Retained Blockers

- Linux x64 CLI artifact publication remains blocked until Linux artifact evidence is recorded and
  the macOS publication checksum is operator-verified.
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

The release may continue toward Linux x64 evidence capture, but the Linux x64 artifact must not be
attached to the existing `v0.1.0` GitHub Release until the published macOS arm64 checksum sidecars
are operator-verified and cited in the Linux evidence record.
