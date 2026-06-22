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
    "milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "9054f1c3823b8f0ff69f0776b60060b642705e28"
SOURCE_SHORT = "9054f1c"
SOURCE_TREE = "3f8cb66249826d67ab6030032c7784a2a4ff411b"
HISTORICAL_CANDIDATE_CRATES = [
    "ethos-doc-core mapped from crates/ethos-core; package-name migration remains pending",
    "ethos-verify mapped from crates/ethos-verify; dependency manifest activation remains pending",
    "ethos-pdf mapped from crates/ethos-pdf; dependency manifest activation and PDFium boundary confirmation must remain current",
]
HISTORICAL_CANDIDATE_MANIFEST_DIFF = [
    "crates/ethos-core/Cargo.toml candidate package-name migration: package.name ethos-core -> ethos-doc-core; current manifest remains unchanged",
    "crates/ethos-verify/Cargo.toml candidate dependency activation: ethos_core package alias points at ethos-doc-core; current manifest remains unchanged",
    "crates/ethos-pdf/Cargo.toml candidate dependency activation: ethos_core package alias points at ethos-doc-core; current manifest remains unchanged",
    "included candidate crates require later publish-flag activation only after dedicated approval; current manifests remain publish=false",
]
HISTORICAL_RETAINED_BLOCKERS = [
    "candidate package version map is recorded but no package publication version is selected",
    "candidate package tag names are recorded but no package tag is created",
    "candidate manifest activation diff is recorded but no Cargo manifest is changed",
    "registry-backed dependent package assembly evidence remains required",
    "public installation remains blocked",
    "package publication remains blocked",
    "real-version cargo publish remains blocked",
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


class MilestoneEPackagePublicationApprovalReadinessReviewTests(unittest.TestCase):
    def test_readiness_record_is_indexed_and_source_bound(self) -> None:
        prep = load_json(PREP)
        readme = read(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication approval-readiness review validation", re.sub(r"\s+", " ", readme))
        self.assertEqual(
            "docs/validation/milestone-e-package-publication-approval-readiness-review-validation-2026-06-21.md",
            prep["follow_up_records"]["package_approval_readiness_review"],
        )
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Readiness review source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Readiness review source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_readiness_review_summarizes_present_inputs_and_remaining_blockers(self) -> None:
        prep = load_json(PREP)
        packet = prep["package_publication_decision_input_packet"]
        record = normalized(RECORD)

        self.assertEqual("decision_input_packet_recorded_publication_blocked", packet["packet_state"])
        for crate in HISTORICAL_CANDIDATE_CRATES:
            self.assertIn(crate, record)
        for version in packet["candidate_version_map"]:
            self.assertIn(version, record)
        for tag in packet["candidate_package_tag_names"]:
            self.assertIn(tag, record)
        for candidate_diff in HISTORICAL_CANDIDATE_MANIFEST_DIFF:
            self.assertIn(candidate_diff, record)
        for blocker in HISTORICAL_RETAINED_BLOCKERS:
            self.assertIn(blocker, record)
        self.assertIn("exact package publication approval decision record remains required", record)
        self.assertIn("registry-backed dependent package assembly evidence remains required", record)
        self.assertIn("public-surface posture check after exact public installation wording changes remains required", record)
        self.assertIn("claims gate after exact public installation wording changes remains required", record)
        self.assertIn("make milestone-e-prep after exact decision record remains required", record)
        self.assertIn("Package publication remains blocked", record)
        self.assertIn("Public installation remains blocked", record)

    def test_candidate_inputs_do_not_activate_tags_or_manifests(self) -> None:
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

    def test_docs_reference_readiness_review_and_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path)

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("package publication approval readiness review", doc.lower(), str(path))
            self.assertIn("package publication remains blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_readiness_review_after_decision_input_packet(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        packet_guard = "test_milestone_e_package_publication_decision_input_packet.py"
        readiness_guard = "test_milestone_e_package_publication_approval_readiness_review.py"
        public_facing_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + readiness_guard, text)
            self.assertEqual(1, text.count(prefix + readiness_guard))
            self.assertLess(text.index(prefix + packet_guard), text.index(prefix + readiness_guard))
            self.assertLess(text.index(prefix + readiness_guard), text.index(prefix + public_facing_guard))

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
