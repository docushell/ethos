#!/usr/bin/env python3
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

import copy
import json
import unittest
from pathlib import Path

from security_report_validation import (
    FINDING_MESSAGE_TEMPLATES,
    SECURITY_WARNING_CODES,
    diagnose_security_report_example,
)


ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"


class SecurityReportValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads((EXAMPLES / "document.example.json").read_text())
        self.report = json.loads((EXAMPLES / "security-report.example.json").read_text())

    def test_current_examples_are_coherent(self) -> None:
        self.assertEqual(diagnose_security_report_example(self.document, self.report), [])

    def test_all_security_warning_codes_have_fixed_message_templates(self) -> None:
        self.assertEqual(set(FINDING_MESSAGE_TEMPLATES), SECURITY_WARNING_CODES)

    def test_schema_version_must_match_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["schema_version"] = "1.0.1"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: schema_version diverges from document example",
            diagnostics,
        )

    def test_document_fingerprint_must_match_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["document_fingerprint"] = "sha256:" + ("0" * 64)

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: document_fingerprint diverges from document example",
            diagnostics,
        )

    def test_source_fingerprint_must_match_document_source(self) -> None:
        report = copy.deepcopy(self.report)
        report["source_fingerprint"] = "sha256:" + ("0" * 64)

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: source_fingerprint diverges from document example",
            diagnostics,
        )

    def test_profile_identity_must_match_document_profile(self) -> None:
        report = copy.deepcopy(self.report)
        report["profile"]["id"] = "ethos-deterministic-v2"
        report["profile"]["sha256"] = "0" * 64

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: profile.id diverges from document example",
            diagnostics,
        )
        self.assertIn(
            "security-report.example.json: profile.sha256 diverges from document example",
            diagnostics,
        )

    def test_report_identity_scalar_fields_must_match_schema_patterns(self) -> None:
        cases = (
            (
                ("schema_version",),
                "1.0",
                r"security-report.example.json: schema_version must match "
                r"pattern ^[0-9]+\.[0-9]+\.[0-9]+$",
                "security-report.example.json: schema_version diverges from "
                "document example",
            ),
            (
                ("schema_version",),
                100,
                r"security-report.example.json: schema_version must match "
                r"pattern ^[0-9]+\.[0-9]+\.[0-9]+$",
                "security-report.example.json: schema_version diverges from "
                "document example",
            ),
            (
                ("document_fingerprint",),
                "sha256:" + ("g" * 64),
                "security-report.example.json: document_fingerprint must match "
                "pattern ^sha256:[0-9a-f]{64}$",
                "security-report.example.json: document_fingerprint diverges from "
                "document example",
            ),
            (
                ("document_fingerprint",),
                None,
                "security-report.example.json: document_fingerprint must match "
                "pattern ^sha256:[0-9a-f]{64}$",
                "security-report.example.json: document_fingerprint diverges from "
                "document example",
            ),
            (
                ("source_fingerprint",),
                "5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef",
                "security-report.example.json: source_fingerprint must match "
                "pattern ^sha256:[0-9a-f]{64}$",
                "security-report.example.json: source_fingerprint diverges from "
                "document example",
            ),
            (
                ("profile", "id"),
                "ethos-deterministic-v",
                "security-report.example.json: profile.id must match "
                "pattern ^ethos-deterministic-v[0-9]+$",
                "security-report.example.json: profile.id diverges from "
                "document example",
            ),
            (
                ("profile", "id"),
                None,
                "security-report.example.json: profile.id must match "
                "pattern ^ethos-deterministic-v[0-9]+$",
                "security-report.example.json: profile.id diverges from "
                "document example",
            ),
            (
                ("profile", "sha256"),
                "A" * 64,
                "security-report.example.json: profile.sha256 must match "
                "pattern ^[0-9a-f]{64}$",
                "security-report.example.json: profile.sha256 diverges from "
                "document example",
            ),
        )
        for path, value, expected_diagnostic, divergence_diagnostic in cases:
            with self.subTest(path=".".join(path)):
                report = copy.deepcopy(self.report)
                target = report
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(expected_diagnostic, diagnostics)
                self.assertNotIn(divergence_diagnostic, diagnostics)

    def test_report_must_be_object(self) -> None:
        diagnostics = diagnose_security_report_example(self.document, [])

        self.assertIn(
            "security-report.example.json: report must be an object",
            diagnostics,
        )

    def test_top_level_report_fields_are_required(self) -> None:
        identity_diagnostics = {
            "schema_version": "security-report.example.json: schema_version diverges from document example",
            "document_fingerprint": "security-report.example.json: document_fingerprint diverges from document example",
            "source_fingerprint": "security-report.example.json: source_fingerprint diverges from document example",
        }
        for field in (
            "schema_version",
            "document_fingerprint",
            "source_fingerprint",
            "profile",
            "summary",
            "findings",
            "inventories",
        ):
            with self.subTest(field=field):
                report = copy.deepcopy(self.report)
                report.pop(field)

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    f"security-report.example.json: {field} is required",
                    diagnostics,
                )
                if field in identity_diagnostics:
                    self.assertNotIn(identity_diagnostics[field], diagnostics)

    def test_finding_items_must_be_objects(self) -> None:
        for value in ("bad", [], None):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["findings"].append(value)

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: findings[3] must be an object",
                    diagnostics,
                )

    def test_profile_must_be_object(self) -> None:
        report = copy.deepcopy(self.report)
        report["profile"] = []

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: profile must be an object",
            diagnostics,
        )
        self.assertNotIn(
            "security-report.example.json: profile.id diverges from document example",
            diagnostics,
        )
        self.assertNotIn(
            "security-report.example.json: profile.sha256 diverges from document example",
            diagnostics,
        )

    def test_profile_fields_are_required(self) -> None:
        identity_diagnostics = {
            "id": "security-report.example.json: profile.id diverges from document example",
            "sha256": "security-report.example.json: profile.sha256 diverges from document example",
        }
        for field in ("id", "sha256"):
            with self.subTest(field=field):
                report = copy.deepcopy(self.report)
                report["profile"].pop(field)

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    f"security-report.example.json: profile.{field} is required",
                    diagnostics,
                )
                self.assertNotIn(identity_diagnostics[field], diagnostics)

    def test_unexpected_report_fields_fail_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["unexpected"] = True
        report["profile"]["unexpected"] = True

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: unexpected is not allowed",
            diagnostics,
        )
        self.assertIn(
            "security-report.example.json: profile.unexpected is not allowed",
            diagnostics,
        )

    def test_finding_ids_must_be_contiguous_in_report_order(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][1]["id"] = "f0004"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: findings[1].id must be f0002 "
            "for deterministic numbering",
            diagnostics,
        )

    def test_finding_ids_must_match_schema_pattern(self) -> None:
        for value in ("finding-1", "f001", "F0001", []):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["findings"][0]["id"] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: findings[0].id must match "
                    "pattern ^f[0-9]{4}$",
                    diagnostics,
                )
                self.assertNotIn(
                    "security-report.example.json: findings[0].id must be f0001 "
                    "for deterministic numbering",
                    diagnostics,
                )

    def test_finding_ids_must_be_unique(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][1]["id"] = "f0001"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: duplicate finding id f0001",
            diagnostics,
        )

    def test_finding_codes_must_be_security_report_codes(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"].append(
            {
                "id": "f0004",
                "code": "unknown_code",
                "message": "unknown",
                "page": "p0001",
                "excluded_from_default_chunks": False,
            }
        )

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0004 code unknown_code "
            "is not a security report code",
            diagnostics,
        )

    def test_finding_codes_are_required(self) -> None:
        for value in (None, 7):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                if value is None:
                    report["findings"][0].pop("code")
                else:
                    report["findings"][0]["code"] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: finding f0001 code is required",
                    diagnostics,
                )

    def test_finding_required_fields_must_be_present(self) -> None:
        expected_diagnostics = {
            "id": "security-report.example.json: findings[0].id is required",
            "message": "security-report.example.json: finding f0001.message is required",
            "excluded_from_default_chunks": (
                "security-report.example.json: "
                "finding f0001.excluded_from_default_chunks is required"
            ),
        }
        suppressed_diagnostics = {
            "id": "security-report.example.json: findings[0].id must be f0001 "
            "for deterministic numbering",
            "message": (
                "security-report.example.json: finding f0001 message must match "
                "fixed template for hidden_text_detected"
            ),
            "excluded_from_default_chunks": (
                "security-report.example.json: finding f0001 "
                "excluded_from_default_chunks must be true for hidden_text_detected"
            ),
        }
        suppressed_projection_diagnostics = (
            "security-report.example.json: missing warning-derived finding for hidden_text_detected",
            "security-report.example.json: finding f0001 has no matching "
            "security_warnings entry for hidden_text_detected",
        )

        for field in ("id", "message", "excluded_from_default_chunks"):
            with self.subTest(field=field):
                report = copy.deepcopy(self.report)
                report["findings"][0].pop(field)

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(expected_diagnostics[field], diagnostics)
                self.assertNotIn(suppressed_diagnostics[field], diagnostics)
                if field in ("message", "excluded_from_default_chunks"):
                    for diagnostic in suppressed_projection_diagnostics:
                        self.assertNotIn(diagnostic, diagnostics)

    def test_finding_string_fields_must_be_strings(self) -> None:
        cases = (
            (
                0,
                "message",
                7,
                "security-report.example.json: finding f0001.message must be a string",
                "security-report.example.json: finding f0001 message must match "
                "fixed template for hidden_text_detected",
            ),
            (
                0,
                "text_preview",
                ["internal-draft-do-not-cite"],
                "security-report.example.json: finding f0001.text_preview "
                "must be a string",
                "security-report.example.json: finding f0001 text_preview must match "
                "span_ref s000003 text",
            ),
        )
        for index, field, value, expected_diagnostic, suppressed_diagnostic in cases:
            with self.subTest(field=field, value=value):
                report = copy.deepcopy(self.report)
                report["findings"][index][field] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(expected_diagnostic, diagnostics)
                self.assertNotIn(suppressed_diagnostic, diagnostics)

    def test_unexpected_finding_fields_fail_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["unexpected"] = True

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001.unexpected is not allowed",
            diagnostics,
        )

    def test_hidden_text_finding_message_must_match_fixed_template(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["message"] = "hidden text changed"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 message must match "
            "fixed template for hidden_text_detected",
            diagnostics,
        )

    def test_security_warning_message_must_match_fixed_template(self) -> None:
        for code in sorted(SECURITY_WARNING_CODES):
            with self.subTest(code=code):
                document = copy.deepcopy(self.document)
                document["payload"]["security_warnings"].append(
                    {
                        "id": "w0099",
                        "code": code,
                        "message": "security warning changed",
                        "page": "p0001",
                    }
                )

                diagnostics = diagnose_security_report_example(document, self.report)

                self.assertIn(
                    "security-report.example.json: security warning w0099 message "
                    f"must match fixed template for {code}",
                    diagnostics,
                )

    def test_text_exclusion_finding_messages_must_match_fixed_templates(self) -> None:
        for code, changed_message in (
            ("off_page_text_detected", "off-page text changed"),
            ("low_contrast_text_detected", "low-contrast text changed"),
        ):
            with self.subTest(code=code):
                document = copy.deepcopy(self.document)
                document["payload"]["security_warnings"].append(
                    {
                        "id": "w0099",
                        "code": code,
                        "message": changed_message,
                        "page": "p0001",
                        "span_ref": "s000003",
                    }
                )
                report = copy.deepcopy(self.report)
                report["findings"].append(
                    {
                        "id": "f0004",
                        "code": code,
                        "message": changed_message,
                        "page": "p0001",
                        "span_ref": "s000003",
                        "bbox": [100, 79100, 6000, 79200],
                        "text_preview": "internal-draft-do-not-cite",
                        "excluded_from_default_chunks": True,
                    }
                )
                report["summary"][code] = 1

                diagnostics = diagnose_security_report_example(document, report)

                self.assertIn(
                    "security-report.example.json: finding f0004 message must match "
                    f"fixed template for {code}",
                    diagnostics,
                )

    def test_annotation_finding_message_must_match_fixed_template(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][1]["message"] = "annotations changed"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0002 message must match "
            "fixed template for annotations_present",
            diagnostics,
        )

    def test_external_link_finding_message_must_match_fixed_template(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][2]["message"] = "links changed"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0003 message must match "
            "fixed template for external_links_present",
            diagnostics,
        )

    def test_unsupported_annotation_finding_message_must_match_fixed_template(
        self,
    ) -> None:
        report = copy.deepcopy(self.report)
        report["findings"].append(
            {
                "id": "f0004",
                "code": "unsupported_annotation",
                "message": "unsupported annotation changed",
                "page": "p0001",
                "excluded_from_default_chunks": False,
            }
        )
        report["summary"]["unsupported_annotation"] = 1
        report["inventories"]["annotations"][0]["supported"] = False

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0004 message must match "
            "fixed template for unsupported_annotation",
            diagnostics,
        )

    def test_image_only_page_finding_message_must_match_fixed_template(self) -> None:
        document = copy.deepcopy(self.document)
        document["payload"]["security_warnings"].append(
            {
                "id": "w0099",
                "code": "image_only_page",
                "message": "image-only page changed",
                "page": "p0001",
            }
        )
        report = copy.deepcopy(self.report)
        report["findings"].append(
            {
                "id": "f0004",
                "code": "image_only_page",
                "message": "image-only page changed",
                "page": "p0001",
                "excluded_from_default_chunks": False,
            }
        )
        report["summary"]["image_only_page"] = 1

        diagnostics = diagnose_security_report_example(document, report)

        self.assertIn(
            "security-report.example.json: finding f0004 message must match "
            "fixed template for image_only_page",
            diagnostics,
        )

    def test_warning_derived_summary_must_match_document_warning_count(self) -> None:
        report = copy.deepcopy(self.report)
        report["summary"]["hidden_text_detected"] = 2

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: summary.hidden_text_detected must be 1 "
            "for warning-derived findings",
            diagnostics,
        )

    def test_summary_must_match_all_report_finding_counts(self) -> None:
        report = copy.deepcopy(self.report)
        report["summary"]["external_links_present"] = 2

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: summary.external_links_present must be 1 "
            "for report findings",
            diagnostics,
        )

    def test_summary_counts_must_be_non_negative_json_integers(self) -> None:
        for value in (True, "1", -1):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["summary"]["hidden_text_detected"] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: summary.hidden_text_detected "
                    "must be a non-negative integer",
                    diagnostics,
                )

    def test_zero_count_summary_keys_must_be_omitted(self) -> None:
        report = copy.deepcopy(self.report)
        report["summary"]["image_only_page"] = 0

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: summary.image_only_page must be omitted "
            "when no report findings use that code",
            diagnostics,
        )

    def test_unknown_summary_keys_fail_closed(self) -> None:
        for value in (0, 1):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["summary"]["unknown_code"] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: summary.unknown_code is not a security report code",
                    diagnostics,
                )

    def test_document_security_warnings_must_have_matching_findings(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"] = [
            finding
            for finding in report["findings"]
            if finding["code"] != "hidden_text_detected"
        ]
        report["summary"].pop("hidden_text_detected")

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: missing warning-derived finding for hidden_text_detected",
            diagnostics,
        )

    def test_stale_summary_without_matching_finding_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"] = [
            finding
            for finding in report["findings"]
            if finding["code"] != "external_links_present"
        ]

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: summary.external_links_present must be 0 "
            "for report findings",
            diagnostics,
        )

    def test_unexpected_warning_derived_report_finding_fails_closed(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"].append(
            {
                "id": "f0004",
                "code": "image_only_page",
                "message": "image-only page",
                "page": "p0001",
                "excluded_from_default_chunks": False,
            }
        )
        report["summary"]["image_only_page"] = 1

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0004 has no matching "
            "security_warnings entry for image_only_page",
            diagnostics,
        )

    def test_warning_refs_must_match_report_finding_projection(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["span_ref"] = "s999999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: missing warning-derived finding for hidden_text_detected",
            diagnostics,
        )

    def test_default_excluded_warning_codes_must_be_flagged(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["excluded_from_default_chunks"] = False

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: missing warning-derived finding for hidden_text_detected",
            diagnostics,
        )
        self.assertIn(
            "security-report.example.json: finding f0001 excluded_from_default_chunks "
            "must be true for hidden_text_detected",
            diagnostics,
        )

    def test_non_exclusion_finding_codes_must_not_be_default_excluded(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][1]["excluded_from_default_chunks"] = True

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0002 excluded_from_default_chunks "
            "must be false for annotations_present",
            diagnostics,
        )

    def test_excluded_from_default_chunks_must_be_boolean(self) -> None:
        for index, value in ((0, 1), (1, 0), (0, "true")):
            with self.subTest(index=index, value=value):
                report = copy.deepcopy(self.report)
                report["findings"][index]["excluded_from_default_chunks"] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                finding_id = report["findings"][index]["id"]
                self.assertIn(
                    f"security-report.example.json: finding {finding_id} "
                    "excluded_from_default_chunks must be a boolean",
                    diagnostics,
                )

    def test_finding_page_refs_must_exist_in_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][1]["page"] = "p9999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0002 references unknown page p9999",
            diagnostics,
        )

    def test_finding_page_refs_must_match_schema_pattern(self) -> None:
        for value in ("page-1", []):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["findings"][1]["page"] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: finding f0002.page must match "
                    "pattern ^p[0-9]{4}$",
                    diagnostics,
                )
                self.assertFalse(
                    any(
                        diagnostic.startswith(
                            "security-report.example.json: finding f0002 "
                            "references unknown page"
                        )
                        for diagnostic in diagnostics
                    )
                )

    def test_finding_element_refs_must_exist_in_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][1]["element_ref"] = "e999999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0002 references unknown element_ref e999999",
            diagnostics,
        )

    def test_finding_element_refs_must_match_schema_pattern(self) -> None:
        for value in ("element-1", []):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["findings"][1]["element_ref"] = value
                report["findings"][1]["span_ref"] = "s000003"

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: finding f0002.element_ref "
                    "must match pattern ^e[0-9]{6}$",
                    diagnostics,
                )
                self.assertFalse(
                    any(
                        diagnostic.startswith(
                            "security-report.example.json: finding f0002 "
                            "references unknown element_ref"
                        )
                        for diagnostic in diagnostics
                    )
                )
                self.assertFalse(
                    any(
                        "owned by element_ref" in diagnostic
                        for diagnostic in diagnostics
                    )
                )

    def test_finding_span_refs_must_exist_in_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["span_ref"] = "s999999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 references unknown span_ref s999999",
            diagnostics,
        )

    def test_finding_span_refs_must_match_schema_pattern(self) -> None:
        for value in ("span-1", []):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["findings"][0]["span_ref"] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: finding f0001.span_ref "
                    "must match pattern ^s[0-9]{6}$",
                    diagnostics,
                )
                self.assertFalse(
                    any(
                        diagnostic.startswith(
                            "security-report.example.json: finding f0001 "
                            "references unknown span_ref"
                        )
                        for diagnostic in diagnostics
                    )
                )

    def test_finding_span_refs_must_match_finding_page(self) -> None:
        document = copy.deepcopy(self.document)
        document["payload"]["pages"].append(
            {
                "id": "p0002",
                "index": 2,
                "width": 61200,
                "height": 79200,
                "rotation": 0,
            }
        )
        report = copy.deepcopy(self.report)
        report["findings"][0]["page"] = "p0002"

        diagnostics = diagnose_security_report_example(document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 span_ref s000003 page p0001 "
            "does not match page p0002",
            diagnostics,
        )

    def test_text_backed_finding_requires_span_ref(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0].pop("span_ref")

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 requires span_ref for "
            "hidden_text_detected",
            diagnostics,
        )

    def test_finding_span_ref_must_be_owned_by_element_ref_when_both_present(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["element_ref"] = "e000001"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 span_ref s000003 is not "
            "owned by element_ref e000001",
            diagnostics,
        )

    def test_finding_element_span_refs_must_be_deterministic_array(self) -> None:
        document = copy.deepcopy(self.document)
        document["payload"]["elements"][0]["span_refs"] = "s000001"
        report = copy.deepcopy(self.report)
        report["findings"][0]["element_ref"] = "e000001"

        diagnostics = diagnose_security_report_example(document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 element_ref e000001 "
            "span_refs must be an array",
            diagnostics,
        )

    def test_finding_bbox_must_have_page(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0].pop("page")

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 bbox requires page",
            diagnostics,
        )

    def test_finding_bbox_must_have_positive_area(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["bbox"][2] = report["findings"][0]["bbox"][0]

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 bbox has zero area",
            diagnostics,
        )

    def test_finding_bbox_rejects_boolean_coordinates(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["bbox"][0] = True

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 bbox must be four integer coordinates",
            diagnostics,
        )

    def test_finding_bbox_must_stay_inside_page_bounds(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["bbox"][2] = 61201

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 bbox exceeds page p0001 bounds",
            diagnostics,
        )

    def test_text_backed_finding_requires_span_bbox(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0].pop("bbox")

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 span_ref s000003 requires bbox",
            diagnostics,
        )

    def test_text_backed_finding_bbox_must_match_span_bbox(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["bbox"][0] = 101

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 bbox must match span_ref "
            "s000003 bbox",
            diagnostics,
        )

    def test_text_backed_finding_requires_text_preview(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0].pop("text_preview")

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 span_ref s000003 requires text_preview",
            diagnostics,
        )

    def test_text_backed_finding_preview_must_match_span_text(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][0]["text_preview"] = "internal-draft"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 text_preview must match "
            "span_ref s000003 text",
            diagnostics,
        )

    def test_text_backed_finding_preview_uses_deterministic_truncation(self) -> None:
        document = copy.deepcopy(self.document)
        span_text = "x" * 121
        document["payload"]["spans"][2]["text"] = span_text
        report = copy.deepcopy(self.report)
        report["findings"][0]["text_preview"] = "x" * 120

        diagnostics = diagnose_security_report_example(document, report)

        self.assertIn(
            "security-report.example.json: finding f0001 text_preview must match "
            "span_ref s000003 text",
            diagnostics,
        )

    def test_text_backed_finding_accepts_deterministic_truncated_preview(self) -> None:
        document = copy.deepcopy(self.document)
        span_text = "x" * 121
        document["payload"]["spans"][2]["text"] = span_text
        report = copy.deepcopy(self.report)
        report["findings"][0]["text_preview"] = ("x" * 120) + "\u2026"

        diagnostics = diagnose_security_report_example(document, report)

        self.assertNotIn(
            "security-report.example.json: finding f0001 text_preview must match "
            "span_ref s000003 text",
            diagnostics,
        )

    def test_annotations_inventory_requires_matching_finding(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"] = [
            finding
            for finding in report["findings"]
            if finding["code"] != "annotations_present"
        ]
        report["summary"].pop("annotations_present")

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.annotations requires annotations_present finding",
            diagnostics,
        )

    def test_annotations_finding_requires_inventory_entry(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["annotations"] = []

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: annotations_present finding requires "
            "inventories.annotations entry",
            diagnostics,
        )

    def test_unsupported_annotation_inventory_requires_matching_finding(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["annotations"][0]["supported"] = False

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.annotations supported=false "
            "requires unsupported_annotation finding",
            diagnostics,
        )

    def test_unsupported_annotation_finding_requires_inventory_entry(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"].append(
            {
                "id": "f0004",
                "code": "unsupported_annotation",
                "message": "unsupported annotation ignored",
                "page": "p0001",
                "excluded_from_default_chunks": False,
            }
        )
        report["summary"]["unsupported_annotation"] = 1

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: unsupported_annotation finding requires "
            "inventories.annotations supported=false entry",
            diagnostics,
        )

    def test_inventory_page_refs_must_exist_in_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["annotations"][0]["page"] = "p9999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.annotations[0] "
            "references unknown page p9999",
            diagnostics,
        )

    def test_inventory_page_refs_must_match_schema_pattern(self) -> None:
        cases = (
            ("annotations", "page-1"),
            ("actions", []),
            ("scripts", "1"),
            ("links", []),
        )
        for name, value in cases:
            with self.subTest(name=name, value=value):
                report = copy.deepcopy(self.report)
                if not report["inventories"][name]:
                    report["inventories"][name] = [{"location": "document"}]
                report["inventories"][name][0]["page"] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    f"security-report.example.json: inventories.{name}[0].page "
                    "must match pattern ^p[0-9]{4}$",
                    diagnostics,
                )
                self.assertFalse(
                    any(
                        diagnostic.startswith(
                            f"security-report.example.json: inventories.{name}[0] "
                            "references unknown page"
                        )
                        for diagnostic in diagnostics
                    )
                )

    def test_inventory_bbox_must_have_page(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["links"][0].pop("page")

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.links[0] bbox requires page",
            diagnostics,
        )

    def test_inventory_bbox_must_have_positive_area(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["links"][0]["bbox"][2] = report["inventories"]["links"][0][
            "bbox"
        ][0]

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.links[0] bbox has zero area",
            diagnostics,
        )

    def test_inventory_bbox_rejects_boolean_coordinates(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["links"][0]["bbox"][0] = True

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.links[0] bbox must be four "
            "integer coordinates",
            diagnostics,
        )

    def test_inventory_bbox_must_stay_inside_page_bounds(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["annotations"][0]["bbox"][3] = 79201

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.annotations[0] "
            "bbox exceeds page p0001 bounds",
            diagnostics,
        )

    def test_action_inventory_page_refs_are_checked_without_action_semantics(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["actions"][0]["page"] = "p9999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.actions[0] references unknown page p9999",
            diagnostics,
        )

    def test_external_link_inventory_requires_matching_finding(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"] = [
            finding
            for finding in report["findings"]
            if finding["code"] != "external_links_present"
        ]
        report["summary"].pop("external_links_present")

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.links external=true requires "
            "external_links_present finding",
            diagnostics,
        )

    def test_external_link_finding_requires_external_inventory_entry(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["links"][0]["external"] = False

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: external_links_present finding requires "
            "inventories.links external=true entry",
            diagnostics,
        )

    def test_inventory_shape_must_be_deterministic_arrays(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["links"] = {"page": "p0001"}

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.links must be an array",
            diagnostics,
        )

    def test_inventory_items_must_be_objects(self) -> None:
        for name in ("annotations", "actions", "attachments", "scripts", "links"):
            with self.subTest(name=name):
                report = copy.deepcopy(self.report)
                report["inventories"][name] = ["bad"]

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    f"security-report.example.json: inventories.{name}[0] "
                    "must be an object",
                    diagnostics,
                )

    def test_required_inventory_lanes_must_be_present(self) -> None:
        for name in ("annotations", "actions", "attachments", "scripts", "links"):
            with self.subTest(name=name):
                report = copy.deepcopy(self.report)
                report["inventories"].pop(name)

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    f"security-report.example.json: inventories.{name} is required",
                    diagnostics,
                )

    def test_unexpected_inventory_fields_fail_closed(self) -> None:
        inventory_items = {
            "annotations": {"page": "p0001", "kind": "link"},
            "actions": {"kind": "uri"},
            "attachments": {"name": "attachment.bin", "bytes": 0},
            "scripts": {"location": "document"},
            "links": {"page": "p0001", "uri": "https://example.com/q3", "external": True},
        }
        report = copy.deepcopy(self.report)
        report["inventories"]["widgets"] = []
        for name, item in inventory_items.items():
            report["inventories"][name] = [copy.deepcopy(item)]
            report["inventories"][name][0]["unexpected"] = True

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.widgets is not allowed",
            diagnostics,
        )
        for name in inventory_items:
            with self.subTest(name=name):
                self.assertIn(
                    f"security-report.example.json: inventories.{name}[0].unexpected "
                    "is not allowed",
                    diagnostics,
                )

    def test_required_inventory_item_fields_must_be_present(self) -> None:
        inventory_items = {
            "annotations": {"page": "p0001", "kind": "link"},
            "actions": {"kind": "uri"},
            "attachments": {"name": "attachment.bin", "bytes": 0},
            "scripts": {"location": "document"},
            "links": {"page": "p0001", "uri": "https://example.com/q3", "external": True},
        }
        required_fields = {
            "annotations": ("page", "kind"),
            "actions": ("kind",),
            "attachments": ("name", "bytes"),
            "scripts": ("location",),
            "links": ("page", "uri", "external"),
        }

        for name, fields in required_fields.items():
            for field in fields:
                with self.subTest(name=name, field=field):
                    report = copy.deepcopy(self.report)
                    report["inventories"][name] = [copy.deepcopy(inventory_items[name])]
                    report["inventories"][name][0].pop(field)

                    diagnostics = diagnose_security_report_example(self.document, report)

                    self.assertIn(
                        f"security-report.example.json: inventories.{name}[0].{field} "
                        "is required",
                        diagnostics,
                    )

    def test_attachment_inventory_bytes_must_be_non_negative_json_integer(self) -> None:
        for value in (True, False, "1", 1.0, -1):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["inventories"]["attachments"] = [
                    {"name": "attachment.bin", "bytes": value}
                ]

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: inventories.attachments[0].bytes "
                    "must be a non-negative integer",
                    diagnostics,
                )

    def test_inventory_string_fields_must_be_strings(self) -> None:
        inventory_items = {
            "annotations": {"page": "p0001", "kind": "link"},
            "actions": {"kind": "uri", "target": "https://example.com/q3"},
            "attachments": {"name": "attachment.bin", "bytes": 0},
            "scripts": {"location": "document", "trigger": "open"},
            "links": {"page": "p0001", "uri": "https://example.com/q3", "external": True},
        }
        cases = (
            ("annotations", "kind", 7),
            ("actions", "kind", False),
            ("actions", "target", ["https://example.com/q3"]),
            ("attachments", "name", None),
            ("scripts", "trigger", 7),
            ("links", "uri", ["https://example.com/q3"]),
        )
        for name, field, value in cases:
            with self.subTest(name=name, field=field, value=value):
                report = copy.deepcopy(self.report)
                report["inventories"][name] = [copy.deepcopy(inventory_items[name])]
                report["inventories"][name][0][field] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    f"security-report.example.json: inventories.{name}[0].{field} "
                    "must be a string",
                    diagnostics,
                )

    def test_attachment_inventory_sha256_must_be_lowercase_hex_digest(self) -> None:
        for value in ("abc", "g" * 64, "A" * 64, 64, None):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["inventories"]["attachments"] = [
                    {"name": "attachment.bin", "bytes": 0, "sha256": value}
                ]

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: inventories.attachments[0].sha256 "
                    "must be a 64-character lowercase hex digest",
                    diagnostics,
                )

    def test_attachment_inventory_sha256_accepts_lowercase_hex_digest(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["attachments"] = [
            {"name": "attachment.bin", "bytes": 0, "sha256": "a" * 64}
        ]

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertNotIn(
            "security-report.example.json: inventories.attachments[0].sha256 "
            "must be a 64-character lowercase hex digest",
            diagnostics,
        )

    def test_inventory_boolean_fields_must_be_boolean(self) -> None:
        cases = (
            ("annotations", "supported", 1),
            ("annotations", "supported", "false"),
            ("links", "external", 1),
            ("links", "external", "true"),
        )
        for name, field, value in cases:
            with self.subTest(name=name, field=field, value=value):
                report = copy.deepcopy(self.report)
                report["inventories"][name][0][field] = value

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    f"security-report.example.json: inventories.{name}[0].{field} "
                    "must be a boolean",
                    diagnostics,
                )

    def test_script_inventory_location_must_be_supported(self) -> None:
        for value in ("widget", "", 7, None, [], {}):
            with self.subTest(value=value):
                report = copy.deepcopy(self.report)
                report["inventories"]["scripts"] = [{"location": value}]

                diagnostics = diagnose_security_report_example(self.document, report)

                self.assertIn(
                    "security-report.example.json: inventories.scripts[0].location "
                    "must be a supported script location",
                    diagnostics,
                )

    def test_action_inventory_shape_is_checked_without_action_semantics(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["actions"] = {"kind": "uri"}

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.actions must be an array",
            diagnostics,
        )

    def test_inventories_must_be_deterministic_object(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"] = []

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories must be an object",
            diagnostics,
        )

    def test_security_codes_in_parser_warnings_fail_closed(self) -> None:
        document = copy.deepcopy(self.document)
        document["payload"]["parser_warnings"].append(
            {
                "id": "w0099",
                "code": "image_only_page",
                "message": "image-only page requires OCR",
                "page": "p0001",
            }
        )

        diagnostics = diagnose_security_report_example(document, self.report)

        self.assertIn(
            "security-report.example.json: parser warning w0099 (image_only_page) "
            "must be in security_warnings",
            diagnostics,
        )
        self.assertNotIn(
            "security-report.example.json: missing warning-derived finding for image_only_page",
            diagnostics,
        )
        self.assertNotIn(
            "security-report.example.json: security warning w0099 message must "
            "match fixed template for image_only_page",
            diagnostics,
        )

    def test_parser_codes_in_security_warnings_fail_closed(self) -> None:
        document = copy.deepcopy(self.document)
        document["payload"]["security_warnings"].append(
            {
                "id": "w0099",
                "code": "low_confidence_reading_order",
                "message": "parser warning placed in security lane",
                "page": "p0001",
            }
        )

        diagnostics = diagnose_security_report_example(document, self.report)

        self.assertIn(
            "security-report.example.json: security warning w0099 "
            "(low_confidence_reading_order) is not a security warning code",
            diagnostics,
        )


if __name__ == "__main__":
    unittest.main()
