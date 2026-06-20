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
from pathlib import Path
from typing import Any

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "docs/milestone-e-public-beta-approval-prep.json"
PREP_SCHEMA = ROOT / "schemas/ethos-milestone-e-public-beta-approval-prep.schema.json"
LANE_BLOCKERS = ROOT / "docs/milestone-e-public-approval-lane-blockers.json"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_BOUNDARY = [
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
EXPECTED_GATE = ".github/scripts/test_milestone_e_public_beta_approval_prep.py"
EXPECTED_RECORD = "docs/validation/milestone-e-public-beta-approval-prep-validation-2026-06-20.md"

FORBIDDEN_PREP_WORDING = [
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class MilestoneEPublicBetaApprovalPrepTests(unittest.TestCase):
    def test_prep_is_started_but_not_approved(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(1, prep["schema_version"])
        self.assertEqual("source-only-pre-alpha-internal-milestone-e-prep", prep["status"])
        self.assertEqual("public_beta_approval_prep", prep["scope"])
        self.assertEqual("public-beta-approval", prep["lane_id"])
        self.assertEqual("Public beta approval", prep["lane_name"])
        self.assertEqual("started_blocked_pending_dedicated_approval", prep["approval_status"])
        self.assertEqual("not_approved", prep["decision_status"])
        self.assertEqual("decider", prep["approval_owner"])
        self.assertEqual(EXPECTED_APPROVED_SENTENCE, prep["exact_approved_public_sentence"])
        self.assertEqual(EXPECTED_BOUNDARY, prep["public_boundary"])
        self.assertEqual(EXPECTED_GATE, prep["gate_script"])
        self.assertEqual(EXPECTED_RECORD, prep["validation_record"])

    def test_prep_keeps_approved_snapshot_source_only(self) -> None:
        snapshot = load_json(PREP)["approved_source_snapshot"]

        self.assertEqual("660f268df400351347d5185ad36584faa0481c7f", snapshot["source_head"])
        self.assertEqual("ethos-source-snapshot-660f268", snapshot["tag"])
        self.assertEqual("ethos-source-snapshot-660f268.tar.gz", snapshot["archive"])
        self.assertEqual(
            "58ec6fc1ec47a4c16f1294673ba9520b2fe9c2497e15ec96d78679db8517dd87",
            snapshot["sha256"],
        )
        self.assertEqual("source-snapshot-only; no public beta approval", snapshot["boundary"])

    def test_public_beta_lane_stays_aligned_with_global_lane_blocker(self) -> None:
        prep = load_json(PREP)
        lane_blockers = load_json(LANE_BLOCKERS)
        [public_beta_lane] = [
            lane for lane in lane_blockers["approval_lanes"] if lane["lane_id"] == "public-beta-approval"
        ]

        self.assertEqual(public_beta_lane["lane_name"], prep["lane_name"])
        self.assertEqual(public_beta_lane["approval_owner"], prep["approval_owner"])
        self.assertEqual("blocked_pending_dedicated_approval", public_beta_lane["approval_status"])
        self.assertIn("public beta remains blocked", public_beta_lane["explicit_blockers"])
        self.assertIn("ADR-0005 does not approve public beta", public_beta_lane["explicit_blockers"])
        self.assertIn("public beta remains blocked", prep["explicit_blockers"])
        self.assertIn("ADR-0005 does not approve public beta", prep["explicit_blockers"])

    def test_required_evidence_and_blockers_are_explicit(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(5, len(prep["approval_scope"]))
        self.assertEqual(7, len(prep["required_evidence"]))
        self.assertEqual(7, len(prep["explicit_blockers"]))
        self.assertIn("dedicated public beta approval decision record", prep["required_evidence"])
        self.assertIn("release-scope engineering blocker review", prep["required_evidence"])
        self.assertIn("public setup path review", prep["required_evidence"])
        self.assertIn("decider signoff on exact wording and surface", prep["required_evidence"])
        self.assertIn("public beta remains blocked", prep["explicit_blockers"])
        self.assertIn("H2 source-snapshot closeout does not approve public beta", prep["explicit_blockers"])

    def test_allowed_and_forbidden_wording_stay_narrow(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(
            [
                "Ethos remains source-only pre-alpha for this lane.",
                "Public beta remains blocked pending dedicated approval.",
                "The exact approved pre-alpha sentence may be used on current source-repository surfaces.",
            ],
            prep["allowed_wording"],
        )
        self.assertIn(
            "any statement that expands beyond the exact approved pre-alpha sentence",
            prep["forbidden_wording"],
        )
        self.assertIn(
            "any statement that treats a beta as open for public use",
            prep["forbidden_wording"],
        )

    def test_schema_validation_covers_public_beta_prep(self) -> None:
        schema = load_json(PREP_SCHEMA)
        validate_examples = read(VALIDATE_EXAMPLES)
        schemas_readme = read(SCHEMAS_README)

        self.assertEqual(False, schema["additionalProperties"])
        self.assertEqual(False, schema["$defs"]["approved_source_snapshot"]["additionalProperties"])
        self.assertEqual(7, schema["properties"]["required_evidence"]["minItems"])
        self.assertEqual(7, schema["properties"]["explicit_blockers"]["minItems"])
        self.assertIn("ethos-milestone-e-public-beta-approval-prep.schema.json", validate_examples)
        self.assertIn("docs\" / \"milestone-e-public-beta-approval-prep.json", validate_examples)
        self.assertIn("ethos-milestone-e-public-beta-approval-prep.schema.json", schemas_readme)
        self.assertIn("docs/milestone-e-public-beta-approval-prep.json", schemas_readme)

    def test_docs_reference_public_beta_prep_boundary(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            normalized = " ".join(read(path).split())

            self.assertIn("docs/milestone-e-public-beta-approval-prep.json", normalized, str(path))
            self.assertIn("public beta approval prep", normalized, str(path))
            self.assertIn("does not approve public beta", normalized, str(path))

    def test_make_target_runs_public_beta_prep_after_lane_blocker(self) -> None:
        block = target_block("milestone-e-prep")

        lane_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py"
        )
        beta_guard = "$(PYTHON) .github/scripts/test_milestone_e_public_beta_approval_prep.py"
        beta_record = (
            "$(PYTHON) .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py"
        )
        index_guard = "$(PYTHON) .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(beta_guard, block)
        self.assertIn(beta_record, block)
        self.assertLess(block.index(lane_record), block.index(beta_guard))
        self.assertLess(block.index(beta_guard), block.index(beta_record))
        self.assertLess(block.index(beta_record), block.index(index_guard))
        self.assertLess(block.index(beta_record), block.index("git diff --check"))

    def test_ci_runs_public_beta_prep_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        lane_record = (
            "python3 .github/scripts/test_milestone_e_public_approval_lane_blockers_validation_record.py"
        )
        beta_guard = "python3 .github/scripts/test_milestone_e_public_beta_approval_prep.py"
        beta_record = "python3 .github/scripts/test_milestone_e_public_beta_approval_prep_validation_record.py"
        index_guard = "python3 .github/scripts/test_milestone_e_validation_record_index.py"

        self.assertIn(beta_guard, text)
        self.assertIn(beta_record, text)
        self.assertEqual(1, text.count(beta_guard))
        self.assertEqual(1, text.count(beta_record))
        self.assertLess(text.index(lane_record), text.index(beta_guard))
        self.assertLess(text.index(beta_guard), text.index(beta_record))
        self.assertLess(text.index(beta_record), text.index(index_guard))

    def test_prep_avoids_scope_expansion_language(self) -> None:
        text = json.dumps(load_json(PREP), sort_keys=True).lower()

        for phrase in FORBIDDEN_PREP_WORDING:
            self.assertNotIn(phrase, text)

    def test_prep_avoids_local_private_paths(self) -> None:
        text = read(PREP)

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
