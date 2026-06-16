# ethos-grounding-opendataloader-json

GroundingSource adapter over **OpenDataLoader PDF JSON output** — the proof that foreign
parser output can enter `ethos-verify` (PRD §1.5, §16). Status: **B alpha** with the
documented synthetic subset plus pinned real OpenDataLoader 2.4.7 output; D hardens this
adapter toward v1.

This is not an ODL fork: ODL output is consumed as data from a pinned upstream version
(plan §6.5).

## What the adapter maps

For the documented synthetic subset, it maps parser identity (`tool.name`/`tool.version` +
adapter id/version), pages (number, width, height → centipoints), elements (id, page, bbox,
type, text), and optional tables/cells (id, page, bbox, row/col, spans, bbox, text).

For real OpenDataLoader 2.4.x JSON, it maps the top-level `kids` tree into grounding
elements (`id` → `odl-{id}` for numeric and non-empty string ids, missing ids →
`odl-el-N`, `page number` → `page-N`, `bounding box` → centipoints, `content` or
unambiguous `text` → text). Nested `kids`/`children`, `list items`/`list_items`, and
`rows[].cells` containers are traversed in document order. Pure structural wrappers that
only carry child containers are traversed without becoming grounding elements. Child
containers must use array shapes, and malformed child containers, non-string text values,
or conflicting `content`/`text` values are rejected instead of being silently skipped. Real
ODL JSON does not include parser version or page dimensions, so the adapter reports parser
version as `unknown` and derives page extents from observed bounding boxes. Coordinate
origin remains unknown. Real ODL-style table nodes with explicit `page number`, `bounding
box`, and `rows[].cells[]` cell page/bbox/text fields are mapped to deterministic grounding
tables; row and column addresses are derived from row/cell order.

## Declared capabilities (honest downgrades)

`spans: false`, `char_offsets: false`, `fingerprint: false`, `crop_support: false`,
`coordinate_origin: unknown` (until the B-alpha pin verifies ODL's convention). Verification
over this source therefore carries explicit `capability_limited` warnings — never silent
approximation (PRD §5.5).

## Fixtures

`tests/fixtures/odl-sample.json` is synthetic and labeled as such.
`fixtures/foreign/opendataloader/real/` pins real OpenDataLoader 2.4.7 output with source
PDF, citations, expected verification report, and manifest provenance. Every mapping change
ships fixtures and CLI verification coverage in the same PR.
