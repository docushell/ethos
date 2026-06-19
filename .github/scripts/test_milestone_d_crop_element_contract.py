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
VERIFY_SOURCE = ROOT / "crates/ethos-cli/src/cmd/verify.rs"
VERIFY_TESTS = ROOT / "crates/ethos-cli/tests/verify.rs"
EXPECTED_EXPLICIT_BLOCKERS = [
    "a first-class `crop_element` CLI command or binding surface",
    "Python, Node, MCP, or hosted crop API surfaces",
    "sandbox/subprocess backend expansion",
    "rendered-crop backend changes",
    "foreign-adapter crop coordinate hardening",
    "cross-platform rendered-crop byte identity claims",
]
EXPECTED_DIAGNOSTIC_MESSAGES = [
    "request_ref is missing",
    "request_ref does not match crop element request identity tuple",
    "descriptor must bind exactly one logical check id",
    "descriptor crop_ref does not match logical identity tuple",
    "descriptor text_sha256 does not match verification evidence",
    "request document_fingerprint does not match document fingerprint",
    "descriptor document_fingerprint does not match request",
    "request element_id does not match contract inventory case",
    "request element_id does not resolve in document",
    "resolved element is missing page",
    "descriptor page does not match resolved element",
    "resolved element is missing bbox",
    "resolved element bbox has non-positive area",
    "resolved element bbox exceeds page bounds",
    "descriptor bbox does not match resolved element",
    "request rendering does not match contract inventory case",
    "descriptor rendering_status does not match request",
]
EXPECTED_DIAGNOSTIC_CASES = [
    {
        "name": "request-ref-missing",
        "surface": "request_ref",
        "expected_diagnostics": ["request_ref is missing"],
    },
    {
        "name": "request-ref-identity-drift",
        "surface": "request_ref",
        "expected_diagnostics": [
            "request_ref does not match crop element request identity tuple"
        ],
    },
    {
        "name": "request-element-unresolved",
        "surface": "request_binding",
        "expected_diagnostics": [
            "request element_id does not match contract inventory case",
            "request element_id does not resolve in document",
        ],
    },
    {
        "name": "request-document-fingerprint-mismatch",
        "surface": "request_binding",
        "expected_diagnostics": [
            "request document_fingerprint does not match document fingerprint",
            "descriptor document_fingerprint does not match request",
        ],
    },
    {
        "name": "request-element-mismatch",
        "surface": "request_binding",
        "expected_diagnostics": [
            "request element_id does not match contract inventory case",
            "descriptor bbox does not match resolved element",
        ],
    },
    {
        "name": "descriptor-document-fingerprint-mismatch",
        "surface": "request_binding",
        "expected_diagnostics": [
            "descriptor document_fingerprint does not match request",
        ],
    },
    {
        "name": "descriptor-page-mismatch",
        "surface": "request_binding",
        "expected_diagnostics": [
            "descriptor page does not match resolved element",
        ],
    },
    {
        "name": "descriptor-bbox-mismatch",
        "surface": "request_binding",
        "expected_diagnostics": [
            "descriptor bbox does not match resolved element",
        ],
    },
    {
        "name": "request-rendering-mismatch",
        "surface": "request_binding",
        "expected_diagnostics": [
            "request rendering does not match contract inventory case",
        ],
    },
    {
        "name": "descriptor-rendering-status-mismatch",
        "surface": "request_binding",
        "expected_diagnostics": [
            "descriptor rendering_status does not match request",
        ],
    },
    {
        "name": "resolved-element-missing-page",
        "surface": "request_binding",
        "expected_diagnostics": ["resolved element is missing page"],
    },
    {
        "name": "resolved-element-missing-bbox",
        "surface": "request_binding",
        "expected_diagnostics": ["resolved element is missing bbox"],
    },
    {
        "name": "resolved-element-zero-area-bbox",
        "surface": "request_binding",
        "expected_diagnostics": ["resolved element bbox has non-positive area"],
    },
    {
        "name": "resolved-element-bbox-outside-page",
        "surface": "request_binding",
        "expected_diagnostics": ["resolved element bbox exceeds page bounds"],
    },
    {
        "name": "descriptor-crop-ref-identity-drift",
        "surface": "descriptor_ref",
        "expected_diagnostics": [
            "descriptor crop_ref does not match logical identity tuple"
        ],
    },
    {
        "name": "descriptor-text-sha256-mismatch",
        "surface": "descriptor_binding",
        "expected_diagnostics": [
            "descriptor text_sha256 does not match verification evidence"
        ],
    },
    {
        "name": "descriptor-ambiguous-checks",
        "surface": "descriptor_ref",
        "expected_diagnostics": ["descriptor must bind exactly one logical check id"],
    },
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


def pages_by_id(document: dict) -> dict[str, dict]:
    return {
        page["id"]: page
        for page in document["payload"]["pages"]
        if "id" in page
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


def descriptor_evidence_diagnostics(descriptor: dict, report: dict) -> list[str]:
    if "text_sha256" not in descriptor:
        return []

    report_checks = checks_by_id(report)
    for check_id in descriptor.get("check_ids", []):
        check = report_checks.get(check_id)
        if check is None:
            continue
        evidence_text = check.get("evidence", {}).get("text")
        if evidence_text is None:
            continue
        if descriptor["text_sha256"] != sha256_text(evidence_text):
            return ["descriptor text_sha256 does not match verification evidence"]

    return []


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

    page = None
    if "page" not in element:
        diagnostics.append("resolved element is missing page")
    else:
        page = pages_by_id(document).get(element["page"])
        if page is None:
            diagnostics.append("resolved element is missing page")
        elif descriptor["page"] != element["page"]:
            diagnostics.append("descriptor page does not match resolved element")

    if "bbox" not in element:
        diagnostics.append("resolved element is missing bbox")
    else:
        x0, y0, x1, y1 = element["bbox"]
        if x0 >= x1 or y0 >= y1:
            diagnostics.append("resolved element bbox has non-positive area")
        if page is not None and (
            x0 < 0 or y0 < 0 or x1 > page["width"] or y1 > page["height"]
        ):
            diagnostics.append("resolved element bbox exceeds page bounds")
        if descriptor["bbox"] != element["bbox"]:
            diagnostics.append("descriptor bbox does not match resolved element")

    if request["rendering"] != case["rendering_status"]:
        diagnostics.append("request rendering does not match contract inventory case")
    if descriptor["rendering_status"] != request["rendering"]:
        diagnostics.append("descriptor rendering_status does not match request")

    return diagnostics


def inventory_diagnostic_outputs(inventory: dict) -> dict[str, list[str]]:
    case = inventory["cases"][0]
    request = load_json(ROOT / case["request"])
    document = load_json(ROOT / case["document"])
    descriptor = load_json(ROOT / case["descriptor"])
    report = load_json(VERIFICATION_REPORT_EXAMPLE)

    missing_request_ref = dict(request)
    del missing_request_ref["request_ref"]

    stale_request_ref = dict(request, request_ref="request-" + "0" * 64)
    unknown_element_request = dict(request, element_id="e999999")
    stale_request = dict(request, document_fingerprint="sha256:" + "0" * 64)
    mismatched_element_request = dict(request, element_id="e000001")
    mismatched_rendering_case = dict(case, rendering_status="rendered")

    stale_descriptor_fingerprint = dict(
        descriptor,
        document_fingerprint="sha256:" + "0" * 64,
    )
    stale_descriptor_page = dict(descriptor, page="p999999")
    stale_descriptor_bbox = dict(descriptor, bbox=[0, 0, 1, 1])
    stale_descriptor_rendering = dict(descriptor, rendering_status="rendered")

    document_without_page = deepcopy(document)
    del elements_by_id(document_without_page)[request["element_id"]]["page"]

    document_without_bbox = deepcopy(document)
    del elements_by_id(document_without_bbox)[request["element_id"]]["bbox"]

    zero_area_bbox = [10, 20, 10, 30]
    document_with_zero_area_bbox = deepcopy(document)
    elements_by_id(document_with_zero_area_bbox)[request["element_id"]]["bbox"] = zero_area_bbox
    descriptor_with_zero_area_bbox = dict(descriptor, bbox=zero_area_bbox)

    outside_page_bbox = [-1, 0, 10, 10]
    document_with_outside_page_bbox = deepcopy(document)
    elements_by_id(document_with_outside_page_bbox)[request["element_id"]][
        "bbox"
    ] = outside_page_bbox
    descriptor_with_outside_page_bbox = dict(descriptor, bbox=outside_page_bbox)

    stale_crop_ref = dict(descriptor, crop_ref="crop-" + "0" * 64 + ".json")
    stale_text_sha256 = dict(descriptor, text_sha256="0" * 64)
    ambiguous_checks = dict(descriptor, check_ids=["v0001", "v0002"])

    return {
        "request-ref-missing": request_ref_drift_diagnostics(missing_request_ref),
        "request-ref-identity-drift": request_ref_drift_diagnostics(stale_request_ref),
        "request-element-unresolved": request_case_diagnostics(
            unknown_element_request,
            document,
            descriptor,
            case,
        ),
        "request-document-fingerprint-mismatch": request_case_diagnostics(
            stale_request,
            document,
            descriptor,
            case,
        ),
        "request-element-mismatch": request_case_diagnostics(
            mismatched_element_request,
            document,
            descriptor,
            case,
        ),
        "descriptor-document-fingerprint-mismatch": request_case_diagnostics(
            request,
            document,
            stale_descriptor_fingerprint,
            case,
        ),
        "descriptor-page-mismatch": request_case_diagnostics(
            request,
            document,
            stale_descriptor_page,
            case,
        ),
        "descriptor-bbox-mismatch": request_case_diagnostics(
            request,
            document,
            stale_descriptor_bbox,
            case,
        ),
        "request-rendering-mismatch": request_case_diagnostics(
            request,
            document,
            descriptor,
            mismatched_rendering_case,
        ),
        "descriptor-rendering-status-mismatch": request_case_diagnostics(
            request,
            document,
            stale_descriptor_rendering,
            case,
        ),
        "resolved-element-missing-page": request_case_diagnostics(
            request,
            document_without_page,
            descriptor,
            case,
        ),
        "resolved-element-missing-bbox": request_case_diagnostics(
            request,
            document_without_bbox,
            descriptor,
            case,
        ),
        "resolved-element-zero-area-bbox": request_case_diagnostics(
            request,
            document_with_zero_area_bbox,
            descriptor_with_zero_area_bbox,
            case,
        ),
        "resolved-element-bbox-outside-page": request_case_diagnostics(
            request,
            document_with_outside_page_bbox,
            descriptor_with_outside_page_bbox,
            case,
        ),
        "descriptor-crop-ref-identity-drift": crop_ref_drift_diagnostics(stale_crop_ref),
        "descriptor-text-sha256-mismatch": descriptor_evidence_diagnostics(
            stale_text_sha256,
            report,
        ),
        "descriptor-ambiguous-checks": crop_ref_drift_diagnostics(ambiguous_checks),
    }


class MilestoneDCropElementContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-crop-element-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-crop-element-contract")

        required = [
            "cargo test --locked -p ethos-core crop_element",
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
        self.assertIn("internal Rust resolver in `ethos-core::crop_element`", text)
        self.assertIn("descriptor-only crop descriptors", text)
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

    def test_contract_inventory_pins_fail_closed_diagnostics(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(EXPECTED_DIAGNOSTIC_CASES, inventory["diagnostic_cases"])

        diagnostic_names = [case["name"] for case in inventory["diagnostic_cases"]]
        self.assertEqual(len(diagnostic_names), len(set(diagnostic_names)))
        self.assertEqual(
            ["descriptor_binding", "descriptor_ref", "request_binding", "request_ref"],
            sorted({case["surface"] for case in inventory["diagnostic_cases"]}),
        )
        self.assertEqual(
            set(EXPECTED_DIAGNOSTIC_MESSAGES),
            {
                diagnostic
                for case in inventory["diagnostic_cases"]
                for diagnostic in case["expected_diagnostics"]
            },
        )

    def test_contract_inventory_diagnostics_match_current_helpers(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        actual_diagnostics = inventory_diagnostic_outputs(inventory)

        self.assertEqual(
            {case["name"] for case in inventory["diagnostic_cases"]},
            set(actual_diagnostics),
        )
        for case in inventory["diagnostic_cases"]:
            self.assertEqual(
                case["expected_diagnostics"],
                actual_diagnostics[case["name"]],
                case["name"],
            )

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

        zero_area_bbox = [10, 20, 10, 30]
        document_with_zero_area_bbox = deepcopy(document)
        elements_by_id(document_with_zero_area_bbox)[request["element_id"]][
            "bbox"
        ] = zero_area_bbox
        self.assertIn(
            "resolved element bbox has non-positive area",
            request_case_diagnostics(
                request,
                document_with_zero_area_bbox,
                dict(descriptor, bbox=zero_area_bbox),
                case,
            ),
        )

        outside_page_bbox = [-1, 0, 10, 10]
        document_with_outside_page_bbox = deepcopy(document)
        elements_by_id(document_with_outside_page_bbox)[request["element_id"]][
            "bbox"
        ] = outside_page_bbox
        self.assertIn(
            "resolved element bbox exceeds page bounds",
            request_case_diagnostics(
                request,
                document_with_outside_page_bbox,
                dict(descriptor, bbox=outside_page_bbox),
                case,
            ),
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
            self.assertEqual([], descriptor_evidence_diagnostics(descriptor, report))

    def test_descriptor_text_hash_fails_closed_on_evidence_mismatch(self) -> None:
        descriptor = load_json(ROOT / "schemas/examples/crop-descriptor.example.json")
        report = load_json(VERIFICATION_REPORT_EXAMPLE)

        stale_text_sha256 = dict(descriptor, text_sha256="0" * 64)
        self.assertIn(
            "descriptor text_sha256 does not match verification evidence",
            descriptor_evidence_diagnostics(stale_text_sha256, report),
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

    def test_crop_descriptor_rendering_metadata_schema_boundaries(self) -> None:
        schema = load_json(CROP_DESCRIPTOR_SCHEMA)
        descriptor = load_json(ROOT / "schemas/examples/crop-descriptor.example.json")

        self.assertEqual("descriptor_only", descriptor["rendering_status"])
        self.assertEqual([], schema_errors(schema, descriptor))

        conditional_fields = [
            "source_pdf_fingerprint",
            "rendered_ref",
            "rendered_format",
            "rendered_sha256",
            "rendered_width_px",
            "rendered_height_px",
        ]

        rendered_descriptor = dict(
            descriptor,
            rendering_status="rendered",
            source_pdf_fingerprint="sha256:" + "1" * 64,
            rendered_ref="crop-" + "2" * 64 + ".png",
            rendered_format="png",
            rendered_sha256="3" * 64,
            rendered_width_px=10,
            rendered_height_px=20,
        )
        self.assertEqual([], schema_errors(schema, rendered_descriptor))

        for field in conditional_fields:
            missing_field = dict(rendered_descriptor)
            del missing_field[field]
            self.assertNotEqual([], schema_errors(schema, missing_field), field)

        for field in conditional_fields:
            descriptor_only_with_rendered_metadata = dict(descriptor)
            descriptor_only_with_rendered_metadata[field] = rendered_descriptor[field]
            self.assertNotEqual(
                [],
                schema_errors(schema, descriptor_only_with_rendered_metadata),
                field,
            )

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

    def test_current_crop_carrier_uses_core_crop_ref_identity(self) -> None:
        text = VERIFY_SOURCE.read_text(encoding="utf-8")

        self.assertIn("ethos_core::crop_element::crop_element_crop_ref", text)
        self.assertNotIn('"version": "ethos.logical_crop_ref.v1"', text)

    def test_current_crop_carrier_serializes_core_descriptor_type(self) -> None:
        text = VERIFY_SOURCE.read_text(encoding="utf-8")

        self.assertIn("BTreeMap<String, CropElementDescriptor>", text)
        self.assertIn("serde_json::to_value(&descriptor)", text)
        self.assertNotIn("serde_json::Map::new()", text)

    def test_current_crop_carrier_has_fail_closed_descriptor_diagnostics(self) -> None:
        text = VERIFY_SOURCE.read_text(encoding="utf-8")

        for test_name in [
            "write_crop_artifacts_requires_document_fingerprint_for_descriptors",
            "write_crop_artifacts_rejects_crop_ref_collisions",
            "crop_artifact_path_rejects_unsafe_crop_refs",
        ]:
            self.assertIn(f"fn {test_name}()", text)
        for message in [
            "crop descriptor requires document fingerprint",
            "crop_ref collision while writing crop descriptors",
            "crop_ref is not a safe artifact filename",
        ]:
            self.assertIn(message, text)


if __name__ == "__main__":
    unittest.main()
