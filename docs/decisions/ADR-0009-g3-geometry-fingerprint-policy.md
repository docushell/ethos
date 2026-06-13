# ADR-0009: G3 Geometry Fingerprint Policy

- Status: **Accepted**
- Date: 2026-06-13
- Decider: Gate Zero decider
- Governs: Gate Zero G3 cross-platform geometry determinism, document fingerprints, and citation geometry.

## Context

Gate Zero G3 originally required byte-identical raw canonical payload hashes and document fingerprints
across `macos-arm64` and `linux-x64`. The first cross-platform G3 run failed on five synthetic
documents:

- `simple-text`
- `two-lines`
- `two-columns`
- `rotation-90`
- `hyphenated-line-break`

Raw document diffs showed that text, page structure, span order, font identity, warning IDs,
corpus bindings, manifest hash, and deterministic profile hash were stable. The divergences were
limited to bbox coordinates, which then changed `payload_sha256` and document fingerprints.

The geometry-source probe compared PDFium signals for those five documents across macOS arm64 and
Linux x64. The saved diagnostic reports are:

- `benchmarks/results/gate-zero/diagnostics/geometry/macos-linux-probe-comparison.json`
- `benchmarks/results/gate-zero/diagnostics/geometry/origin-locator-experiment.json`

The probe result was:

- `FPDFText_GetCharBox`: diverged on all five documents.
- `FPDFText_GetLooseCharBox`: diverged on all five documents.
- `FPDFText_GetRect`: diverged on all five documents.
- `FPDFText_GetCharOrigin`: matched on all five documents.

An origin-derived run locator using page id, run text/range, first/last char origins, font id, and
font size matched for all five documents.

## Decision

Do not make platform-unstable bbox dimensions fingerprint-critical for G3. Preserve precise bboxes
in document output for citation display, crop hints, and human inspection, but introduce a stable
origin-derived locator as the fingerprint-critical geometry identity for text runs.

The candidate locator policy is `origin-run-locator-v1`:

- page id
- parser-like run index
- run text
- character start/end range
- first `FPDFText_GetCharOrigin` point
- last `FPDFText_GetCharOrigin` point
- deterministic font id
- quantized font size

G3 compares `payload_sha256`, the stable payload projection hash, and document fingerprints. Raw
emitted JSON bytes may still differ when precise bbox dimensions differ, and `output_sha256`
remains diagnostic run data rather than the G3 equality key.

## Consequences

- The determinism contract defines `payload_sha256` as the stable payload projection hash.
- Existing precise bboxes should remain available for citation inspection, but public claims must
  not imply they are byte-stable across platforms.
- Verification can use stable origin locators for evidence identity while treating precise bboxes
  as display/evidence geometry with explicit tolerance and capability limits.
- The policy must be validated beyond the five synthetic documents before changing canonical
  fingerprints.
- G3 should not pass until macOS/Linux G1 evidence is rerun with the accepted policy and the
  resulting cross-platform G3 comparison passes.
