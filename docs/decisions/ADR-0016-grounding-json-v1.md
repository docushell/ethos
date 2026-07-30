# ADR-0016: Grounding JSON v1 and OpenDataLoader mapping boundary

Status / Date / Governs: Accepted / 2026-07-30 / WP-1 strict Grounding JSON loading and validation.

## Context

WP-0 verified that the DocuShell-vendored OpenDataLoader 2.5.0 JAR can provide a deterministic
source mapping for the accepted real PDF fixture. Its bounding boxes are PDF-point coordinates
with a bottom-left origin; page geometry is supplied by the source PDF metadata. The mapper can
therefore produce honest top-left centipoint geometry, but OpenDataLoader does not provide spans,
character offsets, or tables in this fixture.

## Decision

Ethos accepts exactly `artifact_type="ethos.grounding.v1"` and `schema_version="1.0.0"` for the
new language-neutral artifact. The accepted representation is hashed byte-for-byte as
`representation_sha256`; this is the GroundingSource fingerprint. The original PDF hash remains
the separate `source.sha256` binding and is not substituted by the representation hash.

The strict parser rejects duplicate keys before JSON value construction, unknown fields, nulls in
the typed shape, floats/exponents, invalid UTF-8/BOM, and invariant violations. It fails closed
with one bounded, stable error. WP-1 enforces these measured structural limits: 256 MiB input,
64 nesting levels, 5,000 pages, 1,000,000 elements or spans, 100,000 tables, 1,000,000 cells,
256-byte IDs, and 16,384-byte strings.

No new runtime dependency is introduced. OpenDataLoader remains an explicit mapper input and is
not bundled into Ethos.

### Frozen validation error vocabulary

These fifteen codes are the complete, frozen `error.code` vocabulary for
`ethos.grounding_validation.v1`. They appear in a schema-backed artifact and consumers may branch on
them, so they are part of the public compatibility surface. Codes may be added in a later schema
version; within `1.0.0` none may be renamed, removed, or repurposed.

| Code | Meaning |
| --- | --- |
| `invalid_json` | input is not valid UTF-8 or JSON, or uses an unsupported numeric form |
| `bom_not_allowed` | input begins with a UTF-8 BOM |
| `duplicate_key` | a JSON object repeated a key at any depth |
| `unknown_field` | an object contains a field outside the contract |
| `invalid_field` | a required field is absent or has the wrong shape |
| `unsupported_version` | artifact or schema identity is not the supported v1 identity |
| `invalid_capabilities` | a capability combination is contradictory |
| `duplicate_id` | a page, element, span, or table identifier was repeated |
| `unknown_reference` | a referenced page or element does not exist |
| `invalid_order` | an array ordering invariant failed |
| `invalid_bbox` | a bounding box is malformed or outside its page |
| `invalid_offsets` | character offsets do not match the owning text |
| `invalid_table` | a table or cell invariant failed |
| `invalid_invariant` | a reference, order, identifier, or geometry invariant failed |
| `limit_exceeded` | an accepted structural limit was exceeded |

Each failure returns exactly one code with one bounded JSON path and one bounded, Ethos-owned
message. Parser-library diagnostics, document text, local paths, and unbounded values are never
copied into a deterministic report.

### Representation identity versus source binding

`representation_sha256` is the `GroundingSource` fingerprint and is what the verification report
records as `document_fingerprint`. The verifier only ever observes the Grounding JSON, so the
fingerprint must describe the representation that was actually checked rather than a PDF the
verifier never saw.

The consequence is accepted deliberately: re-emitting the artifact changes the fingerprint, so
citations bound to a previous representation report `stale` even when the PDF is unchanged. The
alternative — using `source.sha256` — would let a silently re-mapped artifact with different
geometry present as fresh, which is the failure mode this project exists to prevent.

`source.sha256` remains the separate, optional binding to the original PDF, reported as
`matched`, `mismatched`, or `not_checked`. A match proves only that the mapper declared the hash of
the supplied PDF; it is never evidence of faithful extraction.

## Consequences

All parsers that participate in the future shared loader must map into this one strict artifact.
Missing capabilities remain false and cannot be inferred. CLI loading, source-PDF preflight, and
verification integration remain WP-2 work; this ADR does not authorize those surfaces.
