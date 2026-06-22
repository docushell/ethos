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

import re
import subprocess
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
RECORD = (
    ROOT
    / "docs/validation/"
    "milestone-e-package-publication-registry-action-evidence-validation-2026-06-22.md"
)
APPROVAL_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-registry-action-approval-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

RECORD_SOURCE_COMMIT = "38e0158d7df5fddeded942926f2dfcdff02dbd92"
RECORD_SOURCE_SHORT = "38e0158"
RECORD_SOURCE_TREE = "15c973f51515745dfc8e879609208279b8661fee"
TAG_SOURCE_COMMIT = "421bed8c6e04fa3d2299c6a1d9c99ccfd508122e"
TAG_SOURCE_TREE = "aa0d5d31d879540fd0044052dfeb747f12b64204"
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.1.0",
    "ethos-package-ethos-verify-0.1.0",
    "ethos-package-ethos-pdf-0.1.0",
)
TAG_OBJECTS = (
    "16f260a8f635f3250e2583bd4f7e10cca5dabcb2",
    "bc9876f5682d5f670b6357bd0206a467d76ac850",
    "95613c035a128644998af5c9432729cf0024ed3e",
)
FORBIDDEN_SCOPE_EXPANSION = [
    "public installation approved",
    "public installation is approved",
    "public installation wording is approved",
    "release-ready",
    "release artifact approved",
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


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class MilestoneEPackagePublicationRegistryActionEvidenceTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication registry action evidence validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{RECORD_SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Registry action evidence source commit: `{RECORD_SOURCE_COMMIT}`", record)
        self.assertIn(f"Registry action evidence source tree: `{RECORD_SOURCE_TREE}`", record)
        self.assertIn(f"Accepted package tag source commit: `{TAG_SOURCE_COMMIT}`", record)
        self.assertIn(f"Accepted package tag source tree: `{TAG_SOURCE_TREE}`", record)
        self.assertEqual(RECORD_SOURCE_COMMIT, git("rev-parse", RECORD_SOURCE_SHORT))
        self.assertEqual(RECORD_SOURCE_TREE, git("rev-parse", f"{RECORD_SOURCE_SHORT}^{{tree}}"))
        self.assertEqual(TAG_SOURCE_TREE, git("rev-parse", f"{TAG_SOURCE_COMMIT}^{{tree}}"))

    def test_record_captures_tag_and_first_registry_action_evidence(self) -> None:
        record = normalized(RECORD)

        self.assertIn(APPROVAL_RECORD, record)
        for tag in PACKAGE_TAGS:
            self.assertIn(tag, record)
            self.assertIn(f"{TAG_SOURCE_COMMIT} refs/tags/{tag}^{{}}", record)
        for tag_object in TAG_OBJECTS:
            self.assertIn(tag_object, record)
        self.assertIn("cargo publish --locked -p ethos-doc-core", record)
        self.assertIn("Uploaded ethos-doc-core v0.1.0 to registry `crates-io`", record)
        self.assertIn("Published ethos-doc-core v0.1.0 at registry `crates-io`", record)

    def test_record_captures_dependent_dry_runs_without_authorizing_dependent_actions(self) -> None:
        record = normalized(RECORD)

        self.assertIn("cargo publish --dry-run --locked -p ethos-verify", record)
        self.assertIn("cargo publish --dry-run --locked -p ethos-pdf", record)
        self.assertIn("Downloaded ethos-doc-core v0.1.0", record)
        self.assertIn("Compiling ethos-doc-core v0.1.0", record)
        self.assertIn("warning: aborting upload due to dry run", record)
        self.assertIn("Registry actions for `ethos-verify` and `ethos-pdf` remain blocked", record)
        self.assertIn("Public installation instructions remain blocked", record)
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_action_evidence_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path).lower()

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("registry action evidence", doc, str(path))
            self.assertIn("dependent registry actions remain blocked", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_evidence_after_approval_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        approval_guard = "test_milestone_e_package_publication_registry_action_approval.py"
        evidence_guard = "test_milestone_e_package_publication_registry_action_evidence.py"
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + evidence_guard, text)
            self.assertEqual(1, text.count(prefix + evidence_guard))
            self.assertLess(text.index(prefix + approval_guard), text.index(prefix + evidence_guard))
            self.assertLess(text.index(prefix + evidence_guard), text.index(prefix + readiness_guard))

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
