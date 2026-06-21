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
VALIDATION_DIR = ROOT / "docs/validation"

EXPECTED_TOP_LEVEL_STATUS = "source-only-pre-alpha-internal-milestone-e-prep"
EXPECTED_CANDIDATE_ROW_STATUS = "source-only-pre-alpha-internal-candidate"

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
class SourceStatusArtifact:
    artifact: str
    schema: str
    row_key: str | None = None
    row_schema_def: str | None = None


SOURCE_STATUS_ARTIFACTS = (
    SourceStatusArtifact(
        "docs/milestone-e-fixture-candidates.json",
        "schemas/ethos-milestone-e-fixture-candidates.schema.json",
        "fixture_candidates",
        "fixture_candidate",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-fixture-promotion-criteria.json",
        "schemas/ethos-milestone-e-fixture-promotion-criteria.schema.json",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-internal-trust-loop-walkthrough.json",
        "schemas/ethos-milestone-e-internal-trust-loop-walkthrough.schema.json",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-internal-trust-loop-use-protocol.json",
        "schemas/ethos-milestone-e-internal-trust-loop-use-protocol.schema.json",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-internal-trust-loop-rehearsal-evidence-matrix.json",
        "schemas/ethos-milestone-e-internal-trust-loop-rehearsal-evidence-matrix.schema.json",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-internal-trust-loop-blocker-ledger.json",
        "schemas/ethos-milestone-e-internal-trust-loop-blocker-ledger.schema.json",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-public-approval-lane-blockers.json",
        "schemas/ethos-milestone-e-public-approval-lane-blockers.schema.json",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-public-beta-approval-prep.json",
        "schemas/ethos-milestone-e-public-beta-approval-prep.schema.json",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-package-publication-approval-prep.json",
        "schemas/ethos-milestone-e-package-publication-approval-prep.schema.json",
    ),
    SourceStatusArtifact(
        "docs/milestone-e-public-facing-readiness-ledger.json",
        "schemas/ethos-milestone-e-public-facing-readiness-ledger.schema.json",
    ),
)

STATUS_VALIDATION_RECORDS = (
    "milestone-e-fixture-promotion-criteria-validation-2026-06-19.md",
    "milestone-e-internal-trust-loop-walkthrough-validation-2026-06-19.md",
    "milestone-e-internal-trust-loop-walkthrough-all-candidates-validation-2026-06-19.md",
    "milestone-e-internal-trust-loop-use-protocol-validation-2026-06-19.md",
    "milestone-e-internal-trust-loop-rehearsal-evidence-matrix-validation-2026-06-19.md",
    "milestone-e-internal-trust-loop-blocker-ledger-validation-2026-06-19.md",
)


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def row_defs_with_status(schema: dict[str, Any]) -> set[str]:
    defs = schema.get("$defs", {})
    return {
        name
        for name, definition in defs.items()
        if isinstance(definition, dict)
        and "status" in definition.get("properties", {})
    }


class MilestoneESourceStatusAlignmentTests(unittest.TestCase):
    def test_current_e_artifacts_keep_expected_top_level_status(self) -> None:
        for entry in SOURCE_STATUS_ARTIFACTS:
            artifact = load_json(entry.artifact)

            self.assertEqual(EXPECTED_TOP_LEVEL_STATUS, artifact["status"], entry.artifact)

    def test_current_e_fixture_candidate_rows_keep_expected_status(self) -> None:
        candidates = load_json("docs/milestone-e-fixture-candidates.json")

        for row in candidates["fixture_candidates"]:
            self.assertEqual(EXPECTED_CANDIDATE_ROW_STATUS, row["status"], row["id"])

        for entry in SOURCE_STATUS_ARTIFACTS[1:]:
            artifact = load_json(entry.artifact)
            for key, value in artifact.items():
                if not isinstance(value, list):
                    continue
                rows = [row for row in value if isinstance(row, dict)]
                if not rows:
                    continue
                self.assertFalse(
                    any("status" in row for row in rows),
                    f"{entry.artifact}:{key}",
                )

    def test_current_e_schemas_keep_expected_top_level_status_const(self) -> None:
        for entry in SOURCE_STATUS_ARTIFACTS:
            schema = load_json(entry.schema)

            self.assertIn("status", schema["required"], entry.schema)
            self.assertEqual(
                EXPECTED_TOP_LEVEL_STATUS,
                schema["properties"]["status"]["const"],
                entry.schema,
            )

    def test_fixture_candidate_schema_keeps_expected_row_status_const(self) -> None:
        for entry in SOURCE_STATUS_ARTIFACTS:
            schema = load_json(entry.schema)

            if entry.row_schema_def is None:
                self.assertEqual(set(), row_defs_with_status(schema), entry.schema)
                continue

            row_schema = schema["$defs"][entry.row_schema_def]
            self.assertIn("status", row_schema["required"], entry.schema)
            self.assertEqual(
                EXPECTED_CANDIDATE_ROW_STATUS,
                row_schema["properties"]["status"]["const"],
                entry.schema,
            )

    def test_source_status_artifact_and_schema_sets_are_explicit(self) -> None:
        discovered_top_level_artifacts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "docs").glob("milestone-e-*.json")
            if "status" in load_json(str(path.relative_to(ROOT)))
        }
        discovered_top_level_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
            if "status" in load_json(str(path.relative_to(ROOT)))["properties"]
        }
        discovered_row_schemas = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "schemas").glob("ethos-milestone-e-*.schema.json")
            if row_defs_with_status(load_json(str(path.relative_to(ROOT))))
        }

        self.assertEqual({entry.artifact for entry in SOURCE_STATUS_ARTIFACTS}, discovered_top_level_artifacts)
        self.assertEqual({entry.schema for entry in SOURCE_STATUS_ARTIFACTS}, discovered_top_level_schemas)
        self.assertEqual({"schemas/ethos-milestone-e-fixture-candidates.schema.json"}, discovered_row_schemas)

    def test_validation_records_name_current_source_status(self) -> None:
        for record in STATUS_VALIDATION_RECORDS:
            text = read(VALIDATION_DIR / record)

            self.assertIn(EXPECTED_TOP_LEVEL_STATUS, text, record)

    def test_scope_status_and_roadmap_name_source_status_alignment(self) -> None:
        for path in (PREP_SCOPE, EXECUTION_STATUS, ROADMAP):
            normalized = " ".join(read(path).split())

            self.assertIn("source-status alignment", normalized, str(path))
            self.assertIn(EXPECTED_TOP_LEVEL_STATUS, normalized, str(path))
            self.assertIn("does not resolve or soften blockers", normalized, str(path))

    def test_make_target_runs_source_status_guard_after_promotion_status_guard(self) -> None:
        block = target_block("milestone-e-prep")

        promotion_guard = "$(PYTHON) .github/scripts/test_milestone_e_promotion_status_alignment.py"
        source_status_guard = "$(PYTHON) .github/scripts/test_milestone_e_source_status_alignment.py"
        prep_scope_guard = "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(source_status_guard, block)
        self.assertLess(block.index(promotion_guard), block.index(source_status_guard))
        self.assertLess(block.index(source_status_guard), block.index(prep_scope_guard))
        self.assertLess(block.index(source_status_guard), block.index("git diff --check"))

    def test_ci_runs_source_status_guard_once_in_order(self) -> None:
        text = read(CI_WORKFLOW)
        promotion_guard = "python3 .github/scripts/test_milestone_e_promotion_status_alignment.py"
        source_status_guard = "python3 .github/scripts/test_milestone_e_source_status_alignment.py"
        prep_scope_guard = "python3 .github/scripts/test_milestone_e_prep_scope.py"

        self.assertIn(source_status_guard, text)
        self.assertEqual(1, text.count(source_status_guard))
        self.assertLess(text.index(promotion_guard), text.index(source_status_guard))
        self.assertLess(text.index(source_status_guard), text.index(prep_scope_guard))

    def test_source_status_artifacts_avoid_scope_expansion_language(self) -> None:
        text = "\n".join(
            json.dumps(load_json(entry.artifact), sort_keys=True).lower()
            for entry in SOURCE_STATUS_ARTIFACTS
        )

        for phrase in FORBIDDEN_ARTIFACT_WORDING:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
