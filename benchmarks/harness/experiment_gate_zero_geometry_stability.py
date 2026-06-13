#!/usr/bin/env python3
"""Evaluate bbox canonicalization candidates against raw Gate Zero documents.

This is an experiment harness only. It reads existing raw Ethos document JSON
from two platform directories, applies candidate bbox transforms in memory, and
reports whether the transformed documents become equal after derived hashes are
removed. It does not change parser output or the determinism contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

import diff_gate_zero_docs


DERIVED_HASH_FIELDS = {"fingerprint", "payload_sha256"}
BBOX_FIELDS = {"bbox"}


def strip_fields(value: Any, field_names: set[str]) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_fields(child, field_names)
            for key, child in value.items()
            if key not in field_names
        }
    if isinstance(value, list):
        return [strip_fields(child, field_names) for child in value]
    return value


def floor_to_step(value: int, step: int) -> int:
    return (value // step) * step


def ceil_to_step(value: int, step: int) -> int:
    return -((-value) // step) * step


def nearest_to_step(value: int, step: int) -> int:
    sign = -1 if value < 0 else 1
    magnitude = abs(value)
    quotient, remainder = divmod(magnitude, step)
    if remainder * 2 >= step:
        quotient += 1
    return sign * quotient * step


def transform_bboxes(value: Any, transform: Callable[[list[int]], list[int]]) -> Any:
    if isinstance(value, dict):
        transformed: dict[str, Any] = {}
        for key, child in value.items():
            if key == "bbox" and is_bbox(child):
                transformed[key] = transform(child)
            else:
                transformed[key] = transform_bboxes(child, transform)
        return transformed
    if isinstance(value, list):
        return [transform_bboxes(child, transform) for child in value]
    return value


def is_bbox(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(item, int) for item in value)
    )


def canonical_compare_value(value: Any) -> Any:
    return strip_fields(value, DERIVED_HASH_FIELDS)


def bbox_deltas(left: Any, right: Any, pointer: str = "") -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    if isinstance(left, dict) and isinstance(right, dict):
        if is_bbox(left.get("bbox")) and is_bbox(right.get("bbox")):
            for index, (left_coord, right_coord) in enumerate(zip(left["bbox"], right["bbox"])):
                if left_coord != right_coord:
                    child_pointer = diff_gate_zero_docs.join_pointer(
                        diff_gate_zero_docs.join_pointer(pointer, "bbox"),
                        index,
                    )
                    delta = right_coord - left_coord
                    deltas.append(
                        {
                            "pointer": child_pointer,
                            "left": left_coord,
                            "right": right_coord,
                            "delta_quanta": delta,
                            "abs_delta_quanta": abs(delta),
                            "delta_points": delta / 100,
                        }
                    )
        for key in sorted(set(left) & set(right)):
            deltas.extend(bbox_deltas(left[key], right[key], diff_gate_zero_docs.join_pointer(pointer, key)))
    elif isinstance(left, list) and isinstance(right, list):
        for index, (left_child, right_child) in enumerate(zip(left, right)):
            deltas.extend(
                bbox_deltas(
                    left_child,
                    right_child,
                    diff_gate_zero_docs.join_pointer(pointer, index),
                )
            )
    return deltas


def bbox_delta_summary(deltas: list[dict[str, Any]], max_examples: int) -> dict[str, Any]:
    if not deltas:
        return {
            "count": 0,
            "max_abs_delta_quanta": 0,
            "max_abs_delta_points": 0.0,
            "examples": [],
        }
    ordered = sorted(deltas, key=lambda item: item["abs_delta_quanta"], reverse=True)
    return {
        "count": len(deltas),
        "max_abs_delta_quanta": ordered[0]["abs_delta_quanta"],
        "max_abs_delta_points": ordered[0]["abs_delta_quanta"] / 100,
        "examples": ordered[:max_examples],
    }


def identity(value: Any) -> Any:
    return deepcopy(value)


def drop_bbox(value: Any) -> Any:
    return strip_fields(value, BBOX_FIELDS)


def nearest_grid(step: int) -> Callable[[Any], Any]:
    def apply(value: Any) -> Any:
        return transform_bboxes(value, lambda bbox: [nearest_to_step(coord, step) for coord in bbox])

    return apply


def outward_grid(step: int) -> Callable[[Any], Any]:
    def apply(value: Any) -> Any:
        return transform_bboxes(
            value,
            lambda bbox: [
                floor_to_step(bbox[0], step),
                floor_to_step(bbox[1], step),
                ceil_to_step(bbox[2], step),
                ceil_to_step(bbox[3], step),
            ],
        )

    return apply


def strategy_records(args: argparse.Namespace) -> list[dict[str, Any]]:
    records = [
        {
            "id": "identity",
            "kind": "identity",
            "description": "Preserve all document geometry; strip only derived hashes before comparison.",
            "transform": identity,
        },
        {
            "id": "drop-bbox",
            "kind": "drop-bbox",
            "description": "Remove all bbox fields; diagnostic only, not a viable citation geometry policy.",
            "transform": drop_bbox,
        },
    ]
    for step in args.nearest_grid:
        records.append(
            {
                "id": f"nearest-grid-{step}q",
                "kind": "nearest-grid",
                "description": f"Round bbox coordinates to nearest {step} quanta ({step / 100:.2f} pt).",
                "grid_quanta": step,
                "grid_points": step / 100,
                "transform": nearest_grid(step),
            }
        )
    for step in args.outward_grid:
        records.append(
            {
                "id": f"outward-grid-{step}q",
                "kind": "outward-grid",
                "description": (
                    f"Snap bbox min edges down and max edges up to {step} quanta "
                    f"({step / 100:.2f} pt)."
                ),
                "grid_quanta": step,
                "grid_points": step / 100,
                "transform": outward_grid(step),
            }
        )
    return records


def compare_with_transform(
    left: Any,
    right: Any,
    transform: Callable[[Any], Any],
) -> bool:
    left_value = canonical_compare_value(transform(left))
    right_value = canonical_compare_value(transform(right))
    return left_value == right_value


def load_document_pair(args: argparse.Namespace, doc_id: str) -> tuple[Any, Any]:
    left_path = diff_gate_zero_docs.document_path(args.left_dir, doc_id)
    right_path = diff_gate_zero_docs.document_path(args.right_dir, doc_id)
    return diff_gate_zero_docs.load_json(left_path), diff_gate_zero_docs.load_json(right_path)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    doc_ids = selected_doc_ids(args)
    strategies = strategy_records(args)
    documents: list[dict[str, Any]] = []
    strategy_results: list[dict[str, Any]] = []
    pairs = {doc_id: load_document_pair(args, doc_id) for doc_id in doc_ids}

    for doc_id, (left, right) in pairs.items():
        deltas = bbox_deltas(left, right)
        stable_except_bbox = (
            strip_fields(left, DERIVED_HASH_FIELDS | BBOX_FIELDS)
            == strip_fields(right, DERIVED_HASH_FIELDS | BBOX_FIELDS)
        )
        documents.append(
            {
                "doc_id": doc_id,
                "stable_except_bbox_and_hashes": stable_except_bbox,
                "bbox_deltas": bbox_delta_summary(deltas, args.max_examples),
            }
        )

    for record in strategies:
        transform = record["transform"]
        matching_doc_ids = [
            doc_id
            for doc_id, (left, right) in pairs.items()
            if compare_with_transform(left, right, transform)
        ]
        result = {key: value for key, value in record.items() if key != "transform"}
        mismatched_doc_ids = [doc_id for doc_id in doc_ids if doc_id not in matching_doc_ids]
        result.update(
            {
                "documents_total": len(doc_ids),
                "matching_documents": len(matching_doc_ids),
                "mismatching_documents": len(mismatched_doc_ids),
                "matching_doc_ids": matching_doc_ids,
                "mismatching_doc_ids": mismatched_doc_ids,
                "candidate_status": "resolved" if not mismatched_doc_ids else "unresolved",
            }
        )
        strategy_results.append(result)

    bbox_preserving = [
        result
        for result in strategy_results
        if result["kind"] not in {"drop-bbox"}
    ]
    best_bbox_preserving = max(
        bbox_preserving,
        key=lambda result: result["matching_documents"],
        default=None,
    )
    return {
        "schema_version": "ethos-gate-zero-geometry-stability-experiment-v1",
        "inputs": {
            "left_label": args.left_label,
            "right_label": args.right_label,
            "left_dir": str(args.left_dir),
            "right_dir": str(args.right_dir),
            "manifest": str(args.manifest) if args.manifest else None,
            "manifest_sha256": sha256_file(args.manifest) if args.manifest else None,
            "doc_ids": doc_ids,
        },
        "documents": documents,
        "candidates": strategy_results,
        "summary": {
            "documents_total": len(documents),
            "stable_except_bbox_and_hashes": sum(
                document["stable_except_bbox_and_hashes"] for document in documents
            ),
            "candidates_total": len(strategy_results),
            "resolved_candidates": [
                result["id"]
                for result in strategy_results
                if result["candidate_status"] == "resolved"
            ],
            "best_bbox_preserving_strategy": best_bbox_preserving["id"] if best_bbox_preserving else None,
            "best_bbox_preserving_matching_documents": (
                best_bbox_preserving["matching_documents"] if best_bbox_preserving else 0
            ),
        },
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_doc_ids(path: Path) -> list[str]:
    manifest = diff_gate_zero_docs.load_json(path)
    doc_ids = [
        entry.get("id")
        for entry in manifest.get("corpus", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    ]
    if not doc_ids:
        raise ValueError(f"manifest contains no corpus ids: {path}")
    return doc_ids


def selected_doc_ids(args: argparse.Namespace) -> list[str]:
    if args.doc_id:
        return args.doc_id
    if args.manifest:
        return manifest_doc_ids(args.manifest)
    return diff_gate_zero_docs.DEFAULT_DOC_IDS


def positive_grid(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("grid quanta must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("grid quanta must be > 0")
    return parsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-dir", type=Path, required=True)
    parser.add_argument("--right-dir", type=Path, required=True)
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--doc-id", action="append")
    parser.add_argument("--nearest-grid", action="append", type=positive_grid, default=[])
    parser.add_argument("--outward-grid", action="append", type=positive_grid, default=[])
    parser.add_argument("--max-examples", type=int, default=10)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--stdout", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.max_examples < 0:
        print("max-examples must be >= 0", file=sys.stderr)
        return 2
    if not args.nearest_grid:
        args.nearest_grid = [5, 10, 20, 25, 50, 100, 200]
    if not args.outward_grid:
        args.outward_grid = [25, 50, 100, 200, 300, 400, 500, 1000]
    try:
        report = build_report(args)
    except Exception as exc:
        print(f"Gate Zero geometry experiment: {exc}", file=sys.stderr)
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
