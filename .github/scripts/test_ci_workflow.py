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

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


def workflow_text() -> str:
    return CI_WORKFLOW.read_text(encoding="utf-8")


class CiWorkflowTests(unittest.TestCase):
    def test_alpha_fixture_and_layout_gates_run_in_pr_ci(self) -> None:
        text = workflow_text()

        self.assertIn("python3 fixtures/validate_fixtures.py", text)
        self.assertIn("make layout-evaluator-alpha", text)
        self.assertIn("PYTHONPATH=python python3 -m unittest discover -s python/tests", text)

    def test_schema_job_installs_jsonschema_and_validates_examples(self) -> None:
        text = workflow_text()

        self.assertIn('pip install "jsonschema>=4.18"', text)
        self.assertIn("python3 schemas/validate_examples.py", text)
        self.assertIn("python3 schemas/test_security_report_validation.py", text)
        self.assertIn("python3 schemas/test_table_model_validation.py", text)

    def test_ci_workflow_guard_is_run_by_ci(self) -> None:
        text = workflow_text()

        self.assertIn("python3 .github/scripts/test_ci_workflow.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_b_internal_checks.py", text)
        self.assertIn("python3 .github/scripts/test_rag_chunk_alpha.py", text)
        self.assertIn("python3 .github/scripts/test_security_report_alpha.py", text)
        self.assertIn("python3 .github/scripts/test_execution_status.py", text)
        self.assertIn("python3 .github/scripts/test_roadmap_status.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_b_closeout_record.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_c_closeout_record.py", text)
        self.assertIn("python3 .github/scripts/test_milestone_b_exit_checklist.py", text)


if __name__ == "__main__":
    unittest.main()
