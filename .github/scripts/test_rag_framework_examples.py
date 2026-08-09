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

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples/citation-emission"
REQUIREMENTS = EXAMPLES / "requirements-frameworks.txt"
ETHOS_BIN = ROOT / "target/debug/ethos"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"
FRAMEWORKS = {
    "langchain": ROOT / "examples/langchain-rag/run.py",
    "llamaindex": ROOT / "examples/llamaindex-rag/run.py",
}
CASES = {
    "grounded": (0, True, ["grounded", "grounded"], "hydrated.grounded.json"),
    "fabricated": (1, False, ["mismatch"], "hydrated.fabricated-quote.json"),
}
API_KEY_ENV = (
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "DOCUSHELL_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
)


def run_example(script: Path, case: str, out_dir: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    for name in API_KEY_ENV:
        environment.pop(name, None)
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--case",
            case,
            "--ethos-bin",
            str(ETHOS_BIN),
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        text=True,
        capture_output=True,
    )


class RagFrameworkExampleTests(unittest.TestCase):
    def test_examples_run_twice_byte_identically_without_api_keys(self) -> None:
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="ethos-rag-frameworks-") as temp:
            temp_dir = Path(temp)
            for framework, script in FRAMEWORKS.items():
                for case, (expected_exit, grounded, statuses, fixture) in CASES.items():
                    artifacts = []
                    for run in (1, 2):
                        out_dir = temp_dir / framework / f"run{run}"
                        result = run_example(script, case, out_dir)
                        self.assertEqual("", result.stderr, (framework, case, run))
                        self.assertEqual(
                            expected_exit,
                            result.returncode,
                            (framework, case, run, result.stderr),
                        )
                        case_dir = out_dir / case
                        artifacts.append((
                            (case_dir / "citations.json").read_bytes(),
                            (case_dir / "verification-report.json").read_bytes(),
                        ))

                    self.assertEqual(artifacts[0], artifacts[1], (framework, case))
                    self.assertEqual(
                        (EXAMPLES / fixture).read_bytes(),
                        artifacts[0][0],
                        (framework, case),
                    )
                    report = json.loads(artifacts[0][1])
                    self.assertEqual(grounded, report["all_evidence_grounded"])
                    self.assertEqual(statuses, [check["status"] for check in report["checks"]])

        self.assertLess(time.monotonic() - started, 30 * 60)

    def test_examples_use_only_exact_framework_pins(self) -> None:
        lines = [
            line
            for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        ]
        self.assertEqual([
            "langchain-core==0.3.86",
            "llama-index-core==0.14.16",
        ], lines)
        self.assertNotIn("requirements-frameworks", (ROOT / "pyproject.toml").read_text())

    def test_examples_use_native_framework_types_and_document_the_boundary(self) -> None:
        expected_imports = {
            "langchain": "from langchain_core.documents import Document",
            "llamaindex": "from llama_index.core.schema import NodeWithScore, TextNode",
        }
        for framework, script in FRAMEWORKS.items():
            self.assertIn(expected_imports[framework], script.read_text(encoding="utf-8"))
            readme = script.with_name("README.md").read_text(encoding="utf-8")
            for required in [
                "--case fabricated",
                "intentionally exits `1`",
                "needs no API key",
                "Ethos verifies citation grounding, not semantic truth.",
            ]:
                self.assertIn(required, readme, (framework, required))

    def test_make_target_never_leaks_secrets_or_publishes(self) -> None:
        # Content guard, not a wiring guard. The removed half of this test asserted
        # that ci.yml contained specific literal strings, which breaks whenever CI is
        # legitimately reorganised and catches no product defect.
        block = target_block("rag-framework-examples")
        self.assertIn("$(PYTHON) .github/scripts/test_rag_framework_examples.py", block)
        for forbidden in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "npm publish", "cargo publish"]:
            self.assertNotIn(forbidden, block)


if __name__ == "__main__":
    unittest.main()
