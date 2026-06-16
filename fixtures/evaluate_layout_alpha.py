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
extraction.json or layout.json drift away from fixture.json expectations, when
required expectation fields are missing, when committed export goldens drift, or
when heading/list/reading-order/rotation fixture coverage is absent.
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
ALPHA_LAYOUT_CONFIDENCE_WARNING_THRESHOLD = 800
LOW_CONFIDENCE_READING_ORDER_CODE = "low_confidence_reading_order"
TEXT_EXPORT = "text.txt"
MARKDOWN_EXPORT = "markdown.md"
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
    "rotation_fixture": {
        "subset": "rotation",
        "expected_rotation": True,
    },
    "hyphenation_fixture": {
        "subset": "hyphenation",
        "expected_pages": True,
        "expected_span_text": True,
    },
    "ligature_fixture": {
        "subset": "ligatures",
        "expected_pages": True,
        "expected_span_text": True,
    },
    "font_identity_fixture": {
        "subset": "fonts",
        "expected_font_id": True,
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
        print(
            "ok    layout evaluator "
            "heading/list/reading-order/rotation/hyphenation/ligature/font-identity coverage present"
        )
        print("ok    layout evaluator export and warning diagnostics present")
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
    extraction = load_json(
        fixture_dir / "extraction.json",
        diagnostics,
        fixture_id,
        f"{fixture_rel}/extraction.json",
    )
    if not isinstance(metadata, dict) or not isinstance(layout, dict):
        return None
    if not isinstance(extraction, dict):
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
    warnings = layout.get("warnings", [])
    if not isinstance(warnings, list):
        diagnostics.append(
            diagnostic(
                "invalid_layout",
                fixture_id,
                "layout.json warnings must be an array",
                f"{fixture_rel}/layout.json",
            )
        )
        warnings = []

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
    expected_pages = metadata.get("expected_pages")
    expected_span_text = metadata.get("expected_span_text")
    expected_font_id = metadata.get("expected_font_id")
    expected_rotation = metadata.get("expected_rotation")

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
    expected_pages_status = compare_expected_pages(
        fixture_id,
        fixture_rel,
        expected_pages,
        extraction,
        diagnostics,
    )
    expected_span_text_status = compare_expected_span_text(
        fixture_id,
        fixture_rel,
        expected_span_text,
        extraction,
        diagnostics,
    )
    expected_font_id_status = compare_expected_font_id(
        fixture_id,
        fixture_rel,
        expected_font_id,
        extraction,
        diagnostics,
    )
    expected_rotation_status = compare_expected_rotation(
        fixture_id,
        fixture_rel,
        subsets,
        expected_rotation,
        extraction,
        diagnostics,
    )
    warning_shape_status = compare_warning_shape(
        fixture_id,
        fixture_rel,
        elements,
        warnings,
        diagnostics,
    )
    confidence_policy_status = compare_confidence_policy(
        fixture_id,
        fixture_rel,
        elements,
        warnings,
        diagnostics,
    )
    export_goldens_status = compare_export_goldens(
        fixture_id,
        fixture_dir,
        fixture_rel,
        elements,
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
        "expected_pages": expected_pages_status,
        "expected_span_text": expected_span_text_status,
        "expected_font_id": expected_font_id_status,
        "expected_rotation": expected_rotation_status,
        "warning_shape": warning_shape_status,
        "confidence_policy": confidence_policy_status,
        "export_goldens": export_goldens_status,
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


def compare_expected_pages(
    fixture_id: str,
    fixture_rel: str,
    expected_pages: Any,
    extraction: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> str:
    if expected_pages is None:
        return "not_declared"
    if (
        not isinstance(expected_pages, int)
        or isinstance(expected_pages, bool)
        or expected_pages < 0
    ):
        diagnostics.append(
            diagnostic(
                "invalid_expectation",
                fixture_id,
                "expected_pages must be an integer >= 0",
                f"{fixture_rel}/fixture.json",
            )
        )
        return "invalid"
    pages = extraction.get("pages")
    if not isinstance(pages, list):
        diagnostics.append(
            diagnostic(
                "invalid_extraction",
                fixture_id,
                "extraction.json pages must be an array",
                f"{fixture_rel}/extraction.json",
            )
        )
        return "invalid"
    actual_pages = len(pages)
    if expected_pages != actual_pages:
        diagnostics.append(
            diagnostic(
                "expected_pages_mismatch",
                fixture_id,
                "expected_pages does not match extraction page count",
                f"{fixture_rel}/fixture.json",
                expected=expected_pages,
                actual=actual_pages,
            )
        )
        return "mismatch"
    return "pass"


def compare_expected_span_text(
    fixture_id: str,
    fixture_rel: str,
    expected_span_text: Any,
    extraction: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> str:
    if expected_span_text is None:
        return "not_declared"
    if not isinstance(expected_span_text, list) or not all(
        isinstance(item, str) for item in expected_span_text
    ):
        diagnostics.append(
            diagnostic(
                "invalid_expectation",
                fixture_id,
                "expected_span_text must be a string array",
                f"{fixture_rel}/fixture.json",
            )
        )
        return "invalid"
    spans = extraction.get("spans")
    if not isinstance(spans, list):
        diagnostics.append(
            diagnostic(
                "invalid_extraction",
                fixture_id,
                "extraction.json spans must be an array",
                f"{fixture_rel}/extraction.json",
            )
        )
        return "invalid"

    actual_span_text = []
    for span_index, span in enumerate(spans):
        text = span.get("text") if isinstance(span, dict) else None
        if not isinstance(text, str):
            diagnostics.append(
                diagnostic(
                    "invalid_extraction",
                    fixture_id,
                    f"extraction span {span_index} text must be a string",
                    f"{fixture_rel}/extraction.json",
                )
            )
            return "invalid"
        actual_span_text.append(text)

    if expected_span_text != actual_span_text:
        diagnostics.append(
            diagnostic(
                "expected_span_text_mismatch",
                fixture_id,
                "expected_span_text does not match extraction span text order",
                f"{fixture_rel}/fixture.json",
                expected=expected_span_text,
                actual=actual_span_text,
            )
        )
        return "mismatch"
    return "pass"


def compare_expected_font_id(
    fixture_id: str,
    fixture_rel: str,
    expected_font_id: Any,
    extraction: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> str:
    if expected_font_id is None:
        return "not_declared"
    if not isinstance(expected_font_id, str) or not expected_font_id:
        diagnostics.append(
            diagnostic(
                "invalid_expectation",
                fixture_id,
                "expected_font_id must be a non-empty string",
                f"{fixture_rel}/fixture.json",
            )
        )
        return "invalid"
    spans = extraction.get("spans")
    if not isinstance(spans, list):
        diagnostics.append(
            diagnostic(
                "invalid_extraction",
                fixture_id,
                "extraction.json spans must be an array",
                f"{fixture_rel}/extraction.json",
            )
        )
        return "invalid"

    actual_font_ids = []
    for span_index, span in enumerate(spans):
        font_id = span.get("font_id") if isinstance(span, dict) else None
        if not isinstance(font_id, str) or not font_id:
            diagnostics.append(
                diagnostic(
                    "invalid_extraction",
                    fixture_id,
                    f"extraction span {span_index} font_id must be a non-empty string",
                    f"{fixture_rel}/extraction.json",
                )
            )
            return "invalid"
        actual_font_ids.append(font_id)

    if actual_font_ids != [expected_font_id] * len(actual_font_ids):
        diagnostics.append(
            diagnostic(
                "expected_font_id_mismatch",
                fixture_id,
                "expected_font_id does not match every extraction span font_id",
                f"{fixture_rel}/fixture.json",
                expected=expected_font_id,
                actual=actual_font_ids,
            )
        )
        return "mismatch"
    return "pass"


def compare_expected_rotation(
    fixture_id: str,
    fixture_rel: str,
    subsets: List[str],
    expected_rotation: Any,
    extraction: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> str:
    if "rotation" not in subsets:
        return "not_applicable"
    if expected_rotation is None:
        diagnostics.append(
            diagnostic(
                "missing_expectation",
                fixture_id,
                "rotation subset must declare expected_rotation",
                f"{fixture_rel}/fixture.json",
            )
        )
        return "missing"
    if (
        not isinstance(expected_rotation, int)
        or isinstance(expected_rotation, bool)
        or expected_rotation not in (0, 90, 180, 270)
    ):
        diagnostics.append(
            diagnostic(
                "invalid_expectation",
                fixture_id,
                "expected_rotation must be one of 0, 90, 180, or 270",
                f"{fixture_rel}/fixture.json",
            )
        )
        return "invalid"

    pages = extraction.get("pages")
    if not isinstance(pages, list) or not pages:
        diagnostics.append(
            diagnostic(
                "invalid_extraction",
                fixture_id,
                "extraction.json pages must be a non-empty array for rotation fixtures",
                f"{fixture_rel}/extraction.json",
            )
        )
        return "invalid"
    rotations = []
    for page_index, page in enumerate(pages):
        rotation = page.get("rotation") if isinstance(page, dict) else None
        if (
            not isinstance(rotation, int)
            or isinstance(rotation, bool)
            or rotation not in (0, 90, 180, 270)
        ):
            diagnostics.append(
                diagnostic(
                    "invalid_extraction",
                    fixture_id,
                    f"extraction page {page_index} rotation must be one of 0, 90, 180, or 270",
                    f"{fixture_rel}/extraction.json",
                )
            )
            return "invalid"
        rotations.append(rotation)

    if rotations != [expected_rotation] * len(rotations):
        diagnostics.append(
            diagnostic(
                "expected_rotation_mismatch",
                fixture_id,
                "expected_rotation does not match extraction page rotation values",
                f"{fixture_rel}/fixture.json",
                expected=[expected_rotation] * len(rotations),
                actual=rotations,
            )
        )
        return "mismatch"
    return "pass"


def compare_warning_shape(
    fixture_id: str,
    fixture_rel: str,
    elements: List[Any],
    warnings: List[Any],
    diagnostics: List[Dict[str, Any]],
) -> str:
    invalid = False
    mismatch = False
    checked = False
    element_ids = {
        element.get("id")
        for element in elements
        if isinstance(element, dict) and isinstance(element.get("id"), str)
    }
    warning_ids = set()

    for warning_index, warning in enumerate(warnings):
        checked = True
        if not isinstance(warning, dict):
            diagnostics.append(
                diagnostic(
                    "invalid_layout",
                    fixture_id,
                    f"layout warning {warning_index} must be an object",
                    f"{fixture_rel}/layout.json",
                )
            )
            invalid = True
            continue
        warning_id = warning.get("id")
        if not isinstance(warning_id, str) or not warning_id:
            diagnostics.append(
                diagnostic(
                    "invalid_layout",
                    fixture_id,
                    f"layout warning {warning_index} id must be a non-empty string",
                    f"{fixture_rel}/layout.json",
                )
            )
            invalid = True
        elif warning_id in warning_ids:
            diagnostics.append(
                diagnostic(
                    "invalid_layout",
                    fixture_id,
                    f"layout warning {warning_index} id must be unique",
                    f"{fixture_rel}/layout.json",
                )
            )
            invalid = True
        else:
            warning_ids.add(warning_id)
        for field in ("code", "message"):
            if not isinstance(warning.get(field), str) or not warning[field]:
                diagnostics.append(
                    diagnostic(
                        "invalid_layout",
                        fixture_id,
                        f"layout warning {warning_index} {field} must be a non-empty string",
                        f"{fixture_rel}/layout.json",
                    )
                )
                invalid = True
        for field in ("page", "element_ref", "span_ref", "region_ref"):
            value = warning.get(field)
            if value is not None and not isinstance(value, str):
                diagnostics.append(
                    diagnostic(
                        "invalid_layout",
                        fixture_id,
                        f"layout warning {warning_index} {field} must be a string when present",
                        f"{fixture_rel}/layout.json",
                    )
                )
                invalid = True
        element_ref = warning.get("element_ref")
        if isinstance(element_ref, str) and element_ref not in element_ids:
            diagnostics.append(
                diagnostic(
                    "warning_ref_mismatch",
                    fixture_id,
                    "layout warning element_ref must reference a committed layout element",
                    f"{fixture_rel}/layout.json",
                    expected=sorted(element_ids),
                    actual=element_ref,
                )
            )
            mismatch = True

    for element_index, element in enumerate(elements):
        if not isinstance(element, dict):
            continue
        warning_refs = element.get("warning_refs", [])
        if warning_refs:
            checked = True
        if not isinstance(warning_refs, list) or not all(
            isinstance(item, str) for item in warning_refs
        ):
            diagnostics.append(
                diagnostic(
                    "invalid_layout",
                    fixture_id,
                    f"layout element {element_index} warning_refs must be a string array",
                    f"{fixture_rel}/layout.json",
                )
            )
            invalid = True
            continue
        for warning_ref in warning_refs:
            if warning_ref not in warning_ids:
                diagnostics.append(
                    diagnostic(
                        "warning_ref_mismatch",
                        fixture_id,
                        "layout element warning_refs must reference committed layout warnings",
                        f"{fixture_rel}/layout.json",
                        expected=sorted(warning_ids),
                        actual=warning_ref,
                    )
                )
                mismatch = True

    if invalid:
        return "invalid"
    if mismatch:
        return "mismatch"
    return "pass" if checked else "not_applicable"


def compare_confidence_policy(
    fixture_id: str,
    fixture_rel: str,
    elements: List[Any],
    warnings: List[Any],
    diagnostics: List[Dict[str, Any]],
) -> str:
    invalid = False
    checked = 0
    warning_by_id: Dict[str, Dict[str, Any]] = {}

    for warning_index, warning in enumerate(warnings):
        if not isinstance(warning, dict):
            diagnostics.append(
                diagnostic(
                    "invalid_layout",
                    fixture_id,
                    f"layout warning {warning_index} must be an object",
                    f"{fixture_rel}/layout.json",
                )
            )
            invalid = True
            continue
        warning_id = warning.get("id")
        if isinstance(warning_id, str):
            warning_by_id[warning_id] = warning

    for element_index, element in enumerate(elements):
        if not isinstance(element, dict):
            continue
        confidence = element.get("confidence")
        if confidence is None:
            continue
        checked += 1
        if not isinstance(confidence, int) or not 0 <= confidence <= 1000:
            diagnostics.append(
                diagnostic(
                    "invalid_layout",
                    fixture_id,
                    f"layout element {element_index} confidence must be an integer 0..1000",
                    f"{fixture_rel}/layout.json",
                )
            )
            invalid = True
            continue
        if confidence >= ALPHA_LAYOUT_CONFIDENCE_WARNING_THRESHOLD:
            continue

        warning_refs = element.get("warning_refs", [])
        if not isinstance(warning_refs, list) or not all(
            isinstance(item, str) for item in warning_refs
        ):
            diagnostics.append(
                diagnostic(
                    "invalid_layout",
                    fixture_id,
                    f"layout element {element_index} warning_refs must be a string array",
                    f"{fixture_rel}/layout.json",
                )
            )
            invalid = True
            continue

        element_id = element.get("id")
        matched_warning = None
        for warning_ref in warning_refs:
            warning = warning_by_id.get(warning_ref)
            if not isinstance(warning, dict):
                continue
            if (
                warning.get("code") == LOW_CONFIDENCE_READING_ORDER_CODE
                and warning.get("element_ref") == element_id
            ):
                matched_warning = warning
                break
        if matched_warning is None:
            diagnostics.append(
                diagnostic(
                    "confidence_policy_mismatch",
                    fixture_id,
                    "layout element below alpha confidence threshold must reference "
                    "a matching low_confidence_reading_order warning",
                    f"{fixture_rel}/layout.json",
                    expected={
                        "code": LOW_CONFIDENCE_READING_ORDER_CODE,
                        "element_ref": element_id,
                    },
                    actual={
                        "confidence": confidence,
                        "warning_refs": warning_refs,
                    },
                )
            )

    if invalid:
        return "invalid"
    return "pass" if checked else "not_applicable"


def compare_export_goldens(
    fixture_id: str,
    fixture_dir: Path,
    fixture_rel: str,
    elements: List[Any],
    diagnostics: List[Dict[str, Any]],
) -> Dict[str, str]:
    return {
        "text": compare_export_file(
            fixture_id,
            fixture_dir / TEXT_EXPORT,
            f"{fixture_rel}/{TEXT_EXPORT}",
            render_text_export(elements),
            "text export",
            diagnostics,
        ),
        "markdown": compare_export_file(
            fixture_id,
            fixture_dir / MARKDOWN_EXPORT,
            f"{fixture_rel}/{MARKDOWN_EXPORT}",
            render_markdown_export(fixture_id, fixture_rel, elements, diagnostics),
            "Markdown export",
            diagnostics,
        ),
    }


def compare_export_file(
    fixture_id: str,
    path: Path,
    display_path: str,
    expected: Optional[str],
    label: str,
    diagnostics: List[Dict[str, Any]],
) -> str:
    if expected is None:
        return "invalid"
    try:
        actual = path.read_bytes()
    except FileNotFoundError:
        diagnostics.append(
            diagnostic(
                "missing_file",
                fixture_id,
                f"{path.name} is missing",
                display_path,
            )
        )
        return "missing"
    try:
        actual_text = actual.decode("utf-8")
    except UnicodeDecodeError as exc:
        diagnostics.append(
            diagnostic(
                "invalid_export",
                fixture_id,
                f"{path.name} must be UTF-8 text: {exc.reason}",
                display_path,
            )
        )
        return "invalid"
    if actual_text != expected:
        diagnostics.append(
            diagnostic(
                "export_golden_mismatch",
                fixture_id,
                f"{path.name} does not match {label} rendered from layout.json",
                display_path,
                expected=expected,
                actual=actual_text,
            )
        )
        return "mismatch"
    return "pass"


def render_text_export(elements: List[Any]) -> Optional[str]:
    text_blocks = []
    for element in elements:
        if not isinstance(element, dict):
            return None
        text = element.get("text")
        if not isinstance(text, str):
            return None
        text_blocks.append(text)
    return "\n\n".join(text_blocks) + "\n"


def render_markdown_export(
    fixture_id: str,
    fixture_rel: str,
    elements: List[Any],
    diagnostics: List[Dict[str, Any]],
) -> Optional[str]:
    blocks = []
    invalid = False
    for element_index, element in enumerate(elements):
        if not isinstance(element, dict):
            return None
        text = element.get("text")
        if not isinstance(text, str):
            return None
        if element.get("type") == "heading":
            level = element.get("heading_level", 1)
            if not isinstance(level, int):
                diagnostics.append(
                    diagnostic(
                        "invalid_layout",
                        fixture_id,
                        f"layout heading element {element_index} heading_level must be an integer",
                        f"{fixture_rel}/layout.json",
                    )
                )
                invalid = True
                level = 1
            level = min(max(level, 1), 6)
            blocks.append(f"{'#' * level} {text}")
        else:
            blocks.append(text)
    if invalid:
        return None
    return "\n\n".join(blocks) + "\n"


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
    if "rotation" in subsets:
        statuses.append("rotation")
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
        if requirement.get("expected_rotation") and check["expected_rotation"] != "pass":
            continue
        if requirement.get("expected_pages") and check["expected_pages"] != "pass":
            continue
        if (
            requirement.get("expected_span_text")
            and check["expected_span_text"] != "pass"
        ):
            continue
        if requirement.get("expected_font_id") and check["expected_font_id"] != "pass":
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
