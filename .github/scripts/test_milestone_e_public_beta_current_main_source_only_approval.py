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
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_BETA_PREP = ROOT / "docs/milestone-e-public-beta-approval-prep.json"
LANE_BLOCKERS = ROOT / "docs/milestone-e-public-approval-lane-blockers.json"
READINESS_LEDGER = ROOT / "docs/milestone-e-public-facing-readiness-ledger.json"
REFRESH_PREP = ROOT / "docs/milestone-e-public-beta-current-main-refresh-prep.json"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

REVIEWED_COMMIT = "902c423"
MERGED_MAIN_COMMIT = "6019a97"
MERGED_MAIN_FULL = "6019a97651190182730453988dd4c75e828639fc"
APPROVED_TREE = "f56fde854f6f6e4c4070209329f8c7b12310aa51"
APPROVED_SOURCE = {
    "surface": "GitHub source repository docushell/ethos source-only evaluation",
    "reviewed_commit": REVIEWED_COMMIT,
    "merged_main_commit": MERGED_MAIN_COMMIT,
    "tree": APPROVED_TREE,
    "boundary": "source-only clone, build, and validation commands only",
}
APPROVED_WORDING = (
    "Ethos is public beta for source-only evaluation. It verifies whether AI citations are "
    "grounded in document evidence across native Ethos JSON and supported foreign parser outputs. "
    "Package publication, hosted surfaces, production positioning, and public benchmark claims "
    "remain blocked."
)
RETAINED_BLOCKERS = [
    "Package publication remains blocked",
    "Public installation remains blocked",
    "Hosted surfaces remain blocked",
    "Production positioning remains blocked",
    "Public benchmark reports remain blocked",
    "Public benchmark claims remain blocked",
    "Release artifacts remain blocked",
    "Binaries remain blocked",
    "Wheels remain blocked",
    "npm packages remain blocked",
    "Crate publication remains blocked",
    "Project-maintained PDFium builds remain blocked",
    "Public reports remain blocked",
    "Public result wording remains blocked",
]
REQUIRED_COMMANDS = [
    "python3 .github/scripts/test_milestone_e_public_beta_current_main_refresh_prep.py",
    "python3 .github/scripts/test_milestone_e_public_beta_current_main_source_only_approval.py",
    "python3 .github/scripts/test_public_surface_posture.py",
    "python3 .github/scripts/claims_gate.py",
    "cargo build --locked -p ethos-cli",
    "make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python",
    "git diff --check",
]
FORBIDDEN_SCOPE_EXPANSION = [
    "package publication approved",
    "public installation approved",
    "hosted surface approved",
    "hosted demo approved",
    "production positioning approved",
    "public benchmark report approved",
    "public benchmark claims approved",
    "release artifact approved",
    "binaries approved",
    "wheels approved",
    "npm packages approved",
    "crate publication approved",
    "project-maintained PDFium builds approved",
    "public result wording approved",
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


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class MilestoneEPublicBetaCurrentMainSourceOnlyApprovalTests(unittest.TestCase):
    def test_canonical_public_beta_source_binding_is_refreshed(self) -> None:
        public_beta = load_json(PUBLIC_BETA_PREP)
        lane_blockers = load_json(LANE_BLOCKERS)
        readiness = load_json(READINESS_LEDGER)
        [public_beta_lane] = [
            lane for lane in lane_blockers["approval_lanes"] if lane["lane_id"] == "public-beta-approval"
        ]

        self.assertEqual(APPROVED_SOURCE, public_beta["approved_public_beta_source"])
        self.assertEqual(APPROVED_SOURCE, lane_blockers["approved_public_beta_source"])
        self.assertEqual(APPROVED_SOURCE, readiness["approved_public_beta_source"])
        self.assertEqual(APPROVED_WORDING, public_beta["exact_approved_public_beta_wording"])
        self.assertEqual(APPROVED_WORDING, lane_blockers["exact_approved_public_beta_wording"])
        self.assertEqual(APPROVED_WORDING, public_beta_lane["allowed_wording"][0])
        self.assertEqual("approved_source_only_public_beta", public_beta["decision_status"])
        self.assertEqual("approved_source_only_public_beta", public_beta_lane["approval_status"])

    def test_reviewed_branch_and_merged_main_share_approved_tree(self) -> None:
        self.assertEqual(APPROVED_TREE, git("rev-parse", f"{REVIEWED_COMMIT}^{{tree}}"))
        self.assertEqual(APPROVED_TREE, git("rev-parse", f"{MERGED_MAIN_COMMIT}^{{tree}}"))
        self.assertEqual(MERGED_MAIN_FULL, git("rev-parse", MERGED_MAIN_COMMIT))
        subprocess.check_call(
            ["git", "merge-base", "--is-ancestor", MERGED_MAIN_COMMIT, "HEAD"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def test_readiness_ledger_records_refresh_approval_without_lane_expansion(self) -> None:
        readiness = load_json(READINESS_LEDGER)

        self.assertEqual(
            "current_main_source_only_public_beta_refresh_approved",
            readiness["ledger_state"],
        )
        self.assertEqual(MERGED_MAIN_FULL, readiness["validated_current_main"]["commit"])
        self.assertEqual(APPROVED_TREE, readiness["validated_current_main"]["tree"])
        self.assertIn(
            "refreshed source-only public beta source state",
            readiness["validated_current_main"]["candidate_status"],
        )
        self.assertEqual(MERGED_MAIN_FULL, readiness["current_main_refresh_candidate"]["candidate_commit"])
        self.assertEqual(APPROVED_TREE, readiness["current_main_refresh_candidate"]["candidate_tree"])
        self.assertIn(
            "package publication, public installation, hosted surfaces, production positioning, and public benchmark lanes remain blocked",
            readiness["current_main_refresh_candidate"]["refresh_status"],
        )
        self.assertIn("this ledger does not change the approved public beta wording", readiness["non_approvals"])
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_public_beta_current_main_source_only_approval.py",
            readiness["required_gates"],
        )

    def test_refresh_prep_remains_historical_input_not_current_approval(self) -> None:
        refresh_prep = load_json(REFRESH_PREP)

        self.assertEqual("current_main_refresh_prepared_approval_blocked", refresh_prep["decision_state"])
        self.assertEqual("9262b281ee2cfb7fb0c9adf9f70afafe624e6878", refresh_prep["refresh_candidate"]["candidate_commit"])
        self.assertEqual("9f18f9e40c57551aef9b0cb2a53641c87207546b", refresh_prep["refresh_candidate"]["candidate_tree"])
        self.assertNotEqual(APPROVED_SOURCE, refresh_prep["existing_public_beta_source"])

    def test_approval_record_indexes_exact_surface_commands_and_exclusions(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("current-main source-only public beta approval validation", re.sub(r"\s+", " ", readme))
        self.assertIn("Validated source HEAD before this record: `6019a97`", read(RECORD))
        self.assertIn("Decision: approve current-main source-only public beta evaluation", record)
        self.assertIn(f"Reviewed commit: `{REVIEWED_COMMIT}`", record)
        self.assertIn(f"Merged main commit: `{MERGED_MAIN_COMMIT}`", record)
        self.assertIn(f"Tree: `{APPROVED_TREE}`", record)
        self.assertIn(APPROVED_WORDING, record)
        for command in REQUIRED_COMMANDS:
            self.assertIn(command, record)
        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, record)

    def test_docs_reference_current_main_source_only_approval(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn("current-main source-only public beta", doc, str(path))
            self.assertIn("6019a97", doc, str(path))
            self.assertIn("package publication remains blocked", doc, str(path))

    def test_make_and_ci_run_current_main_approval_after_refresh_prep(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        refresh_guard = "test_milestone_e_public_beta_current_main_refresh_prep.py"
        approval_guard = "test_milestone_e_public_beta_current_main_source_only_approval.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + approval_guard, text)
            self.assertEqual(1, text.count(prefix + approval_guard))
            self.assertLess(text.index(prefix + refresh_guard), text.index(prefix + approval_guard))

    def test_approval_record_avoids_scope_expansion_language_and_private_paths(self) -> None:
        text = (
            json.dumps(load_json(PUBLIC_BETA_PREP), sort_keys=True)
            + json.dumps(load_json(LANE_BLOCKERS), sort_keys=True)
            + json.dumps(load_json(READINESS_LEDGER), sort_keys=True)
            + normalized(RECORD)
        ).lower()
        raw = read(RECORD) + read(PUBLIC_BETA_PREP) + read(LANE_BLOCKERS) + read(READINESS_LEDGER)

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, text)
        self.assertNotIn("/Users/", raw)
        self.assertNotIn("/private/tmp", raw)
        self.assertNotIn("/private/var", raw)
        self.assertNotIn("/var/folders", raw)
        self.assertNotIn("saumildiwaker", raw)
        self.assertNotIn("Desktop/Stuff", raw)
        self.assertNotIn("project/repo/ethos", raw)
        self.assertNotIn("docs/.roadmap.md.swp", raw)
        self.assertNotIn("web/", raw)


if __name__ == "__main__":
    unittest.main()
