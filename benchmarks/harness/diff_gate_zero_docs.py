#!/usr/bin/env python3
"""Diff raw Ethos document JSON emitted on two Gate Zero platforms."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_DOC_IDS = [
    "simple-text",
    "two-lines",
    "two-columns",
    "rotation-90",
    "hyphenated-line-break",
]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"document JSON does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"document JSON is invalid: {path}: {exc}") from exc


def pointer_part(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def join_pointer(base: str, part: str | int) -> str:
    suffix = pointer_part(str(part))
    return f"/{suffix}" if base == "" else f"{base}/{suffix}"


def value_kind(value: Any) -> str:
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if value is None:
        return "null"
    return type(value).__name__


def shorten(value: Any, max_len: int = 120) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 1]}…"


def diff_values(left: Any, right: Any, pointer: str = "") -> list[dict[str, Any]]:
    if left == right:
        return []
    if isinstance(left, dict) and isinstance(right, dict):
        diffs: list[dict[str, Any]] = []
        for key in sorted(set(left) | set(right)):
            child_pointer = join_pointer(pointer, key)
            if key not in left:
                diffs.append(
                    {
                        "pointer": child_pointer,
                        "kind": "missing_left",
                        "left": None,
                        "right": right[key],
                    }
                )
            elif key not in right:
                diffs.append(
                    {
                        "pointer": child_pointer,
                        "kind": "missing_right",
                        "left": left[key],
                        "right": None,
                    }
                )
            else:
                diffs.extend(diff_values(left[key], right[key], child_pointer))
        return diffs
    if isinstance(left, list) and isinstance(right, list):
        diffs = []
        shared_len = min(len(left), len(right))
        for index in range(shared_len):
            diffs.extend(diff_values(left[index], right[index], join_pointer(pointer, index)))
        for index in range(shared_len, len(left)):
            diffs.append(
                {
                    "pointer": join_pointer(pointer, index),
                    "kind": "missing_right",
                    "left": left[index],
                    "right": None,
                }
            )
        for index in range(shared_len, len(right)):
            diffs.append(
                {
                    "pointer": join_pointer(pointer, index),
                    "kind": "missing_left",
                    "left": None,
                    "right": right[index],
                }
            )
        return diffs
    return [
        {
            "pointer": pointer or "/",
            "kind": "value",
            "left": left,
            "right": right,
        }
    ]


def top_level_bucket(pointer: str) -> str:
    if pointer in {"", "/"}:
        return "/"
    parts = pointer.strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "payload":
        return f"/payload/{parts[1]}"
    return f"/{parts[0]}"


def compare_document(left_path: Path, right_path: Path, max_diffs: int) -> dict[str, Any]:
    left = load_json(left_path)
    right = load_json(right_path)
    diffs = diff_values(left, right)
    buckets = Counter(top_level_bucket(diff["pointer"]) for diff in diffs)
    return {
        "left": str(left_path),
        "right": str(right_path),
        "status": "same" if not diffs else "different",
        "diff_count": len(diffs),
        "buckets": dict(sorted(buckets.items())),
        "sample_diffs": [
            {
                "pointer": diff["pointer"],
                "kind": diff["kind"],
                "left_kind": value_kind(diff["left"]),
                "right_kind": value_kind(diff["right"]),
                "left": shorten(diff["left"]),
                "right": shorten(diff["right"]),
            }
            for diff in diffs[:max_diffs]
        ],
    }


def document_path(root: Path, doc_id: str) -> Path:
    return root / f"{doc_id}.json"


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    doc_ids = args.doc_id or DEFAULT_DOC_IDS
    comparisons = [
        {
            "doc_id": doc_id,
            **compare_document(
                document_path(args.left_dir, doc_id),
                document_path(args.right_dir, doc_id),
                args.max_diffs,
            ),
        }
        for doc_id in doc_ids
    ]
    return {
        "schema_version": "ethos-gate-zero-doc-diff-v1",
        "left_label": args.left_label,
        "right_label": args.right_label,
        "comparisons": comparisons,
        "summary": {
            "documents_total": len(comparisons),
            "documents_different": sum(
                comparison["status"] == "different" for comparison in comparisons
            ),
            "diffs_total": sum(comparison["diff_count"] for comparison in comparisons),
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-dir", type=Path, required=True)
    parser.add_argument("--right-dir", type=Path, required=True)
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument("--doc-id", action="append")
    parser.add_argument("--max-diffs", type=int, default=20)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.max_diffs < 0:
        print("max-diffs must be >= 0", file=sys.stderr)
        return 2
    try:
        report = build_report(args)
    except Exception as exc:
        print(f"Gate Zero document diff: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if report["summary"]["documents_different"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
