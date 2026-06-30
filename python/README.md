# Ethos Python Package

This directory contains the `ethos-pdf` Python package source for Ethos.

Install the published evaluation wheel from PyPI with:

```sh
python3 -m pip install ethos-pdf==0.2.0
```

`v0.2.0` adds JSON verification and evidence-anchor wrapper calls through a caller-provided
`ethos` CLI binary. The Python wheel does not bundle the CLI or PDFium.

The package exposes a public semver API beginning at `0.1.0` for Python `>=3.8`. Patch releases
must not break public function signatures, exception classes, or documented return shapes. Minor
releases may add backward-compatible API, and major releases may break API after a release-scope
decision.

Public API:

- `EthosCli`
- `EthosPythonSurfaceError`
- `EthosNotFoundError`
- `EthosTimeoutError`
- `EthosCommandError`
- `PdfiumNotFoundError`
- `InvalidPdfError`
- `CorruptPdfError`
- `ParseTimeoutError`
- `EthosOutputError`
- `parse_pdf_json`
- `parse_pdf_markdown`
- `parse_pdf_text`
- `crop_element`
- `verify`
- `proof_summary`
- `app_answer_release_decision`
- `anchor`

The current module is intentionally thin: it shells out to a caller-provided local `ethos` CLI
binary and returns `ethos doc parse` output, source-bound `ethos crop_element` JSON, `ethos verify`
JSON reports, or `ethos evidence anchor` JSON reports. It can pass caller-provided source PDF and
crop artifact directory arguments for rendered crop artifacts. It does not bundle PDFium, does not
publish hosted surfaces, and does not expand parser behavior. The Rust CLI remains the source of
truth.

The package name is historical continuity naming. JSON verification and evidence-anchor calls do
not require PDF parsing, but the package is still named `ethos-pdf`.

PDFium-backed parse and crop paths require caller-provided PDFium through
`ETHOS_PDFIUM_LIBRARY_PATH`. Importing `ethos_pdf` does not require PDFium. If PDFium is missing,
the wrapper raises `PdfiumNotFoundError` and preserves the underlying CLI stderr so callers can show
the setup guidance from `QUICKSTART.md` or `docs/pdfium-manual-setup.md`.

## Exceptions

All wrapper-owned exceptions inherit from `EthosPythonSurfaceError`.

Subprocess failures inherit from `EthosCommandError` and expose `command`, `returncode`, `stdout`,
and `stderr`. When the CLI emits its stable JSON error envelope on stderr, the wrapper maps by
`error.code`; otherwise it falls back to the documented exit code:

| CLI condition | Exit | Python exception |
| --- | ---: | --- |
| missing caller-provided PDFium | any non-zero exit with PDFium setup stderr | `PdfiumNotFoundError` |
| `invalid_pdf` | 3 | `InvalidPdfError` |
| `corrupt_pdf` | 4 | `CorruptPdfError` |
| `parse_timeout` | 10 | `ParseTimeoutError` |
| any other non-zero CLI exit | other | `EthosCommandError` |

Wrapper-side timeouts raised by `subprocess.run(..., timeout=...)` use `EthosTimeoutError`.
Missing input files raise Python `FileNotFoundError` before invoking the CLI.

## JSON Verify And Evidence Anchor

Use the `binary` constructor alias when a caller manages the CLI path explicitly:

```python
from ethos_pdf import EthosCli

ethos = EthosCli(binary="/path/to/ethos")

report = ethos.verify(
    source="source.ethos.json",
    citations="citations.json",
    grounding=None,
    config=None,
    fail_on_ungrounded=False,
    output_format="json",
    timeout=30,
)

anchor_report = ethos.anchor(
    source="source.ethos.json",
    evidence_refs="evidence_refs.json",
    grounding=None,
    output_format="json",
    timeout=30,
)
```

`verify(...)` maps `source` to the positional CLI input, maps `citations` to `--citations`, maps
`grounding` to an adapter id such as `opendataloader-json`, maps `config` to `--config`, and maps
`fail_on_ungrounded=True` to `--fail-on-ungrounded`.

`anchor(...)` maps `source` to the positional CLI input, maps `evidence_refs` to `--evidence-refs`,
and maps `grounding` to an adapter id. It does not expose a fail flag in the v0.2 preparation
surface. Non-bound evidence-anchor outcomes are returned as structured reports, not exceptions.

Verify exit semantics:

- exit `0` with JSON returns a report;
- exit `1` with JSON returns a negative verification report when `fail_on_ungrounded=True`;
- exit `>=2` raises `EthosCommandError` or a more specific subclass.

Use `proof_summary(report)` when a product or API wrapper needs the same derived status as the Rust
`VerificationReport::proof_summary()` helper:

```python
from ethos_pdf import EthosCli, proof_summary

ethos = EthosCli(binary="/path/to/ethos")
report = ethos.verify("source.ethos.json", citations="citations.json")
summary = proof_summary(report)
print(summary["proof_status"])
```

The summary is not a replacement for the canonical verification report. It deterministically
derives `proof_status`, `request_certified`, reusable grounded check ids, needs-review check ids,
and proof limitations from the report that `ethos verify` already emitted.

Use `app_answer_release_decision(...)` when an application has already labeled claim relevance and
synthesis, and wants the conservative release policy from `docs/app-answer-release-contract.md`:

```python
from ethos_pdf import app_answer_release_decision, proof_summary

summary = proof_summary(report)
decision = app_answer_release_decision(
    "What was Q3 2025 revenue?",
    summary,
    [
        {
            "id": "claim-revenue",
            "text": "Revenue grew to $12.4M in Q3 2025.",
            "check_ids": ["v0001"],
            "question_relevance": "direct_answer",
            "claim_type": "source_fact",
        }
    ],
)
print(decision["app_status"])
```

The helper does not judge relevance or synthesis. Callers supply those labels; the helper applies
the release rule and requires referenced Ethos check IDs to be reusable before a claim can enter
the final answer. It also rejects duplicate claim IDs so `final_answer_claim_ids`,
`review_claim_ids`, and `blocked_claim_ids` stay unambiguous.

Run the focused tests with:

```sh
make python-surface-test
```

The tests use a fake local command, so they do not require PDFium.
