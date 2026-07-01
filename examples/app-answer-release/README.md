# App Answer Release Demo

This demo is an offline reference path for applications that use Ethos grounding before deciding
which answer claims can be released.

It shows this flow:

```text
verification-report.json
-> proof_summary(...)
-> app-labeled claims
-> app_answer_release_decision(...)
-> final / review / blocked claim lists
```

The demo does not call an LLM, does not use DocuShell UI code, and does not ask Ethos to judge
question relevance or synthesis. Ethos derives the grounding summary. The application supplies the
original question plus `question_relevance` and `claim_type` labels.

## Run

From the repo root:

```sh
python3 examples/app-answer-release/run_python_demo.py --check
```

The command prints the decision envelope and exits non-zero if it differs from
`expected-decision.json`.

## Files

- `verification-report.json`: canonical Ethos-style grounding report used as the audit artifact.
- `proof-summary.json`: expected output from `proof_summary(verification_report)`.
- `claims.json`: application-owned question, relevance labels, and synthesis labels.
- `expected-decision.json`: expected app release envelope from `app_answer_release_decision(...)`.
- `run_python_demo.py`: copyable Python reference path.

## Cases Covered

- `claim-revenue`: certified source fact, released into the final answer.
- `claim-growth-driver`: grounded synthesis, kept for review.
- `claim-office-background`: grounded but irrelevant, blocked.
- `claim-margin`: unsupported by reusable grounded evidence, blocked.
