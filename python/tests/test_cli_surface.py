#
# Copyright 2026 The Ethos maintainers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import annotations

import os
import stat
import tempfile
import textwrap
import unittest
from pathlib import Path

from ethos_pdf import (
    CorruptPdfError,
    EthosCli,
    EthosCommandError,
    EthosNotFoundError,
    EthosOutputError,
    EthosTimeoutError,
    InvalidPdfError,
    ParseTimeoutError,
    PdfiumNotFoundError,
    anchor,
    app_answer_release_decision,
    crop_element,
    parse_pdf_json,
    proof_summary,
    verify,
)


FAKE_ETHOS = """\
#!/usr/bin/env python3
import json
import os
import sys
import time

mode = os.environ.get("ETHOS_FAKE_MODE", "ok")
if mode == "fail":
    sys.stdout.write("partial output\\n")
    sys.stderr.write("usage: fake ethos failure\\n")
    raise SystemExit(2)
if mode == "sleep":
    time.sleep(10)
    raise SystemExit(0)
if mode == "invalid-json":
    sys.stdout.write("not-json\\n")
    raise SystemExit(0)
if mode == "missing-pdfium":
    sys.stderr.write(
        "PDFium not found: set ETHOS_PDFIUM_LIBRARY_PATH to the caller-provided PDFium dynamic library path. Run ethos doctor for setup diagnostics, run ethos doctor --require-pdfium after setting it, and see docs/pdfium-manual-setup.md.\\n"
    )
    raise SystemExit(1)
if mode == "invalid-pdf":
    sys.stderr.write("invalid_pdf: not a PDF\\n")
    raise SystemExit(3)
if mode == "invalid-pdf-envelope":
    sys.stderr.write(json.dumps({"error": {"code": "invalid_pdf", "message": "not a PDF"}}) + "\\n")
    raise SystemExit(3)
if mode == "corrupt-pdf":
    sys.stderr.write("corrupt_pdf: broken xref\\n")
    raise SystemExit(4)
if mode == "parse-timeout":
    sys.stderr.write("parse_timeout: parse exceeded wall-time limit\\n")
    raise SystemExit(10)

if sys.argv[1:2] == ["crop_element"]:
    if "--request" not in sys.argv or "--check-id" not in sys.argv:
        sys.stderr.write("missing crop arguments\\n")
        raise SystemExit(2)
    sys.stdout.write(
        json.dumps(
            {
                "artifact_type": "ethos.crop_descriptor.v1",
                "argv": sys.argv[1:],
                "ok": True,
            },
            sort_keys=True,
        )
        + "\\n"
    )
    raise SystemExit(0)

if sys.argv[1:2] == ["verify"]:
    if "--citations" not in sys.argv or "--format" not in sys.argv:
        sys.stderr.write("missing verify arguments\\n")
        raise SystemExit(2)
    all_grounded = mode != "verify-negative"
    sys.stdout.write(
        json.dumps(
            {
                "artifact_type": "ethos.verification_report.v1",
                "all_evidence_grounded": all_grounded,
                "argv": sys.argv[1:],
                "ok": True,
            },
            sort_keys=True,
        )
        + "\\n"
    )
    raise SystemExit(1 if mode == "verify-negative" else 0)

if sys.argv[1:3] == ["evidence", "anchor"]:
    if "--evidence-refs" not in sys.argv:
        sys.stderr.write("missing evidence anchor arguments\\n")
        raise SystemExit(2)
    sys.stdout.write(
        json.dumps(
            {
                "artifact_type": "ethos.evidence_anchor_report.v1",
                "anchors": [
                    {
                        "anchor_status": "not_found"
                        if mode == "anchor-non-bound"
                        else "bound"
                    }
                ],
                "argv": sys.argv[1:],
                "ok": True,
            },
            sort_keys=True,
        )
        + "\\n"
    )
    raise SystemExit(0)

if sys.argv[1:3] != ["doc", "parse"]:
    sys.stderr.write("unexpected command\\n")
    raise SystemExit(2)

output_format = "json"
if "--format" in sys.argv:
    output_format = sys.argv[sys.argv.index("--format") + 1]

if output_format == "json":
    sys.stdout.write(json.dumps({"argv": sys.argv[1:], "ok": True}, sort_keys=True) + "\\n")
elif output_format == "markdown":
    sys.stdout.write("# Alpha\\n\\nTrust loop\\n")
elif output_format == "text":
    sys.stdout.write("Alpha trust loop\\n")
else:
    sys.stderr.write("unsupported format\\n")
    raise SystemExit(2)
"""


class PythonSurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.fake_ethos = self.root / "ethos"
        self.fake_ethos.write_text(textwrap.dedent(FAKE_ETHOS), encoding="utf-8")
        self.fake_ethos.chmod(
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP
        )
        self.pdf = self.root / "document.pdf"
        self.pdf.write_bytes(b"%PDF-1.7\n")
        self.document = self.root / "document.ethos.json"
        self.document.write_text("{}", encoding="utf-8")
        self.citations = self.root / "citations.json"
        self.citations.write_text("[]", encoding="utf-8")
        self.config = self.root / "verification-config.json"
        self.config.write_text("{}", encoding="utf-8")
        self.evidence_refs = self.root / "evidence-refs.json"
        self.evidence_refs.write_text(
            '{"artifact_type":"ethos.evidence_anchor_request.v1","evidence_refs":[]}',
            encoding="utf-8",
        )
        self.crop_request = self.root / "crop-request.json"
        self.crop_request.write_text("{}", encoding="utf-8")
        self.crop_source_pdf = self.root / "source.pdf"
        self.crop_source_pdf.write_bytes(b"%PDF-1.7\n")
        self.crop_dir = self.root / "crops"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_parse_pdf_json_invokes_doc_parse_with_pages_and_diagnostics(self) -> None:
        result = parse_pdf_json(
            self.pdf,
            ethos_bin=self.fake_ethos,
            pages="1-2",
            diagnostics=True,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["argv"],
            [
                "doc",
                "parse",
                str(self.pdf),
                "--format",
                "json",
                "--pages",
                "1-2",
                "--diagnostics",
            ],
        )

    def test_constructor_accepts_binary_alias(self) -> None:
        result = EthosCli(binary=self.fake_ethos).parse_pdf_json(self.pdf)

        self.assertTrue(result["ok"])

    def test_constructor_rejects_binary_and_ethos_bin_together(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos, binary=self.fake_ethos)

    def test_parse_pdf_text_preserves_cli_stdout(self) -> None:
        result = EthosCli(self.fake_ethos).parse_pdf_text(self.pdf)

        self.assertEqual(result, "Alpha trust loop\n")

    def test_parse_pdf_markdown_preserves_cli_stdout(self) -> None:
        result = EthosCli(self.fake_ethos).parse_pdf_markdown(self.pdf)

        self.assertEqual(result, "# Alpha\n\nTrust loop\n")

    def test_command_failure_raises_with_exit_code_and_streams(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "fail"})

        with self.assertRaises(EthosCommandError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertEqual(caught.exception.returncode, 2)
        self.assertIn("partial output", caught.exception.stdout)
        self.assertIn("fake ethos failure", caught.exception.stderr)

    def test_missing_pdfium_setup_error_is_specific_and_preserves_stderr(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "missing-pdfium"})

        with self.assertRaises(PdfiumNotFoundError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertIsInstance(caught.exception, EthosCommandError)
        self.assertEqual(caught.exception.returncode, 1)
        self.assertIn("PDFium not found", caught.exception.stderr)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", caught.exception.stderr)
        self.assertIn("ethos doctor", caught.exception.stderr)
        self.assertIn("ethos doctor --require-pdfium", caught.exception.stderr)
        self.assertIn("docs/pdfium-manual-setup.md", caught.exception.stderr)

    def test_invalid_pdf_exit_code_maps_to_specific_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-pdf"})

        with self.assertRaises(InvalidPdfError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertIsInstance(caught.exception, EthosCommandError)
        self.assertEqual(caught.exception.returncode, 3)

    def test_stable_error_envelope_maps_to_specific_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-pdf-envelope"})

        with self.assertRaises(InvalidPdfError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertIn('"code": "invalid_pdf"', caught.exception.stderr)

    def test_corrupt_pdf_exit_code_maps_to_specific_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "corrupt-pdf"})

        with self.assertRaises(CorruptPdfError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertEqual(caught.exception.returncode, 4)

    def test_parse_timeout_exit_code_maps_to_specific_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "parse-timeout"})

        with self.assertRaises(ParseTimeoutError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertEqual(caught.exception.returncode, 10)

    def test_missing_binary_raises_not_found(self) -> None:
        cli = EthosCli(self.root / "missing-ethos")

        with self.assertRaises(EthosNotFoundError):
            cli.parse_pdf_json(self.pdf)

    def test_timeout_raises_timeout_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "sleep"})

        with self.assertRaises(EthosTimeoutError):
            cli.parse_pdf_json(self.pdf, timeout_seconds=0.01)

    def test_invalid_format_is_rejected_before_command_execution(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).parse_pdf(self.pdf, output_format="html")

    def test_empty_pages_is_rejected_before_command_execution(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).parse_pdf_json(self.pdf, pages="")

    def test_non_positive_timeout_is_rejected_before_command_execution(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).parse_pdf_json(self.pdf, timeout_seconds=0)

    def test_missing_input_pdf_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            EthosCli(self.fake_ethos).parse_pdf_json(self.root / "missing.pdf")

    def test_invalid_json_stdout_raises_output_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-json"})

        with self.assertRaises(EthosOutputError) as caught:
            cli.parse_pdf_json(self.pdf)

        self.assertIn("invalid JSON", str(caught.exception))
        self.assertEqual(caught.exception.stdout, "not-json\n")

    def test_crop_element_invokes_descriptor_cli_with_request_and_check_id(self) -> None:
        result = crop_element(
            self.document,
            self.crop_request,
            ethos_bin=self.fake_ethos,
            check_id="v0002",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["artifact_type"], "ethos.crop_descriptor.v1")
        self.assertEqual(
            result["argv"],
            [
                "crop_element",
                str(self.document),
                "--request",
                str(self.crop_request),
                "--check-id",
                "v0002",
            ],
        )

    def test_crop_element_method_uses_default_check_id(self) -> None:
        result = EthosCli(self.fake_ethos).crop_element(self.document, self.crop_request)

        self.assertEqual(result["argv"][-2:], ["--check-id", "v0001"])

    def test_crop_element_rejects_empty_check_id_before_command_execution(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).crop_element(
                self.document,
                self.crop_request,
                check_id="",
            )

    def test_crop_element_missing_request_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            EthosCli(self.fake_ethos).crop_element(
                self.document,
                self.root / "missing-request.json",
            )

    def test_crop_element_invalid_json_stdout_raises_output_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-json"})

        with self.assertRaises(EthosOutputError) as caught:
            cli.crop_element(self.document, self.crop_request)

        self.assertIn("invalid JSON", str(caught.exception))
        self.assertEqual(caught.exception.stdout, "not-json\n")

    def test_crop_element_passes_rendered_artifact_arguments(self) -> None:
        result = EthosCli(self.fake_ethos).crop_element(
            self.document,
            self.crop_request,
            crop_source_pdf=self.crop_source_pdf,
            crop_dir=self.crop_dir,
        )

        self.assertEqual(
            result["argv"][-4:],
            [
                "--crop-source-pdf",
                str(self.crop_source_pdf),
                "--crop-dir",
                str(self.crop_dir),
            ],
        )

    def test_crop_element_rejects_partial_rendered_arguments(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).crop_element(
                self.document,
                self.crop_request,
                crop_source_pdf=self.crop_source_pdf,
            )

    def test_verify_maps_source_citations_grounding_config_and_fail_flag(self) -> None:
        result = verify(
            self.document,
            citations=self.citations,
            ethos_bin=self.fake_ethos,
            grounding="opendataloader-json",
            config=self.config,
            fail_on_ungrounded=True,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["argv"],
            [
                "verify",
                str(self.document),
                "--citations",
                str(self.citations),
                "--grounding",
                "opendataloader-json",
                "--config",
                str(self.config),
                "--fail-on-ungrounded",
                "--format",
                "json",
            ],
        )

    def test_verify_exit_one_with_json_returns_negative_result(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "verify-negative"})

        result = cli.verify(
            self.document,
            citations=self.citations,
            fail_on_ungrounded=True,
        )

        self.assertFalse(result["all_evidence_grounded"])

    def test_verify_exit_one_without_fail_flag_raises_command_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "verify-negative"})

        with self.assertRaises(EthosCommandError) as caught:
            cli.verify(self.document, citations=self.citations)

        self.assertEqual(caught.exception.returncode, 1)
        self.assertIn("ethos.verification_report.v1", caught.exception.stdout)

    def test_verify_exit_two_raises_command_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "fail"})

        with self.assertRaises(EthosCommandError) as caught:
            cli.verify(self.document, citations=self.citations)

        self.assertEqual(caught.exception.returncode, 2)

    def test_verify_invalid_json_stdout_raises_output_error(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "invalid-json"})

        with self.assertRaises(EthosOutputError):
            cli.verify(self.document, citations=self.citations)

    def test_verify_rejects_non_json_format(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).verify(
                self.document,
                citations=self.citations,
                output_format="summary",
            )

    def test_proof_summary_keeps_capability_limit_visible_without_failing_certified_request(
        self,
    ) -> None:
        report = {
            "all_evidence_grounded": True,
            "fingerprint_stale": False,
            "capability_limits": ["missing_fingerprint"],
            "unsupported_claim_kinds": [],
            "warnings": ["capability_limited"],
            "checks": [
                {
                    "id": "v0001",
                    "status": "grounded",
                    "semantic_unverified": False,
                    "warnings": [],
                }
            ],
        }

        result = proof_summary(report)

        self.assertEqual(result["proof_status"], "verified")
        self.assertTrue(result["request_certified"])
        self.assertEqual(result["reusable_grounded_check_ids"], ["v0001"])
        self.assertEqual(result["needs_review_check_ids"], [])
        self.assertEqual(result["proof_limitations"], ["capability_limited"])

    def test_proof_summary_marks_mixed_report_as_partially_verified(self) -> None:
        report = {
            "all_evidence_grounded": False,
            "fingerprint_stale": False,
            "capability_limits": [],
            "unsupported_claim_kinds": ["region"],
            "warnings": [],
            "checks": [
                {
                    "id": "v0001",
                    "status": "grounded",
                    "semantic_unverified": False,
                    "warnings": [],
                },
                {
                    "id": "v0002",
                    "status": "unsupported_claim_kind",
                    "semantic_unverified": False,
                    "warnings": [],
                },
            ],
        }

        result = proof_summary(report)

        self.assertEqual(result["proof_status"], "partially_verified")
        self.assertFalse(result["request_certified"])
        self.assertEqual(result["reusable_grounded_check_ids"], ["v0001"])
        self.assertEqual(result["needs_review_check_ids"], ["v0002"])
        self.assertEqual(
            result["proof_limitations"],
            ["unsupported_claim_kind", "non_grounded_checks"],
        )

    def test_proof_summary_excludes_stale_and_semantic_grounded_checks(self) -> None:
        stale_report = {
            "all_evidence_grounded": False,
            "fingerprint_stale": True,
            "capability_limits": [],
            "unsupported_claim_kinds": [],
            "warnings": [],
            "checks": [
                {
                    "id": "v0001",
                    "status": "grounded",
                    "semantic_unverified": False,
                    "warnings": [],
                }
            ],
        }
        semantic_report = {
            "all_evidence_grounded": False,
            "fingerprint_stale": False,
            "capability_limits": [],
            "unsupported_claim_kinds": [],
            "warnings": [],
            "checks": [
                {
                    "id": "v0001",
                    "status": "grounded",
                    "semantic_unverified": True,
                    "warnings": [],
                }
            ],
        }

        stale = proof_summary(stale_report)
        semantic = proof_summary(semantic_report)

        self.assertEqual(stale["proof_status"], "unverified")
        self.assertEqual(stale["reusable_grounded_check_ids"], [])
        self.assertEqual(stale["needs_review_check_ids"], ["v0001"])
        self.assertEqual(stale["proof_limitations"], ["stale_fingerprint"])
        self.assertEqual(semantic["proof_status"], "unverified")
        self.assertEqual(semantic["reusable_grounded_check_ids"], [])
        self.assertEqual(semantic["needs_review_check_ids"], ["v0001"])
        self.assertEqual(semantic["proof_limitations"], ["semantic_unverified"])

    def test_app_answer_release_decision_applies_relevance_and_synthesis_policy(
        self,
    ) -> None:
        summary = {
            "proof_status": "partially_verified",
            "request_certified": False,
            "reusable_grounded_check_ids": ["v0001", "v0002", "v0003"],
            "needs_review_check_ids": ["v0004"],
            "proof_limitations": ["non_grounded_checks"],
        }

        result = app_answer_release_decision(
            "What was Q3 2025 revenue?",
            summary,
            [
                {
                    "id": "claim-revenue",
                    "text": "Revenue grew to $12.4M in Q3 2025.",
                    "check_ids": ["v0001"],
                    "question_relevance": "direct_answer",
                    "claim_type": "source_fact",
                },
                {
                    "id": "claim-background",
                    "text": "The company opened a European office.",
                    "check_ids": ["v0002"],
                    "question_relevance": "background_only",
                    "claim_type": "source_fact",
                },
                {
                    "id": "claim-synthesis",
                    "text": "Revenue growth was likely driven by enterprise expansion.",
                    "check_ids": ["v0001", "v0003"],
                    "question_relevance": "supports_answer",
                    "claim_type": "synthesis",
                },
                {
                    "id": "claim-margin",
                    "text": "Gross margin improved in Q3 2025.",
                    "check_ids": ["v0004"],
                    "question_relevance": "direct_answer",
                    "claim_type": "unsupported",
                },
            ],
            verification_report_ref="reports/q3-verification.json",
            notes=["application-owned relevance labels"],
        )

        self.assertEqual(
            result["artifact_type"],
            "ethos.app_answer_release_decision.v1",
        )
        self.assertEqual(result["app_status"], "partial_certified")
        self.assertEqual(result["grounding"]["verification_report_ref"], "reports/q3-verification.json")
        self.assertEqual(result["final_answer_claim_ids"], ["claim-revenue"])
        self.assertEqual(result["review_claim_ids"], ["claim-synthesis"])
        self.assertEqual(result["blocked_claim_ids"], ["claim-background", "claim-margin"])
        self.assertEqual(result["claims"][0]["release_reason"], "certified")
        self.assertEqual(result["claims"][0]["check_ids"], ["v0001"])
        self.assertTrue(result["claims"][0]["citation_grounded"])
        self.assertEqual(result["claims"][1]["release_reason"], "grounded_but_irrelevant")
        self.assertEqual(result["claims"][2]["release_action"], "needs_review")
        self.assertEqual(result["claims"][2]["check_ids"], ["v0001", "v0003"])
        self.assertFalse(result["claims"][3]["citation_grounded"])
        self.assertEqual(result["claims"][3]["release_reason"], "cannot_answer_from_sources")
        self.assertEqual(result["notes"], ["application-owned relevance labels"])

    def test_app_answer_release_decision_accepts_verification_report(self) -> None:
        report = {
            "all_evidence_grounded": True,
            "fingerprint_stale": False,
            "capability_limits": [],
            "unsupported_claim_kinds": [],
            "warnings": [],
            "checks": [
                {
                    "id": "v0001",
                    "status": "grounded",
                    "semantic_unverified": False,
                    "warnings": [],
                }
            ],
        }

        result = app_answer_release_decision(
            "What was Q3 2025 revenue?",
            report,
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

        self.assertEqual(result["app_status"], "certified")
        self.assertEqual(result["grounding"]["proof_status"], "verified")
        self.assertEqual(result["final_answer_claim_ids"], ["claim-revenue"])

    def test_app_answer_release_decision_blocks_empty_source_answer(self) -> None:
        summary = {
            "proof_status": "unverified",
            "request_certified": False,
            "reusable_grounded_check_ids": [],
            "needs_review_check_ids": [],
            "proof_limitations": [],
        }

        result = app_answer_release_decision(
            "What was Q3 2025 revenue?",
            summary,
            [],
        )

        self.assertEqual(result["app_status"], "cannot_answer_from_sources")
        self.assertEqual(result["final_answer_claim_ids"], [])
        self.assertEqual(result["review_claim_ids"], [])
        self.assertEqual(result["blocked_claim_ids"], [])

    def test_app_answer_release_decision_rejects_inconsistent_or_unknown_checks(
        self,
    ) -> None:
        summary = {
            "proof_status": "partially_verified",
            "request_certified": False,
            "reusable_grounded_check_ids": ["v0001"],
            "needs_review_check_ids": ["v0002"],
            "proof_limitations": ["non_grounded_checks"],
        }

        with self.assertRaises(ValueError):
            app_answer_release_decision(
                "What was Q3 2025 revenue?",
                summary,
                [
                    {
                        "id": "claim-bad",
                        "text": "Revenue grew.",
                        "check_ids": ["v0001"],
                        "citation_grounded": False,
                        "question_relevance": "direct_answer",
                        "claim_type": "source_fact",
                    }
                ],
            )

        with self.assertRaises(ValueError):
            app_answer_release_decision(
                "What was Q3 2025 revenue?",
                summary,
                [
                    {
                        "id": "claim-unknown",
                        "text": "Revenue grew.",
                        "check_ids": ["v9999"],
                        "question_relevance": "direct_answer",
                        "claim_type": "source_fact",
                    }
                ],
            )

    def test_app_answer_release_decision_rejects_duplicate_claim_ids(self) -> None:
        summary = {
            "proof_status": "partially_verified",
            "request_certified": False,
            "reusable_grounded_check_ids": ["v0001", "v0002"],
            "needs_review_check_ids": [],
            "proof_limitations": [],
        }

        with self.assertRaisesRegex(ValueError, "duplicate claim id: claim-revenue"):
            app_answer_release_decision(
                "What was Q3 2025 revenue?",
                summary,
                [
                    {
                        "id": "claim-revenue",
                        "text": "Revenue grew.",
                        "check_ids": ["v0001"],
                        "question_relevance": "direct_answer",
                        "claim_type": "source_fact",
                    },
                    {
                        "id": "claim-revenue",
                        "text": "Revenue increased.",
                        "check_ids": ["v0002"],
                        "question_relevance": "supports_answer",
                        "claim_type": "source_fact",
                    },
                ],
            )

    def test_anchor_maps_source_evidence_refs_and_grounding(self) -> None:
        result = anchor(
            self.document,
            evidence_refs=self.evidence_refs,
            ethos_bin=self.fake_ethos,
            grounding="opendataloader-json",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["argv"],
            [
                "evidence",
                "anchor",
                str(self.document),
                "--evidence-refs",
                str(self.evidence_refs),
                "--grounding",
                "opendataloader-json",
            ],
        )
        self.assertNotIn("--fail-on-ungrounded", result["argv"])

    def test_anchor_non_bound_report_returns_without_exception(self) -> None:
        cli = EthosCli(self.fake_ethos, env={"ETHOS_FAKE_MODE": "anchor-non-bound"})

        result = cli.anchor(self.document, evidence_refs=self.evidence_refs)

        self.assertEqual(result["anchors"][0]["anchor_status"], "not_found")

    def test_anchor_rejects_non_json_format(self) -> None:
        with self.assertRaises(ValueError):
            EthosCli(self.fake_ethos).anchor(
                self.document,
                evidence_refs=self.evidence_refs,
                output_format="summary",
            )


if __name__ == "__main__":
    unittest.main()
