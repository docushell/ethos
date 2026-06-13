#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import compare_gate_zero_geometry_probes


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def probe(*, text: str = "Hello", char_box: list[int] | None = None) -> dict[str, object]:
    resolved_box = char_box or [10, 20, 30, 40]
    return {
        "schema_version": "ethos-pdfium-geometry-probe-v1",
        "quantum_per_point": 100,
        "backend": {
            "id": "pdfium",
            "phase": 1,
            "platform_sha256": "a" * 64,
            "version": "chromium/7881",
        },
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
                "chars": [
                    {
                        "index": 0,
                        "unicode": ord(text[0]),
                        "text": text[0],
                        "parser_action": "include",
                        "char_box": resolved_box,
                        "loose_char_box": resolved_box,
                        "char_origin": [10, 40],
                        "font_id": "subst:liberation-sans-regular",
                        "font_size_q": 1200,
                    }
                ],
                "runs": [
                    {
                        "index": 1,
                        "text": text,
                        "char_start": 0,
                        "char_end": len(text),
                        "char_indices": [0],
                        "char_box_union": resolved_box,
                        "loose_char_box_union": resolved_box,
                        "text_rects": [resolved_box],
                        "text_rect_union": resolved_box,
                        "first_origin": [10, 40],
                        "last_origin": [10, 40],
                        "font_id": "subst:liberation-sans-regular",
                        "font_size_q": 1200,
                    }
                ],
            }
        ],
    }


class GateZeroGeometryProbeComparisonTests(unittest.TestCase):
    def test_matching_probes_report_all_signals_matched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(left / "sample.json", probe())
            write_json(right / "sample.json", probe())

            report = compare_gate_zero_geometry_probes.build_report(
                compare_gate_zero_geometry_probes.parse_args(
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

        self.assertEqual(report["summary"]["structural_matches"], 1)
        self.assertEqual(
            sorted(report["summary"]["matched_signals"]),
            ["char_box", "char_origin", "loose_char_box", "text_rects"],
        )
        self.assertEqual(report["summary"]["diverged_signals"], [])

    def test_signal_divergence_does_not_break_structural_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(left / "sample.json", probe(char_box=[10, 20, 30, 40]))
            write_json(right / "sample.json", probe(char_box=[10, 20, 31, 40]))

            report = compare_gate_zero_geometry_probes.build_report(
                compare_gate_zero_geometry_probes.parse_args(
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

        by_signal = {item["signal"]: item for item in report["summary"]["signals"]}
        self.assertEqual(report["summary"]["structural_matches"], 1)
        self.assertEqual(by_signal["char_box"]["status"], "diverged")
        self.assertEqual(by_signal["loose_char_box"]["status"], "diverged")
        self.assertEqual(by_signal["text_rects"]["status"], "diverged")

    def test_structural_text_difference_is_reported_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(left / "sample.json", probe(text="Hello"))
            write_json(right / "sample.json", probe(text="World"))

            report = compare_gate_zero_geometry_probes.build_report(
                compare_gate_zero_geometry_probes.parse_args(
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

        self.assertEqual(report["summary"]["structural_matches"], 0)
        self.assertEqual(report["comparisons"][0]["structural_status"], "diverged")
        self.assertGreater(report["comparisons"][0]["structural_diff_count"], 0)


if __name__ == "__main__":
    unittest.main()
