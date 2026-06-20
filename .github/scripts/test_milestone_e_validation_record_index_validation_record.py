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
RECORD = ROOT / "docs/validation/milestone-e-validation-record-index-validation-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

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


class MilestoneEValidationRecordIndexValidationRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")
        normalized = re.sub(r"\s+", " ", text)

        self.assertIn("milestone-e-validation-record-index-validation-2026-06-20.md", text)
        self.assertIn(
            "internal Milestone E validation-record index validation",
            normalized,
        )

    def test_record_names_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `50bb692`", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_validation_record_index.py", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_validation_record_index_validation_record.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_schema_registry_alignment.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git grep <validation-record-index-forbidden-wording-expression>", text)
        self.assertIn("git grep <validation-record-index-private-path-expression>", text)
        self.assertIn("git diff --check", text)

    def test_record_keeps_source_only_internal_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("pass for internal Milestone E validation-record index validation", text)
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("does not change any fixture", text)
        self.assertIn("does not change any schema", text)
        self.assertIn("does not resolve or soften blockers", text)
        self.assertIn("does not promote any fixture", text)
        self.assertIn("not_promoted_beyond_internal_fixture_planning", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)

    def test_record_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_record_text()

        self.assertIn("Public reports remain blocked", text)
        self.assertIn("Public result wording remains blocked", text)
        self.assertIn("Hosted surfaces remain blocked", text)
        self.assertIn("Release artifacts remain blocked", text)
        self.assertIn("Package publication remains blocked", text)
        self.assertIn("Production positioning remains blocked", text)
        self.assertIn("Broad demo-generation workflows remain blocked", text)
        self.assertIn("Performance claims remain blocked", text)
        self.assertIn("Quality claims remain blocked", text)
        self.assertIn("Footprint claims remain blocked", text)
        self.assertIn("Table-quality claims remain blocked", text)
        self.assertIn("Parser-quality claims remain blocked", text)

    def test_make_target_runs_index_guards_in_order(self) -> None:
        block = target_block("milestone-e-prep")

        row_guard = "$(PYTHON) .github/scripts/test_milestone_e_rehearsal_row_record_coverage_validation.py"
        schema_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment_validation_record.py"
        )
        index_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py"
        record_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index_validation_record.py"
        )
        prep_record_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py"

        self.assertIn(index_guard, block)
        self.assertIn(record_guard, block)
        self.assertLess(block.index(row_guard), block.index(index_guard))
        self.assertLess(block.index(schema_guard), block.index(index_guard))
        self.assertLess(block.index(index_guard), block.index(record_guard))
        self.assertLess(block.index(record_guard), block.index(prep_record_guard))
        self.assertLess(block.index(record_guard), block.index("git diff --check"))

    def test_ci_runs_index_guards_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        row_guard = "python3 .github/scripts/test_milestone_e_rehearsal_row_record_coverage_validation.py"
        schema_guard = (
            "python3 .github/scripts/test_milestone_e_schema_registry_alignment_validation_record.py"
        )
        index_guard = "python3 .github/scripts/test_milestone_e_validation_record_index.py"
        record_guard = (
            "python3 .github/scripts/test_milestone_e_validation_record_index_validation_record.py"
        )
        prep_record_guard = "python3 .github/scripts/test_milestone_e_prep_validation_record.py"

        self.assertIn(index_guard, text)
        self.assertEqual(1, text.count(index_guard))
        self.assertIn(record_guard, text)
        self.assertEqual(1, text.count(record_guard))
        self.assertLess(text.index(row_guard), text.index(index_guard))
        self.assertLess(text.index(schema_guard), text.index(index_guard))
        self.assertLess(text.index(index_guard), text.index(record_guard))
        self.assertLess(text.index(record_guard), text.index(prep_record_guard))

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
