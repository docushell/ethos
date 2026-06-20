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
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RECORD = ROOT / "docs/validation/release-readiness-next-steps-approval-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

APPROVED_STEPS = [
    "Close H1",
    "Close H2",
    "Approve any wording beyond the exact pre-alpha sentence",
    "Harden release-scope engineering blockers",
    "Run release-candidate validation gates",
]

BOUNDARY_PHRASES = [
    "does not approve public benchmark reports",
    "does not approve release artifacts",
    "does not approve package publication",
    "does not approve production positioning",
    "does not approve hosted surfaces",
    "does not approve wording beyond the exact approved pre-alpha sentence",
]

FORBIDDEN_SCOPE_EXPANSION = [
    "pre-alpha exit approved",
    "public beta approved",
    "public benchmark reports approved",
    "release artifacts approved",
    "package publication approved",
    "production positioning approved",
    "hosted surfaces approved",
    "ready for first release",
    "first release is approved",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class ReleaseReadinessNextStepsApprovalTests(unittest.TestCase):
    def test_approved_sequence_is_recorded_in_order(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RECORD):
            text = normalized(path)
            cursor = -1
            for step in APPROVED_STEPS:
                position = text.find(step)
                self.assertGreater(position, cursor, f"{step} missing or out of order in {path}")
                cursor = position

    def test_boundaries_remain_explicit(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RECORD):
            text = normalized(path)
            for phrase in BOUNDARY_PHRASES:
                self.assertIn(phrase, text, f"{phrase} missing from {path}")

    def test_h1_current_status_can_close_without_expanding_release_scope(self) -> None:
        current_docs = "\n".join(normalized(path) for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST))
        historical_record = normalized(RECORD)

        self.assertIn("does not close H1 or H2", historical_record)
        self.assertIn("closed for public-safe evidence acceptance only", current_docs)
        self.assertIn("H2 | Complete public release/package checklist", normalized(EXECUTION_STATUS))

    def test_record_preserves_pre_alpha_status_and_required_before_status_change(self) -> None:
        text = normalized(RECORD)

        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("Milestone E remains closed only for the current internal source-only prep boundary", text)
        self.assertIn("Required Before Status Change", text)
        self.assertIn("H1 closes with accepted, public-safe competitor comparison evidence", text)
        self.assertIn("H2 closes with an explicitly approved public release/package checklist", text)
        self.assertIn("Release-candidate validation gates pass", text)

    def test_approval_record_is_indexed(self) -> None:
        text = read(VALIDATION_README)

        self.assertEqual(
            1,
            text.count("release-readiness-next-steps-approval-2026-06-20.md"),
        )

    def test_make_target_runs_next_steps_guard_after_prealpha_wording_guard(self) -> None:
        block = target_block("milestone-e-prep")
        wording_guard = "$(PYTHON) .github/scripts/test_public_prealpha_wording_approval.py"
        next_steps_guard = "$(PYTHON) .github/scripts/test_release_readiness_next_steps_approval.py"
        schema_validation = "$(PYTHON) schemas/validate_examples.py"

        self.assertIn(next_steps_guard, block)
        self.assertLess(block.index(wording_guard), block.index(next_steps_guard))
        self.assertLess(block.index(next_steps_guard), block.index(schema_validation))

    def test_ci_runs_next_steps_guard_after_prealpha_wording_guard(self) -> None:
        text = read(CI_WORKFLOW)
        wording_guard = "python3 .github/scripts/test_public_prealpha_wording_approval.py"
        next_steps_guard = "python3 .github/scripts/test_release_readiness_next_steps_approval.py"
        milestone_d = "python3 .github/scripts/test_milestone_d_internal_contracts.py"

        self.assertIn(next_steps_guard, text)
        self.assertEqual(1, text.count(next_steps_guard))
        self.assertLess(text.index(wording_guard), text.index(next_steps_guard))
        self.assertLess(text.index(next_steps_guard), text.index(milestone_d))

    def test_sequence_docs_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            read(path).lower()
            for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RECORD)
        )

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, text)

    def test_record_avoids_local_private_paths(self) -> None:
        text = read(RECORD)

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
