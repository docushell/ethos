#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import diff_gate_zero_docs


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class GateZeroDocDiffTests(unittest.TestCase):
    def test_identical_documents_report_same(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            doc = {"fingerprint": "sha256:a", "payload": {"spans": [{"text": "Hello"}]}}
            write_json(left / "sample.json", doc)
            write_json(right / "sample.json", doc)

            report = diff_gate_zero_docs.build_report(
                diff_gate_zero_docs.parse_args(
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

        self.assertEqual(report["summary"]["documents_different"], 0)
        self.assertEqual(report["comparisons"][0]["status"], "same")
        self.assertEqual(report["comparisons"][0]["diff_count"], 0)

    def test_value_differences_are_bucketed_by_payload_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(
                left / "sample.json",
                {
                    "fingerprint": "sha256:left",
                    "payload": {
                        "pages": [{"width": 30000}],
                        "spans": [{"text": "Hello", "bbox": [1, 2, 3, 4]}],
                    },
                },
            )
            write_json(
                right / "sample.json",
                {
                    "fingerprint": "sha256:right",
                    "payload": {
                        "pages": [{"width": 30001}],
                        "spans": [{"text": "Hello", "bbox": [1, 2, 3, 5]}],
                    },
                },
            )

            report = diff_gate_zero_docs.build_report(
                diff_gate_zero_docs.parse_args(
                    [
                        "--left-dir",
                        str(left),
                        "--right-dir",
                        str(right),
                        "--doc-id",
                        "sample",
                        "--max-diffs",
                        "10",
                    ]
                )
            )

        comparison = report["comparisons"][0]
        self.assertEqual(comparison["status"], "different")
        self.assertEqual(comparison["buckets"]["/fingerprint"], 1)
        self.assertEqual(comparison["buckets"]["/payload/pages"], 1)
        self.assertEqual(comparison["buckets"]["/payload/spans"], 1)
        self.assertEqual(report["summary"]["documents_different"], 1)

    def test_array_length_differences_are_reported(self) -> None:
        diffs = diff_gate_zero_docs.diff_values([{"id": "a"}, {"id": "b"}], [{"id": "a"}])

        self.assertEqual(diffs, [{"pointer": "/1", "kind": "missing_right", "left": {"id": "b"}, "right": None}])


if __name__ == "__main__":
    unittest.main()
