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
    "milestone-e-internal-trust-loop-rehearsal-evidence-matrix-validation-2026-06-19.md"
)
MATRIX = ROOT / "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


def record_text() -> str:
    return RECORD.read_text(encoding="utf-8")


def normalized_record_text() -> str:
    return re.sub(r"\s+", " ", record_text())


class MilestoneEInternalTrustLoopRehearsalEvidenceMatrixValidationRecordTests(
    unittest.TestCase
):
    def test_record_is_indexed(self) -> None:
        text = VALIDATION_README.read_text(encoding="utf-8")
        normalized = re.sub(r"\s+", " ", text)

        self.assertIn(
            "milestone-e-internal-trust-loop-rehearsal-evidence-matrix-validation-2026-06-19.md",
            text,
        )
        self.assertIn(
            "internal Milestone E trust-loop rehearsal/evidence matrix validation",
            normalized,
        )
        self.assertIn(
            "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            text,
        )

    def test_record_names_validation_commands(self) -> None:
        text = record_text()

        self.assertIn("Validated source HEAD before this record: `8f0206d`", text)
        self.assertIn(
            "python3 -m json.tool docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            text,
        )
        self.assertIn(
            "python3 -m json.tool schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
            text,
        )
        self.assertIn("<jsonschema-venv>/bin/python schemas/validate_examples.py", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol_validation_record.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)
        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git grep <matrix-forbidden-wording-expression>", text)
        self.assertIn("git grep <matrix-record-private-path-expression>", text)
        self.assertIn("git diff --check", text)

    def test_record_keeps_source_only_internal_scope(self) -> None:
        text = normalized_record_text()

        self.assertIn(
            "pass for internal Milestone E trust-loop rehearsal/evidence matrix validation",
            text,
        )
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("internal evidence lanes for rehearsal planning", text)
        self.assertIn("does not move any fixture beyond internal planning", text)
        self.assertIn("evidence grounding", text)
        self.assertIn("diagnostics", text)
        self.assertIn("fixture/evaluator validation", text)
        self.assertIn("explicit blockers", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)
        self.assertIn("source-only-pre-alpha-internal-milestone-e-prep", text)
        self.assertIn("internal_trust_loop_rehearsal_evidence_matrix", text)
        self.assertIn("internal_source_only_rehearsal_evidence_matrix", text)
        self.assertIn(
            "internal_source_only_rehearsal_evidence_matrix_defined_not_executed",
            text,
        )
        self.assertIn("internal_source_only_rehearsal_defined_not_promoted", text)
        self.assertIn("not_promoted_beyond_internal_fixture_planning", text)
        self.assertIn("docs/milestone-e-fixture-candidates.json", text)
        self.assertIn("docs/milestone-e-fixture-promotion-criteria.json", text)
        self.assertIn("docs/milestone-e-internal-trust-loop-walkthrough.json", text)
        self.assertIn("docs/milestone-e-internal-trust-loop-use-protocol.json", text)
        self.assertIn(
            "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            text,
        )

    def test_record_keeps_public_boundaries_explicit(self) -> None:
        text = normalized_record_text()
        lowered = text.lower()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

        self.assertIn("does not promote any fixture", text)
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

    def test_record_covers_every_matrix_row(self) -> None:
        text = normalized_record_text()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

        for row in matrix["matrix_rows"]:
            self.assertIn(row["step_id"], text)
            self.assertIn(row["candidate_id"], text)
            self.assertIn(row["validation_command_must_pass"], text)
            self.assertIn(row["diagnostic_boundary_must_remain"], text)
            for path in row["required_input_fixtures"]:
                self.assertIn(path, text)
            for blocker in row["blockers_must_remain_explicit"]:
                self.assertIn(blocker, text)
            for lane in row["evidence_matrix_lanes"]:
                self.assertIn(lane, text)

    def test_record_names_validated_matrix_boundary(self) -> None:
        text = normalized_record_text()

        self.assertIn("The matrix stays source-only, internal, and non-public", text)
        self.assertIn("The matrix references only current protocol step ids", text)
        self.assertIn("Each matrix row exactly matches its protocol step", text)
        self.assertIn("Each matrix row exactly matches its walkthrough step and criteria entry", text)
        self.assertIn("Required input fixtures are relative, tracked, and path-backed", text)
        self.assertIn("Validation commands are existing allowlisted Make targets", text)
        self.assertIn(
            "Evidence lanes are exactly evidence grounding, diagnostics, fixture/evaluator validation, and explicit blockers",
            text,
        )
        self.assertIn("Schema validation covers the matrix plan and schema", text)
        self.assertIn("Public boundaries remain explicit and blocked", text)

    def test_make_target_runs_record_guard_after_matrix_guard(self) -> None:
        block = target_block("milestone-e-prep")

        protocol_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py"
        )
        matrix_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py"
        )
        protocol_record_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py"
        )
        record_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py"
        )
        prep_record_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_validation_record.py"
        self.assertIn(protocol_guard, block)
        self.assertIn(matrix_guard, block)
        self.assertIn(protocol_record_guard, block)
        self.assertIn(record_guard, block)
        self.assertIn(prep_record_guard, block)
        self.assertLess(block.index(protocol_guard), block.index(matrix_guard))
        self.assertLess(block.index(matrix_guard), block.index(protocol_record_guard))
        self.assertLess(block.index(protocol_record_guard), block.index(record_guard))
        self.assertLess(block.index(record_guard), block.index(prep_record_guard))
        self.assertLess(block.index(record_guard), block.index("git diff --check"))

    def test_ci_runs_record_guard_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        matrix_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py"
        )
        protocol_record_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py"
        )
        record_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py"
        )
        prep_record_guard = "python3 .github/scripts/test_milestone_e_prep_validation_record.py"

        self.assertIn(record_guard, text)
        self.assertEqual(1, text.count(record_guard))
        self.assertLess(text.index(matrix_guard), text.index(protocol_record_guard))
        self.assertLess(text.index(protocol_record_guard), text.index(record_guard))
        self.assertLess(text.index(record_guard), text.index(prep_record_guard))

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
