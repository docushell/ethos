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
TEMPLATE = ROOT / "docs/validation/first-public-release-launch-copy-audit-template-2026-06-22.md"
VALIDATION_README = ROOT / "docs/validation/README.md"

RETAINED_BLOCKERS = (
    "Hosted surfaces remain blocked",
    "Production positioning remains blocked",
    "Public benchmark reports remain blocked",
    "Public benchmark claims remain blocked",
    "Windows x64 packaged artifacts remain blocked",
    "Bundled project-maintained PDFium builds remain blocked",
    "`ethos-doc` remains blocked",
    "`ethos-rag` remains blocked",
)
FORBIDDEN_APPROVALS = (
    "hosted surfaces approved",
    "production positioning approved",
    "public benchmark claims approved",
    "public benchmark reports approved",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class LaunchCopyApprovalScaffoldTests(unittest.TestCase):
    def test_template_is_explicitly_not_approval(self) -> None:
        text = normalized(TEMPLATE)
        lower = text.lower()

        self.assertIn("template only; no launch copy approved", text)
        self.assertIn("does not approve launch wording", text)
        self.assertIn("final approval record", text)
        for phrase in FORBIDDEN_APPROVALS:
            self.assertNotIn(phrase, lower)

    def test_template_requires_sentence_level_claim_audit_and_blockers(self) -> None:
        text = normalized(TEMPLATE)

        self.assertIn("Every sentence in candidate launch copy must be reviewed", text)
        self.assertIn("Sentence Audit Table", text)
        self.assertIn("approved/blocked/revise", text)
        for blocker in RETAINED_BLOCKERS:
            self.assertIn(blocker, text)

    def test_release_candidate_target_runs_launch_copy_guard(self) -> None:
        block = target_block("release-candidate-prep")

        self.assertIn("$(PYTHON) .github/scripts/test_launch_copy_approval_scaffold.py", block)

    def test_validation_readme_indexes_template(self) -> None:
        text = normalized(VALIDATION_README)

        self.assertIn(TEMPLATE.name, text)
        self.assertIn("launch copy audit template", text)
        self.assertIn("no launch wording is approved", text)


if __name__ == "__main__":
    unittest.main()
