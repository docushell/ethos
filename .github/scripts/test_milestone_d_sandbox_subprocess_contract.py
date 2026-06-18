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
from pathlib import Path

from jsonschema import Draft202012Validator
from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestone-d-sandbox-subprocess-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/sandbox/sandbox_subprocess_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-sandbox-subprocess-contract.schema.json"
SANDBOX_REQUEST_SCHEMA = ROOT / "schemas/ethos-sandbox-subprocess-request.schema.json"
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
EXPECTED_DIAGNOSTIC_MESSAGES = [
    "request_ref is missing",
    "request_ref does not match sandbox subprocess request identity tuple",
    "request operation does not match command surface",
    "request diagnostics does not match inventory case",
    "request stderr policy does not match diagnostics mode",
    "request failure stdout policy is not empty",
    "request max_parse_ms does not match inventory case",
    "doc_parse request must bind explicit page selection",
    "fingerprint request must not carry page selection",
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
            "request_ref does not match sandbox subprocess request identity tuple"
        ],
    },
    {
        "name": "request-operation-mismatch",
        "surface": "request_policy",
        "expected_diagnostics": ["request operation does not match command surface"],
    },
    {
        "name": "request-diagnostics-mismatch",
        "surface": "request_policy",
        "expected_diagnostics": ["request diagnostics does not match inventory case"],
    },
    {
        "name": "request-stderr-policy-mismatch",
        "surface": "request_policy",
        "expected_diagnostics": [
            "request stderr policy does not match diagnostics mode"
        ],
    },
    {
        "name": "request-stdout-policy-mismatch",
        "surface": "request_policy",
        "expected_diagnostics": ["request failure stdout policy is not empty"],
    },
    {
        "name": "request-max-parse-ms-mismatch",
        "surface": "request_policy",
        "expected_diagnostics": ["request max_parse_ms does not match inventory case"],
    },
    {
        "name": "doc-parse-page-selection-missing",
        "surface": "request_policy",
        "expected_diagnostics": ["doc_parse request must bind explicit page selection"],
    },
    {
        "name": "fingerprint-page-selection-present",
        "surface": "request_policy",
        "expected_diagnostics": ["fingerprint request must not carry page selection"],
    },
]
EXPECTED_FAILURES = {
    "doc-parse-timeout": {
        "exit_code": 10,
        "error_code": "parse_timeout",
        "error_message": "parse exceeded max_parse_ms",
        "stdout": "empty",
        "diagnostics": False,
    },
    "fingerprint-timeout": {
        "exit_code": 10,
        "error_code": "parse_timeout",
        "error_message": "parse exceeded max_parse_ms",
        "stdout": "empty",
        "diagnostics": False,
    },
    "doc-parse-memory-limit": {
        "exit_code": 11,
        "error_code": "memory_limit_exceeded",
        "error_message": "parse exceeded memory limit",
        "stdout": "empty",
        "diagnostics": False,
    },
    "doc-parse-stable-error-envelope": {
        "exit_code": 3,
        "error_code": "invalid_pdf",
        "error_message": "input does not contain a PDF header",
        "stdout": "empty",
        "diagnostics": False,
    },
    "doc-parse-stderr-hidden-by-default": {
        "exit_code": 12,
        "error_code": "internal_error",
        "error_message": "pdfium worker failed",
        "stdout": "empty",
        "diagnostics": False,
    },
    "doc-parse-diagnostics-gated-stderr": {
        "exit_code": 12,
        "error_code": "internal_error",
        "error_message": "pdfium worker failed",
        "stdout": "empty",
        "diagnostics": True,
        "worker_exit_code": 101,
        "worker_stderr": "native pdfium stderr sentinel\nsecond line",
    },
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_c14n(value: dict) -> str:
    encoded = json.dumps(
        value,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def schema_errors(schema: dict, instance: dict) -> list:
    return sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )


def expected_operation(command_surface: str) -> str:
    return {
        "ethos doc parse": "doc_parse",
        "ethos fingerprint": "fingerprint",
    }[command_surface]


def expected_request_policy(case: dict) -> tuple[bool, str, int]:
    if case["name"] == "doc-parse-diagnostics-gated-stderr":
        return True, "stable_error_envelope_with_worker_stderr", 120_000
    if case["boundary"] == "max_parse_ms_timeout":
        return False, "stable_error_envelope", 25
    return False, "stable_error_envelope", 120_000


def logical_sandbox_request_ref(request: dict) -> str:
    identity = {
        "operation": request["operation"],
        "input": request["input"],
        "limits": request["limits"],
        "diagnostics": request["diagnostics"],
        "stdout_on_failure": request["stdout_on_failure"],
        "stderr_policy": request["stderr_policy"],
        "version": "ethos.sandbox_subprocess_request_ref.v1",
    }
    if "page_selection" in request:
        identity["page_selection"] = request["page_selection"]
    return "request-{}".format(sha256_c14n(identity))


def request_ref_drift_diagnostics(request: dict) -> list[str]:
    if "request_ref" not in request:
        return ["request_ref is missing"]
    if request["request_ref"] != logical_sandbox_request_ref(request):
        return ["request_ref does not match sandbox subprocess request identity tuple"]
    return []


def request_case_diagnostics(request: dict, case: dict) -> list[str]:
    diagnostics: list[str] = []
    want_diagnostics, want_stderr_policy, want_max_parse_ms = expected_request_policy(case)

    if request["operation"] != expected_operation(case["command_surface"]):
        diagnostics.append("request operation does not match command surface")
    if request["diagnostics"] != want_diagnostics:
        diagnostics.append("request diagnostics does not match inventory case")
    if request["stderr_policy"] != want_stderr_policy:
        diagnostics.append("request stderr policy does not match diagnostics mode")
    if request["stdout_on_failure"] != "empty":
        diagnostics.append("request failure stdout policy is not empty")
    if request["limits"]["max_parse_ms"] != want_max_parse_ms:
        diagnostics.append("request max_parse_ms does not match inventory case")

    if request["operation"] == "doc_parse" and request.get("page_selection") != "all":
        diagnostics.append("doc_parse request must bind explicit page selection")
    if request["operation"] == "fingerprint" and "page_selection" in request:
        diagnostics.append("fingerprint request must not carry page selection")

    return diagnostics


def contract_case_by_name(inventory: dict, name: str) -> dict:
    return next(case for case in inventory["cases"] if case["name"] == name)


def inventory_diagnostic_outputs(inventory: dict) -> dict[str, list[str]]:
    doc_parse_case = contract_case_by_name(inventory, "doc-parse-stable-error-envelope")
    timeout_case = contract_case_by_name(inventory, "doc-parse-timeout")
    diagnostics_case = contract_case_by_name(inventory, "doc-parse-diagnostics-gated-stderr")
    fingerprint_case = contract_case_by_name(inventory, "fingerprint-timeout")

    doc_parse_request = load_json(ROOT / doc_parse_case["request"])
    timeout_request = load_json(ROOT / timeout_case["request"])
    diagnostics_request = load_json(ROOT / diagnostics_case["request"])
    fingerprint_request = load_json(ROOT / fingerprint_case["request"])

    missing_request_ref = dict(doc_parse_request)
    del missing_request_ref["request_ref"]

    stale_request_ref = dict(doc_parse_request, request_ref="request-" + "0" * 64)

    wrong_operation = dict(timeout_request, operation="fingerprint")
    del wrong_operation["page_selection"]

    diagnostics_disabled = dict(diagnostics_request, diagnostics=False)
    wrong_stderr_policy = dict(
        diagnostics_request,
        stderr_policy="stable_error_envelope",
    )
    stdout_not_empty = dict(diagnostics_request, stdout_on_failure="not-empty")
    wrong_timeout = dict(diagnostics_request, limits={"max_parse_ms": 25})

    doc_parse_without_pages = dict(doc_parse_request)
    del doc_parse_without_pages["page_selection"]

    fingerprint_with_pages = dict(fingerprint_request, page_selection="all")

    return {
        "request-ref-missing": request_ref_drift_diagnostics(missing_request_ref),
        "request-ref-identity-drift": request_ref_drift_diagnostics(stale_request_ref),
        "request-operation-mismatch": request_case_diagnostics(
            wrong_operation,
            timeout_case,
        ),
        "request-diagnostics-mismatch": request_case_diagnostics(
            diagnostics_disabled,
            diagnostics_case,
        ),
        "request-stderr-policy-mismatch": request_case_diagnostics(
            wrong_stderr_policy,
            diagnostics_case,
        ),
        "request-stdout-policy-mismatch": request_case_diagnostics(
            stdout_not_empty,
            diagnostics_case,
        ),
        "request-max-parse-ms-mismatch": request_case_diagnostics(
            wrong_timeout,
            diagnostics_case,
        ),
        "doc-parse-page-selection-missing": request_case_diagnostics(
            doc_parse_without_pages,
            doc_parse_case,
        ),
        "fingerprint-page-selection-present": request_case_diagnostics(
            fingerprint_with_pages,
            fingerprint_case,
        ),
    }


def rust_test_body(source: str, test_name: str) -> str:
    match = re.search(
        rf"(?:#\[[^\n]+\]\n)*\s*#\[test\]\s*fn {re.escape(test_name)}\(\) \{{",
        source,
    )
    if match is None:
        raise AssertionError(f"missing Rust test body for {test_name}")

    depth = 1
    index = match.end()
    while index < len(source):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.end():index]
        index += 1

    raise AssertionError(f"unterminated Rust test body for {test_name}")


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
            "`schemas/ethos-sandbox-subprocess-request.schema.json`",
            "`schemas/examples/sandbox-subprocess-*.example.json`",
            "`request_ref`",
            "`ethos.sandbox_subprocess_request_ref.v1`",
            "request identity and request-policy diagnostics",
            "stable worker error envelopes are relayed",
            "non-envelope worker stderr is hidden by default",
            "explicit diagnostics",
            "request envelopes bind each failure case",
            "source-tree fixture validation pins expected diagnostics",
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

    def test_request_examples_validate_against_request_schema(self) -> None:
        schema = load_json(SANDBOX_REQUEST_SCHEMA)
        inventory = load_json(CONTRACT_INVENTORY)
        Draft202012Validator.check_schema(schema)

        request_paths = sorted({case["request"] for case in inventory["cases"]})
        self.assertGreaterEqual(len(request_paths), 3)

        for request_path in request_paths:
            request = load_json(ROOT / request_path)
            self.assertEqual([], schema_errors(schema, request), request_path)

        doc_parse_request = load_json(ROOT / "schemas/examples/sandbox-subprocess-doc-parse-request.example.json")
        doc_parse_without_request_ref = dict(doc_parse_request)
        del doc_parse_without_request_ref["request_ref"]
        self.assertNotEqual([], schema_errors(schema, doc_parse_without_request_ref))

        doc_parse_without_pages = dict(doc_parse_request)
        del doc_parse_without_pages["page_selection"]
        self.assertNotEqual([], schema_errors(schema, doc_parse_without_pages))

        fingerprint_request = load_json(ROOT / "schemas/examples/sandbox-subprocess-fingerprint-timeout-request.example.json")
        fingerprint_with_pages = dict(fingerprint_request, page_selection="all")
        self.assertNotEqual([], schema_errors(schema, fingerprint_with_pages))

        diagnostics_request = load_json(ROOT / "schemas/examples/sandbox-subprocess-doc-parse-diagnostics-request.example.json")
        diagnostics_without_stderr = dict(
            diagnostics_request,
            stderr_policy="stable_error_envelope",
        )
        self.assertNotEqual([], schema_errors(schema, diagnostics_without_stderr))

        doc_parse_with_stderr_without_diagnostics = dict(
            doc_parse_request,
            stderr_policy="stable_error_envelope_with_worker_stderr",
        )
        self.assertNotEqual(
            [],
            schema_errors(schema, doc_parse_with_stderr_without_diagnostics),
        )

    def test_contract_inventory_matches_existing_worker_tests(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        request_schema = load_json(SANDBOX_REQUEST_SCHEMA)
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
            request_path = ROOT / case["request"]
            self.assertTrue(request_path.is_file(), case["name"])
            request = load_json(request_path)
            self.assertEqual([], schema_errors(request_schema, request), case["name"])
            self.assertEqual([], request_ref_drift_diagnostics(request), case["name"])
            self.assertEqual([], request_case_diagnostics(request, case), case["name"])
            self.assertEqual(
                EXPECTED_FAILURES[case["name"]],
                case["expected_failure"],
                case["name"],
            )
            self.assertIn(f"fn {case['test_filter']}()", test_source, case["name"])

    def test_contract_inventory_pins_fail_closed_diagnostics(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(EXPECTED_DIAGNOSTIC_CASES, inventory["diagnostic_cases"])

        diagnostic_names = [case["name"] for case in inventory["diagnostic_cases"]]
        self.assertEqual(len(diagnostic_names), len(set(diagnostic_names)))
        self.assertEqual(
            ["request_policy", "request_ref"],
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

    def test_contract_inventory_case_order_is_deterministic(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(
            [
                "doc-parse-timeout",
                "fingerprint-timeout",
                "doc-parse-memory-limit",
                "doc-parse-stable-error-envelope",
                "doc-parse-stderr-hidden-by-default",
                "doc-parse-diagnostics-gated-stderr",
            ],
            [case["name"] for case in inventory["cases"]],
        )

    def test_request_ref_fails_closed_on_identity_drift(self) -> None:
        request = load_json(ROOT / "schemas/examples/sandbox-subprocess-doc-parse-request.example.json")

        expected_refs = {
            "schemas/examples/sandbox-subprocess-doc-parse-request.example.json":
                "request-5e6951ae8d44fcfa636bbf7cbd079414bcc6b9ca6cd1fd2037c10550014f94ac",
            "schemas/examples/sandbox-subprocess-doc-parse-timeout-request.example.json":
                "request-37ad10e9ab78491dfb4cb26268774f18d7d35b76cf226069d0ef16940f75350c",
            "schemas/examples/sandbox-subprocess-doc-parse-diagnostics-request.example.json":
                "request-590058131f2c0b21a8892f131802d0d52b3db08efabe8164e22f119b8d4c4e18",
            "schemas/examples/sandbox-subprocess-fingerprint-timeout-request.example.json":
                "request-da18cc9ac61abb6d4f11e20b72d1428b3e6a0d2c7036292f7dc5b2fb8c858ade",
        }
        for request_path, expected_ref in expected_refs.items():
            current = load_json(ROOT / request_path)
            self.assertEqual(expected_ref, current["request_ref"], request_path)
            self.assertEqual(expected_ref, logical_sandbox_request_ref(current), request_path)

        self.assertEqual(
            "request-5e6951ae8d44fcfa636bbf7cbd079414bcc6b9ca6cd1fd2037c10550014f94ac",
            logical_sandbox_request_ref(request),
        )
        self.assertEqual([], request_ref_drift_diagnostics(request))

        missing_request_ref = dict(request)
        del missing_request_ref["request_ref"]
        self.assertEqual(
            ["request_ref is missing"],
            request_ref_drift_diagnostics(missing_request_ref),
        )

        stale_request_ref = dict(request, request_ref="request-" + "0" * 64)
        self.assertEqual(
            ["request_ref does not match sandbox subprocess request identity tuple"],
            request_ref_drift_diagnostics(stale_request_ref),
        )

        stale_limit = dict(request, limits={"max_parse_ms": 25})
        self.assertNotEqual(request["request_ref"], logical_sandbox_request_ref(stale_limit))
        self.assertEqual(
            ["request_ref does not match sandbox subprocess request identity tuple"],
            request_ref_drift_diagnostics(stale_limit),
        )

        stale_stderr_policy = dict(
            request,
            stderr_policy="stable_error_envelope_with_worker_stderr",
        )
        self.assertNotEqual(
            request["request_ref"],
            logical_sandbox_request_ref(stale_stderr_policy),
        )
        self.assertEqual(
            ["request_ref does not match sandbox subprocess request identity tuple"],
            request_ref_drift_diagnostics(stale_stderr_policy),
        )

        stale_page_selection = dict(request, page_selection="1")
        self.assertNotEqual(
            request["request_ref"],
            logical_sandbox_request_ref(stale_page_selection),
        )
        self.assertEqual(
            ["request_ref does not match sandbox subprocess request identity tuple"],
            request_ref_drift_diagnostics(stale_page_selection),
        )

        stale_operation = dict(request, operation="fingerprint")
        del stale_operation["page_selection"]
        self.assertNotEqual(
            request["request_ref"],
            logical_sandbox_request_ref(stale_operation),
        )
        self.assertEqual(
            ["request_ref does not match sandbox subprocess request identity tuple"],
            request_ref_drift_diagnostics(stale_operation),
        )

    def test_request_binding_guard_fails_closed_on_policy_drift(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        case = next(
            case
            for case in inventory["cases"]
            if case["name"] == "doc-parse-diagnostics-gated-stderr"
        )
        request = load_json(ROOT / case["request"])

        wrong_operation = dict(request, operation="fingerprint")
        self.assertIn(
            "request operation does not match command surface",
            request_case_diagnostics(wrong_operation, case),
        )

        diagnostics_disabled = dict(request, diagnostics=False)
        self.assertIn(
            "request diagnostics does not match inventory case",
            request_case_diagnostics(diagnostics_disabled, case),
        )

        stdout_not_empty = dict(request, stdout_on_failure="not-empty")
        self.assertIn(
            "request failure stdout policy is not empty",
            request_case_diagnostics(stdout_not_empty, case),
        )

        wrong_timeout = dict(request, limits={"max_parse_ms": 25})
        self.assertIn(
            "request max_parse_ms does not match inventory case",
            request_case_diagnostics(wrong_timeout, case),
        )

    def test_inventory_worker_failure_tests_keep_stdout_empty(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        test_source = PDF_PARSE_TESTS.read_text(encoding="utf-8")

        for case in inventory["cases"]:
            body = rust_test_body(test_source, case["test_filter"])
            self.assertIn(
                "assert!(output.stdout.is_empty());",
                body,
                case["name"],
            )

    def test_inventory_worker_failure_tests_pin_expected_outcomes(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        test_source = PDF_PARSE_TESTS.read_text(encoding="utf-8")

        for case in inventory["cases"]:
            failure = case["expected_failure"]
            body = rust_test_body(test_source, case["test_filter"])
            self.assertIn(
                f"assert_eq!(output.status.code(), Some({failure['exit_code']}));",
                body,
                case["name"],
            )
            self.assertIn(failure["error_code"], body, case["name"])
            self.assertIn(failure["error_message"], body, case["name"])

            if failure["diagnostics"]:
                self.assertIn("--diagnostics", body, case["name"])
                self.assertIn(
                    f'error["diagnostics"]["pdfium_worker"]["exit_code"], {failure["worker_exit_code"]}',
                    body,
                    case["name"],
                )
                self.assertIn(
                    failure["worker_stderr"].replace("\n", "\\n"),
                    body,
                    case["name"],
                )
            else:
                self.assertNotIn('error["diagnostics"]', body, case["name"])

            if case["name"] == "doc-parse-stderr-hidden-by-default":
                self.assertIn(
                    r'{\"error\":{\"code\":\"internal_error\",\"message\":\"pdfium worker failed\"}}\n',
                    body,
                    case["name"],
                )

    def test_inventory_keeps_current_command_surfaces_narrow(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(
            {"ethos doc parse", "ethos fingerprint"},
            {case["command_surface"] for case in inventory["cases"]},
        )


if __name__ == "__main__":
    unittest.main()
