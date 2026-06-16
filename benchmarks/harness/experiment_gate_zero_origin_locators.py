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

"""Evaluate stable origin-derived run locators from PDFium geometry probes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import compare_gate_zero_geometry_probes
import diff_gate_zero_docs
import run_gate_zero


LOCATOR_POLICY = {
    "id": "origin-run-locator-v1",
    "description": (
        "Diagnostic run locator derived from page id, parser-like run text/range, "
        "first/last FPDFText_GetCharOrigin points, and deterministic font identity."
    ),
    "fields": [
        "page",
        "run_index",
        "text",
        "char_start",
        "char_end",
        "first_origin",
        "last_origin",
        "font_id",
        "font_size_q",
    ],
}


def run_locator(page: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    return {
        "page": page.get("id"),
        "run_index": run.get("index"),
        "text": run.get("text"),
        "char_start": run.get("char_start"),
        "char_end": run.get("char_end"),
        "first_origin": run.get("first_origin"),
        "last_origin": run.get("last_origin"),
        "font_id": run.get("font_id"),
        "font_size_q": run.get("font_size_q"),
    }


def derive_locators(probe: dict[str, Any]) -> list[dict[str, Any]]:
    locators = []
    for page in probe.get("pages", []):
        if not isinstance(page, dict):
            continue
        for run in page.get("runs", []):
            if isinstance(run, dict):
                locators.append(run_locator(page, run))
    return locators


def locator_digest(locators: list[dict[str, Any]]) -> str:
    return run_gate_zero.sha256_c14n_value(locators)


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


def compare_locator_pair(
    left: dict[str, Any],
    right: dict[str, Any],
    max_diffs: int,
) -> dict[str, Any]:
    left_locators = derive_locators(left)
    right_locators = derive_locators(right)
    diffs = diff_gate_zero_docs.diff_values(left_locators, right_locators)
    return {
        "status": "matched" if not diffs else "diverged",
        "left_locator_count": len(left_locators),
        "right_locator_count": len(right_locators),
        "left_locator_sha256": locator_digest(left_locators),
        "right_locator_sha256": locator_digest(right_locators),
        "diff_count": len(diffs),
        "sample_diffs": sample_diffs(diffs, max_diffs),
    }


def probe_path(root: Path, doc_id: str) -> Path:
    return root / f"{doc_id}.json"


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    doc_ids = args.doc_id or diff_gate_zero_docs.DEFAULT_DOC_IDS
    comparisons = []
    for doc_id in doc_ids:
        left_path = probe_path(args.left_dir, doc_id)
        right_path = probe_path(args.right_dir, doc_id)
        left = compare_gate_zero_geometry_probes.load_probe(left_path)
        right = compare_gate_zero_geometry_probes.load_probe(right_path)
        comparisons.append(
            {
                "doc_id": doc_id,
                "left": str(left_path),
                "right": str(right_path),
                **compare_locator_pair(left, right, args.max_diffs),
            }
        )

    return {
        "schema_version": "ethos-gate-zero-origin-locator-experiment-v1",
        "left_label": args.left_label,
        "right_label": args.right_label,
        "left_dir": str(args.left_dir),
        "right_dir": str(args.right_dir),
        "locator_policy": LOCATOR_POLICY,
        "comparisons": comparisons,
        "summary": {
            "documents_total": len(comparisons),
            "matched_documents": sum(
                comparison["status"] == "matched" for comparison in comparisons
            ),
            "diverged_documents": [
                comparison["doc_id"]
                for comparison in comparisons
                if comparison["status"] == "diverged"
            ],
            "status": "resolved" if all(
                comparison["status"] == "matched" for comparison in comparisons
            ) else "unresolved",
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
        print(f"Gate Zero origin locator experiment: {exc}", file=sys.stderr)
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
