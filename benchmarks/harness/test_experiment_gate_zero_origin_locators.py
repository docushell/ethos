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

import experiment_gate_zero_origin_locators


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def probe(
    *,
    text: str = "Hello",
    char_box: list[int] | None = None,
    first_origin: list[int] | None = None,
    last_origin: list[int] | None = None,
) -> dict[str, object]:
    resolved_box = char_box or [10, 20, 30, 40]
    resolved_first = first_origin or [10, 40]
    resolved_last = last_origin or [30, 40]
    return {
        "schema_version": "ethos-pdfium-geometry-probe-v1",
        "quantum_per_point": 100,
        "backend": {"id": "pdfium", "phase": 1, "version": "chromium/7881"},
        "pages": [
            {
                "id": "p0001",
                "index": 1,
                "width": 61200,
                "height": 79200,
                "rotation": 0,
                "char_count": len(text),
                "symbols": {
                    "char_origin": True,
                    "loose_char_box": True,
                    "text_rects": True,
                },
                "chars": [],
                "runs": [
                    {
                        "index": 1,
                        "text": text,
                        "char_start": 0,
                        "char_end": len(text),
                        "char_indices": list(range(len(text))),
                        "char_box_union": resolved_box,
                        "loose_char_box_union": resolved_box,
                        "text_rects": [resolved_box],
                        "text_rect_union": resolved_box,
                        "first_origin": resolved_first,
                        "last_origin": resolved_last,
                        "font_id": "subst:liberation-sans-regular",
                        "font_size_q": 1200,
                    }
                ],
            }
        ],
    }


class GateZeroOriginLocatorExperimentTests(unittest.TestCase):
    def test_bbox_divergence_does_not_change_origin_locator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(left / "sample.json", probe(char_box=[10, 20, 30, 40]))
            write_json(right / "sample.json", probe(char_box=[11, 19, 31, 42]))

            report = experiment_gate_zero_origin_locators.build_report(
                experiment_gate_zero_origin_locators.parse_args(
                    [
                        "--left-dir",
                        str(left),
                        "--right-dir",
                        str(right),
                        "--doc-id",
                        "sample",
                    ]
                )
            )

        comparison = report["comparisons"][0]
        self.assertEqual(report["summary"]["status"], "resolved")
        self.assertEqual(comparison["status"], "matched")
        self.assertEqual(comparison["left_locator_sha256"], comparison["right_locator_sha256"])

    def test_origin_divergence_changes_origin_locator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(left / "sample.json", probe(first_origin=[10, 40]))
            write_json(right / "sample.json", probe(first_origin=[11, 40]))

            report = experiment_gate_zero_origin_locators.build_report(
                experiment_gate_zero_origin_locators.parse_args(
                    [
                        "--left-dir",
                        str(left),
                        "--right-dir",
                        str(right),
                        "--doc-id",
                        "sample",
                    ]
                )
            )

        comparison = report["comparisons"][0]
        self.assertEqual(report["summary"]["status"], "unresolved")
        self.assertEqual(comparison["status"], "diverged")
        self.assertNotEqual(comparison["left_locator_sha256"], comparison["right_locator_sha256"])

    def test_text_divergence_changes_origin_locator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(left / "sample.json", probe(text="Hello"))
            write_json(right / "sample.json", probe(text="World"))

            report = experiment_gate_zero_origin_locators.build_report(
                experiment_gate_zero_origin_locators.parse_args(
                    [
                        "--left-dir",
                        str(left),
                        "--right-dir",
                        str(right),
                        "--doc-id",
                        "sample",
                    ]
                )
            )

        self.assertEqual(report["summary"]["status"], "unresolved")
        self.assertEqual(report["summary"]["diverged_documents"], ["sample"])


if __name__ == "__main__":
    unittest.main()
