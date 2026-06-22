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
    "milestone-e-package-publication-dependent-registry-action-evidence-validation-2026-06-22.md"
)
APPROVAL_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-dependent-registry-action-approval-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EVIDENCE_SOURCE_COMMIT = "2a6ba4a8dc3f109acb62f572cce1efa3b37a9590"
EVIDENCE_SOURCE_SHORT = "2a6ba4a"
EVIDENCE_SOURCE_TREE = "d1bc7657709204d70e338c8e97ad3493c326ec5e"
TAG_SOURCE_COMMIT = "421bed8c6e04fa3d2299c6a1d9c99ccfd508122e"
TAG_SOURCE_TREE = "aa0d5d31d879540fd0044052dfeb747f12b64204"
AUTHORIZED_COMMANDS = (
    "cargo publish --locked -p ethos-verify",
    "cargo publish --locked -p ethos-pdf",
)
OBSERVED_RESULTS = (
    "Uploaded ethos-verify v0.1.0 to registry `crates-io`",
    "Published ethos-verify v0.1.0 at registry `crates-io`",
    "Uploaded ethos-pdf v0.1.0 to registry `crates-io`",
    "Published ethos-pdf v0.1.0 at registry `crates-io`",
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


class MilestoneEPackagePublicationDependentRegistryActionEvidenceTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication dependent registry action evidence validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{EVIDENCE_SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Evidence source commit: `{EVIDENCE_SOURCE_COMMIT}`", record)
        self.assertIn(f"Evidence source tree: `{EVIDENCE_SOURCE_TREE}`", record)
        self.assertIn(f"Accepted package tag source commit: `{TAG_SOURCE_COMMIT}`", record)
        self.assertIn(f"Accepted package tag source tree: `{TAG_SOURCE_TREE}`", record)
        self.assertEqual(EVIDENCE_SOURCE_COMMIT, git("rev-parse", EVIDENCE_SOURCE_SHORT))
        self.assertEqual(EVIDENCE_SOURCE_TREE, git("rev-parse", f"{EVIDENCE_SOURCE_SHORT}^{{tree}}"))
        self.assertEqual(TAG_SOURCE_TREE, git("rev-parse", f"{TAG_SOURCE_COMMIT}^{{tree}}"))

    def test_record_captures_completed_dependent_registry_actions(self) -> None:
        record = normalized(RECORD)

        self.assertIn(APPROVAL_RECORD, record)
        self.assertIn("completed dependent registry action evidence", record)
        for command in AUTHORIZED_COMMANDS:
            self.assertIn(command, record)
        for result in OBSERVED_RESULTS:
            self.assertIn(result, record)

    def test_record_keeps_public_installation_wording_and_other_surfaces_blocked(self) -> None:
        record = normalized(RECORD)

        self.assertIn("Public installation wording remains blocked", record)
        self.assertIn("Wheels, npm packages, binaries, hosted surfaces", record)
        self.assertIn("public benchmark reports", record)
        self.assertIn("public benchmark claims", record)
        self.assertIn("project-maintained PDFium builds", record)
        self.assertIn("`ethos-doc`", record)
        self.assertIn("`ethos-rag`", record)
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_dependent_registry_evidence_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path).lower()

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("dependent registry action evidence", doc, str(path))
            self.assertIn("public installation wording remains blocked", doc, str(path))

    def test_make_and_ci_run_evidence_after_approval_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        approval_guard = "test_milestone_e_package_publication_dependent_registry_action_approval.py"
        evidence_guard = "test_milestone_e_package_publication_dependent_registry_action_evidence.py"
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
