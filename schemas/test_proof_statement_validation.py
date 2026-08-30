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
"""Negative coverage for the proof statement schema (ci.yml: schema-validate job).

`validate_examples.py` proves the schema accepts what Ethos emits. It cannot prove the
schema rejects anything, and a schema that accepts every document passes that gate exactly
as loudly as one that does its job. These are the refusals.

The case that matters most is `a_bare_report_is_not_a_statement`: before 0.6.0 the bare
report *was* the artifact, so a consumer who never noticed the wrapper is handing this
schema the old shape. It has to say no, and say so on the missing envelope rather than
somewhere confusing inside the predicate.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "ethos-proof-statement.schema.json"
EXAMPLE = ROOT / "schemas" / "examples" / "proof-statement.example.json"


def validator() -> Draft202012Validator:
    return Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))


def example() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


class ProofStatementSchemaTest(unittest.TestCase):
    def assert_valid(self, document: dict) -> None:
        errors = list(validator().iter_errors(document))
        self.assertEqual(errors, [], f"expected valid, got: {[e.message for e in errors]}")

    def assert_refused(self, document: dict, expect: str) -> None:
        errors = list(validator().iter_errors(document))
        self.assertTrue(errors, "expected the schema to refuse this document")
        joined = " | ".join(e.message for e in errors)
        self.assertIn(expect, joined)

    def test_the_emitted_example_validates(self) -> None:
        # Real `ethos verify` output, not hand-written. If this fails the schema has
        # drifted from the binary, which is the only way it can be wrong that matters.
        self.assert_valid(example())

    def test_a_bare_report_is_not_a_statement(self) -> None:
        # The pre-0.6.0 artifact, handed to the post-0.6.0 schema.
        self.assert_refused(example()["predicate"], "'_type' is a required property")

    def test_an_unknown_predicate_type_is_refused(self) -> None:
        document = example()
        document["predicateType"] = "https://example.invalid/grounding/v1"
        self.assert_refused(document, "is not one of")

    def test_the_statement_type_is_pinned(self) -> None:
        document = example()
        document["_type"] = "https://in-toto.io/Statement/v0.1"
        self.assert_refused(document, "was expected")

    def test_an_empty_subject_is_refused(self) -> None:
        # in-toto forbids it and the Rust type makes it unrepresentable; the schema
        # should not be the one place it becomes expressible again.
        document = example()
        document["subject"] = []
        self.assert_refused(document, "should be non-empty")

    def test_more_than_representation_and_source_is_refused(self) -> None:
        document = example()
        document["subject"] = document["subject"] * 3
        self.assert_refused(document, "too long")

    def test_a_digest_must_be_bare_lowercase_hex(self) -> None:
        # `sha256:`-prefixed is how `document_fingerprint` is spelled inside a report,
        # which makes it the plausible wrong answer here rather than an unlikely one.
        for bad in ["NOTHEX", "sha256:" + "a" * 64, "a" * 63, "A" * 64]:
            document = example()
            document["subject"] = [{"name": "x", "digest": {"sha256": bad}}]
            self.assert_refused(document, "does not match")

    def test_an_unexpected_algorithm_is_refused(self) -> None:
        document = example()
        document["subject"] = [
            {"name": "x", "digest": {"sha256": "a" * 64, "sha512": "b" * 128}}
        ]
        self.assert_refused(document, "Additional properties are not allowed")

    def test_extra_envelope_fields_are_refused(self) -> None:
        # A signed in-toto envelope carries `signatures`. Ethos does not sign, and a
        # document that looks signed must not validate as one Ethos wrote.
        document = example()
        document["signatures"] = []
        self.assert_refused(document, "Additional properties are not allowed")

    def test_the_predicate_must_be_an_object(self) -> None:
        document = example()
        document["predicate"] = "the verdict"
        self.assert_refused(document, "is not of type 'object'")

    def test_every_declared_predicate_type_is_accepted(self) -> None:
        # The enum is the contract; each member must actually validate rather than
        # merely be listed.
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        declared = schema["properties"]["predicateType"]["enum"]
        self.assertEqual(len(declared), 5)
        for predicate_type in declared:
            document = copy.deepcopy(example())
            document["predicateType"] = predicate_type
            self.assert_valid(document)


if __name__ == "__main__":
    unittest.main()
