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

"""Internal Milestone B layout evaluator over committed fixture goldens.

This script does not parse PDFs and does not compare Ethos to other tools. It
summarizes the committed alpha layout fixture expectations and fails closed when
layout.json drifts away from fixture.json expectations, when required expectation
fields are missing, or when heading/list/reading-order fixture coverage is absent.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
REQUIRED_EXPECTATION_FIELDS = ("expected_text", "expected_element_types")
COVERAGE_GATES = {
    "heading_fixture": {
        "subset": "headings",
        "element_type": "heading",
    },
    "list_item_fixture": {
        "subset": "lists",
        "element_type": "list_item",
    },
    "multi_column_reading_order_fixture": {
        "subset": "multi_column",
        "requires_multi_element_expected_text": True,
    },
}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures-root",
        type=Path,
        default=ROOT,
        help="Path to the fixtures directory. Defaults to this script's directory.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional path for the deterministic JSON evaluator report.",
    )
    args = parser.parse_args(argv)

    report = evaluate_layout_alpha(args.fixtures_root)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(canonical_json_bytes(report))

    for diagnostic in report["diagnostics"]:
        fixture = diagnostic.get("fixture_id", "corpus")
        print(f"FAIL  {fixture}: {diagnostic['message']}")

    if report["status"] == "pass":
        print(
            "ok    layout evaluator checked "
            f"{report['fixtures_evaluated']} successful fixture(s)"
        )
        print(
            "ok    layout evaluator element types "
            f"{json.dumps(report['element_type_counts'], sort_keys=True)}"
        )
        print("ok    layout evaluator heading/list/reading-order coverage present")
        if args.out is not None:
            print(f"ok    layout evaluator report wrote {args.out}")
        return 0

    print(f"\n{len(report['diagnostics'])} layout evaluator failure(s)")
    return 1


def evaluate_layout_alpha(fixtures_root: Path) -> Dict[str, Any]:
    diagnostics: List[Dict[str, Any]] = []
    manifest = load_json(
        fixtures_root / "manifest.json",
        diagnostics,
        None,
        "manifest.json",
    )
    entries = manifest.get("fixtures", []) if isinstance(manifest, dict) else []
    if not isinstance(entries, list):
        diagnostics.append(
            diagnostic(
                "invalid_manifest",
                None,
                "manifest fixtures must be an array",
                "manifest.json",
            )
        )
        entries = []

    checks: List[Dict[str, Any]] = []
    element_type_counts: Counter[str] = Counter()
    subset_counts: Counter[str] = Counter()
    coverage: Dict[str, List[str]] = {gate: [] for gate in COVERAGE_GATES}

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            diagnostics.append(
                diagnostic(
                    "invalid_manifest_entry",
                    None,
                    f"manifest fixtures[{index}] must be an object",
                    "manifest.json",
                )
            )
            continue

        fixture_id = entry.get("id")
        fixture_file = entry.get("file")
        subsets = entry.get("subsets")
        if not isinstance(fixture_id, str) or not fixture_id:
            fixture_id = f"manifest fixtures[{index}]"
        if not isinstance(fixture_file, str):
            diagnostics.append(
                diagnostic(
                    "invalid_manifest_entry",
                    fixture_id,
                    "manifest entry file must be a string",
                    "manifest.json",
                )
            )
            continue
        if not isinstance(subsets, list) or not all(isinstance(item, str) for item in subsets):
            diagnostics.append(
                diagnostic(
                    "invalid_manifest_entry",
                    fixture_id,
                    "manifest entry subsets must be a string array",
                    "manifest.json",
                )
            )
            continue
        if "failure" in subsets:
            continue

        fixture_dir = (fixtures_root / fixture_file).parent
        check = evaluate_fixture(fixtures_root, fixture_id, fixture_dir, subsets, diagnostics)
        if check is None:
            continue
        checks.append(check)
        element_type_counts.update(check["element_types"])
        subset_counts.update(subsets)
        update_coverage(coverage, check, subsets)

    for gate, fixtures in coverage.items():
        if not fixtures:
            diagnostics.append(
                diagnostic(
                    "missing_coverage",
                    None,
                    f"{gate} has no committed successful fixture coverage",
                    "manifest.json",
                )
            )

    diagnostics.sort(key=diagnostic_sort_key)
    checks.sort(key=lambda check: check["fixture_id"])
    report = {
        "version": 1,
        "status": "pass" if not diagnostics else "fail",
        "fixtures_evaluated": len(checks),
        "element_type_counts": sorted_counter_dict(element_type_counts),
        "subset_counts": sorted_counter_dict(subset_counts),
        "coverage": {key: sorted(value) for key, value in sorted(coverage.items())},
        "checks": checks,
        "diagnostics": diagnostics,
    }
    return report


def evaluate_fixture(
    fixtures_root: Path,
    fixture_id: str,
    fixture_dir: Path,
    subsets: List[str],
    diagnostics: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    fixture_rel = relpath(fixtures_root, fixture_dir)
    metadata = load_json(
        fixture_dir / "fixture.json",
        diagnostics,
        fixture_id,
        f"{fixture_rel}/fixture.json",
    )
    layout = load_json(
        fixture_dir / "layout.json",
        diagnostics,
        fixture_id,
        f"{fixture_rel}/layout.json",
    )
    if not isinstance(metadata, dict) or not isinstance(layout, dict):
        return None

    elements = layout.get("elements")
    if not isinstance(elements, list):
        diagnostics.append(
            diagnostic(
                "invalid_layout",
                fixture_id,
                "layout.json elements must be an array",
                f"{fixture_rel}/layout.json",
            )
        )
        return None

    element_text = []
    element_types = []
    for element_index, element in enumerate(elements):
        if not isinstance(element, dict):
            diagnostics.append(
                diagnostic(
                    "invalid_layout",
                    fixture_id,
                    f"layout element {element_index} must be an object",
                    f"{fixture_rel}/layout.json",
                )
            )
            continue
        element_text.append(element.get("text"))
        element_types.append(element.get("type"))

    missing_fields = [
        field for field in REQUIRED_EXPECTATION_FIELDS if field not in metadata
    ]
    for field in missing_fields:
        diagnostics.append(
            diagnostic(
                "missing_expectation",
                fixture_id,
                f"fixture.json must include {field}",
                f"{fixture_rel}/fixture.json",
            )
        )

    expected_text = normalize_expected_text(metadata.get("expected_text"))
    expected_element_types = metadata.get("expected_element_types")
    expected_elements = metadata.get("expected_elements")

    expected_text_status = compare_expected_text(
        fixture_id,
        fixture_rel,
        expected_text,
        element_text,
        diagnostics,
    )
    expected_element_types_status = compare_expected_element_types(
        fixture_id,
        fixture_rel,
        expected_element_types,
        element_types,
        diagnostics,
    )
    expected_elements_status = compare_expected_elements(
        fixture_id,
        fixture_rel,
        expected_elements,
        len(elements),
        diagnostics,
    )
    subset_status = compare_subset_expectations(
        fixture_id,
        fixture_rel,
        subsets,
        element_types,
        expected_text,
        diagnostics,
    )

    return {
        "fixture_id": fixture_id,
        "path": fixture_rel,
        "subsets": sorted(subsets),
        "elements": len(elements),
        "element_types": as_string_list(element_types),
        "expected_text": expected_text_status,
        "expected_element_types": expected_element_types_status,
        "expected_elements": expected_elements_status,
        "subset_expectations": subset_status,
    }


def compare_expected_text(
    fixture_id: str,
    fixture_rel: str,
    expected_text: Optional[List[str]],
    element_text: List[Any],
    diagnostics: List[Dict[str, Any]],
) -> str:
    if expected_text is None:
        return "missing"
    if not all(isinstance(item, str) for item in element_text):
        diagnostics.append(
            diagnostic(
                "invalid_layout",
                fixture_id,
                "layout element text values must all be strings",
                f"{fixture_rel}/layout.json",
            )
        )
        return "invalid"
    if element_text != expected_text:
        diagnostics.append(
            diagnostic(
                "expected_text_mismatch",
                fixture_id,
                "expected_text does not match layout element text order",
                f"{fixture_rel}/fixture.json",
                expected=expected_text,
                actual=element_text,
            )
        )
        return "mismatch"
    return "pass"


def compare_expected_element_types(
    fixture_id: str,
    fixture_rel: str,
    expected_element_types: Any,
    element_types: List[Any],
    diagnostics: List[Dict[str, Any]],
) -> str:
    if expected_element_types is None:
        return "missing"
    if not isinstance(expected_element_types, list) or not all(
        isinstance(item, str) for item in expected_element_types
    ):
        diagnostics.append(
            diagnostic(
                "invalid_expectation",
                fixture_id,
                "expected_element_types must be a string array",
                f"{fixture_rel}/fixture.json",
            )
        )
        return "invalid"
    if not all(isinstance(item, str) for item in element_types):
        diagnostics.append(
            diagnostic(
                "invalid_layout",
                fixture_id,
                "layout element type values must all be strings",
                f"{fixture_rel}/layout.json",
            )
        )
        return "invalid"
    if element_types != expected_element_types:
        diagnostics.append(
            diagnostic(
                "expected_element_types_mismatch",
                fixture_id,
                "expected_element_types does not match layout element type order",
                f"{fixture_rel}/fixture.json",
                expected=expected_element_types,
                actual=element_types,
            )
        )
        return "mismatch"
    return "pass"


def compare_expected_elements(
    fixture_id: str,
    fixture_rel: str,
    expected_elements: Any,
    actual_count: int,
    diagnostics: List[Dict[str, Any]],
) -> str:
    if expected_elements is None:
        return "not_declared"
    if not isinstance(expected_elements, int) or expected_elements < 0:
        diagnostics.append(
            diagnostic(
                "invalid_expectation",
                fixture_id,
                "expected_elements must be an integer >= 0",
                f"{fixture_rel}/fixture.json",
            )
        )
        return "invalid"
    if expected_elements != actual_count:
        diagnostics.append(
            diagnostic(
                "expected_elements_mismatch",
                fixture_id,
                "expected_elements does not match layout element count",
                f"{fixture_rel}/fixture.json",
                expected=expected_elements,
                actual=actual_count,
            )
        )
        return "mismatch"
    return "pass"


def compare_subset_expectations(
    fixture_id: str,
    fixture_rel: str,
    subsets: List[str],
    element_types: List[Any],
    expected_text: Optional[List[str]],
    diagnostics: List[Dict[str, Any]],
) -> str:
    statuses = []
    if "headings" in subsets:
        statuses.append("headings")
        if "heading" not in element_types:
            diagnostics.append(
                diagnostic(
                    "subset_expectation_mismatch",
                    fixture_id,
                    "headings subset must include at least one heading element",
                    f"{fixture_rel}/layout.json",
                )
            )
    if "lists" in subsets:
        statuses.append("lists")
        if "list_item" not in element_types:
            diagnostics.append(
                diagnostic(
                    "subset_expectation_mismatch",
                    fixture_id,
                    "lists subset must include at least one list_item element",
                    f"{fixture_rel}/layout.json",
                )
            )
    if "multi_column" in subsets:
        statuses.append("multi_column")
        if expected_text is None or len(expected_text) < 2:
            diagnostics.append(
                diagnostic(
                    "subset_expectation_mismatch",
                    fixture_id,
                    "multi_column subset must declare multi-element expected_text",
                    f"{fixture_rel}/fixture.json",
                )
            )
    return "pass" if statuses else "not_applicable"


def update_coverage(
    coverage: Dict[str, List[str]],
    check: Dict[str, Any],
    subsets: Iterable[str],
) -> None:
    subset_set = set(subsets)
    element_types = set(check["element_types"])
    for gate, requirement in COVERAGE_GATES.items():
        required_subset = requirement["subset"]
        if required_subset not in subset_set:
            continue
        required_type = requirement.get("element_type")
        if required_type is not None and required_type not in element_types:
            continue
        if (
            requirement.get("requires_multi_element_expected_text")
            and check["expected_text"] != "pass"
        ):
            continue
        if requirement.get("requires_multi_element_expected_text") and check["elements"] < 2:
            continue
        coverage[gate].append(check["fixture_id"])


def load_json(
    path: Path,
    diagnostics: List[Dict[str, Any]],
    fixture_id: Optional[str],
    display_path: str,
) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        diagnostics.append(
            diagnostic(
                "missing_file",
                fixture_id,
                f"{path.name} is missing",
                display_path,
            )
        )
    except json.JSONDecodeError as exc:
        diagnostics.append(
            diagnostic(
                "invalid_json",
                fixture_id,
                f"{path.name} is not valid JSON: {exc.msg}",
                display_path,
            )
        )
    return None


def normalize_expected_text(value: Any) -> Optional[List[str]]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return None


def as_string_list(values: Iterable[Any]) -> List[str]:
    return [value if isinstance(value, str) else "<invalid>" for value in values]


def sorted_counter_dict(counter: Counter[str]) -> Dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def diagnostic(
    code: str,
    fixture_id: Optional[str],
    message: str,
    path: str,
    *,
    expected: Any = None,
    actual: Any = None,
) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "code": code,
        "message": message,
        "path": path,
    }
    if fixture_id is not None:
        item["fixture_id"] = fixture_id
    if expected is not None:
        item["expected"] = expected
    if actual is not None:
        item["actual"] = actual
    return item


def diagnostic_sort_key(item: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        str(item.get("fixture_id", "")),
        str(item.get("code", "")),
        str(item.get("path", "")),
    )


def canonical_json_bytes(value: Any) -> bytes:
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return f"{text}\n".encode("utf-8")


def relpath(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    sys.exit(main())
