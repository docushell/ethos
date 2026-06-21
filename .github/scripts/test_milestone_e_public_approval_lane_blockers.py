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
LEDGER = ROOT / "docs/milestone-e-public-approval-lane-blockers.json"
LEDGER_SCHEMA = ROOT / "schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_PUBLIC_BOUNDARY = [
    "public reports remain blocked",
    "release artifacts remain blocked",
    "package publication remains blocked",
    "hosted surfaces remain blocked",
    "public result wording remains blocked",
    "performance claims remain blocked",
    "quality claims remain blocked",
    "footprint claims remain blocked",
    "table-quality claims remain blocked",
    "parser-quality claims remain blocked",
]

EXPECTED_APPROVED_SENTENCE = (
    "Ethos is pre-alpha. It verifies whether AI citations are grounded in document "
    "evidence across native Ethos JSON and supported foreign parser outputs."
)
EXPECTED_PUBLIC_BETA_WORDING = (
    "Ethos is public beta for source-only evaluation. It verifies whether AI citations are "
    "grounded in document evidence across native Ethos JSON and supported foreign parser outputs. "
    "Package publication, hosted surfaces, production positioning, and public benchmark claims "
    "remain blocked."
)
EXPECTED_PACKAGE_PREP_WORDING = (
    "Ethos crate publication is in internal preparation only and remains blocked for public "
    "installation. No Ethos crates are published; the reserved crates.io names remain "
    "0.0.0-reserved.0 placeholders with no public API. Wheels, npm packages, binaries, hosted "
    "surfaces, production positioning, and public benchmark claims remain blocked."
)
EXPECTED_GATE_SCRIPT = ".github/scripts/test_milestone_e_public_approval_lane_blockers.py"
EXPECTED_VALIDATION_RECORD = (
    "docs/validation/milestone-e-public-approval-lane-blockers-validation-2026-06-20.md"
)
EXPECTED_SOURCE_SNAPSHOT = {
    "source_head": "660f268df400351347d5185ad36584faa0481c7f",
    "tag": "ethos-source-snapshot-660f268",
    "archive": "ethos-source-snapshot-660f268.tar.gz",
    "sha256": "58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87",
    "boundary": (
        "source-snapshot-only; source-only public beta evaluation approved separately for the "
        "reviewed GitHub source tree; no package, hosted, production, or public-report approval"
    ),
}
EXPECTED_PUBLIC_BETA_SOURCE = {
    "surface": "GitHub source repository docushell/ethos source-only evaluation",
    "reviewed_commit": "902c423",
    "merged_main_commit": "6019a97",
    "tree": "f56fde854f6f6e4c4070209329f8c7b12310aa51",
    "boundary": "source-only clone, build, and validation commands only",
}

FORBIDDEN_LEDGER_WORDING = [
    "public beta is approved",
    "public beta approved",
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
class ApprovalLane:
    sequence: int
    lane_id: str
    lane_name: str
    approval_status: str
    owner: str
    required_blocker_phrase: str


EXPECTED_LANES = (
    ApprovalLane(
        1,
        "public-beta-approval",
        "Public beta approval",
        "approved_source_only_public_beta",
        "decider",
        "package publication remains blocked",
    ),
    ApprovalLane(
        2,
        "package-publication",
        "Package publication",
        "prep_approved_publication_blocked",
        "docushell-admin",
        "real-version cargo publish remains blocked",
    ),
    ApprovalLane(
        3,
        "hosted-surface",
        "Hosted surface",
        "blocked_pending_dedicated_approval",
        "decider",
        "ADR-0005 and H2 source-snapshot closeout do not approve hosted surfaces",
    ),
    ApprovalLane(
        4,
        "production-positioning",
        "Production positioning",
        "blocked_pending_dedicated_approval",
        "decider",
        "ADR-0005 does not approve production positioning",
    ),
    ApprovalLane(
        5,
        "public-benchmark-report",
        "Public benchmark report",
        "blocked_pending_dedicated_approval",
        "benchmark owner / decider",
        "ADR-0005 does not approve public benchmark reports",
    ),
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class MilestoneEPublicApprovalLaneBlockerTests(unittest.TestCase):
    def test_ledger_records_source_only_public_beta_package_prep_and_blocked_lanes(self) -> None:
        ledger = load_json(LEDGER)

        self.assertEqual(1, ledger["schema_version"])
        self.assertEqual("source-only-pre-alpha-internal-milestone-e-prep", ledger["status"])
        self.assertEqual("public_approval_lane_blocker_ledger", ledger["scope"])
        self.assertEqual("internal_public_approval_lane_blocker_prep", ledger["ledger_boundary"])
        self.assertEqual(
            "public_beta_source_only_and_package_prep_approved_other_lanes_blocked",
            ledger["ledger_status"],
        )
        self.assertEqual(EXPECTED_APPROVED_SENTENCE, ledger["exact_approved_public_sentence"])
        self.assertEqual(EXPECTED_PUBLIC_BETA_WORDING, ledger["exact_approved_public_beta_wording"])
        self.assertEqual(
            EXPECTED_PACKAGE_PREP_WORDING,
            ledger["exact_approved_package_publication_prep_wording"],
        )
        self.assertEqual(EXPECTED_SOURCE_SNAPSHOT, ledger["approved_source_snapshot"])
        self.assertEqual(EXPECTED_PUBLIC_BETA_SOURCE, ledger["approved_public_beta_source"])
        self.assertEqual(EXPECTED_PUBLIC_BOUNDARY, ledger["public_boundary"])
        self.assertEqual(EXPECTED_GATE_SCRIPT, ledger["lane_gate_script"])
        self.assertEqual(EXPECTED_VALIDATION_RECORD, ledger["lane_validation_record"])

    def test_all_recommended_lanes_are_present_with_expected_status(self) -> None:
        rows = load_json(LEDGER)["approval_lanes"]

        self.assertEqual([lane.sequence for lane in EXPECTED_LANES], [row["sequence"] for row in rows])
        self.assertEqual([lane.lane_id for lane in EXPECTED_LANES], [row["lane_id"] for row in rows])
        self.assertEqual([lane.lane_name for lane in EXPECTED_LANES], [row["lane_name"] for row in rows])
        self.assertEqual(
            [lane.approval_status for lane in EXPECTED_LANES],
            [row["approval_status"] for row in rows],
        )
        self.assertEqual(len(rows), len({row["lane_id"] for row in rows}))

        for expected, row in zip(EXPECTED_LANES, rows):
            self.assertEqual(expected.owner, row["approval_owner"])
            self.assertEqual(EXPECTED_GATE_SCRIPT, row["gate_script"])
            self.assertEqual(EXPECTED_VALIDATION_RECORD, row["validation_record"])
            self.assertIn(expected.required_blocker_phrase, row["explicit_blockers"])
            self.assertGreaterEqual(len(row["required_evidence"]), 5, row["lane_id"])
            self.assertGreaterEqual(len(row["explicit_blockers"]), 5, row["lane_id"])
            self.assertGreaterEqual(len(row["allowed_wording"]), 3, row["lane_id"])
            self.assertGreaterEqual(len(row["forbidden_wording"]), 4, row["lane_id"])

    def test_lane_rows_keep_required_approval_contract_fields(self) -> None:
        for row in load_json(LEDGER)["approval_lanes"]:
            self.assertIn("Approval", row["explicit_scope"])
            self.assertTrue(
                any(
                    "dedicated" in item and "approval" in item and "record" in item
                    for item in row["required_evidence"]
                ),
                row["lane_id"],
            )
            self.assertTrue(
                any("signoff" in item for item in row["required_evidence"]),
                row["lane_id"],
            )
            blocker_text = " ".join(row["explicit_blockers"])
            self.assertIn("remain blocked", blocker_text, row["lane_id"])
            allowed_text = " ".join(row["allowed_wording"]).lower()
            if row["lane_id"] == "public-beta-approval":
                self.assertIn("source-only evaluation", allowed_text)
                self.assertIn(EXPECTED_PUBLIC_BETA_WORDING.lower(), allowed_text)
                self.assertIn("package publication remains blocked", blocker_text)
            elif row["lane_id"] == "package-publication":
                self.assertIn(EXPECTED_PACKAGE_PREP_WORDING.lower(), allowed_text)
                self.assertIn("real-version cargo publish remains blocked", blocker_text)
                self.assertIn("package publication remains blocked", blocker_text)
            else:
                self.assertIn("blocked pending dedicated approval", allowed_text, row["lane_id"])
                self.assertTrue(
                    any("exact approved pre-alpha sentence" in item for item in row["forbidden_wording"]),
                    row["lane_id"],
                )

    def test_schema_validation_covers_lane_ledger(self) -> None:
        schema = load_json(LEDGER_SCHEMA)
        row_schema = schema["$defs"]["approval_lane"]
        validate_examples = read(VALIDATE_EXAMPLES)
        schemas_readme = read(SCHEMAS_README)

        self.assertEqual(False, schema["additionalProperties"])
        self.assertEqual(False, row_schema["additionalProperties"])
        self.assertIn("approved_public_beta_source", schema["required"])
        self.assertEqual(5, schema["properties"]["approval_lanes"]["minItems"])
        self.assertEqual(5, schema["properties"]["approval_lanes"]["maxItems"])
        self.assertEqual(5, row_schema["properties"]["sequence"]["maximum"])
        self.assertEqual([lane.lane_id for lane in EXPECTED_LANES], row_schema["properties"]["lane_id"]["enum"])
        self.assertIn("ethos-milestone-e-public-approval-lane-blockers.schema.json", validate_examples)
        self.assertIn("docs\" / \"milestone-e-public-approval-lane-blockers.json", validate_examples)
        self.assertIn("ethos-milestone-e-public-approval-lane-blockers.schema.json", schemas_readme)
        self.assertIn("docs/milestone-e-public-approval-lane-blockers.json", schemas_readme)

    def test_status_roadmap_scope_and_validation_index_reference_lane_ledger(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            text = read(path)

            self.assertIn("docs/milestone-e-public-approval-lane-blockers.json", text, str(path))
            self.assertIn("public approval lane", text, str(path))

        status = " ".join(read(EXECUTION_STATUS).split())
        self.assertIn("Public beta source-only evaluation is approved", status)
        self.assertIn("Package publication remains blocked", status)
        self.assertIn("Hosted surfaces remain blocked", status)
        self.assertIn("Production positioning remains blocked", status)
        self.assertIn("Public benchmark reports remain blocked", status)

    def test_make_target_runs_lane_guard_before_validation_record_index(self) -> None:
        block = target_block("milestone-e-prep")

        required_before_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_required_before_alignment_validation_record.py"
        )
        lane_guard = "$(PYTHON) .github/scripts/test_milestone_e_public_approval_lane_blockers.py"
        lane_record_guard = (
            "$(PYTHON) .github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py"
        )
        index_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(lane_guard, block)
        self.assertIn(lane_record_guard, block)
        self.assertLess(block.index(required_before_record), block.index(lane_guard))
        self.assertLess(block.index(lane_guard), block.index(lane_record_guard))
        self.assertLess(block.index(lane_record_guard), block.index(index_guard))
        self.assertLess(block.index(lane_record_guard), block.index("git diff --check"))

    def test_ci_runs_lane_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        required_before_record = (
            "python3 .github/scripts/test_milestone_e_required_before_alignment_validation_record.py"
        )
        lane_guard = "python3 .github/scripts/test_milestone_e_public_approval_lane_blockers.py"
        lane_record_guard = (
            "python3 .github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py"
        )
        index_guard = "python3 .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(lane_guard, text)
        self.assertIn(lane_record_guard, text)
        self.assertEqual(1, text.count(lane_guard))
        self.assertEqual(1, text.count(lane_record_guard))
        self.assertLess(text.index(required_before_record), text.index(lane_guard))
        self.assertLess(text.index(lane_guard), text.index(lane_record_guard))
        self.assertLess(text.index(lane_record_guard), text.index(index_guard))

    def test_ledger_avoids_scope_expansion_language(self) -> None:
        text = json.dumps(load_json(LEDGER), sort_keys=True).lower()

        for phrase in FORBIDDEN_LEDGER_WORDING:
            self.assertNotIn(phrase, text)

    def test_ledger_avoids_local_private_paths(self) -> None:
        text = read(LEDGER)

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
