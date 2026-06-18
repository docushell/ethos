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

from jsonschema import Draft202012Validator
from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestone-d-sandbox-subprocess-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/sandbox/sandbox_subprocess_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-sandbox-subprocess-contract.schema.json"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
PDF_PARSE_TESTS = ROOT / "crates/ethos-cli/tests/pdf_parse.rs"
EXPECTED_EXPLICIT_BLOCKERS = [
    "hardened OS sandbox rules",
    "network-denying runtime proof",
    "file-descriptor or child-process enforcement",
    "arbitrary filesystem allowlist enforcement",
    "a new public command or binding surface",
    "Python, Node, MCP, or hosted sandbox surfaces",
    "crop or verification API changes",
]
EXPECTED_BOUNDARIES = [
    "max_parse_ms_timeout",
    "memory_limit_error",
    "stable_error_envelope",
    "diagnostics_gated_stderr",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def normalized_contract_text() -> str:
    return re.sub(r"\s+", " ", contract_text())


def contract_explicit_blockers() -> list[str]:
    match = re.search(
        r"## Explicit Blockers For This Slice\n\n"
        r"This first `sandbox_subprocess` slice does not add:\n\n"
        r"(?P<bullets>(?:- .+\n)+)",
        contract_text(),
    )
    if match is None:
        raise AssertionError("missing sandbox_subprocess explicit blocker list")
    return [
        line.removeprefix("- ").rstrip(";.")
        for line in match.group("bullets").strip().splitlines()
    ]


class MilestoneDSandboxSubprocessContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-sandbox-subprocess-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-sandbox-subprocess-contract")

        required = [
            "cargo test --locked -p ethos-cli --test pdf_parse worker",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_sandbox_subprocess_contract.py",
            "git diff --check",
        ]
        for command in required:
            self.assertIn(command, block)

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("milestone-d-sandbox-subprocess-contract")

        for out_of_scope in [
            "verify-rendered-crops",
            "compare-rendered-crops",
            "layout-evaluator-alpha",
            "python-surface-test",
            "milestone-c-internal-checks",
            "milestone-d-crop-element-contract",
            "npm",
            "mcp",
        ]:
            self.assertNotIn(out_of_scope, block)

    def test_contract_is_linked_from_status_docs(self) -> None:
        for path in [ROADMAP, EXECUTION_STATUS, SCHEMAS_README]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("milestone-d-sandbox-subprocess-contract.md", text, path)

    def test_contract_defines_existing_carrier_not_new_surface(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("does not add a hardened OS sandbox", text)
        self.assertIn(
            "The current executable carrier remains the PDF worker process behind "
            "`ethos doc parse` and `ethos fingerprint`",
            text,
        )
        self.assertIn(
            "`sandbox_subprocess` names the future backend contract between hostile PDF input, "
            "bounded worker execution, normalized document output, and stable error envelopes",
            text,
        )

    def test_contract_pins_fail_closed_boundaries(self) -> None:
        text = normalized_contract_text()

        for required in [
            "`parse_timeout` error code",
            "`memory_limit_exceeded` error code",
            "stable worker error envelopes are relayed",
            "non-envelope worker stderr is hidden by default",
            "explicit diagnostics",
            "stdout remains empty on worker failures",
            "`make milestone-d-sandbox-subprocess-contract PYTHON=<jsonschema-venv>/bin/python`",
        ]:
            self.assertIn(required, text)
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, contract_explicit_blockers())

    def test_contract_inventory_schema_validates_inventory(self) -> None:
        schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        inventory = load_json(CONTRACT_INVENTORY)
        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(inventory),
            key=lambda error: list(error.absolute_path),
        )
        self.assertEqual([], errors)

    def test_contract_inventory_matches_existing_worker_tests(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        test_source = PDF_PARSE_TESTS.read_text(encoding="utf-8")

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "sandbox_subprocess.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "pdfium worker process")
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])

        case_names = [case["name"] for case in inventory["cases"]]
        self.assertEqual(len(case_names), len(set(case_names)))
        self.assertEqual(
            sorted(EXPECTED_BOUNDARIES),
            sorted({case["boundary"] for case in inventory["cases"]}),
        )
        for case in inventory["cases"]:
            self.assertIn(f"fn {case['test_filter']}()", test_source, case["name"])

    def test_inventory_keeps_current_command_surfaces_narrow(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(
            {"ethos doc parse", "ethos fingerprint"},
            {case["command_surface"] for case in inventory["cases"]},
        )


if __name__ == "__main__":
    unittest.main()
