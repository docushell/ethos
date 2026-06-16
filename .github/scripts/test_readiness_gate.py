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

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().with_name("readiness_gate.py")
SPEC = importlib.util.spec_from_file_location("readiness_gate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
readiness_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readiness_gate)

HEX = "a" * 64


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def ready_manifest() -> dict[str, object]:
    return {
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
    }


def ready_lock() -> dict[str, object]:
    return {
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
    }


class ReadinessGateTests(unittest.TestCase):
    def with_repo(self, manifest: object, lock: object):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        write_json(root / "benchmarks/gate-zero/manifest.json", manifest)
        write_json(root / "benchmarks/competitors.lock.json", lock)
        return temp, root

    def test_gate_zero_green_with_minimal_frozen_inputs(self) -> None:
        temp, root = self.with_repo(ready_manifest(), ready_lock())
        with temp:
            with patch.object(readiness_gate, "ROOT", root):
                gate = readiness_gate.run("gate-zero")
        self.assertEqual(gate.failures, [])

    def test_draft_manifest_and_unpinned_lock_block(self) -> None:
        manifest = {
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
        }
        lock = {
            "gate_zero": [
                {
                    "id": "opendataloader-pdf",
                    "version": None,
                    "artifact_sha256": None,
                    "jvm_version": None,
                    "pinned": False,
                }
            ],
        }
        temp, root = self.with_repo(manifest, lock)
        with temp:
            with patch.object(readiness_gate, "ROOT", root):
                failures = readiness_gate.run("gate-zero").failures
        self.assertIn("Gate Zero manifest is not frozen", failures)
        self.assertIn("Gate Zero corpus[] is empty", failures)
        self.assertIn("hardware mac-m4pro-arm64 missing cpu", failures)
        self.assertIn("competitor opendataloader-pdf is not pinned", failures)

    def test_missing_performance_hardware_blocks(self) -> None:
        manifest = ready_manifest()
        manifest["hardware"] = []
        temp, root = self.with_repo(manifest, ready_lock())
        with temp:
            with patch.object(readiness_gate, "ROOT", root):
                failures = readiness_gate.run("gate-zero").failures
        self.assertIn("Gate Zero manifest has no performance hardware host", failures)

    def test_missing_expected_competitor_blocks(self) -> None:
        lock = ready_lock()
        lock["gate_zero"] = [
            entry for entry in lock["gate_zero"] if entry["id"] != "edgeparse"
        ]
        temp, root = self.with_repo(ready_manifest(), lock)
        with temp:
            with patch.object(readiness_gate, "ROOT", root):
                failures = readiness_gate.run("gate-zero").failures
        self.assertIn("competitor edgeparse missing from gate_zero lock", failures)

    def test_invalid_hash_blocks(self) -> None:
        manifest = ready_manifest()
        manifest["corpus"][0]["sha256"] = "A" * 64
        lock = ready_lock()
        lock["gate_zero"][0]["artifact_sha256"] = "short"
        temp, root = self.with_repo(manifest, lock)
        with temp:
            with patch.object(readiness_gate, "ROOT", root):
                failures = readiness_gate.run("gate-zero").failures
        self.assertIn("Gate Zero corpus entry 1 sha256 is not lowercase hex", failures)
        self.assertIn(
            "competitor opendataloader-pdf artifact_sha256 is not lowercase hex",
            failures,
        )

    def test_report_only_keeps_blocked_cli_exit_zero(self) -> None:
        manifest = ready_manifest()
        manifest["frozen"] = False
        temp, root = self.with_repo(manifest, ready_lock())
        with temp:
            with patch.object(readiness_gate, "ROOT", root):
                with patch.object(
                    sys,
                    "argv",
                    ["readiness_gate.py", "gate-zero", "--report-only"],
                ):
                    self.assertEqual(readiness_gate.main(), 0)


if __name__ == "__main__":
    unittest.main()
