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

"""Offline regression coverage for Evidence Handle Bridge v1/v2 helpers."""

from __future__ import annotations

import copy
import unittest

from ethos_pdf import (
    CitationEmissionError,
    build_citation_emission,
    build_evidence_citation_emission,
    build_evidence_handle_context,
    build_langchain_context,
    citation_json_bytes,
    hydrate_citations,
    hydrate_evidence_citations,
)


FINGERPRINT = "sha256:" + ("a" * 64)


def evidence_record(evidence_id, locator, **overrides):
    record = {
        "document_fingerprint": FINGERPRINT,
        "evidence_id": evidence_id,
        "locator": locator,
    }
    record.update(overrides)
    return record


def assert_error(test, code, callable_):
    with test.assertRaises(CitationEmissionError) as raised:
        callable_()
    test.assertEqual(code, raised.exception.code)
    return raised.exception


class EvidenceHandleBridgeTests(unittest.TestCase):
    def test_v1_citation_emission_remains_compatible(self):
        emission = build_citation_emission(
            "The value is $12.",
            [{"kind": "value", "text": "$12", "element_id": "e000001"}],
        )
        context = build_langchain_context([
            {
                "metadata": {
                    "document_fingerprint": FINGERPRINT,
                    "element_refs": ["e000001"],
                }
            }
        ])

        self.assertEqual("1.0.0", emission["schema_version"])
        self.assertEqual(
            {"document_fingerprint": FINGERPRINT, "claims": [{
                "kind": "value",
                "text": "$12",
                "citation": {"element_id": "e000001"},
            }]},
            hydrate_citations(emission, context),
        )

    def test_build_emit_and_hydrate_opaque_handles(self):
        records = [
            evidence_record(
                "ev-page",
                {"page": "p0001"},
                display="Page 1",
                excerpt="A non-authoritative display excerpt.",
            ),
            evidence_record("ev-element", {"element_id": "e000001"}),
            evidence_record(
                "ev-cell", {"table_id": "t0001", "cell": {"row": 0, "col": 1}}
            ),
        ]
        before = copy.deepcopy(records)

        context = build_evidence_handle_context(records)
        emission = build_evidence_citation_emission("The value is $12.", [
            {"kind": "quote", "text": "A non-authoritative", "evidence_id": "ev-page"},
            {"kind": "value", "text": "$12", "evidence_id": "ev-element"},
            {"kind": "table_cell", "text": "$12", "evidence_id": "ev-cell"},
        ])
        hydrated = hydrate_evidence_citations(emission, context)

        self.assertEqual(before, records)
        self.assertEqual("ethos.evidence_handle_context.v1", context["artifact_type"])
        self.assertEqual("1.0.0", context["schema_version"])
        self.assertEqual("2.0.0", emission["schema_version"])
        self.assertEqual(
            {
                "document_fingerprint": FINGERPRINT,
                "claims": [
                    {"kind": "quote", "text": "A non-authoritative", "citation": {"page": "p0001"}},
                    {"kind": "value", "text": "$12", "citation": {"element_id": "e000001"}},
                    {"kind": "table_cell", "text": "$12", "citation": {"table_id": "t0001", "cell": {"row": 0, "col": 1}}},
                ],
            },
            hydrated,
        )
        self.assertNotIn("display", citation_json_bytes(hydrated).decode("ascii"))
        self.assertNotIn("excerpt", citation_json_bytes(hydrated).decode("ascii"))

    def test_new_artifacts_are_byte_identical_across_two_runs(self):
        records = [evidence_record("opaque-1", {"span_id": "s000001"})]
        claims = [{"kind": "quote", "text": "A quoted span.", "evidence_id": "opaque-1"}]

        first_context = build_evidence_handle_context(records)
        second_context = build_evidence_handle_context(records)
        first_emission = build_evidence_citation_emission("Answer.", claims)
        second_emission = build_evidence_citation_emission("Answer.", claims)
        first_hydrated = hydrate_evidence_citations(first_emission, first_context)
        second_hydrated = hydrate_evidence_citations(second_emission, second_context)

        self.assertEqual(citation_json_bytes(first_context), citation_json_bytes(second_context))
        self.assertEqual(citation_json_bytes(first_emission), citation_json_bytes(second_emission))
        self.assertEqual(citation_json_bytes(first_hydrated), citation_json_bytes(second_hydrated))

    def test_invalid_context_records_fail_closed(self):
        invalid_records = [
            ("duplicate_evidence_id", [
                evidence_record("same", {"page": "p0001"}),
                evidence_record("same", {"page": "p0002"}),
            ]),
            ("mixed_document_fingerprints", [
                evidence_record("one", {"page": "p0001"}),
                evidence_record("two", {"page": "p0002"}, document_fingerprint="sha256:" + ("b" * 64)),
            ]),
            ("invalid_locator", [evidence_record("bad", {"page": "p0001", "element_id": "e000001"})]),
            ("invalid_locator", [evidence_record("bad", {"table_id": "t0001", "cell": {"row": -1, "col": 0}})]),
            ("invalid_evidence_record", [evidence_record("bad", {"page": "p0001"}, untrusted=True)]),
        ]
        for code, records in invalid_records:
            with self.subTest(code=code, records=records):
                assert_error(self, code, lambda records=records: build_evidence_handle_context(records))

    def test_invalid_v2_emission_shapes_fail_closed(self):
        invalid_emissions = [
            ("unsupported_schema_version", {"schema_version": "1.0.0", "answer": "Answer.", "claims": []}),
            ("invalid_claim", {"schema_version": "2.0.0", "answer": "Answer.", "claims": [{"kind": "presence", "text": "no", "evidence_id": "ev-1"}]}),
            ("invalid_claim", {"schema_version": "2.0.0", "answer": "Answer.", "claims": [{"kind": "quote", "text": "x", "evidence_id": "ev-1", "page": "p0001"}]}),
        ]
        for code, emission in invalid_emissions:
            with self.subTest(code=code, emission=emission):
                assert_error(self, code, lambda emission=emission: build_evidence_citation_emission(emission["answer"], emission["claims"]) if emission["schema_version"] == "2.0.0" else hydrate_evidence_citations(emission, {}))

    def test_unknown_handle_and_invalid_context_fail_closed_during_hydration(self):
        context = build_evidence_handle_context([
            evidence_record("ev-1", {"page": "p0001"})
        ])
        unknown = build_evidence_citation_emission(
            "Answer.", [{"kind": "presence", "evidence_id": "not-shown"}]
        )
        error = assert_error(
            self,
            "out_of_vocabulary",
            lambda: hydrate_evidence_citations(unknown, context),
        )
        self.assertEqual(1, error.claim_index)

        invalid_context = dict(context)
        invalid_context["schema_version"] = "0.0.0"
        assert_error(
            self,
            "unsupported_schema_version",
            lambda: hydrate_evidence_citations(
                build_evidence_citation_emission("Answer.", [{"kind": "presence", "evidence_id": "ev-1"}]),
                invalid_context,
            ),
        )


if __name__ == "__main__":
    unittest.main()
