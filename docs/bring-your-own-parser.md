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

## Geometry is required, and where that requirement lives

**For adapter authors: your source needs real coordinates.** `ethos.grounding.v1` requires
`bbox` on every element, span, table, and cell. A text-only parser cannot use this profile
honestly. Do not submit page-sized boxes, zero boxes, or invented coordinates — a zero-area
box is rejected outright, so a `[0,0,0,0]` sentinel will not get you through.

The Rust trait types carry `Option<[i64; 4]>`. That is deliberate and it is **not** an
invitation to send `None`: the wire schema still requires the field, and the reader will
reject an artifact without it. The `Option` exists so the type system can express a source
that has no geometry to declare, which is not a thing this profile accepts today.

**For maintainers: the constraint is narrower than it looks.** The verifier already binds
text evidence with no geometry at all. An evidence ref of `{element_id, expected_text}`
with no page locator and no bbox reaches `AnchorStatus::Bound` at `AnchorLevel::Text` and
pushes no capability limit. That behaviour is covered by tests in `ethos-verify` named
`geometry_free_*` and `absent_page_locator_resolves_to_not_checked_never_not_found` — do
not remove them, they are what keeps the path open.

Geometry is mandatory in the **artifact and its validator**, not in the verification
algorithm. Five gates enforce it, all in one layer:

| # | Gate | Where |
| --- | --- | --- |
| 1 | `media_type` is `const "application/pdf"` | `schemas/ethos-grounding-source.schema.json` |
| 2 | the same media-type check | `crates/ethos-core/src/grounding_json.rs` |
| 3 | `coordinate_system` pins `unit: centipoint`, `origin: top-left` | schema |
| 4 | `bbox` required on element, span, table, cell | schema |
| 5 | positive-area and in-page-bounds enforcement | `grounding_json.rs` |

Gate 5 is why any future change must make `bbox` *absent* rather than empty. It also means
an off-canvas PPTX shape, which legitimately carries negative coordinates, is rejected
today — arguably a security-report finding rather than a parse error, and that call is a
prerequisite to PPTX support rather than a detail.

**If format support is ever taken up**, the order is DOCX, then XLSX, then PPTX. That is
the reverse of the intuition that the format with visible geometry is the cheap one:

- **DOCX** exercises the geometry-absent path, which is the only genuinely new behaviour.
  Paragraph order in `word/document.xml` is document order — deterministic, no layout
  engine, no font metrics. Pagination does not exist in the file and must not be
  synthesised.
- **XLSX** reuses that path and adds an `R1C1` locator convention. `GroundingCell` already
  carries `row`, `col`, `row_span`, and `col_span`, so a sheet maps onto the existing table
  model with no new locator concept. Do not compute column geometry: the same nominal
  8.43-character column measures 4800 centipoints under Calibri 11 and 5400 under Verdana
  11, a 12.5% swing driven by system font metrics that ADR-0003's font policy does not
  cover.
- **PPTX** last, despite clean arithmetic (127 EMU = 1 centipoint, and 127 is odd so
  rounding ties are impossible), because gate 5 must be resolved first.

Full analysis, including the measurements above and why rendering to PDF fails both the
footprint and licence gates, is in `docs/v0-6-0-release.md` §10.1. Multi-format support is
out of scope for v0.6.0 — `docs/proof-statement-v1.md` §7 records the trigger for
revisiting it.
