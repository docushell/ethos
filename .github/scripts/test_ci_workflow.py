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
import re
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
FROZEN_GUARDS = ROOT / ".github/scripts/frozen_record_guards.json"


def workflow_text() -> str:
    return CI_WORKFLOW.read_text(encoding="utf-8")


def frozen_guard_paths() -> list[str]:
    payload = json.loads(FROZEN_GUARDS.read_text(encoding="utf-8"))
    return payload["guards"]


def active_package_guard_names(text: str) -> list[str]:
    return re.findall(
        r"test_milestone_e_package_publication_[A-Za-z0-9_]+\.py",
        text,
    )


class CiWorkflowTests(unittest.TestCase):
    def test_active_behavior_and_schema_gates_run_in_pr_ci(self) -> None:
        text = workflow_text()

        for command in (
            "cargo test --locked --workspace --all-features",
            "python3 fixtures/validate_fixtures.py",
            "make layout-evaluator-alpha",
            "PYTHONPATH=python python3 -m unittest discover -s python/tests",
            "python3 .github/scripts/test_evidence_anchor_v1_contract.py",
            "make app-answer-release-contract PYTHON=python3",
            "python3 .github/scripts/test_python_public_api_policy.py",
            "python3 .github/scripts/test_milestone_d_internal_contracts.py",
            "python3 benchmarks/harness/test_run_gate_zero.py",
        ):
            self.assertIn(command, text)

    def test_package_integrity_and_registry_surface_gates_run_in_pr_ci(self) -> None:
        text = workflow_text()

        for command in (
            "npm test --prefix packages/npm/ethos-pdf",
            "python3 .github/scripts/test_package_registry_source_consistency.py",
            "python3 .github/scripts/test_claims_gate_registry_surfaces.py",
            "python3 .github/scripts/claims_gate.py",
            "python3 .github/scripts/public_boundary_claims_gate.py",
            "python3 .github/scripts/check_release_boundary_paths.py",
        ):
            self.assertIn(command, text)

    def test_frozen_guards_are_manifest_driven_once(self) -> None:
        text = workflow_text()
        runner = "python3 .github/scripts/run_frozen_record_guards.py"

        self.assertEqual(1, text.count(runner))
        self.assertEqual(
            1,
            text.count("python3 .github/scripts/test_run_frozen_record_guards.py"),
        )
        for guard in frozen_guard_paths():
            self.assertNotIn(f"python3 {guard}", text, guard)

    def test_active_package_guard_sequence_matches_make_and_follows_frozen_runner(self) -> None:
        text = workflow_text()
        make_guards = active_package_guard_names(target_block("milestone-e-prep"))
        ci_guards = active_package_guard_names(text)

        self.assertTrue(make_guards)
        self.assertEqual(len(make_guards), len(set(make_guards)))
        self.assertEqual(make_guards, ci_guards)

        frozen_runner = "python3 .github/scripts/run_frozen_record_guards.py"
        first_command = f"python3 .github/scripts/{ci_guards[0]}"
        last_command = f"python3 .github/scripts/{ci_guards[-1]}"
        gate_zero = "python3 benchmarks/harness/test_run_gate_zero.py"
        self.assertLess(text.index(frozen_runner), text.index(first_command))
        self.assertLess(text.index(last_command), text.index(gate_zero))

        make_tail = (
            "$(PYTHON) .github/scripts/"
            "test_milestone_e_public_facing_readiness_ledger.py"
        )
        make_last = f"$(PYTHON) .github/scripts/{make_guards[-1]}"
        make_block = target_block("milestone-e-prep")
        self.assertLess(make_block.index(make_last), make_block.index(make_tail))

    def test_current_release_state_is_tested_and_checked(self) -> None:
        text = workflow_text()

        self.assertEqual(1, text.count("python3 .github/scripts/test_release_state.py"))
        self.assertEqual(
            1,
            text.count("python3 .github/scripts/check_release_state.py --check"),
        )
        self.assertEqual(
            1,
            text.count("python3 .github/scripts/test_github_release_metadata.py"),
        )

    def test_verify_portability_uses_metadata_policy_not_a_name_blocklist(self) -> None:
        text = workflow_text()

        self.assertIn(
            "python3 .github/scripts/test_check_verify_dependency_boundary.py",
            text,
        )
        self.assertIn(
            "python3 .github/scripts/check_verify_dependency_boundary.py",
            text,
        )
        self.assertIn(
            "cargo check --locked -p ethos-doc-core --no-default-features --features grounding",
            text,
        )
        self.assertIn(
            "cargo check --locked -p ethos-doc-core --no-default-features --features verify-types",
            text,
        )
        self.assertNotIn("grep -qiE 'ethos-pdf|ethos-layout", text)

    def test_schema_and_release_hygiene_jobs_remain_explicit(self) -> None:
        text = workflow_text()

        for command in (
            'pip install "jsonschema>=4.18"',
            "python3 schemas/validate_examples.py",
            "python3 schemas/test_security_report_validation.py",
            "python3 schemas/test_table_model_validation.py",
            "python3 .github/scripts/validation_record_integrity.py",
        ):
            self.assertIn(command, text)
        self.assertIn("fetch-depth: 0", text)
        self.assertNotIn(
            'echo "skipped: PDFium runtime is not configured in base CI yet"',
            text,
        )

    def test_active_package_publication_guards_stay_visible(self) -> None:
        text = workflow_text()

        active_guards = (
            "test_milestone_e_package_publication_approval_prep.py",
            "test_milestone_e_package_publication_dependency_ordering.py",
            "test_milestone_e_package_publication_current_registry_assembly.py",
            "test_milestone_e_package_publication_public_installation_availability.py",
            "test_v0_3_0_version_activation.py",
        )
        for guard in active_guards:
            command = f"python3 .github/scripts/{guard}"
            self.assertEqual(1, text.count(command), guard)


if __name__ == "__main__":
    unittest.main()
