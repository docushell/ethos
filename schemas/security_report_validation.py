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

"""Security-report example validation helpers."""

from __future__ import annotations


SECURITY_WARNING_CODES = {
    "hidden_text_detected",
    "off_page_text_detected",
    "low_contrast_text_detected",
    "annotations_present",
    "external_links_present",
    "unsupported_annotation",
    "image_only_page",
}

REPORTABLE_WARNING_CODES = SECURITY_WARNING_CODES

INVENTORY_BACKED_FINDING_CODES = {
    "annotations_present",
    "external_links_present",
    "unsupported_annotation",
}

WARNING_DERIVED_FINDING_CODES = SECURITY_WARNING_CODES - INVENTORY_BACKED_FINDING_CODES

DEFAULT_CHUNK_EXCLUDED_CODES = {
    "hidden_text_detected",
    "off_page_text_detected",
    "low_contrast_text_detected",
}

TEXT_BACKED_FINDING_CODES = DEFAULT_CHUNK_EXCLUDED_CODES

FINDING_MESSAGE_TEMPLATES = {
    "hidden_text_detected": "hidden text detected: excluded from default chunks",
    "annotations_present": "annotations present on page",
    "external_links_present": "external links present on page",
}


def diagnose_security_report_example(
    document,
    report,
    ctx: str = "security-report.example.json",
):
    diagnostics = []
    payload = document.get("payload") if isinstance(document, dict) else {}
    security_warnings = []
    parser_warnings = []
    if isinstance(payload, dict):
        security_warnings = warning_items(payload.get("security_warnings", []))
        parser_warnings = warning_items(payload.get("parser_warnings", []))
    refs = document_reference_index(payload)
    diagnose_report_identity(document, report, ctx, diagnostics)
    diagnose_warning_lanes(security_warnings, parser_warnings, ctx, diagnostics)

    findings = report.get("findings") if isinstance(report, dict) else []
    if not isinstance(findings, list):
        return [f"{ctx}: findings must be an array"]
    summary = report.get("summary") if isinstance(report, dict) else {}
    if not isinstance(summary, dict):
        return [f"{ctx}: summary must be an object"]

    warning_derived_findings = [
        projected_warning_finding(warning)
        for warning in security_warnings
        if isinstance(warning, dict) and warning.get("code") in REPORTABLE_WARNING_CODES
    ]
    actual_projected_findings = [
        project_report_finding(finding)
        for finding in findings
        if isinstance(finding, dict)
    ]
    finding_counts = {}
    for finding in findings:
        if isinstance(finding, dict) and isinstance(finding.get("code"), str):
            code = finding["code"]
            finding_counts[code] = finding_counts.get(code, 0) + 1

    for expected in warning_derived_findings:
        if expected not in actual_projected_findings:
            diagnostics.append(
                f"{ctx}: missing warning-derived finding for {expected['code']}"
            )

    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        code = finding.get("code")
        if code not in WARNING_DERIVED_FINDING_CODES:
            continue
        projected = project_report_finding(finding)
        if projected not in warning_derived_findings:
            diagnostics.append(
                f"{ctx}: {finding_ctx(finding, index)} has no matching "
                f"security_warnings entry for {code}"
            )

    for code in sorted({finding["code"] for finding in warning_derived_findings}):
        expected_count = sum(
            1 for finding in warning_derived_findings if finding["code"] == code
        )
        if summary.get(code) != expected_count:
            diagnostics.append(
                f"{ctx}: summary.{code} must be {expected_count} "
                "for warning-derived findings"
            )

    for code in sorted(summary.keys()):
        if code not in SECURITY_WARNING_CODES:
            diagnostics.append(f"{ctx}: summary.{code} is not a security report code")

    for code in sorted(set(summary.keys()) | set(finding_counts.keys())):
        expected_count = finding_counts.get(code, 0)
        if code in summary and summary.get(code) == 0 and expected_count == 0:
            diagnostics.append(
                f"{ctx}: summary.{code} must be omitted when no report findings use that code"
            )
        if summary.get(code, 0) != expected_count:
            diagnostics.append(
                f"{ctx}: summary.{code} must be {expected_count} for report findings"
            )

    diagnose_finding_ids(findings, ctx, diagnostics)
    diagnose_finding_messages(findings, ctx, diagnostics)
    diagnose_finding_exclusion_flags(findings, ctx, diagnostics)
    diagnose_findings_references(findings, refs, ctx, diagnostics)

    inventories = report.get("inventories") if isinstance(report, dict) else {}
    if not isinstance(inventories, dict):
        diagnostics.append(f"{ctx}: inventories must be an object")
        return diagnostics

    inventory_lists = {
        name: inventory_items(inventories, name, ctx, diagnostics)
        for name in ("annotations", "actions", "attachments", "scripts", "links")
    }
    annotations = inventory_lists["annotations"]
    links = inventory_lists["links"]
    external_links = [
        link for link in links if isinstance(link, dict) and link.get("external") is True
    ]

    if annotations and finding_counts.get("annotations_present", 0) == 0:
        diagnostics.append(
            f"{ctx}: inventories.annotations requires annotations_present finding"
        )
    if finding_counts.get("annotations_present", 0) > 0 and not annotations:
        diagnostics.append(
            f"{ctx}: annotations_present finding requires inventories.annotations entry"
        )

    if external_links and finding_counts.get("external_links_present", 0) == 0:
        diagnostics.append(
            f"{ctx}: inventories.links external=true requires external_links_present finding"
        )
    if finding_counts.get("external_links_present", 0) > 0 and not external_links:
        diagnostics.append(
            f"{ctx}: external_links_present finding requires inventories.links external=true entry"
        )

    diagnose_inventory_references(inventory_lists, refs, ctx, diagnostics)

    return diagnostics


def warning_items(value):
    if isinstance(value, list):
        return value
    return []


def diagnose_warning_lanes(security_warnings, parser_warnings, ctx, diagnostics):
    for warning in parser_warnings:
        if not isinstance(warning, dict):
            continue
        code = warning.get("code")
        if code in SECURITY_WARNING_CODES:
            diagnostics.append(
                f"{ctx}: parser warning {warning_id(warning)} ({code}) "
                "must be in security_warnings"
            )

    for warning in security_warnings:
        if not isinstance(warning, dict):
            continue
        code = warning.get("code")
        if isinstance(code, str) and code not in SECURITY_WARNING_CODES:
            diagnostics.append(
                f"{ctx}: security warning {warning_id(warning)} ({code}) "
                "is not a security warning code"
            )


def projected_warning_finding(warning):
    projected = {
        "code": warning.get("code"),
        "message": warning.get("message"),
        "excluded_from_default_chunks": warning.get("code") in DEFAULT_CHUNK_EXCLUDED_CODES,
    }
    for key in ("page", "element_ref", "span_ref"):
        if key in warning:
            projected[key] = warning[key]
    return projected


def diagnose_report_identity(document, report, ctx, diagnostics):
    if not isinstance(document, dict) or not isinstance(report, dict):
        return
    expected = {
        "schema_version": document.get("schema_version"),
        "document_fingerprint": document.get("fingerprint"),
        "source_fingerprint": nested_get(document, "source", "fingerprint"),
        "profile.id": nested_get(document, "profile", "id"),
        "profile.sha256": nested_get(document, "profile", "sha256"),
    }
    actual = {
        "schema_version": report.get("schema_version"),
        "document_fingerprint": report.get("document_fingerprint"),
        "source_fingerprint": report.get("source_fingerprint"),
        "profile.id": nested_get(report, "profile", "id"),
        "profile.sha256": nested_get(report, "profile", "sha256"),
    }
    for key, want in expected.items():
        if want is not None and actual.get(key) != want:
            diagnostics.append(f"{ctx}: {key} diverges from document example")


def diagnose_finding_ids(findings, ctx, diagnostics):
    seen = set()
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        finding_id = finding.get("id")
        expected_id = f"f{index + 1:04d}"
        if finding_id != expected_id:
            diagnostics.append(
                f"{ctx}: findings[{index}].id must be {expected_id} for deterministic numbering"
            )
        if isinstance(finding_id, str):
            if finding_id in seen:
                diagnostics.append(f"{ctx}: duplicate finding id {finding_id}")
            seen.add(finding_id)


def diagnose_finding_messages(findings, ctx, diagnostics):
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        code = finding.get("code")
        expected_message = FINDING_MESSAGE_TEMPLATES.get(code)
        if expected_message is None:
            continue
        actual_message = finding.get("message")
        if actual_message != expected_message:
            diagnostics.append(
                f"{ctx}: {finding_ctx(finding, index)} message must match fixed template for {code}"
            )


def diagnose_finding_exclusion_flags(findings, ctx, diagnostics):
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        code = finding.get("code")
        if not isinstance(code, str):
            continue
        expected = code in DEFAULT_CHUNK_EXCLUDED_CODES
        if finding.get("excluded_from_default_chunks") != expected:
            diagnostics.append(
                f"{ctx}: {finding_ctx(finding, index)} excluded_from_default_chunks "
                f"must be {str(expected).lower()} for {code}"
            )


def nested_get(value, outer_key, inner_key):
    outer = value.get(outer_key) if isinstance(value, dict) else None
    if not isinstance(outer, dict):
        return None
    return outer.get(inner_key)


def project_report_finding(finding):
    projected = {
        "code": finding.get("code"),
        "message": finding.get("message"),
        "excluded_from_default_chunks": finding.get("excluded_from_default_chunks"),
    }
    for key in ("page", "element_ref", "span_ref"):
        if key in finding:
            projected[key] = finding[key]
    return projected


def inventory_items(inventories, name, ctx, diagnostics):
    items = inventories.get(name, [])
    if not isinstance(items, list):
        diagnostics.append(f"{ctx}: inventories.{name} must be an array")
        return []
    return items


def document_reference_index(payload):
    if not isinstance(payload, dict):
        return {"pages": {}, "elements": {}, "spans": {}}
    return {
        "pages": keyed_objects(payload.get("pages", [])),
        "elements": keyed_objects(payload.get("elements", [])),
        "spans": keyed_objects(payload.get("spans", [])),
    }


def keyed_objects(items):
    if not isinstance(items, list):
        return {}
    return {
        item["id"]: item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def diagnose_findings_references(findings, refs, ctx, diagnostics):
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        item_ctx = finding_ctx(finding, index)
        page = finding.get("page")
        if page is not None:
            check_page_ref(page, refs, ctx, item_ctx, diagnostics)
        check_locator_ref(
            finding, "element_ref", "elements", refs, ctx, item_ctx, diagnostics
        )
        check_locator_ref(
            finding, "span_ref", "spans", refs, ctx, item_ctx, diagnostics
        )
        if "bbox" in finding:
            check_bbox(finding.get("bbox"), page, refs, ctx, item_ctx, diagnostics)
        check_text_backed_finding(finding, refs, ctx, item_ctx, diagnostics)


def diagnose_inventory_references(inventory_lists, refs, ctx, diagnostics):
    for name, items in inventory_lists.items():
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            item_ctx = f"inventories.{name}[{index}]"
            page = item.get("page")
            if page is not None:
                check_page_ref(page, refs, ctx, item_ctx, diagnostics)
            if "bbox" in item:
                check_bbox(item.get("bbox"), page, refs, ctx, item_ctx, diagnostics)


def check_locator_ref(item, key, ref_kind, refs, ctx, item_ctx, diagnostics):
    ref = item.get(key)
    if ref is None:
        return
    target = refs[ref_kind].get(ref)
    if target is None:
        diagnostics.append(f"{ctx}: {item_ctx} references unknown {key} {ref}")
        return
    page = item.get("page")
    target_page = target.get("page") if isinstance(target, dict) else None
    if page is not None and target_page is not None and page != target_page:
        diagnostics.append(
            f"{ctx}: {item_ctx} {key} {ref} page {target_page} does not match page {page}"
        )
    if key == "span_ref":
        check_element_span_ownership(item, refs, ctx, item_ctx, ref, diagnostics)


def check_page_ref(page, refs, ctx, item_ctx, diagnostics):
    if page not in refs["pages"]:
        diagnostics.append(f"{ctx}: {item_ctx} references unknown page {page}")
        return None
    return refs["pages"][page]


def check_bbox(bbox, page, refs, ctx, item_ctx, diagnostics):
    if page is None:
        diagnostics.append(f"{ctx}: {item_ctx} bbox requires page")
        return
    page_obj = refs["pages"].get(page)
    if page_obj is None:
        return
    if (
        not isinstance(bbox, list)
        or len(bbox) != 4
        or any(not isinstance(coord, int) for coord in bbox)
    ):
        diagnostics.append(f"{ctx}: {item_ctx} bbox must be four integer coordinates")
        return
    x0, y0, x1, y1 = bbox
    if x0 >= x1 or y0 >= y1:
        diagnostics.append(f"{ctx}: {item_ctx} bbox has zero area")
        return
    if (
        x0 < 0
        or y0 < 0
        or x1 > page_obj.get("width", 0)
        or y1 > page_obj.get("height", 0)
    ):
        diagnostics.append(f"{ctx}: {item_ctx} bbox exceeds page {page} bounds")


def check_text_backed_finding(finding, refs, ctx, item_ctx, diagnostics):
    if finding.get("code") not in TEXT_BACKED_FINDING_CODES:
        return
    span_ref = finding.get("span_ref")
    if span_ref is None:
        diagnostics.append(
            f"{ctx}: {item_ctx} requires span_ref for {finding.get('code')}"
        )
        return
    span = refs["spans"].get(span_ref)
    if not isinstance(span, dict):
        return

    if "bbox" not in finding:
        diagnostics.append(f"{ctx}: {item_ctx} span_ref {span_ref} requires bbox")
    elif finding.get("bbox") != span.get("bbox"):
        diagnostics.append(f"{ctx}: {item_ctx} bbox must match span_ref {span_ref} bbox")

    span_text = span.get("text")
    if not isinstance(span_text, str):
        return
    expected_preview = deterministic_preview(span_text)
    if "text_preview" not in finding:
        diagnostics.append(
            f"{ctx}: {item_ctx} span_ref {span_ref} requires text_preview"
        )
    elif finding.get("text_preview") != expected_preview:
        diagnostics.append(
            f"{ctx}: {item_ctx} text_preview must match span_ref {span_ref} text"
        )


def deterministic_preview(text):
    if len(text) <= 120:
        return text
    return text[:120] + "\u2026"


def check_element_span_ownership(item, refs, ctx, item_ctx, span_ref, diagnostics):
    element_ref = item.get("element_ref")
    if element_ref is None:
        return
    element = refs["elements"].get(element_ref)
    if not isinstance(element, dict):
        return
    span_refs = element.get("span_refs", [])
    if not isinstance(span_refs, list):
        diagnostics.append(
            f"{ctx}: {item_ctx} element_ref {element_ref} span_refs must be an array"
        )
        return
    if span_ref not in span_refs:
        diagnostics.append(
            f"{ctx}: {item_ctx} span_ref {span_ref} is not owned by element_ref {element_ref}"
        )


def finding_ctx(finding, index):
    finding_id = finding.get("id")
    if isinstance(finding_id, str):
        return f"finding {finding_id}"
    return f"findings[{index}]"


def warning_id(warning):
    identifier = warning.get("id")
    if isinstance(identifier, str):
        return identifier
    return "<missing-id>"
