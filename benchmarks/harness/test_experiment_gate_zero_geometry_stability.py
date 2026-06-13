#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from argparse import ArgumentTypeError
from pathlib import Path

import experiment_gate_zero_geometry_stability


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def document(*, text: str = "Hello", bbox: list[int] | None = None) -> dict[str, object]:
    resolved_bbox = bbox or [11, 21, 31, 41]
    return {
        "fingerprint": "sha256:" + "a" * 64,
        "payload_sha256": "b" * 64,
        "payload": {
            "spans": [
                {
                    "id": "s1",
                    "text": text,
                    "bbox": resolved_bbox,
                }
            ],
            "elements": [
                {
                    "id": "e1",
                    "type": "paragraph",
                    "text": text,
                    "bbox": resolved_bbox,
                }
            ],
        },
    }


class GateZeroGeometryExperimentTests(unittest.TestCase):
    def test_bbox_only_divergence_reports_drop_bbox_and_coarse_strategy_as_passing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(left / "sample.json", document(bbox=[11, 21, 31, 41]))
            write_json(right / "sample.json", document(bbox=[19, 29, 39, 49]))

            report = experiment_gate_zero_geometry_stability.build_report(
                experiment_gate_zero_geometry_stability.parse_args(
                    [
                        "--left-dir",
                        str(left),
                        "--right-dir",
                        str(right),
                        "--doc-id",
                        "sample",
                        "--nearest-grid",
                        "10",
                        "--outward-grid",
                        "10",
                    ]
                )
            )

        by_id = {candidate["id"]: candidate for candidate in report["candidates"]}
        self.assertEqual(report["summary"]["stable_except_bbox_and_hashes"], 1)
        self.assertEqual(by_id["identity"]["candidate_status"], "unresolved")
        self.assertEqual(by_id["drop-bbox"]["candidate_status"], "resolved")
        self.assertEqual(by_id["nearest-grid-10q"]["candidate_status"], "unresolved")
        self.assertEqual(by_id["outward-grid-10q"]["candidate_status"], "resolved")
        self.assertEqual(report["documents"][0]["bbox_deltas"]["max_abs_delta_quanta"], 8)

    def test_semantic_difference_does_not_pass_drop_bbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            write_json(left / "sample.json", document(text="Hello", bbox=[11, 21, 31, 41]))
            write_json(right / "sample.json", document(text="Goodbye", bbox=[11, 21, 31, 41]))

            report = experiment_gate_zero_geometry_stability.build_report(
                experiment_gate_zero_geometry_stability.parse_args(
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

        by_id = {candidate["id"]: candidate for candidate in report["candidates"]}
        self.assertEqual(report["summary"]["stable_except_bbox_and_hashes"], 0)
        self.assertEqual(by_id["drop-bbox"]["candidate_status"], "unresolved")

    def test_manifest_can_select_document_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = root / "left"
            right = root / "right"
            manifest = root / "manifest.json"
            write_json(left / "sample.json", document())
            write_json(right / "sample.json", document())
            write_json(manifest, {"corpus": [{"id": "sample"}]})
            manifest_sha256 = experiment_gate_zero_geometry_stability.sha256_file(manifest)

            report = experiment_gate_zero_geometry_stability.build_report(
                experiment_gate_zero_geometry_stability.parse_args(
                    [
                        "--left-dir",
                        str(left),
                        "--right-dir",
                        str(right),
                        "--manifest",
                        str(manifest),
                    ]
                )
            )

            self.assertEqual(report["inputs"]["manifest"], str(manifest))
            self.assertEqual(report["inputs"]["manifest_sha256"], manifest_sha256)
            self.assertEqual(report["inputs"]["doc_ids"], ["sample"])

    def test_positive_grid_rejects_non_positive_values(self) -> None:
        with self.assertRaises(ArgumentTypeError):
            experiment_gate_zero_geometry_stability.positive_grid("0")


if __name__ == "__main__":
    unittest.main()
