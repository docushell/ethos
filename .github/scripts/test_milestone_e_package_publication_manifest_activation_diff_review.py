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
    "milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "89d24c84614a7c961dcecdccf85a9e9eca235046"
SOURCE_SHORT = "89d24c8"
SOURCE_TREE = "21b263dca908ef7cc977e7669e40206096eef93e"
HISTORICAL_CANDIDATE_MANIFEST_DIFF = [
    "crates/ethos-core/Cargo.toml candidate package-name migration: package.name ethos-core -> ethos-doc-core; current manifest remains unchanged",
    "crates/ethos-verify/Cargo.toml candidate dependency activation: ethos_core package alias points at ethos-doc-core; current manifest remains unchanged",
    "crates/ethos-pdf/Cargo.toml candidate dependency activation: ethos_core package alias points at ethos-doc-core; current manifest remains unchanged",
    "included candidate crates require later publish-flag activation only after dedicated approval; current manifests remain publish=false",
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


class MilestoneEPackagePublicationManifestActivationDiffReviewTests(unittest.TestCase):
    def test_diff_review_record_is_indexed_and_source_bound(self) -> None:
        prep = load_json(PREP)
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication manifest-activation diff review validation", readme)
        self.assertEqual(
            "docs/validation/"
            "milestone-e-package-publication-manifest-activation-diff-review-validation-2026-06-21.md",
            prep["follow_up_records"]["package_manifest_activation_diff_review"],
        )
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Manifest activation diff review source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Manifest activation diff review source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_record_carries_candidate_manifest_diff_without_activation(self) -> None:
        packet = load_json(PREP)["package_publication_decision_input_packet"]
        record = normalized(RECORD)

        for candidate_diff in HISTORICAL_CANDIDATE_MANIFEST_DIFF:
            self.assertIn(candidate_diff, record)
        self.assertIn("Candidate manifest activation diff is recorded", record)
        self.assertIn("No Cargo manifest was changed", record)
        self.assertIn("No package tag was created", record)
        self.assertIn("No registry-backed assembly was activated", record)
        self.assertIn("Package publication and public installation remained blocked", record)
        self.assertIn("registry-backed dependent package assembly evidence remains required", record)
        self.assertIn("public-surface posture check after exact public installation wording changes remains required", record)
        self.assertIn("claims gate after exact public installation wording changes remains required", record)

    def test_current_manifests_stay_unactivated(self) -> None:
        packet = load_json(PREP)["package_publication_decision_input_packet"]
        core_manifest = read(ROOT / "crates/ethos-core/Cargo.toml")
        verify_manifest = read(ROOT / "crates/ethos-verify/Cargo.toml")
        pdf_manifest = read(ROOT / "crates/ethos-pdf/Cargo.toml")

        for value in packet["candidate_package_tag_names"]:
            tag = value.split(": ", maxsplit=1)[1].split(";", maxsplit=1)[0]
            self.assertEqual("", git("tag", "--list", tag))
        self.assertIn('name = "ethos-doc-core"', core_manifest)
        self.assertIn('reserved_crates_io_name = "ethos-doc-core"', core_manifest)
        self.assertNotIn("publish = false", core_manifest)
        self.assertIn('name = "ethos-verify"', verify_manifest)
        self.assertNotIn("publish = false", verify_manifest)
        self.assertIn('name = "ethos-pdf"', pdf_manifest)
        self.assertNotIn("publish = false", pdf_manifest)
        self.assertNotIn('package = "ethos-doc-core"', verify_manifest)
        self.assertNotIn('package = "ethos-doc-core"', pdf_manifest)

    def test_docs_reference_diff_review_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("manifest-activation diff review", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_diff_review_after_readiness_review(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        readiness_guard = "test_milestone_e_package_publication_approval_readiness_review.py"
        diff_review_guard = "test_milestone_e_package_publication_manifest_activation_diff_review.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + diff_review_guard, text)
            self.assertEqual(1, text.count(prefix + diff_review_guard))
            self.assertLess(text.index(prefix + readiness_guard), text.index(prefix + diff_review_guard))
            self.assertLess(text.index(prefix + diff_review_guard), text.index(prefix + public_facing_guard))

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
