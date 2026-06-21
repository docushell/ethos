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

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"

EXPECTED_PUBLIC_BOUNDARY = [
    "public reports remain blocked",
    "release artifacts remain blocked",
    "package publication remains blocked",
    "hosted surfaces remain blocked",
    "public result wording remains blocked",
    "performance claims remain blocked",
    "quality claims remain blocked",
    "footprint claims remain blocked",
    "table-quality claims remain blocked",
    "parser-quality claims remain blocked",
]


@dataclass(frozen=True)
class BoundaryArtifact:
    artifact: str
    schema: str


BOUNDARY_ARTIFACTS = (
    BoundaryArtifact(
        "docs/milestone-e-fixture-candidates.json",
        "schemas/ethos-milestone-e-fixture-candidates.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-fixture-promotion-criteria.json",
        "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-internal-trust-loop-walkthrough.json",
        "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-internal-trust-loop-use-protocol.json",
        "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
        "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-internal-trust-loop-blocker-ledger.json",
        "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-public-approval-lane-blockers.json",
        "schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-public-beta-approval-prep.json",
        "schemas/ethos-milestone-e-public-beta-approval-prep.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-package-publication-approval-prep.json",
        "schemas/ethos-milestone-e-package-publication-approval-prep.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-public-facing-readiness-ledger.json",
        "schemas/ethos-milestone-e-public-facing-readiness-ledger.schema.json",
    ),
    BoundaryArtifact(
        "docs/milestone-e-public-beta-current-main-refresh-prep.json",
        "schemas/ethos-milestone-e-public-beta-current-main-refresh-prep.schema.json",
    ),
)


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class MilestoneEPublicBoundaryAlignmentTests(unittest.TestCase):
    def test_current_e_artifacts_share_exact_public_boundary(self) -> None:
        self.assertEqual(10, len(EXPECTED_PUBLIC_BOUNDARY))
        self.assertEqual(len(EXPECTED_PUBLIC_BOUNDARY), len(set(EXPECTED_PUBLIC_BOUNDARY)))

        for entry in BOUNDARY_ARTIFACTS:
            artifact = load_json(entry.artifact)

            self.assertEqual(
                EXPECTED_PUBLIC_BOUNDARY,
                artifact["public_boundary"],
                entry.artifact,
            )

    def test_current_e_schemas_share_exact_public_boundary_enum(self) -> None:
        for entry in BOUNDARY_ARTIFACTS:
            schema = load_json(entry.schema)
            boundary_schema = schema["$defs"]["public_boundary"]
            property_schema = schema["properties"]["public_boundary"]

            self.assertEqual(EXPECTED_PUBLIC_BOUNDARY, boundary_schema["enum"], entry.schema)
            self.assertEqual(10, property_schema["minItems"], entry.schema)
            self.assertEqual(10, property_schema["maxItems"], entry.schema)
            self.assertTrue(property_schema["uniqueItems"], entry.schema)

    def test_boundary_artifact_set_matches_schema_registry(self) -> None:
        discovered_artifacts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "docs").glob("milestone-e-*.json")
        }
        discovered_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
        }

        self.assertEqual({entry.artifact for entry in BOUNDARY_ARTIFACTS}, discovered_artifacts)
        self.assertEqual({entry.schema for entry in BOUNDARY_ARTIFACTS}, discovered_schemas)

    def test_make_target_runs_public_boundary_guard_after_registry_guard(self) -> None:
        block = target_block("milestone-e-prep")

        registry_guard = "$(PYTHON) .github/scripts/test_milestone_e_schema_registry_alignment.py"
        boundary_guard = "$(PYTHON) .github/scripts/test_milestone_e_public_boundary_alignment.py"
        prep_scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(registry_guard, block)
        self.assertIn(boundary_guard, block)
        self.assertIn(prep_scope_guard, block)
        self.assertLess(block.index(registry_guard), block.index(boundary_guard))
        self.assertLess(block.index(boundary_guard), block.index(prep_scope_guard))

    def test_ci_runs_public_boundary_guard_once_in_order(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        registry_guard = "python3 .github/scripts/test_milestone_e_schema_registry_alignment.py"
        boundary_guard = "python3 .github/scripts/test_milestone_e_public_boundary_alignment.py"
        prep_scope_guard = "python3 .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(boundary_guard, text)
        self.assertEqual(1, text.count(boundary_guard))
        self.assertLess(text.index(registry_guard), text.index(boundary_guard))
        self.assertLess(text.index(boundary_guard), text.index(prep_scope_guard))


if __name__ == "__main__":
    unittest.main()
