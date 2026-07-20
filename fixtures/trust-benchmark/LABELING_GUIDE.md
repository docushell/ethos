# Trust corpus labeling guide

This guide defines the labels in `v1/manifest.json`. The corpus is Ethos-authored synthetic
evidence for verifier regression and judge comparison; it is not a neutral benchmark suite.

Each check receives exactly one label based only on the cited document bytes and locator:

- `grounded`: the literal quote/value or presence claim is available at the locator.
- `fabricated-quote`: the claimed quotation does not appear at the locator or elsewhere.
- `wrong-page`: the text exists, but not on the cited page.
- `paraphrase-drift`: the claim is semantically related but is not a literal quotation/value.
- `split-quote`: the exact quotation crosses two geometrically adjacent text elements on one page.
- `stale-fingerprint`: the citation envelope fingerprint differs from the grounding document.
- `capability-limited`: the text grounds, but requested crop evidence is unavailable; the report
  must declare `missing_crop_support` and `capability_limited` instead of silently passing the
  requested evidence tier.

The generator assigns expected verifier status and reason mechanically. The first review executes
all 200 labels against Ethos and compares their status/reason to the manifest. Because the initial
labels are AI-generated, the second review is a human spot-check of the deterministic, category-
balanced 40-check sample in `review-record.json` (20% of 200). The human pass is complete only
when all 40 decisions are recorded, reviewer and date are filled, and any correction is applied to
the manifest generator before regeneration.
