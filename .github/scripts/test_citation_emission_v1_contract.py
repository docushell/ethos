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

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from makefile_guard import makefile_text, target_block


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/ethos-llm-citation-output.schema.json"
CITATIONS_SCHEMA = ROOT / "schemas/ethos-citations.schema.json"
DOCUMENT = ROOT / "schemas/examples/document.example.json"
EXAMPLES = ROOT / "examples/citation-emission"
CONTEXT = EXAMPLES / "retrieval-context.json"
ETHOS_BIN = ROOT / "target/debug/ethos"
CONTRACT = ROOT / "docs/citation-emission-spec.md"
SCHEMAS_README = ROOT / "schemas/README.md"
VALIDATE_EXAMPLES = ROOT / "schemas/validate_examples.py"
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_fixture_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode("utf-8")


def hydrate(emission: dict, context: dict) -> dict:
    pages = set(context["pages"])
    elements = set(context["elements"])
    spans = set(context["spans"])
    table_cells = {
        (entry["table_id"], entry["row"], entry["col"])
        for entry in context["table_cells"]
    }
    claims = []
    for index, emitted in enumerate(emission["claims"], 1):
        citation = {}
        if "page" in emitted:
            if emitted["page"] not in pages:
                raise ValueError(f"claim {index}: out_of_vocabulary page {emitted['page']}")
            citation["page"] = emitted["page"]
        if "element_id" in emitted:
            if emitted["element_id"] not in elements:
                raise ValueError(
                    f"claim {index}: out_of_vocabulary element_id {emitted['element_id']}"
                )
            citation["element_id"] = emitted["element_id"]
        if "span_id" in emitted:
            if emitted["span_id"] not in spans:
                raise ValueError(f"claim {index}: out_of_vocabulary span_id {emitted['span_id']}")
            citation["span_id"] = emitted["span_id"]
        if "table_id" in emitted:
            cell = emitted["cell"]
            locator = (emitted["table_id"], cell["row"], cell["col"])
            if locator not in table_cells:
                raise ValueError(
                    f"claim {index}: out_of_vocabulary table_cell "
                    f"{emitted['table_id']}[{cell['row']},{cell['col']}]"
                )
            citation["table_id"] = emitted["table_id"]
            citation["cell"] = {"row": cell["row"], "col": cell["col"]}

        primary_count = sum(
            key in citation for key in ["element_id", "span_id", "table_id"]
        )
        if primary_count > 1:
            raise ValueError(f"claim {index}: locator_conflict")
        if primary_count == 0 and "page" not in citation:
            raise ValueError(f"claim {index}: locator_missing")

        claim = {"kind": emitted["kind"]}
        if "text" in emitted:
            claim["text"] = emitted["text"]
        claim["citation"] = citation
        claims.append(claim)

    return {
        "document_fingerprint": context["document_fingerprint"],
        "claims": claims,
    }


class CitationEmissionV1ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_json(SCHEMA)
        cls.validator = Draft202012Validator(cls.schema)
        cls.citations_validator = Draft202012Validator(load_json(CITATIONS_SCHEMA))
        cls.context = load_json(CONTEXT)

    def test_schema_is_independently_versioned_and_model_facing(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual("urn:ethos:schema:llm-citation-output:1", self.schema["$id"])
        self.assertEqual({"const": "1.0.0"}, self.schema["properties"]["schema_version"])
        text = SCHEMA.read_text(encoding="utf-8")
        self.assertNotIn("document_fingerprint\"", text)
        self.assertNotIn("bbox\"", text)

    def test_valid_fixtures_validate_and_conflicting_locator_fails(self) -> None:
        for name in [
            "model-output.grounded.json",
            "model-output.fabricated-quote.json",
            "model-output.dangling-id.json",
        ]:
            self.assertEqual([], list(self.validator.iter_errors(load_json(EXAMPLES / name))), name)
        errors = list(
            self.validator.iter_errors(load_json(EXAMPLES / "model-output.locator-conflict.json"))
        )
        self.assertTrue(errors)

    def test_schema_rejects_missing_or_forbidden_model_fields(self) -> None:
        grounded = load_json(EXAMPLES / "model-output.grounded.json")
        invalid = []

        no_claims = dict(grounded)
        no_claims["claims"] = []
        invalid.append(no_claims)

        blank_answer = dict(grounded)
        blank_answer["answer"] = "   "
        invalid.append(blank_answer)

        fingerprint = dict(grounded)
        fingerprint["document_fingerprint"] = self.context["document_fingerprint"]
        invalid.append(fingerprint)

        no_locator = dict(grounded)
        no_locator["claims"] = [{"kind": "quote", "text": "asserted text"}]
        invalid.append(no_locator)

        bbox = dict(grounded)
        bbox["claims"] = [{
            "kind": "quote",
            "text": "asserted text",
            "page": "p0001",
            "bbox": [0, 0, 1, 1],
        }]
        invalid.append(bbox)

        presence_text = dict(grounded)
        presence_text["claims"] = [{
            "kind": "presence",
            "text": "not permitted",
            "element_id": "e000002",
        }]
        invalid.append(presence_text)

        table_without_cell = dict(grounded)
        table_without_cell["claims"] = [{
            "kind": "table_cell",
            "text": "$12.4M",
            "table_id": "t0001",
        }]
        invalid.append(table_without_cell)

        for index, payload in enumerate(invalid, 1):
            self.assertTrue(list(self.validator.iter_errors(payload)), index)

    def test_source_ids_are_grounding_source_owned_not_native_only(self) -> None:
        foreign = {
            "schema_version": "1.0.0",
            "answer": "A foreign source value.",
            "claims": [{
                "kind": "value",
                "text": "foreign-value",
                "element_id": "docling/items/paragraph-7",
            }],
        }
        self.assertEqual([], list(self.validator.iter_errors(foreign)))

    def test_hydration_is_byte_identical_and_matches_committed_fixtures(self) -> None:
        for stem in ["grounded", "fabricated-quote"]:
            emission = load_json(EXAMPLES / f"model-output.{stem}.json")
            first = canonical_fixture_bytes(hydrate(emission, self.context))
            second = canonical_fixture_bytes(hydrate(emission, self.context))
            self.assertEqual(first, second)
            self.assertEqual((EXAMPLES / f"hydrated.{stem}.json").read_bytes(), first)
            self.assertEqual(
                [],
                list(self.citations_validator.iter_errors(json.loads(first))),
                stem,
            )

    def test_dangling_id_fails_closed_before_verification(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            r"claim 1: out_of_vocabulary element_id e999999",
        ):
            hydrate(load_json(EXAMPLES / "model-output.dangling-id.json"), self.context)

    def test_verification_reports_are_byte_identical_across_runs(self) -> None:
        cases = [
            ("grounded", 0, True, ["grounded", "grounded"]),
            ("fabricated-quote", 1, False, ["mismatch"]),
        ]
        with tempfile.TemporaryDirectory(prefix="ethos-citation-emission-") as temp:
            temp_dir = Path(temp)
            for stem, expected_exit, all_grounded, statuses in cases:
                reports = []
                for run in [1, 2]:
                    report = temp_dir / f"{stem}.run{run}.json"
                    result = subprocess.run(
                        [
                            str(ETHOS_BIN),
                            "verify",
                            str(DOCUMENT),
                            "--citations",
                            str(EXAMPLES / f"hydrated.{stem}.json"),
                            "--fail-on-ungrounded",
                            "--out",
                            str(report),
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(expected_exit, result.returncode, result.stderr)
                    reports.append(report.read_bytes())
                self.assertEqual(reports[0], reports[1], stem)
                payload = json.loads(reports[0])
                self.assertEqual(all_grounded, payload["all_evidence_grounded"])
                self.assertEqual(statuses, [check["status"] for check in payload["checks"]])

    def test_repository_wiring_and_normative_boundary_are_present(self) -> None:
        self.assertIn("citation-emission-v1-contract", makefile_text())
        commands = [
            line.strip()
            for line in target_block("citation-emission-v1-contract").splitlines()
            if line.strip()
        ]
        self.assertEqual([
            "cargo build --locked -p ethos-cli",
            "$(PYTHON) schemas/validate_examples.py",
            "$(PYTHON) .github/scripts/test_citation_emission_v1_contract.py",
            "git diff --check",
        ], commands)
        self.assertIn("make citation-emission-v1-contract", CI_WORKFLOW.read_text(encoding="utf-8"))
        self.assertIn("ethos-llm-citation-output.schema.json", SCHEMAS_README.read_text(encoding="utf-8"))
        self.assertIn("llm-citation-output.example.json", VALIDATE_EXAMPLES.read_text(encoding="utf-8"))

        contract = CONTRACT.read_text(encoding="utf-8")
        for required in [
            "Ethos verifies citation grounding, not semantic truth.",
            "The model MUST NOT emit document fingerprints or bounding boxes.",
            "Applications MUST NOT retry an exit-1 verification",
            "independently from the verification-report schema",
            "table_id",
        ]:
            self.assertIn(required, contract)


if __name__ == "__main__":
    unittest.main()
