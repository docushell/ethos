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

CRITERIA = "docs/milestone-e-fixture-promotion-criteria.json"
WALKTHROUGH = "docs/milestone-e-internal-trust-loop-walkthrough.json"
PROTOCOL = "docs/milestone-e-internal-trust-loop-use-protocol.json"
MATRIX = "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json"
LEDGER = "docs/milestone-e-internal-trust-loop-blocker-ledger.json"

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
class RequiredBeforeArtifact:
    artifact: str
    schema: str
    key: str
    schema_def: str
    requirements: tuple[str, ...]


COMMON_INTERNAL_USE_REQUIREMENTS = (
    "validation command is rerun in the source checkout",
    "input fixtures remain tracked and path-backed",
    "expected diagnostic boundary remains explicit",
    "blocker status remains explicit",
    "make milestone-e-prep remains green",
    "public-surface posture and claims gates remain green",
)

REQUIRED_BEFORE_ARTIFACTS = (
    RequiredBeforeArtifact(
        CRITERIA,
        "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json",
        "global_required_before_internal_demo_plan",
        "global_requirement",
        (
            "candidate remains listed in docs/milestone-e-fixture-candidates.json",
            "validated command is rerun in the source checkout",
            "input fixtures remain tracked and path-backed",
            "expected diagnostic boundary remains explicit",
            "blocker status remains explicit",
            "make milestone-e-prep remains green",
            "public-surface posture and claims gates remain green",
            "criteria changes require a validation record or explicit superseding record",
        ),
    ),
    RequiredBeforeArtifact(
        WALKTHROUGH,
        "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
        "required_before_internal_use",
        "internal_use_requirement",
        (
            "candidate remains listed in docs/milestone-e-fixture-candidates.json",
            "criteria remain listed in docs/milestone-e-fixture-promotion-criteria.json",
            *COMMON_INTERNAL_USE_REQUIREMENTS,
        ),
    ),
    RequiredBeforeArtifact(
        PROTOCOL,
        "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
        "required_before_internal_use",
        "internal_use_requirement",
        (
            "candidate remains listed in docs/milestone-e-fixture-candidates.json",
            "criteria remain listed in docs/milestone-e-fixture-promotion-criteria.json",
            "walkthrough remains listed in docs/milestone-e-internal-trust-loop-walkthrough.json",
            *COMMON_INTERNAL_USE_REQUIREMENTS,
        ),
    ),
    RequiredBeforeArtifact(
        MATRIX,
        "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
        "required_before_internal_rehearsal",
        "internal_rehearsal_requirement",
        (
            "candidate remains listed in docs/milestone-e-fixture-candidates.json",
            "criteria remain listed in docs/milestone-e-fixture-promotion-criteria.json",
            "walkthrough remains listed in docs/milestone-e-internal-trust-loop-walkthrough.json",
            "protocol remains listed in docs/milestone-e-internal-trust-loop-use-protocol.json",
            *COMMON_INTERNAL_USE_REQUIREMENTS,
        ),
    ),
    RequiredBeforeArtifact(
        LEDGER,
        "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
        "required_before_blocker_resolution",
        "blocker_resolution_requirement",
        (
            "blocker remains explicit in the source tree",
            "resolution requires a later source-only decision",
            "public-facing use remains blocked until claim-audit and release-scope decisions",
            "make milestone-e-prep remains green",
            "public-surface posture and claims gates remain green",
        ),
    ),
)


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def required_before_keys(mapping: dict[str, Any]) -> list[str]:
    return [
        key
        for key in mapping
        if key.startswith("required_before_") or key.startswith("global_required_before_")
    ]


class MilestoneERequiredBeforeAlignmentTests(unittest.TestCase):
    def test_current_e_artifacts_keep_expected_required_before_values(self) -> None:
        for entry in REQUIRED_BEFORE_ARTIFACTS:
            artifact = load_json(entry.artifact)

            self.assertEqual(list(entry.requirements), artifact[entry.key], entry.artifact)
            self.assertEqual([entry.key], required_before_keys(artifact), entry.artifact)

    def test_current_e_schemas_keep_matching_required_before_enums(self) -> None:
        for entry in REQUIRED_BEFORE_ARTIFACTS:
            schema = load_json(entry.schema)
            requirement_property = schema["properties"][entry.key]
            requirement_def = schema["$defs"][entry.schema_def]

            self.assertIn(entry.key, schema["required"], entry.schema)
            self.assertEqual([entry.key], required_before_keys(schema["properties"]), entry.schema)
            self.assertEqual(len(entry.requirements), requirement_property["minItems"], entry.schema)
            self.assertEqual(len(entry.requirements), requirement_property["maxItems"], entry.schema)
            self.assertEqual(f"#/$defs/{entry.schema_def}", requirement_property["items"]["$ref"], entry.schema)
            self.assertIs(True, requirement_property["uniqueItems"], entry.schema)
            self.assertEqual(list(entry.requirements), requirement_def["enum"], entry.schema)

    def test_required_before_artifact_and_schema_sets_are_explicit(self) -> None:
        discovered_artifacts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "docs").glob("milestone-e-*.json")
            if required_before_keys(load_json(str(path.relative_to(ROOT))))
        }
        discovered_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
            if required_before_keys(load_json(str(path.relative_to(ROOT)))["properties"])
        }

        self.assertEqual({entry.artifact for entry in REQUIRED_BEFORE_ARTIFACTS}, discovered_artifacts)
        self.assertEqual({entry.schema for entry in REQUIRED_BEFORE_ARTIFACTS}, discovered_schemas)

    def test_required_before_values_preserve_source_only_gate_vocabulary(self) -> None:
        for entry in REQUIRED_BEFORE_ARTIFACTS:
            requirements = load_json(entry.artifact)[entry.key]

            self.assertIn("make milestone-e-prep remains green", requirements, entry.artifact)
            self.assertIn("public-surface posture and claims gates remain green", requirements, entry.artifact)

        for entry in REQUIRED_BEFORE_ARTIFACTS[:-1]:
            requirements = load_json(entry.artifact)[entry.key]
            self.assertIn("expected diagnostic boundary remains explicit", requirements, entry.artifact)
            self.assertIn("blocker status remains explicit", requirements, entry.artifact)

    def test_scope_status_and_roadmap_name_required_before_alignment(self) -> None:
        for path in (PREP_SCOPE, EXECUTION_STATUS, ROADMAP):
            normalized = " ".join(read(path).split())

            self.assertIn("required-before alignment", normalized, str(path))
            self.assertIn("make milestone-e-prep remains green", normalized, str(path))
            self.assertIn("does not resolve or soften blockers", normalized, str(path))

    def test_make_target_runs_required_before_guard_after_applies_to_guard(self) -> None:
        block = target_block("milestone-e-prep")

        applies_to_guard = "$(PYTHON) .github/scripts/test_milestone_e_applies_to_binding_alignment.py"
        required_before_guard = "$(PYTHON) .github/scripts/test_milestone_e_required_before_alignment.py"
        prep_scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(required_before_guard, block)
        self.assertLess(block.index(applies_to_guard), block.index(required_before_guard))
        self.assertLess(block.index(required_before_guard), block.index(prep_scope_guard))
        self.assertLess(block.index(required_before_guard), block.index("git diff --check"))

    def test_ci_runs_required_before_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        applies_to_guard = "python3 .github/scripts/test_milestone_e_applies_to_binding_alignment.py"
        required_before_guard = "python3 .github/scripts/test_milestone_e_required_before_alignment.py"
        prep_scope_guard = "python3 .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(required_before_guard, text)
        self.assertEqual(1, text.count(required_before_guard))
        self.assertLess(text.index(applies_to_guard), text.index(required_before_guard))
        self.assertLess(text.index(required_before_guard), text.index(prep_scope_guard))

    def test_required_before_artifacts_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            json.dumps(load_json(entry.artifact), sort_keys=True).lower()
            for entry in REQUIRED_BEFORE_ARTIFACTS
        )

        for phrase in FORBIDDEN_ARTIFACT_WORDING:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
