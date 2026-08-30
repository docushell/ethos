# v0.6.0 Release Promotion Record

Status: **operator named; artifact bindings recorded** (2026-08-30).

Discharges the promotion gate in
[`RELEASE_OPERATOR_RUNBOOK.md`](../RELEASE_OPERATOR_RUNBOOK.md) §"Promotion Gate". Until this
record exists and its bindings are filled, the runbook holds that everything `release.yml`
produces is draft evidence, because repository write access alone is not release authority.

## Operator

Release operator for v0.6.0: **docushell-dev <hello@docushell.com>**.

Authority: decider of record on every v0.6.0 approval in `docs/validation/`, and sole committer
on the release lane. Named on 2026-08-30.

This names the operator only. It does not widen any approved boundary, and it does not authorize
hosted surfaces, Windows packaged artifacts, bundled project-maintained PDFium builds, public
benchmark reports, `ethos-doc`, or `ethos-rag`, all of which remain in `blocked_lanes`.

## Promotion bindings

All six bindings the runbook requires, recorded from release run
[33325655578](https://github.com/docushell/ethos/actions/runs/33325655578) on tag `v0.6.0` —
the first green run of `release.yml` in the project's history.

| Binding | Value |
| --- | --- |
| Exact source commit | `8adda91cd01baae487c9f2b18e4054b58a378a20` (`main`, merge of #239) |
| Artifact names and platform targets | `ethos-macos-arm64.tar.gz` (macOS arm64), `ethos-linux-x64.tar.gz` (Linux x64), plus `ethos-full-0.6.0-*` for both |
| License/NOTICE bundle | `LICENSE` and `NOTICE`, present in each archive; smoke evidence records `required_files` as `ethos`, `LICENSE`, `NOTICE`, `pdfium-manual-setup.md` |
| PDFium posture | caller-provided via `ETHOS_PDFIUM_LIBRARY_PATH`, per ADR-0013. `doc parse` exits `12` with the caller-provided guidance when unset; no bundled PDFium in the base archives |
| Exact public wording | approved in [`v0-6-0-public-wording-request.md`](v0-6-0-public-wording-request.md), applied at publication only |

### SHA256 checksums

```text
c12772255ba8a85b020bd9b6bb8bf77d01eaf11a6928a0d7348536eff7c378f2  ethos-linux-x64.tar.gz
c116b3449a3de1f4bddc6217e7717a1307a6ef58c240e5404be0850af81789bb  ethos-macos-arm64.tar.gz
d8cf121f111ff6ecb73670c79db4fc1c81e05d02b8cd5d8367104f5cbf3b38ac  ethos-full-0.6.0-linux-x64.tar.gz
a0fe3df1b572f47c42b8fc4d456d6ce0983277191a8324b889747407bddd2625  ethos-full-0.6.0-macos-arm64.tar.gz
```

Each value was recomputed from the downloaded archive and compared against the `.sha256` sidecar
the run published. That is a weaker check than it looks — the sidecar is generated in the same
workflow step as the archive — so it verifies transport, not provenance. What binds provenance is
the source commit above and the run that produced them.

The binaries report `ethos 0.6.0`, confirmed both from the run's smoke evidence
(`version_stdout`) and by extracting the macOS archive and executing `ethos --version`.

### Windows is not part of this promotion

The same run produced `ethos-windows-x64.zip`
(`db9559dfe0c7a0e9866081af1d6ec110868bb74b3e077eb20ac4b3e4baed4216`) from the verify-only
candidate lane. Windows packaged artifacts remain in `blocked_lanes` in
[`../release-state.json`](../release-state.json) and are **not** authorized by this record. The
archive is draft evidence for that lane only.

### The inventories still say blocked

Every `*.inventory.json` in the run carries `"status": "draft_not_release_ready"` and
`"publication": "blocked"`, because `write_release_artifact_inventory.py` hard-codes both. That is
a known limitation of the inventory writer, not a statement about this record: the sidecars cannot
currently describe an approved artifact. Read this record, not the inventory, for promotion state.

## Consumer acceptance

Release-prep §9.4 is discharged by
[`v0-6-0-docushell-acceptance.md`](v0-6-0-docushell-acceptance.md), bound to DocuShell
`docushell@cc652ec`, reviewed and fast-forward merged so the reviewed SHA and the SHA on
`main` are identical.

## Clean-room criterion

Release-prep §5.1 required a developer who did not implement the feature to complete emit, check,
and verify using only the published documentation. **That criterion was removed by decider
decision on 2026-08-30** (release-prep §5.1.1). It is recorded here so this record does not read
as having satisfied it.

The capability claim — that any parser can reach the verifier through one mapper, with no Rust and
no PDFium — is evidenced by the JavaScript, Python, and DocuShell mappers. Discoverability, which
is what §5.1 protected, is not evidenced by anything and is not claimed.

## Resource ceiling

Release-prep §12's resource evidence is met by
[`v0-6-0-validator-resource-baseline.md`](v0-6-0-validator-resource-baseline.md), whose
peak-RSS ceiling was revised from 2 KB to 3 KB per element on 2026-08-30 by decider decision,
recorded there as a deliberate revision with the shape B measurements behind it.

## What this record does not do

- It does not mark v0.6.0 published. `docs/release-state.json` continues to report 0.5.0 as the
  published baseline, and every install surface continues to name 0.5.0, until the packages are
  actually live.
- It does not approve production positioning. The README states what Ethos is and where it ships,
  with no lifecycle claim in either direction.
- It does not authorize publication on its own. The three pending bindings above must be filled
  from a green release run first.

## Source binding

Recorded against Ethos `9e5ffd9119eea196b48fb271dd30e72068997cb4`.
