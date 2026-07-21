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
    project_evidence_states,
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


def verification_report(hydrated_claims, statuses, *, stale=False, fingerprint=FINGERPRINT):
    """Build the smallest schema-valid report needed by state projection tests."""
    checks = []
    for index, (claim, status) in enumerate(zip(hydrated_claims, statuses), 1):
        checks.append({
            "id": f"v{index:04d}",
            "claim": claim,
            "status": status,
            "match_method": "presence_only" if claim["kind"] == "presence" else "exact_text",
            "semantic_unverified": False,
            "warnings": [],
        })
    supported = [check for check in checks if check["status"] != "unsupported_claim_kind"]
    return {
        "schema_version": "1.0.0",
        "document_fingerprint": fingerprint,
        "verification_config_sha256": "b" * 64,
        "grounding": {
            "parser": {"name": "ethos", "version": "0.5.0"},
            "capabilities": {
                "spans": True,
                "char_offsets": True,
                "tables": True,
                "fingerprint": True,
                "coordinate_origin": "top-left",
                "crop_support": False,
            },
        },
        "capability_limits": [],
        "fingerprint_stale": stale,
        "all_evidence_grounded": bool(supported) and all(
            check["status"] == "grounded" for check in supported
        ),
        "checks": checks,
        "unsupported_claim_kinds": [],
        "warnings": [],
    }


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
            ("invalid_locator", [evidence_record("bad", {"element_id": "e000001", "span_id": "s000001"})]),
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

    def test_projects_context_ordered_evidence_states(self):
        context = build_evidence_handle_context([
            evidence_record("unreferenced", {"page": "p0001"}),
            evidence_record("mixed", {"element_id": "e000001"}, display="Revenue"),
            evidence_record("ungrounded", {"span_id": "s000001"}),
        ])
        emission = build_evidence_citation_emission("Answer.", [
            {"kind": "quote", "text": "Revenue", "evidence_id": "mixed"},
            {"kind": "value", "text": "$12", "evidence_id": "mixed"},
            {"kind": "presence", "evidence_id": "ungrounded"},
        ])
        hydrated = hydrate_evidence_citations(emission, context)
        report = verification_report(hydrated["claims"], ["grounded", "mismatch", "not_found"])

        projection = project_evidence_states(context, emission, report)

        self.assertEqual(FINGERPRINT, projection["document_fingerprint"])
        self.assertFalse(projection["all_evidence_grounded"])
        self.assertEqual(
            [
                {"evidence_id": "unreferenced", "state": "unreferenced", "claim_indexes": [], "check_ids": []},
                {"evidence_id": "mixed", "state": "partially_grounded", "claim_indexes": [1, 2], "check_ids": ["v0001", "v0002"], "display": "Revenue"},
                {"evidence_id": "ungrounded", "state": "ungrounded", "claim_indexes": [3], "check_ids": ["v0003"]},
            ],
            projection["states"],
        )

    def test_projection_fails_closed_for_stale_mismatched_or_inconsistent_report(self):
        context = build_evidence_handle_context([
            evidence_record("ev-1", {"page": "p0001"}),
        ])
        emission = build_evidence_citation_emission("Answer.", [
            {"kind": "presence", "evidence_id": "ev-1"},
        ])
        hydrated = hydrate_evidence_citations(emission, context)
        report = verification_report(hydrated["claims"], ["grounded"])

        stale = copy.deepcopy(report)
        stale["fingerprint_stale"] = True
        mismatched = copy.deepcopy(report)
        mismatched["checks"][0]["claim"]["citation"] = {"page": "p9999"}
        inconsistent = copy.deepcopy(report)
        inconsistent["all_evidence_grounded"] = False

        for invalid_report, code in (
            (stale, "report_context_mismatch"),
            (mismatched, "report_context_mismatch"),
            (inconsistent, "invalid_report"),
        ):
            with self.subTest(code=code):
                assert_error(
                    self,
                    code,
                    lambda invalid_report=invalid_report: project_evidence_states(
                        context, emission, invalid_report
                    ),
                )

    def test_projection_is_byte_identical_across_two_runs(self):
        context = build_evidence_handle_context([
            evidence_record("ev-1", {"page": "p0001"}),
        ])
        emission = build_evidence_citation_emission("Answer.", [
            {"kind": "presence", "evidence_id": "ev-1"},
        ])
        report = verification_report(
            hydrate_evidence_citations(emission, context)["claims"], ["grounded"]
        )

        self.assertEqual(
            citation_json_bytes(project_evidence_states(context, emission, report)),
            citation_json_bytes(project_evidence_states(context, emission, report)),
        )


if __name__ == "__main__":
    unittest.main()
