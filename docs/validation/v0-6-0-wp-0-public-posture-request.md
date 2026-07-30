# v0.6.0 WP-0 Public-Posture Request

Status: **partially accepted; publication still gated** (updated 2026-07-30).

## Acceptance record

- **README.md restructure: accepted by the decider on 2026-07-30** and applied in commit `7f3d8ed`.
  The change reorganizes the existing supported-scope and limitation wording, retains public-beta
  positioning, and marks Grounding JSON explicitly as a proposal rather than a current feature.
- **`docs/public-boundary-claims.json`: not yet updated.** The registry remains the authoritative
  claim set and still pins the previous published version strings. Reconciling it with the
  published v0.5.0 baseline is tracked as a release blocker in
  [`../v0-6-0-release.md`](../v0-6-0-release.md) §8.
- **Publication and production positioning: still gated.** Nothing below is relaxed.

The original request follows, unchanged.

---

Status of the original request: **gated request; not approved for publication** (2026-07-30).

The requested coordinated posture change is to remove mandatory public-beta positioning while
retaining explicit supported-scope and limitation wording. It must be reviewed as one change across
`README.md`, `docs/public-boundary-claims.json`, and their enforcing tests.

This request does not approve Grounding JSON availability, npm SDK availability, production
positioning, automatic support for every parser, parser-quality claims, or any claim that evidence
matching proves truth. The current README and claims registry remain the authoritative public
surfaces until the claims approval lane accepts the coordinated patch.
