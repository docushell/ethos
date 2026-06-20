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
RECORD = ROOT / "docs/validation/milestone-e-validation-command-index-validation-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_COMMANDS = (
    "make verify-alpha",
    "make milestone-d-capability-downgrade-contract",
    "make milestone-d-opendataloader-adapter-shape-contract",
    "make milestone-d-internal-contracts",
    "make rag-chunk-alpha",
    "make security-report-alpha",
)

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


class MilestoneEValidationCommandIndexValidationRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")
        normalized = re.sub(r"\s+", " ", text)

        self.assertIn("milestone-e-validation-command-index-validation-2026-06-20.md", text)
        self.assertIn(
            "internal Milestone E validation-command index validation",
            normalized,
        )

    def test_record_names_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `ddd9673`", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_validation_command_index.py", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_validation_command_index_validation_record.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_rehearsal_row_record_coverage_validation.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git grep <validation-command-index-forbidden-wording-expression>", text)
        self.assertIn("git grep <validation-command-index-private-path-expression>", text)
        self.assertIn("git diff --check", text)

    def test_record_names_current_canonical_command_set(self) -> None:
        text = record_text()

        for command in EXPECTED_COMMANDS:
            self.assertIn(f"- `{command}`", text)

    def test_record_keeps_source_only_internal_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("pass for internal Milestone E validation-command index validation", text)
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("does not change any fixture JSON artifact", text)
        self.assertIn("does not change any schema", text)
        self.assertIn("does not resolve or soften blockers", text)
        self.assertIn("does not promote any fixture", text)
        self.assertIn("plain source-checkout make targets", text)
        self.assertIn("not_promoted_beyond_internal_fixture_planning", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)

    def test_make_target_runs_validation_command_record_guard_in_order(self) -> None:
        block = target_block("milestone-e-prep")

        public_boundary_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py"
        )
        command_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_command_index.py"
        record_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_validation_command_index_validation_record.py"
        )
        index_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(record_guard, block)
        self.assertLess(block.index(public_boundary_record), block.index(command_guard))
        self.assertLess(block.index(command_guard), block.index(record_guard))
        self.assertLess(block.index(record_guard), block.index(index_guard))
        self.assertLess(block.index(record_guard), block.index("git diff --check"))

    def test_ci_runs_validation_command_record_guard_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        public_boundary_record = (
            "python3 .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py"
        )
        command_guard = "python3 .github/scripts/test_milestone_e_validation_command_index.py"
        record_guard = (
            "python3 .github/scripts/test_milestone_e_validation_command_index_validation_record.py"
        )
        index_guard = "python3 .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(record_guard, text)
        self.assertEqual(1, text.count(record_guard))
        self.assertLess(text.index(public_boundary_record), text.index(command_guard))
        self.assertLess(text.index(command_guard), text.index(record_guard))
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
