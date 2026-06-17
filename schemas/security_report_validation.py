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


REPORTABLE_WARNING_CODES = {
    "hidden_text_detected",
    "off_page_text_detected",
    "low_contrast_text_detected",
    "annotations_present",
    "external_links_present",
    "unsupported_annotation",
    "image_only_page",
}

DEFAULT_CHUNK_EXCLUDED_CODES = {
    "hidden_text_detected",
    "off_page_text_detected",
    "low_contrast_text_detected",
}


def diagnose_security_report_example(
    document,
    report,
    ctx: str = "security-report.example.json",
):
    diagnostics = []
    payload = document.get("payload") if isinstance(document, dict) else {}
    warnings = []
    if isinstance(payload, dict):
        warnings.extend(payload.get("security_warnings", []))
        warnings.extend(payload.get("parser_warnings", []))

    findings = report.get("findings") if isinstance(report, dict) else []
    if not isinstance(findings, list):
        return [f"{ctx}: findings must be an array"]
    summary = report.get("summary") if isinstance(report, dict) else {}
    if not isinstance(summary, dict):
        return [f"{ctx}: summary must be an object"]

    warning_derived_findings = [
        projected_warning_finding(warning)
        for warning in warnings
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

    for code in sorted({finding["code"] for finding in warning_derived_findings}):
        expected_count = sum(
            1 for finding in warning_derived_findings if finding["code"] == code
        )
        if summary.get(code) != expected_count:
            diagnostics.append(
                f"{ctx}: summary.{code} must be {expected_count} "
                "for warning-derived findings"
            )

    for code in sorted(set(summary.keys()) | set(finding_counts.keys())):
        expected_count = finding_counts.get(code, 0)
        if summary.get(code, 0) != expected_count:
            diagnostics.append(
                f"{ctx}: summary.{code} must be {expected_count} for report findings"
            )

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

    return diagnostics


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
