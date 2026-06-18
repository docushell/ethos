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

import ast
import json
import unittest
from pathlib import Path

from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
ROADMAP = ROOT / "docs/roadmap.md"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
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
        "contract": "claim_kind_boundary.v1",
        "carrier": "ethos verify",
        "target": "milestone-d-claim-kind-boundary-contract",
        "doc": "docs/milestone-d-claim-kind-boundary-contract.md",
        "inventory": "examples/verify/claim_kind_boundary_v1_contract.json",
        "schema": "schemas/ethos-claim-kind-boundary-contract.schema.json",
    },
    {
        "contract": "grounding_source.v1",
        "carrier": "GroundingSource trait",
        "target": "milestone-d-grounding-source-contract",
        "doc": "docs/milestone-d-grounding-source-contract.md",
        "inventory": "examples/verify/grounding_source_v1_contract.json",
        "schema": "schemas/ethos-grounding-source-contract.schema.json",
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
        "contract": "crop_element_surface_shape.v1",
        "carrier": "source-only crop_element surface shape",
        "target": "milestone-d-crop-element-surface-shape-contract",
        "doc": "docs/milestone-d-crop-element-surface-shape-contract.md",
        "inventory": "examples/crop/crop_element_surface_shape_v1_contract.json",
        "schema": "schemas/ethos-crop-element-surface-shape-contract.schema.json",
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


def registered_paths(key: str) -> list[str]:
    return sorted(entry[key] for entry in CONTRACT_REGISTRY)


def discovered_d_contract_docs() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "docs").glob("milestone-d-*-contract.md")
    )


def discovered_d_contract_schemas() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "schemas").glob("ethos-*-contract.schema.json")
    )


def discovered_d_contract_inventories() -> list[str]:
    roots = [
        ROOT / "examples" / "verify",
        ROOT / "examples" / "crop",
        ROOT / "examples" / "sandbox",
    ]
    return sorted(
        str(path.relative_to(ROOT))
        for root in roots
        for path in root.glob("*_v1_contract.json")
    )


def path_expr_to_repo_path(node: ast.AST) -> str:
    roots = {
        "ROOT": "",
        "SCHEMAS": "schemas",
        "EXAMPLES": "schemas/examples",
    }
    if isinstance(node, ast.Name) and node.id in roots:
        return roots[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = path_expr_to_repo_path(node.left)
        right = path_expr_to_repo_path(node.right)
        return f"{left}/{right}" if left else right
    raise AssertionError(f"unsupported validate_examples path expression: {ast.dump(node)}")


def schema_example_validation_pairs() -> set[tuple[str, str]]:
    tree = ast.parse(VALIDATE_EXAMPLES.read_text(encoding="utf-8"))
    pairs_node = next(
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "PAIRS" for target in node.targets)
    )

    pairs = set()
    for pair_node in pairs_node.elts:
        schema_node, example_nodes = pair_node.elts
        schema_path = f"schemas/{schema_node.value}"
        for example_node in example_nodes.elts:
            pairs.add((schema_path, path_expr_to_repo_path(example_node)))
    return pairs


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

    def test_contract_registry_covers_current_d_artifacts(self) -> None:
        self.assertEqual(registered_paths("doc"), discovered_d_contract_docs())
        self.assertEqual(registered_paths("schema"), discovered_d_contract_schemas())
        self.assertEqual(registered_paths("inventory"), discovered_d_contract_inventories())

    def test_registered_contract_inventories_are_schema_validated(self) -> None:
        registered_pairs = {
            (entry["schema"], entry["inventory"])
            for entry in CONTRACT_REGISTRY
        }
        registered_schemas = {entry["schema"] for entry in CONTRACT_REGISTRY}
        validated_contract_pairs = {
            pair
            for pair in schema_example_validation_pairs()
            if pair[0] in registered_schemas
        }

        self.assertEqual(registered_pairs, validated_contract_pairs)

    def test_registry_references_are_consistent(self) -> None:
        for entry in CONTRACT_REGISTRY:
            doc = (ROOT / entry["doc"]).read_text(encoding="utf-8")
            self.assertIn(Path(entry["inventory"]).name, doc, entry["contract"])
            self.assertIn(entry["target"], doc, entry["contract"])

    def test_registered_contracts_are_documented_in_status_surfaces(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")
        execution_status = EXECUTION_STATUS.read_text(encoding="utf-8")
        schemas_readme = SCHEMAS_README.read_text(encoding="utf-8")

        for entry in CONTRACT_REGISTRY:
            self.assertIn(Path(entry["doc"]).name, roadmap, entry["contract"])
            self.assertIn(entry["doc"], execution_status, entry["contract"])
            self.assertIn(entry["doc"], schemas_readme, entry["contract"])
            self.assertIn(Path(entry["schema"]).name, schemas_readme, entry["contract"])
            self.assertIn(entry["inventory"], schemas_readme, entry["contract"])

    def test_contract_docs_keep_common_public_language_boundary(self) -> None:
        required_text = [
            "Status: source-only pre-alpha contract work for internal Milestone D continuation.",
            "## Explicit Blockers For This Slice",
            "language remains limited to source-only pre-alpha internal continuation",
            "evidence grounding",
            "diagnostics",
            "fixture-backed validation",
            "explicit blockers",
        ]

        for entry in CONTRACT_REGISTRY:
            doc = (ROOT / entry["doc"]).read_text(encoding="utf-8")
            normalized_doc = " ".join(doc.split())
            for text in required_text:
                self.assertIn(" ".join(text.split()), normalized_doc, entry["contract"])

    def test_contract_inventories_keep_explicit_blockers_nonempty(self) -> None:
        for entry in CONTRACT_REGISTRY:
            blockers = load_json(entry["inventory"])["explicit_blockers"]

            self.assertGreater(len(blockers), 0, entry["contract"])
            self.assertEqual(len(blockers), len(set(blockers)), entry["contract"])
            for blocker in blockers:
                self.assertEqual(blocker.strip(), blocker, entry["contract"])
                self.assertNotEqual("", blocker, entry["contract"])

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
