# Grounding adapters

Foreign-parser output enters `ethos-verify` exclusively through the `GroundingSource` trait
(`ethos-core`, feature `grounding`). Adapters consume **pinned upstream parser output as
data** — no forks are maintained (plan §6.5).

| Adapter | Status | Notes |
| --- | --- | --- |
| `opendataloader-json` | reference adapter | Strict documented-subset adapter over OpenDataLoader-style JSON |
| `liteparse-json` | candidate (post-B, PRD §2.1) | if useful |
| `docling-json` | candidate (post-B) | if useful |

Adapter rules: declare capabilities honestly (missing spans/fingerprints/origins become
explicit `capability_limited` downgrades — never silent approximation); deterministic
mapping (same input bytes, same output, same order); depend only on `ethos-core`'s
`grounding` feature, never on parser internals; ship fixtures with every mapping change
(request template: `.github/ISSUE_TEMPLATE/adapter_request.yml`).

For v0.2.0 preparation, OpenDataLoader remains the full reference adapter, not the minimum
onboarding example. It validates the documented subset strictly, downgrades unsupported
capabilities explicitly, bounds element/table/cell boxes to page dimensions, rejects negative
origins, and accepts exact page boundaries. New parser authors should start with
`docs/bring-your-own-parser.md`, then use this adapter as a fuller mapping reference.
