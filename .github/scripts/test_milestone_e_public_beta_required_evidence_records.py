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
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
PREP = ROOT / "docs/milestone-e-public-beta-approval-prep.json"
LEDGER = ROOT / "docs/milestone-e-public-approval-lane-blockers.json"

RECORDS = (
    "milestone-e-public-beta-approval-decision-validation-2026-06-20.md",
    "milestone-e-public-beta-release-scope-engineering-blocker-review-validation-2026-06-20.md",
    "milestone-e-public-beta-public-setup-path-review-validation-2026-06-20.md",
    "milestone-e-public-beta-pdfium-build-path-review-validation-2026-06-20.md",
)

FORBIDDEN_RECORD_WORDING = [
    "public beta is approved",
    "public beta approved",
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class MilestoneEPublicBetaRequiredEvidenceRecordTests(unittest.TestCase):
    def test_required_evidence_records_are_indexed(self) -> None:
        readme = read(VALIDATION_README)

        for record in RECORDS:
            self.assertIn(record, readme)
        self.assertIn("internal Milestone E public beta required-evidence validation", readme)

    def test_records_keep_public_beta_blocked(self) -> None:
        for record in RECORDS:
            path = ROOT / "docs/validation" / record
            text = normalized(path)
            lower = text.lower()

            self.assertIn("Validated source HEAD before this record: `3a104a2`", text, record)
            self.assertIn("Ethos remains source-only pre-alpha", text, record)
            self.assertIn("Public beta remains blocked", text, record)
            self.assertIn("does not approve public beta", lower, record)
            self.assertIn("does not resolve or soften blockers", lower, record)
            self.assertIn("Public reports remain blocked", text, record)
            self.assertIn("Public result wording remains blocked", text, record)

    def test_records_name_validation_commands(self) -> None:
        for record in RECORDS:
            text = read(ROOT / "docs/validation" / record)

            self.assertIn(
                "python3 .github/scripts/test_milestone_e_public_beta_required_evidence_records.py",
                text,
                record,
            )
            self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text, record)
            self.assertIn("python3 .github/scripts/claims_gate.py", text, record)
            self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text, record)
            self.assertIn("git diff --check", text, record)

    def test_prep_and_lane_blockers_reflect_reviewed_but_blocked_state(self) -> None:
        prep = read(PREP)
        ledger = read(LEDGER)
        expected = "release-scope engineering blocker review did not clear public beta"

        self.assertIn(expected, prep)
        self.assertIn(expected, ledger)
        self.assertNotIn("release-scope validation record remains absent", prep)
        self.assertNotIn("release-scope validation record remains absent", ledger)

    def test_make_target_runs_required_evidence_after_public_beta_prep(self) -> None:
        block = target_block("milestone-e-prep")

        beta_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py"
        )
        evidence_guard = "$(PYTHON) .github/scripts/test_milestone_e_public_beta_required_evidence_records.py"
        package_guard = "$(PYTHON) .github/scripts/test_milestone_e_package_publication_approval_prep.py"
        index_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(evidence_guard, block)
        self.assertLess(block.index(beta_record), block.index(evidence_guard))
        self.assertLess(block.index(evidence_guard), block.index(package_guard))
        self.assertLess(block.index(evidence_guard), block.index(index_guard))
        self.assertLess(block.index(evidence_guard), block.index("git diff --check"))

    def test_ci_runs_required_evidence_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        beta_record = (
            "python3 .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py"
        )
        evidence_guard = "python3 .github/scripts/test_milestone_e_public_beta_required_evidence_records.py"
        package_guard = "python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py"
        index_guard = "python3 .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(evidence_guard, text)
        self.assertEqual(1, text.count(evidence_guard))
        self.assertLess(text.index(beta_record), text.index(evidence_guard))
        self.assertLess(text.index(evidence_guard), text.index(package_guard))
        self.assertLess(text.index(evidence_guard), text.index(index_guard))

    def test_records_avoid_scope_expansion_language(self) -> None:
        for record in RECORDS:
            text = normalized(ROOT / "docs/validation" / record).lower()

            for phrase in FORBIDDEN_RECORD_WORDING:
                self.assertNotIn(phrase, text, record)

    def test_records_avoid_local_private_paths(self) -> None:
        for record in RECORDS:
            text = read(ROOT / "docs/validation" / record)

            self.assertNotIn("/Users/", text, record)
            self.assertNotIn("/private/tmp", text, record)
            self.assertNotIn("/private/var", text, record)
            self.assertNotIn("/var/folders", text, record)
            self.assertNotIn("saumildiwaker", text, record)
            self.assertNotIn("Desktop/Stuff", text, record)
            self.assertNotIn("project/repo/ethos", text, record)
            self.assertNotIn("docs/.roadmap.md.swp", text, record)
            self.assertNotIn("web/", text, record)


if __name__ == "__main__":
    unittest.main()
