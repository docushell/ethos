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
CONTRACT = ROOT / "docs/milestone-d-claim-kind-boundary-contract.md"
CONTRACT_INVENTORY = ROOT / "examples/verify/claim_kind_boundary_v1_contract.json"
CONTRACT_INVENTORY_SCHEMA = ROOT / "schemas/ethos-claim-kind-boundary-contract.schema.json"
CITATIONS_SCHEMA = ROOT / "schemas/ethos-citations.schema.json"
VERIFICATION_CONFIG_SCHEMA = ROOT / "schemas/ethos-verification-config.schema.json"
VERIFICATION_REPORT_SCHEMA = ROOT / "schemas/ethos-verification-report.schema.json"
VERIFY_CITATIONS_INVENTORY = ROOT / "examples/verify/verify_citations_v1_contract.json"
VERIFY_CASES = ROOT / "examples/verify/cases.json"
RUST_VERIFY_TYPES = ROOT / "crates/ethos-core/src/verify_types.rs"
RUST_VERIFY_LIB = ROOT / "crates/ethos-verify/src/lib.rs"
RUST_CLI_VERIFY = ROOT / "crates/ethos-cli/src/cmd/verify.rs"
CLI_VERIFY_TESTS = ROOT / "crates/ethos-cli/tests/verify.rs"
ROADMAP = ROOT / "docs/roadmap.md"
EXECUTION_STATUS = ROOT / "docs/execution-status.md"
SCHEMAS_README = ROOT / "schemas/README.md"
EXPECTED_SUPPORTED = ["quote", "value", "presence", "table_cell"]
EXPECTED_UNSUPPORTED = ["region", "other"]
EXPECTED_EXPLICIT_BLOCKERS = [
    "new claim-kind support",
    "semantic, visual, arithmetic, or cross-region verification",
    "a new command or binding surface",
    "crop API changes",
    "sandbox backend changes",
    "foreign-adapter broadening beyond committed fixtures",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def normalized_contract_text() -> str:
    return re.sub(r"\s+", " ", contract_text())


def schema_errors(schema: dict, instance: dict) -> list:
    return sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )


def contract_explicit_blockers() -> list[str]:
    match = re.search(
        r"## Explicit Blockers For This Slice\n\n"
        r"This first `claim_kind_boundary` slice does not add:\n\n"
        r"(?P<bullets>(?:- .+\n)+)",
        contract_text(),
    )
    if match is None:
        raise AssertionError("missing claim_kind_boundary explicit blocker list")
    return [
        line.removeprefix("- ").rstrip(";.")
        for line in match.group("bullets").strip().splitlines()
    ]


def citation_claims(citations: dict) -> list[dict]:
    return citations["claims"]


class MilestoneDClaimKindBoundaryContractTests(unittest.TestCase):
    def test_target_is_declared_phony(self) -> None:
        text = makefile_text()

        self.assertIn(".PHONY:", text)
        self.assertIn("milestone-d-claim-kind-boundary-contract", text)

    def test_target_composes_contract_gates(self) -> None:
        block = target_block("milestone-d-claim-kind-boundary-contract")

        required = [
            "cargo test --locked -p ethos-verify claim_kind",
            "cargo test --locked -p ethos-cli --test verify invalid_config_constraints_are_usage_errors",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_execution_status.py",
            "$(PYTHON) .github/scripts/test_roadmap_status.py",
            "$(PYTHON) .github/scripts/test_milestone_d_claim_kind_boundary_contract.py",
            "git diff --check",
        ]
        self.assertEqual(required, [line.strip() for line in block.splitlines() if line.strip()])

    def test_target_stays_contract_scoped(self) -> None:
        block = target_block("milestone-d-claim-kind-boundary-contract")

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
            self.assertIn("milestone-d-claim-kind-boundary-contract.md", text, path)

    def test_contract_defines_boundary_not_new_behavior(self) -> None:
        text = normalized_contract_text()

        self.assertIn("source-only pre-alpha contract work", text)
        self.assertIn("The current executable carrier remains `ethos verify`", text)
        self.assertIn("does not add new claim-kind support", text)
        self.assertIn("future claim-kind expansion from silently changing", text)
        self.assertIn("does not add or broaden verification behavior", text)
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, contract_explicit_blockers())

    def test_contract_inventory_schema_validates_inventory(self) -> None:
        schema = load_json(CONTRACT_INVENTORY_SCHEMA)
        inventory = load_json(CONTRACT_INVENTORY)

        Draft202012Validator.check_schema(schema)
        self.assertEqual([], schema_errors(schema, inventory))

    def test_inventory_binds_current_claim_kind_sets(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)

        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["contract"], "claim_kind_boundary.v1")
        self.assertEqual(inventory["status"], "source-only-pre-alpha")
        self.assertEqual(inventory["carrier"], "ethos verify")
        self.assertEqual(EXPECTED_SUPPORTED, inventory["supported_claim_kinds"])
        self.assertEqual(EXPECTED_UNSUPPORTED, inventory["unsupported_claim_kinds"])
        self.assertEqual(EXPECTED_EXPLICIT_BLOCKERS, inventory["explicit_blockers"])

    def test_schema_boundaries_match_inventory(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        citations_schema = load_json(CITATIONS_SCHEMA)
        config_schema = load_json(VERIFICATION_CONFIG_SCHEMA)
        report_schema = load_json(VERIFICATION_REPORT_SCHEMA)

        citation_kinds = citations_schema["$defs"]["claim"]["properties"]["kind"]["enum"]
        config_kinds = config_schema["properties"]["claim_kinds"]["items"]["enum"]
        report_kinds = (
            report_schema["properties"]["checks"]["items"]["properties"]["claim"]["properties"]["kind"]["enum"]
        )

        self.assertEqual(EXPECTED_SUPPORTED + EXPECTED_UNSUPPORTED, citation_kinds)
        self.assertEqual(EXPECTED_SUPPORTED, config_kinds)
        self.assertEqual(EXPECTED_SUPPORTED + EXPECTED_UNSUPPORTED, report_kinds)
        self.assertEqual(EXPECTED_SUPPORTED, inventory["config_boundary"]["accepted_claim_kinds"])
        self.assertEqual(EXPECTED_UNSUPPORTED, inventory["config_boundary"]["rejected_claim_kinds"])
        self.assertEqual(VERIFICATION_CONFIG_SCHEMA, ROOT / inventory["config_boundary"]["schema"])

    def test_report_case_matches_committed_fixture_pair(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        case = inventory["report_case"]
        citations = load_json(ROOT / case["citations"])
        report = load_json(ROOT / case["golden"])
        claims = citation_claims(citations)
        checks = report["checks"]

        self.assertEqual("native-non-v1-claims", case["name"])
        self.assertEqual(len(claims), len(checks))
        self.assertEqual([claim["kind"] for claim in claims], ["presence", "region", "other"])
        self.assertEqual([check["claim"] for check in checks], claims)
        self.assertEqual(case["expected_statuses"], [check["status"] for check in checks])
        self.assertEqual(
            case["expected_reasons"],
            [check["reason"] for check in checks if "reason" in check],
        )
        self.assertEqual(
            case["expected_match_methods"],
            [check["match_method"] for check in checks],
        )
        self.assertEqual(
            case["expected_unsupported_claim_kinds"],
            report["unsupported_claim_kinds"],
        )
        self.assertEqual(case["all_evidence_grounded"], report["all_evidence_grounded"])

    def test_unsupported_checks_fail_closed_without_evidence_or_semantic_state(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        report = load_json(ROOT / inventory["report_case"]["golden"])
        unsupported_checks = [
            check for check in report["checks"] if check["status"] == "unsupported_claim_kind"
        ]

        self.assertEqual(2, len(unsupported_checks))
        for check in unsupported_checks:
            self.assertEqual("unsupported_claim_kind", check["reason"])
            self.assertEqual("none", check["match_method"])
            self.assertFalse(check["semantic_unverified"])
            self.assertNotIn("evidence", check)
            self.assertEqual([], check["warnings"])

    def test_verify_citations_inventory_keeps_non_v1_case_classified(self) -> None:
        inventory = load_json(VERIFY_CITATIONS_INVENTORY)
        matching = [
            case for case in inventory["report_cases"] if case["name"] == "native-non-v1-claims"
        ]

        self.assertEqual(1, len(matching))
        self.assertEqual("unsupported-non-v1", matching[0]["category"])
        self.assertEqual(False, matching[0]["all_evidence_grounded"])
        self.assertEqual(
            ["grounded", "unsupported_claim_kind", "unsupported_claim_kind"],
            matching[0]["statuses"],
        )
        self.assertEqual(
            ["unsupported_claim_kind", "unsupported_claim_kind"],
            matching[0]["reasons"],
        )

    def test_executable_case_inventory_points_to_same_fixture_pair(self) -> None:
        inventory = load_json(CONTRACT_INVENTORY)
        cases = load_json(VERIFY_CASES)
        matching = [
            case for case in cases["report_cases"] if case["name"] == inventory["report_case"]["name"]
        ]

        self.assertEqual(1, len(matching))
        self.assertEqual(inventory["report_case"]["citations"], matching[0]["citations"])
        self.assertEqual(inventory["report_case"]["golden"], matching[0]["golden"])

    def test_rust_surfaces_keep_claim_kind_boundary_explicit(self) -> None:
        verify_types = RUST_VERIFY_TYPES.read_text(encoding="utf-8")
        verify_lib = RUST_VERIFY_LIB.read_text(encoding="utf-8")
        cli_verify = RUST_CLI_VERIFY.read_text(encoding="utf-8")
        cli_tests = CLI_VERIFY_TESTS.read_text(encoding="utf-8")

        for variant in ["Quote", "Value", "Presence", "TableCell", "Region", "Other"]:
            self.assertIn(variant, verify_types)
        self.assertIn("ClaimKind::Region => \"region\"", verify_lib)
        self.assertIn("ClaimKind::Other => \"other\"", verify_lib)
        self.assertIn("non_v1_claim_kinds_are_deduped_and_keep_gate_false", verify_lib)
        self.assertIn("unsupported_claim_kinds_are_explicit", verify_lib)
        self.assertIn("ClaimKind::Region | ClaimKind::Other", cli_verify)
        self.assertIn("verification config claim_kinds must include only quote", cli_verify)
        self.assertIn("invalid_config_constraints_are_usage_errors", cli_tests)


if __name__ == "__main__":
    unittest.main()
