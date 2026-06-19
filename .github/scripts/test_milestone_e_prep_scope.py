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

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
PREP_SCOPE = ROOT / "docs/milestone-e-prep-scope.md"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", read(path))


class MilestoneEPrepScopeTests(unittest.TestCase):
    def test_prep_scope_keeps_internal_source_only_status(self) -> None:
        text = normalized(PREP_SCOPE)

        self.assertIn("source-only pre-alpha prep for internal Milestone E continuation", text)
        self.assertIn("ADR-0005 remains an internal continuation decision only", text)
        self.assertIn("does not approve public benchmark reports", text)
        self.assertIn("release artifacts, package publication, production positioning", text)
        self.assertIn(
            "performance, quality, footprint, table-quality, or parser-quality claims",
            text,
        )
        self.assertIn("These are internal fixture candidates, not public proof points", text)

    def test_prep_scope_names_guarded_fixture_candidates(self) -> None:
        text = read(PREP_SCOPE)

        required_paths = [
            "examples/verify/cases.json",
            "examples/verify/goldens/native_grounded_report.json",
            "examples/verify/native_split_quote_citations.json",
            "examples/verify/native_non_v1_claims_citations.json",
            "examples/verify/capability_downgrade_v1_contract.json",
            "examples/verify/goldens/opendataloader_capability_limited_report.json",
            "examples/verify/opendataloader_adapter_shape_v1_contract.json",
            "examples/verify/opendataloader.json",
            "fixtures/foreign/opendataloader/real/manifest.json",
            "examples/crop/crop_element_v1_contract.json",
            "examples/crop/crop_element_surface_shape_v1_contract.json",
            "schemas/examples/chunks.example.jsonl",
            "schemas/examples/security-report.example.json",
            "docs/demos/verify-alpha.md",
        ]
        for path in required_paths:
            self.assertIn(f"`{path}`", text)
            self.assertTrue((ROOT / path).exists(), path)

    def test_status_and_roadmap_reference_prep_scope(self) -> None:
        roadmap = read(ROADMAP)
        status = read(EXECUTION_STATUS)

        self.assertIn("docs/milestone-e-prep-scope.md", roadmap)
        self.assertIn("docs/milestone-e-prep-scope.md", status)
        self.assertIn("make milestone-e-prep", status)

    def test_make_target_is_narrow_and_guarded(self) -> None:
        block = target_block("milestone-e-prep")

        required = [
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_public_surface_posture.py",
            "$(PYTHON) .github/scripts/claims_gate.py",
            "$(PYTHON) .github/scripts/test_milestone_e_prep_scope.py",
            "git diff --check",
        ]
        for command in required:
            self.assertIn(command, block)

        for excluded in [
            "release-",
            "third-party-license-manifest",
            "release-notice-draft",
            "deploy",
            "publish",
            "benchmark-report",
            "ethos-bench",
        ]:
            self.assertNotIn(excluded, block)

    def test_ci_runs_prep_scope_guard(self) -> None:
        text = read(CI_WORKFLOW)

        self.assertIn("python3 .github/scripts/test_milestone_e_prep_scope.py", text)

    def test_prep_scope_avoids_public_launch_posture(self) -> None:
        text = normalized(PREP_SCOPE).lower()

        forbidden = [
            "public beta is approved",
            "release-ready",
            "package-ready",
            "production-ready",
            "benchmark-validated",
            "launch-ready",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
