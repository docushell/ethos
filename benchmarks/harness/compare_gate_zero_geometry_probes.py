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

"""Compare debug PDFium geometry probe JSON across Gate Zero platforms."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import diff_gate_zero_docs


SIGNAL_GROUPS = {
    "char_box": {"char_box", "char_box_union"},
    "loose_char_box": {"loose_char_box", "loose_char_box_union"},
    "char_origin": {"char_origin", "first_origin", "last_origin"},
    "text_rects": {"text_rects", "text_rect_union"},
}
SIGNAL_KEYS = set().union(*SIGNAL_GROUPS.values())
VOLATILE_KEYS = {"backend"}


def load_probe(path: Path) -> dict[str, Any]:
    value = diff_gate_zero_docs.load_json(path)
    if value.get("schema_version") != "ethos-pdfium-geometry-probe-v1":
        raise ValueError(f"{path} is not an Ethos PDFium geometry probe")
    return value


def strip_keys(value: Any, keys: set[str]) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_keys(child, keys)
            for key, child in value.items()
            if key not in keys
        }
    if isinstance(value, list):
        return [strip_keys(child, keys) for child in value]
    return value


def collect_keys(value: Any, keys: set[str], pointer: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = diff_gate_zero_docs.join_pointer(pointer, key)
            if key in keys:
                out[child_pointer] = child
            out.update(collect_keys(child, keys, child_pointer))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.update(
                collect_keys(
                    child,
                    keys,
                    diff_gate_zero_docs.join_pointer(pointer, index),
                )
            )
    return out


def sample_diffs(diffs: list[dict[str, Any]], max_diffs: int) -> list[dict[str, Any]]:
    return [
        {
            "pointer": diff["pointer"],
            "kind": diff["kind"],
            "left_kind": diff_gate_zero_docs.value_kind(diff["left"]),
            "right_kind": diff_gate_zero_docs.value_kind(diff["right"]),
            "left": diff_gate_zero_docs.shorten(diff["left"]),
            "right": diff_gate_zero_docs.shorten(diff["right"]),
        }
        for diff in diffs[:max_diffs]
    ]


def compare_probe_pair(
    left: dict[str, Any],
    right: dict[str, Any],
    max_diffs: int,
) -> dict[str, Any]:
    structural_left = strip_keys(left, SIGNAL_KEYS | VOLATILE_KEYS)
    structural_right = strip_keys(right, SIGNAL_KEYS | VOLATILE_KEYS)
    structural_diffs = diff_gate_zero_docs.diff_values(structural_left, structural_right)
    signals = []
    for signal, keys in SIGNAL_GROUPS.items():
        left_signal = collect_keys(left, keys)
        right_signal = collect_keys(right, keys)
        diffs = diff_gate_zero_docs.diff_values(left_signal, right_signal)
        signals.append(
            {
                "signal": signal,
                "status": "matched" if not diffs else "diverged",
                "diff_count": len(diffs),
                "sample_diffs": sample_diffs(diffs, max_diffs),
            }
        )
    return {
        "structural_status": "matched" if not structural_diffs else "diverged",
        "structural_diff_count": len(structural_diffs),
        "structural_sample_diffs": sample_diffs(structural_diffs, max_diffs),
        "signals": signals,
    }


def probe_path(root: Path, doc_id: str) -> Path:
    return root / f"{doc_id}.json"


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    doc_ids = args.doc_id or diff_gate_zero_docs.DEFAULT_DOC_IDS
    comparisons = []
    signal_totals = {signal: 0 for signal in SIGNAL_GROUPS}
    signal_diverged_docs = {signal: [] for signal in SIGNAL_GROUPS}

    for doc_id in doc_ids:
        left_path = probe_path(args.left_dir, doc_id)
        right_path = probe_path(args.right_dir, doc_id)
        comparison = compare_probe_pair(
            load_probe(left_path),
            load_probe(right_path),
            args.max_diffs,
        )
        for signal_result in comparison["signals"]:
            signal = signal_result["signal"]
            signal_totals[signal] += signal_result["diff_count"]
            if signal_result["status"] == "diverged":
                signal_diverged_docs[signal].append(doc_id)
        comparisons.append(
            {
                "doc_id": doc_id,
                "left": str(left_path),
                "right": str(right_path),
                **comparison,
            }
        )

    signal_summary = [
        {
            "signal": signal,
            "status": "matched" if not signal_diverged_docs[signal] else "diverged",
            "diff_count": signal_totals[signal],
            "diverged_doc_ids": signal_diverged_docs[signal],
        }
        for signal in SIGNAL_GROUPS
    ]
    return {
        "schema_version": "ethos-gate-zero-geometry-probe-comparison-v1",
        "left_label": args.left_label,
        "right_label": args.right_label,
        "left_dir": str(args.left_dir),
        "right_dir": str(args.right_dir),
        "comparisons": comparisons,
        "summary": {
            "documents_total": len(comparisons),
            "structural_matches": sum(
                comparison["structural_status"] == "matched"
                for comparison in comparisons
            ),
            "signals": signal_summary,
            "matched_signals": [
                item["signal"] for item in signal_summary if item["status"] == "matched"
            ],
            "diverged_signals": [
                item["signal"] for item in signal_summary if item["status"] == "diverged"
            ],
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-dir", type=Path, required=True)
    parser.add_argument("--right-dir", type=Path, required=True)
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument("--doc-id", action="append")
    parser.add_argument("--max-diffs", type=int, default=10)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--stdout", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.max_diffs < 0:
        print("max-diffs must be >= 0", file=sys.stderr)
        return 2
    try:
        report = build_report(args)
    except Exception as exc:
        print(f"Gate Zero geometry probe comparison: {exc}", file=sys.stderr)
        return 2

    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded + "\n", encoding="utf-8")
    if args.stdout or not args.out:
        print(encoded)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
