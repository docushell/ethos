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
