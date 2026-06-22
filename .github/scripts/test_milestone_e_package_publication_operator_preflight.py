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
    "milestone-e-package-publication-operator-preflight-validation-2026-06-22.md"
)
BINDING_RECORD = (
    "docs/validation/"
    "milestone-e-package-publication-tag-binding-refresh-validation-2026-06-22.md"
)
VALIDATION_README = ROOT / "docs/validation/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

SOURCE_COMMIT = "421bed8c6e04fa3d2299c6a1d9c99ccfd508122e"
SOURCE_SHORT = "421bed8"
SOURCE_TREE = "aa0d5d31d879540fd0044052dfeb747f12b64204"
PACKAGE_TAGS = (
    "ethos-package-ethos-doc-core-0.1.0",
    "ethos-package-ethos-verify-0.1.0",
    "ethos-package-ethos-pdf-0.1.0",
)
PUBLISH_COMMANDS = (
    "cargo publish --locked -p ethos-doc-core",
    "cargo publish --locked -p ethos-verify",
    "cargo publish --locked -p ethos-pdf",
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


class MilestoneEPackagePublicationOperatorPreflightTests(unittest.TestCase):
    def test_record_is_indexed_and_source_bound(self) -> None:
        readme = normalized(VALIDATION_README)
        record = normalized(RECORD)

        self.assertIn(RECORD.name, readme)
        self.assertIn("package publication operator preflight validation", readme)
        self.assertIn(f"Validated source HEAD before this record: `{SOURCE_SHORT}`", read(RECORD))
        self.assertIn(f"Operator preflight source commit: `{SOURCE_COMMIT}`", record)
        self.assertIn(f"Operator preflight source tree: `{SOURCE_TREE}`", record)
        self.assertEqual(SOURCE_COMMIT, git("rev-parse", SOURCE_SHORT))
        self.assertEqual(SOURCE_TREE, git("rev-parse", f"{SOURCE_SHORT}^{{tree}}"))

    def test_preflight_lists_exact_manual_evidence_and_commands(self) -> None:
        record = normalized(RECORD)

        self.assertIn(BINDING_RECORD, record)
        self.assertIn("crates.io owner/account confirmation remains manual evidence", record)
        self.assertIn("reserved name ownership for `ethos-doc-core`, `ethos-verify`, and `ethos-pdf`", record)
        self.assertIn("dependency order: `ethos-doc-core`, then `ethos-verify`, then `ethos-pdf`", record)
        for command in PUBLISH_COMMANDS:
            self.assertIn(command, record)
        self.assertIn("No command in this record has been executed against crates.io", record)

    def test_registry_actions_and_public_installation_remain_blocked(self) -> None:
        record = normalized(RECORD)

        self.assertIn("No package tag is created by this record", record)
        self.assertIn("`cargo publish` remains blocked", record)
        self.assertIn("Public installation instructions remain blocked", record)
        self.assertIn("wheels, npm packages, binaries, hosted surfaces", record)
        for tag in PACKAGE_TAGS:
            self.assertIn(tag, record)
            self.assertEqual("", git("tag", "--list", tag), tag)
        self.assertFalse((ROOT / ".cargo/config.toml").exists())
        self.assertFalse((ROOT / "target/package-registry").exists())

    def test_docs_reference_operator_preflight_and_retained_blockers(self) -> None:
        for path in (PREP_SCOPE, ROADMAP, EXECUTION_STATUS, VALIDATION_README):
            doc = normalized(path).lower()

            self.assertIn(RECORD.name, doc, str(path))
            self.assertIn("operator preflight", doc, str(path))
            self.assertIn("manual registry evidence remains required", doc, str(path))
            self.assertIn("public installation remains blocked", doc, str(path))

    def test_make_and_ci_run_operator_preflight_after_binding_before_readiness(self) -> None:
        make_block = target_block("milestone-e-prep")
        ci = read(CI_WORKFLOW)
        binding_guard = "test_milestone_e_package_publication_tag_binding_refresh.py"
        operator_guard = "test_milestone_e_package_publication_operator_preflight.py"
        readiness_guard = "test_milestone_e_public_facing_readiness_ledger.py"

        for text, prefix in ((make_block, "$(PYTHON) .github/scripts/"), (ci, "python3 .github/scripts/")):
            self.assertIn(prefix + operator_guard, text)
            self.assertEqual(1, text.count(prefix + operator_guard))
            self.assertLess(text.index(prefix + binding_guard), text.index(prefix + operator_guard))
            self.assertLess(text.index(prefix + operator_guard), text.index(prefix + readiness_guard))

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
