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
class BlockedOutputArtifact:
    artifact: str
    schema: str
    row_key: str | None = None


BLOCKED_OUTPUT_ARTIFACTS = (
    BlockedOutputArtifact(
        "docs/milestone-e-internal-trust-loop-use-protocol.json",
        "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
    ),
    BlockedOutputArtifact(
        "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
        "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
    ),
    BlockedOutputArtifact(
        "docs/milestone-e-internal-trust-loop-blocker-ledger.json",
        "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
        "blocker_rows",
    ),
)


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class MilestoneEBlockedOutputAlignmentTests(unittest.TestCase):
    def test_current_e_artifacts_share_exact_blocked_output_list(self) -> None:
        self.assertEqual(13, len(EXPECTED_BLOCKED_OUTPUTS))
        self.assertEqual(len(EXPECTED_BLOCKED_OUTPUTS), len(set(EXPECTED_BLOCKED_OUTPUTS)))

        for entry in BLOCKED_OUTPUT_ARTIFACTS:
            artifact = load_json(entry.artifact)

            self.assertEqual(
                EXPECTED_BLOCKED_OUTPUTS,
                artifact["blocked_outputs"],
                entry.artifact,
            )

    def test_current_e_schemas_share_exact_blocked_output_enum(self) -> None:
        for entry in BLOCKED_OUTPUT_ARTIFACTS:
            schema = load_json(entry.schema)
            blocked_output_schema = schema["$defs"]["blocked_output"]
            property_schema = schema["properties"]["blocked_outputs"]

            self.assertEqual(EXPECTED_BLOCKED_OUTPUTS, blocked_output_schema["enum"], entry.schema)
            self.assertEqual(13, property_schema["minItems"], entry.schema)
            self.assertEqual(13, property_schema["maxItems"], entry.schema)
            self.assertTrue(property_schema["uniqueItems"], entry.schema)

    def test_ledger_rows_keep_global_blocked_outputs_explicit(self) -> None:
        ledger = load_json("docs/milestone-e-internal-trust-loop-blocker-ledger.json")

        self.assertEqual(EXPECTED_BLOCKED_OUTPUTS, ledger["blocked_outputs"])
        for row in ledger["blocker_rows"]:
            self.assertEqual(
                EXPECTED_BLOCKED_OUTPUTS,
                row["global_blocked_outputs_must_remain"],
                row["step_id"],
            )

    def test_ledger_schema_requires_row_level_blocked_outputs(self) -> None:
        schema = load_json("schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json")
        row_schema = schema["$defs"]["blocker_row"]
        global_schema = row_schema["properties"]["global_blocked_outputs_must_remain"]

        self.assertIn("global_blocked_outputs_must_remain", row_schema["required"])
        self.assertEqual(13, global_schema["minItems"])
        self.assertEqual(13, global_schema["maxItems"])
        self.assertTrue(global_schema["uniqueItems"])
        self.assertEqual("#/$defs/blocked_output", global_schema["items"]["$ref"])

    def test_blocked_output_artifact_set_is_explicit(self) -> None:
        discovered_artifacts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "docs").glob("milestone-e-*.json")
            if "blocked_outputs" in load_json(str(path.relative_to(ROOT)))
        }
        discovered_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
            if "blocked_outputs" in load_json(str(path.relative_to(ROOT)))["properties"]
        }

        self.assertEqual({entry.artifact for entry in BLOCKED_OUTPUT_ARTIFACTS}, discovered_artifacts)
        self.assertEqual({entry.schema for entry in BLOCKED_OUTPUT_ARTIFACTS}, discovered_schemas)

    def test_scope_and_status_name_blocked_output_alignment(self) -> None:
        prep_scope = read(PREP_SCOPE)
        status = read(EXECUTION_STATUS)

        for text in (prep_scope, status):
            self.assertIn("blocked-output alignment", text)
            self.assertIn("source-only", text)
            self.assertIn("does not resolve or soften blockers", text)

    def test_make_target_runs_blocked_output_guard_after_public_boundary_guard(self) -> None:
        block = target_block("milestone-e-prep")

        public_boundary_guard = "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment.py"
        blocked_output_guard = "$(PYTHON) .github/scripts/test_milestone_e_blocked_output_alignment.py"
        prep_scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(blocked_output_guard, block)
        self.assertLess(block.index(public_boundary_guard), block.index(blocked_output_guard))
        self.assertLess(block.index(blocked_output_guard), block.index(prep_scope_guard))
        self.assertLess(block.index(blocked_output_guard), block.index("git diff --check"))

    def test_ci_runs_blocked_output_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        public_boundary_guard = "python3 .github/scripts/test_milestone_e_public_boundary_alignment.py"
        blocked_output_guard = "python3 .github/scripts/test_milestone_e_blocked_output_alignment.py"
        prep_scope_guard = "python3 .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(blocked_output_guard, text)
        self.assertEqual(1, text.count(blocked_output_guard))
        self.assertLess(text.index(public_boundary_guard), text.index(blocked_output_guard))
        self.assertLess(text.index(blocked_output_guard), text.index(prep_scope_guard))

    def test_blocked_output_artifacts_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            json.dumps(load_json(entry.artifact), sort_keys=True).lower()
            for entry in BLOCKED_OUTPUT_ARTIFACTS
        )

        for phrase in FORBIDDEN_ARTIFACT_WORDING:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
