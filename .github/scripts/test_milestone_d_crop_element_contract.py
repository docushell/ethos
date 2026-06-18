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

import hashlib
import json
import re
import unittest
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator
from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestone-d-crop-element-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/crop/crop_element_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-crop-element-contract.schema.json"
CROP_ELEMENT_REQUEST_SCHEMA = ROOT / "schemas/ethos-crop-element-request.schema.json"
CROP_ELEMENT_REQUEST_EXAMPLE = ROOT / "schemas/examples/crop-element-request.example.json"
CROP_DESCRIPTOR_SCHEMA = ROOT / "schemas/ethos-crop-descriptor.schema.json"
VERIFICATION_REPORT_EXAMPLE = ROOT / "schemas/examples/verification-report.example.json"
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


def checks_by_id(report: dict) -> dict[str, dict]:
    return {check["id"]: check for check in report["checks"]}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_c14n(value: dict) -> str:
    encoded = json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def logical_crop_ref(document_fingerprint: str, check_id: str, page: str) -> str:
    return "crop-{}.json".format(
        sha256_c14n(
            {
                "check_id": check_id,
                "document_fingerprint": document_fingerprint,
                "page": page,
                "version": "ethos.logical_crop_ref.v1",
            }
        )
    )


def logical_request_ref(request: dict) -> str:
    identity = {
        "document_fingerprint": request["document_fingerprint"],
        "element_id": request["element_id"],
        "rendering": request["rendering"],
        "version": "ethos.crop_element_request_ref.v1",
    }
    if "source_pdf_fingerprint" in request:
        identity["source_pdf_fingerprint"] = request["source_pdf_fingerprint"]
    return "request-{}".format(sha256_c14n(identity))


def request_ref_drift_diagnostics(request: dict) -> list[str]:
    if "request_ref" not in request:
        return ["request_ref is missing"]
    if request["request_ref"] != logical_request_ref(request):
        return ["request_ref does not match crop element request identity tuple"]
    return []


def crop_ref_drift_diagnostics(descriptor: dict) -> list[str]:
    diagnostics: list[str] = []
    check_ids = descriptor.get("check_ids", [])
    if len(check_ids) != 1:
        diagnostics.append("descriptor must bind exactly one logical check id")
        return diagnostics

    expected = logical_crop_ref(
        descriptor["document_fingerprint"],
        check_ids[0],
        descriptor["page"],
    )
    if descriptor["crop_ref"] != expected:
        diagnostics.append("descriptor crop_ref does not match logical identity tuple")
    return diagnostics


def schema_errors(schema: dict, instance: dict) -> list:
    return sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )


def request_case_diagnostics(
    request: dict,
    document: dict,
    descriptor: dict,
    case: dict,
) -> list[str]:
    diagnostics: list[str] = []

    if request["document_fingerprint"] != document["fingerprint"]:
        diagnostics.append("request document_fingerprint does not match document fingerprint")
    if descriptor["document_fingerprint"] != request["document_fingerprint"]:
        diagnostics.append("descriptor document_fingerprint does not match request")
    if request["element_id"] != case["element_id"]:
        diagnostics.append("request element_id does not match contract inventory case")

    element = elements_by_id(document).get(request["element_id"])
    if element is None:
        diagnostics.append("request element_id does not resolve in document")
        return diagnostics

    if "page" not in element:
        diagnostics.append("resolved element is missing page")
    elif descriptor["page"] != element["page"]:
        diagnostics.append("descriptor page does not match resolved element")

    if "bbox" not in element:
        diagnostics.append("resolved element is missing bbox")
    elif descriptor["bbox"] != element["bbox"]:
        diagnostics.append("descriptor bbox does not match resolved element")

    if request["rendering"] != case["rendering_status"]:
        diagnostics.append("request rendering does not match contract inventory case")
    if descriptor["rendering_status"] != request["rendering"]:
        diagnostics.append("descriptor rendering_status does not match request")

    return diagnostics


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
            "`schemas/ethos-crop-element-request.schema.json`",
            "`schemas/ethos-crop-descriptor.schema.json`",
            "`examples/crop/crop_element_v1_contract.json`",
            "`schemas/examples/crop-element-request.example.json`",
            "`schemas/examples/crop-descriptor.example.json`",
            "document fingerprint",
            "element id",
            "request_ref",
            "crop element request identity",
            "`ethos.crop_element_request_ref.v1`",
            "page id",
            "bbox",
            "check id",
            "crop descriptor filename",
            "logical evidence identity",
            "`ethos.logical_crop_ref.v1`",
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

    def test_crop_element_request_example_validates_against_request_schema(self) -> None:
        schema = load_json(CROP_ELEMENT_REQUEST_SCHEMA)
        request = load_json(CROP_ELEMENT_REQUEST_EXAMPLE)

        Draft202012Validator.check_schema(schema)
        self.assertEqual([], schema_errors(schema, request))
        self.assertEqual(
            "request-489e91879dd347b3fce36cec50598144cfa96d0158c557665b8f35c6dc46ef85",
            request["request_ref"],
        )
        self.assertEqual([], request_ref_drift_diagnostics(request))

        rendered_request = dict(
            request,
            rendering="rendered",
            source_pdf_fingerprint="sha256:" + "1" * 64,
        )
        rendered_request["request_ref"] = logical_request_ref(rendered_request)
        self.assertEqual([], schema_errors(schema, rendered_request))
        self.assertEqual([], request_ref_drift_diagnostics(rendered_request))

        missing_request_ref = dict(request)
        del missing_request_ref["request_ref"]
        self.assertNotEqual([], schema_errors(schema, missing_request_ref))

        rendered_without_source = dict(request, rendering="rendered")
        self.assertNotEqual([], schema_errors(schema, rendered_without_source))

        descriptor_only_with_source = dict(
            request,
            source_pdf_fingerprint="sha256:" + "1" * 64,
        )
        self.assertNotEqual([], schema_errors(schema, descriptor_only_with_source))

        stale_request_ref = dict(request, request_ref="request-" + "0" * 64)
        self.assertIn(
            "request_ref does not match crop element request identity tuple",
            request_ref_drift_diagnostics(stale_request_ref),
        )

        stale_request_element = dict(request, element_id="e000001")
        self.assertIn(
            "request_ref does not match crop element request identity tuple",
            request_ref_drift_diagnostics(stale_request_element),
        )

        stale_request_fingerprint = dict(request, document_fingerprint="sha256:" + "0" * 64)
        self.assertIn(
            "request_ref does not match crop element request identity tuple",
            request_ref_drift_diagnostics(stale_request_fingerprint),
        )

        rendered_stale_source = dict(
            rendered_request,
            source_pdf_fingerprint="sha256:" + "2" * 64,
        )
        self.assertIn(
            "request_ref does not match crop element request identity tuple",
            request_ref_drift_diagnostics(rendered_stale_source),
        )

    def test_contract_inventory_binds_element_to_descriptor_example(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        request_schema = load_json(CROP_ELEMENT_REQUEST_SCHEMA)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "crop_element.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "ethos verify --crop-dir")
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])

        case_names = [case["name"] for case in inventory["cases"]]
        self.assertEqual(len(case_names), len(set(case_names)))

        for case in inventory["cases"]:
            document_path = ROOT / case["document"]
            request_path = ROOT / case["request"]
            descriptor_path = ROOT / case["descriptor"]
            self.assertTrue(document_path.is_file(), case["name"])
            self.assertTrue(request_path.is_file(), case["name"])
            self.assertTrue(descriptor_path.is_file(), case["name"])

            document = load_json(document_path)
            request = load_json(request_path)
            descriptor = load_json(descriptor_path)
            element = elements_by_id(document)[case["element_id"]]

            self.assertEqual([], schema_errors(request_schema, request), case["name"])
            self.assertEqual([], request_ref_drift_diagnostics(request), case["name"])
            self.assertEqual(request["document_fingerprint"], document["fingerprint"])
            self.assertEqual(request["element_id"], case["element_id"])
            self.assertEqual(request["rendering"], case["rendering_status"])
            self.assertEqual(descriptor["artifact_type"], "ethos.crop_descriptor.v1")
            self.assertEqual(descriptor["document_fingerprint"], request["document_fingerprint"])
            self.assertEqual(descriptor["page"], element["page"])
            self.assertEqual(descriptor["bbox"], element["bbox"])
            self.assertEqual(descriptor["rendering_status"], request["rendering"])
            self.assertEqual(descriptor["check_ids"], ["v0001"])
            self.assertEqual([], crop_ref_drift_diagnostics(descriptor), case["name"])
            self.assertEqual([], request_case_diagnostics(request, document, descriptor, case))

    def test_request_binding_guard_fails_closed_on_stale_or_unresolved_inputs(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        case = inventory["cases"][0]
        request = load_json(ROOT / case["request"])
        document = load_json(ROOT / case["document"])
        descriptor = load_json(ROOT / case["descriptor"])

        unknown_element_request = dict(request, element_id="e999999")
        self.assertIn(
            "request element_id does not resolve in document",
            request_case_diagnostics(unknown_element_request, document, descriptor, case),
        )

        stale_request = dict(request, document_fingerprint="sha256:" + "0" * 64)
        self.assertIn(
            "request document_fingerprint does not match document fingerprint",
            request_case_diagnostics(stale_request, document, descriptor, case),
        )

        mismatched_element_request = dict(request, element_id="e000001")
        self.assertIn(
            "request element_id does not match contract inventory case",
            request_case_diagnostics(mismatched_element_request, document, descriptor, case),
        )

        document_without_page = deepcopy(document)
        del elements_by_id(document_without_page)[request["element_id"]]["page"]
        self.assertIn(
            "resolved element is missing page",
            request_case_diagnostics(request, document_without_page, descriptor, case),
        )

        document_without_bbox = deepcopy(document)
        del elements_by_id(document_without_bbox)[request["element_id"]]["bbox"]
        self.assertIn(
            "resolved element is missing bbox",
            request_case_diagnostics(request, document_without_bbox, descriptor, case),
        )

    def test_contract_inventory_binds_descriptor_to_verification_evidence(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        report = load_json(VERIFICATION_REPORT_EXAMPLE)
        report_checks = checks_by_id(report)

        for case in inventory["cases"]:
            descriptor = load_json(ROOT / case["descriptor"])

            self.assertEqual(report["document_fingerprint"], descriptor["document_fingerprint"])
            for check_id in descriptor["check_ids"]:
                check = report_checks[check_id]
                evidence = check["evidence"]
                citation = check["claim"]["citation"]

                self.assertEqual(citation["element_id"], case["element_id"], case["name"])
                self.assertEqual(evidence["page"], descriptor["page"], case["name"])
                self.assertEqual(evidence["bbox"], descriptor["bbox"], case["name"])
                self.assertEqual(
                    logical_crop_ref(report["document_fingerprint"], check_id, descriptor["page"]),
                    descriptor["crop_ref"],
                    case["name"],
                )
                self.assertEqual(
                    descriptor["text_sha256"],
                    sha256_text(evidence["text"]),
                    case["name"],
                )

    def test_crop_descriptor_crop_ref_fails_closed_on_logical_identity_drift(self) -> None:
        descriptor = load_json(ROOT / "schemas/examples/crop-descriptor.example.json")

        self.assertEqual(
            "crop-17e98204468b3c83e92fabe1ce7749ff4c1c1eaf919c327e6234ab29b50b2677.json",
            logical_crop_ref(descriptor["document_fingerprint"], "v0001", descriptor["page"]),
        )
        self.assertEqual(
            [],
            crop_ref_drift_diagnostics(descriptor),
        )

        stale_crop_ref = dict(descriptor, crop_ref="crop-" + "0" * 64 + ".json")
        self.assertIn(
            "descriptor crop_ref does not match logical identity tuple",
            crop_ref_drift_diagnostics(stale_crop_ref),
        )

        stale_page = dict(descriptor, page="p0002")
        self.assertIn(
            "descriptor crop_ref does not match logical identity tuple",
            crop_ref_drift_diagnostics(stale_page),
        )

        ambiguous_checks = dict(descriptor, check_ids=["v0001", "v0002"])
        self.assertIn(
            "descriptor must bind exactly one logical check id",
            crop_ref_drift_diagnostics(ambiguous_checks),
        )

        self.assertNotEqual(
            logical_crop_ref("sha256:" + "0" * 64, "v0001", descriptor["page"]),
            descriptor["crop_ref"],
        )
        self.assertNotEqual(
            logical_crop_ref(descriptor["document_fingerprint"], "v9999", descriptor["page"]),
            descriptor["crop_ref"],
        )

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
