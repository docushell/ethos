# v0.6.0 Release Promotion Record

Status: **operator named; artifact bindings outstanding** (2026-08-30).

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

The runbook requires six bindings. Four can be recorded now. Two cannot exist until a green
release run produces real artifacts, and are deliberately left blank rather than estimated.

| Binding | Value |
| --- | --- |
| Exact source commit | pending — the commit of the green `release.yml` run |
| Artifact names and platform targets | pending — `ethos-macos-arm64.tar.gz`, `ethos-linux-x64.tar.gz` and their sidecars, on a run that has not yet succeeded |
| SHA256 checksums | pending — from that run's `.sha256` sidecars, never from a local build |
| License/NOTICE bundle | `LICENSE` and `NOTICE`, copied into each archive by `release.yml` |
| PDFium posture | caller-provided via `ETHOS_PDFIUM_LIBRARY_PATH`, per ADR-0013. No bundled PDFium in the base archives |
| Exact public wording | approved in [`v0-6-0-public-wording-request.md`](v0-6-0-public-wording-request.md), applied at publication only |

**The three pending rows are the gate.** `release.yml` has never completed a run. Filling them
from anything other than that run — a local build, a previous release, an estimate — would
manufacture the evidence this record exists to bind, so they stay blank until the run is green.

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
