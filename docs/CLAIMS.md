# What an Ethos Verdict Proves — and What It Does Not

Status: active. This document is the answer to "what exactly are you claiming?", written so
it can be handed to a security review without a conversation attached.

The honesty rule: Ethos proves that **cited evidence exists where a citation says it does,
in a representation Ethos read**. It proves nothing about whether the answer is true,
relevant, complete, or authorised, and nothing about whether the representation faithfully
reflects the original document.

---

## 1. What a verdict proves

| Claim | Mechanism | Where it lives |
| --- | --- | --- |
| The cited quote, value, table cell, or page exists in the source representation | Literal matching against the resolved locator target; no similarity scores, no thresholds | `ethos-verify` `resolve_target`, `text_check` |
| The same inputs produce the same verdict, byte for byte, forever | Canonical JSON (c14n v1), integer quantisation, pinned profile; CI asserts byte equality on every run | `ethos-core::c14n`, `determinism.yml` |
| The citation was checked against the current representation, not a stale one | Source fingerprint compared with the citation's declared fingerprint | `fingerprint_stale` |
| Exactly what Ethos could **not** establish | Capability declarations drive explicit downgrades; a missing capability is stated, never approximated | `capability_limits`, `status: capability_blocked` with `evidence_tier` absent |
| How precisely each claim was bound | Set where the target resolves, so it cannot drift from locator precedence | `evidence_tier` |
| What produced the verdict | Verifier crate name and version, config label, and a hash over the exact parsed claims | `attestation` |
| Which artifact the verdict concerns | SHA-256 of the bytes Ethos read, in a form a consumer holding the same file can recompute | `subject[0].digest` |
| Anyone can re-run it with no key, no account, and no network | Verification is a pure function; the base tree bans network-capable crates and CI proves zero egress | `deny.toml`, `no-network-runtime` CI job |

---

## 2. What a verdict does not prove

State these too. Every one is a real limit, not a caveat.

| Not proven | Why | What would close it |
| --- | --- | --- |
| That the claim is **true**, relevant, or complete | Ethos never sees the user's question and makes no semantic judgement. A quote can be exact and the answer still misleading. | Application-layer review; the four-axis split in `docs/app-answer-release-contract.md` assigns relevance, synthesis, and claim support to the application |
| That the **representation faithfully reflects the document** | Ethos verifies a claim against the representation, not the representation against the source. A parser error that both drafts and verifies consistently is invisible. | Reviewer inspection of a rendered crop; independently derived parsers compared against each other, analysed and deliberately cut in `docs/proof-statement-v1.md` §7 — revisiting it needs a measured divergence rate on real documents, not a threat model |
| That the named verifier binary actually ran | `attestation` records the crate name and version, which are compile-time constants. A hostile operator can write anything there. | Reproducible builds and signed release provenance; out of scope |
| That `subject[0]` is the original document | `subject[0]` is the artifact Ethos read. On the Grounding JSON path that is a parser's output, and Ethos never opened the PDF. | `--crop-source-pdf`, where Ethos loads and validates real PDF bytes. A producer-declared source hash is a declaration, never a binding (`docs/proof-statement-v1.md` §1.4) |
| That two runs of the same question agree | Each verification is independent. Ethos never compares across runs, and a model that rewords its answer produces different claims and so a different verdict. | Application-layer stability measurement; Ethos being fixed is what makes model variance measurable at all |
| That a **paraphrase** of a true fact is grounded | Matching is literal after a pinned normalisation profile — whitespace collapse, or the opt-in `unicode_compat_v1` fold table (curly quotes, dashes, ligatures), which maps characters, never words. "We may approve" and "we will approve" are different strings under every profile. | Pointer-first citation emission, so the model cites an element id and never retypes evidence (`docs/citation-emission-spec.md`) |
| That coverage was complete | A page that failed to process yields an explicit limitation. Absence of a check is never a pass. | Nothing in Ethos; the limitation is the honest output |
| Any speed, footprint, or parser-quality property | No benchmark has been run whose numbers we would defend | A published harness with its corpus named |

---

## 3. Mapping to the questions a review asks

Conservative on purpose. Ethos is a control, not a compliance programme.

| Regime | The question it asks | What Ethos answers | Residual gap — say it |
| --- | --- | --- | --- |
| EU AI Act Art. 12 | Are events recorded traceably? | Each verdict is a self-describing, reproducible record naming its inputs and the verifier that produced it | Ethos is invoked, not ambient. It records the checks you ask for, and logging that you asked is the caller's job |
| ISO/IEC 42001 | Is there a control over AI output quality? | A deterministic, independently re-runnable check on document-grounded claims | One control, not a management system. Governance, roles, and lifecycle sit outside |
| SR 11-7 (model risk) | Can a decision be validated and reproduced? | Same inputs and verifier version reproduce the verdict byte for byte; the artifact names all three | Ethos validates a citation, not a model. It says nothing about model fitness |
| FRE 902(14) | Is the record self-authenticating? | Not yet at this tier | Signing is out of scope for v0.6. The artifact shape reserves the envelope so signatures add without a format change |
| SOC 2 CC7.2 | Is there monitoring with reliable evidence? | Verdicts are stable evidence a reviewer can re-derive | Ethos is not monitoring and raises no alerts |

---

## 4. The paragraph to paste into a questionnaire

> For each document-grounded claim, Ethos produces a deterministic verdict recording whether
> the cited evidence exists in the source representation, how precisely it was bound, what
> it could not establish, and which verifier version and configuration produced the result.
> The same inputs reproduce the same verdict byte for byte, offline, with no key, account,
> or network access, so any party can re-derive it independently. Ethos does not judge
> whether an answer is true, relevant, or complete, and it verifies claims against the
> parsed representation rather than verifying that representation against the original
> document. Signing and hardware-rooted provenance are not claimed.

---

## 5. Proof tiers

| Tier | What it means | Key required | Status |
| --- | --- | --- | --- |
| **T0 Reproducible** | Anyone re-runs the verdict and gets identical bytes | no | shipped |
| **T1 Attested** | The verdict names the verifier, config, and exact claims that produced it | no | shipped |
| **T2 Signed** | A named key asserts who ran it and when | yes | not built |

T0 is the strongest of the three and the easiest to misread as the weakest. A signature says
*someone claimed this*. Reproducibility says *check it yourself*. T2 adds accountability for
who ran the check; it adds nothing to whether the check was right.
