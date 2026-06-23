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
PREP = ROOT / "docs/milestone-e-public-beta-current-main-refresh-prep.json"
SCHEMA = ROOT / "schemas/ethos-milestone-e-public-beta-current-main-refresh-prep.schema.json"
PUBLIC_BETA_PREP = ROOT / "docs/milestone-e-public-beta-approval-prep.json"
READINESS_LEDGER = ROOT / "docs/milestone-e-public-facing-readiness-ledger.json"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-public-beta-current-main-refresh-prep-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

REFRESH_COMMIT = "9262b281ee2cfb7fb0c9adf9f70afafe624e6878"
REFRESH_TREE = "9f18f9e40c57551aef9b0cb2a53641c87207546b"
PRIOR_READINESS_COMMIT = "847e12db42d4519665b1486ccb35c85fe01f00b0"
PRIOR_READINESS_TREE = "9d3701aa14d98017626583c2a0a0ef45ac0df79f"
CURRENT_APPROVED_MAIN = "6019a97651190182730453988dd4c75e828639fc"
PRE_REFRESH_SOURCE = {
    "surface": "GitHub source repository docushell/ethos source-only evaluation",
    "reviewed_commit": "d755e7c",
    "merged_main_commit": "3f9e1c4",
    "tree": "a9e913b0ba7ecd1567479b2ec773342868cba126",
    "boundary": "source-only clone, build, and validation commands only",
}
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


class MilestoneEPublicBetaCurrentMainRefreshPrepTests(unittest.TestCase):
    def test_refresh_prep_records_candidate_without_approval(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(1, prep["schema_version"])
        self.assertEqual("source-only-pre-alpha-internal-milestone-e-prep", prep["status"])
        self.assertEqual("public_beta_current_main_refresh_prep", prep["scope"])
        self.assertEqual("public-beta-approval", prep["lane_id"])
        self.assertEqual("current_main_refresh_prepared_approval_blocked", prep["decision_state"])
        self.assertEqual(REFRESH_COMMIT, prep["refresh_candidate"]["candidate_commit"])
        self.assertEqual(REFRESH_TREE, prep["refresh_candidate"]["candidate_tree"])
        self.assertIn("no refreshed source approval", prep["refresh_candidate"]["candidate_state"])
        self.assertEqual(EXPECTED_BOUNDARY, prep["public_boundary"])

    def test_refresh_candidate_resolves_in_repository_history(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(REFRESH_COMMIT, git("rev-parse", REFRESH_COMMIT))
        self.assertEqual(REFRESH_TREE, git("rev-parse", f"{REFRESH_COMMIT}^{{tree}}"))
        subprocess.check_call(
            ["git", "merge-base", "--is-ancestor", REFRESH_COMMIT, "HEAD"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertEqual(REFRESH_COMMIT, prep["refresh_candidate"]["candidate_commit"])
        self.assertEqual(REFRESH_TREE, prep["refresh_candidate"]["candidate_tree"])

    def test_existing_public_beta_and_readiness_bindings_stay_separate(self) -> None:
        prep = load_json(PREP)
        public_beta = load_json(PUBLIC_BETA_PREP)
        readiness = load_json(READINESS_LEDGER)

        self.assertEqual(PRE_REFRESH_SOURCE, prep["existing_public_beta_source"])
        self.assertNotEqual(public_beta["approved_public_beta_source"], prep["existing_public_beta_source"])
        self.assertEqual(PRIOR_READINESS_COMMIT, prep["prior_readiness_ledger_candidate"]["candidate_commit"])
        self.assertEqual(PRIOR_READINESS_TREE, prep["prior_readiness_ledger_candidate"]["candidate_tree"])
        self.assertEqual(CURRENT_APPROVED_MAIN, readiness["current_main_refresh_candidate"]["candidate_commit"])
        self.assertNotEqual(
            prep["existing_public_beta_source"]["tree"],
            prep["refresh_candidate"]["candidate_tree"],
        )
        self.assertNotEqual(
            prep["prior_readiness_ledger_candidate"]["candidate_tree"],
            prep["refresh_candidate"]["candidate_tree"],
        )

    def test_required_evidence_non_approvals_and_blockers_are_explicit(self) -> None:
        prep = load_json(PREP)

        self.assertEqual(7, len(prep["refresh_required_evidence"]))
        self.assertEqual(8, len(prep["refresh_non_approvals"]))
        self.assertEqual(14, len(prep["retained_blockers"]))
        self.assertIn("dedicated source-only public beta refresh decision record", prep["refresh_required_evidence"])
        self.assertIn("exact refreshed source commit and tree", prep["refresh_required_evidence"])
        self.assertIn("this prep does not refresh the reviewed public beta source state", prep["refresh_non_approvals"])
        self.assertIn("this prep does not approve package publication", prep["refresh_non_approvals"])
        self.assertIn("package publication remains blocked", prep["retained_blockers"])
        self.assertIn("public installation remains blocked", prep["retained_blockers"])
        self.assertIn("public benchmark claims remain blocked", prep["retained_blockers"])

    def test_schema_validation_covers_current_main_refresh_prep(self) -> None:
        schema = load_json(SCHEMA)
        validate_examples = read(VALIDATE_EXAMPLES)
        schemas_readme = read(SCHEMAS_README)

        self.assertEqual(False, schema["additionalProperties"])
        self.assertIn("refresh_candidate", schema["required"])
        self.assertIn("existing_public_beta_source", schema["required"])
        self.assertEqual(7, schema["properties"]["refresh_required_evidence"]["minItems"])
        self.assertEqual(8, schema["properties"]["refresh_non_approvals"]["minItems"])
        self.assertIn("ethos-milestone-e-public-beta-current-main-refresh-prep.schema.json", validate_examples)
        self.assertIn("docs\" / \"milestone-e-public-beta-current-main-refresh-prep.json", validate_examples)
        self.assertIn("ethos-milestone-e-public-beta-current-main-refresh-prep.schema.json", schemas_readme)
        self.assertIn("docs/milestone-e-public-beta-current-main-refresh-prep.json", schemas_readme)

    def test_validation_record_indexes_commands_and_boundaries(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)
        record_lower = record.lower()
        prep = load_json(PREP)

        self.assertIn(RECORD.name, readme)
        self.assertIn("public beta current-main refresh prep validation", re.sub(r"\s+", " ", readme))
        self.assertIn("Validated source HEAD before this record: `9262b28`", read(RECORD))
        for gate in prep["required_gates"]:
            self.assertIn(gate, record)
        for blocker in prep["retained_blockers"]:
            self.assertIn(blocker.lower(), record_lower)
        self.assertIn("Ethos remains source-only pre-alpha", record)
        self.assertIn("Public reports remain blocked", record)
        self.assertIn("Public result wording remains blocked", record)

    def test_docs_reference_current_main_refresh_prep(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn("docs/milestone-e-public-beta-current-main-refresh-prep.json", doc, str(path))
            self.assertIn("public beta current-main refresh prep", doc, str(path))
            self.assertIn("current-main refresh candidate", doc, str(path))
            self.assertIn("package publication remains blocked", doc, str(path))

    def test_make_and_ci_run_refresh_prep_after_readiness_ledger(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"
        refresh_guard = "test_milestone_e_public_beta_current_main_refresh_prep.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + refresh_guard, text)
            self.assertEqual(1, text.count(prefix + refresh_guard))
            self.assertLess(text.index(prefix + readiness_guard), text.index(prefix + refresh_guard))

    def test_refresh_prep_avoids_scope_expansion_language_or_private_paths(self) -> None:
        lower = json.dumps(load_json(PREP), sort_keys=True).lower()
        record_lower = normalized(RECORD).lower()
        raw = read(PREP) + read(RECORD)

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
