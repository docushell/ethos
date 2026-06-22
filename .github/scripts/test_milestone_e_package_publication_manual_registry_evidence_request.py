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
    "milestone-e-package-publication-manual-registry-evidence-request-validation-2026-06-22.md"
)
OPERATOR_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-operator-preflight-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "7d9329a0f26e5335e32b6351711e8718729a3a43"
SOURCE_SHORT = "7d9329a"
SOURCE_TREE = "d11dafbe47a75953ff2173be6515a727745b2d05"
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.1.0",
    "ethos-package-ethos-verify-0.1.0",
    "ethos-package-ethos-pdf-0.1.0",
)
OWNER_COMMANDS = (
    "cargo owner --list ethos-doc-core",
    "cargo owner --list ethos-verify",
    "cargo owner --list ethos-pdf",
)
DRY_RUN_COMMANDS = (
    "cargo publish --dry-run --locked -p ethos-doc-core",
    "cargo publish --dry-run --locked -p ethos-verify",
    "cargo publish --dry-run --locked -p ethos-pdf",
)
FORBIDDEN_SCOPE_EXPANSION = [
    "package publication approved",
    "package publication is approved",
    "public installation approved",
    "public installation is approved",
    "public installation wording is approved",
    "package tag creation approved",
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


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        encoding="utf-8",
        stderr=subprocess.DEVNULL,
    ).strip()


class MilestoneEPackagePublicationManualRegistryEvidenceRequestTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication manual registry evidence request validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Manual registry evidence request source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Manual registry evidence request source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_request_lists_exact_manual_outputs_without_tokens(self) -> None:
        record = normalized(RECORD)

        self.assertIn(OPERATOR_RECORD, record)
        self.assertIn("Manual Evidence Output Packet", record)
        self.assertIn("Do not paste tokens, passwords, or secret registry credentials", record)
        self.assertIn("crates.io account name or owner identity", record)
        self.assertIn("reserved name owner outputs", record)
        self.assertIn("first dry-run output for `ethos-doc-core`", record)
        self.assertIn("dependent dry-run outputs after `ethos-doc-core` is visible", record)
        for command in OWNER_COMMANDS:
            self.assertIn(command, record)
        for command in DRY_RUN_COMMANDS:
            self.assertIn(command, record)

    def test_registry_actions_and_public_installation_remain_blocked(self) -> None:
        record = normalized(RECORD)

        self.assertIn("No package tag is created by this record", record)
        self.assertIn("`cargo publish` remains blocked", record)
        self.assertIn("Public installation instructions remain blocked", record)
        self.assertIn("Manual registry evidence remains required", record)
        for tag in PACKAGE_TAGS:
            self.assertIn(tag, record)
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_manual_registry_request_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path).lower()

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("manual registry evidence request", doc, str(path))
            self.assertIn("manual registry evidence remains required", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_request_after_operator_preflight_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        operator_guard = "test_milestone_e_package_publication_operator_preflight.py"
        request_guard = "test_milestone_e_package_publication_manual_registry_evidence_request.py"
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + request_guard, text)
            self.assertEqual(1, text.count(prefix + request_guard))
            self.assertLess(text.index(prefix + operator_guard), text.index(prefix + request_guard))
            self.assertLess(text.index(prefix + request_guard), text.index(prefix + readiness_guard))

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
