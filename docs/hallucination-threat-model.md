# Advanced Hallucination Threat Model and Deterministic Hardening Roadmap

Status: implemented on the current source tree. This document records Ethos's posture against
anticipated next-generation citation hallucinations and the deterministic hardening now present
in the verifier, evidence-anchor reports, and app-answer-release contract. Release packaging and
public product claims remain separate decisions.

Owner: product / decider.
Related: ADR-0007 (trust layer first), ADR-0012 (evidence anchoring boundary),
`docs/app-answer-release-contract.md`, `docs/milestone-d-claim-kind-boundary-contract.md`,
`docs/determinism-contract.md`.

Code references cite behavior verified on the current source tree; re-verify before relying on
line-level details.

## Premise

As LLMs improve, citation hallucinations will shift from inventing text toward defeating naive
validators: recombining real fragments, citing true evidence in misleading contexts, and
distorting meaning around perfectly copied spans. Ethos's defense is not to out-guess models
semantically; it is to make every seam between proof and interpretation loudly visible in a
deterministic report, and to keep the proof layer impossible to satisfy with anything but the
cited evidence at the cited location.

## Threat Assessment

### T1: Context stitching (fragment recombination)

Threat: generated text assembled from real phrases scattered across a document, aimed at
validators that substring-match against the whole document text.

Current posture: **countered within the deterministic locator boundary.** Ethos does not
match against whole-document text. Locator resolution (`resolve_target` in `ethos-verify`) is
precedence-based: table locators first, then `span_id`, then `element_id`, then `page`+`bbox`.
Matching runs against the resolved target, or — for quote claims only — the cited element joined
with **one numerically adjacent element under the source's declared coordinates** (shared bbox
edge on the same line, or vertically stacked with a shared edge; `adjacent_quote_target` /
`element_bboxes_are_adjacent`). The join is inferred from an ordinary `element_id` quote claim,
not a general caller-declared multi-span citation contract. Existing tests confirm the join
rejects page-only citations, non-adjacent elements, unknown-coordinate joins, and direct
cross-page adjacency.

Consequence for T1: a sentence stitched from fragments in different, non-adjacent elements does
not exist contiguously in any permitted match target and returns `mismatch`, fail-closed.

**Resolved gap G1 — locators are jointly enforced where the source contract can prove
agreement.** A supplemental `page` must agree with the resolved table, span, or element target,
and multiple primary locator groups fail closed with `locator_conflict`.

**Resolved gap G2 — adjacency is capability-gated.** Adjacent-element joins require a known
coordinate origin. A source with `CoordinateOrigin::Unknown` may still ground a single-element
match, and a check whose outcome genuinely turns on adjacency fails closed with
`capability_limited` and `unknown_coordinate_origin`. A quote that no reading-order neighbour
could have joined still returns its determinate `mismatch`: refusing there would trade a sound
negative for "cannot tell" and hide a real document finding behind a capability limit.

The residual threat above the verifier: N individually true fragment claims assembled into a
misleading answer. Each check is legitimately `grounded`; the distortion lives in the assembly.
Assembly is app-owned by contract (synthesis axis), and R3 gives the app layer a dispersion
signal for it.

### T2: True evidence, wrong context

Threat: a fact quoted accurately from one part of a document (for example, a definitions section)
used to answer a question governed by another part (for example, a termination clause), fully
grounded and fully misleading.

Current posture: **out of scope by design, with deterministic review context now exposed.** Ethos
never sees the user's question and structurally cannot judge relevance; the app-answer-release
contract assigns the question-relevance axis to the application. Hardened 1.1 reports can now
include the cited element's heading path, role, and reading-order neighbors. Sources without that
structure report `capability_limited` provenance rather than inventing it.

### T3: Semantic drift around exact spans

Threat: a span copied perfectly while the surrounding paraphrase inverts or weakens its meaning
("We may approve" presented as "We will approve"), or modality/negation stripped by quoting a
fragment out of its sentence.

Current posture: **literal drift is caught; semantic drift has an explicit app-owned landing
place.** If the span itself is altered, matching against the resolved target fails (`mismatch`) —
"will approve" is not in the source element. If the span is exact and the distortion lives in
surrounding answer text, the check is legitimately `grounded`: a cited exact span can be grounded
while the surrounding answer is still misleading.

Precision notes, both verified:

- The `semantic_unverified` report field is **not** an active detector for this case. The current
  alpha literal checkers always set it `false` — non-literal claims fail closed as unsupported
  rather than being marked semantically checked (`verify_types.rs`). The field marks the boundary
  in the schema; it does not fire on exact-span drift.
- **Resolved gap G3 — the app release envelope represents this state explicitly.** The 1.1
  envelope carries app-owned `claim_support` values (`supported`, `unsupported`, `contradicted`,
  or `not_evaluated`). Grounded-but-unsupported and grounded-but-contradicted claims are blocked;
  unevaluated claims require review. Ethos transports this label but never computes it.

R2 makes app-layer and human review of this case cheaper, but it does not make Ethos semantically
judge it. Hardened reports expose a bounded source context echo without requiring PDFium; rendered
crops remain available as a separate visual audit path.

## Explicit Non-Goal: no semantic entailment engine in Ethos core

Rejected: transitioning Ethos core to a semantic entailment engine.

Entailment is probabilistic. Ethos's product identity is deterministic, reproducible,
dependency-restricted proof (ADR-0004, ADR-0007, determinism contract). A core that returns
non-reproducible judgments can no longer tell an auditor which part of a report is proven, and
competes as a worse version of probabilistic LLM-judge tools instead of as the layer beneath them.

If market demand justifies semantic checking, it ships **above** the proof layer: an optional,
separately named, clearly probabilistic tier (application-side or a future separate product) that
consumes verification reports and never contaminates them. Canonical report artifacts must never
contain non-deterministic fields. R5 below defines where such a tier's *output label* lands — in
the app-owned decision envelope, never in the canonical verification report.

## Deterministic Hardening Roadmap

R0–R3 and R5 are implemented on the source tree; R4 remains standing discipline. None add ML,
network access, or judgment calls to core.

### R0: Verifier hardening — close G1 and G2 (implemented)

- **R0a — supplemental-page agreement.** Full pairwise agreement across all locator kinds is not
  uniformly computable: span→element ownership is optional (`GroundingSpan.element` is
  `Option`), and tables expose no element ownership. R0a is therefore scoped precisely: the
  citation's **primary locator** is whichever field wins the existing `resolve_target` precedence
  (table cell, then `span_id`, then `element_id`, then `page`+`bbox`), and the only permitted
  supplemental field in v1 is `page` — which, when supplied alongside a primary locator, must
  agree with the resolved target's page or the check fails closed (`mismatch` or a dedicated
  `locator_conflict` reason) instead of the page being silently ignored. **Multiple primary
  locator groups are invalid**: a citation supplying locators from more than one primary group
  (for example `span_id` alongside `element_id`, or a table locator alongside `element_id`)
  fails closed with `locator_conflict` — precedence must never silently ignore a supplied
  locator field. Other cross-locator agreement rules (span-in-element, bbox-in-element) require
  ownership data the contract does not guarantee and are out of scope until `GroundingSource`
  exposes them. This is a behavior change to `resolve_target` and needs its own contract note
  plus golden updates.
- **R0b — adjacency capability gate.** The adjacent-element quote join requires a trusted
  geometry basis: gate it on a compatible coordinate-origin/reading-order capability, mirroring
  the existing `page`+`bbox` refusal of `CoordinateOrigin::Unknown`. Sources without the
  capability get single-element matching only, with a `capability_limited` diagnostic when the
  join would have been attempted. **"Would have been attempted" is decided, not assumed.** Of the
  join's preconditions only `element_bboxes_are_adjacent` reads coordinates *as* coordinates; page
  identity, bbox presence, and the joined-text match are structural and hold whatever the origin
  is. On an unknown-origin source the verifier evaluates those first
  (`adjacent_join_has_text_candidate`): when no reading-order neighbour could have joined anyway,
  the outcome does not turn on geometry, and the determinate `mismatch` already computed against
  the cited element stands. `capability_limited` is reserved for the case where a neighbour
  genuinely would have joined and only adjacency is unknowable. Neither branch can return
  `grounded`, so the refinement cannot leak a pass.
- DocuShell use: none directly — this is trust-surface integrity. It is a prerequisite for the
  acceptance tests below meaning what they say.

### R1: Structural provenance on checks (implemented, config-gated)

Add the cited element's structural context to each verification/anchor check: heading chain
(section path), element role, and reading-order neighbors' identity.

Scope honesty: this is **more than report enrichment.** No section path exists as report-ready
data today. Native elements carry type, heading level, and reading order (`ethos-core::model`),
so a deterministic heading-chain derivation is buildable for native sources — but
`GroundingElement` exposes only id/page/bbox/kind/text (`ethos-core::grounding`), so R1 requires:
(a) a deterministic structural-provenance derivation over the native document graph, and (b) a
`GroundingSource` contract/capability extension so foreign adapters can declare whether they
expose structure. Plan it as a contract-change lane, not a field addition.

- Report sketch: `check.provenance = { heading_path: ["§14", "§14.2 Termination for Convenience"], element_role: "paragraph" }`.
- DocuShell use: one breadcrumb line under each citation chip ("✓ p.12 — §14.2 Termination for
  Convenience"); later, app policy over section paths.
- Boundary: provenance describes where evidence lives. It does not judge whether that location is
  relevant to any question.
- Foreign sources: capability-gated; adapters that expose no structure report `capability_limited`
  provenance, never a fabricated one.

### R2: Source context echo (implemented, config-gated)

Include a bounded window of source text surrounding the matched span in each grounded quote/value
check, with the matched span delimited. The textual analog of crops, with no PDFium, render step,
or click required.

Scope honesty: **not pure report enrichment** — normalized matching collapses whitespace and uses
containment (`text_matches` in `ethos-verify`), so the contract must pin deterministic
match-location rules before the echo can be byte-stable:

- how a normalized match maps back to original (un-normalized) source text offsets;
- which occurrence wins when the matched text repeats within the target (first occurrence in
  reading order is the default candidate rule);
- window units (Unicode scalar values vs bytes vs grapheme clusters) fixed by the deterministic
  profile;
- behavior when a match crosses the synthetic join between the cited element and its adjacent
  element (echo must mark the element boundary, never fabricate contiguous source text).

- Report sketch: `check.context_echo = { before: "In no event, except as stated in §9, ", match: "the vendor will refund all fees", after: " paid in advance." }`.
- DocuShell use: citation tooltip with the span bolded in its source sentence; the same field in
  job metadata closes most "the AI lied" support tickets by inspection.
- Boundary: the echo is quoted source text, deterministic and byte-stable. Ethos draws no
  conclusion from it. The field must be omittable by config (redaction-sensitive consumers)
  without changing check statuses.

### R3: Evidence dispersion diagnostics (implemented, config-gated)

Report-level counts describing how scattered the verified evidence is. Split into two phases:

- **R3a (independent):** the counted population is **reusable grounded checks**, matching the
  existing proof-summary rule: `status = grounded`, `semantic_unverified = false`, and the report
  is not fingerprint-stale. Mismatched, not-found, unsupported, and `capability_blocked` checks
  are excluded. A grounded check is **not** excluded merely because the report carries
  `capability_limited` warnings — capability limits stay visible without invalidating grounding
  (the existing proof-summary tests certify and reuse grounded checks alongside capability
  warnings). Because grounded checks may target elements, spans, table cells, bbox regions, or
  page-level presence, and not every resolved target carries an element identity, the contract
  must define `elements` precisely: **distinct resolved source elements of element-addressed
  grounded checks.** Checks whose targets carry no element identity are counted separately as
  `unmapped_grounded_checks` so dispersion can never silently understate scatter.

  **Adjacent-element joins count both elements.** A quote grounded through the adjacent-element
  join resolves across two elements and contributes **both resolved element IDs** to `elements` —
  R3 counters stitching, and the join is precisely the sanctioned stitching case, so it must be
  visible in the count. As implemented, the join carries both identities: `adjacent_quote_target`
  returns `element_ids: [first, second]` on the joined `FoundTarget`, which reaches the check as
  `resolved_element_ids`, so joined quotes are counted in `elements` and never fall through to
  `unmapped_grounded_checks`. `element_index` stays `None` on the joined target — it addresses a
  single position and a join has two — and is not the identity carrier.
- **R3b (depends on R1):** distinct top-level sections spanned. Section identity requires R1's
  structural provenance; do not approximate it from page ranges. The `sections` count is omitted
  when any reusable grounded target is unmapped or lacks structural provenance, so it cannot
  silently understate dispersion.

- Report sketch (R3a): `report.dispersion = { grounded_checks: 4, elements: 3, pages: 3, unmapped_grounded_checks: 1 }`; R3b adds `sections: 3`.
- DocuShell use: one app-owned threshold (with R3a, pages >= 3 on a short answer; with R3b,
  sections >= 3 shows "Assembled from multiple sections — review sources"). Thresholds are
  application policy and never ship as Ethos judgments.
- Boundary: integers only. High dispersion is not an error, a warning, or a score; legitimate
  cross-document synthesis exists. Fits the internal readiness derivation planned for the
  DocuShell integration lane.

### R4: Claim-kind boundary discipline (standing defense, already shipped)

The existing claim-kind boundary contract stays the spine of adversarial resilience: any claim
kind Ethos cannot prove is an explicit `unsupported` diagnostic, never a fuzzy pass. As models
emit new citation shapes, each either gets exact deterministic semantics through a contract-change
PR or remains loudly unsupported.

- DocuShell use: render `unsupported` as "unverifiable," never as verified.
- Boundary: no "best effort" matching modes, ever. A validator that approximates is a validator
  that can be gamed.

### R5: App-contract claim-support axis (implemented; closes G3)

Extend the **app-answer-release contract and decision envelope** (not the canonical verification
report) with an app-owned claim-support axis so the T3 end-state is representable:

```text
citation_grounded = true
claim_support     = supported | unsupported | contradicted | not_evaluated   (app-owned label)
release_action    = block                                                    (per app policy)
```

Because semantic review is optional, `not_evaluated` is the default state and **fails closed**:
a claim with `citation_grounded = true` and `claim_support = not_evaluated` may not release as
final; it lands in `review` (or `block`, per app policy) until evaluated. Interaction with the
existing `claim_type` axis must be specified, not left ambiguous: `claim_type` describes what
kind of statement the claim is (source fact vs synthesis), `claim_support` describes whether its
meaning is faithful to the grounded evidence, and the stricter of the two axes always wins the
release action — e.g. `claim_type = source_fact` with `claim_support = unsupported` or
`contradicted` releases as `block`, regardless of grounding.

**Resolving the overlap with `claim_type = unsupported`.** The current `AppClaimType` enum
contains a third value, `unsupported`, which overlaps with the new axis. R5 removes the overlap
by decision, not coexistence: `claim_type = unsupported` is **deprecated** in the same contract
change, leaving `claim_type` as `source_fact | synthesis`. Transition rules: a legacy input
supplying `claim_type = unsupported` is accepted during the deprecation window and mapped to
`claim_support = unsupported` (with `claim_type` recorded as unspecified); a contradictory
combination such as legacy `claim_type = unsupported` alongside `claim_support = supported` is
rejected as an input error. After the window, `claim_type = unsupported` is rejected outright.
Two fields describing the same fact is how envelopes silently disagree with themselves.

This requires relaxing the current helper rule that rejects an unsupported claim whose citation is
grounded — that combination stops being an input error and becomes the canonical description of a
semantically drifted answer. The evaluator that assigns `claim_support` stays probabilistic or
human-reviewed and lives **outside** canonical Ethos reports, consistent with the non-goal above:
Ethos transports the label in the app envelope; it never computes it.

- DocuShell use: Evidence Chat can block or flag an answer whose citations all verify but whose
  claim a reviewer (or future semantic tier) marked unsupported — today that state cannot even be
  recorded.
- Boundary: `claim_support` never appears in `verification_report.json`. It is an application
  decision-envelope field with an explicit "not proven by Ethos" framing.

## Schema and Golden Compatibility

The new report fields are **not** automatically compatible: the verification-report schema declares
`additionalProperties: false`, so old validators reject reports carrying new fields, and any
emitted field changes byte goldens. R1/R2/R3 therefore use:

- profile- or config-gated emission (fields absent unless enabled), **and** a schema-version
  transition for the enabled shape, with the schema updated in the same `contract-change` PR;
- an unchanged 1.0 default example and a hardened 1.1 config/report pair;
- an explicit compatibility note before release packaging.

"Additive and optional" is a design goal for consumers that opt in; it is not a claim that
existing strict validators keep passing without a schema update.

## Implementation and release sequencing

The source implementation follows the dependency order R0, R2/R3a, R1/R3b, with R5 isolated in
the app envelope. R4 remains continuous. The default verifier profile stays at report schema
1.0.0; opting into hardening emits 1.1.0. Release versioning, soak time, and inclusion in any
package packet require a separate decider action.

## Acceptance Criteria (adversarial test matrix)

Each roadmap item lands with fixture-backed tests proving the boundary holds, not just that the
feature works:

1. **Supplemental-page agreement (R0a):** a citation with a correct `element_id` (or `span_id`,
   or table locator) and a supplemental `page` that disagrees with the resolved target's page
   fails closed with a locator-conflict diagnostic; the same citation with an agreeing or absent
   `page` still grounds; a citation supplying locators from more than one primary group
   (`span_id` + `element_id`, or table + `element_id`) fails closed with `locator_conflict`.
2. **Adjacent-only stitching:** a quote spanning the cited element and its strictly adjacent
   neighbor grounds; the same text cited against a non-adjacent element pair returns `mismatch`.
3. **Unknown-coordinate adjacency (R0b):** a foreign source with `CoordinateOrigin::Unknown`
   never produces an adjacency join, and single-element matching still works. The refusal is
   conditional on the join being load-bearing: a quote whose cited element does not contain it and
   whose reading-order neighbours do not join to match it returns `mismatch`/`text_mismatch`, not
   `capability_blocked`; a quote that genuinely spans the cited element and its neighbour returns
   `capability_blocked`/`unknown_coordinate_origin`. A neighbour on the next page is never a
   candidate, so a page-break split is `mismatch`, not a capability limit.
4. **Non-adjacent recombination:** a sentence assembled from real fragments in non-adjacent
   elements, cited against any single element, returns `mismatch` — never `grounded`.
5. **Cross-page adjacency:** the adjacency join never crosses pages, including when bbox numbers
   would otherwise satisfy the edge rules.
6. **Exact quote, misleading app claim (R5):** a fixture where the span grounds
   (`semantic_unverified: false`) and the app envelope records
   `citation_grounded: true, claim_support: unsupported, release_action: block`; a companion case
   proves `claim_support: not_evaluated` fails closed to `review`/`block` and never releases as
   final; migration cases prove legacy `claim_type: unsupported` maps to
   `claim_support: unsupported` and that legacy `claim_type: unsupported` alongside
   `claim_support: supported` is rejected as an input error. This test documents the division of
   labor; it must never be "fixed" by making the verifier guess.
7. **Missing-structure capability (R1):** a foreign source without structural metadata yields
   `capability_limited` provenance, never a fabricated heading path; native sources yield a
   byte-stable heading chain across platforms.
8. **Echo determinism (R2):** repeated-text fixtures prove occurrence selection is stable;
   normalized-match fixtures prove original-text mapping is byte-identical across runs and
   platforms; a match spanning the adjacent-element join marks the element boundary in the echo.
9. **Dispersion definition (R3):** the counted population is reusable grounded checks —
   mismatched, not-found, unsupported, and `capability_blocked` checks are excluded, and a
   fingerprint-stale report contributes nothing; a grounded check accompanied by
   `capability_limited` report warnings **is** counted (capability limits do not invalidate
   grounding); a quote grounded through the adjacent-element join contributes both resolved
   element IDs to `elements`, not `unmapped_grounded_checks`; non-element-addressed grounded
   checks land in `unmapped_grounded_checks`; a report with zero reusable grounded checks
   reports zero dispersion, not an error.

## Claims Boundary

This document is an engineering implementation record, not a public claim. Nothing here asserts that Ethos
detects, prevents, or scores hallucinations, semantic drift, or context misuse. Public wording
about any shipped roadmap item goes through `docs/public-boundary-claims.json` and must describe
deterministic report fields, not adversarial-robustness guarantees.
