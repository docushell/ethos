# Bring Your Own Parser

Status: v0.2.0 release-candidate tutorial for parser authors. This document shows the intended trust-layer
integration shape before any `0.2.0` publication claim is made.

The integration model is:

```text
Your parser output -> GroundingSource -> ethos-verify -> report
```

Your parser keeps ownership of extraction. Ethos consumes deterministic source evidence through
`GroundingSource` and verifies whether requested citations or evidence refs bind to that source.
Ethos does not become your parser and does not judge full semantic truth.

## Dependencies

Once the `0.2.0` registry lane is approved and published, a minimal Rust verifier integration uses:

```toml
[dependencies]
ethos-doc-core = { version = "0.2", features = ["grounding"] }
ethos-verify = "0.2"
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
- use 1-based `PageGeometry.index` for parser-neutral page identity;
- declare missing features as capability limits instead of approximating silently;
- expose a fingerprint when the parser can bind evidence to exact source bytes;
- keep table-cell text projection distinct from Markdown table rendering;
- fail closed on malformed locators, negative coordinates, and out-of-page boxes.

The OpenDataLoader JSON adapter remains the full reference adapter. It is useful for serious
foreign-parser mapping, but the minimal integration surface is the `GroundingSource` trait above.
