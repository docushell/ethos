# Writing a Grounding JSON Mapper

Status: guide for parser authors and integrators. Applies to `ethos.grounding.v1`.

This is the language-neutral path. If you are integrating from Rust and want to implement the
`GroundingSource` trait directly, see [`bring-your-own-parser.md`](bring-your-own-parser.md)
instead.

You do not need Rust, PDFium, a running service, an Ethos account, or a network connection after
install. You need one program that reads your parser's output and writes one JSON file.

```text
your parser  ->  your mapper  ->  ethos.grounding.v1 JSON  ->  ethos verify  ->  report
```

---

## 1. What a mapper owns

Ethos deliberately does **not** infer any of this. Only you know it.

1. **Stable IDs and reading order.** Array order is semantically significant.
2. **Coordinate conversion.** Into top-left centipoints, as integers.
3. **Honest capability declarations.** What your parser actually supports.

Everything else — matching, capability downgrades, staleness, warnings, the report — is owned by
the existing verifier and does not change.

---

## 2. The smallest complete artifact

```json
{
  "artifact_type": "ethos.grounding.v1",
  "schema_version": "1.0.0",
  "source": {
    "media_type": "application/pdf",
    "sha256": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  },
  "producer": { "name": "my-parser", "version": "1.2.3" },
  "capabilities": { "spans": false, "char_offsets": false, "tables": false },
  "coordinate_system": { "unit": "centipoint", "origin": "top-left" },
  "pages": [
    { "id": "page-1", "index": 1, "width": 61200, "height": 79200, "rotation": 0 }
  ],
  "elements": [
    {
      "id": "block-17",
      "page": "page-1",
      "bbox": [7200, 8400, 54000, 10200],
      "kind": "text_block",
      "text": "Revenue increased to $12.4 million."
    }
  ]
}
```

`spans` and `tables` are the only optional top-level arrays. There is no metadata or extension
object in v1, and `additionalProperties: false` applies at every object boundary. Omit optional
fields rather than setting them to `null`.

---

## 3. Page geometry: the part that trips everyone up

**Grounding JSON requires real page dimensions and real element boxes.** Most parsers do not emit
page geometry — OpenDataLoader does not — so this is usually the first thing that blocks a mapper.

Page geometry comes from the PDF itself, not from your parser. You need each page's MediaBox
dimensions and rotation. Any PDF library can read this without doing extraction:

- Python: `pypdf`, `pikepdf`, or `PyMuPDF`
- JavaScript: `pdf-lib`
- Java: PDFBox
- CLI: `pdfinfo` from poppler-utils

The shipped examples keep this in a small sidecar file next to the parser output:

```bash
node   examples/map-grounding.js  parser-output.json page-metadata.json grounding.json
python examples/map_grounding.py  parser-output.json page-metadata.json grounding.json
```

`page-metadata.json` carries the per-page width, height, and rotation in PDF points, sourced from
the PDF. Your mapper can read geometry however you like — a sidecar is just the simplest thing
that works and keeps the example dependency-free.

### If your parser is text-only

Then this profile is not for you yet, and that is deliberate.

**Do not** emit page-sized boxes, zero boxes, or invented coordinates to get past validation. It
would pass, and it would make the report claim inspectability that does not exist. That is exactly
the failure Ethos exists to prevent.

Open an issue describing the blocked integration instead. Making geometry optional would reshape a
public trait and needs its own compatibility decision, which should be driven by real blocked
integrations rather than guessed at.

---

## 4. Coordinates

Two conversions, in this order.

**Origin.** Ethos uses top-left, x increasing right, y increasing down. PDF-native coordinates are
bottom-left. If your parser reports `[left, bottom, right, top]` in PDF points against a page of
height `H`:

```text
x0 = left
y0 = H - top
x1 = right
y1 = H - bottom
```

**Unit.** Ethos uses centipoints — one hundredth of a PDF point — as integers. Multiply by 100 and
round half away from zero. Not banker's rounding, not truncation:

```python
def to_centipoints(points: float) -> int:
    return int(Decimal(str(points)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))  # on points*100
```

```javascript
const toCentipoints = (points) => {
  const scaled = points * 100;
  return scaled < 0 ? -Math.round(-scaled) : Math.round(scaled);
};
```

Ethos never guesses or silently converts units. If you submit points instead of centipoints, your
boxes will be 100× too small and will validate — they are still integers inside the page — but every
citation will fail to match. **A passing `grounding check` does not mean your coordinates are
right.** Verify one known claim end-to-end before trusting a mapper.

Every box is `[x0, y0, x1, y1]`, must have positive area, and must lie within its page.

---

## 5. IDs and ordering

- IDs match `^[A-Za-z0-9][A-Za-z0-9._:-]*$` and are unique within their typed namespace: pages,
  elements, spans, and tables each have their own namespace.
- Page indexes are 1-based, unique, and ascending.
- Every referenced page, element, and table must exist.
- A span and its owning element must reference the same page.
- Element order is your deterministic reading order and is semantically significant.
- Table cells are ordered by ascending `(row, col)`, are zero-based, have positive spans, and must
  not overlap.

**If your parser has no native stable IDs,** you may derive ordinal ones (`block-1`, `block-2`, …)
— but only after your parser's output order is itself deterministic. Derive them in the mapper;
Ethos never generates IDs during loading. Prove it with the double-run test in section 8.

Citations reference these IDs. If your IDs change between runs of the same document, every stored
citation breaks.

---

## 6. Capabilities: declare down, never up

```json
"capabilities": { "spans": false, "char_offsets": false, "tables": false }
```

Rules the validator enforces:

- `char_offsets: true` requires `spans: true`.
- Supplying `spans` is forbidden when `spans: false`.
- Supplying `tables` is forbidden when `tables: false`.
- Character offsets are zero-based **Unicode scalar** indexes with an exclusive end — not bytes,
  not UTF-16 code units. Watch this with emoji and combining marks.
- When offsets are declared, the referenced slice must equal the span text exactly.
- Empty `spans` or `tables` arrays do not change a declared capability.

Declaring `false` is not a failure. It produces an explicit, visible downgrade in the report:

```json
"capability_limits": ["missing_spans", "missing_char_offsets", "missing_tables"],
"warnings": ["capability_limited"]
```

That is the honest outcome, and it is far better than a `true` you cannot back. Ethos will never
upgrade a `false` declaration by inspecting a document.

---

## 7. The two hashes

This is the most common conceptual mistake. There are two different hashes and they answer
different questions.

| | `source.sha256` | `representation_sha256` |
| --- | --- | --- |
| What it hashes | the original PDF bytes | the accepted Grounding JSON bytes |
| Who writes it | your mapper declares it | Ethos computes it |
| Where it appears | inside your artifact | in the validation report, and as `document_fingerprint` in the verification report |
| What it proves | which PDF you claim you read | which representation was actually verified |

**Citations must carry `representation_sha256`, not the PDF hash.** Get it from `grounding check`:

```bash
ethos grounding check grounding.json --out validation.json
# -> "representation_sha256": "sha256:f0f1…"
```

```json
{
  "document_fingerprint": "sha256:f0f1…",
  "claims": [
    {
      "kind": "quote",
      "text": "Revenue increased to $12.4 million.",
      "citation": { "page": "page-1", "element_id": "block-17" }
    }
  ]
}
```

The verifier only ever sees your Grounding JSON. It cannot verify anything about the PDF, so the
fingerprint records what was actually checked. A consequence worth planning for: **re-emitting the
artifact changes the fingerprint** — including a `producer.version` bump against an unchanged PDF —
and stored citations against the old representation become `stale`. That is the honest answer. If
you re-extracted with a different parser build, you genuinely do not know the evidence is the same.

Supplying the PDF binds the two:

```bash
ethos grounding check grounding.json --source-artifact source.pdf --out validation.json
```

`source_binding` becomes `matched`, `mismatched`, or — without `--source-artifact` — `not_checked`.
It is never silently reported as `matched`.

**A match proves only that your mapper declared the hash of the PDF you supplied.** It is not
evidence that your parser extracted that PDF faithfully. Do not present it as such, and do not
build a product claim on it.

---

## 8. Self-check before you ship

Run this against your own mapper. It is the same bar the shipped examples meet.

**1. Determinism.** Run twice on identical input and compare bytes:

```bash
your-mapper input.json out-a.json
your-mapper input.json out-b.json
cmp out-a.json out-b.json
```

Nondeterminism usually comes from unordered map iteration, timestamps, absolute paths, or locale.
None of those belong in the artifact.

**2. Structure.**

```bash
ethos grounding check out-a.json --source-artifact source.pdf --out validation.json
```

Expect exit `0`, `structure: valid`, `source_binding: matched`.

**3. A real claim.** Take one exact string from a known element and verify it:

```bash
ethos verify out-a.json --citations citations.json --fail-on-ungrounded
```

Expect exit `0` and `all_evidence_grounded: true`. **Do not skip this step.** It is the only one
that catches wrong coordinates, wrong reading order, and unit mistakes, all of which pass
structural validation.

**4. A negative.** Change one character in the claim text and confirm you get `not_found` rather
than a match. A mapper that grounds everything is broken in a way that matters.

---

## 9. Rejections and what they mean

Errors are deterministic: the first failure, one stable code, one bounded JSON path. Ethos never
repairs an artifact.

| Code | Fix |
| --- | --- |
| `invalid_json` | submit valid UTF-8 JSON without unsupported numeric forms |
| `bom_not_allowed` | remove the UTF-8 BOM |
| `duplicate_key` | remove the duplicate object key |
| `unknown_field` | remove the unknown field |
| `invalid_field` | correct the field type or required fields |
| `unsupported_version` | use `ethos.grounding.v1` with `schema_version` `1.0.0` |
| `invalid_capabilities` | make capabilities agree with supplied arrays and offsets |
| `duplicate_id` | make identifiers unique within their typed namespace |
| `unknown_reference` | reference an existing page or element |
| `invalid_order` | preserve the required deterministic array order |
| `invalid_bbox` | submit a positive bounding box within its page |
| `invalid_offsets` | make Unicode scalar offsets select the span text exactly |
| `invalid_table` | correct table cell order, ranges, and overlaps |
| `invalid_invariant` | correct the referenced value or invariant |
| `limit_exceeded` | reduce the submitted artifact within the measured limits |

Floats and exponent forms are rejected outright — every number in the artifact is an integer.

### Limits

256 MiB input · 64 nesting levels · 5,000 pages · 1,000,000 elements · 1,000,000 spans ·
100,000 tables · 1,000,000 cells · 256-byte IDs · 16,384-byte strings.

Oversized input is rejected before any parse work, in milliseconds, with exit `7`.

### Sizing the process that runs the check

`grounding check` holds the parsed artifact in memory rather than streaming it, so **peak resident
memory runs about 6–12× the artifact size**. Measured on a release build.

Cost tracks the number of records — elements *and* spans — not bytes. Declaring `spans` roughly
doubles both the artifact and the resident set, so the two shapes are listed separately. Size your
worker from whichever row matches what your mapper emits.

**`capabilities` all `false`** (elements only):

| Elements | Artifact | Wall clock | Peak RSS |
| --- | --- | --- | --- |
| 10,000 | 1.5 MB | 0.15 s | 14 MB |
| 100,000 | 15 MB | 1.9 s | 138 MB |
| 1,000,000 (the ceiling) | 151 MB | 26.5 s | 1.29 GB |

**`spans: true, char_offsets: true`** (one span per element):

| Elements + spans | Artifact | Wall clock | Peak RSS |
| --- | --- | --- | --- |
| 10,000 | 2.3 MB | 0.13 s | 28 MB |
| 100,000 | 23.5 MB | 1.2 s | 270 MB |
| 1,000,000 (the ceiling) | 227 MiB | 13.0 s | 2.66 GB |

If you run Ethos in a memory-capped worker, size it from the shape you actually emit. **An artifact
at the element ceiling with spans needs roughly 3 GB.** A cap below that gets your worker killed
instead of receiving a clean rejection. Tables add cells on top of either shape and are not
tabulated separately; leave headroom if you emit large tables.

### Practice

`packages/npm/ethos-pdf/examples/fixtures/grounding-invalid.json` is a deliberately broken artifact.
Run `grounding check` on it, read the error, fix the one coordinate it names, and re-run. It takes
about a minute and teaches the whole correction loop.

---

## 10. What Ethos will never do

By design, so you can rely on it:

- infer, repair, or generate IDs
- guess or convert coordinate units
- reorder your arrays
- upgrade a `false` capability by inspecting a document
- repair or substitute a source hash
- accept an artifact that violates any invariant in section 5 or 6

And what a passing report does **not** mean: `grounded` says a submitted literal claim matched
recorded evidence. It says nothing about whether the answer is true, relevant, complete, fresh, or
correct for your business. Ethos does not generate claims, select evidence, or judge relevance.

---

## 11. Platform notes

Grounding JSON validation and verification **never require PDFium** and run anywhere the CLI runs,
including hosts Ethos does not ship binaries for.

The packaged npm binaries and the pinned PDFium profile cover macOS arm64 and Linux x64. On other
hosts — macOS x64, for example — build the CLI from source with `cargo build -p ethos-cli`; the
whole path in this guide works from that binary.

---

## 12. Reference

- Schema: `schemas/ethos-grounding-source.schema.json`
- Validation report schema: `schemas/ethos-grounding-validation-report.schema.json`
- Worked examples: `packages/npm/ethos-pdf/examples/map-grounding.js`, `map_grounding.py`
- Positive and negative fixtures: `schemas/examples/grounding-source*.json`
- Decision record: `docs/decisions/ADR-0016-grounding-json-v1.md`
