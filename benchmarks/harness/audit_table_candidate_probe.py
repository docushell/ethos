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
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "ethos-table-candidate-probe-audit-v1"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Ethos table-candidate probe coverage against markdown ground truth."
    )
    parser.add_argument("--probe-report", type=Path, required=True)
    parser.add_argument("--ground-truth-markdown-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args(argv)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def has_ground_truth_table(path: Path) -> bool:
    if not path.exists():
        return False
    return "<table" in path.read_text(encoding="utf-8", errors="replace").lower()


def median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def is_numeric_cell(text: str) -> bool:
    normalized = (
        text.strip()
        .replace(",", "")
        .replace("%", "")
        .replace("+", "")
        .replace("-", "")
        .replace("−", "")
    )
    return bool(normalized) and re.fullmatch(r"(\d+|\d*\.\d+)", normalized) is not None


def first_table_features(document: dict[str, Any]) -> dict[str, Any] | None:
    if document.get("status") != "pass" or int(document.get("tables_total", 0)) <= 0:
        return None

    probe_report = document.get("probe_report")
    if not probe_report:
        return None

    path = Path(str(probe_report))
    if not path.exists():
        return None

    report = read_json(path)
    tables = report.get("tables", [])
    if not tables:
        return None

    table = tables[0].get("table", {})
    cells = table.get("cells", [])
    rows_total = int(table.get("n_rows", 0))
    cols_total = int(table.get("n_cols", 0))
    if rows_total <= 0 or cols_total <= 0 or not cells:
        return None

    texts = [str(cell.get("text", "")).strip() for cell in cells]
    nonempty_texts = [text for text in texts if text]
    empty_cells = len(texts) - len(nonempty_texts)
    numeric_cells = [text for text in nonempty_texts if is_numeric_cell(text)]
    word_counts = [len(text.split()) for text in nonempty_texts]
    long_cells = [count for count in word_counts if count >= 4]

    cells_by_row: dict[int, list[dict[str, Any]]] = {
        row: [] for row in range(rows_total)
    }
    cells_by_col: dict[int, list[dict[str, Any]]] = {
        col: [] for col in range(cols_total)
    }
    for cell in cells:
        row = int(cell.get("row", -1))
        col = int(cell.get("col", -1))
        if row in cells_by_row:
            cells_by_row[row].append(cell)
        if col in cells_by_col:
            cells_by_col[col].append(cell)

    row_fill_counts = [
        sum(1 for cell in cells_by_row[row] if str(cell.get("text", "")).strip())
        for row in range(rows_total)
    ]

    col_lefts: list[float] = []
    col_rights: list[float] = []
    alignment_deviations: list[float] = []
    for col in range(cols_total):
        nonempty_cells = [
            cell for cell in cells_by_col[col] if str(cell.get("text", "")).strip()
        ]
        lefts = [float(cell["bbox"][0]) for cell in nonempty_cells if "bbox" in cell]
        rights = [float(cell["bbox"][2]) for cell in nonempty_cells if "bbox" in cell]
        left_median = median(lefts)
        right_median = median(rights)
        if left_median is not None and right_median is not None:
            col_lefts.append(left_median)
            col_rights.append(right_median)
            alignment_deviations.extend(abs(left - left_median) for left in lefts)

    gutters = [
        col_lefts[index + 1] - col_rights[index]
        for index in range(len(col_lefts) - 1)
    ]
    bbox = table.get("bbox", [0, 0, 0, 0])
    table_width = max(float(bbox[2] - bbox[0]), 1.0) if len(bbox) == 4 else 1.0

    return {
        "avg_words_per_nonempty_cell": (
            sum(word_counts) / len(word_counts) if word_counts else None
        ),
        "cols": cols_total,
        "empty_cell_ratio": empty_cells / len(texts),
        "fill_median_ratio": (
            median([float(count) for count in row_fill_counts]) / cols_total
            if row_fill_counts
            else None
        ),
        "long_cell_ratio": (
            len(long_cells) / len(nonempty_texts) if nonempty_texts else None
        ),
        "max_gutter_ratio": (
            max(gutters) / table_width if gutters else None
        ),
        "median_alignment_deviation_ratio": (
            median(alignment_deviations) / table_width
            if alignment_deviations
            else None
        ),
        "median_gutter_ratio": (
            median(gutters) / table_width if gutters else None
        ),
        "nonempty_cells": len(nonempty_texts),
        "numeric_cell_ratio": (
            len(numeric_cells) / len(nonempty_texts) if nonempty_texts else None
        ),
        "rows": rows_total,
        "single_word_cell_ratio": (
            sum(1 for count in word_counts if count == 1) / len(nonempty_texts)
            if nonempty_texts
            else None
        ),
    }


def classify_document(document: dict[str, Any], ground_truth_dir: Path) -> dict[str, Any]:
    doc_id = str(document["doc_id"])
    ground_truth_path = ground_truth_dir / f"{doc_id}.md"
    expected_table = has_ground_truth_table(ground_truth_path)
    candidate_present = (
        document.get("status") == "pass" and int(document.get("tables_total", 0)) > 0
    )

    if expected_table and candidate_present:
        classification = "true_positive"
    elif expected_table and not candidate_present:
        classification = "false_negative"
    elif not expected_table and candidate_present:
        classification = "false_positive"
    else:
        classification = "true_negative"

    return {
        "doc_id": doc_id,
        "candidate_present": candidate_present,
        "classification": classification,
        "expected_table": expected_table,
        "ground_truth": str(ground_truth_path),
        "first_table_features": first_table_features(document),
        "probe_report": document.get("probe_report"),
        "probe_status": document.get("status"),
        "tables_total": int(document.get("tables_total", 0)),
    }


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def feature_value(document: dict[str, Any], key: str) -> float | None:
    features = document.get("first_table_features")
    if features is None:
        return None
    value = features.get(key)
    if value is None:
        return None
    return float(value)


def rejects_tight_gutter_unstable_alignment(document: dict[str, Any]) -> bool:
    median_gutter = feature_value(document, "median_gutter_ratio")
    alignment = feature_value(document, "median_alignment_deviation_ratio")
    return median_gutter is not None and alignment is not None and median_gutter <= 0.005 and alignment >= 0.008


def rejects_no_long_cells_tight_gutter(document: dict[str, Any]) -> bool:
    long_cells = feature_value(document, "long_cell_ratio")
    median_gutter = feature_value(document, "median_gutter_ratio")
    return long_cells is not None and median_gutter is not None and long_cells <= 0.0 and median_gutter <= 0.02


def rejects_very_tall_low_numeric(document: dict[str, Any]) -> bool:
    rows = feature_value(document, "rows")
    numeric = feature_value(document, "numeric_cell_ratio")
    return rows is not None and numeric is not None and rows >= 30 and numeric <= 0.3


def rejects_too_many_columns(document: dict[str, Any]) -> bool:
    rows = feature_value(document, "rows")
    cols = feature_value(document, "cols")
    return rows is not None and cols is not None and rows >= 10 and cols >= 12


def rejects_dense_low_fill_tight_gutter(document: dict[str, Any]) -> bool:
    empty = feature_value(document, "empty_cell_ratio")
    fill = feature_value(document, "fill_median_ratio")
    return empty is not None and fill is not None and empty <= 0.2 and fill <= 0.9


GATE_TRIALS = [
    {
        "description": "Reject narrow-gutter prose-like grids with unstable column starts.",
        "name": "tight_gutter_unstable_alignment",
        "rejects": rejects_tight_gutter_unstable_alignment,
    },
    {
        "description": "Reject tight-gutter grids whose cells are all one to three words.",
        "name": "no_long_cells_tight_gutter",
        "rejects": rejects_no_long_cells_tight_gutter,
    },
    {
        "description": "Reject very tall low-numeric grids, usually page-flow prose artifacts.",
        "name": "very_tall_low_numeric",
        "rejects": rejects_very_tall_low_numeric,
    },
    {
        "description": "Reject tall candidates with many columns, usually word-position grids.",
        "name": "too_many_columns",
        "rejects": rejects_too_many_columns,
    },
    {
        "description": "Reject dense candidates with weak row fill and tight gutters.",
        "name": "dense_low_fill_tight_gutter",
        "rejects": rejects_dense_low_fill_tight_gutter,
    },
]


def gate_trial_summary(
    documents: list[dict[str, Any]],
    name: str,
    description: str,
    rejected_doc_ids: set[str],
) -> dict[str, Any]:
    rejected = [doc for doc in documents if doc["doc_id"] in rejected_doc_ids]
    retained = [doc for doc in documents if doc["doc_id"] not in rejected_doc_ids]
    retained_candidates = [doc for doc in retained if doc["candidate_present"]]
    retained_tp = [
        doc for doc in retained_candidates if doc["classification"] == "true_positive"
    ]
    retained_fp = [
        doc for doc in retained_candidates if doc["classification"] == "false_positive"
    ]
    rejected_tp = [doc for doc in rejected if doc["classification"] == "true_positive"]
    rejected_fp = [doc for doc in rejected if doc["classification"] == "false_positive"]
    expected_table = [doc for doc in documents if doc["expected_table"]]

    return {
        "candidate_docs_after": len(retained_candidates),
        "description": description,
        "false_positive_rejections": len(rejected_fp),
        "name": name,
        "precision_doc_level_after": ratio(
            len(retained_tp), len(retained_tp) + len(retained_fp)
        ),
        "recall_doc_level_after": ratio(len(retained_tp), len(expected_table)),
        "rejected_doc_ids": [doc["doc_id"] for doc in rejected],
        "true_positive_rejections": len(rejected_tp),
    }


def evaluate_gate_trials(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    trials: list[dict[str, Any]] = []
    combined_rejections: set[str] = set()

    for trial in GATE_TRIALS:
        rejected_doc_ids = {
            doc["doc_id"]
            for doc in documents
            if doc["candidate_present"] and trial["rejects"](doc)
        }
        combined_rejections.update(rejected_doc_ids)
        trials.append(
            gate_trial_summary(
                documents,
                str(trial["name"]),
                str(trial["description"]),
                rejected_doc_ids,
            )
        )

    trials.append(
        gate_trial_summary(
            documents,
            "combined_probe_precision_trial_v1",
            "Union of the current corpus-derived zero-true-positive-loss probe gates.",
            combined_rejections,
        )
    )
    return trials


def build_audit(probe_report: dict[str, Any], ground_truth_dir: Path) -> dict[str, Any]:
    documents = [
        classify_document(document, ground_truth_dir)
        for document in probe_report.get("documents", [])
    ]
    true_positive = [doc for doc in documents if doc["classification"] == "true_positive"]
    false_positive = [doc for doc in documents if doc["classification"] == "false_positive"]
    false_negative = [doc for doc in documents if doc["classification"] == "false_negative"]
    true_negative = [doc for doc in documents if doc["classification"] == "true_negative"]
    expected_table = [doc for doc in documents if doc["expected_table"]]
    expected_non_table = [doc for doc in documents if not doc["expected_table"]]
    candidate_present = [doc for doc in documents if doc["candidate_present"]]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "probe_report_summary": probe_report.get("summary", {}),
        "summary": {
            "candidate_docs": len(candidate_present),
            "docs_total": len(documents),
            "expected_non_table_docs": len(expected_non_table),
            "expected_table_docs": len(expected_table),
            "false_negative_docs": len(false_negative),
            "false_positive_docs": len(false_positive),
            "precision_doc_level": ratio(
                len(true_positive), len(true_positive) + len(false_positive)
            ),
            "recall_doc_level": ratio(
                len(true_positive), len(true_positive) + len(false_negative)
            ),
            "true_negative_docs": len(true_negative),
            "true_positive_docs": len(true_positive),
        },
        "documents": documents,
        "gate_trials": evaluate_gate_trials(documents),
        "review_sets": {
            "false_negative_doc_ids": [doc["doc_id"] for doc in false_negative],
            "false_positive_doc_ids": [doc["doc_id"] for doc in false_positive],
            "true_negative_doc_ids": [doc["doc_id"] for doc in true_negative],
            "true_positive_doc_ids": [doc["doc_id"] for doc in true_positive],
        },
    }


def main() -> None:
    args = parse_args()
    probe_report = read_json(args.probe_report)
    audit = build_audit(probe_report, args.ground_truth_markdown_dir)
    write_json(args.out, audit)
    print(f"table candidate audit: {audit['summary']}")


if __name__ == "__main__":
    main()
