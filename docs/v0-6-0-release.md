# Ethos v0.6.0 — Release Record

Status: **implementation verified; release blocked on governance and platform items in section 8.**
This document does not authorize publication, production positioning, or any new public claim.

Date: 2026-07-30. Branch: `v0_6_0Release`. Baseline: `main` at the v0.5.0 publication closeout.

This is the reality-based companion to [`v0-6-0-release-prep.md`](v0-6-0-release-prep.md), which
remains the scope authority. Where this document and the prep document disagree, the difference is
called out explicitly in section 3 and needs a decider ruling — it is not silently resolved here.

---

## 1. What v0.6.0 is

An **adoption release**. It adds one strict, language-neutral `ethos.grounding.v1` JSON artifact in
front of the existing `GroundingSource` boundary, so that a parser written in any language can reach
the existing verifier by emitting one file.

```text
any parser, any language
  -> one deterministic mapper owned by that integration
  -> ethos.grounding.v1 JSON
  -> one shared Ethos loader and validator
  -> existing GroundingSource
  -> existing ethos-verify algorithm
  -> existing verification_report.json
```

No new verification algorithm. No change to the verification report. No plugin runtime, mapping
language, hosted service, receipt, proof package, or replay protocol.

---

## 2. Verification record

Everything below was executed on 2026-07-30. Nothing in this section is inferred.

**Environment.** Rust 1.87.0 / cargo 1.87.0. Node v20.11.1. Python 3.13.3.
Host platform `darwin:x64`. PDFium 151.0.7881.0 (`chromium/7881`) extracted to
`~/.cache/ethos/pdfium/chromium-7881/lib/libpdfium.dylib`.

### 2.1 Build and lint

| Gate | Result |
| --- | --- |
| `cargo build --locked -p ethos-cli` | clean |
| `cargo clippy --locked --workspace --all-targets --all-features -- -D warnings` | **clean, after fixing 4 findings** (section 4.3) |

### 2.2 Test suite

`cargo test --locked --workspace --no-fail-fast`:

| `ETHOS_PDFIUM_LIBRARY_PATH` | Before this work | After |
| --- | --- | --- |
| unset | 389 passed, 1 failed | **390 passed, 0 failed** |
| set to a correct PDFium this host cannot pin | 364 passed, 27 failed | **390 passed, 0 failed** |

Both pre-existing failure sets were confirmed on `main` by stashing all working-tree changes and
re-running. Neither was a regression from v0.6.0; both are now fixed.

### 2.3 The PDFium trap — fixed

`ethos doctor --require-pdfium` on this host reports
`configured PDFium is not usable by Ethos: pdfium phase 1 profile has no hash for this platform`.
Ethos pins PDFium runtime hashes for macOS **arm64** and Linux **x64** only, so on `darwin:x64` a
correct library is rejected as unverifiable regardless of its contents.

The PDFium-gated tests previously skipped when the variable was unset but **hard-failed when it was
set to a library Ethos could not verify**, so a contributor who correctly followed
`scripts/fetch-pdfium.sh` on an unsupported host ended up strictly worse off than one who ignored
it — 27 failures instead of 1.

The harness now asks the product instead of guessing: `pdfium_configured()` in the CLI test suites
runs `ethos doctor --require-pdfium` and skips with an explanatory message when Ethos does not
accept the library. The in-crate `ethos-pdf` test consults `current_platform_key()` for the same
reason. Two doctor tests that asserted a pin-mismatch message now assert the platform-independent
contract — exit 12, "not usable by Ethos", phase 1 profile named, setup guidance present — and
check the pin-specific wording only on hosts that have a pinned profile.

### 2.4 Schema and governance gates

| Gate | Result |
| --- | --- |
| `schemas/validate_examples.py` | **all green** — both new schemas valid 2020-12; 3 positive examples accepted; all 5 negative fixtures correctly rejected |
| `public_boundary_claims_gate.py` | green |
| `claims_gate.py` | green |
| `test_public_surface_posture.py` | green |
| `test_execution_status.py` | green |
| `test_release_state.py` | green |
| `test_claims_gate_registry_surfaces.py` | green |
| All 8 milestone-D / v1 contract gates | **green** (were red on `main` — see below) |

Across every `.github/scripts/test_*.py` gate, failures went from **12 to 4**, with none newly
broken. Three pre-existing defects, all traceable to commit `73d53c8` ("docs: remove completed
historical records"), were fixed:

1. **Eight contract gates asserted that `docs/roadmap.md` links the contract.** That file was
   deliberately deleted; the gates were never updated, so all eight errored on `FileNotFoundError`.
   They now check the surviving status surfaces.
2. **The Makefile invoked `.github/scripts/test_roadmap_status.py` in 11 targets.** The script does
   not exist, so `make milestone-d-grounding-source-contract` — the documented way to run the
   contract gate — failed outright. Removed, along with the ten contract-gate assertions that
   pinned the dead invocation in place.
3. **The frozen trait inventory omitted `structural_provenance`**, present on `GroundingSource`
   since v0.4.0. Added to both the inventory and the expected list, in declaration order.

The four remaining failures are pre-existing and unrelated to Grounding JSON:
`test_app_answer_release_release_prep`, `test_rag_framework_examples`, and — significantly —
`test_npm_binary_package_scaffold` and `test_package_registry_source_consistency`, which fail on
`'0.4.0' != '0.5.0'`. Those two are the public-version drift in section 8.

`jsonschema` was an undeclared dev dependency; `requirements-dev.txt` now records it.

### 2.5 End-to-end parser-agnostic path

Run against the built CLI with **no PDFium and no Rust knowledge required**:

| Step | Result |
| --- | --- |
| `grounding check` on the minimal fixture | exit `0`, `structure: valid`, `source_binding: not_checked` |
| `grounding check --source-artifact` with the correct PDF | exit `0`, `source_binding: matched` |
| `grounding check --source-artifact` with a truncated PDF | exit `2`, `source_binding: mismatched`, code `source_binding_mismatch`, report still written |
| `grounding check --source-artifact` with a non-PDF | exit `2`, `source artifact is not a PDF`, rejected on magic bytes before hashing |
| `verify` on Grounding JSON, no PDFium | exit `0`, `all_evidence_grounded: true`, `adapter: ethos-grounding-json`, `capability_limits: [missing_spans, missing_char_offsets, missing_tables]` |

Capability downgrades are surfaced honestly rather than approximated, and
`warnings: ["capability_limited"]` appears on a fully grounded report.

### 2.6 Mapper determinism

Both example mappers, run twice each over the same pinned parser output:

```text
node map-grounding.js   fixtures/parser-output.json fixtures/page-metadata.json out.json
python3 map_grounding.py fixtures/parser-output.json fixtures/page-metadata.json out.json
```

- JavaScript double-run: **byte-identical**
- Python double-run: **byte-identical**
- JavaScript output vs Python output: **byte-identical**
- Both vs the packaged `fixtures/grounding.json`: **byte-identical**

This satisfies §11.4 for the JavaScript and Python mappers. The DocuShell mapper row remains
outstanding (section 8).

### 2.7 Documented correction path

The quickstart's correction exercise was walked exactly as written:

1. `grounding check` on `grounding-invalid.json` → exit `2`, and the report names
   `invalid_bbox` at `/elements/0/bbox` with the message `submit a positive bounding box within its page`.
2. Change the box's right coordinate from `60000` to `39415`.
3. Re-run → exit `0`, `structure: valid`.

Ethos does not repair the artifact. The error is precise enough to fix without reading Ethos source,
which is the single best usability property in this release.

### 2.8 npm package

Previously `npm test` died at `sdk.test.js` with an uncaught
`Unsupported Ethos npm binary target: darwin x64`, so four of eight suites never ran.

The SDK now converts launcher failures into typed `EthosSdkError`s — `unsupported_platform` when
the host has no packaged binary, `vendor_invalid` when the payload is missing or malformed — and
the platform check runs before anything can spawn. `sdk.test.js` asserts that contract on
unsupported hosts, including that no process is spawned, then skips the spawn-backed assertions
that need a packaged binary for the target.

Seven of eight suites now pass here: platform selection, vendor assembly, vendor integrity, setup
guidance, sdk, examples, and clean-room. `types.test.js` and `tsc` require `npm install`, which
could not run in this sandbox (no network). The devDependencies are declared correctly, so this is
environmental. The full suite still needs a run on macOS arm64 or Linux x64 (section 8).

---

## 3. Decisions that differ from the prep document

### 3.1 Fingerprint identity — **decision required**

The implementation makes the verifier fingerprint the **representation hash**
(`representation_sha256`, the hash of the accepted Grounding JSON bytes), recorded in ADR-0016.

`v0-6-0-release-prep.md` §8.1 shows the opposite: a quickstart whose citations carry
`"document_fingerprint": "sha256:<same source hash>"`. Its §6.4 is ambiguous — "fixes fingerprint
support to true from `source.sha256`" reads as a capability statement, not a value statement — but
§8.1 is not ambiguous. **A caller who follows §8.1 against this build gets `stale`.**

Prep document is authority #2; ADR-0016 is #3. Per §3 of the prep document, this conflict must go to
the decider rather than be resolved in code.

Verified consequence: `grounding_json_representation_identity_drives_staleness` shows that changing
`producer.name` alone flips every citation to `stale` against an otherwise byte-identical artifact.
A parser version bump invalidates stored citations even when the PDF and geometry are unchanged.

Recommendation on record: **keep the representation hash.** The verifier never sees the PDF, so
stamping the PDF hash on the report as "what I checked" is a claim Ethos cannot support, and it
would let a silently re-mapped artifact with changed geometry read as fresh. If accepted, prep §8.1
must be corrected and the quickstart must explain the two hashes — representation identity versus
source binding — before release.

### 3.2 Shared dispatch now fails closed — **implemented**

Prep §7.3 rule 5 requires that a present-but-unsupported top-level `artifact_type` fail with exit
`2`, and rule 6 forbids falling back to another loader. The original implementation returned a
boolean and silently fell through to the native loader.

The loader now returns a tri-state (`Absent` / `GroundingV1` / `Unsupported`). Because
`serde_json::Value` collapses duplicate keys, a second strict pass counts top-level `artifact_type`
occurrences; anything other than exactly one is `Unsupported`.

Verified against the built binary — all three cases exit `2` with
`unsupported top-level artifact_type (expected exactly 'ethos.grounding.v1', ...)`:

| Input | Before | After |
| --- | --- | --- |
| `"artifact_type": "ethos.grounding.v2"` | fell through to native loader | rejected |
| `"artifact_type": 5` | fell through to native loader | rejected |
| duplicated `artifact_type` key | collapsed, then loaded | rejected |
| no `artifact_type` | native loader | native loader (unchanged) |
| malformed JSON / non-object root | native loader | native loader (unchanged) |

Absent, malformed, and non-object inputs deliberately stay with the native loader so it keeps
ownership of its own error messages. No input is classified by guessing field names.

### 3.3 `evidence anchor` joined the shared loader — **implemented**

`EvidenceAnchorArgs.grounding` was `String` with `default_value = "ethos-json"`. Because the flag was
never absent, auto-detection could never run — this was the "implementation default that prevents
shared dispatch" named in prep §7.3. It is now `Option<String>`, and the command delegates to the
shared loader.

Verified: native input with no flag and with explicit `--grounding ethos-json` produce
**byte-identical** reports, and Grounding JSON input now auto-detects
(`adapter: ethos-grounding-json`).

### 3.4 New surface introduced by 3.3 — **needs a ruling**

Routing `evidence anchor` through the shared loader means `--grounding ethos-json` is now accepted by
`verify` and `verify-batch` too, where it previously errored. It is additive and harmless, but it is
public CLI surface the prep document did not authorize. Either accept it in the ADR or move the
legacy spelling back into `evidence.rs`.

Known wart if accepted: `verify --grounding ethos-json --crop-dir X` fails with
"--crop-dir is currently supported only for native Ethos document grounding", which is confusing
because the caller *did* ask for native. The crop guard was deliberately left untouched.

### 3.5 Scope creep recommended for removal — **not yet actioned**

| Surface | Status | Recommendation |
| --- | --- | --- |
| `verify --source-artifact`, `verify-batch --source-artifact` | implemented | **Cut.** Prep §7.2 puts source binding on `grounding check` only; §8.1's flow is check-then-verify. Keeping it lets callers skip the check step the quickstart teaches. |
| npm `verifyClaims({ citations })` in-memory object | implemented | **Cut.** Not in prep §8.2. Writes a temp file on the caller's behalf. |
| npm `verifyClaims({ sourceArtifactPath })` | implemented | **Cut** with the above. |

---

## 4. What landed

### 4.1 Core and schemas (WP-1)

- `schemas/ethos-grounding-source.schema.json` and
  `schemas/ethos-grounding-validation-report.schema.json`, both `additionalProperties: false` at
  every boundary.
- `crates/ethos-core/src/grounding_json.rs` behind the existing `full` feature: a strict parser
  rejecting invalid UTF-8, BOM, duplicate keys at any depth before value construction, unknown
  fields, nulls, floats and exponent forms, unsafe integers, and every §6 invariant.
- Frozen limits in ADR-0016: 256 MiB input, 64 nesting levels, 5,000 pages, 1,000,000 elements or
  spans, 100,000 tables, 1,000,000 cells, 256-byte IDs, 16,384-byte strings.
- No new runtime dependency.

### 4.2 CLI (WP-2)

- Built-in `GroundingSource` implementation; adapter id `ethos-grounding-json`, version `1.0.0`.
- One shared loader used by `verify`, `verify-batch`, and `evidence anchor`.
- Exact artifact-type detection that fails closed (3.2).
- `ethos grounding check [--source-artifact <pdf>] [--out <file>]`, atomic and deterministic.
- No new Rust crate published.

### 4.3 Fixes applied during verification

- `crates/ethos-core/src/grounding_json.rs`: two `map_or(false, …)` → `is_some_and(…)` (clippy
  `unnecessary_map_or`); one `valid_bbox` ditto.
- `crates/ethos-core/src/grounding_json.rs:998`: removed a vestigial `.replace(x, x)` no-op flagged
  by `clippy::no_effect_replace`. The surrounding duplicate-page-id test was **not** broken — the
  second replace does the real work — so this is dead-code removal, not a behavior change.
- `crates/ethos-cli/src/cmd/grounding.rs`: removed dead `_stable_error`.
- **Two of the new integration tests were passing for the wrong reason.** They asserted stderr
  contained `artifact_type`, which the *native* loader also emits as `unknown field
  \`artifact_type\``. They now assert `unsupported top-level artifact_type`, so they cannot pass via
  the fallback path they exist to forbid.

### 4.4 npm and examples (WP-3)

- Generated `grounding-source.d.ts` and `grounding-validation-report.d.ts`.
- `checkGrounding` and `verifyClaims`, invoking the packaged binary with `spawn` and an argument
  array — never a shell string — with bounded stdout/stderr, timeout, `signal`, and temp cleanup.
- No verification, parsing, hashing, or report construction in production JavaScript.
- JavaScript and Python mapper examples over the same pinned parser output (2.6).

---

## 5. The parser-agnostic contract

This is what a third-party parser owner must satisfy. It is deliberately small, and it is the whole
public surface of this release.

Emit one JSON file:

```json
{
  "artifact_type": "ethos.grounding.v1",
  "schema_version": "1.0.0",
  "source":   { "media_type": "application/pdf", "sha256": "sha256:<64-hex>" },
  "producer": { "name": "your-parser", "version": "1.2.3" },
  "capabilities": { "spans": false, "char_offsets": false, "tables": false },
  "coordinate_system": { "unit": "centipoint", "origin": "top-left" },
  "pages":    [{ "id": "page-1", "index": 1, "width": 61200, "height": 79200, "rotation": 0 }],
  "elements": [{ "id": "block-17", "page": "page-1", "bbox": [7200, 8400, 54000, 10200],
                 "kind": "text_block", "text": "Revenue increased to $12.4 million." }]
}
```

Then:

```bash
ethos grounding check parser-grounding.json --source-artifact source.pdf --out validation.json
```

The mapper owns exactly three things, and Ethos will never do any of them for you:

1. **Stable IDs and reading order.** Element order is semantically significant. Ethos never
   generates or repairs IDs.
2. **Coordinate conversion.** Centipoints, top-left origin, integers only. Use
   `round_half_away_from_zero(points * 100)`. Ethos never guesses or silently converts units.
3. **Honest capability declarations.** `char_offsets` requires `spans`. Supplying spans or tables
   contradicting a `false` declaration is rejected. Ethos never upgrades a `false` declaration by
   inspecting a document.

### 5.1 Honest limits

- **Geometry is mandatory.** Page dimensions and element boxes are required because the released
  `GroundingSource` contract requires them. Text-only parsers cannot use this profile honestly.
  Do not submit page-sized boxes, zero boxes, or invented coordinates. Making geometry optional
  would reshape a public trait and needs its own compatibility decision — log blocked integrations
  instead (prep §6.6).
- **`producer` is unauthenticated.** It is a bounded declaration, not an identity.
- **A source-hash match proves only that the mapper declared the hash of the PDF you supplied.**
  It is not evidence that the parser extracted the PDF faithfully. Nothing in Ethos claims otherwise,
  and nothing built on Ethos should.
- **`grounded` is not truth.** It means a submitted literal claim matched recorded evidence. It says
  nothing about relevance, completeness, freshness, or business correctness.

---

## 6. Test matrix status against prep §11

| Area | Status |
| --- | --- |
| §11.1 Compatibility — native and OpenDataLoader inputs, report bytes, exits | **verified**, plus byte-identical evidence-anchor output across the default removal |
| §11.1 No field-name reclassification | **verified** — only top-level `artifact_type` is inspected |
| §11.2 Conformance — duplicates, unknown fields, identity, IDs, references, order, geometry, capabilities, offsets, tables, limits | **covered** by 12 core tests and 5 negative schema fixtures |
| §11.2 Emoji and combining-mark offset vectors | **gap** — Unicode is covered, but not these specific vectors |
| §11.3 Source binding — absent, matching, malformed, mismatching | **verified** (2.5) |
| §11.3 `not_checked` never rendered as `matched` | **verified** |
| §11.4 Validation report determinism | **verified** |
| §11.4 JavaScript and Python mapper determinism | **verified** (2.6) |
| §11.4 DocuShell mapper determinism | **outstanding** |
| §11.5 `spawn` receives an argument array, never a shell string | **verified by inspection** |
| §11.5 Timeout, cancellation, bounded output, typed exits | implemented; **not executable on this host** |
| §11.5 Unsupported platform fails before pretending verification ran | **fails untyped** (7.2) |
| §11.5 Clean Node project; clean Python environment | **not executable on this host** |
| §11.5 Clean-room developer completes the quickstart | **not yet run with a real developer** |

---

## 7. Open-source usability findings

These are adoption blockers in practice, and most are invisible in the prep document. All except
the platform-target decision itself have been addressed.

| # | Finding | Status |
| --- | --- | --- |
| 7.1 | PDFium-gated tests punished correct setup on unsupported hosts | **fixed** |
| 7.1 | Supported hosts undocumented | **fixed** — QUICKSTART "Supported hosts" |
| 7.2 | Unsupported-platform SDK error was untyped | **fixed** |
| 7.3 | Mapper examples had no documented invocation | **fixed** |
| 7.4 | Page-geometry sidecar was unexplained | **fixed** — QUICKSTART + mapper guide |
| 7.5 | `jsonschema` was an undeclared dev dependency | **fixed** — `requirements-dev.txt` |
| — | No end-to-end guide for non-Rust mapper authors | **added** — `docs/writing-a-mapper.md` |
| — | Adding a `macos-x64` PDFium pin | **open** — release-target decision |

### 7.1 `darwin:x64` is entirely unsupported — highest-impact finding

On an Intel Mac, today: the npm package refuses to run, PDFium is rejected as unverifiable, 25 tests
fail *because* you configured PDFium correctly, and `ethos doctor` reports
`packaged target: not listed in the v0.4 npm CLI package targets`.

The prep document discusses Windows at length and never mentions macOS x64. For an Apache-2.0
project asking third parties to write mappers, a contributor on an Intel Mac currently cannot run the
package tests or the PDF path at all.

Actions taken:

1. **PDFium-gated tests now skip rather than fail** when `ethos doctor` reports PDFium unusable
   (section 2.3). This removes the actively punishing first-run experience.
2. **Supported hosts are now stated explicitly** in the npm QUICKSTART, together with the
   build-from-source path that keeps the whole Grounding JSON workflow available on other hosts.

Still open, deliberately:

3. Whether to pin a `darwin:x64` PDFium hash. Upstream ships `pdfium-mac-x64.tgz` in the same
   `chromium/7881` release, and `current_platform_key()` in `crates/ethos-pdf/src/lib.rs` simply
   has no `macos-x64` arm — so this is a pinning-policy gap, not a technical limit. Adding it means
   a new arm plus entries in `platform_hashes`, `platform_artifacts`, `scripts/fetch-pdfium.sh`,
   and `docs/pdfium-profile.md`. **Hashes must come from the reviewed upstream release artifact,
   never from a locally observed file** — pinning a locally computed hash would launder an
   unverified download into the trust root. This is a release-target decision and must not block
   the adoption boundary.

The good news: **none of this touches the Grounding JSON path**, which needs no PDFium and worked
end-to-end on this unsupported host (2.5, 2.6, 2.7). That is the release thesis holding up.

### 7.2 Unsupported-platform failure is untyped

`resolveBinary()` throws a plain `Error`, not `EthosSdkError`, and it is called inside `execute`'s
try block. Prep §8.2 requires "one small typed SDK error" and §11.5 requires this exact case. The
practical effect is that `npm test` dies with an uncaught stack trace instead of asserting a typed
failure, which is why four suites never run (2.8).

### 7.3 Mapper examples have no documented invocation

Both mappers require three positional arguments:

```bash
node map-grounding.js parser-output.json page-metadata.json output.json
```

The quickstart describes what the mappers do but never shows this signature. Running them bare
prints a usage line and exits `2`. This cost real time during verification and will cost every
clean-room developer the same.

### 7.4 The `page-metadata.json` sidecar is the hardest undocumented concept

Grounding JSON requires page geometry. OpenDataLoader does not supply it, so the example mappers take
a separate page-metadata sidecar sourced from the PDF. **This is the single hardest part of writing a
mapper** — a new integrator's parser probably does not emit page dimensions either — and it is
currently implicit in the example rather than explained.

The quickstart needs a short section: where page geometry comes from, why Ethos requires it, and what
to do when your parser does not provide it (answer: get it from the PDF, or you cannot use this
profile honestly — see 5.1).

### 7.5 `jsonschema` is an undeclared dev dependency

`schemas/validate_examples.py` is wired into CI and the Makefile but fails locally with
`Python package 'jsonschema' is required`. There is no `requirements-dev.txt` or documented install
step. Contributors hit this immediately.

### 7.6 What is genuinely good

Worth preserving deliberately:

- **Error messages are excellent.** `invalid_bbox at /elements/0/bbox` plus
  `submit a positive bounding box within its page` is correctable without reading Ethos source.
- **The correction quickstart works exactly as written** (2.7). Rare, and worth protecting with a test.
- **Fail-closed behavior is consistent** — no repair of IDs, coordinates, order, capabilities, or
  hashes anywhere in the path.
- **The honest-limits framing** (5.1) is the project's real differentiator. Do not let it erode.

---

## 8. Release blockers

### Closed

- `v0-6-0-release-prep.md` is committed, with the dropped receipt-alternative link removed and
  supersession notes at §6.4 and §8.1. The README link resolves.
- ADR-0016 now freezes the 15 stable validation error codes as a public compatibility surface, and
  records the representation-versus-source hash rationale.
- The public-posture request records the decider's README acceptance, so the audit trail no longer
  contradicts itself.
- `docs/execution-status.md` has a v0.6.0 entry.
- All eight contract gates are green; the dead `test_roadmap_status.py` invocations are gone and
  `make milestone-d-grounding-source-contract` runs.
- PDFium-gated tests skip rather than fail on unsupported hosts.
- The unsupported-platform SDK error is typed and asserted.

### Open — decisions

1. **The fingerprint conflict (3.1).** Recommendation on record: keep the representation hash and
   correct prep §8.1. Nothing else should be built on top of this until it is ruled.
2. **Scope-creep surfaces (3.4, 3.5)** need a keep-or-cut ruling. Recommendation: cut
   `verify --source-artifact`, `verify-batch --source-artifact`, and the two extra npm
   `verifyClaims` options; accept `--grounding ethos-json` on verify and record it in the ADR.
3. **The performance-regression ceiling** (prep §12) is still unset. Note that the new path does
   not touch the existing verification path, so a bounded resource test on the new validator is
   the more meaningful measurement.
4. **The DocuShell acceptance commit** is not selected.

### Open — work

5. **Public version drift.** `docs/public-boundary-claims.json` and five docs still pin **0.4.0**
   install strings while the ledger says **0.5.0** is published, so users following the README
   install a version behind. Two gates are red on exactly this
   (`test_npm_binary_package_scaffold`, `test_package_registry_source_consistency`). Flagged in
   prep §4; WP-0 fixed only `execution-status.md`. This is a coordinated public-wording change
   across the claims registry and belongs in its own reviewed change, not folded into a feature
   branch. It is independent of Grounding JSON and should not wait for it.
6. **`npm test` end-to-end, the clean-room Node project, and the clean Python environment** have
   never completed on any host in this verification — `types.test.js` and `tsc` need a networked
   `npm install`. They must pass on macOS arm64 or Linux x64 before release.
7. **The clean-room quickstart must be walked by a developer who did not build this**, with no
   assistance. Prep §5.1 makes undocumented steps a release blocker. This is the only gate that
   tests the adoption thesis rather than the implementation. Sections 7.3 and 7.4 were already
   failures of it, found by walking the path rather than reading it; both are fixed, but the gate
   has not been run by an actual outsider.
8. Two pre-existing unrelated gate failures (`test_app_answer_release_release_prep`,
   `test_rag_framework_examples`) are still red.

Explicitly **not** blockers: Windows artifacts, receipts/proofs/replay, DocuShell commercial
outcomes, and a `darwin:x64` release target.

---

## 9. Non-goals, unchanged

Verification-report changes. Receipt, attestation, proof-package, signing, ledger, checkpoint, or
replay protocols. New PDF parsing behavior or parser-quality claims. New parser-specific adapters
beyond the existing OpenDataLoader adapter. Geometry-less or text-only profiles. Dynamic plugins,
WASM adapters, adapter marketplaces, or mapping DSLs. Automatic field inference, ID repair,
coordinate guessing, capability guessing, or source-hash repair. Non-PDF profiles. Search, indexing,
embeddings, RAG, answer generation, agents, semantic judgment, or workflow orchestration. A hosted
Ethos API or production positioning. A new npm package, Python public API, Rust public crate, or MCP
surface. Windows artifact publication. Pricing commitments, revenue claims, or any claim that
DocuShell monetization is proven.

---

## 10. After v0.6.0

The release thesis is that non-Rust parser owners will write mappers. Nothing in this repository
tests that yet: the only mapper authored against a real parser was written by the Ethos team, for
OpenDataLoader, with full knowledge of Ethos internals.

Two cheap ways to find out early:

- **Ship a mapper example for a parser with real users** — Docling, Marker, or a PyMuPDF pipeline.
  This is an example, not an adapter, so it stays inside the §5.3 exclusion on new parser-specific
  adapters. It is simultaneously proof, documentation, and the most credible marketing available.
- **Set a falsification metric now.** Suggested: three parties outside the team attempt a Grounding
  JSON mapper within 90 days of release. Count attempts, not completions — the friction logs from
  failures are worth more than the successes. If the number is zero, the adoption thesis is wrong
  and v0.7.0 should be something else, most likely revisiting the geometry requirement in 5.1.
