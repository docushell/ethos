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
import re
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-prep-scope-structured-blocker-validation-2026-06-20.md"
)
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
CANDIDATES = ROOT / "docs/milestone-e-fixture-candidates.json"
CRITERIA = ROOT / "docs/milestone-e-fixture-promotion-criteria.json"
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


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def normalized_record_text() -> str:
    return re.sub(r"\s+", " ", record_text())


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class MilestoneEPrepScopeStructuredBlockerValidationRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")
        normalized_text = re.sub(r"\s+", " ", text)

        self.assertIn(
            "milestone-e-prep-scope-structured-blocker-validation-2026-06-20.md",
            text,
        )
        self.assertIn(
            "internal Milestone E prep-scope structured blocker validation",
            normalized_text,
        )

    def test_record_names_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `3141d0a`", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py", text)
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_prep_scope_structured_blocker_validation_record.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn(
            "git grep <prep-scope-structured-blocker-forbidden-wording-expression>",
            text,
        )
        self.assertIn(
            "git grep <prep-scope-structured-blocker-record-private-path-expression>",
            text,
        )
        self.assertIn("git diff --check", text)

    def test_prep_scope_names_structured_blocker_contract(self) -> None:
        text = normalized(PREP_SCOPE)

        self.assertIn("`blockers_must_remain_explicit`", text)
        self.assertIn("structured blocker", text)
        self.assertIn("candidate row must keep a structured", text)
        self.assertIn("promotion criteria row before any internal fixture-planning use", text)
        self.assertIn("every structured blocker", text)
        self.assertIn("fixture-candidate blocker-alignment validation", text)

    def test_inventory_has_visible_structured_blockers_matching_criteria(self) -> None:
        candidates = load_json(CANDIDATES)["fixture_candidates"]
        criteria = load_json(CRITERIA)["criteria"]
        criteria_by_id = {case["candidate_id"]: case for case in criteria}

        self.assertEqual(9, len(candidates))
        self.assertEqual(set(criteria_by_id), {candidate["id"] for candidate in candidates})
        for candidate in candidates:
            candidate_id = candidate["id"]
            blockers = candidate["blockers_must_remain_explicit"]
            self.assertTrue(blockers, candidate_id)
            self.assertEqual(blockers, criteria_by_id[candidate_id]["blockers_must_remain_explicit"])

    def test_record_keeps_source_only_internal_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("pass for internal Milestone E prep-scope structured blocker validation", text)
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("does not change fixture inventory membership", text)
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

    def test_make_target_runs_structured_blocker_record_guard_in_order(self) -> None:
        block = target_block("milestone-e-prep")

        alignment_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py"
        )
        structured_blocker_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_prep_scope_structured_blocker_validation_record.py"
        )
        walkthrough_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py"
        )

        self.assertIn(alignment_guard, block)
        self.assertIn(structured_blocker_guard, block)
        self.assertIn(walkthrough_guard, block)
        self.assertLess(block.index(alignment_guard), block.index(structured_blocker_guard))
        self.assertLess(block.index(structured_blocker_guard), block.index(walkthrough_guard))
        self.assertLess(block.index(structured_blocker_guard), block.index("git diff --check"))

    def test_ci_runs_structured_blocker_record_guard_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        alignment_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py"
        )
        structured_blocker_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_prep_scope_structured_blocker_validation_record.py"
        )
        walkthrough_guard = "python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py"

        self.assertIn(structured_blocker_guard, text)
        self.assertEqual(1, text.count(structured_blocker_guard))
        self.assertLess(text.index(alignment_guard), text.index(structured_blocker_guard))
        self.assertLess(text.index(structured_blocker_guard), text.index(walkthrough_guard))

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
