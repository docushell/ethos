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
RECORD = ROOT / "docs/validation/milestone-b-closeout-validation-2026-06-17.md"
VALIDATION_README = ROOT / "docs/validation/README.md"


def record_text() -> str:
    return RECORD.read_text(encoding="utf-8")


def normalized_record_text() -> str:
    return re.sub(r"\s+", " ", record_text())


class MilestoneBCloseoutRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")

        self.assertIn("milestone-b-closeout-validation-2026-06-17.md", text)

    def test_record_names_internal_validation_command(self) -> None:
        text = record_text()

        self.assertIn("make milestone-b-internal-checks PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("fixtures/validate_fixtures.py", text)
        self.assertIn("make verify-alpha", text)
        self.assertIn("make layout-evaluator-alpha", text)
        self.assertIn("make python-surface-test", text)
        self.assertIn(".github/scripts/claims_gate.py", text)
        self.assertIn(".github/scripts/readiness_gate.py public", text)

    def test_record_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_record_text()

        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("release artifacts", text)
        self.assertIn("package publication", text)
        self.assertIn("production positioning", text)
        self.assertIn("Performance, quality, footprint, table-quality, and parser-quality claims remain blocked", text)

    def test_record_avoids_local_private_paths(self) -> None:
        text = record_text()

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)


if __name__ == "__main__":
    unittest.main()
