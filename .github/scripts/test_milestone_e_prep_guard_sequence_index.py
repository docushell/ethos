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
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"

EXPECTED_MILESTONE_E_PREP_COMMANDS = (
    "$(PYTHON) .github/scripts/test_execution_status.py",
    "$(PYTHON) .github/scripts/test_roadmap_status.py",
    "$(PYTHON) .github/scripts/test_public_surface_posture.py",
    "$(PYTHON) .github/scripts/claims_gate.py",
    "$(PYTHON) schemas/validate_examples.py",
    "$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment.py",
    "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment.py",
    "$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment.py",
    "$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment.py",
    "$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_alignment.py",
    "$(PYTHON) .github/scripts/test_milestone_e_promotion_status_alignment.py",
    "$(PYTHON) .github/scripts/test_milestone_e_source_status_alignment.py",
    "$(PYTHON) .github/scripts/test_milestone_e_applies_to_binding_alignment.py",
    "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py",
    "$(PYTHON) .github/scripts/test_milestone_e_fixture_promotion_criteria.py",
    "$(PYTHON) .github/scripts/test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_prep_scope_structured_blocker_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py",
    "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py",
    "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py",
    "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py",
    "$(PYTHON) .github/scripts/test_milestone_e_fixture_promotion_criteria_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_walkthrough_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_use_protocol_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_demo_narrative_index_rehearsal_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_rehearsal_row_record_coverage_validation.py",
    "$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_promotion_status_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_source_status_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_applies_to_binding_alignment_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_validation_command_index.py",
    "$(PYTHON) .github/scripts/test_milestone_e_validation_command_index_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py",
    "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_prep_guard_sequence_index.py",
    "$(PYTHON) .github/scripts/test_milestone_e_prep_guard_sequence_index_validation_record.py",
    "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py",
    "git diff --check",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def milestone_e_make_script_commands() -> list[str]:
    return [
        command
        for command in EXPECTED_MILESTONE_E_PREP_COMMANDS
        if command.startswith("$(PYTHON) .github/scripts/test_milestone_e_")
    ]


def milestone_e_ci_script_commands() -> list[str]:
    text = read(CI_WORKFLOW)
    return re.findall(r"run: (python3 \.github/scripts/test_milestone_e_[A-Za-z0-9_]+\.py)", text)


class MilestoneEPrepGuardSequenceIndexTests(unittest.TestCase):
    def test_make_target_matches_exact_guard_sequence(self) -> None:
        block = target_block("milestone-e-prep")
        commands = [line.strip() for line in block.splitlines() if line.strip()]

        self.assertEqual(list(EXPECTED_MILESTONE_E_PREP_COMMANDS), commands)
        self.assertEqual("git diff --check", commands[-1])

    def test_ci_runs_same_milestone_e_guard_scripts_in_order(self) -> None:
        expected_ci = [
            command.replace("$(PYTHON)", "python3")
            for command in milestone_e_make_script_commands()
        ]
        actual_ci = milestone_e_ci_script_commands()

        self.assertEqual(expected_ci, actual_ci)
        for command in expected_ci:
            self.assertEqual(1, actual_ci.count(command), command)

    def test_guard_sequence_index_runs_before_prep_validation_record(self) -> None:
        block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)

        index_record_guard = "test_milestone_e_validation_record_index_validation_record.py"
        sequence_guard = "test_milestone_e_prep_guard_sequence_index.py"
        sequence_record_guard = "test_milestone_e_prep_guard_sequence_index_validation_record.py"
        prep_record_guard = "test_milestone_e_prep_validation_record.py"

        for text, prefix in ((block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertLess(text.index(prefix + index_record_guard), text.index(prefix + sequence_guard))
            self.assertLess(text.index(prefix + sequence_guard), text.index(prefix + sequence_record_guard))
            self.assertLess(text.index(prefix + sequence_record_guard), text.index(prefix + prep_record_guard))

    def test_docs_name_guard_sequence_index_without_scope_expansion(self) -> None:
        prep_scope = read(PREP_SCOPE)
        execution_status = read(EXECUTION_STATUS)

        for text in (prep_scope, execution_status):
            normalized = re.sub(r"\s+", " ", text)
            self.assertIn("prep guard-sequence index", normalized)
            self.assertIn("blocked-output alignment", normalized)
            self.assertIn("evidence-lane alignment", normalized)
            self.assertIn("diagnostic-boundary alignment", normalized)
            self.assertIn("promotion-status alignment", normalized)
            self.assertIn("source-status alignment", normalized)
            self.assertIn("applies-to binding alignment", normalized)
            self.assertIn("source-only", normalized)
            self.assertIn("public-report, release, package, hosted", normalized)
            self.assertNotIn("public result wording approved", normalized.lower())
            self.assertNotIn("release-ready", normalized.lower())
            self.assertNotIn("production-ready", normalized.lower())


if __name__ == "__main__":
    unittest.main()
