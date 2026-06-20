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
from dataclasses import dataclass
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
VALIDATION_DIR = ROOT / "docs/validation"
VALIDATION_README = VALIDATION_DIR / "README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


@dataclass(frozen=True)
class RecordCoverage:
    record: str
    guard: str


EXPECTED_RECORDS = (
    RecordCoverage(
        "milestone-e-prep-validation-2026-06-19.md",
        "test_milestone_e_prep_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-fixture-promotion-criteria-validation-2026-06-19.md",
        "test_milestone_e_fixture_promotion_criteria_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-fixture-candidate-blocker-alignment-validation-2026-06-20.md",
        "test_milestone_e_fixture_candidate_blocker_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-prep-scope-structured-blocker-validation-2026-06-20.md",
        "test_milestone_e_prep_scope_structured_blocker_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-internal-trust-loop-walkthrough-validation-2026-06-19.md",
        "test_milestone_e_validation_record_index.py",
    ),
    RecordCoverage(
        "milestone-e-internal-trust-loop-walkthrough-all-candidates-validation-2026-06-19.md",
        "test_milestone_e_internal_trust_loop_walkthrough_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-internal-trust-loop-use-protocol-validation-2026-06-19.md",
        "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-internal-trust-loop-rehearsal-evidence-matrix-validation-2026-06-19.md",
        "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-internal-trust-loop-blocker-ledger-validation-2026-06-19.md",
        "test_milestone_e_internal_trust_loop_blocker_ledger_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-native-grounding-baseline-rehearsal-validation-2026-06-19.md",
        "test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-diagnostic-boundary-check-rehearsal-validation-2026-06-19.md",
        "test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-capability-downgrade-boundary-rehearsal-validation-2026-06-19.md",
        "test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-opendataloader-adapter-grounding-rehearsal-validation-2026-06-19.md",
        "test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-pinned-opendataloader-fixture-path-rehearsal-validation-2026-06-19.md",
        "test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-crop-descriptor-source-bound-shape-rehearsal-validation-2026-06-20.md",
        "test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-rag-chunk-artifact-loop-rehearsal-validation-2026-06-20.md",
        "test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-security-report-artifact-loop-rehearsal-validation-2026-06-20.md",
        "test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-demo-narrative-index-rehearsal-validation-2026-06-20.md",
        "test_milestone_e_demo_narrative_index_rehearsal_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-rehearsal-row-record-coverage-validation-2026-06-20.md",
        "test_milestone_e_rehearsal_row_record_coverage_validation.py",
    ),
    RecordCoverage(
        "milestone-e-schema-registry-alignment-validation-2026-06-20.md",
        "test_milestone_e_schema_registry_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-public-boundary-alignment-validation-2026-06-20.md",
        "test_milestone_e_public_boundary_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-blocked-output-alignment-validation-2026-06-20.md",
        "test_milestone_e_blocked_output_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-evidence-lane-alignment-validation-2026-06-20.md",
        "test_milestone_e_evidence_lane_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-diagnostic-boundary-alignment-validation-2026-06-20.md",
        "test_milestone_e_diagnostic_boundary_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-promotion-status-alignment-validation-2026-06-20.md",
        "test_milestone_e_promotion_status_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-source-status-alignment-validation-2026-06-20.md",
        "test_milestone_e_source_status_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-applies-to-binding-alignment-validation-2026-06-20.md",
        "test_milestone_e_applies_to_binding_alignment_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-validation-command-index-validation-2026-06-20.md",
        "test_milestone_e_validation_command_index_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-validation-record-index-validation-2026-06-20.md",
        "test_milestone_e_validation_record_index_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-prep-guard-sequence-index-validation-2026-06-20.md",
        "test_milestone_e_prep_guard_sequence_index_validation_record.py",
    ),
    RecordCoverage(
        "milestone-e-prep-current-guard-validation-2026-06-20.md",
        "test_milestone_e_prep_validation_record.py",
    ),
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class MilestoneEValidationRecordIndexTests(unittest.TestCase):
    def test_record_files_match_index(self) -> None:
        discovered = {
            path.name
            for path in VALIDATION_DIR.glob("milestone-e-*-validation-*.md")
        }
        expected = {entry.record for entry in EXPECTED_RECORDS}

        self.assertEqual(expected, discovered)

    def test_validation_readme_indexes_every_record_once(self) -> None:
        readme = read(VALIDATION_README)
        indexed = re.findall(r"`(milestone-e-[^`]+-validation-[0-9-]+\.md)`", readme)

        self.assertEqual({entry.record for entry in EXPECTED_RECORDS}, set(indexed))
        for entry in EXPECTED_RECORDS:
            self.assertEqual(1, indexed.count(entry.record), entry.record)

    def test_coverage_guards_exist_and_run_in_prep_target(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        guard_names = {entry.guard for entry in EXPECTED_RECORDS}

        for guard in guard_names:
            guard_path = ROOT / ".github/scripts" / guard
            self.assertTrue(guard_path.is_file(), guard)
            self.assertIn(f"$(PYTHON) .github/scripts/{guard}", make_block, guard)
            self.assertIn(f"python3 .github/scripts/{guard}", ci, guard)

    def test_index_guards_run_after_row_and_schema_records(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)

        row_guard = "test_milestone_e_rehearsal_row_record_coverage_validation.py"
        schema_guard = "test_milestone_e_schema_registry_alignment_validation_record.py"
        blocked_output_guard = "test_milestone_e_blocked_output_alignment_validation_record.py"
        evidence_lane_guard = "test_milestone_e_evidence_lane_alignment_validation_record.py"
        diagnostic_boundary_guard = "test_milestone_e_diagnostic_boundary_alignment_validation_record.py"
        promotion_status_guard = "test_milestone_e_promotion_status_alignment_validation_record.py"
        source_status_guard = "test_milestone_e_source_status_alignment_validation_record.py"
        applies_to_guard = "test_milestone_e_applies_to_binding_alignment_validation_record.py"
        command_guard = "test_milestone_e_validation_command_index_validation_record.py"
        index_guard = "test_milestone_e_validation_record_index.py"
        index_record_guard = "test_milestone_e_validation_record_index_validation_record.py"
        sequence_guard = "test_milestone_e_prep_guard_sequence_index_validation_record.py"
        prep_record_guard = "test_milestone_e_prep_validation_record.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertLess(text.index(prefix + row_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + schema_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + blocked_output_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + evidence_lane_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + diagnostic_boundary_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + promotion_status_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + source_status_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + applies_to_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + command_guard), text.index(prefix + index_guard))
            self.assertLess(text.index(prefix + index_guard), text.index(prefix + index_record_guard))
            self.assertLess(text.index(prefix + index_record_guard), text.index(prefix + sequence_guard))
            self.assertLess(text.index(prefix + sequence_guard), text.index(prefix + prep_record_guard))

    def test_records_keep_source_only_public_boundaries(self) -> None:
        for entry in EXPECTED_RECORDS:
            text = read(VALIDATION_DIR / entry.record)
            self.assertIn("Ethos remains source-only pre-alpha", text, entry.record)
            self.assertIn("Public reports remain blocked", text, entry.record)
            self.assertIn("Public result wording remains blocked", text, entry.record)


if __name__ == "__main__":
    unittest.main()
