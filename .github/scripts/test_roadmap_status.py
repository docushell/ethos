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
ROADMAP = ROOT / "docs/roadmap.md"


def roadmap_text() -> str:
    return ROADMAP.read_text(encoding="utf-8")


def normalized_roadmap_text() -> str:
    return re.sub(r"\s+", " ", roadmap_text())


class RoadmapStatusTests(unittest.TestCase):
    def test_roadmap_points_to_execution_status_for_current_posture(self) -> None:
        text = roadmap_text()

        self.assertIn("Current PM status and blockers: `docs/execution-status.md`.", text)
        self.assertIn("Milestone C has an internal source-tree artifact-validation closeout", text)
        self.assertIn("milestone-c-closeout-validation-2026-06-18.md", text)
        self.assertIn("Milestone D source-only final closeout is recorded", text)
        self.assertIn("milestone-d-final-closeout-validation-2026-06-19.md", text)
        self.assertIn("milestone-d-contract-closeout-validation-2026-06-19.md", text)

    def test_closeout_note_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_roadmap_text()

        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("releases, packages, production positioning", text)
        self.assertIn("performance/quality/footprint claims", text)
        self.assertIn("cross-platform rendered-crop byte identity is not required for D closeout", text)
        self.assertIn("explicit post-D blockers, not D closeout requirements", text)
        self.assertIn("13-D exit complete for source-only pre-alpha scope", text)

    def test_milestone_b_still_precedes_milestone_c(self) -> None:
        text = roadmap_text()

        milestone_b = text.index("| B | weeks 9-14 |")
        milestone_c = text.index("| C | weeks 15-22 |")
        self.assertLess(milestone_b, milestone_c)


if __name__ == "__main__":
    unittest.main()
