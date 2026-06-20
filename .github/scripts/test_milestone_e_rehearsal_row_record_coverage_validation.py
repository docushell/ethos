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
    "milestone-e-rehearsal-row-record-coverage-validation-2026-06-20.md"
)
MATRIX = ROOT / "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json"
LEDGER = ROOT / "docs/milestone-e-internal-trust-loop-blocker-ledger.json"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

ROW_RECORDS = [
    {
        "step_id": "native-grounding-baseline",
        "record": "milestone-e-native-grounding-baseline-rehearsal-validation-2026-06-19.md",
        "guard": "test_milestone_e_native_grounding_baseline_rehearsal_validation_record.py",
    },
    {
        "step_id": "diagnostic-boundary-check",
        "record": "milestone-e-diagnostic-boundary-check-rehearsal-validation-2026-06-19.md",
        "guard": "test_milestone_e_diagnostic_boundary_check_rehearsal_validation_record.py",
    },
    {
        "step_id": "capability-downgrade-boundary",
        "record": "milestone-e-capability-downgrade-boundary-rehearsal-validation-2026-06-19.md",
        "guard": "test_milestone_e_capability_downgrade_boundary_rehearsal_validation_record.py",
    },
    {
        "step_id": "opendataloader-adapter-grounding",
        "record": "milestone-e-opendataloader-adapter-grounding-rehearsal-validation-2026-06-19.md",
        "guard": "test_milestone_e_opendataloader_adapter_grounding_rehearsal_validation_record.py",
    },
    {
        "step_id": "pinned-opendataloader-fixture-path",
        "record": "milestone-e-pinned-opendataloader-fixture-path-rehearsal-validation-2026-06-19.md",
        "guard": "test_milestone_e_pinned_opendataloader_fixture_path_rehearsal_validation_record.py",
    },
    {
        "step_id": "crop-descriptor-source-bound-shape",
        "record": "milestone-e-crop-descriptor-source-bound-shape-rehearsal-validation-2026-06-20.md",
        "guard": "test_milestone_e_crop_descriptor_source_bound_shape_rehearsal_validation_record.py",
    },
    {
        "step_id": "rag-chunk-artifact-loop",
        "record": "milestone-e-rag-chunk-artifact-loop-rehearsal-validation-2026-06-20.md",
        "guard": "test_milestone_e_rag_chunk_artifact_loop_rehearsal_validation_record.py",
    },
    {
        "step_id": "security-report-artifact-loop",
        "record": "milestone-e-security-report-artifact-loop-rehearsal-validation-2026-06-20.md",
        "guard": "test_milestone_e_security_report_artifact_loop_rehearsal_validation_record.py",
    },
    {
        "step_id": "demo-narrative-index",
        "record": "milestone-e-demo-narrative-index-rehearsal-validation-2026-06-20.md",
        "guard": "test_milestone_e_demo_narrative_index_rehearsal_validation_record.py",
    },
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class MilestoneERehearsalRowRecordCoverageValidationTests(unittest.TestCase):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")
        normalized = re.sub(r"\s+", " ", text)

        self.assertIn(
            "milestone-e-rehearsal-row-record-coverage-validation-2026-06-20.md",
            text,
        )
        self.assertIn(
            "internal Milestone E rehearsal row-record coverage validation",
            normalized,
        )

    def test_record_names_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `3db67e7`", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_rehearsal_row_record_coverage_validation.py",
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
        self.assertIn(
            "git grep <row-record-coverage-forbidden-wording-expression>",
            text,
        )
        self.assertIn(
            "git grep <row-record-coverage-record-private-path-expression>",
            text,
        )
        self.assertIn("git diff --check", text)

    def test_current_matrix_rows_have_record_coverage(self) -> None:
        text = record_text()
        readme = VALIDATION_README.read_text(encoding="utf-8")
        make_block = target_block("milestone-e-prep")
        ci = CI_WORKFLOW.read_text(encoding="utf-8")
        matrix_rows = load_json(MATRIX)["matrix_rows"]
        ledger_rows = load_json(LEDGER)["blocker_rows"]

        self.assertEqual([row["step_id"] for row in matrix_rows], [row["step_id"] for row in ROW_RECORDS])
        self.assertEqual([row["step_id"] for row in ledger_rows], [row["step_id"] for row in ROW_RECORDS])

        for row in ROW_RECORDS:
            guard_command = f"python3 .github/scripts/{row['guard']}"
            make_guard_command = f"$(PYTHON) .github/scripts/{row['guard']}"
            guard_path = ROOT / ".github/scripts" / row["guard"]
            record_path = ROOT / "docs/validation" / row["record"]

            self.assertTrue(guard_path.is_file(), row["guard"])
            self.assertTrue(record_path.is_file(), row["record"])
            self.assertIn(row["step_id"], text)
            self.assertIn(row["record"], text)
            self.assertIn(row["guard"], text)
            self.assertIn(row["record"], readme)
            self.assertIn(make_guard_command, make_block)
            self.assertIn(guard_command, ci)

    def test_record_keeps_source_only_internal_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("current matrix rows", text)
        self.assertIn("indexed row-scoped validation record", text)
        self.assertIn("source-only planning artifacts", text)
        self.assertIn("not_promoted_beyond_internal_fixture_planning", text)
        self.assertIn("does not execute the full walkthrough", text)
        self.assertIn("does not resolve or soften blockers", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)
        self.assertIn("public result wording", text)

    def test_record_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_record_text()
        lowered = text.lower()
        matrix = load_json(MATRIX)

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
        for boundary in matrix["public_boundary"]:
            self.assertIn(boundary, lowered)
        for blocked_output in matrix["blocked_outputs"]:
            self.assertIn(blocked_output, lowered)

    def test_make_target_runs_coverage_guard_after_last_row_record(self) -> None:
        block = target_block("milestone-e-prep")

        last_row_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_demo_narrative_index_rehearsal_validation_record.py"
        )
        coverage_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_rehearsal_row_record_coverage_validation.py"
        )
        prep_record_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py"

        self.assertIn(last_row_guard, block)
        self.assertIn(coverage_guard, block)
        self.assertIn(prep_record_guard, block)
        self.assertLess(block.index(last_row_guard), block.index(coverage_guard))
        self.assertLess(block.index(coverage_guard), block.index(prep_record_guard))
        self.assertLess(block.index(coverage_guard), block.index("git diff --check"))

    def test_ci_runs_coverage_guard_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        last_row_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_demo_narrative_index_rehearsal_validation_record.py"
        )
        coverage_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_rehearsal_row_record_coverage_validation.py"
        )
        prep_record_guard = "python3 .github/scripts/test_milestone_e_prep_validation_record.py"

        self.assertIn(coverage_guard, text)
        self.assertEqual(1, text.count(coverage_guard))
        self.assertLess(text.index(last_row_guard), text.index(coverage_guard))
        self.assertLess(text.index(coverage_guard), text.index(prep_record_guard))

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
