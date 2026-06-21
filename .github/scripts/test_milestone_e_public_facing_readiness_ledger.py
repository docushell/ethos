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
LEDGER = ROOT / "docs/milestone-e-public-facing-readiness-ledger.json"
SCHEMA = ROOT / "schemas/ethos-milestone-e-public-facing-readiness-ledger.schema.json"
PUBLIC_BETA_PREP = ROOT / "docs/milestone-e-public-beta-approval-prep.json"
PACKAGE_PREP = ROOT / "docs/milestone-e-package-publication-approval-prep.json"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-public-beta-current-main-source-only-approval-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

CURRENT_MAIN_COMMIT = "6019a97651190182730453988dd4c75e828639fc"
CURRENT_MAIN_TREE = "f56fde854f6f6e4c4070209329f8c7b12310aa51"
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
FORBIDDEN_SCOPE_EXPANSION = [
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "package publication is approved",
    "package publication approved",
    "packages are published",
    "published packages",
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
    "performance validated",
    "quality validated",
    "footprint validated",
    "table-quality validated",
    "parser-quality validated",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class MilestoneEPublicFacingReadinessLedgerTests(unittest.TestCase):
    def test_ledger_records_current_main_source_only_refresh_approval(self) -> None:
        ledger = load_json(LEDGER)

        self.assertEqual(1, ledger["schema_version"])
        self.assertEqual("source-only-pre-alpha-internal-milestone-e-prep", ledger["status"])
        self.assertEqual("public_facing_readiness_current_main_ledger", ledger["scope"])
        self.assertEqual(
            "current_main_source_only_public_beta_refresh_approved",
            ledger["ledger_state"],
        )
        self.assertEqual(CURRENT_MAIN_COMMIT, ledger["validated_current_main"]["commit"])
        self.assertEqual(CURRENT_MAIN_TREE, ledger["validated_current_main"]["tree"])
        self.assertIn(
            "refreshed source-only public beta source state",
            ledger["validated_current_main"]["candidate_status"],
        )
        self.assertEqual(EXPECTED_BOUNDARY, ledger["public_boundary"])

    def test_current_main_binding_resolves_in_repository_history(self) -> None:
        ledger = load_json(LEDGER)

        self.assertEqual(CURRENT_MAIN_COMMIT, git("rev-parse", CURRENT_MAIN_COMMIT))
        self.assertEqual(CURRENT_MAIN_TREE, git("rev-parse", f"{CURRENT_MAIN_COMMIT}^{{tree}}"))
        subprocess.check_call(
            ["git", "merge-base", "--is-ancestor", CURRENT_MAIN_COMMIT, "HEAD"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertEqual(CURRENT_MAIN_COMMIT, ledger["current_main_refresh_candidate"]["candidate_commit"])
        self.assertEqual(
            git("rev-parse", f"{CURRENT_MAIN_COMMIT}^{{tree}}"),
            ledger["current_main_refresh_candidate"]["candidate_tree"],
        )

    def test_public_beta_binding_refreshes_to_current_main(self) -> None:
        ledger = load_json(LEDGER)
        public_beta = load_json(PUBLIC_BETA_PREP)

        self.assertEqual(
            public_beta["approved_public_beta_source"],
            ledger["approved_public_beta_source"],
        )
        self.assertEqual("902c423", ledger["approved_public_beta_source"]["reviewed_commit"])
        self.assertEqual("6019a97", ledger["approved_public_beta_source"]["merged_main_commit"])
        self.assertEqual(
            ledger["approved_public_beta_source"]["tree"],
            ledger["current_main_refresh_candidate"]["candidate_tree"],
        )
        self.assertIn(
            "dedicated source-only public beta refresh approval recorded",
            ledger["current_main_refresh_candidate"]["refresh_status"],
        )

    def test_package_resolution_criteria_match_gap_ledger(self) -> None:
        ledger = load_json(LEDGER)
        package_prep = load_json(PACKAGE_PREP)
        gap_ledger = package_prep["package_publication_pre_approval_gap_ledger"]
        criteria = ledger["package_publication_resolution_criteria"]

        self.assertEqual("pre_approval_gaps_remain_unresolved", criteria["criteria_state"])
        self.assertEqual(
            gap_ledger["required_resolution_inputs"],
            criteria["required_resolution_inputs"],
        )
        self.assertEqual(gap_ledger["retained_blockers"], criteria["retained_blockers"])

    def test_cross_lane_blockers_and_non_approvals_are_explicit(self) -> None:
        ledger = load_json(LEDGER)

        self.assertEqual(14, len(ledger["cross_lane_blockers"]))
        self.assertEqual(12, len(ledger["non_approvals"]))
        self.assertIn("package publication remains blocked", ledger["cross_lane_blockers"])
        self.assertIn("public installation remains blocked", ledger["cross_lane_blockers"])
        self.assertIn("hosted surfaces remain blocked", ledger["cross_lane_blockers"])
        self.assertIn("production positioning remains blocked", ledger["cross_lane_blockers"])
        self.assertIn("public benchmark claims remain blocked", ledger["cross_lane_blockers"])
        self.assertIn("this ledger does not change the approved public beta wording", ledger["non_approvals"])
        self.assertIn("this ledger does not approve package publication", ledger["non_approvals"])
        self.assertIn("this ledger does not approve public installation", ledger["non_approvals"])

    def test_schema_validation_covers_readiness_ledger(self) -> None:
        schema = load_json(SCHEMA)
        validate_examples = read(VALIDATE_EXAMPLES)
        schemas_readme = read(SCHEMAS_README)

        self.assertEqual(False, schema["additionalProperties"])
        self.assertIn("current_main_refresh_candidate", schema["required"])
        self.assertIn("package_publication_resolution_criteria", schema["required"])
        self.assertEqual(14, schema["properties"]["cross_lane_blockers"]["minItems"])
        self.assertEqual(12, schema["properties"]["non_approvals"]["minItems"])
        self.assertEqual(10, schema["properties"]["required_gates"]["maxItems"])
        self.assertIn("ethos-milestone-e-public-facing-readiness-ledger.schema.json", validate_examples)
        self.assertIn("docs\" / \"milestone-e-public-facing-readiness-ledger.json", validate_examples)
        self.assertIn("ethos-milestone-e-public-facing-readiness-ledger.schema.json", schemas_readme)
        self.assertIn("docs/milestone-e-public-facing-readiness-ledger.json", schemas_readme)

    def test_validation_record_indexes_commands_and_boundaries(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)
        ledger = load_json(LEDGER)

        self.assertIn(RECORD.name, readme)
        self.assertIn(
            "current-main source-only public beta approval validation",
            re.sub(r"\s+", " ", readme),
        )
        self.assertIn("Validated source HEAD before this record: `6019a97`", read(RECORD))
        for gate in ledger["required_gates"]:
            self.assertIn(gate, record)
        for blocker in ledger["cross_lane_blockers"]:
            self.assertIn(blocker.lower(), record.lower())
        self.assertIn("Ethos remains source-only pre-alpha", record)
        self.assertIn("Public reports remain blocked", record)
        self.assertIn("Public result wording remains blocked", record)

    def test_docs_reference_public_facing_readiness_ledger(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn("docs/milestone-e-public-facing-readiness-ledger.json", doc, str(path))
            self.assertIn("public-facing readiness ledger", doc, str(path))
            self.assertIn("current-main source-only public beta", doc, str(path))
            self.assertIn("package publication remains blocked", doc, str(path))

    def test_make_and_ci_run_readiness_ledger_after_package_gap_ledger(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        package_gap_guard = "test_milestone_e_package_publication_pre_approval_gap_ledger.py"
        ledger_guard = "test_milestone_e_public_facing_readiness_ledger.py"
        command_guard = "test_milestone_e_validation_command_index.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + ledger_guard, text)
            self.assertEqual(1, text.count(prefix + ledger_guard))
            self.assertLess(text.index(prefix + package_gap_guard), text.index(prefix + ledger_guard))
            self.assertLess(text.index(prefix + ledger_guard), text.index(prefix + command_guard))

    def test_ledger_avoids_scope_expansion_language_or_private_paths(self) -> None:
        lower = json.dumps(load_json(LEDGER), sort_keys=True).lower()
        record_lower = normalized(RECORD).lower()
        raw = read(LEDGER) + read(RECORD)

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, lower)
            self.assertNotIn(phrase, record_lower)
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
