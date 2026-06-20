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
import subprocess
import unittest
from dataclasses import dataclass
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
SCHEMAS_README = ROOT / "schemas/README.md"
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


@dataclass(frozen=True)
class RegistryEntry:
    schema: str
    artifact: str
    scope: str

    @property
    def schema_name(self) -> str:
        return Path(self.schema).name


EXPECTED_REGISTRY = (
    RegistryEntry(
        "schemas/ethos-milestone-e-fixture-candidates.schema.json",
        "docs/milestone-e-fixture-candidates.json",
        "internal_fixture_candidate_inventory",
    ),
    RegistryEntry(
        "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json",
        "docs/milestone-e-fixture-promotion-criteria.json",
        "internal_fixture_promotion_criteria",
    ),
    RegistryEntry(
        "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
        "docs/milestone-e-internal-trust-loop-walkthrough.json",
        "internal_trust_loop_walkthrough_plan",
    ),
    RegistryEntry(
        "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
        "docs/milestone-e-internal-trust-loop-use-protocol.json",
        "internal_trust_loop_use_protocol",
    ),
    RegistryEntry(
        "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
        "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
        "internal_trust_loop_rehearsal_evidence_matrix",
    ),
    RegistryEntry(
        "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
        "docs/milestone-e-internal-trust-loop-blocker-ledger.json",
        "internal_trust_loop_blocker_ledger",
    ),
    RegistryEntry(
        "schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json",
        "docs/milestone-e-public-approval-lane-blockers.json",
        "public_approval_lane_blocker_ledger",
    ),
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def path_parts(node: ast.AST) -> list[str]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return path_parts(node.left) + path_parts(node.right)
    if isinstance(node, ast.Name):
        if node.id == "ROOT":
            return []
        if node.id == "EXAMPLES":
            return ["schemas", "examples"]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    raise AssertionError(f"unsupported path expression in validate_examples.py: {ast.dump(node)}")


def extract_validate_examples_pairs() -> list[tuple[str, str]]:
    tree = ast.parse(read(VALIDATE_EXAMPLES))
    pairs_node = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "PAIRS" for target in node.targets):
            pairs_node = node.value
            break

    if not isinstance(pairs_node, ast.List):
        raise AssertionError("PAIRS list not found in schemas/validate_examples.py")

    pairs: list[tuple[str, str]] = []
    for pair in pairs_node.elts:
        if not isinstance(pair, ast.Tuple) or len(pair.elts) != 2:
            raise AssertionError(f"unexpected PAIRS entry: {ast.dump(pair)}")
        schema_node, examples_node = pair.elts
        if not isinstance(schema_node, ast.Constant) or not isinstance(schema_node.value, str):
            raise AssertionError(f"unexpected schema expression: {ast.dump(schema_node)}")
        if not isinstance(examples_node, ast.List):
            raise AssertionError(f"unexpected example-list expression: {ast.dump(examples_node)}")
        for example in examples_node.elts:
            pairs.append((schema_node.value, "/".join(path_parts(example))))
    return pairs


class MilestoneESchemaRegistryAlignmentTests(unittest.TestCase):
    def assert_tracked_file(self, path: str) -> None:
        self.assertTrue((ROOT / path).is_file(), path)
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, path)

    def test_registry_has_exact_tracked_schema_artifact_pairs(self) -> None:
        self.assertEqual(7, len(EXPECTED_REGISTRY))
        self.assertEqual(
            len(EXPECTED_REGISTRY),
            len({(entry.schema, entry.artifact) for entry in EXPECTED_REGISTRY}),
        )

        for entry in EXPECTED_REGISTRY:
            self.assert_tracked_file(entry.schema)
            self.assert_tracked_file(entry.artifact)

        discovered_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
        }
        discovered_artifacts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "docs").glob("milestone-e-*.json")
        }
        self.assertEqual({entry.schema for entry in EXPECTED_REGISTRY}, discovered_schemas)
        self.assertEqual({entry.artifact for entry in EXPECTED_REGISTRY}, discovered_artifacts)

    def test_validate_examples_has_exact_e_registry_pairs(self) -> None:
        pairs = extract_validate_examples_pairs()
        expected = {(entry.schema_name, entry.artifact) for entry in EXPECTED_REGISTRY}
        actual = {
            (schema_name, example)
            for schema_name, example in pairs
            if schema_name.startswith("ethos-milestone-e-")
        }

        self.assertEqual(expected, actual)
        self.assertEqual(len(EXPECTED_REGISTRY), len(actual))
        self.assertEqual(
            len(EXPECTED_REGISTRY),
            len({schema_name for schema_name, _ in actual}),
        )
        self.assertEqual(
            len(EXPECTED_REGISTRY),
            len({example for _, example in actual}),
        )

    def test_schemas_readme_lists_registry_once(self) -> None:
        text = read(SCHEMAS_README)
        schema_names = re.findall(r"`(ethos-milestone-e-[^`]+\.schema\.json)`", text)
        artifact_paths = re.findall(r"`(docs/milestone-e-[^`]+\.json)`", text)

        self.assertEqual({entry.schema_name for entry in EXPECTED_REGISTRY}, set(schema_names))
        self.assertEqual(len(EXPECTED_REGISTRY), len(schema_names))
        self.assertEqual({entry.artifact for entry in EXPECTED_REGISTRY}, set(artifact_paths))
        self.assertEqual(len(EXPECTED_REGISTRY), len(artifact_paths))

    def test_scope_roadmap_and_status_reference_registry(self) -> None:
        prep_scope = read(PREP_SCOPE)
        roadmap = read(ROADMAP)
        status = read(EXECUTION_STATUS)

        self.assertIn("schema-registry alignment", prep_scope)
        self.assertIn("schemas/validate_examples.py", status)
        for entry in EXPECTED_REGISTRY:
            self.assertIn(entry.schema, prep_scope)
            self.assertIn(entry.artifact, prep_scope)
            self.assertIn(entry.schema, roadmap)
            self.assertIn(entry.artifact, roadmap)
            self.assertIn(entry.artifact, status)

    def test_registry_schema_constants_match_artifacts(self) -> None:
        for entry in EXPECTED_REGISTRY:
            schema = json.loads((ROOT / entry.schema).read_text(encoding="utf-8"))
            artifact = json.loads((ROOT / entry.artifact).read_text(encoding="utf-8"))

            self.assertEqual(False, schema["additionalProperties"], entry.schema)
            self.assertEqual(1, artifact["schema_version"], entry.artifact)
            self.assertEqual(
                schema["properties"]["schema_version"]["const"],
                artifact["schema_version"],
                entry.artifact,
            )
            self.assertEqual(
                schema["properties"]["status"]["const"],
                artifact["status"],
                entry.artifact,
            )
            self.assertEqual(
                schema["properties"]["scope"]["const"],
                artifact["scope"],
                entry.artifact,
            )
            self.assertEqual(entry.scope, artifact["scope"], entry.artifact)

    def test_make_target_runs_registry_guard_before_scope_guard(self) -> None:
        block = target_block("milestone-e-prep")

        schema_validation = "$(PYTHON) schemas/validate_examples.py"
        registry_guard = "$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment.py"
        prep_scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(schema_validation, block)
        self.assertIn(registry_guard, block)
        self.assertIn(prep_scope_guard, block)
        self.assertLess(block.index(schema_validation), block.index(registry_guard))
        self.assertLess(block.index(registry_guard), block.index(prep_scope_guard))
        self.assertLess(block.index(registry_guard), block.index("git diff --check"))

    def test_ci_runs_registry_guard_once_before_scope_guard(self) -> None:
        text = read(CI_WORKFLOW)

        registry_guard = "python3 .github/scripts/test_milestone_e_schema_registry_alignment.py"
        prep_scope_guard = "python3 .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(registry_guard, text)
        self.assertEqual(1, text.count(registry_guard))
        self.assertLess(text.index(registry_guard), text.index(prep_scope_guard))


if __name__ == "__main__":
    unittest.main()
