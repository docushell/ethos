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
    "milestone-e-package-publication-approval-decision-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "fdbd5b7e1817ab73d459f25faadc2132263d88ff"
SOURCE_SHORT = "fdbd5b7"
SOURCE_TREE = "4a7bf5cda2c779e41a04c3feb691a12fec1e5c8d"
REQUIRED_DECISION_FIELDS = [
    "Decision: reject current package publication approval request.",
    "Approver: docushell-admin acting as decider.",
    "Date: 2026-06-21.",
    "Exact candidate crate list reviewed for this decision: `ethos-doc-core`, `ethos-verify`, and `ethos-pdf` only.",
    "Exact package version map approved by this decision: none; candidate `0.1.0` remains unapproved.",
    "Exact package tag name set approved by this decision: none; candidate package tags remain uncreated and unapproved.",
    "Exact package tag source commit and source tree approved by this decision: none.",
    "Exact package-name migration diff for `ethos-doc-core` approved by this decision: none; current Cargo manifests remain unchanged.",
    "Exact dependency manifest activation diff for `ethos-verify` and `ethos-pdf` approved by this decision: none; current Cargo manifests remain unchanged.",
    "Exact registry-backed dependent package assembly evidence after manifest activation: absent; no registry is created and no registry-backed assembly is activated.",
    "Exact public installation wording approved by this decision: none; public installation wording remains blocked.",
    "Public-surface posture check result after this decision: passed with no public installation wording approval.",
    "Claims gate result after this decision: passed with package publication blocked.",
    "Milestone E prep result after this decision record: required for this record branch.",
]
FORBIDDEN_SCOPE_EXPANSION = [
    "package publication approved",
    "package publication is approved",
    "public installation approved",
    "public installation is approved",
    "public installation wording is approved",
    "package tag creation approved",
    "cargo manifests are changed",
    "registry creation approved",
    "registry-backed assembly activation approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "packages are published",
    "published packages",
    "production-ready",
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


class MilestoneEPackagePublicationApprovalDecisionRecordTests(unittest.TestCase):
    def test_decision_record_is_indexed_and_source_bound(self) -> None:
        prep = load_json(PREP)
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication approval decision validation", readme)
        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-approval-decision-validation-2026-06-21.md",
            prep["follow_up_records"]["package_approval_decision_record"],
        )
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Approval decision source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Approval decision source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_decision_rejects_current_package_publication_request(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Decision: **reject current package publication approval request**", record)
        for field in REQUIRED_DECISION_FIELDS:
            self.assertIn(field, record)
        self.assertIn("Status: **pass for package publication approval decision with publication blocked**", record)
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation remains blocked", record)
        self.assertIn("No public installation wording was approved", record)
        self.assertIn("No package publication version was selected", record)
        self.assertIn("No package tag was created", record)
        self.assertIn("No Cargo manifest was changed", record)
        self.assertIn("No registry was created", record)
        self.assertIn("No registry-backed assembly was activated", record)

    def test_current_manifests_tags_and_registry_state_stay_unactivated(self) -> None:
        packet = load_json(PREP)["package_publication_decision_input_packet"]
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        for value in packet["candidate_package_tag_names"]:
            tag = value.split(": ", maxsplit=1)[1].split(";", maxsplit=1)[0]
            self.assertEqual("", git("tag", "--list", tag))
        self.assertIn('name = "ethos-core"', core_manifest)
        self.assertIn("publish = false", core_manifest)
        self.assertIn("publish = false", verify_manifest)
        self.assertIn("publish = false", pdf_manifest)
        self.assertNotIn('package = "ethos-doc-core"', verify_manifest)
        self.assertNotIn('package = "ethos-doc-core"', pdf_manifest)
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_decision_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("approval decision", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_decision_after_template_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        template_guard = "test_milestone_e_package_publication_approval_decision_template.py"
        decision_guard = "test_milestone_e_package_publication_approval_decision_record.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + decision_guard, text)
            self.assertEqual(1, text.count(prefix + decision_guard))
            self.assertLess(text.index(prefix + template_guard), text.index(prefix + decision_guard))
            self.assertLess(text.index(prefix + decision_guard), text.index(prefix + public_facing_guard))

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
