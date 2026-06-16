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

import tempfile
import unittest
import json
from pathlib import Path

import audit_table_candidate_probe


def write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_json(path: Path, value: object) -> Path:
    return write_text(path, json.dumps(value) + "\n")


class TableCandidateProbeAuditTests(unittest.TestCase):
    def test_audit_classifies_doc_level_precision_and_recall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gt = root / "ground-truth"
            write_text(gt / "tp.md", "<table><tr><td>A</td></tr></table>\n")
            write_text(gt / "fn.md", "<table><tr><td>B</td></tr></table>\n")
            write_text(gt / "fp.md", "plain prose\n")
            write_text(gt / "tn.md", "plain prose\n")
            probe_report = {
                "summary": {"documents_total": 4},
                "documents": [
                    {"doc_id": "tp", "status": "pass", "tables_total": 1},
                    {"doc_id": "fn", "status": "pass", "tables_total": 0},
                    {"doc_id": "fp", "status": "pass", "tables_total": 1},
                    {"doc_id": "tn", "status": "pass", "tables_total": 0},
                ],
            }

            audit = audit_table_candidate_probe.build_audit(probe_report, gt)

        self.assertEqual(audit["schema_version"], "ethos-table-candidate-probe-audit-v1")
        self.assertEqual(
            audit["summary"],
            {
                "candidate_docs": 2,
                "docs_total": 4,
                "expected_non_table_docs": 2,
                "expected_table_docs": 2,
                "false_negative_docs": 1,
                "false_positive_docs": 1,
                "precision_doc_level": 0.5,
                "recall_doc_level": 0.5,
                "true_negative_docs": 1,
                "true_positive_docs": 1,
            },
        )
        self.assertEqual(audit["review_sets"]["false_negative_doc_ids"], ["fn"])
        self.assertEqual(audit["review_sets"]["false_positive_doc_ids"], ["fp"])
        self.assertEqual(audit["review_sets"]["true_negative_doc_ids"], ["tn"])
        self.assertEqual(audit["review_sets"]["true_positive_doc_ids"], ["tp"])

    def test_failed_probe_without_candidate_counts_as_miss_for_table_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gt = root / "ground-truth"
            write_text(gt / "sample.md", "<table><tr><td>A</td></tr></table>\n")
            probe_report = {
                "documents": [
                    {
                        "doc_id": "sample",
                        "stage": "parse",
                        "status": "fail",
                    }
                ],
            }

            audit = audit_table_candidate_probe.build_audit(probe_report, gt)

        self.assertEqual(audit["summary"]["false_negative_docs"], 1)
        self.assertEqual(audit["documents"][0]["classification"], "false_negative")
        self.assertFalse(audit["documents"][0]["candidate_present"])

    def test_first_table_features_are_extracted_from_probe_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gt = root / "ground-truth"
            write_text(gt / "sample.md", "<table><tr><td>A</td></tr></table>\n")
            probe = write_json(
                root / "sample.tables.json",
                {
                    "tables": [
                        {
                            "table": {
                                "bbox": [0, 0, 6_000, 2_400],
                                "n_cols": 3,
                                "n_rows": 2,
                                "cells": [
                                    {
                                        "bbox": [0, 0, 600, 400],
                                        "col": 0,
                                        "row": 0,
                                        "text": "Name",
                                    },
                                    {
                                        "bbox": [2_000, 0, 2_600, 400],
                                        "col": 1,
                                        "row": 0,
                                        "text": "2026",
                                    },
                                    {
                                        "bbox": [4_000, 0, 4_600, 400],
                                        "col": 2,
                                        "row": 0,
                                        "text": "Long text cell",
                                    },
                                    {
                                        "bbox": [0, 1_000, 600, 1_400],
                                        "col": 0,
                                        "row": 1,
                                        "text": "Alpha",
                                    },
                                    {
                                        "bbox": [2_000, 1_000, 2_600, 1_400],
                                        "col": 1,
                                        "row": 1,
                                        "text": "42",
                                    },
                                    {
                                        "bbox": [4_000, 1_000, 4_600, 1_400],
                                        "col": 2,
                                        "row": 1,
                                        "text": "",
                                    },
                                ],
                            }
                        }
                    ]
                },
            )
            audit = audit_table_candidate_probe.build_audit(
                {
                    "documents": [
                        {
                            "doc_id": "sample",
                            "probe_report": str(probe),
                            "status": "pass",
                            "tables_total": 1,
                        }
                    ]
                },
                gt,
            )

        features = audit["documents"][0]["first_table_features"]
        self.assertEqual(features["rows"], 2)
        self.assertEqual(features["cols"], 3)
        self.assertEqual(features["nonempty_cells"], 5)
        self.assertEqual(features["empty_cell_ratio"], 1 / 6)
        self.assertEqual(features["numeric_cell_ratio"], 2 / 5)
        self.assertEqual(features["single_word_cell_ratio"], 4 / 5)
        self.assertEqual(features["long_cell_ratio"], 0)
        self.assertEqual(features["fill_median_ratio"], 5 / 6)
        self.assertAlmostEqual(features["median_gutter_ratio"], 1_400 / 6_000)
        self.assertAlmostEqual(features["max_gutter_ratio"], 1_400 / 6_000)
        self.assertAlmostEqual(features["median_alignment_deviation_ratio"], 0)

    def test_gate_trials_report_precision_and_recall_after_rejections(self) -> None:
        documents = [
            {
                "candidate_present": True,
                "classification": "true_positive",
                "doc_id": "tp",
                "expected_table": True,
                "first_table_features": {
                    "cols": 4,
                    "empty_cell_ratio": 0.25,
                    "fill_median_ratio": 1.0,
                    "long_cell_ratio": 0.25,
                    "median_alignment_deviation_ratio": 0.0,
                    "median_gutter_ratio": 0.08,
                    "numeric_cell_ratio": 0.5,
                    "rows": 4,
                },
            },
            {
                "candidate_present": True,
                "classification": "false_positive",
                "doc_id": "fp-tight-align",
                "expected_table": False,
                "first_table_features": {
                    "cols": 5,
                    "empty_cell_ratio": 0.1,
                    "fill_median_ratio": 1.0,
                    "long_cell_ratio": 0.5,
                    "median_alignment_deviation_ratio": 0.01,
                    "median_gutter_ratio": 0.004,
                    "numeric_cell_ratio": 0.1,
                    "rows": 6,
                },
            },
            {
                "candidate_present": True,
                "classification": "false_positive",
                "doc_id": "fp-short-tight",
                "expected_table": False,
                "first_table_features": {
                    "cols": 4,
                    "empty_cell_ratio": 0.1,
                    "fill_median_ratio": 1.0,
                    "long_cell_ratio": 0.0,
                    "median_alignment_deviation_ratio": 0.0,
                    "median_gutter_ratio": 0.01,
                    "numeric_cell_ratio": 0.1,
                    "rows": 6,
                },
            },
            {
                "candidate_present": True,
                "classification": "false_positive",
                "doc_id": "fp-retained",
                "expected_table": False,
                "first_table_features": {
                    "cols": 4,
                    "empty_cell_ratio": 0.25,
                    "fill_median_ratio": 1.0,
                    "long_cell_ratio": 0.25,
                    "median_alignment_deviation_ratio": 0.0,
                    "median_gutter_ratio": 0.08,
                    "numeric_cell_ratio": 0.1,
                    "rows": 6,
                },
            },
            {
                "candidate_present": False,
                "classification": "true_negative",
                "doc_id": "tn",
                "expected_table": False,
                "first_table_features": None,
            },
        ]

        trials = audit_table_candidate_probe.evaluate_gate_trials(documents)

        tight_alignment = next(
            trial
            for trial in trials
            if trial["name"] == "tight_gutter_unstable_alignment"
        )
        self.assertEqual(tight_alignment["false_positive_rejections"], 1)
        self.assertEqual(tight_alignment["true_positive_rejections"], 0)
        self.assertEqual(tight_alignment["rejected_doc_ids"], ["fp-tight-align"])

        combined = trials[-1]
        self.assertEqual(combined["name"], "combined_probe_precision_trial_v1")
        self.assertEqual(combined["candidate_docs_after"], 2)
        self.assertEqual(combined["false_positive_rejections"], 2)
        self.assertEqual(combined["true_positive_rejections"], 0)
        self.assertEqual(
            combined["rejected_doc_ids"], ["fp-tight-align", "fp-short-tight"]
        )
        self.assertEqual(combined["precision_doc_level_after"], 0.5)
        self.assertEqual(combined["recall_doc_level_after"], 1.0)


if __name__ == "__main__":
    unittest.main()
