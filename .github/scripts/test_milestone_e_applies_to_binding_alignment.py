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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

INVENTORY = "docs/milestone-e-fixture-candidates.json"
CRITERIA = "docs/milestone-e-fixture-promotion-criteria.json"
WALKTHROUGH = "docs/milestone-e-internal-trust-loop-walkthrough.json"
PROTOCOL = "docs/milestone-e-internal-trust-loop-use-protocol.json"
MATRIX = "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json"
LEDGER = "docs/milestone-e-internal-trust-loop-blocker-ledger.json"

CURRENT_E_ARTIFACTS = {
    INVENTORY,
    CRITERIA,
    WALKTHROUGH,
    PROTOCOL,
    MATRIX,
    LEDGER,
}

FORBIDDEN_ARTIFACT_WORDING = [
    "public beta is approved",
    "public reports are approved",
    "public result wording approved",
    "release-ready",
    "release artifact approved",
    "package-ready",
    "package publication approved",
    "production-ready",
    "production positioning approved",
    "benchmark-validated",
    "public benchmark pass",
    "speed validated",
    "fastest",
    "launch-ready",
    "hosted surface approved",
    "hosted demo approved",
    "demo-ready",
    "complete demo plan",
    "broad demo approved",
    "performance validated",
    "quality validated",
    "footprint validated",
    "table-quality validated",
    "parser-quality validated",
]


@dataclass(frozen=True)
class AppliesToBindingArtifact:
    artifact: str
    schema: str
    bindings: dict[str, str]


APPLIES_TO_BINDING_ARTIFACTS = (
    AppliesToBindingArtifact(
        CRITERIA,
        "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json",
        {
            "applies_to_inventory": INVENTORY,
        },
    ),
    AppliesToBindingArtifact(
        WALKTHROUGH,
        "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
        {
            "applies_to_inventory": INVENTORY,
            "applies_to_criteria": CRITERIA,
        },
    ),
    AppliesToBindingArtifact(
        PROTOCOL,
        "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
        {
            "applies_to_inventory": INVENTORY,
            "applies_to_criteria": CRITERIA,
            "applies_to_walkthrough": WALKTHROUGH,
        },
    ),
    AppliesToBindingArtifact(
        MATRIX,
        "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
        {
            "applies_to_inventory": INVENTORY,
            "applies_to_criteria": CRITERIA,
            "applies_to_walkthrough": WALKTHROUGH,
            "applies_to_protocol": PROTOCOL,
        },
    ),
    AppliesToBindingArtifact(
        LEDGER,
        "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
        {
            "applies_to_inventory": INVENTORY,
            "applies_to_criteria": CRITERIA,
            "applies_to_walkthrough": WALKTHROUGH,
            "applies_to_protocol": PROTOCOL,
            "applies_to_matrix": MATRIX,
        },
    ),
)


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def applies_to_keys(mapping: dict[str, Any]) -> list[str]:
    return [key for key in mapping if key.startswith("applies_to_")]


class MilestoneEAppliesToBindingAlignmentTests(unittest.TestCase):
    def test_current_e_artifacts_keep_expected_applies_to_bindings(self) -> None:
        for entry in APPLIES_TO_BINDING_ARTIFACTS:
            artifact = load_json(entry.artifact)
            actual = {key: artifact[key] for key in applies_to_keys(artifact)}

            self.assertEqual(entry.bindings, actual, entry.artifact)

    def test_current_e_schemas_require_matching_applies_to_consts(self) -> None:
        for entry in APPLIES_TO_BINDING_ARTIFACTS:
            schema = load_json(entry.schema)
            properties = schema["properties"]
            required = schema["required"]

            self.assertEqual(list(entry.bindings), applies_to_keys(properties), entry.schema)
            self.assertEqual(
                list(entry.bindings),
                [key for key in required if key.startswith("applies_to_")],
                entry.schema,
            )
            for key, expected_value in entry.bindings.items():
                self.assertEqual(expected_value, properties[key]["const"], f"{entry.schema}:{key}")

    def test_applies_to_values_stay_within_current_e_artifact_set(self) -> None:
        for entry in APPLIES_TO_BINDING_ARTIFACTS:
            for key, value in entry.bindings.items():
                self.assertIn(value, CURRENT_E_ARTIFACTS, f"{entry.artifact}:{key}")
                self.assertNotEqual(entry.artifact, value, f"{entry.artifact}:{key}")
                self.assertTrue((ROOT / value).is_file(), f"{entry.artifact}:{key}")

    def test_applies_to_artifact_and_schema_sets_are_explicit(self) -> None:
        discovered_artifacts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "docs").glob("milestone-e-*.json")
            if applies_to_keys(load_json(str(path.relative_to(ROOT))))
        }
        discovered_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
            if applies_to_keys(load_json(str(path.relative_to(ROOT)))["properties"])
        }

        self.assertNotIn("applies_to_inventory", load_json(INVENTORY), INVENTORY)
        self.assertEqual({entry.artifact for entry in APPLIES_TO_BINDING_ARTIFACTS}, discovered_artifacts)
        self.assertEqual({entry.schema for entry in APPLIES_TO_BINDING_ARTIFACTS}, discovered_schemas)

    def test_scope_status_and_roadmap_name_applies_to_binding_alignment(self) -> None:
        for path in (PREP_SCOPE, EXECUTION_STATUS, ROADMAP):
            normalized = " ".join(read(path).split())

            self.assertIn("applies-to binding alignment", normalized, str(path))
            self.assertIn(INVENTORY, normalized, str(path))
            self.assertIn(LEDGER, normalized, str(path))
            self.assertIn("does not resolve or soften blockers", normalized, str(path))

    def test_make_target_runs_applies_to_guard_after_source_status_guard(self) -> None:
        block = target_block("milestone-e-prep")

        source_status_guard = "$(PYTHON) .github/scripts/test_milestone_e_source_status_alignment.py"
        applies_to_guard = "$(PYTHON) .github/scripts/test_milestone_e_applies_to_binding_alignment.py"
        prep_scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(applies_to_guard, block)
        self.assertLess(block.index(source_status_guard), block.index(applies_to_guard))
        self.assertLess(block.index(applies_to_guard), block.index(prep_scope_guard))
        self.assertLess(block.index(applies_to_guard), block.index("git diff --check"))

    def test_ci_runs_applies_to_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        source_status_guard = "python3 .github/scripts/test_milestone_e_source_status_alignment.py"
        applies_to_guard = "python3 .github/scripts/test_milestone_e_applies_to_binding_alignment.py"
        prep_scope_guard = "python3 .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(applies_to_guard, text)
        self.assertEqual(1, text.count(applies_to_guard))
        self.assertLess(text.index(source_status_guard), text.index(applies_to_guard))
        self.assertLess(text.index(applies_to_guard), text.index(prep_scope_guard))

    def test_applies_to_artifacts_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            json.dumps(load_json(entry.artifact), sort_keys=True).lower()
            for entry in APPLIES_TO_BINDING_ARTIFACTS
        )

        for phrase in FORBIDDEN_ARTIFACT_WORDING:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
