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
RECORD = ROOT / "docs/validation/milestone-e-public-boundary-alignment-validation-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_BOUNDARIES = [
    "Public reports remain blocked",
    "Release artifacts remain blocked",
    "Package publication remains blocked",
    "Hosted surfaces remain blocked",
    "Public result wording remains blocked",
    "Performance claims remain blocked",
    "Quality claims remain blocked",
    "Footprint claims remain blocked",
    "Table-quality claims remain blocked",
    "Parser-quality claims remain blocked",
]

FORBIDDEN_RECORD_WORDING = [
    "public beta is approved",
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "package publication approved",
    "production-ready",
    "production positioning approved",
    "benchmark-validated",
    "public benchmark pass",
    "speed validated",
    "fastest",
    "launch-ready",
    "hosted surface approved",
    "hosted demo approved",
    "demo-ready",
    "complete demo plan",
    "broad demo approved",
    "performance validated",
    "quality validated",
    "footprint validated",
    "table-quality validated",
    "parser-quality validated",
]


def record_text() -> str:
    return RECORD.read_text(encoding="utf-8")


def normalized_record_text() -> str:
    return re.sub(r"\s+", " ", record_text())


class MilestoneEPublicBoundaryAlignmentValidationRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")
        normalized = re.sub(r"\s+", " ", text)

        self.assertIn("milestone-e-public-boundary-alignment-validation-2026-06-20.md", text)
        self.assertIn(
            "internal Milestone E public-boundary alignment validation",
            normalized,
        )

    def test_record_names_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `0a3eb51`", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_public_boundary_alignment.py", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_schema_registry_alignment.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git grep <public-boundary-alignment-forbidden-wording-expression>", text)
        self.assertIn("git grep <public-boundary-alignment-private-path-expression>", text)
        self.assertIn("git diff --check", text)

    def test_record_names_current_boundaries(self) -> None:
        text = record_text()

        for boundary in EXPECTED_BOUNDARIES:
            self.assertIn(boundary, text)

    def test_record_keeps_source_only_internal_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("pass for internal Milestone E public-boundary alignment validation", text)
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("does not change any fixture", text)
        self.assertIn("does not change any schema", text)
        self.assertIn("does not resolve or soften blockers", text)
        self.assertIn("does not promote any fixture", text)
        self.assertIn("not_promoted_beyond_internal_fixture_planning", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)

    def test_make_target_runs_public_boundary_record_guard_in_order(self) -> None:
        block = target_block("milestone-e-prep")

        schema_record_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment_validation_record.py"
        )
        record_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py"
        )
        index_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(record_guard, block)
        self.assertLess(block.index(schema_record_guard), block.index(record_guard))
        self.assertLess(block.index(record_guard), block.index(index_guard))
        self.assertLess(block.index(record_guard), block.index("git diff --check"))

    def test_ci_runs_public_boundary_record_guard_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        schema_record_guard = (
            "python3 .github/scripts/test_milestone_e_schema_registry_alignment_validation_record.py"
        )
        record_guard = (
            "python3 .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py"
        )
        index_guard = "python3 .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(record_guard, text)
        self.assertEqual(1, text.count(record_guard))
        self.assertLess(text.index(schema_record_guard), text.index(record_guard))
        self.assertLess(text.index(record_guard), text.index(index_guard))

    def test_record_avoids_scope_expansion_language(self) -> None:
        text = normalized_record_text().lower()

        for phrase in FORBIDDEN_RECORD_WORDING:
            self.assertNotIn(phrase, text)

    def test_record_avoids_local_private_paths(self) -> None:
        text = record_text()

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)
        self.assertNotIn("/var/folders", text)
        self.assertNotIn("saumildiwaker", text)
        self.assertNotIn("Desktop/Stuff", text)
        self.assertNotIn("project/repo/ethos", text)
        self.assertNotIn("docs/.roadmap.md.swp", text)
        self.assertNotIn("web/", text)


if __name__ == "__main__":
    unittest.main()
