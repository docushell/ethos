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

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKLIST = ROOT / "docs/milestone-b-exit-checklist.md"
ROADMAP = ROOT / "docs/roadmap.md"


def checklist_text() -> str:
    return CHECKLIST.read_text(encoding="utf-8")


def normalized_checklist_text() -> str:
    return re.sub(r"\s+", " ", checklist_text())


class MilestoneBExitChecklistTests(unittest.TestCase):
    def test_roadmap_links_to_checklist(self) -> None:
        text = ROADMAP.read_text(encoding="utf-8")

        self.assertIn("[13-B exit checklist](milestone-b-exit-checklist.md)", text)

    def test_checklist_names_current_validation_commands(self) -> None:
        text = checklist_text()

        self.assertIn("make milestone-b-internal-checks PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("make verify-alpha", text)
        self.assertIn("make layout-evaluator-alpha", text)
        self.assertIn("make python-surface-test", text)

    def test_checklist_covers_internal_b_lanes(self) -> None:
        text = checklist_text()

        for lane in [
            "WS-VERIFY-ALPHA",
            "WS-LAYOUT",
            "WS-SURFACES",
            "WS-HARNESS",
            "DETERMINISM",
        ]:
            self.assertIn(lane, text)

    def test_checklist_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_checklist_text()

        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("release artifacts", text)
        self.assertIn("package publication", text)
        self.assertIn("production positioning", text)
        self.assertIn("Performance/quality/footprint claims remain blocked", text)
        self.assertIn("Table-quality and parser-quality claims remain blocked", text)

    def test_checklist_does_not_claim_broader_scope(self) -> None:
        text = checklist_text()

        self.assertIn("No semantic/arithmetic verification expansion is claimed.", text)
        self.assertIn("No broader parser/table/OCR completion is claimed.", text)


if __name__ == "__main__":
    unittest.main()
