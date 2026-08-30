# v0.6.0 Clean-Room Mapper Walkthrough

Status: **procedure validated** (2026-07-30). The independent-developer gate this record was
written against was **removed by decider decision on 2026-08-30**, so it is no longer outstanding
— it no longer exists. See release-prep §5.1.1. The honest limitation below is unchanged and is
the reason that removal is worth reading: this record does not establish discoverability, and
after the removal nothing else does either.

## What this records

An executable walkthrough of the documented Grounding JSON path, performed against a synthetic
third-party parser that shares no shape with any shipped fixture, using only
[`../writing-a-mapper.md`](../writing-a-mapper.md).

## Honest limitation — read this first

**This does not satisfy release-prep §5.1.** That gate requires a developer who did not implement
the feature to complete the path without undocumented intervention. This walkthrough was performed
by the same author as the guide, so it is contaminated by construction: it cannot detect knowledge
that is in the author's head rather than on the page.

What it does establish is weaker but not worthless — that the documented procedure is **complete
and executable end to end**, that it works against a parser shape it was not written for, and that
every step produces the outcome the guide predicts. The remaining gate is whether a stranger finds
it *discoverable*, and only a stranger can answer that.

## Inputs

A fictional `acme-pdf-extract` output chosen to be deliberately unlike the shipped OpenDataLoader
fixture:

- its own field names (`blocks`, `ref`, `pageNo`, `rect`, `content`) rather than the fixture's;
- bottom-left PDF-point coordinates as floats, including values requiring half-away-from-zero
  rounding (`709.28`, `680.125`);
- no page geometry, so dimensions had to be sourced separately per guide §3;
- no spans, character offsets, or tables.

## Result

All four steps of guide §8 passed, in order, with no undocumented intervention.

| Step | Expected | Observed |
| --- | --- | --- |
| 1. Determinism — run twice, `cmp` | byte-identical | byte-identical |
| 2. `grounding check --source-artifact` | exit 0, `valid`, `matched` | exit 0, `valid`, `matched`, counts `{pages:1, elements:2}` |
| 3. Real claim via `verify --fail-on-ungrounded` | exit 0, grounded | exit 0, `grounded`, `fingerprint_stale: false` |
| 4. Negative — one character changed | not a match | exit 1, `mismatch` |

Step 3 used the `representation_sha256` from the step 2 validation report as
`document_fingerprint`, per guide §7. Step 4 changed `$12.4 million` to `$12.5 million` and
correctly produced `mismatch` rather than a match, confirming the mapper is not grounding
everything.

Neither PDFium nor Rust was required at runtime. The walkthrough ran on `darwin:x64`, a host Ethos
does not ship binaries for, against a CLI built from source.

## What the guide got right

The three sections that carried the most weight were the ones added after the earlier walkthrough
found them missing:

- **§3, page geometry.** The synthetic parser emits no page dimensions, exactly like
  OpenDataLoader. Without the explicit instruction that geometry comes from the PDF and not the
  parser, this step has no obvious answer.
- **§4, coordinate conversion.** Both the origin flip (`y0 = H - top`) and half-away-from-zero
  rounding were needed. `680.125` centipoints is a genuine tie case.
- **§7, the two hashes.** Using `source.sha256` as `document_fingerprint` would have produced
  `stale` on a correct artifact. The guide's instruction to read `representation_sha256` from the
  validation report is what made step 3 pass.

## Gaps found

None in this run. The two gaps found by the previous walkthrough — undocumented mapper invocation
and the unexplained page-metadata sidecar — were already fixed and did not recur.

## Still required before release

A developer who did not build this feature must complete emit, check, and verify from the published
docs alone, unassisted, with every stall recorded. Per release-prep §5.1, any required private
knowledge blocks release.
