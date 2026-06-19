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

from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestone-d-verify-citations-contract.md"
VERIFY_CASES = ROOT / "examples/verify/cases.json"
CONTRACT_INVENTORY = ROOT / "examples/verify/verify_citations_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-verify-citations-contract.schema.json"
VERIFICATION_CONFIG_EXAMPLE = ROOT / "schemas/examples/verification-config.example.json"
VERIFICATION_REPORT_SCHEMA = ROOT / "schemas/ethos-verification-report.schema.json"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
EXPECTED_EXPLICIT_BLOCKERS = [
    "a new `verify_citations` CLI alias",
    "Python, Node, MCP, or hosted API surfaces",
    "broad foreign-adapter hardening beyond existing fixtures",
    "crop API implementation",
    "sandbox/subprocess backend expansion",
    "semantic or arithmetic verification",
]
EXPECTED_USAGE_DIAGNOSTIC_CASES = [
    {
        "name": "invalid-table-cell-citation",
        "exit_code": 2,
        "stdout": "empty",
        "stderr_contains": "table_cell citation must include table_id and cell",
    },
    {
        "name": "invalid-bbox-citation",
        "exit_code": 2,
        "stdout": "empty",
        "stderr_contains": "citation bbox requires page unless another target locator is present",
    },
    {
        "name": "opendataloader-malformed-bbox-input",
        "exit_code": 2,
        "stdout": "empty",
        "stderr_contains": "opendataloader-json adapter: bbox is malformed (x0>x1 or y0>y1)",
    },
    {
        "name": "opendataloader-zero-area-bbox-input",
        "exit_code": 2,
        "stdout": "empty",
        "stderr_contains": "opendataloader-json adapter: bbox must have positive area",
    },
    {
        "name": "opendataloader-unknown-page-input",
        "exit_code": 2,
        "stdout": "empty",
        "stderr_contains": "opendataloader-json adapter: element.page references unknown page",
    },
]
REQUIRED_RESOLVED_EVIDENCE_FIELDS = {"bbox", "page"}
TEXT_EVIDENCE_CLAIM_KINDS = {"quote", "table_cell", "value"}
UNRESOLVED_OR_BLOCKED_REASONS = {
    "capability_blocked": "missing_table_capability",
    "not_found": "element_not_found",
    "stale": "stale_fingerprint",
    "unsupported_claim_kind": "unsupported_claim_kind",
}


def contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def normalized_contract_text() -> str:
    return re.sub(r"\s+", " ", contract_text())


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


def contract_explicit_blockers() -> list[str]:
    match = re.search(
        r"## Explicit Blockers For This Slice\n\n"
        r"This first D slice does not add:\n\n"
        r"(?P<bullets>(?:- .+\n)+)",
        contract_text(),
    )
    if match is None:
        raise AssertionError("missing explicit blocker list")
    return [
        line.removeprefix("- ").rstrip(";.")
        for line in match.group("bullets").strip().splitlines()
    ]


def case_names(items: list[dict]) -> list[str]:
    return [item["name"] for item in items]


def assert_unique(testcase: unittest.TestCase, values: list[str], label: str) -> None:
    testcase.assertEqual(
        len(values),
        len(set(values)),
        f"{label} contains duplicate names: {values}",
    )


def assert_disjoint_case_groups(
    testcase: unittest.TestCase, groups: dict[str, list[str]], label: str
) -> None:
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for group_name, names in groups.items():
        for name in names:
            if name in seen:
                duplicates.append(f"{name} appears in both {seen[name]} and {group_name}")
            else:
                seen[name] = group_name
    testcase.assertEqual([], duplicates, f"{label} case names overlap across groups")


def citation_claims(citations) -> list[dict]:
    if isinstance(citations, list):
        return citations
    return citations["claims"]


def citation_document_fingerprint(citations) -> str | None:
    if isinstance(citations, list):
        return None
    return citations.get("document_fingerprint")


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


def expected_usage_diagnostic_cases(cases: dict) -> list[dict]:
    return [
        {
            "name": case["name"],
            "exit_code": 2,
            "stdout": "empty",
            "stderr_contains": case["stderr_contains"],
        }
        for case in cases["usage_error_cases"]
    ]


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

        usage_diagnostic_names = case_names(inventory["usage_diagnostic_cases"])
        assert_unique(
            self,
            usage_diagnostic_names,
            "contract inventory usage_diagnostic_cases",
        )
        self.assertEqual(usage_case_names, usage_diagnostic_names)
        self.assertEqual(
            EXPECTED_USAGE_DIAGNOSTIC_CASES,
            inventory["usage_diagnostic_cases"],
        )
        self.assertEqual(
            expected_usage_diagnostic_cases(cases),
            inventory["usage_diagnostic_cases"],
        )

        summary_case_names = case_names(cases["summary_cases"])
        assert_unique(self, summary_case_names, "cases.json summary_cases")
        self.assertEqual(inventory["summary_cases"], summary_case_names)

    def test_contract_inventory_case_names_are_disjoint_across_lanes(self) -> None:
        cases = load_json(VERIFY_CASES)
        inventory = load_json(CONTRACT_INVENTORY)

        assert_disjoint_case_groups(
            self,
            {
                "cases.json report_cases": case_names(cases["report_cases"]),
                "cases.json usage_error_cases": case_names(cases["usage_error_cases"]),
                "cases.json summary_cases": case_names(cases["summary_cases"]),
            },
            "examples/verify/cases.json",
        )
        assert_disjoint_case_groups(
            self,
            {
                "contract inventory report_cases": case_names(inventory["report_cases"]),
                "contract inventory usage_error_cases": inventory["usage_error_cases"],
                "contract inventory summary_cases": inventory["summary_cases"],
            },
            "verify_citations v1 contract inventory",
        )

    def test_contract_inventory_matches_report_goldens(self) -> None:
        cases = load_json(VERIFY_CASES)
        inventory = load_json(CONTRACT_INVENTORY)
        inventory_schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        case_by_name = {case["name"]: case for case in cases["report_cases"]}
        allowed_categories = set(
            inventory_schema["properties"]["report_cases"]["items"]["properties"][
                "category"
            ]["enum"]
        )
        seen_categories = set()
        derived_categories = set()

        for contract_case in inventory["report_cases"]:
            self.assertIn(contract_case["category"], allowed_categories)
            seen_categories.add(contract_case["category"])
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
            category = derived_category(report)
            derived_categories.add(category)
            self.assertEqual(
                contract_case["category"],
                category,
                contract_case["name"],
            )
        self.assertEqual(allowed_categories, seen_categories)
        self.assertEqual(allowed_categories, derived_categories)

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

    def test_report_goldens_bind_evidence_to_resolved_target_statuses(self) -> None:
        cases = load_json(VERIFY_CASES)

        for case in cases["report_cases"]:
            report = load_json(ROOT / case["golden"])
            for check in report["checks"]:
                label = f"{case['name']} {check['id']}"
                status = check["status"]

                if status == "grounded":
                    self.assertNotIn("reason", check, label)
                    self.assertNotEqual("none", check["match_method"], label)
                    self.assertLessEqual(
                        REQUIRED_RESOLVED_EVIDENCE_FIELDS,
                        set(check["evidence"]),
                        label,
                    )
                    if check["claim"]["kind"] in TEXT_EVIDENCE_CLAIM_KINDS:
                        self.assertIn("text", check["evidence"], label)
                    continue

                if status == "mismatch":
                    self.assertEqual("text_mismatch", check["reason"], label)
                    self.assertNotEqual("none", check["match_method"], label)
                    self.assertLessEqual(
                        REQUIRED_RESOLVED_EVIDENCE_FIELDS,
                        set(check["evidence"]),
                        label,
                    )
                    if check["claim"]["kind"] in TEXT_EVIDENCE_CLAIM_KINDS:
                        self.assertIn("text", check["evidence"], label)
                    continue

                self.assertIn(status, UNRESOLVED_OR_BLOCKED_REASONS, label)
                self.assertEqual(UNRESOLVED_OR_BLOCKED_REASONS[status], check["reason"], label)
                self.assertEqual("none", check["match_method"], label)
                self.assertNotIn("evidence", check, label)

    def test_report_goldens_bind_fingerprint_capability_to_freshness_policy(self) -> None:
        cases = load_json(VERIFY_CASES)

        for case in cases["report_cases"]:
            input_document = load_json(ROOT / case["input"])
            citations = load_json(ROOT / case["citations"])
            report = load_json(ROOT / case["golden"])
            supports_fingerprint = report["grounding"]["capabilities"]["fingerprint"]
            citation_fingerprint = citation_document_fingerprint(citations)

            self.assertEqual(
                supports_fingerprint,
                "document_fingerprint" in report,
                case["name"],
            )
            if supports_fingerprint:
                self.assertEqual(
                    input_document["fingerprint"],
                    report["document_fingerprint"],
                    case["name"],
                )
                self.assertNotIn("missing_fingerprint", report["capability_limits"])
                if citation_fingerprint is not None:
                    self.assertEqual(
                        citation_fingerprint != report["document_fingerprint"],
                        report["fingerprint_stale"],
                        case["name"],
                    )
                continue

            self.assertNotIn("document_fingerprint", report, case["name"])
            self.assertIn("missing_fingerprint", report["capability_limits"], case["name"])
            self.assertFalse(report["fingerprint_stale"], case["name"])

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

    def test_report_goldens_use_default_verification_config_hash(self) -> None:
        cases = load_json(VERIFY_CASES)
        expected_hash = sha256_c14n(load_json(VERIFICATION_CONFIG_EXAMPLE))

        for case in cases["report_cases"]:
            report = load_json(ROOT / case["golden"])
            self.assertEqual(
                expected_hash,
                report["verification_config_sha256"],
                case["name"],
            )

    def test_default_contract_goldens_do_not_emit_crop_refs(self) -> None:
        cases = load_json(VERIFY_CASES)

        for case in cases["report_cases"]:
            report = load_json(ROOT / case["golden"])
            for check in report["checks"]:
                evidence = check.get("evidence") or {}
                self.assertNotIn("crop_ref", evidence, case["name"])

    def test_contract_inventory_keeps_blockers_explicit(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, contract_explicit_blockers())
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])


if __name__ == "__main__":
    unittest.main()
