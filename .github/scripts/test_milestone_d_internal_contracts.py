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


CONTRACT_TARGETS = [
    "milestone-d-verify-citations-contract",
    "milestone-d-crop-element-contract",
    "milestone-d-sandbox-subprocess-contract",
]


class MilestoneDInternalContractsTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-internal-contracts", text)

    def test_target_composes_current_d_contract_targets(self) -> None:
        block = target_block("milestone-d-internal-contracts")

        for target in CONTRACT_TARGETS:
            self.assertIn(f"$(MAKE) {target} PYTHON=$(PYTHON)", block)
        self.assertIn("$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py", block)
        self.assertIn("git diff --check", block)

    def test_target_stays_internal_contract_scoped(self) -> None:
        block = target_block("milestone-d-internal-contracts")

        for out_of_scope in [
            "verify-alpha",
            "rag-chunk-alpha",
            "security-report-alpha",
            "verify-rendered-crops",
            "compare-rendered-crops",
            "layout-evaluator-alpha",
            "python-surface-test",
            "milestone-b-internal-checks",
            "milestone-c-internal-checks",
            "release-",
            "third-party-license-manifest",
            "npm",
            "mcp",
        ]:
            self.assertNotIn(out_of_scope, block)


if __name__ == "__main__":
    unittest.main()
