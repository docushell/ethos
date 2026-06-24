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
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/evidence-anchor-v1-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/verify/evidence_anchor_v1_contract.json"
CONTRACT_SCHEMA = ROOT / "schemas/ethos-evidence-anchor-contract.schema.json"
REQUEST_SCHEMA = ROOT / "schemas/ethos-evidence-anchor-request.schema.json"
REPORT_SCHEMA = ROOT / "schemas/ethos-evidence-anchor-report.schema.json"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
README = ROOT / "README.md"
EVIDENCE_TYPES = ROOT / "crates/ethos-core/src/evidence_anchor.rs"
CLI_TESTS = ROOT / "crates/ethos-cli/tests/evidence_anchor.rs"

EXPECTED_TARGET_COMMANDS = [
    "cargo test --locked -p ethos-cli --test evidence_anchor",
    "cargo test --locked -p ethos-grounding-opendataloader-json",
    "$(PYTHON) schemas/validate_examples.py",
    "$(PYTHON) .github/scripts/test_execution_status.py",
    "$(PYTHON) .github/scripts/test_roadmap_status.py",
    "$(PYTHON) .github/scripts/test_evidence_anchor_v1_contract.py",
    "git diff --check",
]
EXPECTED_ANCHOR_STATUSES = [
    "bound",
    "mismatch",
    "not_found",
    "stale_fingerprint",
    "capability_limited",
    "unsupported_evidence_kind",
]
EXPECTED_BLOCKERS = [
    "semantic answer verification",
    "multi-source joins",
    "crop rendering or source-region image generation",
    "hosted API or service surfaces",
    "DocuShell-specific behavior",
    "production positioning",
    "benchmark, speed, footprint, parser-quality, or table-quality claims",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(schema: dict, instance: dict) -> list:
    return sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )


def rust_test_names(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"(?m)^\s*fn ([a-z][a-z0-9_]*)\(", text))


def snake_case(name: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r"_\1", name).lower()


def anchor_status_variants() -> list[str]:
    text = EVIDENCE_TYPES.read_text(encoding="utf-8")
    match = re.search(r"pub enum AnchorStatus \{(?P<body>.*?)\n\}", text, re.DOTALL)
    if match is None:
        raise AssertionError("missing AnchorStatus enum")
    variants = re.findall(r"(?m)^\s*([A-Z][A-Za-z0-9]*)\b", match.group("body"))
    return [snake_case(variant) for variant in variants]


def contract_explicit_blockers() -> list[str]:
    lines = CONTRACT.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("## Explicit Blockers For This Slice") + 1
    except ValueError as exc:
        raise AssertionError("missing explicit blockers section") from exc

    blockers: list[str] = []
    for line in lines[start:]:
        if line.startswith("- "):
            blockers.append(line.removeprefix("- ").rstrip(";."))
        elif blockers and line.strip():
            break
    return blockers


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


class EvidenceAnchorV1ContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("evidence-anchor-v1-contract", text)

    def test_target_composes_guard_commands(self) -> None:
        commands = [line.strip() for line in target_block("evidence-anchor-v1-contract").splitlines() if line.strip()]

        self.assertEqual(EXPECTED_TARGET_COMMANDS, commands)

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("evidence-anchor-v1-contract")

        for out_of_scope in [
            "release-candidate-prep",
            "milestone-e-prep",
            "release-hygiene",
            "npm",
            "pypi",
            "cargo publish",
            "gh release",
            "verify-rendered-crops",
            "compare-rendered-crops",
        ]:
            self.assertNotIn(out_of_scope, block)

    def test_contract_inventory_schema_validates_inventory(self) -> None:
        schema = load_json(CONTRACT_SCHEMA)
        inventory = load_json(CONTRACT_INVENTORY)

        Draft202012Validator.check_schema(schema)
        self.assertEqual([], schema_errors(schema, inventory))

    def test_contract_inventory_binds_existing_files_and_tests(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "evidence_anchor.v1")
        self.assertEqual(inventory["status"], "source-only-public-beta-evaluation")
        self.assertEqual(inventory["carrier"], "ethos evidence anchor")
        for key in ["request_schema", "report_schema"]:
            self.assertTrue((ROOT / inventory[key]).is_file(), key)
        for path in inventory["implementation"]:
            self.assertTrue((ROOT / path).is_file(), path)
        self.assertLessEqual(set(inventory["cli_tests"]), rust_test_names(CLI_TESTS))

    def test_schema_registry_validates_contract_inventory(self) -> None:
        pair = (
            "schemas/ethos-evidence-anchor-contract.schema.json",
            "examples/verify/evidence_anchor_v1_contract.json",
        )

        self.assertIn(pair, schema_example_validation_pairs())

    def test_schema_readme_registers_contract_inventory(self) -> None:
        text = SCHEMAS_README.read_text(encoding="utf-8")

        self.assertIn("`ethos-evidence-anchor-contract.schema.json`", text)
        self.assertIn("`docs/evidence-anchor-v1-contract.md`", text)
        self.assertIn("`examples/verify/evidence_anchor_v1_contract.json`", text)

    def test_status_docs_link_contract_without_expanding_posture(self) -> None:
        for path in [ROADMAP, EXECUTION_STATUS]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("evidence-anchor-v1-contract.md", text, path)
            self.assertIn("make evidence-anchor-v1-contract", text, path)

        readme = README.read_text(encoding="utf-8")
        self.assertIn("Status: public beta evaluation.", readme)
        self.assertNotIn("production-ready", readme.lower())

    def test_anchor_statuses_match_inventory(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(EXPECTED_ANCHOR_STATUSES, inventory["supported_anchor_statuses"])
        self.assertEqual(EXPECTED_ANCHOR_STATUSES, anchor_status_variants())

    def test_contract_records_current_boundaries(self) -> None:
        text = re.sub(r"\s+", " ", CONTRACT.read_text(encoding="utf-8"))
        inventory = load_json(CONTRACT_INVENTORY)

        for required in [
            "`ethos.evidence_anchor_request.v1`",
            "`ethos.evidence_anchor_report.v1`",
            "native Ethos JSON and OpenDataLoader-style JSON",
            "non-bound per-ref outcomes remain report data and exit `0`",
            "usage errors remain exit `2`",
            "mismatch takes precedence over capability-limited",
        ]:
            self.assertIn(required, text)
        self.assertEqual(EXPECTED_BLOCKERS, contract_explicit_blockers())
        self.assertEqual(EXPECTED_BLOCKERS, inventory["explicit_blockers"])

    def test_request_and_report_schemas_are_strict_objects(self) -> None:
        for path in [REQUEST_SCHEMA, REPORT_SCHEMA, CONTRACT_SCHEMA]:
            schema = load_json(path)
            self.assertEqual(False, schema.get("additionalProperties"))


if __name__ == "__main__":
    unittest.main()
