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
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from makefile_guard import target_block


ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "examples/app-answer-release"
SCRIPT = DEMO / "run_python_demo.py"
SCHEMA = ROOT / "schemas/ethos-app-answer-release-decision.schema.json"
VERIFICATION_SCHEMA = ROOT / "schemas/ethos-verification-report.schema.json"
PYTHON_PACKAGE = ROOT / "python"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_demo() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class AppAnswerReleaseDemoTests(unittest.TestCase):
    def test_demo_script_exits_zero_and_matches_expected_decision(self) -> None:
        result = run_demo()

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(load_json(DEMO / "expected-decision.json"), json.loads(result.stdout))

    def test_demo_expected_decision_validates_against_schema(self) -> None:
        schema = load_json(SCHEMA)
        decision = load_json(DEMO / "expected-decision.json")

        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(decision),
            key=lambda error: list(error.absolute_path),
        )

        self.assertEqual([], errors)

    def test_demo_verification_report_validates_against_canonical_schema(self) -> None:
        schema = load_json(VERIFICATION_SCHEMA)
        report = load_json(DEMO / "verification-report.json")

        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(report),
            key=lambda error: list(error.absolute_path),
        )

        self.assertEqual([], errors)

    def test_demo_derives_expected_proof_summary_from_verification_report(self) -> None:
        if str(PYTHON_PACKAGE) not in sys.path:
            sys.path.insert(0, str(PYTHON_PACKAGE))
        from ethos_pdf import proof_summary

        report = load_json(DEMO / "verification-report.json")

        self.assertEqual(load_json(DEMO / "proof-summary.json"), proof_summary(report))

    def test_demo_keeps_canonical_report_separate_from_app_wrapper(self) -> None:
        report = load_json(DEMO / "verification-report.json")
        decision = load_json(DEMO / "expected-decision.json")

        self.assertIn("checks", report)
        self.assertIn("all_evidence_grounded", report)
        self.assertNotIn("artifact_type", report)
        self.assertNotIn("app_status", report)
        self.assertNotIn("checks", decision)
        self.assertEqual(
            "verification-report.json",
            decision["grounding"]["verification_report_ref"],
        )

    def test_demo_covers_final_review_and_blocked_release_cases(self) -> None:
        decision = load_json(DEMO / "expected-decision.json")
        claims = {claim["id"]: claim for claim in decision["claims"]}

        self.assertEqual(["claim-revenue"], decision["final_answer_claim_ids"])
        self.assertEqual(["claim-growth-driver"], decision["review_claim_ids"])
        self.assertEqual(
            ["claim-office-background", "claim-margin"],
            decision["blocked_claim_ids"],
        )

        certified = claims["claim-revenue"]
        self.assertTrue(certified["citation_grounded"])
        self.assertEqual("source_fact", certified["claim_type"])
        self.assertEqual("show_final", certified["release_action"])
        self.assertEqual("certified", certified["release_reason"])

        synthesis = claims["claim-growth-driver"]
        self.assertTrue(synthesis["citation_grounded"])
        self.assertEqual("synthesis", synthesis["claim_type"])
        self.assertEqual("needs_review", synthesis["release_action"])
        self.assertEqual("supported_synthesis_needs_review", synthesis["release_reason"])

        irrelevant = claims["claim-office-background"]
        self.assertTrue(irrelevant["citation_grounded"])
        self.assertEqual("background_only", irrelevant["question_relevance"])
        self.assertEqual("block", irrelevant["release_action"])
        self.assertEqual("grounded_but_irrelevant", irrelevant["release_reason"])

        unsupported = claims["claim-margin"]
        self.assertFalse(unsupported["citation_grounded"])
        self.assertEqual("unsupported", unsupported["claim_type"])
        self.assertEqual("block", unsupported["release_action"])
        self.assertEqual("cannot_answer_from_sources", unsupported["release_reason"])

    def test_demo_helper_rejects_duplicate_claim_ids(self) -> None:
        if str(PYTHON_PACKAGE) not in sys.path:
            sys.path.insert(0, str(PYTHON_PACKAGE))
        from ethos_pdf import app_answer_release_decision

        summary = load_json(DEMO / "proof-summary.json")
        payload = load_json(DEMO / "claims.json")
        claims = [dict(claim) for claim in payload["claims"]]
        claims[1]["id"] = claims[0]["id"]

        with self.assertRaisesRegex(ValueError, "duplicate claim id: claim-revenue"):
            app_answer_release_decision(
                payload["question"],
                summary,
                claims,
                verification_report_ref=payload["verification_report_ref"],
            )

    def test_make_target_runs_demo_guard_without_publication_actions(self) -> None:
        block = target_block("app-answer-release-demo")

        self.assertIn("$(PYTHON) .github/scripts/test_app_answer_release_demo.py", block)
        self.assertIn("git diff --check", block)
        for out_of_scope in ["cargo publish", "gh release", "npm publish", "twine upload"]:
            self.assertNotIn(out_of_scope, block)


if __name__ == "__main__":
    unittest.main()
