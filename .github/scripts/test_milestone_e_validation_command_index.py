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
from dataclasses import dataclass
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
CANDIDATES = ROOT / "docs/milestone-e-fixture-candidates.json"
CRITERIA = ROOT / "docs/milestone-e-fixture-promotion-criteria.json"
WALKTHROUGH = ROOT / "docs/milestone-e-internal-trust-loop-walkthrough.json"
PROTOCOL = ROOT / "docs/milestone-e-internal-trust-loop-use-protocol.json"
MATRIX = ROOT / "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json"
LEDGER = ROOT / "docs/milestone-e-internal-trust-loop-blocker-ledger.json"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
VALIDATION_DIR = ROOT / "docs/validation"

SCHEMAS = (
    ROOT / "schemas/ethos-milestone-e-fixture-candidates.schema.json",
    ROOT / "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json",
    ROOT / "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
    ROOT / "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
    ROOT / "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
    ROOT / "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
)

EXPECTED_COMMANDS = (
    "make milestone-d-capability-downgrade-contract",
    "make milestone-d-internal-contracts",
    "make milestone-d-opendataloader-adapter-shape-contract",
    "make rag-chunk-alpha",
    "make security-report-alpha",
    "make verify-alpha",
)
COMMAND_RE = re.compile(r"^make [a-z0-9][a-z0-9-]*$")
FORBIDDEN_COMMAND_FRAGMENTS = (
    "&&",
    "||",
    ";",
    "|",
    "`",
    "$(",
    "/Users/",
    "/private/",
    "PYTHON=",
    "python3",
    "cargo ",
    "ethos-bench",
)


@dataclass(frozen=True)
class ValidationCommandRow:
    step_id: str
    candidate_id: str
    label: str
    command: str
    record: str


EXPECTED_ROWS = (
    ValidationCommandRow(
        "native-grounding-baseline",
        "native-verification-trust-loop",
        "Native verification trust loop",
        "make verify-alpha",
        "milestone-e-native-grounding-baseline-rehearsal-validation-2026-06-19.md",
    ),
    ValidationCommandRow(
        "diagnostic-boundary-check",
        "split-quote-unsupported-claim-diagnostics",
        "Split-quote and unsupported-claim diagnostics",
        "make verify-alpha",
        "milestone-e-diagnostic-boundary-check-rehearsal-validation-2026-06-19.md",
    ),
    ValidationCommandRow(
        "capability-downgrade-boundary",
        "capability-downgrade-diagnostics",
        "Capability downgrade diagnostics",
        "make milestone-d-capability-downgrade-contract",
        "milestone-e-capability-downgrade-boundary-rehearsal-validation-2026-06-19.md",
    ),
    ValidationCommandRow(
        "opendataloader-adapter-grounding",
        "opendataloader-style-adapter-grounding",
        "OpenDataLoader-style adapter grounding",
        "make milestone-d-opendataloader-adapter-shape-contract",
        "milestone-e-opendataloader-adapter-grounding-rehearsal-validation-2026-06-19.md",
    ),
    ValidationCommandRow(
        "pinned-opendataloader-fixture-path",
        "pinned-real-opendataloader-fixture-path",
        "Pinned real OpenDataLoader fixture path",
        "make verify-alpha",
        "milestone-e-pinned-opendataloader-fixture-path-rehearsal-validation-2026-06-19.md",
    ),
    ValidationCommandRow(
        "crop-descriptor-source-bound-shape",
        "crop-descriptor-source-bound-crop-shape",
        "Crop descriptor and source-bound crop shape",
        "make milestone-d-internal-contracts",
        "milestone-e-crop-descriptor-source-bound-shape-rehearsal-validation-2026-06-20.md",
    ),
    ValidationCommandRow(
        "rag-chunk-artifact-loop",
        "rag-chunk-artifact-loop",
        "RAG chunk artifact loop",
        "make rag-chunk-alpha",
        "milestone-e-rag-chunk-artifact-loop-rehearsal-validation-2026-06-20.md",
    ),
    ValidationCommandRow(
        "security-report-artifact-loop",
        "security-report-artifact-loop",
        "Security-report artifact loop",
        "make security-report-alpha",
        "milestone-e-security-report-artifact-loop-rehearsal-validation-2026-06-20.md",
    ),
    ValidationCommandRow(
        "demo-narrative-index",
        "demo-narrative-index",
        "Demo narrative index",
        "make verify-alpha",
        "milestone-e-demo-narrative-index-rehearsal-validation-2026-06-20.md",
    ),
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_by_candidate() -> dict[str, str]:
    return {row.candidate_id: row.command for row in EXPECTED_ROWS}


def expected_by_step() -> dict[str, ValidationCommandRow]:
    return {row.step_id: row for row in EXPECTED_ROWS}


def prep_scope_command_rows() -> dict[str, str]:
    rows = {}
    for line in PREP_SCOPE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            continue
        label, _fixtures, command = cells
        if label in {"Candidate", "Candidate lane", "---"} or set(label) == {"-"}:
            continue
        rows[label] = command
    return rows


def make_targets() -> set[str]:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    return set(re.findall(r"^([A-Za-z0-9_.-]+):", text, flags=re.MULTILINE))


def assert_plain_make_command(testcase: unittest.TestCase, command: str) -> None:
    testcase.assertRegex(command, COMMAND_RE)
    for fragment in FORBIDDEN_COMMAND_FRAGMENTS:
        testcase.assertNotIn(fragment, command, command)
    target = command.split(" ", 1)[1]
    testcase.assertIn(target, make_targets(), command)


class MilestoneEValidationCommandIndexTests(unittest.TestCase):
    def test_current_schemas_share_exact_validation_command_enum(self) -> None:
        for schema_path in SCHEMAS:
            schema = load_json(schema_path)

            self.assertEqual(list(EXPECTED_COMMANDS), schema["$defs"]["validation_command"]["enum"])

    def test_fixture_inventory_and_criteria_share_canonical_commands(self) -> None:
        candidates = load_json(CANDIDATES)["fixture_candidates"]
        criteria = load_json(CRITERIA)["criteria"]

        self.assertEqual(
            [row.candidate_id for row in EXPECTED_ROWS],
            [row["id"] for row in candidates],
        )
        self.assertEqual(
            expected_by_candidate(),
            {row["id"]: row["validated_command"] for row in candidates},
        )
        self.assertEqual(
            expected_by_candidate(),
            {row["candidate_id"]: row["validation_command_must_pass"] for row in criteria},
        )

    def test_trust_loop_rows_share_canonical_commands(self) -> None:
        expected = expected_by_step()
        artifacts = (
            (WALKTHROUGH, "walkthrough_steps"),
            (PROTOCOL, "protocol_steps"),
            (MATRIX, "matrix_rows"),
            (LEDGER, "blocker_rows"),
        )

        for artifact, row_key in artifacts:
            rows = load_json(artifact)[row_key]
            self.assertEqual([row.step_id for row in EXPECTED_ROWS], [row["step_id"] for row in rows])
            for actual in rows:
                expected_row = expected[actual["step_id"]]
                self.assertEqual(expected_row.candidate_id, actual["candidate_id"], artifact)
                self.assertEqual(expected_row.command, actual["validation_command_must_pass"], artifact)

    def test_prep_scope_table_uses_canonical_plain_commands(self) -> None:
        rows = prep_scope_command_rows()

        self.assertEqual({row.label for row in EXPECTED_ROWS}, set(rows))
        for expected_row in EXPECTED_ROWS:
            self.assertEqual(f"`{expected_row.command}`", rows[expected_row.label])

    def test_row_validation_records_name_their_canonical_command(self) -> None:
        for expected_row in EXPECTED_ROWS:
            record = (VALIDATION_DIR / expected_row.record).read_text(encoding="utf-8")
            command = expected_row.command

            self.assertIn(f"- Validation command: `{command}`", record, expected_row.record)
            self.assertIn(f"{command} PYTHON=<jsonschema-venv>/bin/python", record)
            self.assertIn(f"The validation command remains `{command}`.", record)

    def test_all_indexed_commands_are_plain_source_checkout_make_targets(self) -> None:
        commands = []
        commands.extend(row["validated_command"] for row in load_json(CANDIDATES)["fixture_candidates"])
        commands.extend(row["validation_command_must_pass"] for row in load_json(CRITERIA)["criteria"])
        commands.extend(
            row["validation_command_must_pass"]
            for row in load_json(WALKTHROUGH)["walkthrough_steps"]
        )
        commands.extend(
            row["validation_command_must_pass"] for row in load_json(PROTOCOL)["protocol_steps"]
        )
        commands.extend(
            row["validation_command_must_pass"] for row in load_json(MATRIX)["matrix_rows"]
        )
        commands.extend(
            row["validation_command_must_pass"] for row in load_json(LEDGER)["blocker_rows"]
        )
        commands.extend(cell.strip("`") for cell in prep_scope_command_rows().values())

        self.assertEqual(set(EXPECTED_COMMANDS), set(commands))
        for command in commands:
            assert_plain_make_command(self, command)

    def test_make_target_runs_validation_command_index_guards_in_order(self) -> None:
        block = target_block("milestone-e-prep")

        public_boundary_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py"
        )
        command_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_command_index.py"
        command_record_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_validation_command_index_validation_record.py"
        )
        record_index_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(command_guard, block)
        self.assertIn(command_record_guard, block)
        self.assertLess(block.index(public_boundary_record), block.index(command_guard))
        self.assertLess(block.index(command_guard), block.index(command_record_guard))
        self.assertLess(block.index(command_record_guard), block.index(record_index_guard))

    def test_ci_runs_validation_command_index_guards_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        public_boundary_record = (
            "python3 .github/scripts/test_milestone_e_public_boundary_alignment_validation_record.py"
        )
        command_guard = "python3 .github/scripts/test_milestone_e_validation_command_index.py"
        command_record_guard = (
            "python3 .github/scripts/test_milestone_e_validation_command_index_validation_record.py"
        )
        record_index_guard = "python3 .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(command_guard, text)
        self.assertIn(command_record_guard, text)
        self.assertEqual(1, text.count(command_guard))
        self.assertEqual(1, text.count(command_record_guard))
        self.assertLess(text.index(public_boundary_record), text.index(command_guard))
        self.assertLess(text.index(command_guard), text.index(command_record_guard))
        self.assertLess(text.index(command_record_guard), text.index(record_index_guard))


if __name__ == "__main__":
    unittest.main()
