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
    "milestone-e-package-publication-approval-decision-refresh-validation-2026-06-22.md"
)
PRIOR_DECISION_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-approval-decision-validation-2026-06-21.md"
)
CANDIDATE_ACTIVATION_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-candidate-activation-evidence-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "6a9151171b4d019780cfa1c718f8a7264bb4f549"
SOURCE_SHORT = "6a91511"
SOURCE_TREE = "8b150d9aebdc282c358e4552a4d709c3140f41b4"
REQUIRED_REFRESH_FIELDS = [
    "Decision: activation evidence is present; manual exact approval remains required.",
    "Activation evidence status: present through the candidate activation evidence record.",
    "Exact candidate crate list approved by this refresh: none.",
    "Exact package version map approved by this refresh: none.",
    "Exact package tag name set approved by this refresh: none.",
    "Exact package tag source commit and source tree approved by this refresh: none.",
    "Exact source manifest activation diff approved by this refresh: none.",
    "Exact public installation wording approved by this refresh: none.",
    "Public-surface posture check result after this refresh: passed with no public installation wording approval.",
    "Claims gate result after this refresh: passed with package publication blocked.",
    "Milestone E prep result after this refresh record: required for this record branch.",
]
MANUAL_INPUT_FIELDS = [
    "exact candidate crate list for the first package-publication surface",
    "exact package version map, including whether candidate `0.1.0` is accepted or rejected",
    "exact package tag names and source binding",
    "exact source Cargo manifest activation diff",
    "exact registry-equivalent dependent package assembly evidence",
    "exact public installation wording and explicit exclusions",
    "posture, claims, and Milestone E prep gate results",
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


class MilestoneEPackagePublicationApprovalDecisionRefreshTests(unittest.TestCase):
    def test_refresh_record_is_indexed_and_source_bound(self) -> None:
        prep = load_json(PREP)
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication approval decision refresh validation", readme)
        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-approval-decision-refresh-validation-2026-06-22.md",
            prep["follow_up_records"]["package_approval_decision_refresh"],
        )
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Approval decision refresh source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Approval decision refresh source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_refresh_records_activation_evidence_but_requires_manual_approval(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Status: **pass for package publication approval decision refresh with publication blocked**", record)
        for field in REQUIRED_REFRESH_FIELDS:
            self.assertIn(field, record)
        self.assertIn(PRIOR_DECISION_RECORD, record)
        self.assertIn(CANDIDATE_ACTIVATION_RECORD, record)
        self.assertIn("Candidate `0.1.0` remains unapproved as a package publication version", record)
        self.assertIn("Candidate package tags remain uncreated and unapproved", record)
        self.assertIn("Current Cargo manifests remain unchanged", record)
        self.assertIn("Manual Decider Input Required", read(RECORD))
        for field in MANUAL_INPUT_FIELDS:
            self.assertIn(field, record)

    def test_current_manifests_tags_and_registry_state_stay_unactivated(self) -> None:
        prep = load_json(PREP)
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        for value in prep["package_publication_decision_input_packet"]["candidate_package_tag_names"]:
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

    def test_docs_reference_refresh_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("approval decision refresh", doc.lower(), str(path))
            self.assertIn("activation evidence is present", doc.lower(), str(path))
            self.assertIn("manual exact approval remains required", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_refresh_after_activation_evidence_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        evidence_guard = "test_milestone_e_package_publication_candidate_activation_evidence.py"
        refresh_guard = "test_milestone_e_package_publication_approval_decision_refresh.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + refresh_guard, text)
            self.assertEqual(1, text.count(prefix + refresh_guard))
            self.assertLess(text.index(prefix + evidence_guard), text.index(prefix + refresh_guard))
            self.assertLess(text.index(prefix + refresh_guard), text.index(prefix + public_facing_guard))

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
