# ADR-0016: Grounding JSON v1 and OpenDataLoader mapping boundary

Status / Date / Governs: Accepted / 2026-07-30 / Grounding JSON v1 across WP-1 validation, WP-2
CLI dispatch and source binding, and the WP-3 npm surface. Includes the frozen error vocabulary,
representation-versus-source hash identity, and the accepted and rejected surface additions below.

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

### Accepted validator resource ceiling

Decided 2026-07-31, replacing release-prep §12's regression comparison against the v0.5.0
verification baseline. That comparison would measure an unchanged code path, because Grounding JSON
adds a parallel loader and no existing verification path changes.

The accepted ceiling, on the release profile:

- **40 µs per element** wall clock
- **2 KB per element** peak resident memory

Measured cost at the frozen 1,000,000-element limit is 26.5 µs and 1.29 KB per element, so the
ceiling carries roughly 1.5× headroom. Wall clock is enforced by
`validator_stays_within_the_accepted_resource_ceiling`, which is release-only and opt-in via
`ETHOS_CHECK_VALIDATOR_CEILING` because wall-clock assertions flake on shared runners. Peak memory
is recorded in `docs/validation/v0-6-0-validator-resource-baseline.md` and re-measured on any
change to the strict parser.

The frozen structural limits are unchanged. A schema-legal artifact at the element ceiling needs
roughly 1.5 GB resident, because the validator retains the parsed artifact rather than streaming
it. That working set is documented for integrators in `docs/writing-a-mapper.md` rather than
addressed by lowering a frozen limit. A validator memory guard using the existing
`MemoryLimitExceeded` exit is recorded as a v0.7.0 input, alongside streaming validation.

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

### Accepted surface beyond release-prep §7.2 and §8.2

Two additions are accepted deliberately. Everything else that appeared during implementation was
removed rather than kept.

**`--grounding ethos-json` on `verify` and `verify-batch`.** Routing `evidence anchor` through the
shared loader gave all three commands one dispatch point. The legacy `ethos-json` spelling is
therefore accepted everywhere rather than special-cased in one command. It is an alias for the
existing no-flag native behavior. Known wart: combining it with `--crop-dir` reports that crops are
native-only, which is confusing because the caller did ask for native; the crop guard is
intentionally left untouched.

**`verifyClaims({ citations })` in the npm SDK.** Release-prep §8.2 lists only `citationsPath`. In
JavaScript the citations are already in memory, so requiring a path pushes every caller to
reimplement the same temporary-file dance, usually without cleanup on throw. The SDK does it once:
`mkdtemp`, an 8 MiB bound, and removal in a `finally`. `citationsPath` and `citations` remain
mutually exclusive.

**Rejected: `--source-artifact` on `verify` and `verify-batch`** (and its `sourceArtifactPath`
passthrough in `verifyClaims`). Source binding belongs to `grounding check`, which records
`source_binding` in a schema-backed artifact. On `verify` the check ran and left no trace: the
report was byte-identical with and without the flag, and `verification_report.json` has no field
that could express it. An operator would reasonably read a passing run as PDF-bound while any
downstream recipient of that report could not distinguish it from an unbound one. Recording the
binding would require a verification-report change, which release-prep §5.3 excludes.

## Consequences

All parsers that participate in the future shared loader must map into this one strict artifact.
Missing capabilities remain false and cannot be inferred. CLI loading, source-PDF preflight, and
verification integration remain WP-2 work; this ADR does not authorize those surfaces.
