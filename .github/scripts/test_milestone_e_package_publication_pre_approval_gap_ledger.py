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
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "docs/milestone-e-package-publication-approval-prep.json"
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-pre-approval-gap-ledger-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

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


class MilestoneEPackagePublicationPreApprovalGapLedgerTests(unittest.TestCase):
    def test_gap_ledger_record_is_indexed(self) -> None:
        readme = read(VALIDATION_README)
        normalized_readme = re.sub(r"\s+", " ", readme)

        self.assertIn(RECORD.name, readme)
        self.assertIn(
            "package publication pre-approval gap-ledger validation",
            normalized_readme,
        )

    def test_record_names_validation_commands(self) -> None:
        text = read(RECORD)

        self.assertIn("Validated source HEAD before this record: `c28704f`", text)
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_package_publication_approval_prep.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/test_milestone_e_package_publication_pre_approval_gap_ledger.py",
            text,
        )
        self.assertIn("python3 .github/scripts/test_public_surface_posture.py", text)
        self.assertIn("python3 .github/scripts/claims_gate.py", text)
        self.assertIn("make milestone-e-prep PYTHON=<jsonschema-venv>/bin/python", text)
        self.assertIn("git diff --check", text)

    def test_record_matches_gap_ledger_without_approving_actions(self) -> None:
        prep = load_json(PREP)
        ledger = prep["package_publication_pre_approval_gap_ledger"]
        record = normalized(RECORD)

        self.assertEqual("pre_approval_gaps_recorded_publication_blocked", ledger["ledger_state"])
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
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation remains blocked", record)

    def test_current_manifests_stay_non_publishable(self) -> None:
        cargo = read(ROOT / "Cargo.toml")
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        self.assertIn('"crates/ethos-core"', cargo)
        self.assertIn('"crates/ethos-verify"', cargo)
        self.assertIn('"crates/ethos-pdf"', cargo)
        self.assertIn("publish = false", core_manifest)
        self.assertIn("publish = false", verify_manifest)
        self.assertIn("publish = false", pdf_manifest)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', core_manifest)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', verify_manifest)
        self.assertIn('reserved_crates_io_version = "0.0.0-reserved.0"', pdf_manifest)

    def test_make_and_ci_run_gap_ledger_after_decision_bundle(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        bundle_guard = "test_milestone_e_package_publication_decision_bundle_validation_record.py"
        gap_guard = "test_milestone_e_package_publication_pre_approval_gap_ledger.py"
        command_guard = "test_milestone_e_validation_command_index.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + gap_guard, text)
            self.assertEqual(1, text.count(prefix + gap_guard))
            self.assertLess(text.index(prefix + bundle_guard), text.index(prefix + gap_guard))
            self.assertLess(text.index(prefix + gap_guard), text.index(prefix + command_guard))

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
