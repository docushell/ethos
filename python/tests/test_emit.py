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

import ast
import copy
import json
import unittest
from pathlib import Path

from ethos_pdf import (
    CitationEmissionError,
    build_citation_emission,
    build_langchain_context,
    build_llamaindex_context,
    citation_json_bytes,
    emit_langchain_citations,
    emit_llamaindex_citations,
    hydrate_citations,
)


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples/citation-emission"
EMIT_MODULE = ROOT / "python/ethos_pdf/emit.py"
FINGERPRINT = "sha256:" + ("a" * 64)


class FakeDocument:
    def __init__(self, metadata):
        self.page_content = "retrieved text"
        self.metadata = metadata


class FakeNode:
    def __init__(self, metadata):
        self.text = "retrieved text"
        self.metadata = metadata


class FakeNodeWithScore:
    def __init__(self, node):
        self.node = node
        self.score = 0.9


def record_metadata(**overrides):
    metadata = {
        "document_fingerprint": FINGERPRINT,
        "page_refs": ["p0001"],
        "element_refs": ["e000001"],
    }
    metadata.update(overrides)
    return metadata


def assert_error(test, code, callable_):
    with test.assertRaises(CitationEmissionError) as raised:
        callable_()
    test.assertEqual(code, raised.exception.code)
    return raised.exception


class CitationEmissionTests(unittest.TestCase):
    def test_build_and_hydrate_match_frozen_nip_4_1_fixtures(self):
        emission = json.loads((EXAMPLES / "model-output.grounded.json").read_text())
        context = json.loads((EXAMPLES / "retrieval-context.json").read_text())
        expected = (EXAMPLES / "hydrated.grounded.json").read_bytes()

        rebuilt = build_citation_emission(emission["answer"], emission["claims"])
        hydrated = hydrate_citations(rebuilt, context)

        self.assertEqual(emission, rebuilt)
        self.assertEqual(expected, citation_json_bytes(hydrated))

    def test_new_artifacts_are_byte_identical_across_two_runs(self):
        documents = [
            FakeDocument(record_metadata(element_refs=["foreign/item-7"])),
            FakeDocument(record_metadata(page_refs=["p0002"], element_refs=["foreign/item-8"])),
        ]
        claims = [{"kind": "value", "text": "$12.4M", "element_id": "foreign/item-7"}]

        first_emission = citation_json_bytes(
            build_citation_emission("Revenue was $12.4M.", claims)
        )
        second_emission = citation_json_bytes(
            build_citation_emission("Revenue was $12.4M.", claims)
        )
        first = citation_json_bytes(
            emit_langchain_citations(documents, "Revenue was $12.4M.", claims)
        )
        second = citation_json_bytes(
            emit_langchain_citations(documents, "Revenue was $12.4M.", claims)
        )

        self.assertEqual(first_emission, second_emission)
        self.assertEqual(first, second)

    def test_langchain_adapter_preserves_encounter_order_and_does_not_mutate(self):
        metadata = record_metadata(
            page_refs=["p0002", "p0001", "p0002"],
            element_refs=["e000002", "e000001"],
            span_refs=["s000001"],
            table_cells=[{"table_id": "t0001", "row": 1, "col": 2}],
            ignored_framework_field="safe to ignore",
        )
        before = copy.deepcopy(metadata)

        context = build_langchain_context([FakeDocument(metadata)])

        self.assertEqual(before, metadata)
        self.assertEqual(["p0002", "p0001"], context["pages"])
        self.assertEqual(["e000002", "e000001"], context["elements"])
        self.assertEqual(["s000001"], context["spans"])
        self.assertEqual([{"table_id": "t0001", "row": 1, "col": 2}], context["table_cells"])

    def test_llamaindex_adapter_accepts_node_with_score_and_mapping(self):
        results = [
            FakeNodeWithScore(FakeNode(record_metadata(element_refs=["node/1"]))),
            {
                "node": {
                    "metadata": record_metadata(
                        page_refs=["page/x"], element_refs=["node/2"]
                    )
                }
            },
        ]
        claims = [{"kind": "presence", "element_id": "node/2", "page": "page/x"}]

        context = build_llamaindex_context(results)
        citations = emit_llamaindex_citations(results, "The item is present.", claims)

        self.assertEqual(["node/1", "node/2"], context["elements"])
        self.assertEqual("node/2", citations["claims"][0]["citation"]["element_id"])

    def test_mixed_or_missing_fingerprint_fails_closed(self):
        assert_error(
            self,
            "mixed_document_fingerprints",
            lambda: build_langchain_context([
                FakeDocument(record_metadata()),
                FakeDocument(record_metadata(document_fingerprint="sha256:" + ("b" * 64))),
            ]),
        )
        assert_error(
            self,
            "missing_document_fingerprint",
            lambda: build_langchain_context([FakeDocument({"element_refs": ["e000001"]})]),
        )
        assert_error(
            self,
            "invalid_document_fingerprint",
            lambda: build_langchain_context([
                FakeDocument(record_metadata(document_fingerprint="foreign-document"))
            ]),
        )

    def test_missing_or_ambiguous_source_metadata_fails_closed(self):
        assert_error(
            self,
            "missing_source_ids",
            lambda: build_langchain_context([
                FakeDocument({"document_fingerprint": FINGERPRINT, "page": 0})
            ]),
        )
        assert_error(
            self,
            "invalid_source_ids",
            lambda: build_langchain_context([FakeDocument(record_metadata(page_refs="p0001"))]),
        )
        assert_error(self, "empty_retrieval_results", lambda: build_llamaindex_context([]))

    def test_unshown_id_and_unshown_table_cell_fail_closed(self):
        context = build_langchain_context([FakeDocument(record_metadata())])
        dangling = build_citation_emission(
            "An assertion.", [{"kind": "quote", "text": "assertion", "element_id": "e999999"}]
        )
        error = assert_error(
            self, "out_of_vocabulary", lambda: hydrate_citations(dangling, context)
        )
        self.assertEqual(1, error.claim_index)

        table = build_citation_emission(
            "$1",
            [{
                "kind": "table_cell",
                "text": "$1",
                "table_id": "t0001",
                "cell": {"row": 0, "col": 0},
            }],
        )
        assert_error(self, "out_of_vocabulary", lambda: hydrate_citations(table, context))

    def test_invalid_emission_shapes_and_configured_limit_fail_closed(self):
        invalid_claims = [
            {"kind": "quote", "text": "x"},
            {"kind": "presence", "text": "x", "page": "p0001"},
            {"kind": "value", "text": "x", "element_id": "e1", "span_id": "s1"},
            {
                "kind": "table_cell",
                "text": "x",
                "table_id": "t1",
                "cell": {"row": True, "col": 0},
            },
            {"kind": "quote", "text": "x", "page": "p1", "bbox": [0, 0, 1, 1]},
            {"kind": ["quote"], "text": "x", "page": "p1"},
        ]
        expected_codes = [
            "locator_missing",
            "invalid_claim",
            "locator_conflict",
            "invalid_claim",
            "invalid_claim",
            "invalid_claim",
        ]
        for claim, expected in zip(invalid_claims, expected_codes):
            with self.subTest(claim=claim):
                assert_error(
                    self,
                    expected,
                    lambda claim=claim: build_citation_emission("answer", [claim]),
                )

        assert_error(
            self,
            "claim_limit_exceeded",
            lambda: build_citation_emission(
                "answer", [{"kind": "presence", "page": "p1"}] * 2, max_claims=1
            ),
        )
        assert_error(
            self,
            "invalid_emission",
            lambda: build_citation_emission("   ", [{"kind": "presence", "page": "p1"}]),
        )

    def test_module_has_no_framework_cli_pdfium_or_network_imports(self):
        tree = ast.parse(EMIT_MODULE.read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        forbidden = {
            "langchain",
            "llama_index",
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "_cli",
        }
        self.assertEqual(set(), imports & forbidden)


if __name__ == "__main__":
    unittest.main()
