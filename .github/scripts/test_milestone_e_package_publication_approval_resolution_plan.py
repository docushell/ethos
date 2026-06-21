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
PREP = ROOT / "docs/milestone-e-package-publication-approval-prep.json"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-approval-resolution-plan-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

CURRENT_MAIN = "524535a621532b5382f91a38d9c3f85d6714a526"
CURRENT_MAIN_SHORT = "524535a"
CURRENT_TREE = "0785ffca8423c42e2c4105df7752e290cc88e5c2"
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


class MilestoneEPackagePublicationApprovalResolutionPlanTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication approval resolution-plan validation", re.sub(r"\s+", " ", readme))
        self.assertIn(f"Validated source HEAD before this record: `{CURRENT_MAIN_SHORT}`", read(RECORD))
        self.assertIn(f"Current source commit: `{CURRENT_MAIN}`", record)
        self.assertIn(f"Current source tree: `{CURRENT_TREE}`", record)
        self.assertEqual(CURRENT_MAIN, git("rev-parse", CURRENT_MAIN_SHORT))
        self.assertEqual(CURRENT_TREE, git("rev-parse", f"{CURRENT_MAIN_SHORT}^{{tree}}"))

    def test_record_covers_gap_ledger_and_request_packet_without_approval(self) -> None:
        prep = load_json(PREP)
        ledger = prep["package_publication_pre_approval_gap_ledger"]
        packet = prep["package_publication_approval_request_packet"]
        record = normalized(RECORD)

        self.assertIn(ledger["ledger_state"], record)
        for row in ledger["gap_rows"]:
            self.assertIn(row, record)
        for action in ledger["blocked_actions"]:
            self.assertIn(action, record)
        for required in ledger["required_resolution_inputs"]:
            self.assertIn(required, record)
        for non_approval in ledger["non_approvals"]:
            self.assertIn(non_approval, record)
        for blocker in ledger["retained_blockers"]:
            self.assertIn(blocker, record)
        for crate in packet["candidate_crates"]:
            self.assertIn(crate, record)
        for exclusion in packet["explicit_exclusions"]:
            self.assertIn(exclusion, record)
        self.assertIn(packet["public_installation_wording"], record)
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation remains blocked", record)

    def test_current_manifests_remain_non_publishable(self) -> None:
        for manifest in (
            ROOT / "crates/ethos-core/Cargo.toml",
            ROOT / "crates/ethos-verify/Cargo.toml",
            ROOT / "crates/ethos-pdf/Cargo.toml",
        ):
            text = read(manifest)

            self.assertIn("publish = false", text)
            self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', text)

    def test_docs_reference_resolution_plan_and_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("package publication approval resolution plan", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_resolution_plan_after_gap_ledger(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        gap_guard = "test_milestone_e_package_publication_pre_approval_gap_ledger.py"
        resolution_guard = "test_milestone_e_package_publication_approval_resolution_plan.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + resolution_guard, text)
            self.assertEqual(1, text.count(prefix + resolution_guard))
            self.assertLess(text.index(prefix + gap_guard), text.index(prefix + resolution_guard))
            self.assertLess(text.index(prefix + resolution_guard), text.index(prefix + public_facing_guard))

    def test_record_avoids_scope_expansion_language_or_private_paths(self) -> None:
        lower = normalized(RECORD).lower()
        raw = read(RECORD)

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, lower)
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
