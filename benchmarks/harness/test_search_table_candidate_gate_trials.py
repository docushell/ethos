#!/usr/bin/env python3
from __future__ import annotations

import unittest

import search_table_candidate_gate_trials


def doc(
    doc_id: str,
    classification: str,
    *,
    expected_table: bool,
    long_cell_ratio: float,
    avg_words_per_nonempty_cell: float,
) -> dict:
    return {
        "candidate_present": True,
        "classification": classification,
        "doc_id": doc_id,
        "expected_table": expected_table,
        "first_table_features": {
            "avg_words_per_nonempty_cell": avg_words_per_nonempty_cell,
            "cols": 4,
            "empty_cell_ratio": 0.0,
            "fill_median_ratio": 1.0,
            "long_cell_ratio": long_cell_ratio,
            "max_gutter_ratio": 0.05,
            "median_alignment_deviation_ratio": 0.0,
            "median_gutter_ratio": 0.04,
            "nonempty_cells": 20,
            "numeric_cell_ratio": 0.0,
            "rows": 5,
            "single_word_cell_ratio": 0.5,
        },
    }


class TableCandidateGateSearchTests(unittest.TestCase):
    def test_search_finds_zero_true_positive_loss_single_feature_rule(self) -> None:
        audit = {
            "documents": [
                doc(
                    "tp",
                    "true_positive",
                    expected_table=True,
                    long_cell_ratio=0.2,
                    avg_words_per_nonempty_cell=2.0,
                ),
                doc(
                    "fp-a",
                    "false_positive",
                    expected_table=False,
                    long_cell_ratio=0.5,
                    avg_words_per_nonempty_cell=4.0,
                ),
                doc(
                    "fp-b",
                    "false_positive",
                    expected_table=False,
                    long_cell_ratio=0.6,
                    avg_words_per_nonempty_cell=4.5,
                ),
                doc(
                    "fp-baseline",
                    "false_positive",
                    expected_table=False,
                    long_cell_ratio=0.7,
                    avg_words_per_nonempty_cell=5.0,
                ),
            ],
            "gate_trials": [
                {
                    "name": "combined_probe_precision_trial_v1",
                    "rejected_doc_ids": ["fp-baseline"],
                }
            ],
        }

        result = search_table_candidate_gate_trials.search_gate_trials(
            audit,
            baseline_gate="combined_probe_precision_trial_v1",
            max_rules=5,
            max_true_positive_rejections=0,
            min_false_positive_rejections=2,
            pair_seed_min_false_positive_rejections=1,
            pair_seed_max_true_positive_rejections=1,
        )

        self.assertEqual(result["summary"]["baseline_rejections"], 1)
        self.assertEqual(result["summary"]["true_positive_docs_after_baseline"], 1)
        self.assertEqual(result["summary"]["false_positive_docs_after_baseline"], 2)

        top_rule = next(
            rule
            for rule in result["single_feature_rules"]
            if rule["condition"] == {
                "field": "long_cell_ratio",
                "op": ">=",
                "threshold": 0.5,
            }
        )
        self.assertEqual(top_rule["trial_false_positive_rejections"], 2)
        self.assertEqual(top_rule["trial_true_positive_rejections"], 0)
        self.assertEqual(top_rule["precision_doc_level_after"], 1.0)
        self.assertEqual(top_rule["recall_doc_level_after"], 1.0)
        self.assertEqual(top_rule["rejected_doc_ids"], ["fp-a", "fp-b"])

    def test_missing_baseline_gate_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "baseline gate not found"):
            search_table_candidate_gate_trials.search_gate_trials(
                {"documents": [], "gate_trials": []},
                baseline_gate="missing",
                max_rules=5,
                max_true_positive_rejections=0,
                min_false_positive_rejections=1,
                pair_seed_min_false_positive_rejections=1,
                pair_seed_max_true_positive_rejections=0,
            )


if __name__ == "__main__":
    unittest.main()
