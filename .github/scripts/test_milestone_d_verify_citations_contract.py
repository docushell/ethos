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

from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestone-d-verify-citations-contract.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"


def contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def normalized_contract_text() -> str:
    return re.sub(r"\s+", " ", contract_text())


class MilestoneDVerifyCitationsContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-verify-citations-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-verify-citations-contract")

        required = [
            "cargo test --locked -p ethos-cli --test verify",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_verify_citations_contract.py",
            "git diff --check",
        ]
        for command in required:
            self.assertIn(command, block)

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("milestone-d-verify-citations-contract")

        for out_of_scope in [
            "verify-alpha",
            "rag-chunk-alpha",
            "security-report-alpha",
            "verify-rendered-crops",
            "compare-rendered-crops",
            "layout-evaluator-alpha",
            "python-surface-test",
            "release-",
            "third-party-license-manifest",
        ]:
            self.assertNotIn(out_of_scope, block)

    def test_contract_is_linked_from_status_docs(self) -> None:
        for path in [ROADMAP, EXECUTION_STATUS, SCHEMAS_README]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("milestone-d-verify-citations-contract.md", text, path)

    def test_contract_defines_existing_carrier_not_new_surface(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("The current executable carrier remains `ethos verify`", text)
        self.assertIn("does not create a new public command, binding, or hosted surface", text)
        self.assertIn(
            "`verify_citations` names the contract between citation input, grounding source, "
            "verification config, and verification report",
            text,
        )

    def test_contract_pins_v1_supported_and_blocked_scope(self) -> None:
        text = normalized_contract_text()

        for kind in ["`quote`", "`value`", "`presence`", "`table_cell`"]:
            self.assertIn(kind, text)
        self.assertIn("`region` and `other` remain explicit unsupported non-v1 inputs", text)

        for blocker in [
            "a new `verify_citations` CLI alias",
            "Python, Node, MCP, or hosted API surfaces",
            "crop API implementation",
            "sandbox/subprocess backend expansion",
            "semantic or arithmetic verification",
        ]:
            self.assertIn(blocker, text)

    def test_contract_names_fixture_backed_validation(self) -> None:
        text = normalized_contract_text()

        self.assertIn("`schemas/examples/citations.example.json`", text)
        self.assertIn("`schemas/examples/verification-report.example.json`", text)
        self.assertIn("echoes the example claims in input order", text)
        self.assertIn("`all_evidence_grounded` is true only under the invariant", text)
        self.assertIn(
            "`make milestone-d-verify-citations-contract PYTHON=<jsonschema-venv>/bin/python`",
            text,
        )


if __name__ == "__main__":
    unittest.main()
