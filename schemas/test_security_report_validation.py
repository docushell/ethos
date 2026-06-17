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

from security_report_validation import diagnose_security_report_example


ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"


class SecurityReportValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads((EXAMPLES / "document.example.json").read_text())
        self.report = json.loads((EXAMPLES / "security-report.example.json").read_text())

    def test_current_examples_are_coherent(self) -> None:
        self.assertEqual(diagnose_security_report_example(self.document, self.report), [])

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

    def test_finding_page_refs_must_exist_in_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][1]["page"] = "p9999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0002 references unknown page p9999",
            diagnostics,
        )

    def test_finding_element_refs_must_exist_in_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["findings"][1]["element_ref"] = "e999999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: finding f0002 references unknown element_ref e999999",
            diagnostics,
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

    def test_inventory_page_refs_must_exist_in_document(self) -> None:
        report = copy.deepcopy(self.report)
        report["inventories"]["annotations"][0]["page"] = "p9999"

        diagnostics = diagnose_security_report_example(self.document, report)

        self.assertIn(
            "security-report.example.json: inventories.annotations[0] "
            "references unknown page p9999",
            diagnostics,
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

    def test_reportable_parser_warning_codes_are_included_when_present(self) -> None:
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
            "security-report.example.json: missing warning-derived finding for image_only_page",
            diagnostics,
        )


if __name__ == "__main__":
    unittest.main()
