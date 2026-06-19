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

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/validation/milestone-e-prep-validation-2026-06-19.md"
VALIDATION_README = ROOT / "docs/validation/README.md"


def record_text() -> str:
    return RECORD.read_text(encoding="utf-8")


def normalized_record_text() -> str:
    return re.sub(r"\s+", " ", record_text())


class MilestoneEPrepValidationRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")

        self.assertIn("milestone-e-prep-validation-2026-06-19.md", text)

    def test_record_names_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `f2c9363`", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 -m json.tool docs/milestone-e-fixture-candidates.json", text)
        self.assertIn("git grep <public-posture-expression>", text)
        self.assertIn("git diff --check", text)

    def test_record_keeps_source_only_prep_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("pass for internal Milestone E source-only prep", text)
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("Milestone E prep has started, but only as internal Milestone E prep continuation", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)
        self.assertIn("internal fixture candidates are not public proof points", text)
        self.assertIn("docs/milestone-e-prep-scope.md", text)
        self.assertIn("docs/milestone-e-fixture-candidates.json", text)
        self.assertIn("The E prep guard requires fixture paths to exist and be tracked", text)
        self.assertIn("CI statically runs the E prep guard", text)

    def test_record_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_record_text()

        self.assertIn("does not approve public reports", text)
        self.assertIn("Public reports remain blocked", text)
        self.assertIn("release artifacts", text)
        self.assertIn("package publication", text)
        self.assertIn("production positioning", text)
        self.assertIn("hosted surfaces", text)
        self.assertIn("public result wording", text)
        self.assertIn("Broad demo-generation workflows remain blocked", text)
        self.assertIn(
            "Performance, quality, footprint, table-quality, and parser-quality claims remain blocked",
            text,
        )

    def test_make_target_runs_validation_record_guard(self) -> None:
        block = target_block("milestone-e-prep")

        scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"
        record_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py"
        self.assertIn(scope_guard, block)
        self.assertIn(record_guard, block)
        self.assertLess(block.index(scope_guard), block.index(record_guard))

    def test_record_avoids_scope_expansion_language(self) -> None:
        text = normalized_record_text().lower()

        for phrase in [
            "public beta is approved",
            "release-ready",
            "package-ready",
            "production-ready",
            "benchmark-validated",
            "launch-ready",
            "public result wording approved",
            "hosted surface approved",
            "broad demo approved",
        ]:
            self.assertNotIn(phrase, text)

    def test_record_avoids_local_private_paths(self) -> None:
        text = record_text()

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)


if __name__ == "__main__":
    unittest.main()
