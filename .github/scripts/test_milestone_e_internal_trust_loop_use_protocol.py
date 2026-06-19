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
PROTOCOL = ROOT / "docs/milestone-e-internal-trust-loop-use-protocol.json"
WALKTHROUGH = ROOT / "docs/milestone-e-internal-trust-loop-walkthrough.json"
CANDIDATES = ROOT / "docs/milestone-e-fixture-candidates.json"
CRITERIA = ROOT / "docs/milestone-e-fixture-promotion-criteria.json"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PROTOCOL_SCHEMA = (
    ROOT / "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json"
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
FORBIDDEN_PROTOCOL_WORDING = [
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


class MilestoneEInternalTrustLoopUseProtocolTests(unittest.TestCase):
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

    def test_protocol_file_is_source_only_internal(self) -> None:
        protocol = load_json(PROTOCOL)

        self.assertEqual(1, protocol["schema_version"])
        self.assertEqual(
            "source-only-pre-alpha-internal-milestone-e-prep",
            protocol["status"],
        )
        self.assertEqual("internal_trust_loop_use_protocol", protocol["scope"])
        self.assertEqual("docs/milestone-e-fixture-candidates.json", protocol["applies_to_inventory"])
        self.assertEqual("docs/milestone-e-fixture-promotion-criteria.json", protocol["applies_to_criteria"])
        self.assertEqual(
            "docs/milestone-e-internal-trust-loop-walkthrough.json",
            protocol["applies_to_walkthrough"],
        )
        self.assertEqual("internal_source_only_walkthrough_use", protocol["protocol_boundary"])
        self.assertEqual(
            "not_promoted_beyond_internal_fixture_planning",
            protocol["promotion_status"],
        )
        self.assertIn("public result wording remains blocked", protocol["public_boundary"])
        self.assertIn("hosted surfaces remain blocked", protocol["public_boundary"])
        self.assertEqual(EXPECTED_BLOCKED_OUTPUTS, protocol["blocked_outputs"])
        self.assertIn(
            "make milestone-e-prep remains green",
            protocol["required_before_internal_use"],
        )
        self.assertIn(
            "public-surface posture and claims gates remain green",
            protocol["required_before_internal_use"],
        )

    def test_protocol_steps_match_walkthrough_and_criteria(self) -> None:
        protocol_steps = load_json(PROTOCOL)["protocol_steps"]
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

        self.assertEqual(EXPECTED_STEP_IDS, [step["step_id"] for step in protocol_steps])
        self.assertEqual(EXPECTED_CANDIDATE_IDS, [step["candidate_id"] for step in protocol_steps])
        self.assertEqual(
            list(range(1, len(protocol_steps) + 1)),
            [step["sequence"] for step in protocol_steps],
        )
        self.assertEqual(len(protocol_steps), len({step["candidate_id"] for step in protocol_steps}))
        self.assertEqual(len(protocol_steps), len({step["step_id"] for step in protocol_steps}))

        for step in protocol_steps:
            step_id = step["step_id"]
            candidate_id = step["candidate_id"]
            self.assertIn(step_id, walkthrough_steps)
            self.assertIn(candidate_id, candidates)
            self.assertIn(candidate_id, criteria)
            walkthrough = walkthrough_steps[step_id]
            case = criteria[candidate_id]

            self.assertEqual(
                "internal_source_only_use_protocol_defined_not_promoted",
                step["use_status"],
            )
            for field in [
                "sequence",
                "candidate_id",
                "promotion_status",
                "validation_command_must_pass",
                "required_input_fixtures",
                "diagnostic_boundary_must_remain",
                "blockers_must_remain_explicit",
            ]:
                self.assertEqual(walkthrough[field], step[field], f"{step_id}:{field}")
            self.assertEqual(case["promotion_status"], step["promotion_status"])
            self.assertEqual(case["validation_command_must_pass"], step["validation_command_must_pass"])
            self.assertEqual(case["required_input_fixtures"], step["required_input_fixtures"])
            self.assertEqual(
                case["diagnostic_boundary_must_remain"],
                step["diagnostic_boundary_must_remain"],
            )
            self.assertEqual(
                case["blockers_must_remain_explicit"],
                step["blockers_must_remain_explicit"],
            )

    def test_protocol_paths_are_tracked_and_not_new_inputs(self) -> None:
        walkthrough_paths = {
            path
            for step in load_json(WALKTHROUGH)["walkthrough_steps"]
            for path in step["required_input_fixtures"]
        }

        for step in load_json(PROTOCOL)["protocol_steps"]:
            for path in step["required_input_fixtures"]:
                self.assertIn(path, walkthrough_paths)
                self.assertEqual(path, path.strip())
                self.assertFalse(path.startswith("/"), path)
                self.assertNotIn("..", path)
                self.assertNotIn("\\", path)
                self.assertNotIn("*", path)
                self.assertNotIn("?", path)
                self.assert_tracked_file(path)

    def test_protocol_validation_commands_are_existing_make_targets(self) -> None:
        makefile = makefile_text()
        for command in {
            step["validation_command_must_pass"]
            for step in load_json(PROTOCOL)["protocol_steps"]
        }:
            target = command.removeprefix("make ")
            declarations = [
                line for line in makefile.splitlines() if line.startswith(f"{target}:")
            ]
            self.assertEqual(1, len(declarations), command)

    def test_schema_validation_covers_protocol(self) -> None:
        schema = load_json(PROTOCOL_SCHEMA)
        step_schema = schema["$defs"]["protocol_step"]
        validate_examples = read(VALIDATE_EXAMPLES)
        schemas_readme = read(SCHEMAS_README)

        self.assertEqual(False, schema["additionalProperties"])
        self.assertEqual(False, step_schema["additionalProperties"])
        self.assertEqual(9, schema["properties"]["protocol_steps"]["minItems"])
        self.assertEqual(9, schema["properties"]["protocol_steps"]["maxItems"])
        self.assertEqual(9, step_schema["properties"]["sequence"]["maximum"])
        self.assertEqual(
            EXPECTED_CANDIDATE_IDS,
            step_schema["properties"]["candidate_id"]["enum"],
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
            validate_examples,
        )
        self.assertIn(
            "docs\" / \"milestone-e-internal-trust-loop-use-protocol.json",
            validate_examples,
        )
        self.assertIn(
            "ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
            schemas_readme,
        )

    def test_status_roadmap_and_scope_reference_protocol(self) -> None:
        prep_scope = read(PREP_SCOPE)
        roadmap = read(ROADMAP)
        status = read(EXECUTION_STATUS)

        self.assertIn("docs/milestone-e-internal-trust-loop-use-protocol.json", prep_scope)
        self.assertIn("internal trust-loop use protocol", prep_scope)
        self.assertIn("not public result wording", prep_scope)
        self.assertIn("docs/milestone-e-internal-trust-loop-use-protocol.json", roadmap)
        self.assertIn("docs/milestone-e-internal-trust-loop-use-protocol.json", status)
        self.assertIn("does not promote any fixture beyond internal source-only planning", status)

    def test_make_target_runs_protocol_guard_in_order(self) -> None:
        block = target_block("milestone-e-prep")

        walkthrough_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_walkthrough.py"
        )
        protocol_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_use_protocol.py"
        )
        walkthrough_record_guard = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_internal_trust_loop_walkthrough_validation_record.py"
        )
        self.assertIn(walkthrough_guard, block)
        self.assertIn(protocol_guard, block)
        self.assertIn(walkthrough_record_guard, block)
        self.assertLess(block.index(walkthrough_guard), block.index(protocol_guard))
        self.assertLess(block.index(protocol_guard), block.index(walkthrough_record_guard))
        self.assertLess(block.index(protocol_guard), block.index("git diff --check"))

    def test_ci_runs_protocol_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        walkthrough_guard = (
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_walkthrough.py"
        )
        protocol_guard = (
            "python3 .github/scripts/test_milestone_e_internal_trust_loop_use_protocol.py"
        )
        walkthrough_record_guard = (
            "python3 .github/scripts/"
            "test_milestone_e_internal_trust_loop_walkthrough_validation_record.py"
        )

        self.assertIn(protocol_guard, text)
        self.assertEqual(1, text.count(protocol_guard))
        self.assertLess(text.index(walkthrough_guard), text.index(protocol_guard))
        self.assertLess(text.index(protocol_guard), text.index(walkthrough_record_guard))

    def test_protocol_avoids_scope_expansion_language(self) -> None:
        text = json.dumps(load_json(PROTOCOL), sort_keys=True).lower()

        for phrase in FORBIDDEN_PROTOCOL_WORDING:
            self.assertNotIn(phrase, text)

    def test_protocol_avoids_local_private_paths(self) -> None:
        text = read(PROTOCOL)

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)
        self.assertNotIn("saumildiwaker", text)
        self.assertNotIn("Desktop/Stuff", text)
        self.assertNotIn("project/repo/ethos", text)


if __name__ == "__main__":
    unittest.main()
