# Ethos Determinism Contract (c14n v1, ids-v1)

Status: v1 draft for Milestone A — changes only via `contract-change` PR with version bump
(PRD §5.1, §8; plan §6.2). This document is normative; `ethos-core` implements it; CI proves it.

**The guarantee (G3, PRD §1.3):** same input bytes + same effective config + same deterministic
profile ⇒ byte-identical canonical payload and equal fingerprints on every supported platform.
A canonical-payload difference across supported platforms under the deterministic profile is a
release-blocking bug (PRD §14). Determinism failures are never retried into green.

## 1. Canonical values

A *canonical value* is any JSON value covered by canonical equality:

| Value | Where |
| --- | --- |
| `payload` of the document graph | `ethos.json` (`urn:ethos:schema:document:1`) |
| fingerprint manifest | computed, §6 |
| effective-config hash subset | computed, §7 |
| verification config | `urn:ethos:schema:verification-config:1` |
| deterministic profile artifact | `profiles/ethos-deterministic-v*.json` |
| chunk records | `chunks.jsonl` lines |
| security / verification reports | their schemas |

The document *envelope* (`schema_version`, `parser`, `profile`, `source`, hashes) is bound by
fingerprints; the `diagnostics` object is runtime-only and excluded (§3).

## 2. c14n v1 — canonical JSON serialization

One implementation lives in `ethos-core::c14n`; no other crate hand-rolls output JSON
(invariant 2). The algorithm over a JSON value:

1. **Encoding:** UTF-8, no BOM, no trailing newline. The hash is over exactly these bytes.
2. **Whitespace:** none. Separators are `,` and `:` with no spaces.
3. **Objects:** keys sorted strictly ascending by Unicode code point (= byte order of their
   UTF-8 encodings). Duplicate keys are a c14n error. (Contract keys are ASCII snake_case, so
   exotic orderings cannot arise, but the rule is total.)
4. **Strings:** raw UTF-8, minimal escaping only:
   - `"` → `\"`, `\` → `\\`;
   - U+0008 `\b`, U+0009 `\t`, U+000A `\n`, U+000C `\f`, U+000D `\r`;
   - other control chars U+0000–U+001F → `\u00xx`, lowercase hex;
   - nothing else is escaped (no `\uXXXX` for non-ASCII; no Unicode normalization — extracted
     text is preserved exactly as extracted).
5. **Numbers:** **integers only.** Base-10, no leading zeros, no `+`, no exponent; `-0` is
   normalized to `0`. Magnitude must satisfy |n| ≤ 2^53−1 (ecosystem-safe). Any non-integer
   number anywhere in a canonical value is a c14n error — geometry is quantized (§4),
   confidence is per-mille, token counts are integers. Floats do not exist in canonical Ethos.
6. **Arrays:** order preserved — array order is semantic (element order IS reading order;
   span/cell/warning orders are defined in §5).
7. **Booleans / null:** literal `true`, `false`, `null`.

c14n is idempotent: `c14n(parse(c14n(v))) == c14n(v)`. Property-tested in `ethos-core`.

A reference implementation in Python (used to generate the §10 vectors):
`json.dumps(v, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")`
— valid only because canonical values contain no floats and no duplicate keys.

## 3. Canonical exclusion table

| Field | Reason |
| --- | --- |
| `$.diagnostics` (whole object) | timings, memory, host info, source paths — varies per run/host |

Rules: nothing inside `payload` may be runtime-dependent (property-tested: no
`diagnostics`-class field names appear in payload); by default the CLI writes **no volatile
diagnostics** (`--diagnostics` opts in), so default output files are byte-identical too, not
just their payloads.

## 4. Geometry quantization (quantize-at-extraction, invariant 1)

- Unit: **quantum = 1/100 PDF point** (`quantum_per_point: 100` in the profile).
- Conversion: `q = round_half_away_from_zero(pts × 100)` computed in `ethos-pdf` **at
  extraction**, before any layout/table/chunk/reading-order heuristic sees a coordinate.
- Implementation must be bit-stable: scale in f64, then
  `if x ≥ 0 { floor(x + 0.5) } else { ceil(x − 0.5) }`, then checked-cast to i64. IEEE-754
  double arithmetic on the same inputs is identical across supported platforms; the only
  permitted float math is this single scale-and-round.
- Enforced by type: extraction emits `QuantizedGeom` (`QPoint`/`QRect`, i64 quanta); raw
  `f64` tuples cannot cross the backend boundary.
- bbox = `[x0, y0, x1, y1]`, top-left origin, `x0 ≤ x1`, `y0 ≤ y1`, after page-rotation
  normalization. Page width/height are quantized the same way.
- Quantization is idempotent by construction (integers in ⇒ same integers out), and
  re-serialization is stable: `parse(serialize(doc)) == doc` exactly.

## 5. ID scheme (ids-v1)

IDs are deterministic functions of canonical order — never random, never time-based.

| Kind | Format | Order rule |
| --- | --- | --- |
| page | `p%04d` | **1-based original document index** — `--pages 3-4` yields `p0003`, `p0004` |
| span | `s%06d` | normalized content-stream order under the pinned backend (page asc, then stream order) |
| element | `e%06d` | reading order, pages ascending (layout output order = array order) |
| table | `t%04d` | reading-order position of the table's anchor element |
| region | `r%04d` | (page asc, y0 asc, x0 asc, stream order) |
| chunk | `c%06d` | chunker emission order (deterministic function of element order + config) |
| warning | `w%04d` | sorted by (code, page, element_ref, span_ref, region_ref, message), then numbered; the sort makes numbering independent of internal pipeline emission order |
| finding | `f%04d` | same rule, within the security report |
| check | `v%04d` | input citation order |

Width overflow (e.g. >999,999 elements) is an `internal_error` — resource limits (PRD §10)
bound real documents far below these widths.

## 6. Fingerprints

All hashes are SHA-256; hex is lowercase; prefixed forms read `sha256:<64 hex>`.

| Name | Formula |
| --- | --- |
| `source.fingerprint` | `sha256:` + sha256(source PDF bytes) |
| `payload_sha256` | sha256(c14n(payload)) |
| `profile.sha256` | sha256(c14n(profile artifact JSON)) |
| `config_sha256` | sha256(c14n(effective-config subset)) — §7 |
| `fingerprint` (document) | `sha256:` + sha256(c14n(fingerprint manifest)) |

Fingerprint manifest — exactly these keys (c14n sorts them):

```json
{"config_sha256":"…","payload_sha256":"…","profile_id":"…","profile_sha256":"…","schema_version":"…","source_fingerprint":"sha256:…"}
```

The backend build identity (PDFium version/flags/hashes, ADR-0002) and font profile
(ADR-0003) are pinned inside the profile artifact, so `profile_sha256` binds them into every
document fingerprint. `ethos fingerprint` recomputes and checks these. Two parses are
comparable iff their fingerprints are equal; verification treats a fingerprint mismatch as
stale evidence.

## 7. Effective-config hash

`config_sha256` hashes the c14n of the *config-hash subset* of the effective configuration —
exactly the fields listed in the profile's `config_hash_inputs` (v1: `pages`).

- `pages`: canonical form of the page selection — ranges parsed from `--pages` syntax
  (`1-5,9`), validated (1-based, ascending bounds, in-document), merged and sorted:
  `"1-5,9"` ⇒ `[[1,5],[9,9]]`; absent selection ⇒ `"all"`. A different page range is a
  legitimately different canonical output (different `config_sha256` ⇒ different fingerprint).
- Fields that do not change the canonical payload (output format selection, verbosity) never
  enter the hash. Chunker/exporter config joins `config_hash_inputs` via `contract-change` PR
  when those lanes land (Milestone C).

## 8. Warning determinism

- Messages come from **fixed templates** keyed by code — no timestamps, paths, hostnames,
  counts-of-the-day. Template changes are output-changing (semver event).
- Stable codes only (PRD §10): 11 warning codes, 10 error codes, mirrored in
  `ethos-core::error` and the schemas. New codes = `contract-change`.
- Ordering/numbering per §5; `security_warnings` vs `parser_warnings` split is by code class:
  security codes are `hidden_text_detected`, `off_page_text_detected`,
  `low_contrast_text_detected`, `annotations_present`, `external_links_present`,
  `unsupported_annotation`, `image_only_page`; the rest are parser warnings.
- Deterministic truncation: any preview text (e.g. security findings) truncates to 120
  Unicode scalar values + `…`, never by bytes.

## 9. Derived artifacts

Markdown, text, chunks.jsonl, reports, and overlays are deterministic functions of
(canonical JSON, versioned config). Same document + same config ⇒ byte-identical derived
artifacts. JSONL files use LF separators and end with a single trailing LF.

## 10. Test vectors (c14n v1)

Embedded in `ethos-core` tests; cross-checked against the Python reference. Inputs are stated
as JSON with explicit codepoints; expected output is the exact c14n byte string and its sha256.

| # | Input (semantic) | c14n bytes | sha256 |
| --- | --- | --- | --- |
| V1 | `{}` | `{}` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| V2 | `{"b":2,"a":1,"_":0,"Z":-3}` | `{"Z":-3,"_":0,"a":1,"b":2}` | `9e8c5fa78b63297991b5b7b45bd334ccc61bd1058c5cd8ca6ee0451f78cd6cc1` |
| V3 | obj with `arr:[3,1,2]`, `flag:true`, `n_neg:-42`, `n_zero:0`, `nothing:null`, `text:"líne1\nl\"ine2\tend — 💡"` (— = U+2014, 💡 = U+1F4A1) | `{"arr":[3,1,2],"flag":true,"n_neg":-42,"n_zero":0,"nothing":null,"text":"líne1\nl\"ine2\tend — 💡"}` (with real `\n`/`\t` escapes) | `86b355efaa571cac1ddb71d422a9971e6042c55ec5369305cce095f2c181426e` |
| V3b | `{"bel":"<U+0007>","backslash":"a\\b"}` | `{"backslash":"a\\b","bel":"\u0007"}` | `a1cc2b96cfaf4e1d27ca13e7c2e56faadf76bd027d233fce5a57124e36ea6dfd` |
| V4 | fingerprint manifest of `schemas/examples/document.example.json` (its embedded hashes are real — regenerated by the reference implementation) | (see §6 manifest with the example's hashes) | `ace86a9fd5f262ed22abb9dcfc7aa0b4eaea12d6f2de696272944f3d416fb194` |

Profile artifact pin: sha256(c14n(`profiles/ethos-deterministic-v1.json`)) =
`73c4883acfbe32727b97d4ede0dce7e65c9053a8a98883545cb02a2fe0733a77` (asserted in
`ethos-core` tests; changes only with a profile version bump).

## 11. Conformance (CI)

- Per-PR: c14n idempotence + no-float + key-order property tests; vector tests; deterministic
  profile validation; same-platform double-parse byte-diff (once the backend lands).
- Nightly + `contract-change` PRs: cross-platform fingerprint + canonical-payload equality on
  Gate Zero platforms (macOS arm64, Linux x64); Windows x64 joins by Milestone B exit (week 8).
- Verification reports are themselves determinism-tested (same inputs ⇒ same report bytes).

## 12. Versioning

c14n algorithm or exclusion-table changes bump `c14n.version` and the profile version —
breaking (old fingerprints incomparable). ID scheme changes bump `id_scheme.version` —
breaking. Both require `contract-change` PR + decider sign-off + CHANGELOG.
