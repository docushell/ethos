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
    "milestone-e-diagnostic-boundary-check-rehearsal-validation-2026-06-19.md"
)
MATRIX = ROOT / "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json"
LEDGER = ROOT / "docs/milestone-e-internal-trust-loop-blocker-ledger.json"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

STEP_ID = "diagnostic-boundary-check"
OTHER_STEP_IDS = [
    "native-grounding-baseline",
    "capability-downgrade-boundary",
    "opendataloader-adapter-grounding",
    "pinned-opendataloader-fixture-path",
    "crop-descriptor-source-bound-shape",
    "rag-chunk-artifact-loop",
    "security-report-artifact-loop",
    "demo-narrative-index",
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


def row_from(path: Path, key: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload[key]
    matches = [row for row in rows if row["step_id"] == STEP_ID]
    assert len(matches) == 1
    return matches[0]


class MilestoneEDiagnosticBoundaryCheckRehearsalValidationRecordTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")
        normalized = re.sub(r"\s+", " ", text)

        self.assertIn(
            "milestone-e-diagnostic-boundary-check-rehearsal-validation-2026-06-19.md",
            text,
        )
        self.assertIn(
            "internal Milestone E diagnostic-boundary-check rehearsal validation",
            normalized,
        )
        self.assertIn(STEP_ID, text)

    def test_record_names_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `483771c`", text)
        self.assertIn("make verify-alpha PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git grep <diagnostic-boundary-check-forbidden-wording-expression>", text)
        self.assertIn("git grep <diagnostic-boundary-check-record-private-path-expression>", text)
        self.assertIn("git diff --check", text)

    def test_record_covers_only_diagnostic_boundary_check(self) -> None:
        text = normalized_record_text()
        self.assertIn(STEP_ID, text)
        for step_id in OTHER_STEP_IDS:
            self.assertNotIn(step_id, text)

    def test_record_matches_matrix_and_ledger_row(self) -> None:
        text = normalized_record_text()
        matrix_row = row_from(MATRIX, "matrix_rows")
        ledger_row = row_from(LEDGER, "blocker_rows")

        self.assertEqual(matrix_row["candidate_id"], ledger_row["candidate_id"])
        self.assertEqual(matrix_row["validation_command_must_pass"], ledger_row["validation_command_must_pass"])
        self.assertEqual(matrix_row["required_input_fixtures"], ledger_row["required_input_fixtures"])
        self.assertEqual(
            matrix_row["diagnostic_boundary_must_remain"],
            ledger_row["diagnostic_boundary_must_remain"],
        )
        self.assertEqual(
            matrix_row["blockers_must_remain_explicit"],
            ledger_row["explicit_blockers_must_remain"],
        )

        self.assertIn(matrix_row["candidate_id"], text)
        self.assertIn(matrix_row["validation_command_must_pass"], text)
        self.assertIn(matrix_row["diagnostic_boundary_must_remain"], text)
        self.assertIn(matrix_row["promotion_status"], text)
        for path in matrix_row["required_input_fixtures"]:
            self.assertIn(path, text)
        for lane in matrix_row["evidence_matrix_lanes"]:
            self.assertIn(lane, text)
        for blocker in matrix_row["blockers_must_remain_explicit"]:
            self.assertIn(blocker, text)

    def test_record_keeps_source_only_internal_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("source-only planning artifacts", text)
        self.assertIn("not_promoted_beyond_internal_fixture_planning", text)
        self.assertIn("does not execute the full walkthrough", text)
        self.assertIn("does not resolve or soften blockers", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)
        self.assertIn("public result wording", text)
        self.assertIn("future claim-kind expansion", text)

    def test_make_target_runs_record_guard_after_native_row_record(self) -> None:
        block = target_block("milestone-e-prep")

        native_row_record_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py"
        )
        row_record_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py"
        )
        prep_record_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py"

        self.assertIn(native_row_record_guard, block)
        self.assertIn(row_record_guard, block)
        self.assertIn(prep_record_guard, block)
        self.assertLess(block.index(native_row_record_guard), block.index(row_record_guard))
        self.assertLess(block.index(row_record_guard), block.index(prep_record_guard))
        self.assertLess(block.index(row_record_guard), block.index("git diff --check"))

    def test_ci_runs_record_guard_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        native_row_record_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py"
        )
        row_record_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py"
        )
        prep_record_guard = "python3 .github/scripts/test_milestone_e_prep_validation_record.py"

        self.assertIn(row_record_guard, text)
        self.assertEqual(1, text.count(row_record_guard))
        self.assertLess(text.index(native_row_record_guard), text.index(row_record_guard))
        self.assertLess(text.index(row_record_guard), text.index(prep_record_guard))

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
