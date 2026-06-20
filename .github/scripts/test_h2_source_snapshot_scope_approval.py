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
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
PUBLIC_RELEASE_CHECKLIST = ROOT / "docs/public-release-checklist.md"
RELEASE_NOTICES = ROOT / "docs/release-artifact-notices.md"
RECORD = ROOT / "docs/validation/h2-source-snapshot-scope-approval-2026-06-20.md"
VALIDATION_README = ROOT / "docs/validation/README.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

BOUNDARY_PHRASES = [
    "does not close H2",
    "does not approve public beta",
    "does not approve GitHub release binaries",
    "does not approve wheels",
    "does not approve npm packages",
    "does not approve crate publication",
    "does not approve hosted surfaces",
    "does not approve public benchmark reports",
    "does not approve wording beyond the exact approved pre-alpha sentence",
]

FORBIDDEN_SCOPE_EXPANSION = [
    "h2 closed",
    "public beta approved",
    "github release binaries approved",
    "wheels approved",
    "npm packages approved",
    "crate publication approved",
    "hosted surfaces approved",
    "public benchmark reports approved",
    "first release approved",
    "release artifact approved",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class H2SourceSnapshotScopeApprovalTests(unittest.TestCase):
    def test_source_snapshot_scope_is_recorded_on_current_surfaces(self) -> None:
        for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_NOTICES):
            text = normalized(path)
            self.assertIn("source-snapshot", text, str(path))
            self.assertIn("h2-source-snapshot-scope-approval-2026-06-20.md", text, str(path))

        self.assertIn("source-snapshot", normalized(RECORD))

    def test_record_keeps_h2_open_and_scope_narrow(self) -> None:
        text = normalized(RECORD)

        self.assertIn("Status: **approved artifact scope: source-snapshot only**", text)
        self.assertIn("Ethos remains source-only pre-alpha", text)
        self.assertIn("H2 remains open", text)
        self.assertIn("Validated source HEAD before this record: `cdf5be7`", text)
        self.assertIn("artifact name: `ethos-cli-draft`", text)
        self.assertIn("status: `draft_not_release_ready`", text)
        self.assertIn("workspace packages: `7`", text)
        self.assertIn("third-party registry packages: `93`", text)

    def test_record_captures_exact_manual_approval(self) -> None:
        text = normalized(RECORD)

        self.assertIn(
            "H2 artifact scope approved: source-snapshot only. No binaries, no wheels, no npm "
            "package, no crate publication, no hosted surface, and no public benchmark report.",
            text,
        )

    def test_boundaries_remain_explicit(self) -> None:
        for phrase in BOUNDARY_PHRASES:
            self.assertIn(phrase, normalized(RECORD), phrase)

    def test_current_docs_keep_non_source_snapshot_artifacts_blocked(self) -> None:
        docs = "\n".join(
            normalized(path)
            for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_NOTICES)
        )

        self.assertIn("binaries, wheels, npm packages, crate publication, hosted surfaces", docs)
        self.assertIn("public benchmark reports remain blocked", docs)
        self.assertIn("H2 | Complete public release/package checklist", normalized(EXECUTION_STATUS))

    def test_approval_record_is_indexed_once(self) -> None:
        self.assertEqual(
            1,
            read(VALIDATION_README).count("h2-source-snapshot-scope-approval-2026-06-20.md"),
        )

    def test_make_target_runs_h2_scope_guard_after_h1_guard(self) -> None:
        block = target_block("milestone-e-prep")
        h1_guard = "$(PYTHON) .github/scripts/test_h1_public_safe_comparison_closeout.py"
        h2_guard = "$(PYTHON) .github/scripts/test_h2_source_snapshot_scope_approval.py"
        schema_validation = "$(PYTHON) schemas/validate_examples.py"

        self.assertIn(h2_guard, block)
        self.assertLess(block.index(h1_guard), block.index(h2_guard))
        self.assertLess(block.index(h2_guard), block.index(schema_validation))

    def test_ci_runs_h2_scope_guard_after_h1_guard(self) -> None:
        text = read(CI_WORKFLOW)
        h1_guard = "python3 .github/scripts/test_h1_public_safe_comparison_closeout.py"
        h2_guard = "python3 .github/scripts/test_h2_source_snapshot_scope_approval.py"
        milestone_d = "python3 .github/scripts/test_milestone_d_internal_contracts.py"

        self.assertIn(h2_guard, text)
        self.assertEqual(1, text.count(h2_guard))
        self.assertLess(text.index(h1_guard), text.index(h2_guard))
        self.assertLess(text.index(h2_guard), text.index(milestone_d))

    def test_scope_docs_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            read(path).lower()
            for path in (EXECUTION_STATUS, PUBLIC_RELEASE_CHECKLIST, RELEASE_NOTICES, RECORD)
        )

        for phrase in FORBIDDEN_SCOPE_EXPANSION:
            self.assertNotIn(phrase, text)

    def test_record_avoids_local_private_paths(self) -> None:
        text = read(RECORD)

        self.assertNotIn("/Users/", text)
        self.assertNotIn("/private/tmp", text)
        self.assertNotIn("/private/var", text)
        self.assertNotIn("/var/folders", text)
        self.assertNotIn("saumildiwaker", text)
        self.assertNotIn("Desktop/Stuff", text)
        self.assertNotIn("project/repo/ethos", text)
        self.assertNotIn("docs/.roadmap.md.swp", text)
        self.assertNotIn("web/", text)


if __name__ == "__main__":
    unittest.main()
