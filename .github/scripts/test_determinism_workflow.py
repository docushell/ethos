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


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/determinism.yml"
REQUIRED_MATRIX_OS = {"macos-14", "ubuntu-latest", "windows-latest"}


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def matrix_os_values(text: str) -> set[str]:
    match = re.search(r"^\s*os:\s*\[([^\]]+)\]\s*$", text, flags=re.MULTILINE)
    if match is None:
        return set()
    return {item.strip() for item in match.group(1).split(",")}


class DeterminismWorkflowTests(unittest.TestCase):
    def test_matrix_includes_gate_zero_platforms_and_windows_preflight(self) -> None:
        self.assertEqual(matrix_os_values(workflow_text()), REQUIRED_MATRIX_OS)

    def test_windows_is_no_longer_left_as_a_todo(self) -> None:
        text = workflow_text()

        self.assertIn("Windows x64 runs a Milestone B", text)
        self.assertNotIn("TODO", text)
        self.assertNotIn("add windows-latest", text)

    def test_contract_vectors_run_on_every_matrix_os(self) -> None:
        text = workflow_text()

        self.assertIn("runs-on: ${{ matrix.os }}", text)
        self.assertIn("cargo test --locked -p ethos-doc-core --all-features", text)

    def test_parser_neutral_verifier_and_report_goldens_run_on_every_os(self) -> None:
        text = workflow_text()

        self.assertIn("cargo test --locked -p ethos-verify", text)
        self.assertIn("verification report repeated-byte and golden equality", text)
        self.assertIn("examples/verify/check_verify_alpha.py", text)
        self.assertIn("--ethos-bin", text)
        self.assertIn("--out-dir", text)

    def test_pdfium_fixture_corpus_and_double_parse_are_explicitly_conditional(self) -> None:
        text = workflow_text()

        self.assertIn("configured PDFium fixture corpus and double-parse equality", text)
        self.assertIn("shell: bash", text)
        self.assertIn("ETHOS_PDFIUM_LIBRARY_PATH", text)
        self.assertIn("benchmarks/harness/run_fixtures.py", text)
        self.assertIn('--out "${RUNNER_TEMP}/fixture-baseline.json"', text)
        self.assertIn("double_parse_is_byte_identical_when_pdfium_is_configured", text)
        self.assertIn("-- --exact --nocapture", text)
        self.assertIn(
            "deferred: caller-provided PDFium runtime is not configured", text
        )
        self.assertNotIn("full-corpus fingerprint equality", text)

    def test_matrix_does_not_fail_fast(self) -> None:
        self.assertIn("fail-fast: false", workflow_text())


if __name__ == "__main__":
    unittest.main()
