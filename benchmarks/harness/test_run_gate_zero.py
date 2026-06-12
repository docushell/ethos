#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import run_gate_zero


HEX = "a" * 64


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


class GateZeroReadinessTests(unittest.TestCase):
    def test_draft_inputs_block_gate_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            competitors_path = root / "competitors.lock.json"
            write_json(
                manifest_path,
                {
                    "status": "DRAFT-UNFROZEN",
                    "frozen": False,
                    "freeze_record": {"frozen_at": None, "signed_by": None},
                    "corpus": [],
                    "hardware": [
                        {
                            "id": "mac-m4pro-arm64",
                            "role": "performance",
                            "model": "Mac (M4 Pro)",
                            "cpu": None,
                            "ram": None,
                            "os": None,
                            "kernel": None,
                            "runner": None,
                        }
                    ],
                },
            )
            write_json(
                competitors_path,
                {
                    "status": "PIN-PENDING",
                    "gate_zero": [
                        {
                            "id": "opendataloader-pdf",
                            "version": None,
                            "artifact_sha256": None,
                            "jvm_version": None,
                            "pinned": False,
                        }
                    ],
                },
            )

            report = run_gate_zero.build_report(root, manifest_path, competitors_path)

        self.assertEqual(report["status"], "blocked")
        self.assertIn("Gate Zero manifest is not frozen", report["blockers"]["manifest"])
        self.assertIn("Gate Zero corpus[] is empty", report["blockers"]["manifest"])
        self.assertIn("hardware mac-m4pro-arm64 missing cpu", report["blockers"]["manifest"])
        self.assertIn("competitor opendataloader-pdf is not pinned", report["blockers"]["competitors"])
        self.assertIn(
            "competitor opendataloader-pdf missing jvm_version",
            report["blockers"]["competitors"],
        )

    def test_frozen_inputs_are_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            competitors_path = root / "competitors.lock.json"
            write_json(
                manifest_path,
                {
                    "status": "FROZEN-SIGNED",
                    "frozen": True,
                    "freeze_record": {
                        "frozen_at": "2026-06-12T00:00:00Z",
                        "signed_by": "Gate Zero decider",
                    },
                    "corpus": [
                        {
                            "file": "sample.pdf",
                            "sha256": HEX,
                            "pages": 1,
                            "subsets": ["born_digital"],
                            "provenance": "synthetic",
                            "license": "CC0",
                        }
                    ],
                    "hardware": [
                        {
                            "id": "mac-m4pro-arm64",
                            "role": "performance",
                            "model": "Mac (M4 Pro)",
                            "cpu": "Apple M4 Pro",
                            "ram": "48 GB",
                            "os": "macOS 15.0",
                            "kernel": "Darwin 24.0.0",
                            "runner": "local",
                        }
                    ],
                },
            )
            write_json(
                competitors_path,
                {
                    "status": "PINNED",
                    "gate_zero": [
                        {
                            "id": "opendataloader-pdf",
                            "version": "1.2.3",
                            "artifact_sha256": HEX,
                            "jvm_version": "21.0.1",
                            "pinned": True,
                        },
                        {
                            "id": "edgeparse",
                            "version": "2.0.0",
                            "artifact_sha256": HEX,
                            "pinned": True,
                        },
                        {
                            "id": "liteparse",
                            "version": "3.0.0",
                            "artifact_sha256": HEX,
                            "pinned": True,
                        },
                        {
                            "id": "pymupdf4llm",
                            "version": "0.1.0",
                            "artifact_sha256": HEX,
                            "python_version": "3.12.0",
                            "pinned": True,
                        },
                    ],
                },
            )

            report = run_gate_zero.build_report(root, manifest_path, competitors_path)

        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["summary"]["blockers_total"], 0)
        self.assertEqual(report["blockers"], {"manifest": [], "competitors": []})


if __name__ == "__main__":
    unittest.main()
