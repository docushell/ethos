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

from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestone-d-verify-citations-contract.md"
VERIFY_CASES = ROOT / "examples/verify/cases.json"
CONTRACT_INVENTORY = ROOT / "examples/verify/verify_citations_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-verify-citations-contract.schema.json"
VERIFICATION_REPORT_SCHEMA = ROOT / "schemas/ethos-verification-report.schema.json"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"


def contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def normalized_contract_text() -> str:
    return re.sub(r"\s+", " ", contract_text())


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def case_names(items: list[dict]) -> list[str]:
    return [item["name"] for item in items]


def assert_unique(testcase: unittest.TestCase, values: list[str], label: str) -> None:
    testcase.assertEqual(
        len(values),
        len(set(values)),
        f"{label} contains duplicate names: {values}",
    )


def citation_claims(citations) -> list[dict]:
    if isinstance(citations, list):
        return citations
    return citations["claims"]


def derived_category(report: dict) -> str:
    statuses = [check["status"] for check in report["checks"]]
    warnings = set(report["warnings"])
    capability_limits = report["capability_limits"]

    if report["fingerprint_stale"] or "stale" in statuses:
        return "stale-fingerprint"
    if report["unsupported_claim_kinds"] or "unsupported_claim_kind" in statuses:
        return "unsupported-non-v1"
    if "capability_blocked" in statuses:
        return "capability-blocked"
    if report["all_evidence_grounded"]:
        if "capability_limited" in warnings or capability_limits:
            return "grounded-with-capability-warning"
        return "grounded"
    return "diagnostic-non-grounded"


class MilestoneDVerifyCitationsContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-verify-citations-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-verify-citations-contract")

        required = [
            "cargo test --locked -p ethos-cli --test verify",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_verify_citations_contract.py",
            "git diff --check",
        ]
        for command in required:
            self.assertIn(command, block)

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("milestone-d-verify-citations-contract")

        for out_of_scope in [
            "verify-alpha",
            "rag-chunk-alpha",
            "security-report-alpha",
            "verify-rendered-crops",
            "compare-rendered-crops",
            "layout-evaluator-alpha",
            "python-surface-test",
            "release-",
            "third-party-license-manifest",
        ]:
            self.assertNotIn(out_of_scope, block)

    def test_contract_is_linked_from_status_docs(self) -> None:
        for path in [ROADMAP, EXECUTION_STATUS, SCHEMAS_README]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("milestone-d-verify-citations-contract.md", text, path)

    def test_contract_defines_existing_carrier_not_new_surface(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("The current executable carrier remains `ethos verify`", text)
        self.assertIn("does not create a new public command, binding, or hosted surface", text)
        self.assertIn(
            "`verify_citations` names the contract between citation input, grounding source, "
            "verification config, and verification report",
            text,
        )

    def test_contract_pins_v1_supported_and_blocked_scope(self) -> None:
        text = normalized_contract_text()

        for kind in ["`quote`", "`value`", "`presence`", "`table_cell`"]:
            self.assertIn(kind, text)
        self.assertIn("`region` and `other` remain explicit unsupported non-v1 inputs", text)

        for blocker in [
            "a new `verify_citations` CLI alias",
            "Python, Node, MCP, or hosted API surfaces",
            "crop API implementation",
            "sandbox/subprocess backend expansion",
            "semantic or arithmetic verification",
        ]:
            self.assertIn(blocker, text)

    def test_contract_names_fixture_backed_validation(self) -> None:
        text = normalized_contract_text()

        self.assertIn("`schemas/examples/citations.example.json`", text)
        self.assertIn("`schemas/examples/verification-report.example.json`", text)
        self.assertIn("`examples/verify/verify_citations_v1_contract.json`", text)
        self.assertIn("echoes the example claims in input order", text)
        self.assertIn("`all_evidence_grounded` is true only under the invariant", text)
        self.assertIn(
            "`make milestone-d-verify-citations-contract PYTHON=<jsonschema-venv>/bin/python`",
            text,
        )

    def test_contract_inventory_schema_check_enums_match_report_schema(self) -> None:
        inventory_schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        report_schema = load_json(VERIFICATION_REPORT_SCHEMA)

        self.assertEqual(
            {
                "check_status": sorted(
                    inventory_schema["$defs"]["check_status"]["enum"]
                ),
                "check_reason": sorted(
                    inventory_schema["$defs"]["check_reason"]["enum"]
                ),
            },
            {
                "check_status": sorted(
                    report_schema["properties"]["checks"]["items"]["properties"][
                        "status"
                    ]["enum"]
                ),
                "check_reason": sorted(report_schema["$defs"]["check_reason"]["enum"]),
            },
        )

    def test_contract_inventory_matches_executable_case_inventory(self) -> None:
        cases = load_json(VERIFY_CASES)
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "verify_citations.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "ethos verify")

        report_case_names = case_names(cases["report_cases"])
        inventory_report_names = case_names(inventory["report_cases"])
        assert_unique(self, report_case_names, "cases.json report_cases")
        assert_unique(self, inventory_report_names, "contract inventory report_cases")
        self.assertEqual(inventory_report_names, report_case_names)

        usage_case_names = case_names(cases["usage_error_cases"])
        assert_unique(self, usage_case_names, "cases.json usage_error_cases")
        self.assertEqual(inventory["usage_error_cases"], usage_case_names)

        summary_case_names = case_names(cases["summary_cases"])
        assert_unique(self, summary_case_names, "cases.json summary_cases")
        self.assertEqual(inventory["summary_cases"], summary_case_names)

    def test_contract_inventory_matches_report_goldens(self) -> None:
        cases = load_json(VERIFY_CASES)
        inventory = load_json(CONTRACT_INVENTORY)
        case_by_name = {case["name"]: case for case in cases["report_cases"]}

        allowed_categories = {
            "grounded",
            "grounded-with-capability-warning",
            "unsupported-non-v1",
            "diagnostic-non-grounded",
            "stale-fingerprint",
            "capability-blocked",
        }

        for contract_case in inventory["report_cases"]:
            self.assertIn(contract_case["category"], allowed_categories)
            report = load_json(ROOT / case_by_name[contract_case["name"]]["golden"])
            statuses = [check["status"] for check in report["checks"]]
            reasons = [
                check["reason"]
                for check in report["checks"]
                if check.get("reason") is not None
            ]

            self.assertEqual(
                contract_case["all_evidence_grounded"],
                report["all_evidence_grounded"],
                contract_case["name"],
            )
            self.assertEqual(contract_case["statuses"], statuses, contract_case["name"])
            self.assertEqual(contract_case["reasons"], reasons, contract_case["name"])
            self.assertEqual(
                contract_case["category"],
                derived_category(report),
                contract_case["name"],
            )

    def test_report_goldens_echo_citation_inputs_in_order(self) -> None:
        cases = load_json(VERIFY_CASES)

        for case in cases["report_cases"]:
            citations = load_json(ROOT / case["citations"])
            report = load_json(ROOT / case["golden"])
            claims = citation_claims(citations)

            self.assertEqual(len(report["checks"]), len(claims), case["name"])
            for index, (check, claim) in enumerate(zip(report["checks"], claims), 1):
                self.assertEqual(check["id"], f"v{index:04}", case["name"])
                self.assertEqual(check["claim"], claim, case["name"])

    def test_report_goldens_keep_current_v1_literal_checks_non_semantic(self) -> None:
        cases = load_json(VERIFY_CASES)

        for case in cases["report_cases"]:
            report = load_json(ROOT / case["golden"])
            checks = report["checks"]
            self.assertGreater(len(checks), 0, case["name"])
            for check in checks:
                self.assertFalse(check["semantic_unverified"], case["name"])
            expected_gate = (
                all(check["status"] == "grounded" for check in checks)
                and not any(check["semantic_unverified"] for check in checks)
                and report["unsupported_claim_kinds"] == []
                and report["fingerprint_stale"] is False
            )
            self.assertEqual(
                report["all_evidence_grounded"],
                expected_gate,
                case["name"],
            )

    def test_contract_inventory_keeps_blockers_explicit(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        blockers = " ".join(inventory["explicit_blockers"])

        for expected in [
            "new verify_citations CLI alias",
            "Python Node MCP or hosted API surfaces",
            "broad foreign-adapter hardening beyond existing fixtures",
            "crop API implementation",
            "sandbox subprocess backend expansion",
            "semantic or arithmetic verification",
        ]:
            self.assertIn(expected, blockers)


if __name__ == "__main__":
    unittest.main()
