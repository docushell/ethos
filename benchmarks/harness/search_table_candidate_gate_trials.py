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

import argparse
import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = "ethos-table-candidate-gate-search-v1"

FEATURE_KEYS = [
    "rows",
    "cols",
    "empty_cell_ratio",
    "numeric_cell_ratio",
    "avg_words_per_nonempty_cell",
    "long_cell_ratio",
    "single_word_cell_ratio",
    "fill_median_ratio",
    "max_gutter_ratio",
    "median_gutter_ratio",
    "median_alignment_deviation_ratio",
    "nonempty_cells",
]

DEFAULT_BASELINE_GATE = "combined_probe_precision_trial_v1"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search audited table-candidate features for precision gate trials."
    )
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--baseline-gate", default=DEFAULT_BASELINE_GATE)
    parser.add_argument("--max-rules", type=int, default=50)
    parser.add_argument("--max-true-positive-rejections", type=int, default=0)
    parser.add_argument("--min-false-positive-rejections", type=int, default=5)
    parser.add_argument("--pair-seed-min-false-positive-rejections", type=int, default=5)
    parser.add_argument("--pair-seed-max-true-positive-rejections", type=int, default=3)
    return parser.parse_args(argv)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def feature_value(document: dict[str, Any], key: str) -> float | None:
    features = document.get("first_table_features")
    if not features:
        return None
    value = features.get(key)
    if value is None:
        return None
    return float(value)


def baseline_rejections(audit: dict[str, Any], gate_name: str | None) -> set[str]:
    if gate_name is None or gate_name == "":
        return set()
    for gate in audit.get("gate_trials", []):
        if gate.get("name") == gate_name:
            return {str(doc_id) for doc_id in gate.get("rejected_doc_ids", [])}
    raise ValueError(f"baseline gate not found: {gate_name}")


def candidate_documents(
    audit: dict[str, Any],
    rejected_doc_ids: set[str],
) -> list[dict[str, Any]]:
    return [
        document
        for document in audit.get("documents", [])
        if document.get("candidate_present")
        and document.get("first_table_features")
        and document.get("doc_id") not in rejected_doc_ids
    ]


def metric_summary(
    documents: list[dict[str, Any]],
    rejected_doc_ids: set[str],
) -> dict[str, Any]:
    expected_table = [doc for doc in documents if doc.get("expected_table")]
    retained_candidates = [
        doc
        for doc in documents
        if doc.get("candidate_present") and doc.get("doc_id") not in rejected_doc_ids
    ]
    retained_tp = [
        doc for doc in retained_candidates if doc.get("classification") == "true_positive"
    ]
    retained_fp = [
        doc for doc in retained_candidates if doc.get("classification") == "false_positive"
    ]
    rejected_tp = [
        doc
        for doc in documents
        if doc.get("doc_id") in rejected_doc_ids
        and doc.get("classification") == "true_positive"
    ]
    rejected_fp = [
        doc
        for doc in documents
        if doc.get("doc_id") in rejected_doc_ids
        and doc.get("classification") == "false_positive"
    ]

    return {
        "candidate_docs_after": len(retained_candidates),
        "false_positive_rejections": len(rejected_fp),
        "precision_doc_level_after": ratio(
            len(retained_tp), len(retained_tp) + len(retained_fp)
        ),
        "recall_doc_level_after": ratio(len(retained_tp), len(expected_table)),
        "true_positive_rejections": len(rejected_tp),
    }


def condition_matches(
    document: dict[str, Any],
    field: str,
    op: str,
    threshold: float,
) -> bool:
    value = feature_value(document, field)
    if value is None:
        return False
    if op == "<=":
        return value <= threshold
    if op == ">=":
        return value >= threshold
    raise ValueError(f"unsupported operator: {op}")


def condition_record(
    documents: list[dict[str, Any]],
    field: str,
    op: str,
    threshold: float,
    rejected_doc_ids: set[str],
) -> dict[str, Any]:
    trial_rejections = {
        str(doc["doc_id"])
        for doc in documents
        if doc.get("candidate_present") and condition_matches(doc, field, op, threshold)
    }
    combined_rejections = rejected_doc_ids | trial_rejections
    summary = metric_summary(documents, combined_rejections)
    trial_rejected = [
        doc for doc in documents if str(doc.get("doc_id")) in trial_rejections
    ]
    summary.update(
        {
            "condition": {
                "field": field,
                "op": op,
                "threshold": threshold,
            },
            "rejected_doc_ids": sorted(trial_rejections),
            "trial_false_positive_rejections": sum(
                1
                for doc in trial_rejected
                if doc.get("classification") == "false_positive"
            ),
            "trial_true_positive_rejections": sum(
                1
                for doc in trial_rejected
                if doc.get("classification") == "true_positive"
            ),
        }
    )
    return summary


def primitive_conditions(
    documents: list[dict[str, Any]],
    baseline_rejected_doc_ids: set[str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for field in FEATURE_KEYS:
        thresholds = sorted(
            {
                feature_value(document, field)
                for document in documents
                if feature_value(document, field) is not None
            }
        )
        for threshold in thresholds:
            assert threshold is not None
            for op in ("<=", ">="):
                records.append(
                    condition_record(
                        documents,
                        field,
                        op,
                        threshold,
                        baseline_rejected_doc_ids,
                    )
                )
    return records


def passes_policy(
    record: dict[str, Any],
    *,
    max_true_positive_rejections: int,
    min_false_positive_rejections: int,
) -> bool:
    return (
        int(record["trial_true_positive_rejections"]) <= max_true_positive_rejections
        and int(record["trial_false_positive_rejections"])
        >= min_false_positive_rejections
    )


def sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda record: (
            -int(record["trial_false_positive_rejections"]),
            int(record["trial_true_positive_rejections"]),
            str(record.get("condition", record.get("conditions"))),
        ),
    )


def conjunction_record(
    documents: list[dict[str, Any]],
    baseline_rejected_doc_ids: set[str],
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    left_condition = left["condition"]
    right_condition = right["condition"]
    trial_rejections = {
        str(doc["doc_id"])
        for doc in documents
        if doc.get("candidate_present")
        and condition_matches(
            doc,
            str(left_condition["field"]),
            str(left_condition["op"]),
            float(left_condition["threshold"]),
        )
        and condition_matches(
            doc,
            str(right_condition["field"]),
            str(right_condition["op"]),
            float(right_condition["threshold"]),
        )
    }
    combined_rejections = baseline_rejected_doc_ids | trial_rejections
    summary = metric_summary(documents, combined_rejections)
    trial_rejected = [
        doc for doc in documents if str(doc.get("doc_id")) in trial_rejections
    ]
    summary.update(
        {
            "conditions": [left_condition, right_condition],
            "rejected_doc_ids": sorted(trial_rejections),
            "trial_false_positive_rejections": sum(
                1
                for doc in trial_rejected
                if doc.get("classification") == "false_positive"
            ),
            "trial_true_positive_rejections": sum(
                1
                for doc in trial_rejected
                if doc.get("classification") == "true_positive"
            ),
        }
    )
    return summary


def search_gate_trials(
    audit: dict[str, Any],
    *,
    baseline_gate: str | None,
    max_rules: int,
    max_true_positive_rejections: int,
    min_false_positive_rejections: int,
    pair_seed_min_false_positive_rejections: int,
    pair_seed_max_true_positive_rejections: int,
) -> dict[str, Any]:
    baseline_rejected = baseline_rejections(audit, baseline_gate)
    documents = [
        doc
        for doc in audit.get("documents", [])
        if doc.get("candidate_present") and doc.get("first_table_features")
    ]
    search_docs = candidate_documents(audit, baseline_rejected)
    primitives = primitive_conditions(search_docs, baseline_rejected)
    single_feature_rules = sort_records(
        [
            record
            for record in primitives
            if passes_policy(
                record,
                max_true_positive_rejections=max_true_positive_rejections,
                min_false_positive_rejections=min_false_positive_rejections,
            )
        ]
    )[:max_rules]

    pair_seeds = [
        record
        for record in primitives
        if passes_policy(
            record,
            max_true_positive_rejections=pair_seed_max_true_positive_rejections,
            min_false_positive_rejections=pair_seed_min_false_positive_rejections,
        )
    ]
    pair_records: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for left, right in combinations(pair_seeds, 2):
        left_condition = left["condition"]
        right_condition = right["condition"]
        if left_condition["field"] == right_condition["field"]:
            continue
        pair_key = tuple(
            sorted(
                [
                    json.dumps(left_condition, sort_keys=True),
                    json.dumps(right_condition, sort_keys=True),
                ]
            )
        )
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)
        record = conjunction_record(search_docs, baseline_rejected, left, right)
        if passes_policy(
            record,
            max_true_positive_rejections=max_true_positive_rejections,
            min_false_positive_rejections=min_false_positive_rejections,
        ):
            pair_records.append(record)

    false_positive_docs = [
        doc for doc in search_docs if doc.get("classification") == "false_positive"
    ]
    true_positive_docs = [
        doc for doc in search_docs if doc.get("classification") == "true_positive"
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "baseline_gate": baseline_gate,
        "baseline_rejected_doc_ids": sorted(baseline_rejected),
        "search_policy": {
            "max_true_positive_rejections": max_true_positive_rejections,
            "min_false_positive_rejections": min_false_positive_rejections,
            "pair_seed_max_true_positive_rejections": pair_seed_max_true_positive_rejections,
            "pair_seed_min_false_positive_rejections": pair_seed_min_false_positive_rejections,
        },
        "summary": {
            "baseline_rejections": len(baseline_rejected),
            "candidate_docs_with_features": len(documents),
            "false_positive_docs_after_baseline": len(false_positive_docs),
            "single_feature_rules": len(single_feature_rules),
            "two_feature_conjunctions": min(len(pair_records), max_rules),
            "true_positive_docs_after_baseline": len(true_positive_docs),
        },
        "single_feature_rules": single_feature_rules,
        "two_feature_conjunctions": sort_records(pair_records)[:max_rules],
    }


def main() -> None:
    args = parse_args()
    audit = read_json(args.audit)
    result = search_gate_trials(
        audit,
        baseline_gate=args.baseline_gate,
        max_rules=args.max_rules,
        max_true_positive_rejections=args.max_true_positive_rejections,
        min_false_positive_rejections=args.min_false_positive_rejections,
        pair_seed_min_false_positive_rejections=args.pair_seed_min_false_positive_rejections,
        pair_seed_max_true_positive_rejections=args.pair_seed_max_true_positive_rejections,
    )
    write_json(args.out, result)
    print(f"table candidate gate search: {result['summary']}")


if __name__ == "__main__":
    main()
