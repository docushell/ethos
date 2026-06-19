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

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
EXAMPLES_README = ROOT / "examples/README.md"
CLAIMS_GATE = ROOT / ".github/scripts/claims_gate.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class PublicSurfacePostureTests(unittest.TestCase):
    def test_readme_status_matches_internal_closeout_scope(self) -> None:
        text = read(README)

        self.assertIn("source-only pre-alpha", text)
        self.assertIn("internal Milestone D closeout complete, Milestone E prep", text)
        self.assertIn("ADR-0005 records an internal", text)
        self.assertIn("continuation only", text)
        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("No performance,", text)
        self.assertIn("table-quality, or parser-quality claims are made", text)
        self.assertNotIn("contracts phase", text)
        self.assertNotIn("has not run", text)

    def test_examples_readme_stays_fixture_scoped(self) -> None:
        text = read(EXAMPLES_README)

        self.assertIn("source-only pre-alpha demo fixture set", text)
        self.assertIn("Pinned fixtures only", text)
        self.assertNotIn("launch package", text.lower())

    def test_claims_gate_blocks_stale_public_posture_terms(self) -> None:
        text = read(CLAIMS_GATE)

        self.assertIn("contracts phase", text)
        self.assertIn("Gate Zero[^\\n]*has not run", text)
        self.assertIn("launch package", text)
        self.assertIn('"docs/milestone-e-prep-scope.md"', text)
        self.assertIn("benchmark[- ]validated", text)
        self.assertIn("release[- ]ready", text)
        self.assertIn("package[- ]ready", text)
        self.assertIn("production[- ]ready", text)
        self.assertIn("launch[- ]ready", text)


if __name__ == "__main__":
    unittest.main()
