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

## Consequences

All parsers that participate in the future shared loader must map into this one strict artifact.
Missing capabilities remain false and cannot be inferred. CLI loading, source-PDF preflight, and
verification integration remain WP-2 work; this ADR does not authorize those surfaces.
