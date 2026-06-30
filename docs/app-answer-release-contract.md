# App Answer Release Contract

Status: source-only guidance for products, APIs, and UI layers that consume Ethos verification
reports.

This document defines how an application should decide what answer text it may show after Ethos
checks citation grounding. It does not add a new verifier status, JSON report field, command,
hosted API, parser adapter, or semantic judge.

## Boundary

Ethos answers one deterministic question:

```text
Do these caller-provided citations bind to source evidence exposed by a trusted GroundingSource?
```

The canonical audit artifact remains `verification_report.json`, governed by
`schemas/ethos-verification-report.schema.json`. Rust callers may derive
`VerificationReport::proof_summary()` and Python callers may derive `proof_summary(report)` for
product wording, reusable-check selection, and API wrapper policy. That derived summary is not a
replacement for the canonical report.

If a wrapper exposes `invalid_request`, that status is a process or API envelope for malformed
input, invalid configuration, adapter failure, or usage errors. It is not derived from a
`VerificationReport`.

## Three Axes

Application answer release decisions should keep three axes separate.

| Axis | Owner | Question |
| --- | --- | --- |
| Citation grounding | Ethos | Does the cited evidence ID, quote, value, table cell, or target exist and match the trusted source evidence? |
| Question relevance | Application | Does the grounded evidence actually answer or support the user's question? |
| Synthesis level | Application | Is the claim directly stated by the source, or is it an inference across multiple grounded facts? |

Ethos is strongest on citation grounding. It does not know the user's question unless a wrapper
adds that context above the verifier, and it does not silently convert grounded snippets into a
semantically complete answer.

## Grounding Status

Use the derived proof summary as the grounding axis only:

- `verified`: the submitted request is certified by `all_evidence_grounded`.
- `partially_verified`: some checks are reusable, but the request as submitted is not certified.
- `unverified`: no check is reusable.

Reusable grounded checks must satisfy all of these conditions:

- the check status is `grounded`;
- `semantic_unverified` is false;
- `fingerprint_stale` is false.

Capability limits and proof limitations must stay visible to users or downstream policy, but they
are not automatic proof failures by themselves. They describe what Ethos could not prove at the
available adapter/source fidelity.

## Application Labels

An application should label every generated claim before deciding whether to show it as final
answer text.

Suggested `question_relevance` values:

- `direct_answer`: the grounded evidence directly answers the user question.
- `supports_answer`: the grounded evidence is needed to support the answer but is not sufficient
  alone.
- `background_only`: the grounded evidence is true but not responsive to the question.
- `unrelated`: the grounded evidence does not support the requested answer.

Suggested `claim_type` values:

- `source_fact`: the claim is directly stated by source evidence.
- `synthesis`: the claim combines multiple grounded facts or adds reasoning across them.
- `unsupported`: the claim cannot be traced to grounded source evidence.

These labels may come from application policy, a reviewed model output schema, human review, or a
separate evaluator. They are outside the canonical Ethos verification report.

## Release Rules

A conservative first application policy is:

| App status | Rule | Default UI treatment |
| --- | --- | --- |
| `certified` | Citation grounding is true, `question_relevance` is `direct_answer` or `supports_answer`, and `claim_type` is `source_fact`. | Show in the final answer. |
| `partial_certified` | At least one claim is `certified`, and at least one requested claim is blocked or review-only. | Show only certified claims; disclose that the answer is partial. |
| `supported_synthesis_needs_review` | Citation grounding is true, `question_relevance` is `direct_answer` or `supports_answer`, and `claim_type` is `synthesis`. | Keep out of the main answer unless the product explicitly allows reviewed synthesis. |
| `grounded_but_irrelevant` | Citation grounding is true, but `question_relevance` is `background_only` or `unrelated`. | Block from the final answer. |
| `cannot_answer_from_sources` | No relevant grounded source facts are available. | Say that the sources do not support an answer. |

This preserves the strict Ethos rule that grounded citations are necessary, while avoiding the
separate failure mode where a true citation supports the wrong answer.

## Wrapper Requirements

Applications that use Ethos as a release gate should:

- build verification requests from trusted source maps or parser artifacts, not from model-returned
  citation IDs alone;
- pass the original user question into the application gate that labels relevance and synthesis;
- release final answer text from certified source facts by default;
- put synthesis in a separate review surface unless the product has an explicit synthesis policy;
- treat retrieval citations, chunks, and model-selected evidence IDs as candidates, not proof;
- keep `verification_report.json` available for audit even when a derived status is shown to users.

The user-facing copy should avoid saying "Ethos verified the answer" unless the application has
also checked relevance and synthesis. Safer wording is:

```text
Ethos verified citation grounding.
Answer relevance: direct, partial, or off-topic.
```

## Parser Neutrality

This contract is not DocuShell-specific. Any parser can participate when its output is adapted into
the parser-neutral `GroundingSource` boundary and the application supplies citation claims for
Ethos to check. The application still owns retrieval, question relevance, synthesis policy, and
final answer release.
