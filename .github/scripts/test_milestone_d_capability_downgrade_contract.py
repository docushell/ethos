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
CONTRACT = ROOT / "docs/milestone-d-capability-downgrade-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/verify/capability_downgrade_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-capability-downgrade-contract.schema.json"
VERIFICATION_REPORT_SCHEMA = ROOT / "schemas/ethos-verification-report.schema.json"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
EXPECTED_EXPLICIT_BLOCKERS = [
    "a new public command or binding surface",
    "Python, Node, MCP, or hosted capability surfaces",
    "adapter hardening beyond committed fixtures",
    "crop API implementation",
    "sandbox backend expansion",
    "semantic or arithmetic verification",
]
EXPECTED_CATEGORY_INVARIANTS = [
    {
        "category": "no-downgrade-control",
        "capability_limits": "absent",
        "report_warning": "absent",
        "blocked_checks": "absent",
        "non_grounded_checks": "absent",
        "all_evidence_grounded": True,
    },
    {
        "category": "report-only-downgrade",
        "capability_limits": "present",
        "report_warning": "capability_limited",
        "blocked_checks": "absent",
        "non_grounded_checks": "absent",
        "all_evidence_grounded": True,
    },
    {
        "category": "non-grounded-with-downgrade",
        "capability_limits": "present",
        "report_warning": "capability_limited",
        "blocked_checks": "absent",
        "non_grounded_checks": "present",
        "all_evidence_grounded": False,
    },
    {
        "category": "check-blocked-downgrade",
        "capability_limits": "present",
        "report_warning": "capability_limited",
        "blocked_checks": "present",
        "non_grounded_checks": "present",
        "all_evidence_grounded": False,
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
        r"This first `capability_downgrade` slice does not add:\n\n"
        r"(?P<bullets>(?:- .+\n)+)",
        contract_text(),
    )
    if match is None:
        raise AssertionError("missing capability_downgrade explicit blocker list")
    return [
        line.removeprefix("- ").rstrip(";.")
        for line in match.group("bullets").strip().splitlines()
    ]


def schema_errors(schema: dict, instance: dict) -> list:
    return sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )


def blocked_checks(report: dict) -> list[dict]:
    return [check for check in report["checks"] if check["status"] == "capability_blocked"]


def present_or_absent(value: bool) -> str:
    return "present" if value else "absent"


def category_invariant(case: dict, report: dict) -> dict:
    return {
        "category": case["category"],
        "capability_limits": present_or_absent(bool(report["capability_limits"])),
        "report_warning": (
            "capability_limited" if "capability_limited" in report["warnings"] else "absent"
        ),
        "blocked_checks": present_or_absent(bool(blocked_checks(report))),
        "non_grounded_checks": present_or_absent(
            any(check["status"] != "grounded" for check in report["checks"])
        ),
        "all_evidence_grounded": report["all_evidence_grounded"],
    }


class MilestoneDCapabilityDowngradeContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-capability-downgrade-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-capability-downgrade-contract")

        required = [
            "cargo test --locked -p ethos-verify capability",
            "cargo test --locked -p ethos-cli --test verify capability",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_capability_downgrade_contract.py",
            "git diff --check",
        ]
        for command in required:
            self.assertIn(command, block)

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("milestone-d-capability-downgrade-contract")

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
            self.assertIn("milestone-d-capability-downgrade-contract.md", text, path)

    def test_contract_defines_existing_carrier_not_new_surface(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("The current executable carrier remains `ethos verify`", text)
        self.assertIn("does not add a new public command", text)
        self.assertIn(
            "`capability_downgrade` names the existing contract between "
            "grounding-source capability declarations",
            text,
        )

    def test_contract_pins_supported_boundaries(self) -> None:
        text = normalized_contract_text()

        for required in [
            "`examples/verify/capability_downgrade_v1_contract.json`",
            "`capability_limits`",
            "`capability_limited`",
            "`capability_blocked`",
            "`missing_table_capability`",
            "category invariants",
            "native Ethos grounding",
            "OpenDataLoader-style grounding",
            "source-tree fixture validation pins the category invariants",
            "`make milestone-d-capability-downgrade-contract PYTHON=<jsonschema-venv>/bin/python`",
        ]:
            self.assertIn(required, text)
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, contract_explicit_blockers())

    def test_contract_inventory_schema_validates_inventory(self) -> None:
        schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        inventory = load_json(CONTRACT_INVENTORY)

        Draft202012Validator.check_schema(schema)
        self.assertEqual([], schema_errors(schema, inventory))

    def test_contract_inventory_schema_enums_match_report_schema(self) -> None:
        inventory_schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        report_schema = load_json(VERIFICATION_REPORT_SCHEMA)

        self.assertEqual(
            sorted(inventory_schema["$defs"]["capability_limit"]["enum"]),
            sorted(report_schema["properties"]["capability_limits"]["items"]["enum"]),
        )
        self.assertEqual(
            sorted(inventory_schema["$defs"]["check_status"]["enum"]),
            sorted(
                report_schema["properties"]["checks"]["items"]["properties"]["status"]["enum"]
            ),
        )
        self.assertEqual(
            sorted(inventory_schema["$defs"]["check_reason"]["enum"]),
            sorted(report_schema["$defs"]["check_reason"]["enum"]),
        )
        report_warnings = set(report_schema["$defs"]["warning_code"]["enum"])
        self.assertEqual(["capability_limited"], inventory_schema["$defs"]["report_warning"]["enum"])
        self.assertIn("capability_limited", report_warnings)

    def test_contract_inventory_case_order_is_deterministic(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(
            [
                "native-grounded",
                "opendataloader-grounded",
                "opendataloader-not-found",
                "opendataloader-capability-limited",
                "real-opendataloader-grounded",
                "real-opendataloader-ungrounded",
            ],
            [case["name"] for case in inventory["report_cases"]],
        )
        self.assertEqual(
            {
                "no-downgrade-control",
                "report-only-downgrade",
                "non-grounded-with-downgrade",
                "check-blocked-downgrade",
            },
            {case["category"] for case in inventory["report_cases"]},
        )
        self.assertEqual(
            [
                "no-downgrade-control",
                "report-only-downgrade",
                "non-grounded-with-downgrade",
                "check-blocked-downgrade",
            ],
            [case["category"] for case in inventory["category_invariants"]],
        )

    def test_contract_inventory_matches_report_goldens(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "capability_downgrade.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "ethos verify")
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])

        case_names = [case["name"] for case in inventory["report_cases"]]
        self.assertEqual(len(case_names), len(set(case_names)))

        for case in inventory["report_cases"]:
            report = load_json(ROOT / case["golden"])
            blocked = blocked_checks(report)

            self.assertEqual(
                case["all_evidence_grounded"],
                report["all_evidence_grounded"],
                case["name"],
            )
            self.assertEqual(
                case["expected_statuses"],
                [check["status"] for check in report["checks"]],
                case["name"],
            )
            self.assertEqual(
                case["expected_reasons"],
                [
                    check["reason"]
                    for check in report["checks"]
                    if check.get("reason") is not None
                ],
                case["name"],
            )
            self.assertEqual(
                case["expected_capability_limits"],
                report["capability_limits"],
                case["name"],
            )
            self.assertEqual(
                case["expected_report_warnings"],
                report["warnings"],
                case["name"],
            )
            self.assertEqual(
                case["expected_blocked_check_ids"],
                [check["id"] for check in blocked],
                case["name"],
            )
            self.assertEqual(
                case["expected_blocked_reasons"],
                [check["reason"] for check in blocked],
                case["name"],
            )

    def test_contract_inventory_pins_category_invariants(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(EXPECTED_CATEGORY_INVARIANTS, inventory["category_invariants"])

        categories = [case["category"] for case in inventory["category_invariants"]]
        self.assertEqual(len(categories), len(set(categories)))
        self.assertEqual(
            {case["category"] for case in inventory["report_cases"]},
            set(categories),
        )

    def test_category_invariants_match_report_goldens(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        expected_by_category = {
            case["category"]: case for case in inventory["category_invariants"]
        }
        seen: dict[str, dict] = {}

        for case in inventory["report_cases"]:
            report = load_json(ROOT / case["golden"])
            actual = category_invariant(case, report)
            self.assertEqual(expected_by_category[case["category"]], actual, case["name"])

            previous = seen.setdefault(case["category"], actual)
            self.assertEqual(previous, actual, case["name"])

    def test_capability_warning_matches_structured_limits(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        for case in inventory["report_cases"]:
            report = load_json(ROOT / case["golden"])
            has_limits = bool(report["capability_limits"])

            self.assertEqual(
                has_limits,
                "capability_limited" in report["warnings"],
                case["name"],
            )
            for check in blocked_checks(report):
                self.assertIn("capability_limited", check["warnings"], case["name"])

    def test_check_level_capability_warnings_stay_blocked_only(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        for case in inventory["report_cases"]:
            report = load_json(ROOT / case["golden"])

            for check in report["checks"]:
                label = f"{case['name']} {check['id']}"
                if check["status"] == "capability_blocked":
                    self.assertEqual(["capability_limited"], check["warnings"], label)
                else:
                    self.assertEqual([], check["warnings"], label)

    def test_capability_blocked_checks_do_not_count_as_grounded(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        for case in inventory["report_cases"]:
            report = load_json(ROOT / case["golden"])
            if blocked_checks(report):
                self.assertFalse(report["all_evidence_grounded"], case["name"])


if __name__ == "__main__":
    unittest.main()
