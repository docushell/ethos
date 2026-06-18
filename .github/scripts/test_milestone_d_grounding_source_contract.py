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
CONTRACT = ROOT / "docs/milestone-d-grounding-source-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/verify/grounding_source_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-grounding-source-contract.schema.json"
GROUNDING_SOURCE = ROOT / "crates/ethos-core/src/grounding.rs"
MODEL_SOURCE = ROOT / "crates/ethos-core/src/model.rs"
ODL_SOURCE = ROOT / "adapters/grounding/opendataloader-json/src/lib.rs"
CLI_VERIFY_TEST = ROOT / "crates/ethos-cli/tests/verify.rs"
VERIFICATION_REPORT_SCHEMA = ROOT / "schemas/ethos-verification-report.schema.json"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
EXPECTED_EXPLICIT_BLOCKERS = [
    "a new command or binding surface",
    "a new foreign parser adapter",
    "adapter behavior beyond committed fixtures",
    "first-class crop API behavior",
    "sandbox backend behavior",
    "claim-kind expansion or semantic verification",
]
EXPECTED_TRAIT_METHODS = [
    "parser",
    "capabilities",
    "fingerprint",
    "pages",
    "elements",
    "spans",
    "tables",
    "crop_ref",
    "element_by_id",
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
        r"This first `grounding_source` slice does not add:\n\n"
        r"(?P<bullets>(?:- .+\n)+)",
        contract_text(),
    )
    if match is None:
        raise AssertionError("missing grounding_source explicit blocker list")
    return [
        line.removeprefix("- ").rstrip(";.")
        for line in match.group("bullets").strip().splitlines()
    ]


def schema_errors(schema: dict, instance: dict) -> list:
    return sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )


def rust_test_names(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"(?m)^\s*fn ([a-z][a-z0-9_]*)\(", text))


def trait_method_names() -> list[str]:
    text = GROUNDING_SOURCE.read_text(encoding="utf-8")
    match = re.search(r"pub trait GroundingSource \{(?P<body>.*?)\n\}", text, re.DOTALL)
    if match is None:
        raise AssertionError("missing GroundingSource trait body")
    return re.findall(r"(?m)^\s*fn ([a-z][a-z0-9_]*)\(", match.group("body"))


class MilestoneDGroundingSourceContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-grounding-source-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-grounding-source-contract")

        required = [
            "cargo test --locked -p ethos-core grounding",
            "cargo test --locked -p ethos-cli --test verify native_ethos_verify_produces_non_empty_checks",
            "cargo test --locked -p ethos-cli --test verify opendataloader_verify_adapter_produces_capability_aware_report",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_grounding_source_contract.py",
            "git diff --check",
        ]
        self.assertEqual(required, [line.strip() for line in block.splitlines() if line.strip()])

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("milestone-d-grounding-source-contract")

        for out_of_scope in [
            "verify-alpha",
            "rag-chunk-alpha",
            "security-report-alpha",
            "verify-rendered-crops",
            "compare-rendered-crops",
            "layout-evaluator-alpha",
            "python-surface-test",
            "milestone-b-internal-checks",
            "milestone-c-internal-checks",
            "npm",
            "mcp",
        ]:
            self.assertNotIn(out_of_scope, block)

    def test_contract_is_linked_from_status_docs(self) -> None:
        for path in [ROADMAP, EXECUTION_STATUS, SCHEMAS_README]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("milestone-d-grounding-source-contract.md", text, path)

    def test_contract_defines_existing_carrier_not_new_surface(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("does not add a new public command", text)
        self.assertIn("The current executable carrier remains the `GroundingSource` trait", text)
        self.assertIn("native Ethos document JSON, foreign adapter output, and the verifier", text)

    def test_contract_pins_supported_boundaries(self) -> None:
        text = normalized_contract_text()

        for required in [
            "`examples/verify/grounding_source_v1_contract.json`",
            "`ParserIdentity`",
            "`Capabilities`",
            "`verification_report.grounding`",
            "default optional trait methods remain safe",
            "`make milestone-d-grounding-source-contract PYTHON=<jsonschema-venv>/bin/python`",
        ]:
            self.assertIn(required, text)
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, contract_explicit_blockers())

    def test_contract_inventory_schema_validates_inventory(self) -> None:
        schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        inventory = load_json(CONTRACT_INVENTORY)

        Draft202012Validator.check_schema(schema)
        self.assertEqual([], schema_errors(schema, inventory))

    def test_trait_method_surface_matches_inventory(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(EXPECTED_TRAIT_METHODS, inventory["required_trait_methods"])
        self.assertEqual(EXPECTED_TRAIT_METHODS, trait_method_names())

    def test_report_schema_grounding_matches_trait_metadata(self) -> None:
        schema = load_json(VERIFICATION_REPORT_SCHEMA)
        grounding = schema["properties"]["grounding"]
        capabilities = grounding["properties"]["capabilities"]

        self.assertEqual(["parser", "capabilities"], grounding["required"])
        self.assertEqual(
            [
                "char_offsets",
                "coordinate_origin",
                "crop_support",
                "fingerprint",
                "spans",
                "tables",
            ],
            sorted(capabilities["properties"].keys()),
        )
        self.assertEqual(
            ["bottom-left", "top-left", "unknown"],
            sorted(capabilities["properties"]["coordinate_origin"]["enum"]),
        )

    def test_contract_inventory_binds_existing_sources_and_tests(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        core_tests = rust_test_names(GROUNDING_SOURCE)
        cli_tests = rust_test_names(CLI_VERIFY_TEST)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "grounding_source.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "GroundingSource trait")
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])
        self.assertTrue((ROOT / inventory["trait_module"]).is_file())
        self.assertTrue((ROOT / inventory["report_schema"]).is_file())

        for case in inventory["source_cases"]:
            self.assertTrue((ROOT / case["implementation"]).is_file(), case["name"])
            self.assertTrue((ROOT / case["report_golden"]).is_file(), case["name"])
            for test_name in case["rust_tests"]:
                self.assertIn(test_name, cli_tests, case["name"])

        default_case = inventory["trait_default_case"]
        self.assertEqual("safe-defaults", default_case["name"])
        self.assertTrue((ROOT / default_case["implementation"]).is_file())
        for test_name in default_case["rust_tests"]:
            self.assertIn(test_name, core_tests)
        self.assertEqual(
            ["spans", "tables", "crop_ref", "element_by_id"],
            default_case["expected_defaults"],
        )

    def test_current_implementations_are_named(self) -> None:
        model = MODEL_SOURCE.read_text(encoding="utf-8")
        odl = ODL_SOURCE.read_text(encoding="utf-8")
        grounding = GROUNDING_SOURCE.read_text(encoding="utf-8")

        self.assertIn("impl crate::grounding::GroundingSource for Document", model)
        self.assertIn("impl GroundingSource for OdlJsonSource", odl)
        self.assertIn("fn spans(&self) -> Vec<GroundingSpan> {\n        Vec::new()", grounding)
        self.assertIn("fn tables(&self) -> Vec<GroundingTable> {\n        Vec::new()", grounding)
        self.assertIn("fn crop_ref(&self, _page: &str, _bbox: [i64; 4]) -> Option<String>", grounding)

    def test_source_cases_match_report_goldens(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        for case in inventory["source_cases"]:
            golden = load_json(ROOT / case["report_golden"])
            self.assertEqual(case["expected_parser"], golden["grounding"]["parser"], case["name"])
            self.assertEqual(
                case["expected_capabilities"],
                golden["grounding"]["capabilities"],
                case["name"],
            )
            if case["document_fingerprint_required"]:
                self.assertIn("document_fingerprint", golden, case["name"])
            else:
                self.assertNotIn("document_fingerprint", golden, case["name"])


if __name__ == "__main__":
    unittest.main()
