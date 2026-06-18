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

from makefile_guard import makefile_text, target_block


class MilestoneCInternalCheckTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-c-internal-checks", text)

    def test_target_composes_current_artifact_gates(self) -> None:
        block = target_block("milestone-c-internal-checks")

        required = [
            "$(MAKE) rag-chunk-alpha PYTHON=$(PYTHON)",
            "$(MAKE) security-report-alpha PYTHON=$(PYTHON)",
            "$(PYTHON) .github/scripts/test_milestone_c_closeout_record.py",
            "$(PYTHON) .github/scripts/test_milestone_c_internal_checks.py",
            "git diff --check",
        ]
        for command in required:
            self.assertIn(command, block)

    def test_target_stays_current_artifact_scoped(self) -> None:
        block = target_block("milestone-c-internal-checks")

        self.assertNotIn("verify-alpha", block)
        self.assertNotIn("layout-evaluator-alpha", block)
        self.assertNotIn("python-surface-test", block)
        self.assertNotIn("verify-rendered-crops", block)
        self.assertNotIn("compare-rendered-crops", block)
        self.assertNotIn("release-", block)
        self.assertNotIn("third-party-license-manifest", block)
        self.assertNotIn("release-notice-draft", block)


if __name__ == "__main__":
    unittest.main()
