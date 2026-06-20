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
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
VALIDATION_DIR = ROOT / "docs/validation"

FORBIDDEN_ARTIFACT_WORDING = [
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


@dataclass(frozen=True)
class DiagnosticBoundaryRow:
    step_id: str
    candidate_id: str
    label: str
    boundary: str
    record: str


@dataclass(frozen=True)
class DiagnosticBoundaryArtifact:
    artifact: str
    schema: str
    row_key: str
    id_key: str
    boundary_key: str
    schema_def: str


EXPECTED_ROWS = (
    DiagnosticBoundaryRow(
        "native-grounding-baseline",
        "native-verification-trust-loop",
        "Native verification trust loop",
        "Native quote, table-cell, and presence evidence checks over checked-in document JSON.",
        "milestone-e-native-grounding-baseline-rehearsal-validation-2026-06-19.md",
    ),
    DiagnosticBoundaryRow(
        "diagnostic-boundary-check",
        "split-quote-unsupported-claim-diagnostics",
        "Split-quote and unsupported-claim diagnostics",
        "Adjacent native text evidence matching and explicit unsupported non-v1 claim diagnostics.",
        "milestone-e-diagnostic-boundary-check-rehearsal-validation-2026-06-19.md",
    ),
    DiagnosticBoundaryRow(
        "capability-downgrade-boundary",
        "capability-downgrade-diagnostics",
        "Capability downgrade diagnostics",
        "Grounding-source capability limits surface as warnings and capability-blocked checks.",
        "milestone-e-capability-downgrade-boundary-rehearsal-validation-2026-06-19.md",
    ),
    DiagnosticBoundaryRow(
        "opendataloader-adapter-grounding",
        "opendataloader-style-adapter-grounding",
        "OpenDataLoader-style adapter grounding",
        "OpenDataLoader-style input shape maps to parser-neutral grounding metadata with deterministic adapter diagnostics.",
        "milestone-e-opendataloader-adapter-grounding-rehearsal-validation-2026-06-19.md",
    ),
    DiagnosticBoundaryRow(
        "pinned-opendataloader-fixture-path",
        "pinned-real-opendataloader-fixture-path",
        "Pinned real OpenDataLoader fixture path",
        "Pinned foreign output exercises grounded and ungrounded verification paths without public comparison wording.",
        "milestone-e-pinned-opendataloader-fixture-path-rehearsal-validation-2026-06-19.md",
    ),
    DiagnosticBoundaryRow(
        "crop-descriptor-source-bound-shape",
        "crop-descriptor-source-bound-crop-shape",
        "Crop descriptor and source-bound crop shape",
        "Source-bound crop descriptor identity and callable CLI/Python surface shape remain tied to current request and descriptor schemas.",
        "milestone-e-crop-descriptor-source-bound-shape-rehearsal-validation-2026-06-20.md",
    ),
    DiagnosticBoundaryRow(
        "rag-chunk-artifact-loop",
        "rag-chunk-artifact-loop",
        "RAG chunk artifact loop",
        "RAG chunk output stays fixture-backed with stale-reference and warning-reference validation.",
        "milestone-e-rag-chunk-artifact-loop-rehearsal-validation-2026-06-20.md",
    ),
    DiagnosticBoundaryRow(
        "security-report-artifact-loop",
        "security-report-artifact-loop",
        "Security-report artifact loop",
        "Security-report output stays source-grounded with locator, warning-lane, and summary diagnostics.",
        "milestone-e-security-report-artifact-loop-rehearsal-validation-2026-06-20.md",
    ),
    DiagnosticBoundaryRow(
        "demo-narrative-index",
        "demo-narrative-index",
        "Demo narrative index",
        "Existing narrative index remains tied to checked-in alpha verification fixtures and posture guards.",
        "milestone-e-demo-narrative-index-rehearsal-validation-2026-06-20.md",
    ),
)

DIAGNOSTIC_BOUNDARY_ARTIFACTS = (
    DiagnosticBoundaryArtifact(
        "docs/milestone-e-fixture-candidates.json",
        "schemas/ethos-milestone-e-fixture-candidates.schema.json",
        "fixture_candidates",
        "id",
        "expected_diagnostic_boundary",
        "fixture_candidate",
    ),
    DiagnosticBoundaryArtifact(
        "docs/milestone-e-fixture-promotion-criteria.json",
        "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json",
        "criteria",
        "candidate_id",
        "diagnostic_boundary_must_remain",
        "criteria_case",
    ),
    DiagnosticBoundaryArtifact(
        "docs/milestone-e-internal-trust-loop-walkthrough.json",
        "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
        "walkthrough_steps",
        "candidate_id",
        "diagnostic_boundary_must_remain",
        "walkthrough_step",
    ),
    DiagnosticBoundaryArtifact(
        "docs/milestone-e-internal-trust-loop-use-protocol.json",
        "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
        "protocol_steps",
        "candidate_id",
        "diagnostic_boundary_must_remain",
        "protocol_step",
    ),
    DiagnosticBoundaryArtifact(
        "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
        "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
        "matrix_rows",
        "candidate_id",
        "diagnostic_boundary_must_remain",
        "matrix_row",
    ),
    DiagnosticBoundaryArtifact(
        "docs/milestone-e-internal-trust-loop-blocker-ledger.json",
        "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
        "blocker_rows",
        "candidate_id",
        "diagnostic_boundary_must_remain",
        "blocker_row",
    ),
)


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def expected_by_candidate() -> dict[str, str]:
    return {row.candidate_id: row.boundary for row in EXPECTED_ROWS}


def contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(contains_key(child, key) for child in value.values())
    if isinstance(value, list):
        return any(contains_key(child, key) for child in value)
    return False


class MilestoneEDiagnosticBoundaryAlignmentTests(unittest.TestCase):
    def test_current_e_artifacts_share_exact_diagnostic_boundaries(self) -> None:
        expected = expected_by_candidate()

        self.assertEqual(9, len(EXPECTED_ROWS))
        self.assertEqual(len(EXPECTED_ROWS), len(set(expected.values())))

        for entry in DIAGNOSTIC_BOUNDARY_ARTIFACTS:
            artifact = load_json(entry.artifact)
            rows = artifact[entry.row_key]

            self.assertEqual(
                [row.candidate_id for row in EXPECTED_ROWS],
                [row[entry.id_key] for row in rows],
                entry.artifact,
            )
            self.assertEqual(
                expected,
                {row[entry.id_key]: row[entry.boundary_key] for row in rows},
                entry.artifact,
            )

    def test_schemas_require_nonempty_diagnostic_boundary_fields(self) -> None:
        for entry in DIAGNOSTIC_BOUNDARY_ARTIFACTS:
            schema = load_json(entry.schema)
            row_schema = schema["$defs"][entry.schema_def]
            boundary_schema = row_schema["properties"][entry.boundary_key]

            self.assertIn(entry.boundary_key, row_schema["required"], entry.schema)
            self.assertEqual("string", boundary_schema["type"], entry.schema)
            self.assertEqual(1, boundary_schema["minLength"], entry.schema)

    def test_diagnostic_boundary_artifact_and_schema_sets_are_explicit(self) -> None:
        discovered_artifacts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "docs").glob("milestone-e-*.json")
            if contains_key(load_json(str(path.relative_to(ROOT))), "expected_diagnostic_boundary")
            or contains_key(load_json(str(path.relative_to(ROOT))), "diagnostic_boundary_must_remain")
        }
        discovered_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
            if contains_key(load_json(str(path.relative_to(ROOT))), "expected_diagnostic_boundary")
            or contains_key(load_json(str(path.relative_to(ROOT))), "diagnostic_boundary_must_remain")
        }

        self.assertEqual(
            {entry.artifact for entry in DIAGNOSTIC_BOUNDARY_ARTIFACTS},
            discovered_artifacts,
        )
        self.assertEqual(
            {entry.schema for entry in DIAGNOSTIC_BOUNDARY_ARTIFACTS},
            discovered_schemas,
        )

    def test_row_validation_records_name_current_diagnostic_boundaries(self) -> None:
        for row in EXPECTED_ROWS:
            text = read(VALIDATION_DIR / row.record)

            self.assertIn(row.step_id, text, row.record)
            self.assertIn(row.boundary, text, row.record)

    def test_scope_status_and_roadmap_name_diagnostic_boundary_alignment(self) -> None:
        for path in (PREP_SCOPE, EXECUTION_STATUS, ROADMAP):
            text = read(path)
            normalized = " ".join(text.split())

            self.assertIn("diagnostic-boundary alignment", normalized, str(path))
            self.assertIn("source-only", normalized, str(path))
            self.assertIn("does not resolve or soften blockers", normalized, str(path))

    def test_make_target_runs_diagnostic_boundary_guard_after_evidence_lane_guard(self) -> None:
        block = target_block("milestone-e-prep")

        evidence_lane_guard = "$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment.py"
        diagnostic_guard = "$(PYTHON) .github/scripts/test_milestone_e_diagnostic_boundary_alignment.py"
        prep_scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(diagnostic_guard, block)
        self.assertLess(block.index(evidence_lane_guard), block.index(diagnostic_guard))
        self.assertLess(block.index(diagnostic_guard), block.index(prep_scope_guard))
        self.assertLess(block.index(diagnostic_guard), block.index("git diff --check"))

    def test_ci_runs_diagnostic_boundary_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        evidence_lane_guard = "python3 .github/scripts/test_milestone_e_evidence_lane_alignment.py"
        diagnostic_guard = "python3 .github/scripts/test_milestone_e_diagnostic_boundary_alignment.py"
        prep_scope_guard = "python3 .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(diagnostic_guard, text)
        self.assertEqual(1, text.count(diagnostic_guard))
        self.assertLess(text.index(evidence_lane_guard), text.index(diagnostic_guard))
        self.assertLess(text.index(diagnostic_guard), text.index(prep_scope_guard))

    def test_diagnostic_boundary_artifacts_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            json.dumps(load_json(entry.artifact), sort_keys=True).lower()
            for entry in DIAGNOSTIC_BOUNDARY_ARTIFACTS
        )

        for phrase in FORBIDDEN_ARTIFACT_WORDING:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
