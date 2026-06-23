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
RECORD = ROOT / "docs/validation/milestone-e-final-closeout-validation-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def record_text() -> str:
    return read(RECORD)


def normalized_record_text() -> str:
    return re.sub(r"\s+", " ", record_text())


class MilestoneEFinalCloseoutRecordTests(unittest.TestCase):
    def test_record_is_indexed_and_referenced(self) -> None:
        record_name = "milestone-e-final-closeout-validation-2026-06-20.md"

        self.assertIn(record_name, read(VALIDATION_README))
        self.assertIn(record_name, read(ROADMAP))
        self.assertIn(record_name, read(EXECUTION_STATUS))

    def test_record_names_final_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `bb3674f`", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_final_closeout_record.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_validation_record.py", text)
        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git grep <milestone-e-final-closeout-forbidden-wording-expression>", text)
        self.assertIn("git grep <milestone-e-final-closeout-private-path-expression>", text)
        self.assertIn("git diff --check", text)

    def test_record_closes_source_only_prep_without_expanding_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("pass for final internal Milestone E source-only prep closeout", text)
        self.assertIn(
            "Milestone E prep is internally complete for the current source-only pre-alpha prep scope",
            text,
        )
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)
        self.assertIn("does not change fixture JSON artifacts", text)
        self.assertIn("does not change schemas", text)
        self.assertIn("does not promote any fixture", text)
        self.assertIn("does not resolve or soften blockers", text)
        self.assertIn("Internal fixture candidates remain non-public planning inputs", text)
        self.assertIn(
            "Promotion status remains `not_promoted_beyond_internal_fixture_planning`",
            text,
        )

    def test_record_names_closed_prep_guard_scope(self) -> None:
        text = normalized_record_text()

        for guard_scope in [
            "schema-registry alignment",
            "public-boundary alignment",
            "blocked-output alignment",
            "evidence-lane alignment",
            "diagnostic-boundary alignment",
            "promotion-status alignment",
            "source-status alignment",
            "applies-to binding alignment",
            "required-before alignment",
            "validation-command indexing",
            "validation-record indexing",
            "validation-record source-head alignment",
            "prep guard-sequence index",
            "current prep guard validation",
        ]:
            self.assertIn(guard_scope, text)

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

    def test_make_target_runs_final_closeout_record_guard(self) -> None:
        block = target_block("milestone-e-prep")

        prep_record_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py"
        final_guard = "$(PYTHON) .github/scripts/test_milestone_e_final_closeout_record.py"

        self.assertIn(final_guard, block)
        self.assertLess(block.index(prep_record_guard), block.index(final_guard))
        self.assertLess(block.index(final_guard), block.index("git diff --check"))

    def test_ci_runs_final_closeout_record_guard(self) -> None:
        text = read(CI_WORKFLOW)

        prep_record_guard = "python3 .github/scripts/test_milestone_e_prep_validation_record.py"
        final_guard = "python3 .github/scripts/test_milestone_e_final_closeout_record.py"

        self.assertIn(final_guard, text)
        self.assertEqual(1, text.count(final_guard))
        self.assertLess(text.index(prep_record_guard), text.index(final_guard))

    def test_status_and_roadmap_keep_final_closeout_source_only(self) -> None:
        for path in (ROADMAP, EXECUTION_STATUS):
            text = re.sub(r"\s+", " ", read(path))

            self.assertIn("Milestone E prep source-only closeout", text, str(path))
            self.assertIn("milestone-e-final-closeout-validation-2026-06-20.md", text, str(path))
            self.assertIn("does not resolve or soften blockers", text, str(path))
            self.assertIn("source-only pre-alpha", text, str(path))

    def test_record_avoids_scope_expansion_language(self) -> None:
        text = normalized_record_text().lower()

        for phrase in [
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
        ]:
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
