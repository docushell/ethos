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

import json
import subprocess
import unittest
from pathlib import Path

from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = ROOT / "docs/milestone-e-fixture-candidates.json"
CRITERIA = ROOT / "docs/milestone-e-fixture-promotion-criteria.json"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
ALLOWED_COMMANDS = {
    "make milestone-d-capability-downgrade-contract",
    "make milestone-d-internal-contracts",
    "make milestone-d-opendataloader-adapter-shape-contract",
    "make rag-chunk-alpha",
    "make security-report-alpha",
    "make verify-alpha",
}
ALLOWED_PATH_PREFIXES = ("docs/demos/", "examples/", "fixtures/", "schemas/")
FORBIDDEN_PROMOTION_WORDING = [
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_make_target_declared(test_case: unittest.TestCase, target: str) -> None:
    declarations = [
        line for line in makefile_text().splitlines() if line.startswith(f"{target}:")
    ]
    test_case.assertEqual(1, len(declarations), target)


class MilestoneEFixturePromotionCriteriaTests(unittest.TestCase):
    def assert_tracked_file(self, path: str) -> None:
        self.assertTrue((ROOT / path).is_file(), path)
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, path)

    def test_criteria_file_is_source_only_internal(self) -> None:
        criteria = load_json(CRITERIA)

        self.assertEqual(1, criteria["schema_version"])
        self.assertEqual(
            "source-only-pre-alpha-internal-milestone-e-prep",
            criteria["status"],
        )
        self.assertEqual("internal_fixture_promotion_criteria", criteria["scope"])
        self.assertEqual(
            "docs/milestone-e-fixture-candidates.json",
            criteria["applies_to_inventory"],
        )
        self.assertEqual(
            "internal_demo_plan_candidate_review_only",
            criteria["promotion_boundary"],
        )
        self.assertIn("public result wording remains blocked", criteria["public_boundary"])
        self.assertIn("hosted surfaces remain blocked", criteria["public_boundary"])
        self.assertIn("make milestone-e-prep remains green", criteria["global_required_before_internal_demo_plan"])
        self.assertIn(
            "criteria changes require a validation record or explicit superseding record",
            criteria["global_required_before_internal_demo_plan"],
        )

    def test_criteria_exactly_matches_candidate_inventory(self) -> None:
        candidates = load_json(CANDIDATES)["fixture_candidates"]
        criteria = load_json(CRITERIA)["criteria"]

        candidates_by_id = {candidate["id"]: candidate for candidate in candidates}
        criteria_by_id = {case["candidate_id"]: case for case in criteria}
        self.assertEqual(set(candidates_by_id), set(criteria_by_id))
        self.assertEqual(len(criteria), len(criteria_by_id))

        for candidate_id, candidate in candidates_by_id.items():
            case = criteria_by_id[candidate_id]
            self.assertEqual(
                "not_promoted_beyond_internal_fixture_planning",
                case["promotion_status"],
            )
            self.assertEqual(candidate["validated_command"], case["validation_command_must_pass"])
            self.assertEqual(candidate["input_fixtures"], case["required_input_fixtures"])
            self.assertEqual(
                candidate["expected_diagnostic_boundary"],
                case["diagnostic_boundary_must_remain"],
            )
            self.assertEqual(
                candidate["blockers_must_remain_explicit"],
                case["blockers_must_remain_explicit"],
            )
            self.assertTrue(candidate["blockers_must_remain_explicit"], candidate_id)
            self.assertIn(case["validation_command_must_pass"], ALLOWED_COMMANDS)
            assert_make_target_declared(
                self,
                case["validation_command_must_pass"].removeprefix("make "),
            )

    def test_criteria_paths_are_tracked(self) -> None:
        self.assert_tracked_file("docs/milestone-e-fixture-candidates.json")
        self.assert_tracked_file("docs/milestone-e-fixture-promotion-criteria.json")
        for case in load_json(CRITERIA)["criteria"]:
            paths = case["required_input_fixtures"]
            self.assertGreater(len(paths), 0, case["candidate_id"])
            self.assertEqual(len(paths), len(set(paths)), case["candidate_id"])
            for path in case["required_input_fixtures"]:
                self.assertEqual(path, path.strip())
                self.assertFalse(path.startswith("/"), path)
                self.assertNotIn("..", path)
                self.assertNotIn("\\", path)
                self.assertNotIn("*", path)
                self.assertNotIn("?", path)
                self.assertTrue(path.startswith(ALLOWED_PATH_PREFIXES), path)
                self.assert_tracked_file(path)

    def test_prep_scope_references_promotion_criteria(self) -> None:
        text = read(PREP_SCOPE)

        self.assertIn("`docs/milestone-e-fixture-promotion-criteria.json`", text)
        self.assertIn("internal fixture-promotion criteria", text)
        self.assertIn("not public demo approval", text)

    def test_make_target_runs_promotion_criteria_guard(self) -> None:
        block = target_block("milestone-e-prep")

        scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"
        criteria_guard = "$(PYTHON) .github/scripts/test_milestone_e_fixture_promotion_criteria.py"
        record_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py"
        self.assertIn(criteria_guard, block)
        self.assertLess(block.index(scope_guard), block.index(criteria_guard))
        self.assertLess(block.index(criteria_guard), block.index(record_guard))

    def test_ci_runs_promotion_criteria_guard_once(self) -> None:
        text = read(CI_WORKFLOW)
        command = "python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py"

        self.assertIn(command, text)
        self.assertEqual(1, text.count(command))

    def test_criteria_avoids_public_launch_posture(self) -> None:
        text = json.dumps(load_json(CRITERIA), sort_keys=True).lower()

        for phrase in FORBIDDEN_PROMOTION_WORDING:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
