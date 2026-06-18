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

import json
import unittest
from pathlib import Path

from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CONTRACT_REGISTRY = [
    {
        "contract": "verify_citations.v1",
        "carrier": "ethos verify",
        "target": "milestone-d-verify-citations-contract",
        "doc": "docs/milestone-d-verify-citations-contract.md",
        "inventory": "examples/verify/verify_citations_v1_contract.json",
        "schema": "schemas/ethos-verify-citations-contract.schema.json",
    },
    {
        "contract": "opendataloader_adapter_shape.v1",
        "carrier": "opendataloader-json adapter",
        "target": "milestone-d-opendataloader-adapter-shape-contract",
        "doc": "docs/milestone-d-opendataloader-adapter-shape-contract.md",
        "inventory": "examples/verify/opendataloader_adapter_shape_v1_contract.json",
        "schema": "schemas/ethos-opendataloader-adapter-shape-contract.schema.json",
    },
    {
        "contract": "capability_downgrade.v1",
        "carrier": "ethos verify",
        "target": "milestone-d-capability-downgrade-contract",
        "doc": "docs/milestone-d-capability-downgrade-contract.md",
        "inventory": "examples/verify/capability_downgrade_v1_contract.json",
        "schema": "schemas/ethos-capability-downgrade-contract.schema.json",
    },
    {
        "contract": "crop_element.v1",
        "carrier": "ethos verify --crop-dir",
        "target": "milestone-d-crop-element-contract",
        "doc": "docs/milestone-d-crop-element-contract.md",
        "inventory": "examples/crop/crop_element_v1_contract.json",
        "schema": "schemas/ethos-crop-element-contract.schema.json",
    },
    {
        "contract": "sandbox_subprocess.v1",
        "carrier": "pdfium worker process",
        "target": "milestone-d-sandbox-subprocess-contract",
        "doc": "docs/milestone-d-sandbox-subprocess-contract.md",
        "inventory": "examples/sandbox/sandbox_subprocess_v1_contract.json",
        "schema": "schemas/ethos-sandbox-subprocess-contract.schema.json",
    },
]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def registered_targets() -> list[str]:
    return [entry["target"] for entry in CONTRACT_REGISTRY]


class MilestoneDInternalContractsTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-internal-contracts", text)

    def test_target_composes_current_d_contract_targets(self) -> None:
        block = target_block("milestone-d-internal-contracts")

        for target in registered_targets():
            self.assertIn(f"$(MAKE) {target} PYTHON=$(PYTHON)", block)
        self.assertIn("$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py", block)
        self.assertIn("git diff --check", block)

    def test_target_commands_match_registered_contracts(self) -> None:
        block = target_block("milestone-d-internal-contracts")
        commands = [line.strip() for line in block.splitlines() if line.strip()]

        self.assertEqual(
            [f"$(MAKE) {target} PYTHON=$(PYTHON)" for target in registered_targets()]
            + [
                "$(PYTHON) .github/scripts/test_milestone_d_internal_contracts.py",
                "git diff --check",
            ],
            commands,
        )

    def test_contract_registry_matches_current_d_inventories(self) -> None:
        contracts = [entry["contract"] for entry in CONTRACT_REGISTRY]
        targets = registered_targets()

        self.assertEqual(len(contracts), len(set(contracts)))
        self.assertEqual(len(targets), len(set(targets)))

        for entry in CONTRACT_REGISTRY:
            inventory = load_json(entry["inventory"])
            self.assertEqual(entry["contract"], inventory["contract"])
            self.assertEqual("source-only-pre-alpha", inventory["status"])
            self.assertEqual(entry["carrier"], inventory["carrier"])
            self.assertTrue((ROOT / entry["schema"]).is_file(), entry["contract"])

    def test_registry_references_are_consistent(self) -> None:
        for entry in CONTRACT_REGISTRY:
            doc = (ROOT / entry["doc"]).read_text(encoding="utf-8")
            self.assertIn(Path(entry["inventory"]).name, doc, entry["contract"])
            self.assertIn(entry["target"], doc, entry["contract"])

    def test_execution_status_names_registry_guard(self) -> None:
        text = EXECUTION_STATUS.read_text(encoding="utf-8")

        self.assertIn("make milestone-d-internal-contracts", text)
        self.assertIn("command wiring and contract registry", text)

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
