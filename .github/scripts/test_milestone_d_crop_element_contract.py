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
CONTRACT = ROOT / "docs/milestone-d-crop-element-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/crop/crop_element_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-crop-element-contract.schema.json"
CROP_DESCRIPTOR_SCHEMA = ROOT / "schemas/ethos-crop-descriptor.schema.json"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
CLI_MAIN = ROOT / "crates/ethos-cli/src/main.rs"
VERIFY_TESTS = ROOT / "crates/ethos-cli/tests/verify.rs"
EXPECTED_EXPLICIT_BLOCKERS = [
    "a first-class `crop_element` CLI command or binding surface",
    "Python, Node, MCP, or hosted crop API surfaces",
    "sandbox/subprocess backend expansion",
    "rendered-crop backend changes",
    "foreign-adapter crop coordinate hardening",
    "cross-platform rendered-crop byte identity claims",
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
        r"This first `crop_element` slice does not add:\n\n"
        r"(?P<bullets>(?:- .+\n)+)",
        contract_text(),
    )
    if match is None:
        raise AssertionError("missing crop_element explicit blocker list")
    return [
        line.removeprefix("- ").rstrip(";.")
        for line in match.group("bullets").strip().splitlines()
    ]


def elements_by_id(document: dict) -> dict[str, dict]:
    return {
        element["id"]: element
        for element in document["payload"]["elements"]
        if "id" in element
    }


class MilestoneDCropElementContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-crop-element-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-crop-element-contract")

        required = [
            "cargo test --locked -p ethos-cli --test verify "
            "native_verify_crop_dir_writes_deterministic_crop_descriptors",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_crop_element_contract.py",
            "git diff --check",
        ]
        for command in required:
            self.assertIn(command, block)

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("milestone-d-crop-element-contract")

        for out_of_scope in [
            "verify-rendered-crops",
            "compare-rendered-crops",
            "layout-evaluator-alpha",
            "python-surface-test",
            "release-",
            "third-party-license-manifest",
            "npm",
            "mcp",
        ]:
            self.assertNotIn(out_of_scope, block)

    def test_contract_is_linked_from_status_docs(self) -> None:
        for path in [ROADMAP, EXECUTION_STATUS, SCHEMAS_README]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("milestone-d-crop-element-contract.md", text, path)

    def test_contract_defines_existing_carrier_not_new_surface(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("does not create a first-class CLI command", text)
        self.assertIn(
            "The current executable crop carrier remains `ethos verify --crop-dir` "
            "and optional `--crop-source-pdf`",
            text,
        )
        self.assertIn(
            "`crop_element` names the future first-class contract between a parsed Ethos "
            "document, an explicit element locator, a crop descriptor, and an optional rendered "
            "artifact",
            text,
        )

    def test_contract_pins_descriptor_artifact_boundary(self) -> None:
        text = normalized_contract_text()

        for required in [
            "`schemas/ethos-crop-descriptor.schema.json`",
            "`examples/crop/crop_element_v1_contract.json`",
            "`schemas/examples/crop-descriptor.example.json`",
            "document fingerprint",
            "element id",
            "page id",
            "bbox",
            "crop descriptor filename",
            "optional rendered PNG metadata and source PDF fingerprint",
            "`make milestone-d-crop-element-contract PYTHON=<jsonschema-venv>/bin/python`",
        ]:
            self.assertIn(required, text)

    def test_contract_keeps_boundaries_explicit(self) -> None:
        text = normalized_contract_text()

        self.assertIn("missing elements, missing pages, missing bboxes, malformed bboxes", text)
        self.assertIn("source fingerprint mismatch fail closed", text)
        self.assertIn("does not infer missing geometry", text)
        self.assertIn("Cross-platform rendered crop byte identity is not part", text)
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

    def test_contract_inventory_binds_element_to_descriptor_example(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "crop_element.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "ethos verify --crop-dir")
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])

        case_names = [case["name"] for case in inventory["cases"]]
        self.assertEqual(len(case_names), len(set(case_names)))

        for case in inventory["cases"]:
            document_path = ROOT / case["document"]
            descriptor_path = ROOT / case["descriptor"]
            self.assertTrue(document_path.is_file(), case["name"])
            self.assertTrue(descriptor_path.is_file(), case["name"])

            document = load_json(document_path)
            descriptor = load_json(descriptor_path)
            element = elements_by_id(document)[case["element_id"]]

            self.assertEqual(descriptor["artifact_type"], "ethos.crop_descriptor.v1")
            self.assertEqual(descriptor["document_fingerprint"], document["fingerprint"])
            self.assertEqual(descriptor["page"], element["page"])
            self.assertEqual(descriptor["bbox"], element["bbox"])
            self.assertEqual(descriptor["rendering_status"], case["rendering_status"])
            self.assertEqual(descriptor["check_ids"], ["v0001"])

    def test_crop_descriptor_example_validates_against_descriptor_schema(self) -> None:
        schema = load_json(CROP_DESCRIPTOR_SCHEMA)
        descriptor = load_json(ROOT / "schemas/examples/crop-descriptor.example.json")
        errors = sorted(
            Draft202012Validator(schema).iter_errors(descriptor),
            key=lambda error: list(error.absolute_path),
        )
        self.assertEqual([], errors)

    def test_current_cli_surface_has_no_first_class_crop_element_command(self) -> None:
        source = CLI_MAIN.read_text(encoding="utf-8")
        match = re.search(
            r"#\[derive\(Subcommand\)\]\s*enum Command \{\n(?P<body>.*?)\n\}",
            source,
            flags=re.S,
        )
        self.assertIsNotNone(match, "missing top-level CLI Command enum")

        command_enum = match.group("body")
        for alias in ["crop-element", "crop_element", "CropElement"]:
            self.assertNotIn(alias, command_enum)

    def test_existing_verify_tests_cover_current_crop_carrier(self) -> None:
        text = VERIFY_TESTS.read_text(encoding="utf-8")

        for test_name in [
            "native_verify_crop_dir_writes_deterministic_crop_descriptors",
            "crop_source_pdf_requires_crop_dir",
            "crop_source_pdf_rejects_source_fingerprint_mismatch",
            "crop_source_pdf_writes_rendered_crop_artifacts_when_pdfium_is_configured",
        ]:
            self.assertIn(f"fn {test_name}()", text)


if __name__ == "__main__":
    unittest.main()
