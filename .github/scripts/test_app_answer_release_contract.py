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
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DOC = ROOT / "docs/app-answer-release-contract.md"
SCHEMA = ROOT / "schemas/ethos-app-answer-release-decision.schema.json"
EXAMPLE = ROOT / "schemas/examples/app-answer-release-decision.example.json"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
SCHEMAS_README = ROOT / "schemas/README.md"
README = ROOT / "README.md"
SPEC = ROOT / "SPEC.md"

EXPECTED_TARGET_COMMANDS = [
    "cargo test --locked -p ethos-doc-core --no-default-features --features verify-types app_answer_release",
    "$(PYTHON) schemas/validate_examples.py",
    "$(PYTHON) .github/scripts/test_app_answer_release_contract.py",
    "$(PYTHON) .github/scripts/claims_gate.py",
    "$(PYTHON) .github/scripts/public_boundary_claims_gate.py",
    "git diff --check",
]
EXPECTED_PROOF_STATUS = ["verified", "partially_verified", "unverified"]
EXPECTED_PROOF_LIMITATIONS = [
    "capability_limited",
    "stale_fingerprint",
    "unsupported_claim_kind",
    "non_grounded_checks",
    "semantic_unverified",
]
EXPECTED_APP_STATUSES = [
    "certified",
    "partial_certified",
    "supported_synthesis_needs_review",
    "grounded_but_irrelevant",
    "cannot_answer_from_sources",
]
EXPECTED_RELEVANCE = ["direct_answer", "supports_answer", "background_only", "unrelated"]
EXPECTED_CLAIM_TYPES = ["source_fact", "synthesis", "unsupported"]
EXPECTED_RELEASE_ACTIONS = ["show_final", "needs_review", "block"]
EXPECTED_RELEASE_REASONS = [
    "certified",
    "supported_synthesis_needs_review",
    "grounded_but_irrelevant",
    "cannot_answer_from_sources",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_enum(name: str) -> list[str]:
    return load_json(SCHEMA)["$defs"][name]["enum"]


def claim_by_id(example: dict) -> dict[str, dict]:
    return {claim["id"]: claim for claim in example["claims"]}


def normalized_markdown(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class AppAnswerReleaseContractTests(unittest.TestCase):
    def test_schema_validates_example(self) -> None:
        schema = load_json(SCHEMA)
        example = load_json(EXAMPLE)

        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(example),
            key=lambda error: list(error.absolute_path),
        )

        self.assertEqual([], errors)

    def test_schema_vocabulary_matches_contract(self) -> None:
        self.assertEqual(EXPECTED_PROOF_STATUS, schema_enum("proof_status"))
        self.assertEqual(EXPECTED_PROOF_LIMITATIONS, schema_enum("proof_limitation"))
        self.assertEqual(EXPECTED_APP_STATUSES, schema_enum("app_status"))
        self.assertEqual(EXPECTED_RELEVANCE, schema_enum("question_relevance"))
        self.assertEqual(EXPECTED_CLAIM_TYPES, schema_enum("claim_type"))
        self.assertEqual(EXPECTED_RELEASE_ACTIONS, schema_enum("release_action"))
        self.assertEqual(EXPECTED_RELEASE_REASONS, schema_enum("release_reason"))

    def test_example_covers_relevance_and_synthesis_failure_modes(self) -> None:
        example = load_json(EXAMPLE)
        claims = claim_by_id(example)

        self.assertEqual("partial_certified", example["app_status"])
        self.assertEqual("partially_verified", example["grounding"]["proof_status"])

        irrelevant = claims["claim-office-background"]
        self.assertTrue(irrelevant["citation_grounded"])
        self.assertEqual("background_only", irrelevant["question_relevance"])
        self.assertEqual("block", irrelevant["release_action"])
        self.assertEqual("grounded_but_irrelevant", irrelevant["release_reason"])

        synthesis = claims["claim-growth-driver"]
        self.assertTrue(synthesis["citation_grounded"])
        self.assertEqual(["v0001", "v0003"], synthesis["check_ids"])
        self.assertEqual("synthesis", synthesis["claim_type"])
        self.assertEqual("needs_review", synthesis["release_action"])
        self.assertEqual("supported_synthesis_needs_review", synthesis["release_reason"])

        unsupported = claims["claim-margin"]
        self.assertFalse(unsupported["citation_grounded"])
        self.assertEqual("unsupported", unsupported["claim_type"])
        self.assertEqual("cannot_answer_from_sources", unsupported["release_reason"])

    def test_final_answer_ids_are_only_certified_source_facts(self) -> None:
        example = load_json(EXAMPLE)
        claims = claim_by_id(example)

        for claim_id in example["final_answer_claim_ids"]:
            claim = claims[claim_id]
            self.assertEqual("show_final", claim["release_action"])
            self.assertEqual("certified", claim["release_reason"])
            self.assertTrue(claim["citation_grounded"])
            self.assertIn(claim["question_relevance"], ["direct_answer", "supports_answer"])
            self.assertEqual("source_fact", claim["claim_type"])

        for claim_id in example["review_claim_ids"]:
            self.assertEqual("needs_review", claims[claim_id]["release_action"])

        for claim_id in example["blocked_claim_ids"]:
            self.assertEqual("block", claims[claim_id]["release_action"])

    def test_schema_registry_validates_example(self) -> None:
        text = VALIDATE_EXAMPLES.read_text(encoding="utf-8")

        self.assertIn('"ethos-app-answer-release-decision.schema.json"', text)
        self.assertIn('EXAMPLES / "app-answer-release-decision.example.json"', text)

    def test_schema_readme_registers_non_canonical_wrapper(self) -> None:
        text = SCHEMAS_README.read_text(encoding="utf-8")

        self.assertIn("`ethos-app-answer-release-decision.schema.json`", text)
        self.assertIn("`schemas/examples/app-answer-release-decision.example.json`", text)
        self.assertIn("not `verification_report.json`", text)

    def test_docs_link_schema_and_keep_boundary_explicit(self) -> None:
        text = CONTRACT_DOC.read_text(encoding="utf-8")
        normalized = normalized_markdown(CONTRACT_DOC)

        self.assertIn("`schemas/ethos-app-answer-release-decision.schema.json`", text)
        self.assertIn("`schemas/examples/app-answer-release-decision.example.json`", text)
        self.assertIn("not a replacement for `verification_report.json`", normalized)
        self.assertIn("`app_answer_release_decision(...)`", text)
        self.assertIn("`derive_app_answer_release_decision(...)`", text)
        self.assertIn("`check_ids`", text)
        self.assertIn("Ethos verified citation grounding.", text)
        for token in EXPECTED_APP_STATUSES + EXPECTED_RELEVANCE + EXPECTED_CLAIM_TYPES:
            self.assertIn(f"`{token}`", text)

    def test_readme_and_spec_point_to_contract(self) -> None:
        for path in [README, SPEC]:
            self.assertIn(
                "docs/app-answer-release-contract.md",
                path.read_text(encoding="utf-8"),
                str(path),
            )

    def test_make_target_composes_scoped_guard(self) -> None:
        text = makefile_text()
        self.assertIn("app-answer-release-contract", text)

        commands = [
            line.strip()
            for line in target_block("app-answer-release-contract").splitlines()
            if line.strip()
        ]

        self.assertEqual(EXPECTED_TARGET_COMMANDS, commands)
        block = target_block("app-answer-release-contract")
        for out_of_scope in [
            "cargo publish",
            "gh release",
            "release-candidate-prep",
            "milestone-e-prep",
            "npm",
        ]:
            self.assertNotIn(out_of_scope, block)


if __name__ == "__main__":
    unittest.main()
