# Grounding adapters

Foreign-parser output enters `ethos-verify` exclusively through the `GroundingSource` trait
(`ethos-core`, feature `grounding`). Adapters consume **pinned upstream parser output as
data** — no forks are maintained (plan §6.5).

| Adapter | Status | Notes |
| --- | --- | --- |
| `opendataloader-json` | **A stub** → B alpha → D v1 | First adapter; documented assumed subset; B hardens against pinned real ODL output |
| `liteparse-json` | candidate (post-B, PRD §2.1) | if useful |
| `docling-json` | candidate (post-B) | if useful |

Adapter rules: declare capabilities honestly (missing spans/fingerprints/origins become
explicit `capability_limited` downgrades — never silent approximation); deterministic
mapping (same input bytes, same output, same order); depend only on `ethos-core`'s
`grounding` feature, never on parser internals; ship fixtures with every mapping change
(request template: `.github/ISSUE_TEMPLATE/adapter_request.yml`).
