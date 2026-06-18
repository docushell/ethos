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
CONTRACT = ROOT / "docs/milestone-d-opendataloader-adapter-shape-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/verify/opendataloader_adapter_shape_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-opendataloader-adapter-shape-contract.schema.json"
ADAPTER_SOURCE = ROOT / "adapters/grounding/opendataloader-json/src/lib.rs"
ADAPTER_README = ROOT / "adapters/grounding/opendataloader-json/README.md"
CLI_VERIFY_TEST = ROOT / "crates/ethos-cli/tests/verify.rs"
VERIFY_CASES = ROOT / "examples/verify/cases.json"
VERIFICATION_REPORT_SCHEMA = ROOT / "schemas/ethos-verification-report.schema.json"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
EXPECTED_EXPLICIT_BLOCKERS = [
    "a new command or binding surface",
    "a new foreign parser adapter",
    "adapter behavior beyond committed fixtures",
    "coordinate-origin inference",
    "fingerprint, span, char-offset, or crop support",
    "claim-kind expansion or semantic verification",
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
        r"This first `opendataloader_adapter_shape` slice does not add:\n\n"
        r"(?P<bullets>(?:- .+\n)+)",
        contract_text(),
    )
    if match is None:
        raise AssertionError("missing opendataloader_adapter_shape explicit blocker list")
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


def verify_cases_by_name(section: str) -> dict[str, dict]:
    cases = load_json(VERIFY_CASES)[section]
    return {case["name"]: case for case in cases}


class MilestoneDOpendataloaderAdapterShapeContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-opendataloader-adapter-shape-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-opendataloader-adapter-shape-contract")

        required = [
            "cargo test --locked -p ethos-grounding-opendataloader-json",
            "cargo test --locked -p ethos-cli --test verify opendataloader",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_opendataloader_adapter_shape_contract.py",
            "git diff --check",
        ]
        self.assertEqual(required, [line.strip() for line in block.splitlines() if line.strip()])

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("milestone-d-opendataloader-adapter-shape-contract")

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
            self.assertIn("milestone-d-opendataloader-adapter-shape-contract.md", text, path)

    def test_contract_defines_existing_carrier_not_new_surface(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("does not add a new public command", text)
        self.assertIn(
            "The current executable carrier remains the `ethos-grounding-opendataloader-json` "
            "adapter crate and `ethos verify --grounding opendataloader-json`",
            text,
        )
        self.assertIn(
            "`opendataloader_adapter_shape` names the current contract between "
            "OpenDataLoader-style JSON shapes and the parser-neutral `GroundingSource` boundary",
            text,
        )

    def test_contract_pins_supported_boundaries(self) -> None:
        text = normalized_contract_text()

        for required in [
            "`examples/verify/opendataloader_adapter_shape_v1_contract.json`",
            "`tool`, `pages`, `elements`, and optional `tables`",
            "`kids`, `children`, `list items`, `list_items`, `rows`, and `cells`",
            "centipoint bbox quantization",
            "deterministic element ids",
            "malformed bbox",
            "unknown page references",
            "`make milestone-d-opendataloader-adapter-shape-contract PYTHON=<jsonschema-venv>/bin/python`",
        ]:
            self.assertIn(required, text)
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, contract_explicit_blockers())

    def test_adapter_readme_still_documents_current_shape_boundary(self) -> None:
        text = ADAPTER_README.read_text(encoding="utf-8")

        for required in [
            "documented synthetic subset",
            "OpenDataLoader 2.4.7 output",
            "Nested `kids`/`children`, `list items`/`list_items`, and",
            "`rows[].cells` containers are traversed in document order",
            "`coordinate_origin: unknown`",
        ]:
            self.assertIn(required, text)

    def test_contract_inventory_schema_validates_inventory(self) -> None:
        schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        inventory = load_json(CONTRACT_INVENTORY)

        Draft202012Validator.check_schema(schema)
        self.assertEqual([], schema_errors(schema, inventory))

    def test_contract_inventory_schema_matches_report_grounding_shape(self) -> None:
        inventory_schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        report_schema = load_json(VERIFICATION_REPORT_SCHEMA)
        report_grounding = report_schema["properties"]["grounding"]["properties"]

        self.assertEqual(
            sorted(inventory_schema["$defs"]["capabilities"]["properties"].keys()),
            sorted(report_grounding["capabilities"]["properties"].keys()),
        )
        self.assertEqual(
            sorted(inventory_schema["$defs"]["capabilities"]["required"]),
            sorted(report_grounding["capabilities"]["required"]),
        )
        self.assertEqual(
            ["top-left", "bottom-left", "unknown"],
            report_grounding["capabilities"]["properties"]["coordinate_origin"]["enum"],
        )
        self.assertEqual(
            sorted(inventory_schema["$defs"]["parser"]["properties"].keys()),
            sorted(report_grounding["parser"]["properties"].keys()),
        )

    def test_contract_inventory_case_order_is_deterministic(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(
            [
                "documented-subset",
                "real-basic-tree",
                "real-text-child-aliases",
                "real-table-cells",
                "real-structural-containers",
            ],
            [case["name"] for case in inventory["accepted_shapes"]],
        )
        self.assertEqual(
            [
                "documented-malformed-bbox",
                "documented-unknown-page",
                "real-malformed-child-containers",
                "real-malformed-table-cells",
                "unrecognized-root",
            ],
            [case["name"] for case in inventory["rejected_shapes"]],
        )

    def test_contract_inventory_binds_existing_tests_and_fixtures(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        adapter_tests = rust_test_names(ADAPTER_SOURCE)
        cli_tests = rust_test_names(CLI_VERIFY_TEST)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "opendataloader_adapter_shape.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "opendataloader-json adapter")
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])

        for case in inventory["accepted_shapes"] + inventory["rejected_shapes"]:
            if "source_fixture" in case:
                self.assertTrue((ROOT / case["source_fixture"]).is_file(), case["name"])
            for test_name in case["adapter_tests"]:
                self.assertIn(test_name, adapter_tests, case["name"])
            for test_name in case["cli_verify_tests"]:
                self.assertIn(test_name, cli_tests, case["name"])

    def test_accepted_report_cases_match_expected_grounding(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        report_cases = verify_cases_by_name("report_cases")

        for shape in inventory["accepted_shapes"]:
            for case_name in shape["cli_verify_cases"]:
                self.assertIn(case_name, report_cases, shape["name"])
                report_case = report_cases[case_name]
                self.assertEqual("opendataloader-json", report_case.get("grounding"))
                if "source_fixture" in shape:
                    self.assertEqual(shape["source_fixture"], report_case["input"])
                golden = load_json(ROOT / report_case["golden"])
                self.assertEqual(shape["expected_parser"], golden["grounding"]["parser"])
                self.assertEqual(
                    shape["expected_capabilities"],
                    golden["grounding"]["capabilities"],
                )
                self.assertIn("capability_limited", golden["warnings"])
                self.assertFalse(golden["fingerprint_stale"])

    def test_rejected_usage_error_cases_match_inventory(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        usage_cases = verify_cases_by_name("usage_error_cases")
        adapter_source = ADAPTER_SOURCE.read_text(encoding="utf-8")

        for shape in inventory["rejected_shapes"]:
            expected = shape["expected_error_contains"]
            if "cli_usage_error_case" in shape:
                case_name = shape["cli_usage_error_case"]
                self.assertIn(case_name, usage_cases, shape["name"])
                usage_case = usage_cases[case_name]
                if "source_fixture" in shape:
                    self.assertEqual(shape["source_fixture"], usage_case["input"])
                self.assertEqual(expected, usage_case["stderr_contains"])
                continue
            self.assertIn(expected, adapter_source, shape["name"])


if __name__ == "__main__":
    unittest.main()
