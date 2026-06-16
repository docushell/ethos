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

import json
import tempfile
import unittest
from pathlib import Path

from evaluate_layout_alpha import canonical_json_bytes, evaluate_layout_alpha


class LayoutEvaluatorAlphaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_passing_fixture_set_reports_counts_and_coverage(self) -> None:
        self.write_required_alpha_fixture_set()

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["fixtures_evaluated"], 6)
        self.assertEqual(
            report["element_type_counts"],
            {"heading": 1, "list_item": 2, "text_block": 6},
        )
        self.assertEqual(
            report["coverage"],
            {
                "heading_fixture": ["heading-case"],
                "hyphenation_fixture": ["hyphen-case"],
                "ligature_fixture": ["ligature-case"],
                "list_item_fixture": ["list-case"],
                "multi_column_reading_order_fixture": ["column-case"],
                "rotation_fixture": ["rotation-case"],
            },
        )
        heading_check = next(
            check for check in report["checks"] if check["fixture_id"] == "heading-case"
        )
        self.assertEqual(heading_check["expected_pages"], "not_declared")
        self.assertEqual(heading_check["expected_span_text"], "not_declared")
        self.assertEqual(heading_check["confidence_policy"], "pass")
        self.assertEqual(heading_check["warning_shape"], "pass")
        self.assertEqual(
            heading_check["export_goldens"],
            {"markdown": "pass", "text": "pass"},
        )
        hyphen_check = next(
            check for check in report["checks"] if check["fixture_id"] == "hyphen-case"
        )
        self.assertEqual(hyphen_check["expected_pages"], "pass")
        self.assertEqual(hyphen_check["expected_span_text"], "pass")
        ligature_check = next(
            check for check in report["checks"] if check["fixture_id"] == "ligature-case"
        )
        self.assertEqual(ligature_check["expected_pages"], "pass")
        self.assertEqual(ligature_check["expected_span_text"], "pass")
        rotation_check = next(
            check for check in report["checks"] if check["fixture_id"] == "rotation-case"
        )
        self.assertEqual(rotation_check["expected_rotation"], "pass")
        self.assertEqual(report["diagnostics"], [])

    def test_missing_expected_text_fails_closed(self) -> None:
        self.write_required_alpha_fixture_set()
        metadata_path = self.root / "synthetic/heading-case/fixture.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.pop("expected_text")
        self.write_json(metadata_path, metadata)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "missing_expectation", "heading-case")

    def test_expected_text_drift_reports_expected_and_actual(self) -> None:
        self.write_required_alpha_fixture_set()
        metadata_path = self.root / "synthetic/column-case/fixture.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["expected_text"] = ["Right column", "Left column"]
        self.write_json(metadata_path, metadata)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        diagnostic = self.onlyDiagnostic(report, "expected_text_mismatch", "column-case")
        self.assertEqual(diagnostic["expected"], ["Right column", "Left column"])
        self.assertEqual(diagnostic["actual"], ["Left column", "Right column"])

    def test_expected_pages_drift_reports_expected_and_actual(self) -> None:
        self.write_required_alpha_fixture_set()
        metadata_path = self.root / "synthetic/hyphen-case/fixture.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["expected_pages"] = 2
        self.write_json(metadata_path, metadata)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        diagnostic = self.onlyDiagnostic(
            report,
            "expected_pages_mismatch",
            "hyphen-case",
        )
        self.assertEqual(diagnostic["expected"], 2)
        self.assertEqual(diagnostic["actual"], 1)
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_expected_pages_rejects_invalid_expectation(self) -> None:
        self.write_required_alpha_fixture_set()
        metadata_path = self.root / "synthetic/hyphen-case/fixture.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["expected_pages"] = -1
        self.write_json(metadata_path, metadata)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "invalid_expectation", "hyphen-case")
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_expected_span_text_drift_reports_expected_and_actual(self) -> None:
        self.write_required_alpha_fixture_set()
        extraction_path = self.root / "synthetic/hyphen-case/extraction.json"
        extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
        extraction["spans"][1]["text"] = "wrong"
        self.write_json(extraction_path, extraction)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        diagnostic = self.onlyDiagnostic(
            report,
            "expected_span_text_mismatch",
            "hyphen-case",
        )
        self.assertEqual(diagnostic["expected"], ["hyphen", "ated"])
        self.assertEqual(diagnostic["actual"], ["hyphen", "wrong"])
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_expected_span_text_rejects_invalid_expectation(self) -> None:
        self.write_required_alpha_fixture_set()
        metadata_path = self.root / "synthetic/ligature-case/fixture.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["expected_span_text"] = ["office", 17]
        self.write_json(metadata_path, metadata)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "invalid_expectation", "ligature-case")
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_expected_span_text_rejects_non_string_extraction_text(self) -> None:
        self.write_required_alpha_fixture_set()
        extraction_path = self.root / "synthetic/ligature-case/extraction.json"
        extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
        extraction["spans"][0]["text"] = 17
        self.write_json(extraction_path, extraction)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "invalid_extraction", "ligature-case")
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_heading_subset_requires_heading_element(self) -> None:
        self.write_required_alpha_fixture_set()
        layout_path = self.root / "synthetic/heading-case/layout.json"
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        layout["elements"][0]["type"] = "text_block"
        self.write_json(layout_path, layout)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "subset_expectation_mismatch", "heading-case")
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_list_subset_requires_list_item_element(self) -> None:
        self.write_required_alpha_fixture_set()
        layout_path = self.root / "synthetic/list-case/layout.json"
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        for element in layout["elements"]:
            element["type"] = "text_block"
        self.write_json(layout_path, layout)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "subset_expectation_mismatch", "list-case")
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_multi_column_fixture_requires_multi_element_expected_text(self) -> None:
        self.write_required_alpha_fixture_set()
        metadata_path = self.root / "synthetic/column-case/fixture.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["expected_text"] = "Left column Right column"
        self.write_json(metadata_path, metadata)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "expected_text_mismatch", "column-case")
        self.assertDiagnostic(report, "subset_expectation_mismatch", "column-case")
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_low_confidence_element_requires_matching_warning(self) -> None:
        self.write_required_alpha_fixture_set()
        layout_path = self.root / "synthetic/heading-case/layout.json"
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        layout["elements"][0].pop("warning_refs")
        layout["warnings"] = []
        self.write_json(layout_path, layout)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        diagnostic = self.onlyDiagnostic(
            report,
            "confidence_policy_mismatch",
            "heading-case",
        )
        self.assertEqual(
            diagnostic["expected"],
            {
                "code": "low_confidence_reading_order",
                "element_ref": "e000001",
            },
        )
        self.assertEqual(
            diagnostic["actual"],
            {
                "confidence": 720,
                "warning_refs": [],
            },
        )

    def test_export_golden_drift_reports_expected_and_actual(self) -> None:
        self.write_required_alpha_fixture_set()
        export_path = self.root / "synthetic/heading-case/markdown.md"
        export_path.write_text("Alpha Heading\n\nBody text\n", encoding="utf-8")

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        diagnostic = self.onlyDiagnostic(
            report,
            "export_golden_mismatch",
            "heading-case",
        )
        self.assertEqual(diagnostic["path"], "synthetic/heading-case/markdown.md")
        self.assertEqual(diagnostic["expected"], "# Alpha Heading\n\nBody text\n")
        self.assertEqual(diagnostic["actual"], "Alpha Heading\n\nBody text\n")

    def test_dangling_warning_ref_fails_closed(self) -> None:
        self.write_required_alpha_fixture_set()
        layout_path = self.root / "synthetic/list-case/layout.json"
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        layout["elements"][0]["warning_refs"] = ["w9999"]
        self.write_json(layout_path, layout)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        diagnostic = self.onlyDiagnostic(
            report,
            "warning_ref_mismatch",
            "list-case",
        )
        self.assertEqual(diagnostic["expected"], [])
        self.assertEqual(diagnostic["actual"], "w9999")

    def test_rotation_subset_requires_expected_rotation(self) -> None:
        self.write_required_alpha_fixture_set()
        metadata_path = self.root / "synthetic/rotation-case/fixture.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.pop("expected_rotation")
        self.write_json(metadata_path, metadata)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "missing_expectation", "rotation-case")
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_rotation_expectation_rejects_non_integer_values(self) -> None:
        self.write_required_alpha_fixture_set()
        metadata_path = self.root / "synthetic/rotation-case/fixture.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["expected_rotation"] = False
        self.write_json(metadata_path, metadata)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "invalid_expectation", "rotation-case")
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_rotation_expectation_matches_extraction_pages(self) -> None:
        self.write_required_alpha_fixture_set()
        extraction_path = self.root / "synthetic/rotation-case/extraction.json"
        extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
        extraction["pages"][0]["rotation"] = 0
        self.write_json(extraction_path, extraction)

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        diagnostic = self.onlyDiagnostic(
            report,
            "expected_rotation_mismatch",
            "rotation-case",
        )
        self.assertEqual(diagnostic["expected"], [90])
        self.assertEqual(diagnostic["actual"], [0])
        self.assertDiagnostic(report, "missing_coverage", None)

    def test_missing_layout_file_reports_missing_file(self) -> None:
        self.write_required_alpha_fixture_set()
        (self.root / "synthetic/list-case/layout.json").unlink()

        report = evaluate_layout_alpha(self.root)

        self.assertEqual(report["status"], "fail")
        self.assertDiagnostic(report, "missing_file", "list-case")

    def test_report_is_canonical_json_serializable(self) -> None:
        self.write_required_alpha_fixture_set()
        report = evaluate_layout_alpha(self.root)

        encoded = canonical_json_bytes(report)
        expected = json.dumps(
            report,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8") + b"\n"

        self.assertEqual(encoded, expected)

    def assertDiagnostic(
        self,
        report,
        code: str,
        fixture_id: str | None,
    ) -> None:
        self.onlyDiagnostic(report, code, fixture_id)

    def onlyDiagnostic(
        self,
        report,
        code: str,
        fixture_id: str | None,
    ):
        matches = [
            diagnostic
            for diagnostic in report["diagnostics"]
            if diagnostic["code"] == code and diagnostic.get("fixture_id") == fixture_id
        ]
        self.assertLessEqual(len(matches), 1, f"multiple diagnostics matched {code}")
        self.assertTrue(matches, f"missing diagnostic {code} for {fixture_id}")
        return matches[0]

    def write_required_alpha_fixture_set(self) -> None:
        entries = [
            self.write_fixture(
                fixture_id="heading-case",
                fixture_path="synthetic/heading-case/document.pdf",
                subsets=["born_digital", "headings"],
                expected_text=["Alpha Heading", "Body text"],
                expected_element_types=["heading", "text_block"],
                elements=[
                    {
                        "id": "e000001",
                        "type": "heading",
                        "text": "Alpha Heading",
                        "confidence": 720,
                        "warning_refs": ["w0001"],
                    },
                    {"id": "e000002", "type": "text_block", "text": "Body text"},
                ],
                warnings=[
                    {
                        "id": "w0001",
                        "code": "low_confidence_reading_order",
                        "message": "layout confidence below alpha threshold",
                        "page": "p0001",
                        "element_ref": "e000001",
                    }
                ],
            ),
            self.write_fixture(
                fixture_id="list-case",
                fixture_path="synthetic/list-case/document.pdf",
                subsets=["born_digital", "lists"],
                expected_text=["- First", "2. Second"],
                expected_element_types=["list_item", "list_item"],
                elements=[
                    {"id": "e000001", "type": "list_item", "text": "- First"},
                    {"id": "e000002", "type": "list_item", "text": "2. Second"},
                ],
            ),
            self.write_fixture(
                fixture_id="column-case",
                fixture_path="synthetic/column-case/document.pdf",
                subsets=["born_digital", "multi_column"],
                expected_text=["Left column", "Right column"],
                expected_element_types=["text_block", "text_block"],
                elements=[
                    {"id": "e000001", "type": "text_block", "text": "Left column"},
                    {"id": "e000002", "type": "text_block", "text": "Right column"},
                ],
            ),
            self.write_fixture(
                fixture_id="rotation-case",
                fixture_path="synthetic/rotation-case/document.pdf",
                subsets=["born_digital", "rotation"],
                expected_text=["Rotate Ninety"],
                expected_element_types=["text_block"],
                elements=[
                    {"id": "e000001", "type": "text_block", "text": "Rotate Ninety"},
                ],
                expected_rotation=90,
                page_rotation=90,
            ),
            self.write_fixture(
                fixture_id="hyphen-case",
                fixture_path="synthetic/hyphen-case/document.pdf",
                subsets=["born_digital", "hyphenation", "fonts"],
                expected_text=["hyphen ated"],
                expected_element_types=["text_block"],
                elements=[
                    {"id": "e000001", "type": "text_block", "text": "hyphen ated"},
                ],
                expected_pages=1,
                expected_span_text=["hyphen", "ated"],
                spans=[
                    {"id": "s000001", "text": "hyphen"},
                    {"id": "s000002", "text": "ated"},
                ],
            ),
            self.write_fixture(
                fixture_id="ligature-case",
                fixture_path="synthetic/ligature-case/document.pdf",
                subsets=["born_digital", "fonts", "ligatures"],
                expected_text=["office file"],
                expected_element_types=["text_block"],
                elements=[
                    {"id": "e000001", "type": "text_block", "text": "office file"},
                ],
                expected_pages=1,
                expected_span_text=["office", "file"],
                spans=[
                    {"id": "s000001", "text": "office"},
                    {"id": "s000002", "text": "file"},
                ],
            ),
        ]
        self.write_json(
            self.root / "manifest.json",
            {
                "manifest_version": "1.0.0",
                "root": "fixtures",
                "subsets_declared": [
                    "born_digital",
                    "fonts",
                    "headings",
                    "hyphenation",
                    "ligatures",
                    "lists",
                    "multi_column",
                    "rotation",
                ],
                "fixtures": entries,
            },
        )

    def write_fixture(
        self,
        *,
        fixture_id: str,
        fixture_path: str,
        subsets: list[str],
        expected_text,
        expected_element_types: list[str],
        elements: list[dict],
        warnings: list[dict] | None = None,
        spans: list[dict] | None = None,
        expected_pages: int | None = None,
        expected_span_text: list[str] | None = None,
        expected_rotation: int | None = None,
        page_rotation: int = 0,
    ):
        fixture_dir = (self.root / fixture_path).parent
        fixture_dir.mkdir(parents=True, exist_ok=True)
        metadata = {
            "id": fixture_id,
            "subsets": subsets,
            "expected_text": expected_text,
            "expected_element_types": expected_element_types,
            "expected_elements": len(elements),
        }
        if expected_pages is not None:
            metadata["expected_pages"] = expected_pages
        if expected_span_text is not None:
            metadata["expected_span_text"] = expected_span_text
        if expected_rotation is not None:
            metadata["expected_rotation"] = expected_rotation
        self.write_json(fixture_dir / "fixture.json", metadata)
        self.write_json(
            fixture_dir / "extraction.json",
            {
                "pages": [
                    {
                        "id": "p0001",
                        "index": 1,
                        "width": 30000,
                        "height": 14400,
                        "rotation": page_rotation,
                    }
                ],
                "spans": spans or [],
                "regions": [],
                "warnings": [],
            },
        )
        self.write_json(
            fixture_dir / "layout.json",
            {"elements": elements, "warnings": warnings or []},
        )
        (fixture_dir / "text.txt").write_text(
            self.render_text_export(elements),
            encoding="utf-8",
        )
        (fixture_dir / "markdown.md").write_text(
            self.render_markdown_export(elements),
            encoding="utf-8",
        )
        return {
            "id": fixture_id,
            "file": fixture_path,
            "sha256": "0" * 64,
            "pages": 1,
            "subsets": subsets,
            "provenance": "Synthetic evaluator unit fixture.",
            "license": "CC0-1.0",
        }

    def write_json(self, path: Path, value) -> None:
        path.write_bytes(canonical_json_bytes(value))

    def render_text_export(self, elements: list[dict]) -> str:
        return "\n\n".join(element["text"] for element in elements) + "\n"

    def render_markdown_export(self, elements: list[dict]) -> str:
        blocks = []
        for element in elements:
            text = element["text"]
            if element.get("type") == "heading":
                level = element.get("heading_level", 1)
                blocks.append(f"{'#' * level} {text}")
            else:
                blocks.append(text)
        return "\n\n".join(blocks) + "\n"


if __name__ == "__main__":
    unittest.main()
