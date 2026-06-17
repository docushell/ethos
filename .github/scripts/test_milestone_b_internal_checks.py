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

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"


def makefile_text() -> str:
    return MAKEFILE.read_text(encoding="utf-8")


def target_block(target: str) -> str:
    lines = makefile_text().splitlines()
    start = None
    for index, line in enumerate(lines):
        if line == f"{target}:":
            start = index + 1
            break
    if start is None:
        raise AssertionError(f"{target} target is missing")

    block: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith(("\t", " ")):
            break
        block.append(line)
    return "\n".join(block)


class MilestoneBInternalCheckTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-b-internal-checks", text)

    def test_target_composes_current_internal_gates(self) -> None:
        block = target_block("milestone-b-internal-checks")

        required = [
            "$(PYTHON) fixtures/validate_fixtures.py",
            "$(PYTHON) fixtures/test_validate_fixtures.py",
            "$(PYTHON) schemas/test_font_policy_validation.py",
            "$(PYTHON) schemas/test_security_report_validation.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_b_closeout_record.py",
            "$(PYTHON) .github/scripts/test_milestone_b_exit_checklist.py",
            "$(MAKE) verify-alpha PYTHON=$(PYTHON)",
            "$(MAKE) layout-evaluator-alpha PYTHON=$(PYTHON)",
            "$(MAKE) python-surface-test PYTHON=$(PYTHON)",
            "$(PYTHON) .github/scripts/claims_gate.py",
            "$(PYTHON) .github/scripts/readiness_gate.py public",
            "git diff --check",
        ]
        for command in required:
            self.assertIn(command, block)

    def test_target_stays_internal_only(self) -> None:
        block = target_block("milestone-b-internal-checks")

        self.assertNotIn("release-", block)
        self.assertNotIn("third-party-license-manifest", block)
        self.assertNotIn("release-notice-draft", block)


if __name__ == "__main__":
    unittest.main()
