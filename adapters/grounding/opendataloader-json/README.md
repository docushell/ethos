# ethos-grounding-opendataloader-json

GroundingSource adapter over **OpenDataLoader PDF JSON output** — the proof that foreign
parser output can enter `ethos-verify` (PRD §1.5, §16). Status: **Milestone A stub** →
B alpha hardening (against pinned real ODL output, version from
`benchmarks/competitors.lock.json`) → D v1.

This is not an ODL fork: ODL output is consumed as data from a pinned upstream version
(plan §6.5).

## What the stub maps

Parser identity (`tool.name`/`tool.version` + adapter id/version), pages (number, width,
height → centipoints), elements (id, page, bbox, type, text). That is exactly the PRD §16
acceptance subset.

## Declared capabilities (honest downgrades)

`spans: false`, `char_offsets: false`, `fingerprint: false`, `crop_support: false`,
`coordinate_origin: unknown` (until the B-alpha pin verifies ODL's convention). Verification
over this source therefore carries explicit `capability_limited` warnings — never silent
approximation (PRD §5.5).

## Fixtures

`tests/fixtures/odl-sample.json` is synthetic and labeled as such. B-alpha replaces/extends
it with pinned real output. Every mapping change ships fixtures in the same PR.
