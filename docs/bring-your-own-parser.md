# Bring Your Own Parser

Status: v0.3 tutorial for parser authors. This document shows the supported trust-layer integration
shape for the published `0.3` Rust crates.

The integration model is:

```text
Your parser output -> GroundingSource -> ethos-verify -> report
```

Your parser keeps ownership of extraction. Ethos consumes deterministic source evidence through
`GroundingSource` and verifies whether requested citations or evidence refs bind to that source.
Ethos does not become your parser and does not judge full semantic truth.

## Dependencies

A minimal Rust verifier integration uses:

```toml
[dependencies]
ethos-doc-core = { version = "0.3", features = ["grounding"] }
ethos-verify = "0.3"
```

The package name and Rust import name intentionally differ:

```rust
use ethos_core::grounding::*;
```

If your crate imports verification schema types directly without depending on `ethos-verify`, also
enable the `verify-types` feature on `ethos-doc-core`.

## Tiny Source

This example exposes one page, one text element, and one fingerprint.

```rust
use ethos_core::grounding::{
    Capabilities, CoordinateOrigin, GroundingElement, GroundingSource, PageGeometry,
    ParserIdentity,
};
use ethos_core::verify_types::{
    CheckStatus, Citation, Claim, ClaimKind, VerificationConfig,
};
use ethos_verify::{verify_claims, CitationEnvelope, CitationInput};

#[derive(Clone)]
struct TinySource;

impl GroundingSource for TinySource {
    fn parser(&self) -> ParserIdentity {
        ParserIdentity {
            name: "tiny-parser".to_string(),
            version: "1.0.0".to_string(),
            adapter: None,
            adapter_version: None,
        }
    }

    fn capabilities(&self) -> Capabilities {
        Capabilities {
            spans: false,
            char_offsets: false,
            tables: false,
            fingerprint: true,
            coordinate_origin: CoordinateOrigin::TopLeft,
            crop_support: false,
        }
    }

    fn fingerprint(&self) -> Option<String> {
        Some("sha256:1111111111111111111111111111111111111111111111111111111111111111".to_string())
    }

    fn pages(&self) -> Vec<PageGeometry> {
        vec![PageGeometry {
            id: "p1".to_string(),
            index: 1,
            width: 61200,
            height: 79200,
            rotation: 0,
        }]
    }

    fn elements(&self) -> Vec<GroundingElement> {
        vec![GroundingElement {
            id: "e1".to_string(),
            page: "p1".to_string(),
            bbox: [7200, 10100, 54000, 11500],
            kind: "text_block".to_string(),
            text: Some("Revenue grew to $12.4M in Q3 2025.".to_string()),
        }]
    }
}

fn main() {
    let source = TinySource;
    let claim = Claim {
        kind: ClaimKind::Quote,
        text: Some("Revenue grew to $12.4M".to_string()),
        citation: Citation {
            element_id: Some("e1".to_string()),
            ..Citation::default()
        },
    };

    let citations = CitationInput::Envelope(CitationEnvelope {
        document_fingerprint: source.fingerprint(),
        claims: vec![claim.clone()],
    });
    let config = VerificationConfig::default_v1();
    let report = verify_claims(
        &source,
        citations,
        &config,
        "example-config-sha256".to_string(),
    );

    assert!(report.all_evidence_grounded);
    assert_eq!(report.checks[0].status, CheckStatus::Grounded);

    let stale_citations = CitationInput::Envelope(CitationEnvelope {
        document_fingerprint: Some(
            "sha256:2222222222222222222222222222222222222222222222222222222222222222"
                .to_string(),
        ),
        claims: vec![claim],
    });
    let stale_report = verify_claims(
        &source,
        stale_citations,
        &config,
        "example-config-sha256".to_string(),
    );

    assert!(stale_report.fingerprint_stale);
    assert_eq!(stale_report.checks[0].status, CheckStatus::Stale);
}
```

## Adapter Rules

Parser adapters should:

- return deterministic pages, elements, spans, and tables in stable order;
- assign stable, non-empty IDs that are unique within each page, element, table, and evidence-ref
  namespace; reject ambiguous duplicate IDs rather than relying on first-match behavior;
- use 1-based `PageGeometry.index` for parser-neutral page identity;
- convert point-space geometry to integer centipoints with
  `round_half_away_from_zero(points * 100)` and test the half-step cases `0.005 -> 1` and
  `-0.005 -> -1` against Ethos conformance behavior;
- declare missing features as capability limits instead of approximating silently;
- expose a fingerprint when the parser can bind evidence to exact source bytes;
- keep table-cell text projection distinct from Markdown table rendering;
- fail closed on malformed locators, negative coordinates, and out-of-page boxes.

The OpenDataLoader JSON adapter remains the full reference adapter. It is useful for serious
foreign-parser mapping, but the minimal integration surface is the `GroundingSource` trait above.

## Geometry, and which sources have to carry it

`ethos.grounding.v1` has two schema versions, and what an element must carry depends on the
version and the media type together. Both are enforced twice — the root `allOf` in
`schemas/ethos-grounding-source.schema.json` and the intake in
`crates/ethos-core/src/grounding_json.rs` — so an artifact that slips past one is stopped by the
other.

| Artifact | `media_type` | Element requires | Element forbids | `pages` / `spans` / `tables` |
| --- | --- | --- | --- | --- |
| `1.0.0` | `application/pdf`, and nothing else | `id`, `page`, `bbox`, `kind` | `locator` | pages populated as before |
| `1.1.0`, paginated | `application/pdf` | `id`, `page`, `bbox`, `kind` | `locator` | unchanged from `1.0.0` |
| `1.1.0`, page-less | one of the eight office types | `id`, `kind`, `locator` | `page`, `bbox` | all three must be empty |

The eight page-less media types are DOCX, XLSX, PPTX, ODT, ODS, ODP, RTF and EPUB, spelled in
full in `PAGE_LESS_MEDIA` in `grounding_json.rs`. A `1.0.0` artifact is byte-for-byte the shape
it always was; the version gate is what lets that stay true while `1.1.0` admits something else
entirely.

**For adapter authors of a paginated source: you still need real coordinates.** Do not submit
page-sized boxes, zero boxes, or invented coordinates — a zero-area box is rejected outright, so
a `[0,0,0,0]` sentinel will not get you through. Positive-area and in-page-bounds enforcement
lives in `grounding_json.rs`, and it means an off-canvas shape carrying legitimately negative
coordinates is rejected today. That is arguably a security-report finding rather than a parse
error, and it remains an open call for any future paginated format.

**For adapter authors of a page-less source: do not synthesise what you do not have.** State
`pages: []`, leave `spans` and `tables` empty, and give every element a non-empty `locator` of at
most 2048 bytes in your own address language — a paragraph index, a sheet cell, a slide and shape
id. The locator is opaque to verification, which resolves by element id; it exists so a citation
can be displayed and round-tripped in terms the source itself uses. Evidence binds at
`element_scoped` precision, which is what a page-less address can honestly claim, and page-scoped
is not available to you because there is no page to scope to.

The Rust trait types carry `Option<[i64; 4]>` for `bbox`. Since `1.1.0` that is no longer a
type-system courtesy with no wire counterpart: `None` arrives from the wire on every page-less
element, and every read of it fails closed.

**For maintainers: the verification algorithm never required geometry.** The verifier already
binds text evidence with none at all — an evidence ref of `{element_id, expected_text}` with no
page locator and no bbox reaches `AnchorStatus::Bound` at `AnchorLevel::Text` and pushes no
capability limit. That behaviour is covered by tests in `ethos-verify` named `geometry_free_*`
and `absent_page_locator_resolves_to_not_checked_never_not_found`. Do not remove them: they were
what kept this path open while the artifact still refused it, and they are now what keeps the
page-less lane honest.

Two things a page-less lane still cannot do, both worth knowing before building on it. A page
citation can never address such a source — it returns `page_not_found` — and an element id
supplied alongside a page returns `locator_conflict`. And `grounding check --source-artifact`
enforces PDF magic bytes unconditionally, so the one check that binds an artifact to the bytes it
names is unavailable for exactly the formats `1.1.0` exists to admit.
