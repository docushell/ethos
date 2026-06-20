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

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_EVIDENCE_LANES = [
    "evidence grounding",
    "diagnostics",
    "fixture/evaluator validation",
    "explicit blockers",
]

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
class EvidenceLaneArtifact:
    artifact: str
    schema: str
    row_key: str


EVIDENCE_LANE_ARTIFACTS = (
    EvidenceLaneArtifact(
        "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
        "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
        "matrix_rows",
    ),
    EvidenceLaneArtifact(
        "docs/milestone-e-internal-trust-loop-blocker-ledger.json",
        "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
        "blocker_rows",
    ),
)


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class MilestoneEEvidenceLaneAlignmentTests(unittest.TestCase):
    def test_current_e_artifacts_share_exact_evidence_lane_list(self) -> None:
        self.assertEqual(4, len(EXPECTED_EVIDENCE_LANES))
        self.assertEqual(len(EXPECTED_EVIDENCE_LANES), len(set(EXPECTED_EVIDENCE_LANES)))

        for entry in EVIDENCE_LANE_ARTIFACTS:
            artifact = load_json(entry.artifact)

            self.assertEqual(
                EXPECTED_EVIDENCE_LANES,
                artifact["evidence_matrix_lanes"],
                entry.artifact,
            )

    def test_current_e_schemas_share_exact_evidence_lane_enum(self) -> None:
        for entry in EVIDENCE_LANE_ARTIFACTS:
            schema = load_json(entry.schema)
            lane_schema = schema["$defs"]["evidence_matrix_lane"]
            property_schema = schema["properties"]["evidence_matrix_lanes"]

            self.assertEqual(EXPECTED_EVIDENCE_LANES, lane_schema["enum"], entry.schema)
            self.assertEqual(4, property_schema["minItems"], entry.schema)
            self.assertEqual(4, property_schema["maxItems"], entry.schema)
            self.assertTrue(property_schema["uniqueItems"], entry.schema)

    def test_rows_keep_evidence_lanes_explicit(self) -> None:
        for entry in EVIDENCE_LANE_ARTIFACTS:
            artifact = load_json(entry.artifact)

            self.assertEqual(EXPECTED_EVIDENCE_LANES, artifact["evidence_matrix_lanes"])
            for row in artifact[entry.row_key]:
                self.assertEqual(
                    EXPECTED_EVIDENCE_LANES,
                    row["evidence_matrix_lanes"],
                    row["step_id"],
                )

    def test_schemas_require_row_level_evidence_lanes(self) -> None:
        for entry in EVIDENCE_LANE_ARTIFACTS:
            schema = load_json(entry.schema)
            row_def = "matrix_row" if entry.row_key == "matrix_rows" else "blocker_row"
            row_schema = schema["$defs"][row_def]
            lane_schema = row_schema["properties"]["evidence_matrix_lanes"]

            self.assertIn("evidence_matrix_lanes", row_schema["required"], entry.schema)
            self.assertEqual(4, lane_schema["minItems"], entry.schema)
            self.assertEqual(4, lane_schema["maxItems"], entry.schema)
            self.assertTrue(lane_schema["uniqueItems"], entry.schema)
            self.assertEqual("#/$defs/evidence_matrix_lane", lane_schema["items"]["$ref"])

    def test_evidence_lane_artifact_set_is_explicit(self) -> None:
        discovered_artifacts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "docs").glob("milestone-e-*.json")
            if "evidence_matrix_lanes" in load_json(str(path.relative_to(ROOT)))
        }
        discovered_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
            if "evidence_matrix_lanes" in load_json(str(path.relative_to(ROOT)))["properties"]
        }

        self.assertEqual({entry.artifact for entry in EVIDENCE_LANE_ARTIFACTS}, discovered_artifacts)
        self.assertEqual({entry.schema for entry in EVIDENCE_LANE_ARTIFACTS}, discovered_schemas)

    def test_scope_and_status_name_evidence_lane_alignment(self) -> None:
        prep_scope = read(PREP_SCOPE)
        status = read(EXECUTION_STATUS)

        for text in (prep_scope, status):
            self.assertIn("evidence-lane alignment", text)
            self.assertIn("source-only", text)
            self.assertIn("does not resolve or soften blockers", text)

    def test_make_target_runs_evidence_lane_guard_after_blocked_output_guard(self) -> None:
        block = target_block("milestone-e-prep")

        blocked_output_guard = "$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment.py"
        evidence_lane_guard = "$(PYTHON) .github/scripts/test_milestone_e_evidence_lane_alignment.py"
        prep_scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(evidence_lane_guard, block)
        self.assertLess(block.index(blocked_output_guard), block.index(evidence_lane_guard))
        self.assertLess(block.index(evidence_lane_guard), block.index(prep_scope_guard))
        self.assertLess(block.index(evidence_lane_guard), block.index("git diff --check"))

    def test_ci_runs_evidence_lane_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        blocked_output_guard = "python3 .github/scripts/test_milestone_e_blocked_output_alignment.py"
        evidence_lane_guard = "python3 .github/scripts/test_milestone_e_evidence_lane_alignment.py"
        prep_scope_guard = "python3 .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(evidence_lane_guard, text)
        self.assertEqual(1, text.count(evidence_lane_guard))
        self.assertLess(text.index(blocked_output_guard), text.index(evidence_lane_guard))
        self.assertLess(text.index(evidence_lane_guard), text.index(prep_scope_guard))

    def test_evidence_lane_artifacts_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            json.dumps(load_json(entry.artifact), sort_keys=True).lower()
            for entry in EVIDENCE_LANE_ARTIFACTS
        )

        for phrase in FORBIDDEN_ARTIFACT_WORDING:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
