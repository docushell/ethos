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
import unittest
from pathlib import Path

from ethos_pdf import proof_summary


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_CONTRACT = REPO_ROOT / "examples/verify/verify_citations_v1_contract.json"
VERIFY_CASES = REPO_ROOT / "examples/verify/cases.json"


class ProofSummaryContractTests(unittest.TestCase):
    def test_python_summary_matches_verify_contract_inventory_goldens(self) -> None:
        contract = _load_json(VERIFY_CONTRACT)
        cases = _load_json(VERIFY_CASES)
        golden_by_name = {
            case["name"]: REPO_ROOT / case["golden"]
            for case in cases["report_cases"]
        }

        for contract_case in contract["report_cases"]:
            with self.subTest(case=contract_case["name"]):
                report = _load_json(golden_by_name[contract_case["name"]])
                summary = proof_summary(report)

                self.assertEqual(
                    summary["proof_status"],
                    contract_case["expected_proof_status"],
                )
                self.assertEqual(
                    summary["request_certified"],
                    contract_case["expected_request_certified"],
                )
                self.assertEqual(
                    summary["reusable_grounded_check_ids"],
                    contract_case["expected_reusable_check_ids"],
                )
                self.assertEqual(
                    summary["proof_limitations"],
                    contract_case["expected_proof_limitations"],
                )
                self.assertEqual(
                    summary["needs_review_check_ids"],
                    [
                        check["id"]
                        for check in report["checks"]
                        if check["id"]
                        not in contract_case["expected_reusable_check_ids"]
                    ],
                )


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
