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
CONTRACT = ROOT / "docs/milestone-d-crop-element-surface-shape-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/crop/crop_element_surface_shape_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-crop-element-surface-shape-contract.schema.json"
CROP_ELEMENT_CONTRACT_INVENTORY = ROOT / "examples/crop/crop_element_v1_contract.json"
CROP_ELEMENT_REQUEST_SCHEMA = ROOT / "schemas/ethos-crop-element-request.schema.json"
CROP_DESCRIPTOR_SCHEMA = ROOT / "schemas/ethos-crop-descriptor.schema.json"
CLI_MAIN = ROOT / "crates/ethos-cli/src/main.rs"
PYTHON_CLI = ROOT / "python/ethos_pdf/_cli.py"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
EXPECTED_EXPLICIT_BLOCKERS = [
    "a first-class `crop_element` CLI command",
    "a Python crop method",
    "Node, MCP, or hosted crop surfaces",
    "rendered-crop backend changes",
    "sandbox backend behavior",
    "foreign-adapter crop coordinate hardening",
]
EXPECTED_SURFACE_MAP = {
    "document_fingerprint": "request.document_fingerprint",
    "element_id": "request.element_id",
    "rendering": "request.rendering",
    "source_pdf_fingerprint": "request.source_pdf_fingerprint",
    "crop_descriptor": "descriptor.crop_ref",
    "rendered_artifact": "descriptor.rendered_ref",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def normalized_contract_text() -> str:
    return re.sub(r"\s+", " ", contract_text())


def contract_explicit_blockers() -> list[str]:
    match = re.search(
        r"## Explicit Blockers For This Slice\n\n"
        r"This first `crop_element_surface_shape` slice does not add:\n\n"
        r"(?P<bullets>(?:- .+\n)+)",
        contract_text(),
    )
    if match is None:
        raise AssertionError("missing crop_element_surface_shape explicit blocker list")
    return [
        line.removeprefix("- ").rstrip(";.")
        for line in match.group("bullets").strip().splitlines()
    ]


def schema_errors(schema: dict, instance: dict) -> list:
    return sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )


def schema_property_names(schema: dict) -> set[str]:
    return set(schema["properties"].keys())


class MilestoneDCropElementSurfaceShapeContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-crop-element-surface-shape-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-crop-element-surface-shape-contract")

        required = [
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_crop_element_surface_shape_contract.py",
            "git diff --check",
        ]
        self.assertEqual(required, [line.strip() for line in block.splitlines() if line.strip()])

    def test_target_stays_surface_shape_scoped(self) -> None:
        block = target_block("milestone-d-crop-element-surface-shape-contract")

        for out_of_scope in [
            "cargo test",
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
            self.assertIn("milestone-d-crop-element-surface-shape-contract.md", text, path)

    def test_contract_defines_surface_shape_not_implementation(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("does not add a first-class CLI command", text)
        self.assertIn("The current executable crop carrier remains `ethos verify --crop-dir`", text)
        self.assertIn("names the future callable surface shape", text)
        self.assertIn("does not implement that surface", text)

    def test_contract_pins_supported_boundaries(self) -> None:
        text = normalized_contract_text()

        for required in [
            "`examples/crop/crop_element_surface_shape_v1_contract.json`",
            "`schemas/ethos-crop-element-request.schema.json`",
            "`schemas/ethos-crop-descriptor.schema.json`",
            "`document_fingerprint`",
            "`element_id`",
            "`source_pdf_fingerprint`",
            "current CLI still has no first-class `crop_element` command",
            "current Python scaffold still has no crop method",
            "`make milestone-d-crop-element-surface-shape-contract PYTHON=<jsonschema-venv>/bin/python`",
        ]:
            self.assertIn(required, text)
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, contract_explicit_blockers())

    def test_contract_inventory_schema_validates_inventory(self) -> None:
        schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        inventory = load_json(CONTRACT_INVENTORY)

        Draft202012Validator.check_schema(schema)
        self.assertEqual([], schema_errors(schema, inventory))

    def test_contract_inventory_binds_existing_crop_contract_files(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "crop_element_surface_shape.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "source-only crop_element surface shape")
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])

        for key in ["request_schema", "descriptor_schema", "base_contract_inventory"]:
            self.assertTrue((ROOT / inventory[key]).is_file(), key)
        self.assertEqual(CROP_ELEMENT_CONTRACT_INVENTORY, ROOT / inventory["base_contract_inventory"])

    def test_surface_fields_map_to_existing_request_and_descriptor_schema_fields(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        request_schema = load_json(CROP_ELEMENT_REQUEST_SCHEMA)
        descriptor_schema = load_json(CROP_DESCRIPTOR_SCHEMA)
        request_fields = schema_property_names(request_schema)
        descriptor_fields = schema_property_names(descriptor_schema)

        actual = {field["name"]: field["maps_to"] for field in inventory["planned_surface_fields"]}
        self.assertEqual(EXPECTED_SURFACE_MAP, actual)

        for mapped in actual.values():
            prefix, name = mapped.split(".", 1)
            if prefix == "request":
                self.assertIn(name, request_fields)
            elif prefix == "descriptor":
                self.assertIn(name, descriptor_fields)
            else:
                raise AssertionError(f"unexpected surface mapping prefix: {prefix}")

    def test_rendering_conditions_reuse_existing_schema_modes(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        request_schema = load_json(CROP_ELEMENT_REQUEST_SCHEMA)
        descriptor_schema = load_json(CROP_DESCRIPTOR_SCHEMA)
        conditional = {
            field["name"]: field.get("required_when")
            for field in inventory["planned_surface_fields"]
            if "required_when" in field
        }

        self.assertEqual(
            {
                "source_pdf_fingerprint": "rendering=rendered",
                "rendered_artifact": "rendering=rendered",
            },
            conditional,
        )
        self.assertEqual(["descriptor_only", "rendered"], request_schema["properties"]["rendering"]["enum"])
        self.assertEqual(
            ["descriptor_only", "rendered"],
            descriptor_schema["properties"]["rendering_status"]["enum"],
        )

    def test_current_cli_and_python_surface_absence_is_guarded(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        checked_files = [ROOT / path for path in inventory["current_surface_absence"]["checked_files"]]
        self.assertEqual([CLI_MAIN, PYTHON_CLI], checked_files)

        cli_text = CLI_MAIN.read_text(encoding="utf-8")
        python_text = PYTHON_CLI.read_text(encoding="utf-8")
        self.assertNotIn("CropElement", cli_text)
        self.assertNotIn("crop-element", cli_text)
        self.assertNotIn("crop_element", cli_text)
        self.assertNotIn("def crop", python_text)
        self.assertNotIn("crop_element", python_text)


if __name__ == "__main__":
    unittest.main()
