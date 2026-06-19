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
import subprocess
import unittest
from pathlib import Path

from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json"
PROTOCOL = ROOT / "docs/milestone-e-internal-trust-loop-use-protocol.json"
WALKTHROUGH = ROOT / "docs/milestone-e-internal-trust-loop-walkthrough.json"
CANDIDATES = ROOT / "docs/milestone-e-fixture-candidates.json"
CRITERIA = ROOT / "docs/milestone-e-fixture-promotion-criteria.json"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
MATRIX_SCHEMA = (
    ROOT
    / "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json"
)
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_STEP_IDS = [
    "native-grounding-baseline",
    "diagnostic-boundary-check",
    "capability-downgrade-boundary",
    "opendataloader-adapter-grounding",
    "pinned-opendataloader-fixture-path",
    "crop-descriptor-source-bound-shape",
    "rag-chunk-artifact-loop",
    "security-report-artifact-loop",
    "demo-narrative-index",
]
EXPECTED_CANDIDATE_IDS = [
    "native-verification-trust-loop",
    "split-quote-unsupported-claim-diagnostics",
    "capability-downgrade-diagnostics",
    "opendataloader-style-adapter-grounding",
    "pinned-real-opendataloader-fixture-path",
    "crop-descriptor-source-bound-crop-shape",
    "rag-chunk-artifact-loop",
    "security-report-artifact-loop",
    "demo-narrative-index",
]
EXPECTED_BLOCKED_OUTPUTS = [
    "public reports",
    "public result wording",
    "hosted surfaces",
    "release artifacts",
    "package publication",
    "production positioning",
    "benchmark publication",
    "performance claims",
    "quality claims",
    "footprint claims",
    "table-quality claims",
    "parser-quality claims",
    "broad demo-generation workflows",
]
EXPECTED_EVIDENCE_MATRIX_LANES = [
    "evidence grounding",
    "diagnostics",
    "fixture/evaluator validation",
    "explicit blockers",
]
FORBIDDEN_MATRIX_WORDING = [
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class MilestoneEInternalTrustLoopRehearsalEvidenceMatrixTests(unittest.TestCase):
    def assert_tracked_file(self, path: str) -> None:
        self.assertTrue((ROOT / path).is_file(), path)
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, path)

    def test_matrix_file_is_source_only_internal(self) -> None:
        matrix = load_json(MATRIX)

        self.assertEqual(1, matrix["schema_version"])
        self.assertEqual(
            "source-only-pre-alpha-internal-milestone-e-prep",
            matrix["status"],
        )
        self.assertEqual("internal_trust_loop_rehearsal_evidence_matrix", matrix["scope"])
        self.assertEqual("docs/milestone-e-fixture-candidates.json", matrix["applies_to_inventory"])
        self.assertEqual("docs/milestone-e-fixture-promotion-criteria.json", matrix["applies_to_criteria"])
        self.assertEqual(
            "docs/milestone-e-internal-trust-loop-walkthrough.json",
            matrix["applies_to_walkthrough"],
        )
        self.assertEqual(
            "docs/milestone-e-internal-trust-loop-use-protocol.json",
            matrix["applies_to_protocol"],
        )
        self.assertEqual(
            "internal_source_only_rehearsal_evidence_matrix",
            matrix["matrix_boundary"],
        )
        self.assertEqual(
            "internal_source_only_rehearsal_evidence_matrix_defined_not_executed",
            matrix["matrix_status"],
        )
        self.assertEqual(
            "not_promoted_beyond_internal_fixture_planning",
            matrix["promotion_status"],
        )
        self.assertIn("public result wording remains blocked", matrix["public_boundary"])
        self.assertIn("hosted surfaces remain blocked", matrix["public_boundary"])
        self.assertEqual(EXPECTED_BLOCKED_OUTPUTS, matrix["blocked_outputs"])
        self.assertEqual(EXPECTED_EVIDENCE_MATRIX_LANES, matrix["evidence_matrix_lanes"])
        self.assertIn(
            "make milestone-e-prep remains green",
            matrix["required_before_internal_rehearsal"],
        )
        self.assertIn(
            "public-surface posture and claims gates remain green",
            matrix["required_before_internal_rehearsal"],
        )

    def test_matrix_rows_match_protocol_walkthrough_and_criteria(self) -> None:
        matrix_rows = load_json(MATRIX)["matrix_rows"]
        protocol_steps = {
            step["step_id"]: step
            for step in load_json(PROTOCOL)["protocol_steps"]
        }
        walkthrough_steps = {
            step["step_id"]: step
            for step in load_json(WALKTHROUGH)["walkthrough_steps"]
        }
        candidates = {
            candidate["id"]: candidate
            for candidate in load_json(CANDIDATES)["fixture_candidates"]
        }
        criteria = {
            case["candidate_id"]: case
            for case in load_json(CRITERIA)["criteria"]
        }

        self.assertEqual(EXPECTED_STEP_IDS, [row["step_id"] for row in matrix_rows])
        self.assertEqual(EXPECTED_CANDIDATE_IDS, [row["candidate_id"] for row in matrix_rows])
        self.assertEqual(
            list(range(1, len(matrix_rows) + 1)),
            [row["sequence"] for row in matrix_rows],
        )
        self.assertEqual(len(matrix_rows), len({row["candidate_id"] for row in matrix_rows}))
        self.assertEqual(len(matrix_rows), len({row["step_id"] for row in matrix_rows}))

        for row in matrix_rows:
            step_id = row["step_id"]
            candidate_id = row["candidate_id"]
            self.assertIn(step_id, protocol_steps)
            self.assertIn(step_id, walkthrough_steps)
            self.assertIn(candidate_id, candidates)
            self.assertIn(candidate_id, criteria)
            protocol_step = protocol_steps[step_id]
            walkthrough = walkthrough_steps[step_id]
            case = criteria[candidate_id]

            self.assertEqual(
                "internal_source_only_rehearsal_defined_not_promoted",
                row["rehearsal_status"],
            )
            self.assertEqual(EXPECTED_EVIDENCE_MATRIX_LANES, row["evidence_matrix_lanes"])
            for field in [
                "sequence",
                "candidate_id",
                "promotion_status",
                "validation_command_must_pass",
                "required_input_fixtures",
                "diagnostic_boundary_must_remain",
                "blockers_must_remain_explicit",
            ]:
                self.assertEqual(protocol_step[field], row[field], f"{step_id}:protocol:{field}")
                self.assertEqual(walkthrough[field], row[field], f"{step_id}:walkthrough:{field}")
            self.assertEqual(case["promotion_status"], row["promotion_status"])
            self.assertEqual(case["validation_command_must_pass"], row["validation_command_must_pass"])
            self.assertEqual(case["required_input_fixtures"], row["required_input_fixtures"])
            self.assertEqual(
                case["diagnostic_boundary_must_remain"],
                row["diagnostic_boundary_must_remain"],
            )
            self.assertEqual(
                case["blockers_must_remain_explicit"],
                row["blockers_must_remain_explicit"],
            )

    def test_matrix_paths_are_tracked_and_not_new_inputs(self) -> None:
        protocol_paths = {
            path
            for step in load_json(PROTOCOL)["protocol_steps"]
            for path in step["required_input_fixtures"]
        }

        for row in load_json(MATRIX)["matrix_rows"]:
            for path in row["required_input_fixtures"]:
                self.assertIn(path, protocol_paths)
                self.assertEqual(path, path.strip())
                self.assertFalse(path.startswith("/"), path)
                self.assertNotIn("..", path)
                self.assertNotIn("\\", path)
                self.assertNotIn("*", path)
                self.assertNotIn("?", path)
                self.assert_tracked_file(path)

    def test_matrix_validation_commands_are_existing_make_targets(self) -> None:
        makefile = makefile_text()
        for command in {
            row["validation_command_must_pass"]
            for row in load_json(MATRIX)["matrix_rows"]
        }:
            target = command.removeprefix("make ")
            declarations = [
                line for line in makefile.splitlines() if line.startswith(f"{target}:")
            ]
            self.assertEqual(1, len(declarations), command)

    def test_schema_validation_covers_matrix(self) -> None:
        schema = load_json(MATRIX_SCHEMA)
        row_schema = schema["$defs"]["matrix_row"]
        validate_examples = read(VALIDATE_EXAMPLES)
        schemas_readme = read(SCHEMAS_README)

        self.assertEqual(False, schema["additionalProperties"])
        self.assertEqual(False, row_schema["additionalProperties"])
        self.assertEqual(9, schema["properties"]["matrix_rows"]["minItems"])
        self.assertEqual(9, schema["properties"]["matrix_rows"]["maxItems"])
        self.assertEqual(9, row_schema["properties"]["sequence"]["maximum"])
        self.assertEqual(
            EXPECTED_CANDIDATE_IDS,
            row_schema["properties"]["candidate_id"]["enum"],
        )
        self.assertEqual(
            EXPECTED_EVIDENCE_MATRIX_LANES,
            schema["$defs"]["evidence_matrix_lane"]["enum"],
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
            schemas_readme,
        )

    def test_status_roadmap_and_scope_reference_matrix(self) -> None:
        prep_scope = read(PREP_SCOPE)
        roadmap = read(ROADMAP)
        status = read(EXECUTION_STATUS)

        self.assertIn(
            "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            prep_scope,
        )
        self.assertIn("internal trust-loop rehearsal/evidence matrix", prep_scope)
        self.assertIn("not public result wording", prep_scope)
        self.assertIn(
            "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            roadmap,
        )
        self.assertIn(
            "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
            status,
        )
        self.assertIn("does not promote any fixture beyond internal source-only planning", status)

    def test_make_target_runs_matrix_guard_in_order(self) -> None:
        block = target_block("milestone-e-prep")

        protocol_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_use_protocol.py"
        )
        matrix_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py"
        )
        protocol_record_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py"
        )
        matrix_record_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix_validation_record.py"
        )
        self.assertIn(protocol_guard, block)
        self.assertIn(matrix_guard, block)
        self.assertIn(protocol_record_guard, block)
        self.assertIn(matrix_record_guard, block)
        self.assertLess(block.index(protocol_guard), block.index(matrix_guard))
        self.assertLess(block.index(matrix_guard), block.index(protocol_record_guard))
        self.assertLess(block.index(protocol_record_guard), block.index(matrix_record_guard))
        self.assertLess(block.index(matrix_record_guard), block.index("git diff --check"))

    def test_ci_runs_matrix_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        protocol_guard = (
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py"
        )
        matrix_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_rehearsal_evidence_matrix.py"
        )
        protocol_record_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_use_protocol_validation_record.py"
        )

        self.assertIn(matrix_guard, text)
        self.assertEqual(1, text.count(matrix_guard))
        self.assertLess(text.index(protocol_guard), text.index(matrix_guard))
        self.assertLess(text.index(matrix_guard), text.index(protocol_record_guard))

    def test_matrix_avoids_scope_expansion_language(self) -> None:
        text = json.dumps(load_json(MATRIX), sort_keys=True).lower()

        for phrase in FORBIDDEN_MATRIX_WORDING:
            self.assertNotIn(phrase, text)

    def test_matrix_avoids_local_private_paths(self) -> None:
        text = read(MATRIX)

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
