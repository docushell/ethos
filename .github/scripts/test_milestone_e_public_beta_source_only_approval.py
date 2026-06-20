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
from typing import Any

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "docs/milestone-e-public-beta-approval-prep.json"
LEDGER = ROOT / "docs/milestone-e-public-approval-lane-blockers.json"
RECORD = ROOT / "docs/validation/milestone-e-public-beta-source-only-approval-validation-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
README = ROOT / "README.md"
EXAMPLES_README = ROOT / "examples/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_WORDING = (
    "Ethos is public beta for source-only evaluation. It verifies whether AI citations are "
    "grounded in document evidence across native Ethos JSON and supported foreign parser outputs. "
    "Package publication, hosted surfaces, production positioning, and public benchmark claims "
    "remain blocked."
)
EXPECTED_SOURCE = {
    "surface": "GitHub source repository docushell/ethos source-only evaluation",
    "reviewed_commit": "d755e7c",
    "merged_main_commit": "3f9e1c4",
    "tree": "a9e913b0ba7ecd1567479b2ec773342868cba126",
    "boundary": "source-only clone, build, and validation commands only",
}
FORBIDDEN_SCOPE_WORDING = [
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


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


class MilestoneEPublicBetaSourceOnlyApprovalTests(unittest.TestCase):
    def test_merged_main_commit_matches_reviewed_tree(self) -> None:
        merged_tree = git_output("rev-parse", "3f9e1c4^{tree}")

        self.assertEqual(EXPECTED_SOURCE["tree"], merged_tree)

    def test_prep_and_ledger_record_exact_source_only_approval(self) -> None:
        prep = load_json(PREP)
        ledger = load_json(LEDGER)
        [public_beta_lane] = [
            lane for lane in ledger["approval_lanes"] if lane["lane_id"] == "public-beta-approval"
        ]

        for artifact in (prep, ledger):
            self.assertEqual("approved_source_only_public_beta", artifact.get("approval_status", public_beta_lane["approval_status"]))
            self.assertEqual(EXPECTED_WORDING, artifact["exact_approved_public_beta_wording"])
            self.assertEqual(EXPECTED_SOURCE, artifact["approved_public_beta_source"])

        self.assertEqual("approved_source_only_public_beta", prep["decision_status"])
        self.assertEqual("approved_source_only_public_beta", public_beta_lane["approval_status"])
        self.assertEqual(EXPECTED_WORDING, public_beta_lane["allowed_wording"][0])
        self.assertIn("package publication remains blocked", public_beta_lane["explicit_blockers"])
        self.assertIn("project-maintained PDFium builds remain blocked", " ".join(public_beta_lane["explicit_blockers"]))

    def test_record_is_indexed_and_names_decision(self) -> None:
        readme = read(VALIDATION_README)
        normalized_readme = re.sub(r"\s+", " ", readme)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("source-only public beta approval validation", normalized_readme)
        self.assertIn("Validated source HEAD before this record: `3f9e1c4`", record)
        self.assertIn("Decision: approve source-only public beta evaluation", record)
        self.assertIn(EXPECTED_WORDING, record)
        self.assertIn("Reviewed commit: `d755e7c`", record)
        self.assertIn("Merged main commit: `3f9e1c4`", record)
        self.assertIn("Tree: `a9e913b0ba7ecd1567479b2ec773342868cba126`", record)

    def test_record_names_rescoped_blockers_and_exclusions(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Release-scope engineering blocker: rescoped", record)
        self.assertIn("Public setup path: resolved for source checkout build and validation commands", record)
        self.assertIn("PDFium build path: rescoped and excluded", record)
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Hosted surfaces remain blocked", record)
        self.assertIn("Production positioning remains blocked", record)
        self.assertIn("Public benchmark reports remain blocked", record)
        self.assertIn("Public benchmark claims remain blocked", record)
        self.assertIn("Project-maintained PDFium builds remain blocked", record)

    def test_public_surfaces_use_exact_approved_wording_and_exclusions(self) -> None:
        readme = read(README)
        normalized_readme = re.sub(r"\s+", " ", readme)
        examples = read(EXAMPLES_README)

        self.assertIn(EXPECTED_WORDING, readme)
        self.assertIn("status-public--beta", readme)
        self.assertIn("source-only public beta", examples)
        self.assertIn("cargo build --locked -p ethos-cli", readme)
        self.assertIn("make verify-alpha", readme)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", readme)
        self.assertIn(
            "There are no published crates, wheels, npm packages, binaries, or GitHub release artifacts yet.",
            normalized_readme,
        )

    def test_make_target_and_ci_run_approval_after_required_evidence(self) -> None:
        block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        evidence_guard = "test_milestone_e_public_beta_required_evidence_records.py"
        approval_guard = "test_milestone_e_public_beta_source_only_approval.py"
        package_guard = "test_milestone_e_package_publication_approval_prep.py"
        index_guard = "test_milestone_e_validation_record_index.py"

        for text, prefix in ((block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + approval_guard, text)
            self.assertLess(text.index(prefix + evidence_guard), text.index(prefix + approval_guard))
            self.assertLess(text.index(prefix + approval_guard), text.index(prefix + package_guard))
            self.assertLess(text.index(prefix + approval_guard), text.index(prefix + index_guard))

    def test_record_avoids_scope_expansion_language_and_private_paths(self) -> None:
        text = normalized(RECORD).lower()
        raw = read(RECORD)

        for phrase in FORBIDDEN_SCOPE_WORDING:
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
