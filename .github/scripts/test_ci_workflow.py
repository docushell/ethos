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

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


def workflow_text() -> str:
    return CI_WORKFLOW.read_text(encoding="utf-8")


class CiWorkflowTests(unittest.TestCase):
    def test_alpha_fixture_and_layout_gates_run_in_pr_ci(self) -> None:
        text = workflow_text()

        self.assertIn("python3 fixtures/validate_fixtures.py", text)
        self.assertIn("make layout-evaluator-alpha", text)
        self.assertIn("PYTHONPATH=python python3 -m unittest discover -s python/tests", text)

    def test_schema_job_installs_jsonschema_and_validates_examples(self) -> None:
        text = workflow_text()

        self.assertIn('pip install "jsonschema>=4.18"', text)
        self.assertIn("python3 schemas/validate_examples.py", text)
        self.assertIn("python3 schemas/test_security_report_validation.py", text)
        self.assertIn("python3 schemas/test_table_model_validation.py", text)

    def test_ci_workflow_guard_is_run_by_ci(self) -> None:
        text = workflow_text()

        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_b_internal_checks.py", text)
        self.assertIn("python3 .github/scripts/test_rag_chunk_alpha.py", text)
        self.assertIn("python3 .github/scripts/test_security_report_alpha.py", text)
        self.assertIn("python3 .github/scripts/test_execution_status.py", text)
        self.assertIn("python3 .github/scripts/test_roadmap_status.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_d_internal_contracts.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_b_closeout_record.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_c_closeout_record.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_d_closeout_prep_record.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_d_closeout_record.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_d_final_closeout_record.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_e_schema_registry_alignment.py", text)
        self.assertEqual(
            1,
            text.count("python3 .github/scripts/test_milestone_e_schema_registry_alignment.py"),
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_public_boundary_alignment.py", text)
        self.assertEqual(
            1,
            text.count("python3 .github/scripts/test_milestone_e_public_boundary_alignment.py"),
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertEqual(1, text.count("python3 .github/scripts/test_milestone_e_prep_scope.py"))
        self.assertLess(
            text.index("python3 .github/scripts/test_milestone_e_schema_registry_alignment.py"),
            text.index("python3 .github/scripts/test_milestone_e_public_boundary_alignment.py"),
        )
        self.assertLess(
            text.index("python3 .github/scripts/test_milestone_e_public_boundary_alignment.py"),
            text.index("python3 .github/scripts/test_milestone_e_prep_scope.py"),
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py", text)
        self.assertEqual(
            1,
            text.count("python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py"),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py"
            ),
        )
        self.assertLess(
            text.index("python3 .github/scripts/test_milestone_e_fixture_promotion_criteria.py"),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_prep_scope_structured_blocker_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_prep_scope_structured_blocker_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_prep_scope_structured_blocker_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_prep_scope_structured_blocker_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py"
            ),
            text.index(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py"
            ),
            text.index(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_blocker_ledger.py"
            ),
            text.index("python3 .github/scripts/test_milestone_e_fixture_promotion_criteria_validation_record.py"),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_walkthrough_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_walkthrough_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py"
            ),
            text.index("python3 .github/scripts/test_milestone_e_fixture_promotion_criteria_validation_record.py"),
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_fixture_promotion_criteria_validation_record.py",
            text,
        )
        self.assertLess(
            text.index("python3 .github/scripts/test_milestone_e_fixture_promotion_criteria_validation_record.py"),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_walkthrough_validation_record.py"
            ),
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_fixture_promotion_criteria_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_walkthrough_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_blocker_ledger_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_blocker_ledger_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_blocker_ledger_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_internal_trust_loop_blocker_ledger_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_demo_narrative_index_rehearsal_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_demo_narrative_index_rehearsal_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_demo_narrative_index_rehearsal_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_demo_narrative_index_rehearsal_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_rehearsal_row_record_coverage_validation.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_rehearsal_row_record_coverage_validation.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_rehearsal_row_record_coverage_validation.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_rehearsal_row_record_coverage_validation.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_schema_registry_alignment_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_schema_registry_alignment_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_schema_registry_alignment_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_schema_registry_alignment_validation_record.py"
            ),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_public_boundary_alignment_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_public_boundary_alignment_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_public_boundary_alignment_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_public_boundary_alignment_validation_record.py"
            ),
            text.index("python3 .github/scripts/test_milestone_e_validation_record_index.py"),
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_validation_record_index.py", text)
        self.assertEqual(
            1,
            text.count("python3 .github/scripts/test_milestone_e_validation_record_index.py"),
        )
        self.assertLess(
            text.index("python3 .github/scripts/test_milestone_e_validation_record_index.py"),
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_validation_record_index_validation_record.py"
            ),
        )
        self.assertIn(
            "python3 .github/scripts/"
            "test_milestone_e_validation_record_index_validation_record.py",
            text,
        )
        self.assertEqual(
            1,
            text.count(
                "python3 .github/scripts/"
                "test_milestone_e_validation_record_index_validation_record.py"
            ),
        )
        self.assertLess(
            text.index(
                "python3 .github/scripts/"
                "test_milestone_e_validation_record_index_validation_record.py"
            ),
            text.index("python3 .github/scripts/test_milestone_e_prep_validation_record.py"),
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_validation_record.py", text)
        self.assertEqual(
            1,
            text.count("python3 .github/scripts/test_milestone_e_prep_validation_record.py"),
        )
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_b_exit_checklist.py", text)


if __name__ == "__main__":
    unittest.main()
